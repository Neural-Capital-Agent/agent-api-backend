import asyncio
import httpx
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
from pathlib import Path

# Coral v01 SDK imports
try:
    from coral_sdk import CoralClient as OfficialCoralClient, CoralAgent
    from coral_sdk.types import AgentRegistration as SDKAgentRegistration
    CORAL_SDK_AVAILABLE = True
except ImportError:
    CORAL_SDK_AVAILABLE = False
    logging.warning("Coral SDK not available, using fallback implementation")

try:
    from ..shared.models import CoralMessage, CoralResponse, AgentRegistration
    from ..clients.mistral_client import mistral_client
except ImportError:
    # For testing when running directly
    from agent.shared.models import CoralMessage, CoralResponse, AgentRegistration
    try:
        from agent.clients.mistral_client import mistral_client
    except ImportError:
        mistral_client = None

logger = logging.getLogger(__name__)

class CoralClient:
    """
    Client for interacting with Coral Protocol infrastructure.
    Handles agent-to-agent communication, payments, and verification.
    Uses official Coral v01 SDK when available, falls back to custom implementation.
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555", agent_id: str = None):
        self.coral_server_url = coral_server_url
        self.agent_id = agent_id
        self.client: Optional[httpx.AsyncClient] = None
        self.registered_agents: Dict[str, AgentRegistration] = {}
        self.wallet_config = self._load_wallet_config()
        self.marketplace_api_url = self._get_marketplace_api_url()

        # Initialize official Coral SDK if available
        if CORAL_SDK_AVAILABLE:
            try:
                self.coral_sdk_client = OfficialCoralClient(
                    server_url=coral_server_url,
                    agent_id=agent_id
                )
                logger.info(f"Initialized Coral v01 SDK client for agent {agent_id}")
            except Exception as e:
                logger.warning(f"Failed to initialize Coral SDK client: {e}, using fallback")
                self.coral_sdk_client = None
        else:
            self.coral_sdk_client = None

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
            # Use official Coral SDK if available
            if self.coral_sdk_client:
                try:
                    logger.info(f"Registering agent {self.agent_id} using Coral v01 SDK")

                    # Create SDK registration object
                    sdk_registration = SDKAgentRegistration(
                        agent_id=self.agent_id,
                        agent_type=agent_type,
                        capabilities=capabilities,
                        endpoint=endpoint
                    )

                    # Register using official SDK
                    result = await self.coral_sdk_client.register_agent(sdk_registration)

                    if result:
                        logger.info(f"[OK] Successfully registered {self.agent_id} with Coral v01 SDK")

                        # Store in local registry too
                        self.registered_agents[self.agent_id] = AgentRegistration(
                            agent_id=self.agent_id,
                            agent_type=agent_type,
                            capabilities=capabilities,
                            endpoint=endpoint
                        )
                        return True
                    else:
                        logger.error("Coral SDK registration failed")
                        return False

                except Exception as sdk_error:
                    logger.warning(f"Coral SDK registration failed: {sdk_error}, falling back to direct registration")
                    # Fall through to legacy implementation

            # Fallback to direct registration
            await self._ensure_client()

            registration_data = {
                "agent_id": self.agent_id,
                "agent_type": agent_type,
                "capabilities": capabilities,
                "endpoint": endpoint
            }

            logger.info(f"Attempting to register agent {self.agent_id} with Coral Protocol (direct)")
            logger.info(f"Agent type: {agent_type}, Capabilities: {capabilities}")

            # Only register if we have a valid agent_id
            if not self.agent_id:
                logger.error("Cannot register agent: missing agent_id")
                return False

            # Try to register with the actual Coral Protocol server
            # Add retry logic for better reliability
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    response = await self.client.post(
                        f"{self.coral_server_url}/register",
                        json=registration_data,
                        timeout=10.0
                    )

                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"[OK] Successfully registered {self.agent_id} with Coral Server")

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
                        if attempt < max_retries - 1:
                            logger.info(f"Retrying registration in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(retry_delay)
                            continue
                        return False

                except Exception as server_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"Registration attempt {attempt + 1} failed: {server_error}")
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        logger.warning(f"Failed to register with Coral Server: All connection attempts failed")
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

            # Handle data_agent methods
            elif target_agent == "data_agent" and method == "get_market_context":
                # Import here to avoid circular imports
                from ..core.data_agent import DataAgent
                try:
                    data_agent = DataAgent()
                    timestamp = parameters.get("timestamp")
                    result = await data_agent.get_market_context(timestamp)
                    return result
                except Exception as e:
                    logger.error(f"Data agent error for get_market_context: {e}")
                    return {"error": str(e), "timestamp": datetime.now().isoformat()}

            elif target_agent == "data_agent" and method == "get_market_data":
                from ..core.data_agent import DataAgent
                try:
                    data_agent = DataAgent()
                    symbol = parameters.get("symbol", "SPY")
                    result = await data_agent.fetch_market_data(symbol)
                    return result.__dict__ if hasattr(result, '__dict__') else result
                except Exception as e:
                    logger.error(f"Data agent error for get_market_data: {e}")
                    return {"error": str(e), "symbol": parameters.get("symbol", "SPY")}

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

    # =============================================================================
    # CORAL PROTOCOL MARKETPLACE INTEGRATION
    # =============================================================================

    def _load_wallet_config(self) -> Optional[Dict[str, Any]]:
        """Load wallet configuration from ~/.coral/wallet.toml"""
        try:
            wallet_path = Path.home() / ".coral" / "wallet.toml"
            if wallet_path.exists():
                import toml
                return toml.load(wallet_path)
            return None
        except Exception as e:
            logger.warning(f"Could not load wallet config: {e}")
            return None

    def _get_marketplace_api_url(self) -> str:
        """Get the marketplace API URL from environment or default"""
        return os.getenv("CORAL_MARKETPLACE_API_URL", "https://api.coralprotocol.org")

    async def register_agent_marketplace(self, agent_config_path: str) -> bool:
        """
        Register agent with Coral Protocol marketplace.
        
        Args:
            agent_config_path: Path to coral-agent.toml configuration file
            
        Returns:
            True if registration successful
        """
        try:
            await self._ensure_client()
            
            # Load agent configuration
            import toml
            config_path = Path(agent_config_path)
            if not config_path.exists():
                logger.error(f"Agent config file not found: {agent_config_path}")
                return False
                
            agent_config = toml.load(config_path)
            
            # Prepare marketplace registration data
            registration_data = {
                "agent": agent_config.get("agent", {}),
                "options": agent_config.get("options", {}),
                "runtimes": agent_config.get("runtimes", {}),
                "wallet_address": self.wallet_config.get("wallet_address") if self.wallet_config else None,
                "publisher_info": {
                    "publisher": "Neural Capital",
                    "email": "hello@neural-capital.com",
                    "website": "https://neural-capital.com"
                }
            }
            
            logger.info(f"Registering agent {agent_config['agent']['name']} with marketplace")
            
            response = await self.client.post(
                f"{self.marketplace_api_url}/api/v1/agents/register",
                json=registration_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                agent_id = result.get("agent_id")
                logger.info(f"Successfully registered agent {agent_id} with marketplace")
                return True
            else:
                logger.error(f"Marketplace registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to register agent with marketplace: {e}")
            return False

    async def claim_payment(self, remote_session_id: str, amount: float, currency: str = "coral") -> bool:
        """
        Claim payment for agent usage in Coral Protocol.
        
        Args:
            remote_session_id: Session ID from agent usage
            amount: Amount to claim
            currency: Currency type (default: "coral")
            
        Returns:
            True if payment claim successful
        """
        try:
            await self._ensure_client()
            
            claim_data = {
                "amount": {
                    "type": currency,
                    "amount": amount
                }
            }
            
            # Get CORAL_API_URL from environment (set by coral server)
            coral_api_url = os.getenv("CORAL_API_URL", self.coral_server_url)
            
            response = await self.client.post(
                f"{coral_api_url}/api/v1/internal/claim/{remote_session_id}",
                json=claim_data,
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully claimed payment: {amount} {currency}")
                return True
            else:
                logger.error(f"Payment claim failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to claim payment: {e}")
            return False

    async def get_marketplace_agents(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover agents available on the Coral Protocol marketplace.
        
        Args:
            category: Optional category filter (e.g., "Financial Services")
            
        Returns:
            List of available marketplace agents
        """
        try:
            await self._ensure_client()
            
            params = {}
            if category:
                params["category"] = category
                
            response = await self.client.get(
                f"{self.marketplace_api_url}/api/v1/agents",
                params=params,
                timeout=10.0
            )
            
            if response.status_code == 200:
                agents = response.json().get("agents", [])
                logger.info(f"Found {len(agents)} agents in marketplace")
                return agents
            else:
                logger.error(f"Failed to fetch marketplace agents: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get marketplace agents: {e}")
            return []

    async def purchase_agent_access(self, agent_id: str, tier: str = "basic") -> Optional[str]:
        """
        Purchase access to an agent on the marketplace.
        
        Args:
            agent_id: ID of the agent to purchase
            tier: Service tier (basic, premium, enterprise)
            
        Returns:
            Access token if successful, None otherwise
        """
        try:
            await self._ensure_client()
            
            purchase_data = {
                "agent_id": agent_id,
                "tier": tier,
                "wallet_address": self.wallet_config.get("wallet_address") if self.wallet_config else None
            }
            
            response = await self.client.post(
                f"{self.marketplace_api_url}/api/v1/agents/{agent_id}/purchase",
                json=purchase_data,
                timeout=15.0
            )
            
            if response.status_code == 200:
                result = response.json()
                access_token = result.get("access_token")
                logger.info(f"Successfully purchased access to agent {agent_id}")
                return access_token
            else:
                logger.error(f"Failed to purchase agent access: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to purchase agent access: {e}")
            return None

    async def get_agent_earnings(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get earnings information for agent(s).
        
        Args:
            agent_id: Specific agent ID, or None for all owned agents
            
        Returns:
            Earnings information
        """
        try:
            await self._ensure_client()
            
            agent_id = agent_id or self.agent_id
            
            response = await self.client.get(
                f"{self.marketplace_api_url}/api/v1/agents/{agent_id}/earnings",
                timeout=10.0
            )
            
            if response.status_code == 200:
                earnings = response.json()
                logger.info(f"Retrieved earnings for agent {agent_id}")
                return earnings
            else:
                logger.error(f"Failed to get agent earnings: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get agent earnings: {e}")
            return {}

    async def update_agent_pricing(self, agent_id: str, pricing_config: Dict[str, Any]) -> bool:
        """
        Update pricing configuration for an agent on the marketplace.
        
        Args:
            agent_id: Agent ID to update
            pricing_config: New pricing configuration
            
        Returns:
            True if update successful
        """
        try:
            await self._ensure_client()
            
            response = await self.client.put(
                f"{self.marketplace_api_url}/api/v1/agents/{agent_id}/pricing",
                json=pricing_config,
                timeout=10.0
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully updated pricing for agent {agent_id}")
                return True
            else:
                logger.error(f"Failed to update agent pricing: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update agent pricing: {e}")
            return False


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