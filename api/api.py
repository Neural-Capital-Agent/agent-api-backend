from fastapi import APIRouter
from api.routes import stocks, alpaca, economy, user, llm, agents, coral, crew

api_router = APIRouter()

# Core API routes
api_router.include_router(user.router, prefix="/user")
api_router.include_router(stocks.router, prefix="/stocks")
api_router.include_router(alpaca.router, prefix="/alpaca")
api_router.include_router(economy.router, prefix="/economy")

# AI/LLM routes
api_router.include_router(llm.router)  # LLM operations with rate limiting
api_router.include_router(agents.router)  # Financial agents endpoints

# CrewAI Workflows
api_router.include_router(crew.router)  # CrewAI orchestrated workflows

# Coral Protocol Integration
api_router.include_router(coral.router)  # Coral Studio integration and agent registry


