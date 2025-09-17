"""
Coral Registry Service - Handles agent registration with Coral Studio/Server
for visibility and orchestration in the Coral Protocol ecosystem.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .coral_client import CoralClient
from .data_agent import DataAgent
from .portfolio_agent import PortfolioAgent
from .planner_agent import PlannerAgent
from .explainability_agent import ExplainabilityAgent

logger = logging.getLogger(__name__)


@dataclass
class AgentEndpoint:
    """Configuration for agent endpoint registration"""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    endpoint_url: str
    health_endpoint: str
    description: str


class CoralRegistry:
    """
    Service for registering and managing agents with Coral Studio/Server.
    Ensures agents are visible and properly configured for orchestration.
    """

    def __init__(self, coral_server_url: str = None, api_base_url: str = None):
        # Import here to avoid circular imports
        from core.config import settings

        self.coral_server_url = coral_server_url or settings.CORAL_SERVER_URL
        self.api_base_url = api_base_url or settings.CORAL_API_BASE_URL
        self.registered_agents: Dict[str, AgentEndpoint] = {}
        self.coral_client = CoralClient(self.coral_server_url, "coral_registry")

    def _get_agent_configurations(self) -> List[AgentEndpoint]:
        """Define agent configurations for registration with Coral Studio"""
        base_api = f"{self.api_base_url}/api/v1"

        return [
            AgentEndpoint(
                agent_id="data_agent",
                agent_type="data_provider",
                capabilities=[
                    "real_time_market_data",
                    "macro_economic_indicators",
                    "market_context_analysis",
                    "signal_validation",
                    "asset_universe_data"
                ],
                endpoint_url=f"{base_api}/agents/data",
                health_endpoint=f"{base_api}/agents/data/health",
                description="Real-time financial data aggregation and macro-economic indicator collection"
            ),
            AgentEndpoint(
                agent_id="portfolio_agent",
                agent_type="portfolio_optimizer",
                capabilities=[
                    "portfolio_optimization",
                    "risk_based_allocation",
                    "dynamic_rebalancing",
                    "performance_analytics",
                    "backtest_analysis"
                ],
                endpoint_url=f"{base_api}/agents/portfolio",
                health_endpoint=f"{base_api}/agents/portfolio/health",
                description="Algorithmic portfolio optimization and dynamic rebalancing"
            ),
            AgentEndpoint(
                agent_id="planner_agent",
                agent_type="financial_planner",
                capabilities=[
                    "goal_parsing",
                    "strategy_generation",
                    "lifecycle_planning",
                    "natural_language_processing",
                    "investment_planning"
                ],
                endpoint_url=f"{base_api}/agents/planner",
                health_endpoint=f"{base_api}/agents/planner/health",
                description="Natural language goal interpretation and lifecycle-based investment planning"
            ),
            AgentEndpoint(
                agent_id="explainability_agent",
                agent_type="explanation_generator",
                capabilities=[
                    "decision_explanation",
                    "jargon_translation",
                    "risk_communication",
                    "plain_english_conversion",
                    "decision_rationale"
                ],
                endpoint_url=f"{base_api}/agents/explainer",
                health_endpoint=f"{base_api}/agents/explainer/health",
                description="Financial jargon translation and decision rationale generation"
            )
        ]

    async def register_all_agents(self) -> Dict[str, bool]:
        """
        Register all agents with Coral Server for Studio visibility.

        Returns:
            Dict mapping agent_id to registration success status
        """
        results = {}
        agent_configs = self._get_agent_configurations()

        logger.info(f"Registering {len(agent_configs)} agents with Coral Server at {self.coral_server_url}")

        for config in agent_configs:
            try:
                # Register agent with Coral Protocol
                success = await self.coral_client.register_agent(
                    agent_type=config.agent_type,
                    capabilities=config.capabilities,
                    endpoint=config.endpoint_url
                )

                if success:
                    self.registered_agents[config.agent_id] = config
                    logger.info(f"✓ Successfully registered {config.agent_id} ({config.agent_type})")
                else:
                    logger.error(f"✗ Failed to register {config.agent_id}")

                results[config.agent_id] = success

            except Exception as e:
                logger.error(f"✗ Error registering {config.agent_id}: {e}")
                results[config.agent_id] = False

        # Log summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        logger.info(f"Agent registration complete: {successful}/{total} agents registered successfully")

        return results

    async def check_agent_health(self, agent_id: str) -> Dict[str, Any]:
        """Check health status of a registered agent"""
        if agent_id not in self.registered_agents:
            return {"error": f"Agent {agent_id} not registered"}

        config = self.registered_agents[agent_id]

        try:
            # Use coral client to check agent health
            health = await self.coral_client.invoke_agent(
                target_agent=agent_id,
                method="health_check",
                parameters={}
            )
            return health
        except Exception as e:
            logger.error(f"Health check failed for {agent_id}: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_agent_registry_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all registered agents"""
        status = {
            "registry_status": "operational",
            "coral_server_url": self.coral_server_url,
            "api_base_url": self.api_base_url,
            "registered_agents": {},
            "summary": {
                "total_agents": len(self.registered_agents),
                "healthy_agents": 0,
                "unhealthy_agents": 0
            },
            "timestamp": datetime.now().isoformat()
        }

        # Check health of all registered agents
        for agent_id, config in self.registered_agents.items():
            try:
                health = await self.check_agent_health(agent_id)
                is_healthy = health.get("status") == "healthy"

                status["registered_agents"][agent_id] = {
                    "agent_type": config.agent_type,
                    "capabilities": config.capabilities,
                    "endpoint": config.endpoint_url,
                    "health_status": health.get("status", "unknown"),
                    "description": config.description,
                    "is_healthy": is_healthy
                }

                if is_healthy:
                    status["summary"]["healthy_agents"] += 1
                else:
                    status["summary"]["unhealthy_agents"] += 1

            except Exception as e:
                logger.error(f"Failed to get status for {agent_id}: {e}")
                status["registered_agents"][agent_id] = {
                    "agent_type": config.agent_type,
                    "error": str(e),
                    "is_healthy": False
                }
                status["summary"]["unhealthy_agents"] += 1

        # Determine overall registry health
        if status["summary"]["unhealthy_agents"] > 0:
            if status["summary"]["healthy_agents"] == 0:
                status["registry_status"] = "critical"
            else:
                status["registry_status"] = "degraded"

        return status

    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from Coral Server"""
        if agent_id not in self.registered_agents:
            logger.warning(f"Agent {agent_id} not found in registry")
            return False

        try:
            # In a full implementation, this would call Coral Server to unregister
            # For now, just remove from local registry
            del self.registered_agents[agent_id]
            logger.info(f"✓ Unregistered {agent_id} from coral registry")
            return True
        except Exception as e:
            logger.error(f"Failed to unregister {agent_id}: {e}")
            return False

    async def discover_coral_agents(self) -> List[Dict[str, Any]]:
        """Discover all agents visible in the Coral network"""
        try:
            discovered_agents = await self.coral_client.discover_agents()

            agent_list = []
            for agent in discovered_agents:
                agent_list.append({
                    "agent_id": agent.agent_id,
                    "agent_type": agent.agent_type,
                    "capabilities": agent.capabilities,
                    "endpoint": agent.endpoint,
                    "is_local": agent.agent_id in self.registered_agents
                })

            logger.info(f"Discovered {len(agent_list)} agents in Coral network")
            return agent_list

        except Exception as e:
            logger.error(f"Failed to discover coral agents: {e}")
            return []

    async def get_coral_studio_config(self) -> Dict[str, Any]:
        """Generate configuration for Coral Studio integration"""
        return {
            "coral_server": {
                "url": self.coral_server_url,
                "status": "connected" if self.registered_agents else "disconnected"
            },
            "api_server": {
                "url": self.api_base_url,
                "endpoints": {
                    "registry_status": f"{self.api_base_url}/api/v1/coral/status",
                    "agent_health": f"{self.api_base_url}/api/v1/coral/health",
                    "discovery": f"{self.api_base_url}/api/v1/coral/discover"
                }
            },
            "agents": [
                {
                    "id": config.agent_id,
                    "type": config.agent_type,
                    "capabilities": config.capabilities,
                    "endpoint": config.endpoint_url,
                    "health_endpoint": config.health_endpoint,
                    "description": config.description
                }
                for config in self.registered_agents.values()
            ],
            "session_config": {
                "auto_register": True,
                "health_check_interval": 30,
                "reconnect_on_failure": True
            }
        }

    async def close(self):
        """Clean shutdown of registry"""
        try:
            await self.coral_client.close()
            logger.info("Coral registry closed successfully")
        except Exception as e:
            logger.error(f"Error closing coral registry: {e}")


# Global registry instance
coral_registry = CoralRegistry()


async def main():
    """Test function to demonstrate coral registry functionality"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Testing Coral Registry Service")
    print("=" * 40)

    try:
        # Test agent registration
        print("\n1. Registering agents with Coral Server...")
        results = await coral_registry.register_all_agents()

        for agent_id, success in results.items():
            status = "SUCCESS" if success else "FAILED"
            print(f"  {status}: {agent_id}")

        # Test registry status
        print("\n2. Getting registry status...")
        status = await coral_registry.get_agent_registry_status()
        print(f"  Registry Status: {status['registry_status']}")
        print(f"  Total Agents: {status['summary']['total_agents']}")
        print(f"  Healthy: {status['summary']['healthy_agents']}")
        print(f"  Unhealthy: {status['summary']['unhealthy_agents']}")

        # Test discovery
        print("\n3. Discovering Coral network agents...")
        discovered = await coral_registry.discover_coral_agents()
        print(f"  Found {len(discovered)} agents in network")

        for agent in discovered:
            print(f"    - {agent['agent_id']} ({agent['agent_type']})")

        # Test Coral Studio config generation
        print("\n4. Generating Coral Studio configuration...")
        studio_config = await coral_registry.get_coral_studio_config()
        print(f"  Coral Server: {studio_config['coral_server']['url']}")
        print(f"  API Server: {studio_config['api_server']['url']}")
        print(f"  Configured Agents: {len(studio_config['agents'])}")

    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        await coral_registry.close()

    print("\n" + "=" * 40)
    print("Coral registry testing completed!")


if __name__ == "__main__":
    asyncio.run(main())