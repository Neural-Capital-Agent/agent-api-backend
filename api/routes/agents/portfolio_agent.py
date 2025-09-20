"""
Portfolio Agent API Routes
Handles portfolio optimization and rebalancing.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from agent.core.portfolio_agent import PortfolioAgent
from .shared import get_user_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Portfolio Agent"], prefix="/portfolio")

# Initialize agent
portfolio_agent = PortfolioAgent()


@router.post("/build")
async def build_portfolio(
    risk_level: int = Body(..., description="Risk level (1-5)"),
    goal: str = Body(..., description="Investment goal"),
    constraints: Optional[Dict[str, Any]] = Body(None, description="Portfolio constraints"),
    user_id: str = Depends(get_user_id)
):
    """Generate initial portfolio allocation based on risk level and goal."""
    try:
        logger.info(f"Building portfolio for user {user_id}, risk level {risk_level}")

        portfolio = await portfolio_agent.build_portfolio(risk_level, goal, constraints)

        return {
            "success": True,
            "agent": "portfolio_agent",
            "portfolio": portfolio,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error building portfolio for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "portfolio_build_failed", "message": str(e), "risk_level": risk_level}
        )


@router.post("/rebalance")
async def calculate_rebalancing(
    current_portfolio: Dict[str, Any] = Body(..., description="Current portfolio allocation"),
    signals: Optional[Dict[str, Any]] = Body(None, description="Macro signals for rebalancing"),
    user_id: str = Depends(get_user_id)
):
    """Calculate rebalancing actions based on current portfolio and macro signals."""
    try:
        rebalance_result = await portfolio_agent.calculate_rebalancing(current_portfolio, signals)

        return {
            "success": True,
            "agent": "portfolio_agent",
            "rebalance_action": rebalance_result,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating rebalancing for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "rebalancing_failed", "message": str(e)}
        )