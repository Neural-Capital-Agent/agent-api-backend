"""
Financial Agents API Routes
Provides endpoints for all 4 financial agents with comprehensive functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import asyncio

from api.schemas.user import UserUsageResponse
from utils.rate_limiter import llm_rate_limiter
from agent.agents import DataAgent, PortfolioAgent, PlannerAgent, ExplainabilityAgent

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

router = APIRouter(tags=["Financial Agents"], prefix="/agents")

# Initialize agents
data_agent = DataAgent()
portfolio_agent = PortfolioAgent()
planner_agent = PlannerAgent()
explainer_agent = ExplainabilityAgent()


async def get_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_id: Optional[str] = Query(None, description="User ID for tracking")
) -> str:
    """Extract user ID for request tracking."""
    if user_id:
        return user_id
    # TODO: Extract from JWT token when authentication is implemented
    return "anonymous"


# ================================
# DATA AGENT ENDPOINTS
# ================================

@router.get("/data/health")
async def data_agent_health():
    """Check Data Agent health and data source availability."""
    try:
        health_status = await data_agent.health_check()
        return {
            "agent": "data_agent",
            "status": "healthy",
            "data_sources": health_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Data agent health check failed: {e}")
        return {
            "agent": "data_agent",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/data/market/{ticker}")
async def get_market_data(
    ticker: str,
    user_id: str = Depends(get_user_id),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Fetch real-time market data for a specific ticker."""
    try:
        logger.info(f"Fetching market data for {ticker} (user: {user_id})")

        market_data = await data_agent.fetch_market_data(ticker, start_date, end_date)

        return {
            "success": True,
            "agent": "data_agent",
            "ticker": ticker,
            "data": {
                "symbol": market_data.symbol,
                "price": market_data.price,
                "previous_close": market_data.previous_close,
                "change": market_data.change,
                "change_percent": market_data.change_percent,
                "timestamp": market_data.timestamp.isoformat()
            },
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error fetching market data for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "market_data_fetch_failed", "message": str(e), "ticker": ticker}
        )


@router.get("/data/market")
async def get_all_market_data(user_id: str = Depends(get_user_id)):
    """Fetch market data for all assets in the universe."""
    try:
        market_data_list = await data_agent.fetch_all_market_data()

        return {
            "success": True,
            "agent": "data_agent",
            "total_assets": len(market_data_list),
            "data": [
                {
                    "symbol": data.symbol,
                    "price": data.price,
                    "previous_close": data.previous_close,
                    "change": data.change,
                    "change_percent": data.change_percent,
                    "timestamp": data.timestamp.isoformat()
                }
                for data in market_data_list
            ],
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error fetching all market data: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "market_data_fetch_failed", "message": str(e)}
        )


@router.get("/data/macro/{indicator}")
async def get_macro_data(
    indicator: str,
    user_id: str = Depends(get_user_id),
    date_range: int = Query(30, description="Number of days to look back")
):
    """Fetch macro-economic data from FRED API."""
    try:
        macro_data = await data_agent.fetch_macro_data(indicator, date_range)

        return {
            "success": True,
            "agent": "data_agent",
            "indicator": indicator,
            "date_range": date_range,
            "data_points": len(macro_data),
            "data": [
                {
                    "indicator": data.indicator,
                    "value": data.value,
                    "date": data.date.isoformat(),
                    "frequency": data.frequency
                }
                for data in macro_data
            ],
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error fetching macro data for {indicator}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "macro_data_fetch_failed", "message": str(e), "indicator": indicator}
        )


@router.get("/data/volatility")
async def get_volatility_data(user_id: str = Depends(get_user_id)):
    """Fetch VIX and other volatility indicators."""
    try:
        volatility_data = await data_agent.fetch_volatility_data()

        return {
            "success": True,
            "agent": "data_agent",
            "volatility_data": volatility_data,
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error fetching volatility data: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "volatility_data_fetch_failed", "message": str(e)}
        )


@router.get("/data/technical/{ticker}")
async def get_technical_indicators(
    ticker: str,
    user_id: str = Depends(get_user_id),
    period: str = Query("1y", description="Time period for historical data")
):
    """Fetch technical indicators for a ticker."""
    try:
        technical_data = await data_agent.fetch_technical_indicators(ticker, period)

        return {
            "success": True,
            "agent": "data_agent",
            "ticker": ticker,
            "period": period,
            "indicators": technical_data,
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error fetching technical indicators for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "technical_indicators_failed", "message": str(e), "ticker": ticker}
        )


# ================================
# PORTFOLIO AGENT ENDPOINTS
# ================================

@router.post("/portfolio/build")
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


@router.post("/portfolio/rebalance")
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


# ================================
# PLANNER AGENT ENDPOINTS
# ================================

@router.post("/planner/parse-goal")
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


@router.post("/planner/create-strategy")
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


@router.post("/planner/glide-path")
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


@router.post("/planner/create-plan")
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


# ================================
# EXPLAINABILITY AGENT ENDPOINTS
# ================================

@router.post("/explainer/explain-decision")
async def explain_decision(
    action: Dict[str, Any] = Body(..., description="Action or decision to explain"),
    context: Optional[Dict[str, Any]] = Body(None, description="Additional context"),
    user_id: str = Depends(get_user_id)
):
    """Generate comprehensive explanation for a financial decision."""
    try:
        explanation = await explainer_agent.explain_decision(action, context)

        return {
            "success": True,
            "agent": "explainability_agent",
            "explanation": explanation,
            "action": action,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error explaining decision for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "explanation_failed", "message": str(e)}
        )


@router.post("/explainer/translate-jargon")
async def translate_jargon(
    technical_text: str = Body(..., description="Text containing financial jargon"),
    user_id: str = Depends(get_user_id)
):
    """Convert technical financial terms to plain English."""
    try:
        translation = await explainer_agent.translate_jargon(technical_text)

        return {
            "success": True,
            "agent": "explainability_agent",
            "original_text": technical_text,
            "translation": translation,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error translating jargon for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "translation_failed", "message": str(e)}
        )


@router.get("/explainer/jargon-definition/{term}")
async def get_jargon_definition(
    term: str,
    user_id: str = Depends(get_user_id)
):
    """Get plain English definition for a financial term."""
    try:
        definition = explainer_agent.get_jargon_definition(term)

        return {
            "success": True,
            "agent": "explainability_agent",
            "term": term,
            "definition": definition,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting definition for term {term}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "definition_failed", "message": str(e), "term": term}
        )


@router.post("/explainer/risk-explanation")
async def explain_risk_level(
    risk_level: str = Body(..., description="Risk level to explain"),
    user_id: str = Depends(get_user_id)
):
    """Explain what a risk level means in plain English."""
    try:
        explanation = explainer_agent.explain_risk_level(risk_level)

        return {
            "success": True,
            "agent": "explainability_agent",
            "risk_level": risk_level,
            "explanation": explanation,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error explaining risk level {risk_level}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "risk_explanation_failed", "message": str(e), "risk_level": risk_level}
        )


# ================================
# MULTI-AGENT WORKFLOWS
# ================================

@router.post("/workflow/complete-analysis")
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


# ================================
# AGENT SYSTEM HEALTH & STATUS
# ================================

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