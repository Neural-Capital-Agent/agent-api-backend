from fastapi import APIRouter
from api.routes import stocks, alpaca, economy, user, llm, agents, crew, dashboard, plan_creator, tier_management

api_router = APIRouter()

# Core API routes
api_router.include_router(user.router, prefix="/user")
api_router.include_router(stocks.router, prefix="/stocks")
api_router.include_router(alpaca.router, prefix="/alpaca")
api_router.include_router(economy.router, prefix="/economy")

# Dashboard routes
api_router.include_router(dashboard.router)  # Dashboard market data

# AI/LLM routes
api_router.include_router(llm.router)  # LLM operations with rate limiting
api_router.include_router(agents.router)  # Financial agents endpoints
api_router.include_router(plan_creator.router)  # Plan Creator with Agent 2 & 3 integration

# CrewAI Workflows
api_router.include_router(crew.router)  # CrewAI orchestrated workflows


# Tier Management
api_router.include_router(tier_management.router)  # User tier and feature access management


