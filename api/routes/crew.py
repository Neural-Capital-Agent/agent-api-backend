"""
Simple CrewAI Workflow Endpoints
Provides easy-to-use endpoints for orchestrated financial advisory workflows.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from agent.crew.agents import crew_manager
from api.middleware.rate_limiting import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crew", tags=["CrewAI Workflows"])

# ================================
# Request Models
# ================================

class MarketAnalysisRequest(BaseModel):
    symbols: Optional[List[str]] = Field(default=["SPY", "QQQ", "BND"], description="Stock symbols to analyze")

class PortfolioAdvisoryRequest(BaseModel):
    goal_text: str = Field(..., description="Your financial goal in plain language", examples=["I want to retire in 20 years with $1M"])
    risk_level: int = Field(default=3, ge=1, le=5, description="Risk tolerance (1=Conservative, 5=Aggressive)")

class QuickAdviceRequest(BaseModel):
    question: str = Field(..., description="Your financial question", examples=["Should I invest in bonds right now?"])

# ================================
# Simple Workflow Endpoints
# ================================

@router.post(
    "/market-analysis",
    summary="Market Analysis Workflow",
    description="Get AI-powered market analysis using CrewAI orchestration",
    response_description="Market analysis with insights and trends"
)
@rate_limit(cost=3)
async def market_analysis(request: MarketAnalysisRequest, req: Request):
    """Run market analysis workflow with CrewAI"""
    try:
        logger.info(f"Starting market analysis for symbols: {request.symbols}")

        result = await crew_manager.market_analysis(request.symbols)

        return JSONResponse(
            status_code=200,
            content={
                "workflow": "market_analysis",
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "symbols": request.symbols
            }
        )

    except Exception as e:
        logger.error(f"Market analysis workflow failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Market analysis failed: {str(e)}"
        )

@router.post(
    "/portfolio-advisory",
    summary="Complete Portfolio Advisory",
    description="Full financial advisory workflow: goal parsing → market analysis → portfolio optimization → explanation",
    response_description="Complete portfolio recommendations with explanations"
)
@rate_limit(cost=5)
async def portfolio_advisory(request: PortfolioAdvisoryRequest, req: Request):
    """Run complete portfolio advisory workflow"""
    try:
        logger.info(f"Starting portfolio advisory for goal: {request.goal_text}")

        result = await crew_manager.portfolio_advisory(
            goal_text=request.goal_text,
            risk_level=request.risk_level
        )

        return JSONResponse(
            status_code=200,
            content={
                "workflow": "portfolio_advisory",
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "input": {
                    "goal": request.goal_text,
                    "risk_level": request.risk_level
                }
            }
        )

    except Exception as e:
        logger.error(f"Portfolio advisory workflow failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio advisory failed: {str(e)}"
        )

@router.post(
    "/quick-advice",
    summary="Quick Financial Advice",
    description="Get quick financial advice for simple questions using AI agents",
    response_description="Clear financial guidance and advice"
)
@rate_limit(cost=2)
async def quick_advice(request: QuickAdviceRequest, req: Request):
    """Get quick financial advice"""
    try:
        logger.info(f"Processing quick advice question: {request.question}")

        result = await crew_manager.quick_advice(request.question)

        return JSONResponse(
            status_code=200,
            content={
                "workflow": "quick_advice",
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "question": request.question
            }
        )

    except Exception as e:
        logger.error(f"Quick advice workflow failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Quick advice failed: {str(e)}"
        )

# ================================
# Status and Management
# ================================

@router.get(
    "/status",
    summary="CrewAI System Status",
    description="Get status of the CrewAI system and agents",
    response_description="System status and agent information"
)
async def crew_status(req: Request):
    """Get CrewAI system status"""
    try:
        status = crew_manager.get_crew_status()

        return {
            "crewai_status": "operational",
            "crew_details": status,
            "available_workflows": [
                "market_analysis",
                "portfolio_advisory",
                "quick_advice"
            ],
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Crew status check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )

@router.get(
    "/workflows",
    summary="Available Workflows",
    description="List all available CrewAI workflows with descriptions",
    response_description="List of workflows and their capabilities"
)
async def list_workflows(req: Request):
    """List available CrewAI workflows"""
    return {
        "workflows": {
            "market_analysis": {
                "description": "Analyze current market conditions and trends",
                "input": "List of stock symbols (optional)",
                "output": "Market analysis with insights",
                "cost": 3,
                "estimated_time": "30-60 seconds"
            },
            "portfolio_advisory": {
                "description": "Complete financial advisory: goal → analysis → optimization → explanation",
                "input": "Financial goal text and risk level",
                "output": "Complete portfolio recommendations",
                "cost": 5,
                "estimated_time": "60-120 seconds"
            },
            "quick_advice": {
                "description": "Quick answers to financial questions",
                "input": "Financial question in plain language",
                "output": "Clear financial advice",
                "cost": 2,
                "estimated_time": "15-30 seconds"
            }
        },
        "agents": {
            "data_analyst": "Analyzes market data and economic indicators",
            "portfolio_manager": "Creates optimized investment portfolios",
            "financial_planner": "Interprets goals and creates strategies",
            "financial_advisor": "Explains recommendations in plain language"
        },
        "timestamp": datetime.now().isoformat()
    }

# ================================
# Example Usage Endpoint
# ================================

@router.get(
    "/examples",
    summary="Workflow Examples",
    description="Get example requests for each workflow type",
    response_description="Example requests and expected responses"
)
async def workflow_examples(req: Request):
    """Get example requests for workflows"""
    return {
        "examples": {
            "market_analysis": {
                "request": {
                    "symbols": ["AAPL", "MSFT", "SPY"]
                },
                "description": "Analyze Apple, Microsoft, and S&P 500"
            },
            "portfolio_advisory": {
                "request": {
                    "goal_text": "I want to save for my child's college education in 15 years",
                    "risk_level": 3
                },
                "description": "Create education savings strategy"
            },
            "quick_advice": {
                "request": {
                    "question": "Should I invest in tech stocks during market volatility?"
                },
                "description": "Get advice on sector allocation"
            }
        },
        "tips": [
            "Use specific financial goals for better portfolio recommendations",
            "Risk level 1=Conservative, 3=Balanced, 5=Aggressive",
            "Market analysis works best with 2-5 symbols",
            "Ask specific questions for better quick advice"
        ],
        "timestamp": datetime.now().isoformat()
    }

# ================================
# Health Check
# ================================

@router.get(
    "/health",
    summary="CrewAI Health Check",
    description="Check if CrewAI system is healthy and ready",
    response_description="Health status of CrewAI components"
)
async def crew_health(req: Request):
    """Health check for CrewAI system"""
    try:
        # Test crew initialization
        status = crew_manager.get_crew_status()

        health_checks = {
            "crew_initialized": status.get("status") == "ready",
            "agents_count": status.get("crew_size", 0),
            "process_type": status.get("process", "unknown")
        }

        all_healthy = all(health_checks.values())

        return {
            "health_status": "healthy" if all_healthy else "unhealthy",
            "checks": health_checks,
            "message": "CrewAI system is operational" if all_healthy else "CrewAI system has issues",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"CrewAI health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "health_status": "unhealthy",
                "error": str(e),
                "message": "CrewAI system is not available",
                "timestamp": datetime.now().isoformat()
            }
        )