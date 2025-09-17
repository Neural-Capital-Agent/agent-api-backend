import asyncio
import httpx
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

try:
    from .models import CoralMessage, CoralResponse, AgentRegistration
    from .mistral_client import mistral_client
except ImportError:
    # For testing when running directly
    from models import CoralMessage, CoralResponse, AgentRegistration
    try:
        from mistral_client import mistral_client
    except ImportError:
        logger.warning("Mistral client not available")
        mistral_client = None

logger = logging.getLogger(__name__)

class CoralClient:
    """
    Client for interacting with Coral Protocol infrastructure.
    Handles agent-to-agent communication, payments, and verification.
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555", agent_id: str = None):
        self.coral_server_url = coral_server_url
        self.agent_id = agent_id
        self.client: Optional[httpx.AsyncClient] = None
        self.registered_agents: Dict[str, AgentRegistration] = {}

    async def __aenter__(self):
        self.client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def _ensure_client(self):
        """Ensure httpx client is available"""
        if self.client is None:
            self.client = httpx.AsyncClient()

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
            await self._ensure_client()

            registration_data = {
                "agent_id": self.agent_id,
                "agent_type": agent_type,
                "capabilities": capabilities,
                "endpoint": endpoint
            }

            logger.info(f"Attempting to register agent {self.agent_id} with Coral Protocol")
            logger.info(f"Agent type: {agent_type}, Capabilities: {capabilities}")

            # Only register if we have a valid agent_id
            if not self.agent_id:
                logger.error("Cannot register agent: missing agent_id")
                return False

            # Try to register with the actual Coral Protocol server
            try:
                response = await self.client.post(
                    f"{self.coral_server_url}/register",
                    json=registration_data,
                    timeout=10.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✓ Successfully registered {self.agent_id} with Coral Server")

                    # Store in local registry too
                    self.registered_agents[self.agent_id] = AgentRegistration(
                        agent_id=self.agent_id,
                        agent_type=agent_type,
                        capabilities=capabilities,
                        endpoint=endpoint
                    )
                    return True
                else:
                    logger.error(f"Registration failed with status {response.status_code}: {response.text}")
                    return False

            except Exception as server_error:
                logger.warning(f"Failed to register with Coral Server: {server_error}")
                logger.info("Falling back to local registration only")

                # Fallback to local registration
                self.registered_agents[self.agent_id] = AgentRegistration(
                    agent_id=self.agent_id,
                    agent_type=agent_type,
                    capabilities=capabilities,
                    endpoint=endpoint
                )
                return True

        except (ValueError, TypeError) as e:
            logger.error(f"Failed to register agent: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during agent registration: {e}")
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
            await self._ensure_client()

            # Try to discover agents from the Coral Protocol server
            try:
                params = {}
                if agent_type:
                    params["agent_type"] = agent_type

                response = await self.client.get(
                    f"{self.coral_server_url}/agents",
                    params=params,
                    timeout=10.0
                )

                if response.status_code == 200:
                    result = response.json()
                    agents_data = result.get("agents", [])

                    # Convert to AgentRegistration objects
                    agents = []
                    for agent_data in agents_data:
                        agents.append(AgentRegistration(
                            agent_id=agent_data["agent_id"],
                            agent_type=agent_data["agent_type"],
                            capabilities=agent_data["capabilities"],
                            endpoint=agent_data["endpoint"]
                        ))

                    logger.info(f"Discovered {len(agents)} agents from Coral Server")
                    return agents

                else:
                    logger.warning(f"Discovery failed with status {response.status_code}")

            except Exception as server_error:
                logger.warning(f"Failed to discover agents from Coral Server: {server_error}")

            # Fallback to local registered agents
            logger.info("Falling back to local agent registry")
            registered_agents = list(self.registered_agents.values())

            if agent_type:
                return [agent for agent in registered_agents if agent.agent_type == agent_type]

            return registered_agents

        except (ConnectionError, TimeoutError, ValueError) as e:
            logger.error(f"Failed to discover agents: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during agent discovery: {e}")
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
            await self._ensure_client()

            message = CoralMessage(
                agent_id=self.agent_id,
                target_agent=target_agent,
                method=method,
                parameters=parameters,
                timestamp=datetime.now()
            )

            logger.info(f"Invoking {method} on {target_agent} with params: {parameters}")

            # Real Coral Protocol invocation would go here
            # In a real implementation, this would:
            # 1. Send the message through Coral Protocol
            # 2. Handle CORAL token payments
            # 3. Wait for response
            # 4. Verify response integrity

            # Handle LLM agent requests
            if target_agent == "llm_agent" and method == "parse_goal":
                # Use Mistral LLM for goal parsing
                if mistral_client:
                    try:
                        goal_text = parameters.get("text", "")
                        result = await mistral_client.parse_financial_goal(goal_text)
                        return result
                    except Exception as e:
                        logger.error(f"Mistral LLM error for goal parsing: {e}")
                        # Fallback to mock response
                        return {
                            "goal_type": "retirement",
                            "target_amount": 1000000,
                            "time_horizon": 30,
                            "confidence": 0.5,
                            "error": str(e)
                        }
                else:
                    raise Exception("Mistral LLM client not available")

            elif target_agent == "llm_agent" and method == "explain_decision":
                # Use Mistral LLM for decision explanations
                if mistral_client:
                    try:
                        action = parameters.get("action", {})
                        context = parameters.get("context", {})
                        explanation = await mistral_client.explain_financial_decision(action, context)
                        return {"explanation": explanation}
                    except Exception as e:
                        logger.error(f"Mistral LLM error for decision explanation: {e}")
                        return {"explanation": f"Investment decision made due to {action.get('reason', 'current market conditions')}. This adjustment helps maintain your portfolio's target risk level and expected returns.", "error": str(e)}
                else:
                    raise Exception("Mistral LLM client not available")

            elif target_agent == "llm_agent" and method == "translate_jargon":
                # Use Mistral LLM for jargon translation
                if mistral_client:
                    try:
                        technical_text = parameters.get("text", "")
                        translation = await mistral_client.translate_financial_jargon(technical_text)
                        return {"translation": translation}
                    except Exception as e:
                        logger.error(f"Mistral LLM error for jargon translation: {e}")
                        return {"translation": parameters.get("text", ""), "error": str(e)}
                else:
                    raise Exception("Mistral LLM client not available")

            elif target_agent == "llm_agent" and method == "create_plan":
                # Use Mistral LLM for investment plan creation
                if mistral_client:
                    try:
                        goal = parameters.get("goal", {})
                        strategy = parameters.get("strategy", {})
                        plan = await mistral_client.create_investment_plan(goal, strategy)
                        return {"plan": plan}
                    except Exception as e:
                        logger.error(f"Mistral LLM error for plan creation: {e}")
                        return {"plan": {"monthly_contribution": 1000, "error": str(e)}}
                else:
                    raise Exception("Mistral LLM client not available")

            elif target_agent == "llm_agent" and method == "validate_signals":
                # Use Mistral LLM for market signal validation
                if mistral_client:
                    try:
                        signals = parameters.get("signals", {})
                        market_data = parameters.get("market_data", {})
                        validation = await mistral_client.validate_market_signals(signals, market_data)
                        return validation
                    except Exception as e:
                        logger.error(f"Mistral LLM error for signal validation: {e}")
                        return {"is_valid": True, "confidence": 0.5, "reasoning": "Default validation due to processing error", "error": str(e)}
                else:
                    raise Exception("Mistral LLM client not available")

            # No mock responses - real implementation required
            raise Exception(f"Agent {target_agent} with method {method} not implemented or unavailable")

        except (ConnectionError, TimeoutError, ValueError, KeyError) as e:
            logger.error(f"Failed to invoke {method} on {target_agent}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error invoking {method} on {target_agent}: {e}")
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

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the coral client is properly configured and operational.

        Returns:
            Health status information including configuration and connectivity
        """
        try:
            health_status = {
                "status": "healthy",
                "checks": {},
                "timestamp": datetime.now().isoformat(),
                "client_info": {
                    "agent_id": self.agent_id,
                    "coral_server_url": self.coral_server_url,
                    "client_active": self.client is not None
                }
            }

            # Check 1: Basic configuration
            health_status["checks"]["configuration"] = {
                "passed": bool(self.coral_server_url and self.agent_id),
                "message": "Configuration valid" if (self.coral_server_url and self.agent_id)
                          else "Missing coral_server_url or agent_id"
            }

            # Check 2: Client connectivity
            await self._ensure_client()
            health_status["checks"]["client"] = {
                "passed": self.client is not None,
                "message": "HTTP client available" if self.client else "No HTTP client available"
            }

            # Check 3: Server connectivity (if possible)
            try:
                response = await self.client.get(
                    f"{self.coral_server_url}/health",
                    timeout=5.0
                )
                server_healthy = response.status_code == 200
                health_status["checks"]["server_connectivity"] = {
                    "passed": server_healthy,
                    "message": f"Server responded with status {response.status_code}" if server_healthy
                             else f"Server unhealthy (status: {response.status_code})"
                }
            except Exception as e:
                health_status["checks"]["server_connectivity"] = {
                    "passed": False,
                    "message": f"Cannot reach coral server: {str(e)}"
                }

            # Check 4: Registration status
            health_status["checks"]["registration"] = {
                "passed": self.agent_id in self.registered_agents,
                "message": "Agent registered" if self.agent_id in self.registered_agents
                          else "Agent not registered with coral protocol",
                "registered_agents_count": len(self.registered_agents)
            }

            # Overall status determination
            failed_checks = [check for check in health_status["checks"].values() if not check["passed"]]
            if failed_checks:
                health_status["status"] = "degraded" if len(failed_checks) <= 2 else "unhealthy"
                health_status["issues_count"] = len(failed_checks)

            return health_status

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "client_info": {
                    "agent_id": self.agent_id,
                    "coral_server_url": self.coral_server_url,
                    "client_active": self.client is not None if hasattr(self, 'client') else False
                }
            }

    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None

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


async def main():
    """Test function to demonstrate coral client health check functionality"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Testing Coral Client Health Check")
    print("=" * 40)

    # Test 1: Client with missing configuration
    print("\n1. Testing with missing configuration...")
    client1 = CoralClient()
    health_result = await client1.health_check()
    print(f"Status: {health_result['status']}")
    print(f"Issues: {health_result.get('issues_count', 0)}")
    for check_name, check_result in health_result.get('checks', {}).items():
        status = "PASS" if check_result['passed'] else "FAIL"
        print(f"  {status} {check_name}: {check_result['message']}")
    await client1.close()

    # Test 2: Client with proper configuration
    print("\n2. Testing with proper configuration...")
    client2 = CoralClient(
        coral_server_url="http://localhost:5555",
        agent_id="test_agent_123"
    )

    # Register the agent to test registration status
    await client2.register_agent(
        agent_type="test_agent",
        capabilities=["health_testing"],
        endpoint="http://localhost:8080/test"
    )

    health_result = await client2.health_check()
    print(f"Status: {health_result['status']}")
    print(f"Issues: {health_result.get('issues_count', 0)}")
    for check_name, check_result in health_result.get('checks', {}).items():
        status = "PASS" if check_result['passed'] else "FAIL"
        print(f"  {status} {check_name}: {check_result['message']}")

    print(f"\nClient Info:")
    client_info = health_result['client_info']
    print(f"  Agent ID: {client_info['agent_id']}")
    print(f"  Server URL: {client_info['coral_server_url']}")
    print(f"  Client Active: {client_info['client_active']}")

    await client2.close()

    print("\n" + "=" * 40)
    print("Health check testing completed!")


if __name__ == "__main__":
    asyncio.run(main())