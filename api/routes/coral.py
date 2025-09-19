"""
Coral Protocol Integration Routes

Provides API endpoints for Coral Studio integration, agent registration,
and network discovery. These endpoints enable visibility and orchestration
of agents within the Coral Protocol ecosystem.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from agent.coral.registry import coral_registry
from api.middleware.rate_limiting import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/coral", tags=["Coral Protocol"])


@router.get(
    "/status",
    summary="Get Coral Registry Status",
    description="Get comprehensive status of all agents registered with Coral Server",
    response_description="Registry status including agent health and configuration"
)
async def get_coral_status(request: Request):
    """Get comprehensive status of the Coral registry and all registered agents."""
    try:
        status = await coral_registry.get_agent_registry_status()
        return JSONResponse(
            status_code=200,
            content=status
        )
    except Exception as e:
        logger.error(f"Failed to get coral status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve coral registry status: {str(e)}"
        )


@router.post(
    "/register",
    summary="Register Agents with Coral Server",
    description="Register all Neural Capital agents with the Coral Server for Studio visibility",
    response_description="Registration results for each agent"
)
@rate_limit(cost=5)  # Higher cost for registration operations
async def register_agents(request: Request, background_tasks: BackgroundTasks):
    """Register all agents with Coral Server for visibility in Coral Studio."""
    try:
        # Perform registration
        results = await coral_registry.register_all_agents()

        # Count successes and failures
        successful = sum(1 for success in results.values() if success)
        total = len(results)

        response_data = {
            "registration_status": "completed",
            "summary": {
                "total_agents": total,
                "successful_registrations": successful,
                "failed_registrations": total - successful,
                "success_rate": (successful / total) if total > 0 else 0
            },
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "coral_server_url": coral_registry.coral_server_url
        }

        # Determine HTTP status based on results
        if successful == total:
            status_code = 200
            response_data["message"] = "All agents registered successfully"
        elif successful > 0:
            status_code = 207  # Multi-status
            response_data["message"] = f"Partial success: {successful}/{total} agents registered"
        else:
            status_code = 500
            response_data["message"] = "All agent registrations failed"
            response_data["registration_status"] = "failed"

        return JSONResponse(
            status_code=status_code,
            content=response_data
        )

    except Exception as e:
        logger.error(f"Agent registration failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register agents with Coral Server: {str(e)}"
        )


@router.get(
    "/discover",
    summary="Discover Coral Network Agents",
    description="Discover all agents visible in the Coral Protocol network",
    response_description="List of discovered agents with their capabilities"
)
async def discover_agents(request: Request):
    """Discover all agents in the Coral Protocol network."""
    try:
        discovered_agents = await coral_registry.discover_coral_agents()

        return {
            "discovery_status": "success",
            "discovered_agents": discovered_agents,
            "agent_count": len(discovered_agents),
            "timestamp": datetime.now().isoformat(),
            "coral_server_url": coral_registry.coral_server_url
        }

    except Exception as e:
        logger.error(f"Agent discovery failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to discover agents in Coral network: {str(e)}"
        )


@router.get(
    "/health/{agent_id}",
    summary="Check Agent Health",
    description="Check health status of a specific registered agent",
    response_description="Health status and diagnostic information for the agent"
)
async def check_agent_health(agent_id: str, request: Request):
    """Check health status of a specific agent."""
    try:
        health = await coral_registry.check_agent_health(agent_id)

        if "error" in health:
            return JSONResponse(
                status_code=404,
                content={
                    "agent_id": agent_id,
                    "health_status": "not_found",
                    "error": health["error"],
                    "timestamp": datetime.now().isoformat()
                }
            )

        return {
            "agent_id": agent_id,
            "health_status": health.get("status", "unknown"),
            "health_details": health,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Health check failed for {agent_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check health for agent {agent_id}: {str(e)}"
        )


@router.get(
    "/studio-config",
    summary="Get Coral Studio Configuration",
    description="Get configuration needed for Coral Studio integration",
    response_description="Configuration parameters for connecting to Coral Studio"
)
async def get_studio_config(request: Request):
    """Get configuration for Coral Studio integration."""
    try:
        config = await coral_registry.get_coral_studio_config()

        return {
            "studio_config": config,
            "generated_at": datetime.now().isoformat(),
            "config_version": "1.0",
            "instructions": {
                "setup": [
                    "1. Ensure Coral Server is running at the specified URL",
                    "2. Register agents using the /coral/register endpoint",
                    "3. Use the provided configuration in Coral Studio",
                    "4. Agents will be visible and orchestrable in Studio"
                ],
                "endpoints": {
                    "register_agents": "/api/v1/coral/register",
                    "check_status": "/api/v1/coral/status",
                    "discover_network": "/api/v1/coral/discover"
                }
            }
        }

    except Exception as e:
        logger.error(f"Failed to generate studio config: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Coral Studio configuration: {str(e)}"
        )


@router.delete(
    "/unregister/{agent_id}",
    summary="Unregister Agent",
    description="Unregister a specific agent from the Coral Server",
    response_description="Unregistration result"
)
@rate_limit(cost=3)
async def unregister_agent(agent_id: str, request: Request):
    """Unregister a specific agent from Coral Server."""
    try:
        success = await coral_registry.unregister_agent(agent_id)

        if success:
            return {
                "unregistration_status": "success",
                "agent_id": agent_id,
                "message": f"Agent {agent_id} successfully unregistered",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "unregistration_status": "failed",
                    "agent_id": agent_id,
                    "error": f"Agent {agent_id} not found in registry",
                    "timestamp": datetime.now().isoformat()
                }
            )

    except Exception as e:
        logger.error(f"Failed to unregister {agent_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to unregister agent {agent_id}: {str(e)}"
        )


@router.get(
    "/network-health",
    summary="Check Network Health",
    description="Check health of the entire Coral Protocol network",
    response_description="Comprehensive network health status"
)
async def check_network_health(request: Request):
    """Check health of the entire Coral Protocol network."""
    try:
        # Get registry status
        registry_status = await coral_registry.get_agent_registry_status()

        # Get discovered agents
        discovered_agents = await coral_registry.discover_coral_agents()

        # Calculate network health metrics
        total_registered = registry_status["summary"]["total_agents"]
        healthy_registered = registry_status["summary"]["healthy_agents"]
        total_discovered = len(discovered_agents)

        network_health_score = (healthy_registered / total_registered) if total_registered > 0 else 0

        return {
            "network_health": {
                "overall_score": network_health_score,
                "status": (
                    "healthy" if network_health_score >= 0.8 else
                    "degraded" if network_health_score >= 0.5 else
                    "unhealthy"
                ),
                "coral_server_reachable": registry_status["registry_status"] != "critical"
            },
            "registered_agents": {
                "total": total_registered,
                "healthy": healthy_registered,
                "unhealthy": registry_status["summary"]["unhealthy_agents"]
            },
            "discovered_agents": {
                "total": total_discovered,
                "local_agents": sum(1 for agent in discovered_agents if agent.get("is_local", False)),
                "external_agents": sum(1 for agent in discovered_agents if not agent.get("is_local", False))
            },
            "coral_server": {
                "url": coral_registry.coral_server_url,
                "status": registry_status["registry_status"]
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Network health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check network health: {str(e)}"
        )


@router.get(
    "/capabilities",
    summary="List Agent Capabilities",
    description="Get a comprehensive list of all agent capabilities in the network",
    response_description="Structured list of capabilities by agent type"
)
async def list_capabilities(request: Request):
    """List all capabilities available in the Coral network."""
    try:
        # Get registered agents
        status = await coral_registry.get_agent_registry_status()

        capabilities_by_type = {}
        all_capabilities = set()

        for agent_id, agent_info in status["registered_agents"].items():
            agent_type = agent_info["agent_type"]
            capabilities = agent_info.get("capabilities", [])

            if agent_type not in capabilities_by_type:
                capabilities_by_type[agent_type] = {
                    "agents": [],
                    "capabilities": set()
                }

            capabilities_by_type[agent_type]["agents"].append({
                "agent_id": agent_id,
                "health": agent_info.get("health_status", "unknown"),
                "endpoint": agent_info.get("endpoint")
            })

            capabilities_by_type[agent_type]["capabilities"].update(capabilities)
            all_capabilities.update(capabilities)

        # Convert sets to lists for JSON serialization
        for agent_type in capabilities_by_type:
            capabilities_by_type[agent_type]["capabilities"] = list(capabilities_by_type[agent_type]["capabilities"])

        return {
            "capabilities_summary": {
                "total_unique_capabilities": len(all_capabilities),
                "agent_types": len(capabilities_by_type),
                "total_agents": sum(len(info["agents"]) for info in capabilities_by_type.values())
            },
            "capabilities_by_agent_type": capabilities_by_type,
            "all_capabilities": sorted(list(all_capabilities)),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to list capabilities: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve agent capabilities: {str(e)}"
        )