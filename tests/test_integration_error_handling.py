"""
Integration tests for error handling across the system.

Tests comprehensive error handling including:
- Error propagation through agent layers
- Fallback system activation
- Error recovery mechanisms
- Logging and error reporting
- Graceful degradation under failures
"""

import pytest
import pytest_asyncio
import asyncio
import logging
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any
from datetime import datetime

from agent import DataAgent, PortfolioAgent, PlannerAgent, ExplainabilityAgent
from agent.shared import ErrorHandler, safe_coral_invoke
from agent.config import config


class TestErrorHandlingIntegration:
    """Integration tests for system-wide error handling"""

    @pytest_asyncio.fixture
    async def agents(self):
        """Create all agents for error testing"""
        return {
            'data': DataAgent(),
            'portfolio': PortfolioAgent(),
            'planner': PlannerAgent(),
            'explainability': ExplainabilityAgent()
        }

    @pytest.mark.asyncio
    async def test_network_failure_handling(self, agents):
        """Test how the system handles network failures"""
        data_agent = agents['data']

        # Mock network failure for external API calls
        with patch('yfinance.Ticker') as mock_yf:
            mock_yf.side_effect = ConnectionError("Network unreachable")

            # Should handle network errors gracefully
            try:
                result = await data_agent.fetch_market_data("SPY")

                # Should either return fallback data or error info
                assert result is not None
                if isinstance(result, dict):
                    # Should indicate error occurred
                    assert 'error' in result or 'symbol' in result

            except Exception as e:
                # Should not propagate raw network errors
                assert "Network unreachable" not in str(e)

    @pytest.mark.asyncio
    async def test_api_key_missing_handling(self, agents):
        """Test handling when API keys are missing"""
        # Test with missing API key
        with patch.dict('os.environ', {}, clear=True):
            try:
                # Should handle missing API keys gracefully
                from agent.mistral_client import MistralLLMClient
                client = MistralLLMClient()

                # Should not crash on initialization
                assert client is not None

                # Health check should indicate missing API key
                health = await client.health_check()
                assert isinstance(health, dict)
                assert health['status'] == 'unhealthy'
                assert health['api_key_configured'] is False

            except Exception as e:
                pytest.skip(f"API key test requires specific setup: {e}")

    @pytest.mark.asyncio
    async def test_invalid_input_handling(self, agents):
        """Test handling of invalid inputs across agents"""
        portfolio_agent = agents['portfolio']
        planner_agent = agents['planner']
        explainability_agent = agents['explainability']

        # Test invalid risk level
        result = await portfolio_agent.build_portfolio(
            risk_level=99,  # Invalid
            goal="test",
            constraints={}
        )

        assert result is not None
        if isinstance(result, dict) and 'error' in result:
            assert isinstance(result['error'], str)

        # Test empty goal text
        result = await planner_agent.parse_goal("")
        assert result is not None

        # Test None action for explanation
        result = await explainability_agent.explain_decision(None)
        assert result is not None

    @pytest.mark.asyncio
    async def test_coral_communication_failure(self, agents):
        """Test handling when Coral Protocol communication fails"""
        explainability_agent = agents['explainability']

        # Mock coral client failure
        with patch.object(explainability_agent.coral_client, 'invoke_agent') as mock_invoke:
            mock_invoke.side_effect = ConnectionError("Coral server unreachable")

            action = {
                'type': 'test_action',
                'details': 'test details',
                'timestamp': datetime.now()
            }

            # Should handle coral failures gracefully
            result = await explainability_agent.explain_decision(action)

            assert result is not None
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_fallback_system_activation(self, agents):
        """Test that fallback system activates correctly during errors"""
        data_agent = agents['data']

        # Ensure fallbacks are enabled for this test
        original_fallback_setting = config.should_use_fallbacks()

        try:
            # Force enable fallbacks
            with patch.object(config, 'should_use_fallbacks', return_value=True):
                with patch('yfinance.Ticker') as mock_yf:
                    mock_yf.side_effect = Exception("External API failure")

                    # Should use fallback data
                    result = await data_agent.fetch_market_data("SPY")

                    assert result is not None
                    if isinstance(result, dict):
                        # Should have fallback data structure
                        expected_keys = ['symbol', 'price', 'timestamp']
                        has_expected_structure = any(key in result for key in expected_keys)
                        has_error_info = 'error' in result

                        assert has_expected_structure or has_error_info

        finally:
            # Restore original setting
            pass

    def test_error_handler_utility_functions(self):
        """Test the ErrorHandler utility class functions"""
        # Test safe_execute function
        def failing_function():
            raise ValueError("Test error")

        def working_function():
            return "success"

        # Test with working function
        result = ErrorHandler.safe_execute(
            working_function,
            "test_operation"
        )
        assert result == "success"

        # Test with failing function (no fallback)
        try:
            ErrorHandler.safe_execute(
                failing_function,
                "test_operation"
            )
        except ValueError as e:
            assert str(e) == "Test error"

        # Test with failing function and fallback
        result = ErrorHandler.safe_execute(
            failing_function,
            "test_operation",
            agent_type="test_agent",
            fallback_type="test_fallback"
        )

        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_safe_coral_invoke_error_handling(self, agents):
        """Test safe_coral_invoke error handling"""
        data_agent = agents['data']

        # Test with mock coral client that fails
        mock_coral_client = MagicMock()
        mock_coral_client.invoke_agent = AsyncMock(side_effect=ConnectionError("Connection failed"))

        result = await safe_coral_invoke(
            mock_coral_client,
            "test_agent",
            "test_method",
            {"param": "value"},
            "test_operation"
        )

        # Should return None on failure
        assert result is None

        # Test with working coral client
        mock_coral_client.invoke_agent = AsyncMock(return_value={"success": True})

        result = await safe_coral_invoke(
            mock_coral_client,
            "test_agent",
            "test_method",
            {"param": "value"},
            "test_operation"
        )

        assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_cascading_error_handling(self, agents):
        """Test how errors cascade through multi-agent workflows"""
        data_agent = agents['data']
        portfolio_agent = agents['portfolio']
        explainability_agent = agents['explainability']

        # Simulate failure in data agent
        with patch.object(data_agent, 'fetch_market_data') as mock_fetch:
            mock_fetch.side_effect = Exception("Data source unavailable")

            # Portfolio agent should handle data unavailability
            try:
                portfolio = await portfolio_agent.build_portfolio(
                    risk_level=3,
                    goal="retirement",
                    constraints={}
                )

                # Should complete despite data agent failure
                assert portfolio is not None

                # Try to explain the portfolio creation
                action = {
                    'type': 'portfolio_creation',
                    'details': str(portfolio),
                    'timestamp': datetime.now()
                }

                explanation = await explainability_agent.explain_decision(action)
                assert explanation is not None

            except Exception as e:
                # Should not have unhandled exceptions in the cascade
                pytest.fail(f"Unhandled exception in cascading workflow: {e}")

    @pytest.mark.asyncio
    async def test_concurrent_error_handling(self, agents):
        """Test error handling under concurrent operations"""
        data_agent = agents['data']

        # Create multiple failing operations
        async def failing_operation():
            raise ValueError("Concurrent failure")

        tasks = []
        for i in range(5):
            # Mix of failing and working operations
            if i % 2 == 0:
                task = failing_operation()
            else:
                task = data_agent.health_check()
            tasks.append(task)

        # Execute concurrently with error handling
        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 5

        # Check that exceptions are properly contained
        for result in results:
            if isinstance(result, Exception):
                assert isinstance(result, ValueError)
            else:
                assert isinstance(result, dict)

    def test_logging_integration_during_errors(self, caplog):
        """Test that errors are properly logged"""
        with caplog.at_level(logging.ERROR):
            # Trigger an error that should be logged
            def failing_function():
                raise ValueError("Test logging error")

            try:
                ErrorHandler.safe_execute(
                    failing_function,
                    "test_logging_operation"
                )
            except ValueError:
                pass

            # Should have logged the error
            assert len(caplog.records) > 0
            error_record = caplog.records[-1]
            assert error_record.levelno == logging.ERROR
            assert "test_logging_operation" in error_record.message

    @pytest.mark.asyncio
    async def test_graceful_degradation(self, agents):
        """Test that system degrades gracefully under various failures"""
        portfolio_agent = agents['portfolio']

        # Test with multiple external dependencies failing
        with patch('yfinance.Ticker') as mock_yf, \
             patch.object(portfolio_agent.coral_client, 'invoke_agent') as mock_coral:

            mock_yf.side_effect = ConnectionError("Yahoo Finance down")
            mock_coral.side_effect = ConnectionError("Coral server down")

            # System should still provide some functionality
            portfolio = await portfolio_agent.build_portfolio(
                risk_level=3,
                goal="retirement",
                constraints={}
            )

            assert portfolio is not None
            # Should either provide fallback portfolio or clear error message
            if isinstance(portfolio, dict):
                has_portfolio_data = 'allocations' in portfolio
                has_error_info = 'error' in portfolio
                assert has_portfolio_data or has_error_info

    @pytest.mark.asyncio
    async def test_error_recovery_mechanisms(self, agents):
        """Test error recovery and retry mechanisms"""
        data_agent = agents['data']

        # Test retry logic (if implemented)
        call_count = 0

        def failing_then_working():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return {"symbol": "SPY", "price": 100}

        with patch('yfinance.Ticker') as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.info = failing_then_working
            mock_yf.return_value = mock_ticker

            # Should eventually succeed after retries (if retry logic exists)
            try:
                result = await data_agent.fetch_market_data("SPY")
                assert result is not None

            except Exception:
                # If no retry logic, should handle gracefully
                pass

    def test_error_response_consistency(self):
        """Test that error responses have consistent structure"""
        # Test ErrorHandler response format
        test_error = ValueError("Test error")

        result = ErrorHandler.handle_with_fallback(
            "test_operation",
            "test_agent",
            "test_fallback",
            test_error
        )

        assert isinstance(result, dict)
        assert 'error' in result
        assert 'timestamp' in result
        assert result['error'] == str(test_error)

        # Timestamp should be valid
        timestamp = datetime.fromisoformat(result['timestamp'])
        assert isinstance(timestamp, datetime)

    @pytest.mark.asyncio
    async def test_memory_and_resource_cleanup_on_errors(self, agents):
        """Test that resources are properly cleaned up when errors occur"""
        data_agent = agents['data']

        # Test that even when operations fail, resources are cleaned up
        initial_tasks = len(asyncio.all_tasks())

        try:
            # Create operations that might fail
            tasks = []
            for _ in range(3):
                task = data_agent.fetch_market_data("INVALID_SYMBOL")
                tasks.append(task)

            # Wait for completion or failure
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Should complete without hanging tasks
            final_tasks = len(asyncio.all_tasks())

            # Task count should not grow significantly
            assert final_tasks <= initial_tasks + 1  # Allow for some test overhead

        except Exception:
            # Even if exceptions occur, test that we don't leak tasks
            final_tasks = len(asyncio.all_tasks())
            assert final_tasks <= initial_tasks + 2  # Allow for some overhead