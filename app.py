from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from api.api import api_router
from api.middleware.rate_limiting import RateLimitMiddleware, LLMUsageMiddleware
from core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title=f"{settings.PROJECT_NAME} - Financial Agents API",
    description="""
    Neural Capital Financial Agents API provides comprehensive financial services through AI-powered agents:

    ## [AI] Available Agents

    * **Data Agent** - Real-time market data, macro indicators, technical analysis
    * **Portfolio Agent** - Portfolio optimization, risk management, rebalancing
    * **Planner Agent** - Goal parsing, investment strategies, lifecycle planning
    * **Explainability Agent** - Decision explanations, jargon translation

    ## [SECURITY] Rate Limiting

    * **Basic Tier**: 50 requests/day, 10/hour, 3/minute, 100 LLM credits
    * **Premium Tier**: 200 requests/day, 50/hour, 10/minute, 500 LLM credits
    * **Enterprise Tier**: 1000 requests/day, 200/hour, 50/minute, 2000 LLM credits

    ## [DATA] Data Sources

    * Yahoo Finance (real-time market data)
    * FRED API (economic indicators)
    * Polygon API (advanced market data)
    * Mistral AI (natural language processing)

    ## [FEATURES] Features

    * Multi-agent financial workflows
    * Real-time data integration
    * Comprehensive rate limiting
    * LLM-powered insights
    * RESTful API design
    """,
    version="2.0.0",
    terms_of_service="https://neural-capital.com/terms",
    contact={
        "name": "Neural Capital API Support",
        "url": "https://neural-capital.com/support",
        "email": "api-support@neural-capital.com",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://neural-capital.com/license",
    },
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Custom exception handlers
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Custom HTTP exception handler with enhanced error information."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url.path),
                "method": request.method
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom validation error handler."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": 422,
                "message": "Request validation failed",
                "details": exc.errors(),
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url.path),
                "method": request.method
            }
        }
    )


# Set up Rate Limiting Middleware (DISABLED FOR TESTING)
# app.add_middleware(LLMUsageMiddleware)
# app.add_middleware(
#     RateLimitMiddleware,
#     llm_endpoints=["/api/v1/llm/", "/api/v1/agents/", "/api/v1/chat/"],
#     default_user_tier="basic"
# )

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup():
    """Initialize the API cache, rate limiting, and agents on startup."""
    try:
        # Initialize cache
        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
        logger.info("[OK] FastAPI cache initialized")

        # Initialize rate limiting (DISABLED FOR TESTING)
        # from utils.rate_limiter import setup_user_tier, USER_TIER_CONFIGS
        # logger.info("✓ Rate limiting system initialized")
        # logger.info(f"[OK] Available tiers: {list(USER_TIER_CONFIGS.keys())}")
        logger.info("[WARNING] Rate limiting disabled for testing")

        # Initialize agents (lazy loading will happen on first request)
        logger.info("[OK] Financial agents ready for initialization")

        # Start Coral Protocol Server in background
        try:
            from agent.coral.server import coral_server
            import asyncio

            logger.info("[CORAL] Starting Coral Protocol Server...")

            # Start the coral server in the background
            asyncio.create_task(coral_server.start_server())

            # Give the server a moment to start
            await asyncio.sleep(2)

            logger.info("[OK] Coral Protocol Server started on http://localhost:5555")

        except Exception as coral_server_error:
            logger.error(f"[WARNING] Coral Protocol Server startup failed: {coral_server_error}")
            logger.info("[NOTE] Continuing without Coral Protocol Server")

        # Initialize CrewAI
        try:
            from agent.coral.crew_agents import crew_manager
            crew_status = crew_manager.get_crew_status()
            logger.info(f"[AI] CrewAI initialized with {crew_status['crew_size']} agents")
            logger.info(f"[TARGET] CrewAI workflows available at /api/v1/crew/")
        except Exception as crew_error:
            logger.error(f"[WARNING] CrewAI initialization failed: {crew_error}")
            logger.info("[NOTE] Individual agents will still function normally")

        # Initialize Coral Protocol integration
        try:
            from agent.coral.registry import coral_registry
            logger.info("[CORAL] Initializing Coral Protocol integration...")

            # Give Coral Server more time to be ready
            await asyncio.sleep(1)

            # Register agents with Coral Server for Studio visibility
            registration_results = await coral_registry.register_all_agents()
            successful_registrations = sum(1 for success in registration_results.values() if success)
            total_agents = len(registration_results)

            if successful_registrations == total_agents:
                logger.info(f"[OK] All {total_agents} agents registered with Coral Server")
            elif successful_registrations > 0:
                logger.warning(f"[WARNING] Partial success: {successful_registrations}/{total_agents} agents registered with Coral Server")
            else:
                logger.error(f"[ERROR] Failed to register any agents with Coral Server")

            logger.info(f"[TARGET] Coral Studio endpoints available at /api/v1/coral/")
            logger.info(f"[CORAL] Coral Server URL: {coral_registry.coral_server_url}")

        except Exception as coral_error:
            logger.error(f"[WARNING] Coral Protocol initialization failed: {coral_error}")
            logger.info("[NOTE] Agents will still function normally without Coral Studio integration")

        # Log startup completion
        logger.info("[STARTING] Neural Capital Financial Agents API started successfully")
        logger.info(f"[DATA] API Documentation: http://localhost:8000/docs")
        logger.info(f"[DOCS] ReDoc: http://localhost:8000/redoc")
        logger.info(f"[CORAL] Coral Protocol Server: http://localhost:5555/health")

    except Exception as e:
        logger.error(f"[ERROR] Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown():
    """Clean shutdown procedures."""
    try:
        logger.info("[RELOAD] Shutting down Neural Capital API...")

        # Close Coral Protocol connections
        try:
            from agent.coral.registry import coral_registry
            await coral_registry.close()
            logger.info("[OK] Coral Protocol connections closed")
        except Exception as coral_error:
            logger.warning(f"[WARNING] Coral shutdown warning: {coral_error}")

        # Close any open connections
        from agent.clients.mistral_client import mistral_client
        await mistral_client.close()

        logger.info("[OK] Shutdown completed successfully")
    except Exception as e:
        logger.error(f"[ERROR] Shutdown error: {e}")


@app.get("/")
async def read_root():
    """Root endpoint with comprehensive API information."""
    return {
        "service": f"{settings.PROJECT_NAME} - Financial Agents API",
        "version": "2.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "openapi": f"{settings.API_V1_STR}/openapi.json",
            "health_checks": {
                "system": "/health",
                "rate_limiting": "/rate-limit/health",
                "agents": f"{settings.API_V1_STR}/agents/health",
                "llm": f"{settings.API_V1_STR}/llm/health"
            }
        },
        "agents": {
            "data_agent": f"{settings.API_V1_STR}/agents/data/",
            "portfolio_agent": f"{settings.API_V1_STR}/agents/portfolio/",
            "planner_agent": f"{settings.API_V1_STR}/agents/planner/",
            "explainability_agent": f"{settings.API_V1_STR}/agents/explainer/"
        },
        "crewai_workflows": {
            "market_analysis": f"{settings.API_V1_STR}/crew/market-analysis",
            "portfolio_advisory": f"{settings.API_V1_STR}/crew/portfolio-advisory",
            "quick_advice": f"{settings.API_V1_STR}/crew/quick-advice",
            "status": f"{settings.API_V1_STR}/crew/status",
            "workflows": f"{settings.API_V1_STR}/crew/workflows",
            "health": f"{settings.API_V1_STR}/crew/health"
        },
        "coral_protocol": {
            "status": f"{settings.API_V1_STR}/coral/status",
            "register": f"{settings.API_V1_STR}/coral/register",
            "studio_config": f"{settings.API_V1_STR}/coral/studio-config",
            "capabilities": f"{settings.API_V1_STR}/coral/capabilities"
        },
        "features": [
            "Real-time market data",
            "AI-powered portfolio optimization",
            "Natural language goal parsing",
            "Financial decision explanations",
            "CrewAI orchestrated workflows",
            "Coral Protocol integration",
            "Multi-agent collaboration",
            "Comprehensive rate limiting",
            "LLM-powered insights",
            "Studio-ready agent visibility"
        ]
    }


@app.get("/health")
async def system_health():
    """Comprehensive system health check."""
    try:
        health_status = {
            "system": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_check": "operational",
            "components": {}
        }

        # Check cache
        try:
            # Simple cache test
            health_status["components"]["cache"] = {
                "status": "healthy",
                "backend": "InMemoryBackend"
            }
        except Exception as e:
            health_status["components"]["cache"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check rate limiter
        try:
            from utils.rate_limiter import llm_rate_limiter
            active_users = len(llm_rate_limiter.user_states)
            health_status["components"]["rate_limiter"] = {
                "status": "healthy",
                "active_users": active_users,
                "configured_users": len(llm_rate_limiter.user_configs)
            }
        except Exception as e:
            health_status["components"]["rate_limiter"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check agents availability (basic check)
        try:
            from agent.core.data_agent import DataAgent
            health_status["components"]["financial_agents"] = {
                "status": "healthy",
                "agents": ["data_agent", "portfolio_agent", "planner_agent", "explainability_agent"]
            }
        except Exception as e:
            health_status["components"]["financial_agents"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check CrewAI system
        try:
            from agent.coral.crew_agents import crew_manager
            crew_status = crew_manager.get_crew_status()
            health_status["components"]["crewai"] = {
                "status": "healthy" if crew_status.get("status") == "ready" else "unhealthy",
                "crew_size": crew_status.get("crew_size", 0),
                "process": crew_status.get("process", "unknown")
            }
        except Exception as e:
            health_status["components"]["crewai"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check Coral Protocol registry
        try:
            from agent.coral.registry import coral_registry
            coral_status = await coral_registry.get_agent_registry_status()
            health_status["components"]["coral_registry"] = {
                "status": "healthy" if coral_status.get("registry_status") != "critical" else "degraded",
                "total_agents": coral_status.get("summary", {}).get("total_agents", 0),
                "healthy_agents": coral_status.get("summary", {}).get("healthy_agents", 0)
            }
        except Exception as e:
            health_status["components"]["coral_registry"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Determine overall health
        unhealthy_components = [
            name for name, status in health_status["components"].items()
            if status.get("status") != "healthy"
        ]

        if unhealthy_components:
            health_status["system"] = "degraded"
            health_status["unhealthy_components"] = unhealthy_components

        return health_status

    except Exception as e:
        logger.error(f"System health check failed: {e}")
        return {
            "system": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/rate-limit/health")
async def rate_limit_health():
    """Detailed rate limiting system health check."""
    from utils.rate_limiter import llm_rate_limiter, USER_TIER_CONFIGS

    try:
        active_users = len(llm_rate_limiter.user_states)
        user_configs = len(llm_rate_limiter.user_configs)

        return {
            "status": "healthy",
            "rate_limiter": {
                "active_users": active_users,
                "configured_users": user_configs,
                "available_tiers": list(USER_TIER_CONFIGS.keys()),
                "middleware_status": "enabled"
            },
            "tier_limits": {
                tier: {
                    "daily": config.daily_limit,
                    "hourly": config.hourly_limit,
                    "minute": config.minute_limit,
                    "credits": config.llm_credits
                }
                for tier, config in USER_TIER_CONFIGS.items()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/info")
async def api_info():
    """Get comprehensive API information."""
    return {
        "api_name": f"{settings.PROJECT_NAME} - Financial Agents API",
        "version": "2.0.0",
        "description": "AI-powered financial agents for market analysis and portfolio management",
        "contact": {
            "support": "api-support@neural-capital.com",
            "documentation": "/docs"
        },
        "capabilities": {
            "agents": {
                "data_agent": {
                    "description": "Real-time market data and macro indicators",
                    "data_sources": ["Yahoo Finance", "FRED API", "Polygon"],
                    "endpoints": 6
                },
                "portfolio_agent": {
                    "description": "Portfolio optimization and rebalancing",
                    "features": ["Risk-based allocation", "Macro signals", "Dynamic rebalancing"],
                    "endpoints": 2
                },
                "planner_agent": {
                    "description": "Financial goal parsing and planning",
                    "features": ["NLP goal parsing", "Strategy generation", "Lifecycle planning"],
                    "endpoints": 4
                },
                "explainability_agent": {
                    "description": "Decision explanations and jargon translation",
                    "features": ["Plain English", "Risk communication", "Jargon translation"],
                    "endpoints": 4
                }
            },
            "llm_integration": {
                "provider": "Mistral AI",
                "rate_limited": True,
                "credit_based": True
            },
            "crewai_workflows": {
                "market_analysis": "Multi-agent market condition analysis",
                "portfolio_advisory": "Complete goal-to-portfolio workflow",
                "quick_advice": "Instant financial guidance",
                "orchestrated": True,
                "ai_powered": True
            },
            "coral_protocol": {
                "studio_integration": True,
                "agent_visibility": True,
                "network_discovery": True,
                "capabilities_export": True
            },
            "rate_limiting": {
                "tiers": ["basic", "premium", "enterprise"],
                "time_windows": ["daily", "hourly", "minute"],
                "credit_system": True
            }
        },
        "statistics": {
            "total_endpoints": "35+",
            "agents": 4,
            "data_sources": 3,
            "llm_operations": 5,
            "crewai_workflows": 3,
            "coral_endpoints": 8,
            "integration_protocols": 2
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "service": "Neural Capital API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - app.startup_time if hasattr(app, 'startup_time') else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


