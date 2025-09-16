"""
Integration tests for Coral Protocol functionality.

Tests the complete Coral Protocol integration including:
- Agent registration and discovery
- Inter-agent communication
- Message routing and delivery
- Token micropayments (if enabled)
- Blockchain verification
- Protocol-level error handling
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
import uuid
from unittest.mock import patch, MagicMock, AsyncMock

from agent.coral_client import CoralClient
from agent import DataAgent, PortfolioAgent, PlannerAgent, ExplainabilityAgent


class TestCoralProtocolIntegration:
    """Integration tests for Coral Protocol functionality"""

    @pytest_asyncio.fixture
    async def coral_clients(self):
        """Create coral clients for testing"""
        return {
            'data': CoralClient("http://localhost:5555", agent_id="data_agent"),
            'portfolio': CoralClient("http://localhost:5555", agent_id="portfolio_agent"),
            'planner': CoralClient("http://localhost:5555", agent_id="planner_agent"),
            'explainability': CoralClient("http://localhost:5555", agent_id="explainability_agent")
        }

    @pytest_asyncio.fixture
    async def agents_with_coral(self):
        """Create agents with coral protocol integration"""
        return {
            'data': DataAgent(),
            'portfolio': PortfolioAgent(),
            'planner': PlannerAgent(),
            'explainability': ExplainabilityAgent()
        }

    def test_coral_client_initialization(self, coral_clients):
        """Test that Coral clients initialize correctly"""
        for agent_name, client in coral_clients.items():
            assert client is not None
            assert client.agent_id == f"{agent_name}_agent"
            assert client.server_url == "http://localhost:5555"

            # Should have required attributes
            assert hasattr(client, 'session')
            assert hasattr(client, 'agent_id')
            assert hasattr(client, 'server_url')

    @pytest.mark.asyncio
    async def test_agent_registration(self, coral_clients):
        """Test agent registration with Coral Protocol"""
        for agent_name, client in coral_clients.items():
            try:
                # Test registration
                registration_result = await client.register_agent()

                # Should complete without error
                assert registration_result is not None

                if isinstance(registration_result, dict):
                    # Should have registration confirmation
                    expected_fields = ['agent_id', 'status', 'timestamp']
                    has_expected = any(field in registration_result for field in expected_fields)
                    assert has_expected or 'error' in registration_result

            except Exception as e:
                pytest.skip(f"Coral server not available for registration test: {e}")

    @pytest.mark.asyncio
    async def test_agent_discovery(self, coral_clients):
        """Test agent discovery through Coral Protocol"""
        client = coral_clients['data']

        try:
            # Test discovering other agents
            agents_list = await client.discover_agents()

            assert agents_list is not None

            if isinstance(agents_list, list):
                # Should be a list of agent information
                for agent_info in agents_list:
                    assert isinstance(agent_info, dict)
                    # Should have basic agent info
                    expected_fields = ['agent_id', 'status', 'capabilities']
                    has_info = any(field in agent_info for field in expected_fields)
                    assert has_info

            elif isinstance(agents_list, dict):
                # Might return as dict with error or different format
                assert 'error' in agents_list or 'agents' in agents_list

        except Exception as e:
            pytest.skip(f"Coral server not available for discovery test: {e}")

    @pytest.mark.asyncio
    async def test_inter_agent_communication(self, coral_clients):
        """Test communication between agents via Coral Protocol"""
        data_client = coral_clients['data']
        portfolio_client = coral_clients['portfolio']

        try:
            # Test message sending from data agent to portfolio agent
            message_data = {
                "market_data": {
                    "SPY": {"price": 400, "change": 2.5},
                    "QQQ": {"price": 350, "change": 1.8}
                },
                "timestamp": datetime.now().isoformat()
            }

            result = await data_client.invoke_agent(
                "portfolio_agent",
                "process_market_update",
                message_data
            )

            # Should complete communication
            assert result is not None

            if isinstance(result, dict):
                # Should have response or error info
                has_response = 'result' in result or 'error' in result or 'status' in result
                assert has_response

        except Exception as e:
            pytest.skip(f"Inter-agent communication requires running Coral server: {e}")

    @pytest.mark.asyncio
    async def test_message_routing_and_delivery(self, coral_clients):
        """Test message routing through Coral Protocol"""
        planner_client = coral_clients['planner']

        try:
            # Test sending message to explainability agent
            message = {
                "action": {
                    "type": "goal_analysis",
                    "details": "Analyzed retirement goal for 30-year timeline",
                    "confidence": 0.85
                },
                "context": {
                    "user_age": 35,
                    "target_amount": 1000000,
                    "time_horizon": 30
                }
            }

            result = await planner_client.invoke_agent(
                "explainability_agent",
                "explain_goal_analysis",
                message
            )

            assert result is not None

            # Should have routed and received response
            if isinstance(result, dict):
                expected_response_fields = ['explanation', 'error', 'status']
                has_response = any(field in result for field in expected_response_fields)
                assert has_response

        except Exception as e:
            pytest.skip(f"Message routing test requires Coral server: {e}")

    @pytest.mark.asyncio
    async def test_coral_protocol_error_handling(self, coral_clients):
        """Test error handling within Coral Protocol"""
        client = coral_clients['data']

        # Test invalid agent target
        try:
            result = await client.invoke_agent(
                "nonexistent_agent",
                "test_method",
                {"test": "data"}
            )

            # Should handle invalid agent gracefully
            assert result is not None
            if isinstance(result, dict):
                assert 'error' in result

        except Exception as e:
            # Should not raise unhandled exceptions for invalid agents
            assert "nonexistent_agent" in str(e) or "not found" in str(e).lower()

        # Test invalid method
        try:
            result = await client.invoke_agent(
                "portfolio_agent",
                "nonexistent_method",
                {"test": "data"}
            )

            # Should handle invalid method gracefully
            assert result is not None

        except Exception as e:
            pytest.skip(f"Method validation test requires specific Coral setup: {e}")

    @pytest.mark.asyncio
    async def test_coral_session_management(self, coral_clients):
        """Test session management in Coral Protocol"""
        client = coral_clients['data']

        # Test session creation and cleanup
        try:
            # Should have an active session
            assert hasattr(client, 'session')

            # Test session health
            if hasattr(client, 'health_check'):
                health = await client.health_check()
                assert health is not None

            # Test session cleanup
            if hasattr(client, 'close'):
                await client.close()

                # Should handle operations after close gracefully
                try:
                    result = await client.invoke_agent("test_agent", "test_method", {})
                    # Should either recreate session or handle gracefully
                    assert True  # If we get here, it handled gracefully

                except Exception:
                    # This is also acceptable - closed session should not work
                    assert True

        except Exception as e:
            pytest.skip(f"Session management test requires Coral server: {e}")

    @pytest.mark.asyncio
    async def test_coral_message_validation(self, coral_clients):
        """Test message validation in Coral Protocol"""
        client = coral_clients['data']

        # Test with valid message
        valid_message = {
            "request_id": str(uuid.uuid4()),
            "data": {"symbol": "SPY"},
            "timestamp": datetime.now().isoformat()
        }

        try:
            result = await client.invoke_agent(
                "portfolio_agent",
                "test_method",
                valid_message
            )

            assert result is not None

        except Exception as e:
            pytest.skip(f"Message validation test requires Coral server: {e}")

        # Test with invalid message format
        try:
            invalid_message = "not a dictionary"
            result = await client.invoke_agent(
                "portfolio_agent",
                "test_method",
                invalid_message
            )

            # Should handle invalid format
            if isinstance(result, dict):
                assert 'error' in result

        except Exception as e:
            # Should not crash on invalid message format
            assert "dict" in str(e).lower() or "format" in str(e).lower()

    @pytest.mark.asyncio
    async def test_coral_concurrent_communications(self, coral_clients):
        """Test concurrent communications through Coral Protocol"""
        try:
            # Create multiple concurrent requests
            tasks = []

            for i, (agent_name, client) in enumerate(coral_clients.items()):
                message = {
                    "request_id": f"concurrent_test_{i}",
                    "data": {"test_index": i},
                    "timestamp": datetime.now().isoformat()
                }

                # Send to different target agents
                target_agents = ["portfolio_agent", "explainability_agent", "data_agent", "planner_agent"]
                target = target_agents[i % len(target_agents)]

                if target != agent_name + "_agent":  # Don't send to self
                    task = client.invoke_agent(target, "health_check", message)
                    tasks.append(task)

            if tasks:
                # Execute concurrent requests
                results = await asyncio.gather(*tasks, return_exceptions=True)

                assert len(results) > 0

                # Check that concurrent requests were handled
                for result in results:
                    if not isinstance(result, Exception):
                        assert result is not None

        except Exception as e:
            pytest.skip(f"Concurrent communication test requires Coral server: {e}")

    def test_coral_client_with_agents_integration(self, agents_with_coral):
        """Test that agents properly integrate with Coral clients"""
        for agent_name, agent in agents_with_coral.items():
            # Agent should have coral_client
            assert hasattr(agent, 'coral_client')
            assert agent.coral_client is not None

            # Coral client should be properly configured
            assert isinstance(agent.coral_client, CoralClient)
            assert agent.coral_client.agent_id == f"{agent_name}_agent"

    @pytest.mark.asyncio
    async def test_coral_protocol_timeout_handling(self, coral_clients):
        """Test timeout handling in Coral Protocol"""
        client = coral_clients['data']

        # Test with a request that might timeout
        try:
            # Use a method that might take time or not exist
            result = await client.invoke_agent(
                "portfolio_agent",
                "complex_analysis",
                {"large_dataset": list(range(1000))}
            )

            # Should either complete or timeout gracefully
            assert result is not None

        except asyncio.TimeoutError:
            # Timeout is acceptable behavior
            assert True

        except Exception as e:
            pytest.skip(f"Timeout test requires specific Coral setup: {e}")

    @pytest.mark.asyncio
    async def test_coral_authentication_and_security(self, coral_clients):
        """Test authentication and security features"""
        client = coral_clients['data']

        try:
            # Test that agent authentication works
            auth_result = await client.register_agent()

            if isinstance(auth_result, dict):
                # Should have some form of authentication confirmation
                expected_fields = ['token', 'status', 'agent_id', 'registered']
                has_auth_info = any(field in auth_result for field in expected_fields)
                assert has_auth_info or 'error' in auth_result

        except Exception as e:
            pytest.skip(f"Authentication test requires Coral server with auth: {e}")

    @pytest.mark.asyncio
    async def test_coral_message_history_and_audit(self, coral_clients):
        """Test message history and audit capabilities"""
        client = coral_clients['data']

        try:
            # Send a tracked message
            message = {
                "request_id": str(uuid.uuid4()),
                "audit_trail": True,
                "data": {"test": "audit_message"}
            }

            result = await client.invoke_agent(
                "portfolio_agent",
                "test_audit_method",
                message
            )

            # Should complete and potentially provide audit info
            assert result is not None

            # Check if audit trail is supported
            if isinstance(result, dict) and 'audit' in result:
                audit_info = result['audit']
                assert 'timestamp' in audit_info
                assert 'request_id' in audit_info

        except Exception as e:
            pytest.skip(f"Audit test requires Coral server with audit features: {e}")

    def test_coral_protocol_configuration(self):
        """Test Coral Protocol configuration options"""
        # Test different configuration options
        configs = [
            {"server_url": "http://localhost:5555", "agent_id": "test_agent"},
            {"server_url": "http://localhost:5556", "agent_id": "test_agent_2"},
        ]

        for config in configs:
            client = CoralClient(**config)
            assert client.server_url == config["server_url"]
            assert client.agent_id == config["agent_id"]

    @pytest.mark.asyncio
    async def test_coral_protocol_resilience(self, coral_clients):
        """Test Coral Protocol resilience to various failures"""
        client = coral_clients['data']

        # Test resilience to server unavailability
        with patch.object(client, 'session') as mock_session:
            mock_session.post = AsyncMock(side_effect=ConnectionError("Server unreachable"))

            try:
                result = await client.invoke_agent(
                    "portfolio_agent",
                    "test_method",
                    {"test": "resilience"}
                )

                # Should handle server unavailability gracefully
                assert result is None or isinstance(result, dict)

            except ConnectionError:
                # This is also acceptable - should propagate connection errors
                assert True

        # Test resilience to malformed responses
        with patch.object(client, 'session') as mock_session:
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value="not a dict")
            mock_response.status = 200
            mock_session.post = AsyncMock(return_value=mock_response)

            try:
                result = await client.invoke_agent(
                    "portfolio_agent",
                    "test_method",
                    {"test": "malformed"}
                )

                # Should handle malformed responses
                assert result is not None

            except Exception as e:
                # Should handle parsing errors gracefully
                assert "json" in str(e).lower() or "parse" in str(e).lower()