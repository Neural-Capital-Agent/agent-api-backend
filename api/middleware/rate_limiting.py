"""
FastAPI middleware for rate limiting LLM and API endpoints.
Integrates with the rate limiter utility and provides request/response handling.
"""

import time
import logging
from typing import Optional, Dict, Any, Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import re

from utils.rate_limiter import llm_rate_limiter, setup_user_tier

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for applying rate limits to requests.
    Focuses on LLM endpoints and provides user identification.
    """

    def __init__(
        self,
        app: ASGIApp,
        llm_endpoints: Optional[list] = None,
        protected_endpoints: Optional[list] = None,
        default_user_tier: str = "basic"
    ):
        super().__init__(app)
        self.llm_endpoints = llm_endpoints or [
            "/api/llm/",
            "/api/agents/",
            "/api/chat/",
            "/api/explain/",
            "/api/parse-goal/",
            "/api/plan/"
        ]
        self.protected_endpoints = protected_endpoints or []
        self.default_user_tier = default_user_tier

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through rate limiting"""
        start_time = time.time()

        try:
            # Check if this endpoint requires rate limiting
            if await self._should_rate_limit(request):
                user_id = await self._get_user_id(request)
                endpoint_type = await self._get_endpoint_type(request)

                # Ensure user has rate limit configuration
                await self._ensure_user_config(user_id)

                # Determine request cost
                cost = await self._calculate_request_cost(request, endpoint_type)

                # Check rate limit
                rate_check = await llm_rate_limiter.check_rate_limit(
                    user_id=user_id,
                    endpoint=endpoint_type,
                    cost=cost
                )

                if not rate_check["allowed"]:
                    return await self._create_rate_limit_response(rate_check)

                # Add rate limit info to request state
                request.state.rate_limit_info = rate_check

            # Process the request
            response = await call_next(request)

            # Add rate limit headers
            if hasattr(request.state, 'rate_limit_info'):
                response = await self._add_rate_limit_headers(response, request.state.rate_limit_info)

            # Log request for monitoring
            process_time = time.time() - start_time
            await self._log_request(request, response, process_time)

            return response

        except HTTPException:
            # Re-raise HTTP exceptions (like 429)
            raise
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # Continue with request on middleware error
            return await call_next(request)

    async def _should_rate_limit(self, request: Request) -> bool:
        """Determine if request should be rate limited"""
        path = str(request.url.path)

        # Check LLM endpoints
        for llm_endpoint in self.llm_endpoints:
            if llm_endpoint in path:
                return True

        # Check protected endpoints
        for protected_endpoint in self.protected_endpoints:
            if protected_endpoint in path:
                return True

        return False

    async def _get_user_id(self, request: Request) -> str:
        """Extract user ID from request"""
        try:
            # Try to get user ID from various sources
            user_id = None

            # 1. From authorization header
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                # Here you would decode JWT token to get user_id
                # For now, using a placeholder
                user_id = await self._extract_user_from_token(auth_header)

            # 2. From query parameters
            if not user_id:
                user_id = request.query_params.get("user_id")

            # 3. From request body (for POST requests)
            if not user_id and request.method == "POST":
                try:
                    # This is a simplified approach - you might want to parse JSON body
                    user_id = request.path_params.get("user_id")
                except:
                    pass

            # 4. From IP address as fallback
            if not user_id:
                client_ip = self._get_client_ip(request)
                user_id = f"ip_{client_ip}"

            return user_id or "anonymous"

        except Exception as e:
            logger.warning(f"Error extracting user ID: {e}")
            return "anonymous"

    async def _extract_user_from_token(self, auth_header: str) -> Optional[str]:
        """Extract user ID from JWT token"""
        try:
            # TODO: Implement JWT token decoding
            # This is a placeholder - you would use your JWT library here
            token = auth_header.replace("Bearer ", "")

            # For now, return None to use fallback methods
            return None

        except Exception as e:
            logger.warning(f"Error decoding token: {e}")
            return None

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    async def _get_endpoint_type(self, request: Request) -> str:
        """Determine endpoint type for rate limiting"""
        path = str(request.url.path).lower()

        if "/llm/" in path or "/chat/" in path:
            return "llm_chat"
        elif "/parse-goal/" in path or "/goal/" in path:
            return "llm_parse"
        elif "/explain/" in path:
            return "llm_explain"
        elif "/plan/" in path:
            return "llm_plan"
        elif "/agents/" in path:
            return "llm_agent"
        else:
            return "api"

    async def _ensure_user_config(self, user_id: str):
        """Ensure user has rate limiting configuration"""
        try:
            # Check if user already has config
            current_config = await llm_rate_limiter.get_user_config(user_id)

            # If user doesn't have config, set up default tier
            if current_config.tier == "basic" and user_id != "anonymous":
                await setup_user_tier(user_id, self.default_user_tier)

        except Exception as e:
            logger.warning(f"Error ensuring user config for {user_id}: {e}")

    async def _calculate_request_cost(self, request: Request, endpoint_type: str) -> int:
        """Calculate the cost/weight of a request"""
        # Different endpoints have different costs
        cost_map = {
            "llm_chat": 3,      # Chat is expensive
            "llm_explain": 2,   # Explanations are moderate
            "llm_parse": 1,     # Parsing is cheaper
            "llm_plan": 3,      # Planning is expensive
            "llm_agent": 2,     # Agent calls are moderate
            "api": 1            # Regular API calls are cheap
        }

        base_cost = cost_map.get(endpoint_type, 1)

        # Adjust cost based on request method
        if request.method in ["POST", "PUT"]:
            base_cost += 1

        return base_cost

    async def _create_rate_limit_response(self, rate_check: Dict[str, Any]) -> JSONResponse:
        """Create rate limit exceeded response"""
        retry_after = int(rate_check.get("retry_after", 60))
        current_usage = rate_check.get("current_usage", {})
        limits = rate_check.get("limits", {})

        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after_seconds": retry_after,
                "current_usage": current_usage,
                "limits": limits,
                "user_id": rate_check.get("user_id"),
                "endpoint": rate_check.get("endpoint")
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(limits.get("minute", 5)),
                "X-RateLimit-Remaining": str(max(0, limits.get("minute", 5) - current_usage.get("minute", 0))),
                "X-RateLimit-Reset": str(int(time.time() + retry_after))
            }
        )

    async def _add_rate_limit_headers(self, response: Response, rate_info: Dict[str, Any]) -> Response:
        """Add rate limiting headers to response"""
        try:
            current_usage = rate_info.get("current_usage", {})
            limits = rate_info.get("limits", {})

            # Add standard rate limit headers
            response.headers["X-RateLimit-Limit"] = str(limits.get("minute", 5))
            response.headers["X-RateLimit-Remaining"] = str(max(0, limits.get("minute", 5) - current_usage.get("minute", 0)))
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))

            # Add LLM-specific headers
            if "credits" in current_usage:
                response.headers["X-LLM-Credits"] = str(current_usage["credits"])

            response.headers["X-User-Tier"] = str(limits.get("tier", "basic"))

        except Exception as e:
            logger.warning(f"Error adding rate limit headers: {e}")

        return response

    async def _log_request(self, request: Request, response: Response, process_time: float):
        """Log request for monitoring and analytics"""
        try:
            log_data = {
                "path": str(request.url.path),
                "method": request.method,
                "status_code": response.status_code,
                "process_time": round(process_time, 3),
                "user_id": getattr(request.state, 'rate_limit_info', {}).get('user_id', 'unknown'),
                "endpoint_type": await self._get_endpoint_type(request),
                "timestamp": time.time()
            }

            # Log at different levels based on status
            if response.status_code == 429:
                logger.warning(f"Rate limited request: {log_data}")
            elif response.status_code >= 400:
                logger.info(f"Client error: {log_data}")
            else:
                logger.debug(f"Successful request: {log_data}")

        except Exception as e:
            logger.error(f"Error logging request: {e}")


class LLMUsageMiddleware(BaseHTTPMiddleware):
    """
    Specialized middleware for tracking LLM usage and costs.
    Provides detailed analytics for LLM operations.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.usage_stats = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track LLM usage"""
        # Check if this is an LLM request
        if "/llm/" in str(request.url.path) or "/chat/" in str(request.url.path):
            start_time = time.time()

            try:
                response = await call_next(request)

                # Track successful LLM usage
                process_time = time.time() - start_time
                await self._track_llm_usage(request, response, process_time)

                return response

            except Exception as e:
                # Track failed LLM usage
                process_time = time.time() - start_time
                await self._track_llm_error(request, e, process_time)
                raise
        else:
            return await call_next(request)

    async def _track_llm_usage(self, request: Request, response: Response, process_time: float):
        """Track successful LLM usage"""
        try:
            user_id = getattr(request.state, 'rate_limit_info', {}).get('user_id', 'unknown')
            endpoint = str(request.url.path)

            # Update usage statistics
            if user_id not in self.usage_stats:
                self.usage_stats[user_id] = {
                    "total_requests": 0,
                    "total_time": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "endpoints": {}
                }

            stats = self.usage_stats[user_id]
            stats["total_requests"] += 1
            stats["total_time"] += process_time
            stats["successful_requests"] += 1

            if endpoint not in stats["endpoints"]:
                stats["endpoints"][endpoint] = {"count": 0, "total_time": 0}

            stats["endpoints"][endpoint]["count"] += 1
            stats["endpoints"][endpoint]["total_time"] += process_time

            logger.info(f"LLM usage tracked for user {user_id}: {endpoint} ({process_time:.3f}s)")

        except Exception as e:
            logger.error(f"Error tracking LLM usage: {e}")

    async def _track_llm_error(self, request: Request, error: Exception, process_time: float):
        """Track failed LLM usage"""
        try:
            user_id = getattr(request.state, 'rate_limit_info', {}).get('user_id', 'unknown')

            if user_id in self.usage_stats:
                self.usage_stats[user_id]["failed_requests"] += 1

            logger.warning(f"LLM error tracked for user {user_id}: {error}")

        except Exception as e:
            logger.error(f"Error tracking LLM error: {e}")

    def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        return self.usage_stats.get(user_id, {})

    def get_all_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all users"""
        return self.usage_stats.copy()