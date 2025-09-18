"""
Agent System API Routes
Handles system-wide agent health checks and status information.
"""

from fastapi import APIRouter
from datetime import datetime
import logging
import asyncio

from agent.data_agent import DataAgent
from agent.portfolio_agent import PortfolioAgent
from agent.planner_agent import PlannerAgent
from agent.explainability_agent import ExplainabilityAgent

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Agent System"])

# Initialize agents
data_agent = DataAgent()
portfolio_agent = PortfolioAgent()
planner_agent = PlannerAgent()
explainer_agent = ExplainabilityAgent()


@router.get("/health")
async def agents_health_check():
    """Comprehensive health check for all financial agents."""
    try:
        # Run health checks in parallel
        health_checks = await asyncio.gather(
            data_agent.health_check(),
            portfolio_agent.health_check() if hasattr(portfolio_agent, 'health_check') else {"status": "no_health_check"},
            planner_agent.health_check() if hasattr(planner_agent, 'health_check') else {"status": "no_health_check"},
            explainer_agent.health_check() if hasattr(explainer_agent, 'health_check') else {"status": "no_health_check"},
            return_exceptions=True
        )

        agent_names = ["data_agent", "portfolio_agent", "planner_agent", "explainability_agent"]
        health_status = {}

        for i, (agent_name, health) in enumerate(zip(agent_names, health_checks)):
            if isinstance(health, Exception):
                health_status[agent_name] = {"status": "error", "error": str(health)}
            else:
                health_status[agent_name] = health

        # Determine overall system health
        overall_status = "healthy"
        if any(status.get("status") == "error" for status in health_status.values()):
            overall_status = "degraded"

        return {
            "system_status": overall_status,
            "agents": health_status,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Agent system health check failed: {e}")
        return {
            "system_status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/status")
async def agents_status():
    """Get status information for all agents."""
    return {
        "agents": {
            "data_agent": {
                "description": "Handles market data, macro indicators, and volatility",
                "endpoints": ["/data/market", "/data/macro", "/data/volatility", "/data/technical"],
                "data_sources": ["Yahoo Finance", "FRED API", "Polygon"]
            },
            "portfolio_agent": {
                "description": "Portfolio optimization and rebalancing",
                "endpoints": ["/portfolio/build", "/portfolio/rebalance"],
                "capabilities": ["Risk-based allocation", "Macro signal integration", "Dynamic rebalancing"]
            },
            "planner_agent": {
                "description": "Goal parsing and investment planning",
                "endpoints": ["/planner/parse-goal", "/planner/create-strategy", "/planner/glide-path"],
                "capabilities": ["Natural language processing", "Lifecycle planning", "Goal-based strategies"]
            },
            "explainability_agent": {
                "description": "Financial decision explanations and jargon translation",
                "endpoints": ["/explainer/explain-decision", "/explainer/translate-jargon", "/explainer/risk-explanation"],
                "capabilities": ["Plain English explanations", "Jargon translation", "Risk communication"]
            }
        },
        "system_info": {
            "total_agents": 4,
            "multi_agent_workflows": ["complete_financial_analysis"],
            "rate_limiting": "enabled",
            "llm_integration": "enabled"
        },
        "timestamp": datetime.now().isoformat()
    }