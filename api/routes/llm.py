"""
LLM API routes with integrated rate limiting.
Provides endpoints for all LLM operations with proper user identification and rate limiting.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from api.schemas.user import (
    UserUsageResponse, UpdateUserTier, AddCreditsRequest,
    RateLimitStatus, UserLLMAnalytics, LLMUsageStats
)
from utils.rate_limiter import llm_rate_limiter, setup_user_tier, USER_TIER_CONFIGS
from agent.clients.mistral_client import (
    parse_goal_with_mistral, explain_decision_with_mistral,
    create_plan_with_mistral, translate_jargon_with_mistral,
    validate_signals_with_mistral, mistral_client
)


logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)
router = APIRouter(tags=["LLM Operations"], prefix="/llm")


async def get_current_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_id: Optional[str] = Query(None, description="User ID for rate limiting")
) -> str:
    """
    Extract user ID from various sources for rate limiting.
    Priority: JWT token > query parameter > IP address
    """
    try:
        # Try to get user from JWT token
        if credentials and credentials.credentials:
            # TODO: Decode JWT token to extract user_id
            # For now, use a placeholder
            user_id_from_token = None  # await decode_jwt_token(credentials.credentials)
            if user_id_from_token:
                return user_id_from_token

        # Try query parameter
        if user_id:
            return user_id

        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip_{client_ip}"

    except Exception as e:
        logger.warning(f"Error extracting user ID: {e}")
        return "anonymous"


@router.post("/parse-goal", response_model=Dict[str, Any])
async def parse_financial_goal(
    goal_text: str,
    request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """
    Parse natural language financial goal into structured format.

    Rate limited: 1 credit per request
    """
    try:
        logger.info(f"Parsing goal for user {user_id}: {goal_text[:100]}...")

        result = await parse_goal_with_mistral(goal_text, user_id)

        logger.info(f"Successfully parsed goal for user {user_id}")
        return {
            "success": True,
            "user_id": user_id,
            "parsed_goal": result,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        # Re-raise rate limiting errors
        raise
    except Exception as e:
        logger.error(f"Error parsing goal for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "goal_parsing_failed",
                "message": str(e),
                "user_id": user_id
            }
        )


@router.post("/explain-decision", response_model=Dict[str, Any])
async def explain_financial_decision(
    action: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate plain English explanation for financial decisions.

    Rate limited: 2 credits per request
    """
    try:
        logger.info(f"Explaining decision for user {user_id}")

        if context is None:
            context = {}

        explanation = await explain_decision_with_mistral(action, context, user_id)

        return {
            "success": True,
            "user_id": user_id,
            "explanation": explanation,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining decision for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "explanation_failed",
                "message": str(e),
                "user_id": user_id
            }
        )


@router.post("/create-plan", response_model=Dict[str, Any])
async def create_investment_plan(
    goal: Dict[str, Any],
    strategy: Optional[Dict[str, Any]] = None,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create detailed investment plan based on goal and strategy.

    Rate limited: 3 credits per request
    """
    try:
        logger.info(f"Creating plan for user {user_id}")

        if strategy is None:
            strategy = {"default": True}

        plan = await create_plan_with_mistral(goal, strategy, user_id)

        return {
            "success": True,
            "user_id": user_id,
            "investment_plan": plan,
            "goal": goal,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating plan for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "plan_creation_failed",
                "message": str(e),
                "user_id": user_id
            }
        )


@router.post("/translate-jargon", response_model=Dict[str, Any])
async def translate_financial_jargon(
    technical_text: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Convert financial jargon to plain English.

    Rate limited: 1 credit per request
    """
    try:
        logger.info(f"Translating jargon for user {user_id}")

        translation = await translate_jargon_with_mistral(technical_text, user_id)

        return {
            "success": True,
            "user_id": user_id,
            "original_text": technical_text,
            "translated_text": translation,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error translating jargon for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "translation_failed",
                "message": str(e),
                "user_id": user_id
            }
        )


@router.post("/validate-signals", response_model=Dict[str, Any])
async def validate_market_signals(
    signals: Dict[str, Any],
    market_data: Optional[Dict[str, Any]] = None,
    user_id: str = Depends(get_current_user_id)
):
    """
    Validate market signals using LLM analysis.

    Rate limited: 2 credits per request
    """
    try:
        logger.info(f"Validating signals for user {user_id}")

        if market_data is None:
            market_data = {}

        validation = await validate_signals_with_mistral(signals, market_data, user_id)

        return {
            "success": True,
            "user_id": user_id,
            "validation": validation,
            "signals": signals,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating signals for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "signal_validation_failed",
                "message": str(e),
                "user_id": user_id
            }
        )


# Rate Limit Management Endpoints

@router.get("/usage/{user_id}", response_model=UserUsageResponse)
async def get_user_usage(user_id: str):
    """Get current usage statistics for a user."""
    try:
        status = await llm_rate_limiter.get_user_status(user_id)

        return UserUsageResponse(
            user_id=user_id,
            current_usage=status["current_usage"],
            limits=status["limits"],
            utilization=status["utilization"],
            tier=status["tier"],
            credits_remaining=status["current_usage"]["credits"]
        )

    except Exception as e:
        logger.error(f"Error getting usage for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "usage_retrieval_failed", "message": str(e)}
        )


@router.post("/set-tier", response_model=Dict[str, Any])
async def update_user_tier(request: UpdateUserTier):
    """Update user's rate limiting tier (admin endpoint)."""
    try:
        if request.new_tier not in USER_TIER_CONFIGS:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_tier", "available_tiers": list(USER_TIER_CONFIGS.keys())}
            )

        # Setup new tier
        config = await setup_user_tier(request.user_id, request.new_tier)

        # Add additional credits if specified
        if request.additional_credits > 0:
            await llm_rate_limiter.add_credits(request.user_id, request.additional_credits)

        return {
            "success": True,
            "user_id": request.user_id,
            "new_tier": request.new_tier,
            "new_limits": {
                "daily": config.daily_limit,
                "hourly": config.hourly_limit,
                "minute": config.minute_limit,
                "credits": config.llm_credits
            },
            "additional_credits": request.additional_credits
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tier for user {request.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "tier_update_failed", "message": str(e)}
        )


@router.post("/add-credits", response_model=Dict[str, Any])
async def add_user_credits(request: AddCreditsRequest):
    """Add LLM credits to a user (admin endpoint)."""
    try:
        if request.credits <= 0:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_credits", "message": "Credits must be positive"}
            )

        await llm_rate_limiter.add_credits(request.user_id, request.credits)

        # Get updated status
        status = await llm_rate_limiter.get_user_status(request.user_id)

        return {
            "success": True,
            "user_id": request.user_id,
            "credits_added": request.credits,
            "new_balance": status["current_usage"]["credits"],
            "reason": request.reason
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding credits for user {request.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "credit_addition_failed", "message": str(e)}
        )


@router.post("/reset-limits/{user_id}", response_model=Dict[str, Any])
async def reset_user_limits(user_id: str):
    """Reset all rate limits for a user (admin endpoint)."""
    try:
        await llm_rate_limiter.reset_user_limits(user_id)

        return {
            "success": True,
            "user_id": user_id,
            "message": "Rate limits reset successfully"
        }

    except Exception as e:
        logger.error(f"Error resetting limits for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "limit_reset_failed", "message": str(e)}
        )


@router.get("/health", response_model=Dict[str, Any])
async def llm_health_check():
    """Check health of LLM services and rate limiting."""
    try:
        # Check Mistral client health
        mistral_health = await mistral_client.health_check()

        # Get rate limiter status (simple check)
        rate_limiter_status = {
            "active_users": len(llm_rate_limiter.user_states),
            "status": "healthy"
        }

        overall_status = "healthy" if mistral_health.get("status") == "healthy" else "degraded"

        return {
            "status": overall_status,
            "mistral_client": mistral_health,
            "rate_limiter": rate_limiter_status,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/tiers", response_model=Dict[str, Any])
async def get_available_tiers():
    """Get available user tiers and their limits."""
    return {
        "tiers": {
            tier: {
                "daily_limit": config.daily_limit,
                "hourly_limit": config.hourly_limit,
                "minute_limit": config.minute_limit,
                "llm_credits": config.llm_credits,
                "tier": config.tier
            }
            for tier, config in USER_TIER_CONFIGS.items()
        }
    }


@router.get("/analytics/{user_id}", response_model=Dict[str, Any])
async def get_user_analytics(user_id: str):
    """Get comprehensive analytics for a user's LLM usage."""
    try:
        # Get current status
        status = await llm_rate_limiter.get_user_status(user_id)

        # This would typically query a database for historical data
        # For now, return current status as analytics
        return {
            "user_id": user_id,
            "current_status": status,
            "message": "Full analytics require historical data storage implementation"
        }

    except Exception as e:
        logger.error(f"Error getting analytics for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "analytics_retrieval_failed", "message": str(e)}
        )