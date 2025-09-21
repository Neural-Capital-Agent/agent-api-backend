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
from agent.services.agent_data_service import AgentDataService
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
    """
    Run a complete financial analysis workflow using all enhanced agents.
    Saves all detailed data to Supabase for retrieval and analysis.
    """
    session_id = None
    try:
        logger.info(f"Starting enhanced complete analysis for user {user_id}")

        # Step 1: Create analysis session
        session_id = await AgentDataService.create_analysis_session(
            user_id=user_id,
            goal_text=goal_text,
            session_type="complete_enhanced_analysis"
        )
        logger.info(f"Created analysis session {session_id}")

        # Step 2: Enhanced Planner Agent Analysis with Monte Carlo
        planner_analysis = await planner_agent.create_complete_plan_analysis(
            goal_text=goal_text,
            user_id=user_id,
            session_id=session_id,
            user_profile=user_profile
        )

        if "error" in planner_analysis:
            raise Exception(f"Planner analysis failed: {planner_analysis['error']}")

        # Step 3: Enhanced Portfolio Agent Analysis with Stress Testing
        risk_level = user_profile.get("risk_tolerance", 3)
        portfolio_analysis = await portfolio_agent.create_complete_portfolio_analysis(
            risk_level=risk_level,
            goal=goal_text,
            user_id=user_id,
            session_id=session_id,
            constraints=current_portfolio
        )

        if "error" in portfolio_analysis:
            raise Exception(f"Portfolio analysis failed: {portfolio_analysis['error']}")

        # Step 4: Enhanced Explainability Agent Analysis
        explainability_analysis = await explainer_agent.create_complete_explanation_analysis(
            session_id=session_id,
            user_id=user_id,
            portfolio_agent_data=portfolio_analysis,
            planner_agent_data=planner_analysis
        )

        if "error" in explainability_analysis:
            raise Exception(f"Explainability analysis failed: {explainability_analysis['error']}")

        # Step 5: Get market context for additional insights
        market_context = await data_agent.get_market_context()

        # Step 6: Mark session as completed
        await AgentDataService.complete_analysis_session(session_id)

        # Step 7: Compile comprehensive response
        comprehensive_results = {
            "session_id": session_id,
            "planner_analysis": {
                "goal_parsing": planner_analysis.get("goal_parsing"),
                "goal_parameters": planner_analysis.get("goal_parameters"),
                "detailed_plan": planner_analysis.get("detailed_plan"),
                "monte_carlo_results": planner_analysis.get("monte_carlo_results"),
                "success_probability": planner_analysis.get("detailed_plan", {}).get("success_probability"),
                "recommended_monthly_investment": planner_analysis.get("detailed_plan", {}).get("recommended_monthly_investment")
            },
            "portfolio_analysis": {
                "allocations": portfolio_analysis.get("allocations"),
                "risk_level": portfolio_analysis.get("risk_level"),
                "expected_return": portfolio_analysis.get("expected_return"),
                "stress_tests": portfolio_analysis.get("stress_tests"),
                "rebalancing_triggers": portfolio_analysis.get("rebalancing_triggers"),
                "portfolio_metrics": {
                    "expected_return": portfolio_analysis.get("expected_return"),
                    "expected_risk": portfolio_analysis.get("expected_risk"),
                    "sharpe_ratio": portfolio_analysis.get("sharpe_ratio")
                }
            },
            "explainability_analysis": {
                "main_explanation": explainability_analysis.get("explanation_summary", {}).get("main_explanation"),
                "components": explainability_analysis.get("components"),
                "quality_metrics": explainability_analysis.get("quality_metrics"),
                "investment_theory": explainability_analysis.get("components", {}).get("investment_theory")
            },
            "market_context": market_context,
            "analysis_summary": {
                "total_agents_used": 4,
                "data_persistence": "supabase",
                "enhanced_features": [
                    "Monte Carlo simulations",
                    "Stress testing",
                    "Sophisticated rebalancing triggers",
                    "Mistral LLM explanations",
                    "120-150 word theoretical explanations"
                ],
                "simulation_count": len(planner_analysis.get("monte_carlo_results", [])) * 1000,
                "stress_scenarios": len(portfolio_analysis.get("stress_tests", [])),
                "rebalancing_triggers": len(portfolio_analysis.get("rebalancing_triggers", []))
            }
        }

        return {
            "success": True,
            "workflow": "enhanced_complete_financial_analysis",
            "session_id": session_id,
            "results": comprehensive_results,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "data_saved": True,
            "data_retrieval_endpoint": f"/workflow/analysis/{session_id}"
        }

    except Exception as e:
        logger.error(f"Enhanced complete analysis workflow failed for user {user_id}: {e}")

        # Mark session as failed if it was created
        if session_id:
            try:
                await AgentDataService.complete_analysis_session(session_id)
            except:
                pass

        raise HTTPException(
            status_code=500,
            detail={
                "error": "enhanced_workflow_failed",
                "message": str(e),
                "workflow": "enhanced_complete_analysis",
                "session_id": session_id
            }
        )


@router.get("/analysis/{session_id}")
async def get_saved_analysis(
    session_id: str,
    user_id: str = Depends(get_user_id)
):
    """
    Retrieve complete saved analysis data from Supabase.
    """
    try:
        logger.info(f"Retrieving saved analysis {session_id} for user {user_id}")

        # Get complete analysis from Supabase
        complete_analysis = await AgentDataService.get_complete_analysis(session_id)

        # Verify user has access to this session
        if complete_analysis.get("session", {}).get("user_id") != user_id:
            raise HTTPException(
                status_code=403,
                detail={"error": "access_denied", "message": "Access denied to this analysis session"}
            )

        return {
            "success": True,
            "session_id": session_id,
            "analysis_data": complete_analysis,
            "retrieved_at": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "retrieval_failed", "message": str(e), "session_id": session_id}
        )


@router.get("/analysis/history")
async def get_analysis_history(
    limit: int = 10,
    user_id: str = Depends(get_user_id)
):
    """
    Get user's analysis history.
    """
    try:
        logger.info(f"Retrieving analysis history for user {user_id}")

        history = await AgentDataService.get_user_analysis_history(user_id, limit)

        return {
            "success": True,
            "user_id": user_id,
            "analysis_history": history,
            "count": len(history),
            "retrieved_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error retrieving analysis history for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "history_retrieval_failed", "message": str(e)}
        )