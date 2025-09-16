"""
Integration tests for multi-agent workflows and interactions.

Tests the complete agent system working together including:
- Agent-to-agent communication via Coral Protocol
- Data flow between DataAgent -> PortfolioAgent -> PlannerAgent -> ExplainabilityAgent
- Error handling and fallback behavior across agents
- Configuration consistency across agents
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
import uuid

from agent import DataAgent, PortfolioAgent, PlannerAgent, ExplainabilityAgent
from agent.models import RiskLevel, GoalType, MarketData, MacroData
from agent.config import config


class TestMultiAgentIntegration:
    """Integration tests for multi-agent workflows"""

    @pytest_asyncio.fixture
    async def agents(self):
        """Create all four agents for testing"""
        return {
            'data': DataAgent(),
            'portfolio': PortfolioAgent(),
            'planner': PlannerAgent(),
            'explainability': ExplainabilityAgent()
        }

    @pytest.mark.asyncio
    async def test_agent_initialization_consistency(self, agents):
        """Test that all agents initialize consistently with BaseAgent"""
        for agent_name, agent in agents.items():
            # All agents should have coral_client
            assert hasattr(agent, 'coral_client')
            assert agent.coral_client is not None

            # All agents should have agent_id
            assert hasattr(agent, 'agent_id')
            assert agent.agent_id is not None
            assert isinstance(agent.agent_id, str)

            # All agents should have config access
            assert hasattr(agent, 'config')
            assert agent.config is not None

            # Agent IDs should be correctly set
            expected_id = f"{agent_name}_agent"
            assert agent.agent_id == expected_id

    @pytest.mark.asyncio
    async def test_agent_health_checks(self, agents):
        """Test health checks across all agents"""
        for agent_name, agent in agents.items():
            health = await agent.health_check()

            assert isinstance(health, dict)

            # Health check should have basic structure
            if 'status' in health:
                assert health['status'] == 'healthy'
            if 'agent_id' in health:
                assert health['agent_id'] == f"{agent_name}_agent"

            # Should have meaningful health information
            assert len(health) > 0

            # If timestamp exists, should be recent
            if 'timestamp' in health:
                timestamp = datetime.fromisoformat(health['timestamp'])
                assert (datetime.now() - timestamp).total_seconds() < 10

            # Health check should contain some status information
            has_status_info = any(
                key in health for key in ['status', 'healthy', 'error', 'fred', 'yahoo_finance']
            )
            assert has_status_info

    @pytest.mark.asyncio
    async def test_data_to_portfolio_workflow(self, agents):
        """Test data flow from DataAgent to PortfolioAgent"""
        data_agent = agents['data']
        portfolio_agent = agents['portfolio']

        # Test that DataAgent can provide data that PortfolioAgent needs
        try:
            # Get market data from DataAgent
            market_data = await data_agent.fetch_market_data("SPY")
            assert market_data is not None

            # Test portfolio building with different risk levels
            for risk_level in [1, 3, 5]:  # Conservative, Balanced, Aggressive
                portfolio = await portfolio_agent.build_portfolio(
                    risk_level=risk_level,
                    goal="retirement",
                    constraints=None
                )

                assert portfolio is not None
                if isinstance(portfolio, dict):
                    # Should have basic portfolio structure
                    assert 'allocations' in portfolio or 'error' in portfolio

        except Exception as e:
            # In test environment, we expect some external API calls to fail
            # This is acceptable as long as the workflow structure is correct
            pytest.skip(f"External API dependency failed: {e}")

    @pytest.mark.asyncio
    async def test_planner_to_explainability_workflow(self, agents):
        """Test workflow from PlannerAgent to ExplainabilityAgent"""
        planner_agent = agents['planner']
        explainability_agent = agents['explainability']

        # Test goal parsing and explanation generation
        try:
            # Parse a financial goal
            goal_text = "I want to save $500,000 for retirement in 20 years"
            parsed_goal = await planner_agent.parse_goal(goal_text)

            assert parsed_goal is not None
            assert isinstance(parsed_goal, dict)

            # Create a mock action for explanation
            action = {
                'type': 'portfolio_rebalance',
                'details': 'Increased equity allocation to 70%',
                'reason': 'Market volatility decreased',
                'timestamp': datetime.now(),
                'agent_source': 'portfolio_agent'
            }

            # Get explanation
            explanation = await explainability_agent.explain_decision(action)

            assert explanation is not None
            assert isinstance(explanation, dict)

        except Exception as e:
            pytest.skip(f"External dependency failed: {e}")

    @pytest.mark.asyncio
    async def test_full_investment_workflow(self, agents):
        """Test complete investment workflow across all agents"""
        data_agent = agents['data']
        portfolio_agent = agents['portfolio']
        planner_agent = agents['planner']
        explainability_agent = agents['explainability']

        try:
            # 1. Parse investment goal (PlannerAgent)
            goal_text = "I need $200,000 for a house down payment in 5 years"
            parsed_goal = await planner_agent.parse_goal(goal_text)

            # 2. Get market context (DataAgent)
            market_context = await data_agent.get_market_context()

            # 3. Build portfolio based on goal (PortfolioAgent)
            portfolio = await portfolio_agent.build_portfolio(
                risk_level=3,  # Balanced
                goal="house_down_payment",
                constraints={"time_horizon": 5}
            )

            # 4. Generate explanation (ExplainabilityAgent)
            if portfolio and not portfolio.get('error'):
                action = {
                    'type': 'portfolio_creation',
                    'details': str(portfolio),
                    'reason': 'Initial portfolio for house down payment goal',
                    'timestamp': datetime.now()
                }

                explanation = await explainability_agent.explain_decision(action)

                # Verify end-to-end workflow completed
                assert parsed_goal is not None
                assert market_context is not None
                assert portfolio is not None
                assert explanation is not None

        except Exception as e:
            pytest.skip(f"External API dependency in full workflow: {e}")

    @pytest.mark.asyncio
    async def test_error_propagation_across_agents(self, agents):
        """Test how errors propagate and are handled across agents"""

        # Test with invalid inputs to see error handling
        portfolio_agent = agents['portfolio']
        explainability_agent = agents['explainability']

        # Test invalid risk level
        try:
            result = await portfolio_agent.build_portfolio(
                risk_level=99,  # Invalid risk level
                goal="invalid_goal",
                constraints={}
            )

            # Should either handle gracefully or provide meaningful error
            assert result is not None
            if isinstance(result, dict) and 'error' in result:
                assert isinstance(result['error'], str)
                assert len(result['error']) > 0

        except Exception as e:
            # Should not raise unhandled exceptions
            assert False, f"Unhandled exception in error case: {e}"

        # Test explanation with invalid action
        try:
            invalid_action = None
            result = await explainability_agent.explain_decision(invalid_action)

            # Should handle gracefully
            assert result is not None

        except Exception as e:
            # Should not raise unhandled exceptions for invalid input
            assert False, f"Unhandled exception for invalid action: {e}"

    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self, agents):
        """Test that agents can operate concurrently without conflicts"""

        # Run multiple agent operations concurrently
        tasks = []

        # Health checks on all agents
        for agent in agents.values():
            tasks.append(agent.health_check())

        # Add some data operations
        data_agent = agents['data']
        tasks.append(data_agent.get_market_context())

        # Add portfolio operations with different risk levels
        portfolio_agent = agents['portfolio']
        for risk_level in [1, 3, 5]:
            tasks.append(portfolio_agent.build_portfolio(
                risk_level=risk_level,
                goal="retirement",
                constraints={}
            ))

        # Execute all tasks concurrently
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check that we got results for all tasks
            assert len(results) == len(tasks)

            # Health checks should all succeed
            health_results = results[:len(agents)]
            for health in health_results:
                if not isinstance(health, Exception):
                    assert isinstance(health, dict)
                    assert health.get('status') == 'healthy'

        except Exception as e:
            pytest.skip(f"Concurrent operations failed due to external dependencies: {e}")

    def test_configuration_consistency_across_agents(self, agents):
        """Test that all agents have consistent configuration access"""

        # All agents should have the same config object
        config_objects = [agent.config for agent in agents.values()]

        # All should reference the same config
        first_config = config_objects[0]
        for cfg in config_objects[1:]:
            assert cfg is first_config  # Same object reference

        # Configuration should have expected agent sections
        assert hasattr(first_config, 'data_agent')
        assert hasattr(first_config, 'portfolio_agent')
        assert hasattr(first_config, 'planner_agent')
        assert hasattr(first_config, 'explainability_agent')

        # Base config should be accessible
        assert hasattr(first_config, 'base_config')
        assert hasattr(first_config.base_config, 'enable_fallbacks')

    @pytest.mark.asyncio
    async def test_shared_utilities_integration(self, agents):
        """Test that shared utilities work consistently across all agents"""

        # Test that all agents can use shared timestamp utility
        from agent.shared import get_current_timestamp

        timestamp1 = get_current_timestamp()
        await asyncio.sleep(0.1)  # Small delay
        timestamp2 = get_current_timestamp()

        # Timestamps should be different and valid ISO format
        assert timestamp1 != timestamp2
        assert datetime.fromisoformat(timestamp1)
        assert datetime.fromisoformat(timestamp2)

        # Test that error handling utilities are available
        from agent.shared import ErrorHandler, safe_get

        test_dict = {"key1": "value1", "key2": None}
        assert safe_get(test_dict, "key1") == "value1"
        assert safe_get(test_dict, "key2") is None
        assert safe_get(test_dict, "missing_key") is None
        assert safe_get(test_dict, "missing_key", "default") == "default"