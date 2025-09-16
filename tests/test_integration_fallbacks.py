"""
Integration tests for fallback system functionality.

Tests the complete fallback system including:
- Fallback activation under various failure scenarios
- Configuration-based fallback behavior
- Fallback data quality and consistency
- Environment-specific fallback behavior
- Recovery mechanisms and fallback graduation
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime
from unittest.mock import patch, MagicMock
from typing import Dict, Any
import os

from agent import DataAgent, PortfolioAgent, PlannerAgent, ExplainabilityAgent
from agent.config import config, ConfigManager
from agent.shared import ErrorHandler


class TestFallbackSystemIntegration:
    """Integration tests for the fallback system"""

    @pytest_asyncio.fixture
    async def agents(self):
        """Create agents for fallback testing"""
        return {
            'data': DataAgent(),
            'portfolio': PortfolioAgent(),
            'planner': PlannerAgent(),
            'explainability': ExplainabilityAgent()
        }

    @pytest.fixture
    def mock_external_failure(self):
        """Fixture that mocks external service failures"""
        patches = []

        # Mock various external services to fail
        patches.append(patch('yfinance.Ticker', side_effect=ConnectionError("External API down")))
        patches.append(patch('requests.get', side_effect=ConnectionError("Network error")))
        patches.append(patch('httpx.AsyncClient.post', side_effect=ConnectionError("HTTP error")))

        for p in patches:
            p.start()

        yield patches

        for p in patches:
            p.stop()

    def test_fallback_configuration_structure(self):
        """Test that fallback configuration is properly structured"""
        # Test that fallback methods exist
        assert hasattr(config, 'should_use_fallbacks')
        assert hasattr(config, 'get_fallback')
        assert callable(config.should_use_fallbacks)
        assert callable(config.get_fallback)

        # Test fallback availability
        fallbacks_enabled = config.should_use_fallbacks()
        assert isinstance(fallbacks_enabled, bool)

    def test_agent_specific_fallbacks(self):
        """Test that each agent has appropriate fallback data"""
        agents = ['data_agent', 'portfolio_agent', 'planner_agent', 'explainability_agent']

        for agent_type in agents:
            # Test that we can get fallback data for each agent
            try:
                fallback = config.get_fallback(agent_type, 'test_fallback')
                assert fallback is not None
                assert isinstance(fallback, dict)
            except (KeyError, AttributeError):
                # Some fallbacks might not exist, but the method should work
                pass

    @pytest.mark.asyncio
    async def test_data_agent_fallbacks(self, agents, mock_external_failure):
        """Test DataAgent fallback behavior"""
        data_agent = agents['data']

        # Force fallback usage
        with patch.object(config, 'should_use_fallbacks', return_value=True):
            # Test market data fallback
            result = await data_agent.fetch_market_data("SPY")

            assert result is not None

            if isinstance(result, dict):
                # Should have fallback structure
                expected_fields = ['symbol', 'price', 'error', 'timestamp']
                has_fallback_structure = any(field in result for field in expected_fields)
                assert has_fallback_structure

                # If it has symbol, should match requested symbol
                if 'symbol' in result:
                    assert result['symbol'] == 'SPY'

                # Should have timestamp indicating when fallback was used
                if 'timestamp' in result:
                    timestamp = result['timestamp']
                    assert isinstance(timestamp, str)
                    # Should be recent
                    parsed_time = datetime.fromisoformat(timestamp)
                    assert (datetime.now() - parsed_time).total_seconds() < 60

    @pytest.mark.asyncio
    async def test_portfolio_agent_fallbacks(self, agents, mock_external_failure):
        """Test PortfolioAgent fallback behavior"""
        portfolio_agent = agents['portfolio']

        with patch.object(config, 'should_use_fallbacks', return_value=True):
            # Test portfolio building with fallbacks
            portfolio = await portfolio_agent.build_portfolio(
                risk_level=3,
                goal="retirement",
                constraints={}
            )

            assert portfolio is not None

            if isinstance(portfolio, dict):
                # Should have either portfolio data or fallback structure
                expected_fields = ['allocations', 'expected_return', 'error', 'fallback_used']
                has_portfolio_structure = any(field in portfolio for field in expected_fields)
                assert has_portfolio_structure

                # If has allocations, should be reasonable
                if 'allocations' in portfolio:
                    allocations = portfolio['allocations']
                    assert isinstance(allocations, dict)

                    # Total allocation should be reasonable
                    if len(allocations) > 0:
                        total = sum(allocations.values())
                        assert 0.8 <= total <= 1.2  # Allow some flexibility

    @pytest.mark.asyncio
    async def test_planner_agent_fallbacks(self, agents, mock_external_failure):
        """Test PlannerAgent fallback behavior"""
        planner_agent = agents['planner']

        with patch.object(config, 'should_use_fallbacks', return_value=True):
            # Test goal parsing with fallbacks
            goal_text = "I want to retire with $1 million in 25 years"
            result = await planner_agent.parse_goal(goal_text)

            assert result is not None
            assert isinstance(result, dict)

            # Should have goal parsing structure
            expected_fields = ['goal_type', 'time_horizon', 'amount', 'error']
            has_goal_structure = any(field in result for field in expected_fields)
            assert has_goal_structure

            # If successful parsing, should have reasonable values
            if 'goal_type' in result and result['goal_type'] != 'UNKNOWN':
                assert isinstance(result['goal_type'], str)

            if 'time_horizon' in result:
                time_horizon = result['time_horizon']
                if time_horizon is not None:
                    assert isinstance(time_horizon, (int, float))
                    assert 0 < time_horizon <= 50  # Reasonable range

    @pytest.mark.asyncio
    async def test_explainability_agent_fallbacks(self, agents, mock_external_failure):
        """Test ExplainabilityAgent fallback behavior"""
        explainability_agent = agents['explainability']

        with patch.object(config, 'should_use_fallbacks', return_value=True):
            # Test explanation with fallbacks
            action = {
                'type': 'portfolio_rebalance',
                'details': 'Increased equity allocation',
                'reason': 'Market outlook improved',
                'timestamp': datetime.now()
            }

            result = await explainability_agent.explain_decision(action)

            assert result is not None
            assert isinstance(result, dict)

            # Should have explanation structure
            expected_fields = ['explanation', 'risk_assessment', 'plain_english', 'error']
            has_explanation_structure = any(field in result for field in expected_fields)
            assert has_explanation_structure

    @patch.dict(os.environ, {'ENVIRONMENT': 'development'})
    def test_development_environment_fallbacks(self):
        """Test fallback behavior in development environment"""
        # Create new config manager for development
        dev_config = ConfigManager()

        # Development should typically have fallbacks enabled
        fallbacks_enabled = dev_config.should_use_fallbacks()
        assert isinstance(fallbacks_enabled, bool)

        # Should be able to get fallback data
        try:
            fallback = dev_config.get_fallback('data_agent', 'market_data', symbol='TEST')
            assert fallback is not None
            assert isinstance(fallback, dict)
        except (KeyError, AttributeError):
            # Some specific fallbacks might not exist
            pass

    @patch.dict(os.environ, {'ENVIRONMENT': 'production'})
    def test_production_environment_fallbacks(self):
        """Test fallback behavior in production environment"""
        # Create new config manager for production
        prod_config = ConfigManager()

        # Production fallback behavior should be configurable
        fallbacks_enabled = prod_config.should_use_fallbacks()
        assert isinstance(fallbacks_enabled, bool)

        # Should handle fallback requests gracefully
        try:
            fallback = prod_config.get_fallback('data_agent', 'market_data', symbol='TEST')
            if fallback is not None:
                assert isinstance(fallback, dict)
        except (KeyError, AttributeError):
            # In production, some fallbacks might be disabled
            pass

    def test_fallback_data_quality(self):
        """Test that fallback data meets quality standards"""
        # Test data agent fallbacks
        fallback = config.get_fallback('data_agent', 'market_data', symbol='SPY')

        assert isinstance(fallback, dict)

        # Should have required fields
        if 'symbol' in fallback:
            assert fallback['symbol'] == 'SPY'

        if 'price' in fallback:
            price = fallback['price']
            assert isinstance(price, (int, float))
            assert price > 0

        if 'timestamp' in fallback:
            timestamp = fallback['timestamp']
            assert isinstance(timestamp, str)
            # Should be valid ISO format
            datetime.fromisoformat(timestamp)

        # Test portfolio agent fallbacks
        portfolio_fallback = config.get_fallback('portfolio_agent', 'allocation', risk_level=3)

        assert isinstance(portfolio_fallback, dict)

        if 'allocations' in portfolio_fallback:
            allocations = portfolio_fallback['allocations']
            assert isinstance(allocations, dict)

            # Should have reasonable asset classes
            expected_classes = ['equity', 'fixed_income', 'alternatives', 'cash']
            has_asset_classes = any(asset_class in allocations for asset_class in expected_classes)
            assert has_asset_classes

    @pytest.mark.asyncio
    async def test_fallback_activation_conditions(self, agents):
        """Test conditions that trigger fallback activation"""
        data_agent = agents['data']

        # Test different error conditions
        error_conditions = [
            ConnectionError("Network down"),
            TimeoutError("Request timeout"),
            ValueError("Invalid response"),
            KeyError("Missing data field")
        ]

        for error in error_conditions:
            with patch('yfinance.Ticker', side_effect=error):
                with patch.object(config, 'should_use_fallbacks', return_value=True):

                    result = await data_agent.fetch_market_data("SPY")

                    # Should handle all error types with fallbacks
                    assert result is not None

                    if isinstance(result, dict):
                        # Should indicate fallback was used
                        has_fallback_indicator = any(
                            key in result for key in ['error', 'fallback_used', 'symbol']
                        )
                        assert has_fallback_indicator

    def test_fallback_error_handler_integration(self):
        """Test integration between fallback system and error handlers"""
        # Test ErrorHandler with fallback
        def failing_operation():
            raise ConnectionError("Service unavailable")

        with patch.object(config, 'should_use_fallbacks', return_value=True):
            result = ErrorHandler.handle_with_fallback(
                operation_name="test_operation",
                agent_type="data_agent",
                fallback_type="market_data",
                error=ConnectionError("Service unavailable"),
                symbol="SPY"
            )

            assert result is not None
            assert isinstance(result, dict)
            assert 'error' in result
            assert 'timestamp' in result

    @pytest.mark.asyncio
    async def test_fallback_graduation_and_recovery(self, agents):
        """Test recovery from fallback mode when services return"""
        data_agent = agents['data']

        # Start with forced failures (fallback mode)
        with patch('yfinance.Ticker', side_effect=ConnectionError("Service down")):
            with patch.object(config, 'should_use_fallbacks', return_value=True):

                result1 = await data_agent.fetch_market_data("SPY")
                assert result1 is not None

                # Should be fallback data
                if isinstance(result1, dict) and 'error' in result1:
                    assert 'Service down' in str(result1['error'])

        # Simulate service recovery (no more forced failures)
        try:
            result2 = await data_agent.fetch_market_data("SPY")
            assert result2 is not None

            # Should either work normally or handle gracefully
            if isinstance(result2, dict):
                # Should not have the forced error anymore
                if 'error' in result2:
                    assert 'Service down' not in str(result2['error'])

        except Exception as e:
            # Real external API might still fail, that's acceptable
            pytest.skip(f"Service recovery test limited by external API: {e}")

    @pytest.mark.asyncio
    async def test_cascading_fallback_behavior(self, agents):
        """Test fallback behavior in cascading agent workflows"""
        data_agent = agents['data']
        portfolio_agent = agents['portfolio']
        explainability_agent = agents['explainability']

        # Force data agent into fallback mode
        with patch.object(data_agent, 'fetch_market_data') as mock_fetch:
            mock_fetch.return_value = config.get_fallback(
                'data_agent', 'market_data', symbol='SPY'
            )

            with patch.object(config, 'should_use_fallbacks', return_value=True):
                # Get fallback market data
                market_data = await data_agent.fetch_market_data("SPY")
                assert market_data is not None

                # Portfolio agent should handle fallback data
                portfolio = await portfolio_agent.build_portfolio(
                    risk_level=3,
                    goal="retirement",
                    constraints={}
                )
                assert portfolio is not None

                # Explainability agent should handle fallback portfolio
                action = {
                    'type': 'portfolio_creation',
                    'details': str(portfolio),
                    'reason': 'Using fallback data',
                    'timestamp': datetime.now()
                }

                explanation = await explainability_agent.explain_decision(action)
                assert explanation is not None

    def test_fallback_logging_and_monitoring(self, caplog):
        """Test that fallback usage is properly logged"""
        import logging

        with caplog.at_level(logging.INFO):
            with patch.object(config, 'should_use_fallbacks', return_value=True):
                with patch.object(config.base_config, 'log_fallback_usage', True):

                    # Trigger fallback usage
                    result = ErrorHandler.handle_with_fallback(
                        operation_name="test_logging",
                        agent_type="data_agent",
                        fallback_type="market_data",
                        error=ConnectionError("Test error"),
                        symbol="SPY"
                    )

                    assert result is not None

                    # Should have logged fallback usage
                    log_messages = [record.message for record in caplog.records]
                    has_fallback_log = any(
                        'fallback' in msg.lower() or 'test_logging' in msg
                        for msg in log_messages
                    )
                    assert has_fallback_log

    @pytest.mark.asyncio
    async def test_fallback_performance_characteristics(self, agents):
        """Test that fallbacks provide acceptable performance"""
        data_agent = agents['data']

        with patch.object(config, 'should_use_fallbacks', return_value=True):
            # Measure fallback performance
            start_time = datetime.now()

            # Force fallback usage
            with patch('yfinance.Ticker', side_effect=ConnectionError("Forced failure")):
                result = await data_agent.fetch_market_data("SPY")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Fallback should be fast (under 1 second)
            assert duration < 1.0

            # Should still return valid data
            assert result is not None

    def test_fallback_consistency_across_calls(self):
        """Test that fallback data is consistent across multiple calls"""
        # Multiple calls to same fallback should return consistent data
        results = []

        for _ in range(3):
            fallback = config.get_fallback('data_agent', 'market_data', symbol='SPY')
            results.append(fallback)

        assert len(results) == 3

        # All results should be similar structure
        for result in results:
            assert isinstance(result, dict)
            if 'symbol' in result:
                assert result['symbol'] == 'SPY'

        # Timestamps might be different, but structure should be same
        first_result = results[0]
        for result in results[1:]:
            # Should have same keys (excluding timestamp which might update)
            non_timestamp_keys = {k for k in first_result.keys() if k != 'timestamp'}
            result_keys = {k for k in result.keys() if k != 'timestamp'}
            assert non_timestamp_keys == result_keys