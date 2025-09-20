"""
Plan Creator API routes for comprehensive investment plan generation.
Integrates Agent 2 (Portfolio Agent) and Agent 3 (Planner Agent) to create detailed investment plans.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import json
import uuid

from agent.core.portfolio_agent import PortfolioAgent
from agent.core.planner_agent import PlannerAgent
from agent.clients.mistral_client import create_plan_with_mistral
from api.dependencies.db import supabase

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Plan Creator"], prefix="/plan-creator")

# Initialize agents
portfolio_agent = PortfolioAgent()
planner_agent = PlannerAgent()


@router.post("/create-comprehensive-plan", response_model=Dict[str, Any])
async def create_comprehensive_plan(
    user_id: str,
    financial_goals: Optional[str] = None,
    investment_preferences: Optional[str] = None,
    goal_type: Optional[str] = "GENERAL",
    risk_level: Optional[str] = "BALANCED",
    time_horizon: Optional[int] = 10,
    target_amount: Optional[float] = 100000.0
):
    """
    Create a comprehensive investment plan using Agent 2 (Portfolio) and Agent 3 (Planner).
    Stores all data in the investment_plans table.

    Args:
        user_id: User identifier
        financial_goals: User's financial goals description
        investment_preferences: User's investment preferences
        goal_type: Type of goal (RETIREMENT, HOUSE, EDUCATION, GENERAL)
        risk_level: Risk tolerance (CONSERVATIVE, BALANCED, AGGRESSIVE)
        time_horizon: Investment time horizon in years
        target_amount: Target investment amount

    Returns:
        Complete investment plan with agent outputs
    """
    plan_id = str(uuid.uuid4())

    try:
        logger.info(f"Creating comprehensive plan for user {user_id}")

        # Step 1: Insert initial plan record
        initial_plan_data = {
            "id": plan_id,
            "user_id": user_id,
            "financial_goals": financial_goals,
            "investment_preferences": investment_preferences,
            "plan_type": goal_type,
            "risk_level": risk_level,
            "time_horizon": time_horizon,
            "target_amount": target_amount,
            "processing_status": "PROCESSING"
        }

        result = supabase.table("investment_plans").insert(initial_plan_data).execute()

        # Step 2: Run Agent 3 (Planner Agent) - Goal interpretation and strategy
        logger.info(f"Running Planner Agent (Agent 3) for plan {plan_id}")

        goal_data = {
            "goal_type": goal_type,
            "target_amount": target_amount,
            "time_horizon": time_horizon,
            "risk_level": risk_level,
            "financial_goals": financial_goals,
            "investment_preferences": investment_preferences
        }

        try:
            # Parse goal using Planner Agent
            goal_text = financial_goals or f"Save ${target_amount} for {goal_type.lower()} in {time_horizon} years"
            parsed_goal = await planner_agent.parse_goal(goal_text)

            agent_3_output = {
                "parsed_goal": parsed_goal,
                "goal_text": goal_text,
                "timestamp": datetime.now().isoformat(),
                "agent": "planner_agent",
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Planner Agent failed: {e}")
            agent_3_output = {
                "error": str(e),
                "goal_text": financial_goals or f"Save ${target_amount} for {goal_type.lower()} in {time_horizon} years",
                "timestamp": datetime.now().isoformat(),
                "agent": "planner_agent",
                "status": "failed"
            }

        # Step 3: Run Agent 2 (Portfolio Agent) - Portfolio optimization
        logger.info(f"Running Portfolio Agent (Agent 2) for plan {plan_id}")

        try:
            # Convert risk level to integer for portfolio agent
            risk_mapping = {"CONSERVATIVE": 1, "BALANCED": 3, "AGGRESSIVE": 5}
            risk_int = risk_mapping.get(risk_level, 3)

            # Build portfolio using Portfolio Agent
            portfolio = await portfolio_agent.build_portfolio(risk_int, goal_type.lower())

            agent_2_output = {
                "portfolio": portfolio,
                "risk_level": risk_int,
                "goal_type": goal_type.lower(),
                "timestamp": datetime.now().isoformat(),
                "agent": "portfolio_agent",
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Portfolio Agent failed: {e}")
            agent_2_output = {
                "error": str(e),
                "risk_level": risk_mapping.get(risk_level, 3),
                "goal_type": goal_type.lower(),
                "timestamp": datetime.now().isoformat(),
                "agent": "portfolio_agent",
                "status": "failed"
            }

        # Step 4: Create final plan using LLM (existing create-plan logic)
        logger.info(f"Creating final plan using LLM for plan {plan_id}")

        final_goal = {
            "type": goal_type,
            "target_amount": target_amount,
            "time_horizon": time_horizon,
            "risk_level": risk_level
        }

        final_strategy = {
            "agent_2_data": agent_2_output,
            "agent_3_data": agent_3_output,
            "user_preferences": investment_preferences
        }

        try:
            llm_plan = await create_plan_with_mistral(final_goal, final_strategy, user_id)
        except Exception as e:
            logger.warning(f"LLM plan generation failed, using fallback: {e}")
            llm_plan = {
                "error": str(e),
                "fallback_plan": {
                    "monthly_contribution": target_amount / (time_horizon * 12),
                    "asset_allocation": {"stocks": 60, "bonds": 35, "cash": 5},
                    "milestones": [{"year": 5, "checkpoint": "Review and rebalance"}],
                    "risk_considerations": ["Market volatility", "Inflation risk"]
                }
            }

        # Step 5: Combine all outputs into final plan
        complete_plan = {
            "plan_id": plan_id,
            "user_input": {
                "financial_goals": financial_goals,
                "investment_preferences": investment_preferences,
                "goal_type": goal_type,
                "risk_level": risk_level,
                "time_horizon": time_horizon,
                "target_amount": target_amount
            },
            "agent_outputs": {
                "agent_2_portfolio": agent_2_output,
                "agent_3_planner": agent_3_output,
                "llm_plan": llm_plan
            },
            "investment_plan": llm_plan,  # Keep backward compatibility with frontend
            "created_at": datetime.now().isoformat(),
            "processing_status": "COMPLETED"
        }

        # Step 6: Update database with complete plan
        update_data = {
            "plan_data": complete_plan,
            "agent_2_data": agent_2_output,
            "agent_3_data": agent_3_output,
            "processing_status": "COMPLETED"
        }

        supabase.table("investment_plans").update(update_data).eq("id", plan_id).execute()

        logger.info(f"Successfully created comprehensive plan {plan_id} for user {user_id}")

        return {
            "success": True,
            "plan_id": plan_id,
            "user_id": user_id,
            **complete_plan
        }

    except Exception as e:
        logger.error(f"Error creating comprehensive plan for user {user_id}: {e}")

        # Update status to failed if plan was created
        try:
            supabase.table("investment_plans").update({"processing_status": "FAILED"}).eq("id", plan_id).execute()
        except:
            pass

        raise HTTPException(
            status_code=500,
            detail={
                "error": "plan_creation_failed",
                "message": str(e),
                "plan_id": plan_id,
                "user_id": user_id
            }
        )


@router.get("/plans/{user_id}", response_model=Dict[str, Any])
async def get_user_plans(user_id: str, active_only: bool = Query(True, description="Return only active plans")):
    """
    Get all investment plans for a user.

    Args:
        user_id: User identifier
        active_only: Whether to return only active plans

    Returns:
        List of user's investment plans
    """
    try:
        # Build query based on active_only parameter
        query = supabase.table("investment_plans").select("*").eq("user_id", user_id)

        if active_only:
            query = query.eq("is_active", True)

        query = query.order("created_at", desc=True)
        result = query.execute()

        plans_list = result.data if result.data else []

        return {
            "success": True,
            "user_id": user_id,
            "plans": plans_list,
            "total_plans": len(plans_list)
        }

    except Exception as e:
        logger.error(f"Error fetching plans for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "plans_fetch_failed",
                "message": str(e),
                "user_id": user_id
            }
        )


@router.get("/plan/{plan_id}", response_model=Dict[str, Any])
async def get_plan_details(plan_id: str):
    """
    Get detailed information about a specific investment plan.

    Args:
        plan_id: Plan identifier

    Returns:
        Detailed plan information
    """
    try:
        result = supabase.table("investment_plans").select("*").eq("id", plan_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail={"error": "plan_not_found", "plan_id": plan_id}
            )

        plan_dict = result.data[0]

        return {
            "success": True,
            "plan": plan_dict
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching plan {plan_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "plan_fetch_failed",
                "message": str(e),
                "plan_id": plan_id
            }
        )


@router.patch("/plan/{plan_id}/favorite", response_model=Dict[str, Any])
async def toggle_plan_favorite(plan_id: str, is_favorite: bool):
    """
    Toggle favorite status of an investment plan.

    Args:
        plan_id: Plan identifier
        is_favorite: Whether to mark as favorite

    Returns:
        Updated plan status
    """
    try:
        result = supabase.table("investment_plans").update({"is_favorite": is_favorite}).eq("id", plan_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail={"error": "plan_not_found", "plan_id": plan_id}
            )

        return {
            "success": True,
            "plan_id": plan_id,
            "is_favorite": result.data[0]['is_favorite']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating favorite status for plan {plan_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "favorite_update_failed",
                "message": str(e),
                "plan_id": plan_id
            }
        )


@router.delete("/plan/{plan_id}", response_model=Dict[str, Any])
async def deactivate_plan(plan_id: str):
    """
    Deactivate an investment plan (soft delete).

    Args:
        plan_id: Plan identifier

    Returns:
        Deactivation confirmation
    """
    try:
        result = supabase.table("investment_plans").update({"is_active": False}).eq("id", plan_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail={"error": "plan_not_found", "plan_id": plan_id}
            )

        return {
            "success": True,
            "plan_id": plan_id,
            "is_active": result.data[0]['is_active'],
            "message": "Plan deactivated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating plan {plan_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "plan_deactivation_failed",
                "message": str(e),
                "plan_id": plan_id
            }
        )


@router.get("/health", response_model=Dict[str, Any])
async def plan_creator_health():
    """Check health of Plan Creator service and agents."""
    try:
        # Test database connection
        supabase.table("investment_plans").select("id").limit(1).execute()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e}"

    # Test agents (basic instantiation check)
    try:
        portfolio_agent_status = "healthy" if portfolio_agent else "unavailable"
        planner_agent_status = "healthy" if planner_agent else "unavailable"
    except Exception as e:
        portfolio_agent_status = f"unhealthy: {e}"
        planner_agent_status = f"unhealthy: {e}"

    overall_status = "healthy" if all(
        status == "healthy" for status in [db_status, portfolio_agent_status, planner_agent_status]
    ) else "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": db_status,
            "portfolio_agent": portfolio_agent_status,
            "planner_agent": planner_agent_status
        }
    }