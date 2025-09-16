"""
Rate limiting utilities for LLM usage and API endpoints.
Supports multiple strategies: in-memory, user-based, and token bucket algorithms.
"""

import time
import asyncio
import logging
from collections import defaultdict, deque
from typing import Dict, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


class RateLimitScope(Enum):
    """Rate limiting scopes"""
    USER = "user"
    IP = "ip"
    GLOBAL = "global"
    ENDPOINT = "endpoint"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    max_requests: int = 10
    window_seconds: int = 60
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    scope: RateLimitScope = RateLimitScope.USER
    burst_allowance: int = 0  # Additional requests allowed in burst
    cost_per_request: int = 1  # Cost/weight per request


@dataclass
class UserLimitConfig:
    """Per-user rate limit configuration"""
    daily_limit: int = 100
    hourly_limit: int = 20
    minute_limit: int = 5
    llm_credits: int = 1000
    tier: str = "basic"  # basic, premium, enterprise


@dataclass
class RateLimitState:
    """Current state for rate limiting"""
    requests: deque = field(default_factory=deque)
    tokens: float = 0.0
    last_refill: float = field(default_factory=time.time)
    daily_count: int = 0
    hourly_count: int = 0
    minute_count: int = 0
    last_reset_day: datetime = field(default_factory=lambda: datetime.now().date())
    last_reset_hour: datetime = field(default_factory=lambda: datetime.now().replace(minute=0, second=0, microsecond=0))
    last_reset_minute: datetime = field(default_factory=lambda: datetime.now().replace(second=0, microsecond=0))


class LLMRateLimiter:
    """
    Comprehensive rate limiter for LLM usage with multiple strategies.
    Supports user-based limiting, token bucket, and sliding window algorithms.
    """

    def __init__(self):
        self.user_states: Dict[str, RateLimitState] = defaultdict(RateLimitState)
        self.user_configs: Dict[str, UserLimitConfig] = defaultdict(
            lambda: UserLimitConfig()
        )
        self.global_config = RateLimitConfig()
        self.lock = asyncio.Lock()

    async def set_user_config(self, user_id: str, config: UserLimitConfig):
        """Set custom rate limit configuration for a user"""
        async with self.lock:
            self.user_configs[user_id] = config
            logger.info(f"Updated rate limit config for user {user_id}: {config}")

    async def get_user_config(self, user_id: str) -> UserLimitConfig:
        """Get rate limit configuration for a user"""
        return self.user_configs[user_id]

    async def check_rate_limit(
        self,
        user_id: str,
        endpoint: str = "llm",
        cost: int = 1
    ) -> Dict[str, Any]:
        """
        Check if request is allowed under current rate limits.

        Args:
            user_id: User identifier
            endpoint: API endpoint being accessed
            cost: Cost/weight of this request (default 1)

        Returns:
            Dict with status and metadata
        """
        async with self.lock:
            try:
                user_config = self.user_configs[user_id]
                user_state = self.user_states[user_id]
                current_time = datetime.now()

                # Reset counters if needed
                await self._reset_counters_if_needed(user_state, current_time)

                # Check all limits
                checks = {
                    "daily": await self._check_daily_limit(user_state, user_config, cost),
                    "hourly": await self._check_hourly_limit(user_state, user_config, cost),
                    "minute": await self._check_minute_limit(user_state, user_config, cost),
                    "credits": await self._check_credits(user_state, user_config, cost)
                }

                # Determine if request is allowed
                all_passed = all(check["allowed"] for check in checks.values())

                if all_passed:
                    # Increment counters
                    user_state.daily_count += cost
                    user_state.hourly_count += cost
                    user_state.minute_count += cost

                    # Deduct credits for LLM usage
                    if endpoint.startswith("llm"):
                        user_config.llm_credits -= cost

                # Calculate time until next allowed request
                reset_times = [
                    check.get("reset_time", 0) for check in checks.values()
                    if not check["allowed"]
                ]
                next_reset = min(reset_times) if reset_times else 0

                return {
                    "allowed": all_passed,
                    "user_id": user_id,
                    "endpoint": endpoint,
                    "cost": cost,
                    "checks": checks,
                    "retry_after": max(0, next_reset - time.time()) if reset_times else 0,
                    "current_usage": {
                        "daily": user_state.daily_count,
                        "hourly": user_state.hourly_count,
                        "minute": user_state.minute_count,
                        "credits": user_config.llm_credits
                    },
                    "limits": {
                        "daily": user_config.daily_limit,
                        "hourly": user_config.hourly_limit,
                        "minute": user_config.minute_limit,
                        "tier": user_config.tier
                    }
                }

            except Exception as e:
                logger.error(f"Error checking rate limit for user {user_id}: {e}")
                # Default to allowing request on error
                return {
                    "allowed": True,
                    "error": str(e),
                    "user_id": user_id,
                    "endpoint": endpoint
                }

    async def _reset_counters_if_needed(self, state: RateLimitState, current_time: datetime):
        """Reset counters if time windows have passed"""
        current_date = current_time.date()
        current_hour = current_time.replace(minute=0, second=0, microsecond=0)
        current_minute = current_time.replace(second=0, microsecond=0)

        # Reset daily counter
        if current_date > state.last_reset_day:
            state.daily_count = 0
            state.last_reset_day = current_date

        # Reset hourly counter
        if current_hour > state.last_reset_hour:
            state.hourly_count = 0
            state.last_reset_hour = current_hour

        # Reset minute counter
        if current_minute > state.last_reset_minute:
            state.minute_count = 0
            state.last_reset_minute = current_minute

    async def _check_daily_limit(self, state: RateLimitState, config: UserLimitConfig, cost: int) -> Dict[str, Any]:
        """Check daily rate limit"""
        would_exceed = (state.daily_count + cost) > config.daily_limit
        next_reset = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        return {
            "allowed": not would_exceed,
            "current": state.daily_count,
            "limit": config.daily_limit,
            "reset_time": next_reset.timestamp()
        }

    async def _check_hourly_limit(self, state: RateLimitState, config: UserLimitConfig, cost: int) -> Dict[str, Any]:
        """Check hourly rate limit"""
        would_exceed = (state.hourly_count + cost) > config.hourly_limit
        next_reset = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        return {
            "allowed": not would_exceed,
            "current": state.hourly_count,
            "limit": config.hourly_limit,
            "reset_time": next_reset.timestamp()
        }

    async def _check_minute_limit(self, state: RateLimitState, config: UserLimitConfig, cost: int) -> Dict[str, Any]:
        """Check per-minute rate limit"""
        would_exceed = (state.minute_count + cost) > config.minute_limit
        next_reset = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=1)

        return {
            "allowed": not would_exceed,
            "current": state.minute_count,
            "limit": config.minute_limit,
            "reset_time": next_reset.timestamp()
        }

    async def _check_credits(self, state: RateLimitState, config: UserLimitConfig, cost: int) -> Dict[str, Any]:
        """Check LLM credits"""
        has_enough = config.llm_credits >= cost

        return {
            "allowed": has_enough,
            "current": config.llm_credits,
            "cost": cost,
            "reset_time": 0  # Credits don't auto-reset
        }

    async def add_credits(self, user_id: str, credits: int):
        """Add LLM credits to a user"""
        async with self.lock:
            self.user_configs[user_id].llm_credits += credits
            logger.info(f"Added {credits} LLM credits to user {user_id}")

    async def get_user_status(self, user_id: str) -> Dict[str, Any]:
        """Get current rate limit status for a user"""
        user_config = self.user_configs[user_id]
        user_state = self.user_states[user_id]
        current_time = datetime.now()

        await self._reset_counters_if_needed(user_state, current_time)

        return {
            "user_id": user_id,
            "tier": user_config.tier,
            "current_usage": {
                "daily": user_state.daily_count,
                "hourly": user_state.hourly_count,
                "minute": user_state.minute_count,
                "credits": user_config.llm_credits
            },
            "limits": {
                "daily": user_config.daily_limit,
                "hourly": user_config.hourly_limit,
                "minute": user_config.minute_limit
            },
            "utilization": {
                "daily_percent": (user_state.daily_count / user_config.daily_limit) * 100,
                "hourly_percent": (user_state.hourly_count / user_config.hourly_limit) * 100,
                "minute_percent": (user_state.minute_count / user_config.minute_limit) * 100,
            }
        }

    async def reset_user_limits(self, user_id: str):
        """Reset all rate limits for a user (admin function)"""
        async with self.lock:
            if user_id in self.user_states:
                del self.user_states[user_id]
            logger.info(f"Reset rate limits for user {user_id}")


def rate_limit_decorator(
    limiter: LLMRateLimiter,
    endpoint: str = "llm",
    cost: int = 1
):
    """
    Decorator to apply rate limiting to functions.

    Args:
        limiter: LLMRateLimiter instance
        endpoint: Endpoint identifier
        cost: Cost of this operation
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user_id from kwargs or first arg
            user_id = kwargs.get('user_id')
            if not user_id and args:
                # Try to extract from first argument if it's a string
                user_id = args[0] if isinstance(args[0], str) else None

            if not user_id:
                user_id = "anonymous"

            # Check rate limit
            result = await limiter.check_rate_limit(user_id, endpoint, cost)

            if not result["allowed"]:
                error_msg = f"Rate limit exceeded. Try again in {result.get('retry_after', 60)} seconds."
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "rate_limit_exceeded",
                        "message": error_msg,
                        "retry_after": result.get('retry_after', 60),
                        "current_usage": result.get('current_usage', {}),
                        "limits": result.get('limits', {})
                    }
                )

            # Execute original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


# Global rate limiter instance
llm_rate_limiter = LLMRateLimiter()


# Predefined user tier configurations
USER_TIER_CONFIGS = {
    "basic": UserLimitConfig(
        daily_limit=50,
        hourly_limit=10,
        minute_limit=3,
        llm_credits=100,
        tier="basic"
    ),
    "premium": UserLimitConfig(
        daily_limit=200,
        hourly_limit=50,
        minute_limit=10,
        llm_credits=500,
        tier="premium"
    ),
    "enterprise": UserLimitConfig(
        daily_limit=1000,
        hourly_limit=200,
        minute_limit=50,
        llm_credits=2000,
        tier="enterprise"
    )
}


async def setup_user_tier(user_id: str, tier: str = "basic"):
    """Setup rate limiting for a user with a specific tier"""
    if tier not in USER_TIER_CONFIGS:
        tier = "basic"

    config = USER_TIER_CONFIGS[tier]
    await llm_rate_limiter.set_user_config(user_id, config)
    return config