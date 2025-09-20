"""
Multi-Agent Workflows API Routes
Handles orchestrated workflows using multiple financial agents.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from agent.core.data_agent import DataAgent
from agent.core.portfolio_agent import PortfolioAgent
from agent.core.planner_agent import PlannerAgent
from agent.core.explainability_agent import ExplainabilityAgent
from .shared import get_user_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Multi-Agent Workflows"], prefix="/workflow")

# Initialize agents
data_agent = DataAgent()
portfolio_agent = PortfolioAgent()
planner_agent = PlannerAgent()
explainer_agent = ExplainabilityAgent()


@router.post("/complete-analysis")
async def complete_financial_analysis(
    goal_text: str = Body(..., description="Natural language financial goal"),
    user_profile: Dict[str, Any] = Body(..., description="User profile"),
    current_portfolio: Optional[Dict[str, Any]] = Body(None, description="Current portfolio if any"),
    user_id: str = Depends(get_user_id)
):
    """Run a complete financial analysis workflow using all agents."""
    try:
        logger.info(f"Starting complete analysis for user {user_id}")

        # Step 1: Parse the goal with Planner Agent
        parsed_goal = await planner_agent.parse_goal(goal_text)

        # Step 2: Generate strategy with Planner Agent
        strategy = await planner_agent.generate_strategy(parsed_goal, user_profile)

        # Step 3: Build portfolio with Portfolio Agent
        risk_level = user_profile.get("risk_tolerance", 3)
        portfolio = await portfolio_agent.build_portfolio(risk_level, goal_text)

        # Step 4: Get market context with Data Agent
        market_context = await data_agent.get_market_context()

        # Step 5: Generate explanations with Explainability Agent
        explanation = await explainer_agent.explain_decision(
            action={"type": "portfolio_creation", "portfolio": portfolio},
            context={"market_data": market_context, "strategy": strategy}
        )

        return {
            "success": True,
            "workflow": "complete_financial_analysis",
            "results": {
                "parsed_goal": parsed_goal,
                "strategy": strategy,
                "recommended_portfolio": portfolio,
                "market_context": market_context,
                "explanation": explanation
            },
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Complete analysis workflow failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "workflow_failed", "message": str(e), "workflow": "complete_analysis"}
        )