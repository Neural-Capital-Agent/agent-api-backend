import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

from .models import CoralMessage, CoralResponse, AgentRegistration

logger = logging.getLogger(__name__)

class CoralClient:
    """
    Client for interacting with Coral Protocol infrastructure.
    Handles agent-to-agent communication, payments, and verification.
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555", agent_id: str = None):
        self.coral_server_url = coral_server_url
        self.agent_id = agent_id
        self.session: Optional[aiohttp.ClientSession] = None
        self.registered_agents: Dict[str, AgentRegistration] = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _ensure_session(self):
        """Ensure aiohttp session is available"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def register_agent(self, agent_type: str, capabilities: List[str], endpoint: str) -> bool:
        """
        Register this agent with the Coral Protocol network.

        Args:
            agent_type: Type of agent (e.g., "data_agent", "portfolio_agent")
            capabilities: List of capabilities this agent provides
            endpoint: HTTP endpoint where this agent can be reached

        Returns:
            True if registration successful
        """
        try:
            await self._ensure_session()

            registration_data = {
                "agent_id": self.agent_id,
                "agent_type": agent_type,
                "capabilities": capabilities,
                "endpoint": endpoint
            }

            # For now, simulate registration (actual Coral Protocol integration would go here)
            logger.info(f"Registering agent {self.agent_id} with Coral Protocol")
            logger.info(f"Agent type: {agent_type}, Capabilities: {capabilities}")

            self.registered_agents[self.agent_id] = AgentRegistration(
                agent_id=self.agent_id,
                agent_type=agent_type,
                capabilities=capabilities,
                endpoint=endpoint
            )

            return True

        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            return False

    async def discover_agents(self, agent_type: Optional[str] = None) -> List[AgentRegistration]:
        """
        Discover other agents in the network.

        Args:
            agent_type: Filter by specific agent type

        Returns:
            List of available agents
        """
        try:
            await self._ensure_session()

            # For now, return mock agents (actual Coral Protocol discovery would go here)
            mock_agents = [
                AgentRegistration(
                    agent_id="data_agent_1",
                    agent_type="data_agent",
                    capabilities=["fetch_market_data", "fetch_macro_data", "validate_signals"],
                    endpoint="http://localhost:8000/data"
                ),
                AgentRegistration(
                    agent_id="portfolio_agent_1",
                    agent_type="portfolio_agent",
                    capabilities=["build_portfolio", "calculate_rebalancing", "backtest_strategy"],
                    endpoint="http://localhost:8001/portfolio"
                ),
                AgentRegistration(
                    agent_id="planner_agent_1",
                    agent_type="planner_agent",
                    capabilities=["parse_goal", "generate_strategy", "build_glide_path"],
                    endpoint="http://localhost:8002/planner"
                )
            ]

            if agent_type:
                return [agent for agent in mock_agents if agent.agent_type == agent_type]

            return mock_agents

        except Exception as e:
            logger.error(f"Failed to discover agents: {e}")
            return []

    async def invoke_agent(self, target_agent: str, method: str, parameters: Dict[str, Any]) -> Any:
        """
        Invoke a method on another agent through Coral Protocol.

        Args:
            target_agent: Target agent ID
            method: Method name to invoke
            parameters: Method parameters

        Returns:
            Response from target agent
        """
        try:
            await self._ensure_session()

            message = CoralMessage(
                agent_id=self.agent_id,
                target_agent=target_agent,
                method=method,
                parameters=parameters,
                timestamp=datetime.now()
            )

            logger.info(f"Invoking {method} on {target_agent} with params: {parameters}")

            # For now, simulate the call (actual Coral Protocol invocation would go here)
            # In a real implementation, this would:
            # 1. Send the message through Coral Protocol
            # 2. Handle CORAL token payments
            # 3. Wait for response
            # 4. Verify response integrity

            if target_agent == "data_agent" and method == "fetch_market_data":
                # Simulate data agent response
                return {
                    "symbol": parameters.get("ticker", "SPY"),
                    "price": 450.50,
                    "change": 2.30,
                    "change_percent": 0.51,
                    "timestamp": datetime.now().isoformat()
                }
            elif target_agent == "data_agent" and method == "validate_signals":
                return {"is_valid": True, "confidence": 0.85}
            elif target_agent == "portfolio_agent" and method == "get_decision_rationale":
                return {
                    "reason": "Rebalancing due to volatility spike",
                    "confidence": 0.78,
                    "supporting_data": {"vix": 28.5}
                }
            elif target_agent == "llm_agent" and method == "parse_goal":
                return {
                    "goal_type": "retirement",
                    "target_amount": 1000000,
                    "time_horizon": 30,
                    "confidence": 0.92
                }

            # Default mock response
            return {"status": "success", "data": parameters}

        except Exception as e:
            logger.error(f"Failed to invoke {method} on {target_agent}: {e}")
            raise

    async def query_agents(self, agent_ids: List[str], query: str = "status") -> Dict[str, Any]:
        """
        Query multiple agents for information.

        Args:
            agent_ids: List of agent IDs to query
            query: Query type

        Returns:
            Aggregated responses from agents
        """
        try:
            responses = {}

            for agent_id in agent_ids:
                try:
                    response = await self.invoke_agent(agent_id, query, {})
                    responses[agent_id] = response
                except Exception as e:
                    logger.error(f"Failed to query {agent_id}: {e}")
                    responses[agent_id] = {"error": str(e)}

            return responses

        except Exception as e:
            logger.error(f"Failed to query agents: {e}")
            return {}

    def create_verification_hash(self, data: Any, action_id: str) -> str:
        """
        Create a verification hash for blockchain storage.

        Args:
            data: Data to hash
            action_id: Associated action ID

        Returns:
            Verification hash
        """
        try:
            # Convert data to string representation
            data_str = json.dumps(data, sort_keys=True, default=str)
            combined = f"{action_id}:{data_str}:{datetime.now().isoformat()}"

            # Create SHA-256 hash
            return hashlib.sha256(combined.encode()).hexdigest()

        except Exception as e:
            logger.error(f"Failed to create verification hash: {e}")
            return ""

    async def verify_on_blockchain(self, verification_hash: str) -> bool:
        """
        Verify data integrity using Coral Protocol's blockchain layer.

        Args:
            verification_hash: Hash to verify

        Returns:
            True if verification successful
        """
        try:
            # For now, simulate blockchain verification
            logger.info(f"Verifying hash on blockchain: {verification_hash}")

            # In a real implementation, this would:
            # 1. Submit the hash to the blockchain
            # 2. Pay CORAL tokens for verification
            # 3. Wait for blockchain confirmation

            return True

        except Exception as e:
            logger.error(f"Blockchain verification failed: {e}")
            return False

    async def pay_coral_tokens(self, recipient: str, amount: float, service: str) -> bool:
        """
        Pay CORAL tokens for services.

        Args:
            recipient: Agent receiving payment
            amount: Amount of CORAL tokens
            service: Service being paid for

        Returns:
            True if payment successful
        """
        try:
            logger.info(f"Paying {amount} CORAL tokens to {recipient} for {service}")

            # For now, simulate payment
            # In a real implementation, this would:
            # 1. Check wallet balance
            # 2. Create blockchain transaction
            # 3. Wait for confirmation

            return True

        except Exception as e:
            logger.error(f"CORAL token payment failed: {e}")
            return False

    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
            self.session = None

    # Agent-specific helper methods
    async def get_market_context_from_data_agent(self, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive market context from Data Agent via Coral Protocol.

        Args:
            timestamp: Optional timestamp for historical context

        Returns:
            Market context data from Data Agent
        """
        try:
            return await self.invoke_agent(
                target_agent="data_agent",
                method="get_market_context",
                parameters={"timestamp": timestamp}
            )
        except Exception as e:
            logger.error(f"Failed to get market context from data agent: {e}")
            return {"error": str(e)}

    async def validate_macro_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate macro signals with Data Agent via Coral Protocol.

        Args:
            signals: Macro signals to validate

        Returns:
            Validation results
        """
        try:
            return await self.invoke_agent(
                target_agent="data_agent",
                method="validate_signals",
                parameters={"signals": signals}
            )
        except Exception as e:
            logger.error(f"Failed to validate macro signals: {e}")
            return {"error": str(e), "is_valid": False, "confidence": 0.0}

    async def get_portfolio_rationale(self, action_id: str) -> Dict[str, Any]:
        """
        Get decision rationale from Portfolio Agent via Coral Protocol.

        Args:
            action_id: ID of the action to explain

        Returns:
            Portfolio decision rationale
        """
        try:
            return await self.invoke_agent(
                target_agent="portfolio_agent",
                method="get_decision_rationale",
                parameters={"action_id": action_id}
            )
        except Exception as e:
            logger.error(f"Failed to get portfolio rationale: {e}")
            return {"error": str(e)}

    async def process_natural_language_goal(self, goal_text: str, context: str = "financial_planning") -> Dict[str, Any]:
        """
        Process natural language goal using LLM Agent via Coral Protocol.

        Args:
            goal_text: Natural language goal description
            context: Context for processing

        Returns:
            Processed goal parameters
        """
        try:
            return await self.invoke_agent(
                target_agent="llm_agent",
                method="parse_goal",
                parameters={"text": goal_text, "context": context}
            )
        except Exception as e:
            logger.error(f"Failed to process natural language goal: {e}")
            return {"error": str(e)}

    async def get_explanation_context(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather context for explanations from multiple agents via Coral Protocol.

        Args:
            action: Action to gather context for

        Returns:
            Comprehensive context from multiple agents
        """
        try:
            context = {}

            # Get market data context
            if action.get("requires_market_data", True):
                context["market_data"] = await self.get_market_context_from_data_agent()

            # Get portfolio context if action is portfolio-related
            if action.get("agent_source") == "portfolio_agent":
                context["portfolio_rationale"] = await self.get_portfolio_rationale(action.get("id", ""))

            # Get planning context if action is planner-related
            if action.get("agent_source") == "planner_agent" and action.get("goal_text"):
                context["goal_processing"] = await self.process_natural_language_goal(action["goal_text"])

            return context

        except Exception as e:
            logger.error(f"Failed to gather explanation context: {e}")
            return {"error": str(e)}

    async def cross_validate_decision(self, decision: Dict[str, Any], validators: List[str]) -> Dict[str, Any]:
        """
        Cross-validate decisions with multiple agents via Coral Protocol.

        Args:
            decision: Decision to validate
            validators: List of agent IDs to use as validators

        Returns:
            Validation results from multiple agents
        """
        try:
            validation_results = {}

            for validator in validators:
                try:
                    result = await self.invoke_agent(
                        target_agent=validator,
                        method="validate_decision",
                        parameters={"decision": decision}
                    )
                    validation_results[validator] = result
                except Exception as e:
                    logger.warning(f"Validation failed with {validator}: {e}")
                    validation_results[validator] = {"error": str(e), "valid": False}

            # Calculate overall validation score
            valid_results = [r for r in validation_results.values() if r.get("valid", False)]
            overall_score = len(valid_results) / len(validators) if validators else 0.0

            return {
                "individual_results": validation_results,
                "overall_validation_score": overall_score,
                "is_validated": overall_score >= 0.6  # 60% consensus required
            }

        except Exception as e:
            logger.error(f"Cross-validation failed: {e}")
            return {"error": str(e), "is_validated": False}

    async def get_agent_performance_metrics(self, agent_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific agent via Coral Protocol.

        Args:
            agent_id: Agent ID to get metrics for

        Returns:
            Performance metrics
        """
        try:
            return await self.invoke_agent(
                target_agent=agent_id,
                method="get_performance_metrics",
                parameters={}
            )
        except Exception as e:
            logger.error(f"Failed to get performance metrics for {agent_id}: {e}")
            return {"error": str(e)}

    async def health_check_all_agents(self) -> Dict[str, Any]:
        """
        Perform health check on all registered agents via Coral Protocol.

        Returns:
            Health status of all agents
        """
        try:
            agents = await self.discover_agents()
            health_results = {}

            for agent in agents:
                try:
                    health = await self.invoke_agent(
                        target_agent=agent.agent_id,
                        method="health_check",
                        parameters={}
                    )
                    health_results[agent.agent_id] = {
                        "status": health.get("status", "unknown"),
                        "agent_type": agent.agent_type,
                        "last_seen": datetime.now().isoformat()
                    }
                except Exception as e:
                    health_results[agent.agent_id] = {
                        "status": "unhealthy",
                        "error": str(e),
                        "agent_type": agent.agent_type,
                        "last_seen": None
                    }

            # Calculate network health
            healthy_agents = sum(1 for h in health_results.values() if h.get("status") == "healthy")
            total_agents = len(health_results)
            network_health = healthy_agents / total_agents if total_agents > 0 else 0

            return {
                "agent_health": health_results,
                "network_health_score": network_health,
                "healthy_agents": healthy_agents,
                "total_agents": total_agents,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Network health check failed: {e}")
            return {"error": str(e), "network_health_score": 0.0}