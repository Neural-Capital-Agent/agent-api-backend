"""
Planner Agent API Routes
Handles goal parsing, strategy generation, and investment planning.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any
from datetime import datetime
import logging

from agent.core.planner_agent import PlannerAgent
from .shared import get_user_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Planner Agent"], prefix="/planner")

# Initialize agent
planner_agent = PlannerAgent()


@router.post("/parse-goal")
async def parse_goal(
    goal_text: str = Body(..., description="Natural language goal description"),
    user_id: str = Depends(get_user_id)
):
    """Parse natural language financial goal into structured format."""
    try:
        parsed_goal = await planner_agent.parse_goal(goal_text)

        return {
            "success": True,
            "agent": "planner_agent",
            "original_goal": goal_text,
            "parsed_goal": parsed_goal,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error parsing goal for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "goal_parsing_failed", "message": str(e)}
        )


@router.post("/create-strategy")
async def generate_strategy(
    goal: Dict[str, Any] = Body(..., description="Parsed goal parameters"),
    user_profile: Dict[str, Any] = Body(..., description="User profile information"),
    user_id: str = Depends(get_user_id)
):
    """Generate investment strategy based on goal and user profile."""
    try:
        strategy = await planner_agent.generate_strategy(goal, user_profile)

        return {
            "success": True,
            "agent": "planner_agent",
            "strategy": strategy,
            "goal": goal,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating strategy for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "strategy_generation_failed", "message": str(e)}
        )


@router.post("/glide-path")
async def build_glide_path(
    age: int = Body(..., description="Current age"),
    retirement_age: int = Body(65, description="Target retirement age"),
    user_id: str = Depends(get_user_id)
):
    """Calculate age-appropriate allocation glide path."""
    try:
        glide_path = planner_agent.build_glide_path(age, retirement_age)

        return {
            "success": True,
            "agent": "planner_agent",
            "glide_path": {
                "age_ranges": glide_path.age_ranges,
                "target_retirement_age": glide_path.target_retirement_age
            },
            "current_age": age,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error building glide path for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "glide_path_failed", "message": str(e), "age": age}
        )


@router.post("/create-plan")
async def create_plan(
    goal: Dict[str, Any] = Body(..., description="Financial goal"),
    user_id: str = Depends(get_user_id)
):
    """Create a comprehensive investment plan based on goal."""
    try:
        plan = await planner_agent.create_plan(goal)

        return {
            "success": True,
            "agent": "planner_agent",
            "plan": plan,
            "goal": goal,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating plan for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "plan_creation_failed", "message": str(e)}
        )