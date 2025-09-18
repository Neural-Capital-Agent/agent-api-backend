"""
Financial Agents API Routes - Main Router
Aggregates all agent-specific routers with proper organization and separation of concerns.
"""

from fastapi import APIRouter

# Import individual agent routers
from .data_agent import router as data_router
from .portfolio_agent import router as portfolio_router
from .planner_agent import router as planner_router
from .explainer_agent import router as explainer_router
from .workflows import router as workflows_router
from .system import router as system_router

# Create main agents router
router = APIRouter(tags=["Financial Agents"], prefix="/agents")

# Include all agent routers
router.include_router(data_router)
router.include_router(portfolio_router)
router.include_router(planner_router)
router.include_router(explainer_router)
router.include_router(workflows_router)
router.include_router(system_router)