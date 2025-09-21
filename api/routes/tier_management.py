"""
Tier Management API Routes
Handles user tier validation, feature access control, and tier updates.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from api.dependencies.db import supabase
from .shared import get_user_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Tier Management"], prefix="/tier")


@router.get("/current")
async def get_current_tier(user_id: str = Depends(get_user_id)):
    """Get current user tier information."""
    try:
        # Get user tier data from Supabase
        result = supabase.table("users").select(
            "user_tier, credits_remaining, tier_expires_at, tier_features, created_at"
        ).eq("id", user_id).single().execute()

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail={"error": "user_not_found", "message": "User not found"}
            )

        user_data = result.data

        # Get tier features and limits
        tier_features = user_data.get("tier_features") or get_default_tier_features(
            user_data.get("user_tier", "free")
        )

        # Check if tier is expired
        tier_expires_at = user_data.get("tier_expires_at")
        is_expired = False
        if tier_expires_at:
            expiry_date = datetime.fromisoformat(tier_expires_at.replace("Z", "+00:00"))
            is_expired = datetime.now() <= expiry_date

        return {
            "success": True,
            "tier_data": {
                "user_id": user_id,
                "tier": user_data.get("user_tier", "free"),
                "credits_remaining": user_data.get("credits_remaining", 0),
                "tier_expires_at": tier_expires_at,
                "tier_features": tier_features,
                "is_expired": is_expired,
                "member_since": user_data.get("created_at"),
                "last_updated": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting current tier for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "tier_fetch_failed", "message": str(e)}
        )


@router.post("/validate-feature")
async def validate_feature_access(
    feature_name: str = Body(..., description="Feature name to validate"),
    user_id: str = Depends(get_user_id)
):
    """Validate if user has access to a specific feature."""
    try:
        # Get current tier data
        tier_response = await get_current_tier(user_id)
        tier_data = tier_response["tier_data"]

        # Check feature access
        has_access = check_feature_access(tier_data, feature_name)
        has_usage = check_usage_remaining(tier_data, feature_name)

        # Get required tier for feature
        required_tier = get_required_tier_for_feature(feature_name)

        return {
            "success": True,
            "feature_name": feature_name,
            "access_granted": has_access and has_usage,
            "details": {
                "has_feature_access": has_access,
                "has_usage_remaining": has_usage,
                "current_tier": tier_data["tier"],
                "required_tier": required_tier,
                "credits_remaining": tier_data["credits_remaining"],
                "upgrade_required": not has_access
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating feature access for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "validation_failed", "message": str(e)}
        )


@router.post("/update-tier")
async def update_user_tier(
    new_tier: str = Body(..., description="New tier level"),
    credits: Optional[int] = Body(None, description="Credits to set"),
    expires_at: Optional[str] = Body(None, description="Tier expiration date"),
    user_id: str = Depends(get_user_id)
):
    """Update user tier (admin function)."""
    try:
        # Validate new tier
        valid_tiers = ["free", "basic", "premium", "enterprise"]
        if new_tier not in valid_tiers:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_tier",
                    "message": f"Invalid tier. Must be one of: {valid_tiers}"
                }
            )

        # Prepare update data
        update_data = {
            "user_tier": new_tier,
            "tier_features": get_default_tier_features(new_tier),
            "updated_at": datetime.now().isoformat()
        }

        # Set credits if provided, otherwise use default
        if credits is not None:
            update_data["credits_remaining"] = credits
        else:
            update_data["credits_remaining"] = get_default_credits_for_tier(new_tier)

        # Set expiration if provided
        if expires_at:
            update_data["tier_expires_at"] = expires_at

        # Update user tier in Supabase
        result = supabase.table("users").update(update_data).eq("id", user_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=400,
                detail={"error": "update_failed", "message": "Failed to update tier"}
            )

        logger.info(f"Tier updated for user {user_id}: {new_tier}")

        return {
            "success": True,
            "message": f"Tier updated to {new_tier}",
            "tier_data": {
                "user_id": user_id,
                "tier": new_tier,
                "credits_remaining": update_data["credits_remaining"],
                "tier_expires_at": expires_at,
                "tier_features": update_data["tier_features"],
                "updated_at": update_data["updated_at"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tier for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "tier_update_failed", "message": str(e)}
        )


@router.post("/consume-credit")
async def consume_user_credit(
    feature_name: str = Body(..., description="Feature that consumed credit"),
    credit_cost: int = Body(1, description="Number of credits to consume"),
    user_id: str = Depends(get_user_id)
):
    """Consume user credits for feature usage."""
    try:
        # Get current tier data
        tier_response = await get_current_tier(user_id)
        tier_data = tier_response["tier_data"]

        current_credits = tier_data["credits_remaining"]

        # Check if user has enough credits
        if current_credits < credit_cost:
            return {
                "success": False,
                "error": "insufficient_credits",
                "message": f"Insufficient credits. Required: {credit_cost}, Available: {current_credits}"
            }

        # Consume credits
        new_credits = current_credits - credit_cost

        # Update credits in database
        result = supabase.table("users").update({
            "credits_remaining": new_credits,
            "updated_at": datetime.now().isoformat()
        }).eq("id", user_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=400,
                detail={"error": "credit_update_failed", "message": "Failed to update credits"}
            )

        logger.info(f"Consumed {credit_cost} credits for {feature_name} - User: {user_id}, Remaining: {new_credits}")

        return {
            "success": True,
            "message": f"Consumed {credit_cost} credits for {feature_name}",
            "credits_data": {
                "credits_consumed": credit_cost,
                "credits_remaining": new_credits,
                "previous_credits": current_credits,
                "feature_used": feature_name
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error consuming credits for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "credit_consumption_failed", "message": str(e)}
        )


@router.get("/features")
async def get_tier_features(user_id: str = Depends(get_user_id)):
    """Get detailed feature access for current user tier."""
    try:
        # Get current tier data
        tier_response = await get_current_tier(user_id)
        tier_data = tier_response["tier_data"]

        # Get all feature definitions
        all_features = get_all_feature_definitions()

        # Check access for each feature
        feature_access = {}
        for feature_name, feature_info in all_features.items():
            has_access = check_feature_access(tier_data, feature_name)
            has_usage = check_usage_remaining(tier_data, feature_name)

            feature_access[feature_name] = {
                "name": feature_info["name"],
                "description": feature_info["description"],
                "has_access": has_access,
                "has_usage": has_usage,
                "is_available": has_access and has_usage,
                "required_tier": feature_info["required_tier"],
                "credit_cost": feature_info.get("credit_cost", 1)
            }

        return {
            "success": True,
            "user_tier": tier_data["tier"],
            "credits_remaining": tier_data["credits_remaining"],
            "features": feature_access,
            "tier_limits": tier_data["tier_features"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tier features for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "features_fetch_failed", "message": str(e)}
        )


@router.get("/usage-stats")
async def get_usage_statistics(user_id: str = Depends(get_user_id)):
    """Get user usage statistics for current billing period."""
    try:
        # This would typically query a usage tracking table
        # For now, return mock data
        return {
            "success": True,
            "user_id": user_id,
            "usage_period": {
                "start_date": datetime.now().replace(day=1).isoformat(),
                "end_date": (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).isoformat()
            },
            "usage_stats": {
                "ai_analysis_count": 15,
                "portfolio_optimizations": 5,
                "chat_messages": 42,
                "api_calls": 150,
                "reports_generated": 3
            },
            "limits": {
                "daily_analysis_limit": 100,
                "monthly_analysis_limit": 1000,
                "chat_message_limit": 500
            }
        }

    except Exception as e:
        logger.error(f"Error getting usage statistics for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "usage_stats_failed", "message": str(e)}
        )


# Utility functions
def get_default_tier_features(tier: str) -> Dict[str, Any]:
    """Get default features for a tier."""
    tier_features = {
        "free": {
            "ai_analysis": False,
            "portfolio_optimization": False,
            "real_time_data": False,
            "advanced_charts": False,
            "chat_support": False,
            "api_access": False,
            "monte_carlo": False,
            "stress_testing": False,
            "custom_reports": False,
            "priority_support": False,
            "daily_analysis_limit": 5,
            "monthly_analysis_limit": 50
        },
        "basic": {
            "ai_analysis": True,
            "portfolio_optimization": True,
            "real_time_data": False,
            "advanced_charts": True,
            "chat_support": False,
            "api_access": False,
            "monte_carlo": False,
            "stress_testing": False,
            "custom_reports": False,
            "priority_support": False,
            "daily_analysis_limit": 20,
            "monthly_analysis_limit": 200
        },
        "premium": {
            "ai_analysis": True,
            "portfolio_optimization": True,
            "real_time_data": True,
            "advanced_charts": True,
            "chat_support": True,
            "api_access": False,
            "monte_carlo": True,
            "stress_testing": True,
            "custom_reports": True,
            "priority_support": False,
            "daily_analysis_limit": 100,
            "monthly_analysis_limit": 1000
        },
        "enterprise": {
            "ai_analysis": True,
            "portfolio_optimization": True,
            "real_time_data": True,
            "advanced_charts": True,
            "chat_support": True,
            "api_access": True,
            "monte_carlo": True,
            "stress_testing": True,
            "custom_reports": True,
            "priority_support": True,
            "daily_analysis_limit": -1,  # Unlimited
            "monthly_analysis_limit": -1  # Unlimited
        }
    }

    return tier_features.get(tier, tier_features["free"])


def get_default_credits_for_tier(tier: str) -> int:
    """Get default credits for a tier."""
    credits = {
        "free": 10,
        "basic": 100,
        "premium": 500,
        "enterprise": 10000
    }
    return credits.get(tier, 10)


def check_feature_access(tier_data: Dict, feature_name: str) -> bool:
    """Check if user has access to a feature."""
    tier_features = tier_data.get("tier_features", {})
    return tier_features.get(feature_name, False)


def check_usage_remaining(tier_data: Dict, feature_name: str = None) -> bool:
    """Check if user has usage remaining."""
    credits_remaining = tier_data.get("credits_remaining", 0)

    # Check if tier has unlimited usage
    tier_features = tier_data.get("tier_features", {})
    daily_limit = tier_features.get("daily_analysis_limit", 0)

    if daily_limit == -1:  # Unlimited
        return True

    # Simple check: has credits remaining
    return credits_remaining > 0


def get_required_tier_for_feature(feature_name: str) -> str:
    """Get the minimum tier required for a feature."""
    feature_tiers = {
        "ai_analysis": "basic",
        "portfolio_optimization": "basic",
        "real_time_data": "premium",
        "advanced_charts": "basic",
        "chat_support": "premium",
        "api_access": "enterprise",
        "monte_carlo": "premium",
        "stress_testing": "premium",
        "custom_reports": "premium",
        "priority_support": "enterprise"
    }

    return feature_tiers.get(feature_name, "premium")


def get_all_feature_definitions() -> Dict[str, Dict]:
    """Get all feature definitions with descriptions."""
    return {
        "ai_analysis": {
            "name": "AI Analysis",
            "description": "Advanced AI-powered investment analysis",
            "required_tier": "basic",
            "credit_cost": 2
        },
        "portfolio_optimization": {
            "name": "Portfolio Optimization",
            "description": "Automated portfolio optimization and rebalancing",
            "required_tier": "basic",
            "credit_cost": 3
        },
        "real_time_data": {
            "name": "Real-time Data",
            "description": "Live market data and real-time updates",
            "required_tier": "premium",
            "credit_cost": 1
        },
        "advanced_charts": {
            "name": "Advanced Charts",
            "description": "Professional charting and technical analysis",
            "required_tier": "basic",
            "credit_cost": 1
        },
        "chat_support": {
            "name": "Chat Support",
            "description": "AI-powered chat support and assistance",
            "required_tier": "premium",
            "credit_cost": 1
        },
        "api_access": {
            "name": "API Access",
            "description": "Full API access for custom integrations",
            "required_tier": "enterprise",
            "credit_cost": 5
        },
        "monte_carlo": {
            "name": "Monte Carlo Simulations",
            "description": "Advanced Monte Carlo portfolio simulations",
            "required_tier": "premium",
            "credit_cost": 5
        },
        "stress_testing": {
            "name": "Stress Testing",
            "description": "Portfolio stress testing and scenario analysis",
            "required_tier": "premium",
            "credit_cost": 3
        },
        "custom_reports": {
            "name": "Custom Reports",
            "description": "Generate custom investment reports",
            "required_tier": "premium",
            "credit_cost": 2
        },
        "priority_support": {
            "name": "Priority Support",
            "description": "Priority customer support and assistance",
            "required_tier": "enterprise",
            "credit_cost": 0
        }
    }