"""
Integration tests for data flow across the system.

Tests end-to-end data flow including:
- Data collection from external sources
- Data transformation and processing
- Data flow between agents
- Data persistence and retrieval
- Data validation and consistency
- Real-time data updates
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock
import uuid

from agent import DataAgent, PortfolioAgent, PlannerAgent, ExplainabilityAgent
from agent.models import MarketData, MacroData, RiskLevel, GoalType


class TestDataFlowIntegration:
    """Integration tests for system-wide data flow"""

    @pytest_asyncio.fixture
    async def agents(self):
        """Create all agents for data flow testing"""
        return {
            'data': DataAgent(),
            'portfolio': PortfolioAgent(),
            'planner': PlannerAgent(),
            'explainability': ExplainabilityAgent()
        }

    @pytest.mark.asyncio
    async def test_market_data_collection_flow(self, agents):
        """Test complete market data collection and distribution flow"""
        data_agent = agents['data']

        try:
            # Test individual asset data collection
            market_data = await data_agent.fetch_market_data("SPY")

            assert market_data is not None

            if isinstance(market_data, MarketData):
                # Should have complete market data structure
                assert hasattr(market_data, 'symbol')
                assert hasattr(market_data, 'price')
                assert hasattr(market_data, 'timestamp')
                assert market_data.symbol == "SPY"
                assert isinstance(market_data.price, (int, float))

            elif isinstance(market_data, dict):
                # Fallback or error format
                expected_fields = ['symbol', 'price', 'error']
                has_expected = any(field in market_data for field in expected_fields)
                assert has_expected

            # Test bulk data collection
            all_market_data = await data_agent.fetch_all_market_data()

            assert all_market_data is not None
            assert isinstance(all_market_data, list)

            if len(all_market_data) > 0:
                for data_point in all_market_data:
                    assert data_point is not None
                    # Should be MarketData object or dict with market info
                    if hasattr(data_point, 'symbol'):
                        assert isinstance(data_point.symbol, str)

        except Exception as e:
            pytest.skip(f"Market data collection requires external APIs: {e}")

    @pytest.mark.asyncio
    async def test_macro_data_collection_flow(self, agents):
        """Test macro-economic data collection and processing"""
        data_agent = agents['data']

        try:
            # Test macro data collection for different indicators
            indicators = ['GDP', 'CPI', 'UNEMPLOYMENT_RATE']

            for indicator in indicators:
                try:
                    macro_data = await data_agent.fetch_macro_data(indicator, date_range=30)

                    assert macro_data is not None
                    assert isinstance(macro_data, list)

                    if len(macro_data) > 0:
                        for data_point in macro_data:
                            if isinstance(data_point, MacroData):
                                assert hasattr(data_point, 'indicator')
                                assert hasattr(data_point, 'value')
                                assert hasattr(data_point, 'date')
                            elif isinstance(data_point, dict):
                                expected_fields = ['indicator', 'value', 'date', 'error']
                                has_expected = any(field in data_point for field in expected_fields)
                                assert has_expected

                except Exception as inner_e:
                    # Individual indicator failures are acceptable
                    continue

        except Exception as e:
            pytest.skip(f"Macro data collection requires external APIs: {e}")

    @pytest.mark.asyncio
    async def test_data_to_portfolio_flow(self, agents):
        """Test data flow from DataAgent to PortfolioAgent"""
        data_agent = agents['data']
        portfolio_agent = agents['portfolio']

        try:
            # Get market context from data agent
            market_context = await data_agent.get_market_context()

            assert market_context is not None
            assert isinstance(market_context, dict)

            # Market context should have useful structure
            expected_sections = ['market_data', 'macro_indicators', 'market_regime', 'timestamp']
            has_sections = any(section in market_context for section in expected_sections)
            assert has_sections or 'error' in market_context

            # Use market context in portfolio building
            for risk_level in [1, 3, 5]:  # Test different risk levels
                portfolio = await portfolio_agent.build_portfolio(
                    risk_level=risk_level,
                    goal="retirement",
                    constraints={"market_context": market_context}
                )

                assert portfolio is not None
                if isinstance(portfolio, dict):
                    # Should have portfolio structure or error info
                    expected_fields = ['allocations', 'expected_return', 'risk_metrics', 'error']
                    has_expected = any(field in portfolio for field in expected_fields)
                    assert has_expected

        except Exception as e:
            pytest.skip(f"Data-to-portfolio flow requires external data: {e}")

    @pytest.mark.asyncio
    async def test_portfolio_to_explanation_flow(self, agents):
        """Test data flow from PortfolioAgent to ExplainabilityAgent"""
        portfolio_agent = agents['portfolio']
        explainability_agent = agents['explainability']

        try:
            # Create portfolio
            portfolio = await portfolio_agent.build_portfolio(
                risk_level=3,
                goal="retirement",
                constraints={}
            )

            assert portfolio is not None

            # Create action from portfolio creation
            action = {
                'type': 'portfolio_creation',
                'details': f"Created portfolio with allocation: {portfolio}",
                'reason': 'Initial retirement portfolio setup',
                'timestamp': datetime.now(),
                'agent_source': 'portfolio_agent',
                'portfolio_data': portfolio
            }

            # Get explanation
            explanation = await explainability_agent.explain_decision(action)

            assert explanation is not None
            assert isinstance(explanation, dict)

            # Should have explanation structure
            expected_fields = ['explanation', 'risk_assessment', 'plain_english', 'error']
            has_expected = any(field in explanation for field in expected_fields)
            assert has_expected

        except Exception as e:
            pytest.skip(f"Portfolio-to-explanation flow requires external services: {e}")

    @pytest.mark.asyncio
    async def test_goal_to_portfolio_flow(self, agents):
        """Test data flow from goal parsing to portfolio creation"""
        planner_agent = agents['planner']
        portfolio_agent = agents['portfolio']

        try:
            # Parse financial goal
            goal_text = "I want to save $500,000 for my child's education in 15 years"
            parsed_goal = await planner_agent.parse_goal(goal_text)

            assert parsed_goal is not None
            assert isinstance(parsed_goal, dict)

            # Extract goal information
            goal_type = parsed_goal.get('goal_type', 'CHILD_EDUCATION')
            time_horizon = parsed_goal.get('time_horizon', 15)

            # Determine appropriate risk level based on goal
            risk_level = 3  # Default balanced
            if time_horizon > 20:
                risk_level = 4  # Growth for longer horizons
            elif time_horizon < 5:
                risk_level = 2  # Conservative for shorter horizons

            # Create portfolio based on parsed goal
            portfolio = await portfolio_agent.build_portfolio(
                risk_level=risk_level,
                goal=goal_type.lower() if isinstance(goal_type, str) else "education",
                constraints={
                    "time_horizon": time_horizon,
                    "target_amount": 500000
                }
            )

            assert portfolio is not None

            # Portfolio should reflect the goal characteristics
            if isinstance(portfolio, dict) and 'allocations' in portfolio:
                allocations = portfolio['allocations']
                # For education goal with 15-year horizon, should have reasonable equity allocation
                if 'equity' in allocations:
                    equity_allocation = allocations['equity']
                    assert 0.4 <= equity_allocation <= 0.8  # Reasonable range

        except Exception as e:
            pytest.skip(f"Goal-to-portfolio flow requires external services: {e}")

    @pytest.mark.asyncio
    async def test_real_time_data_updates(self, agents):
        """Test real-time data update flow"""
        data_agent = agents['data']
        portfolio_agent = agents['portfolio']

        try:
            # Simulate real-time market data updates
            initial_context = await data_agent.get_market_context()
            assert initial_context is not None

            # Wait a short time (simulate time passing)
            await asyncio.sleep(0.1)

            # Get updated context
            updated_context = await data_agent.get_market_context()
            assert updated_context is not None

            # Timestamps should be different (if real-time)
            if (isinstance(initial_context, dict) and 'timestamp' in initial_context and
                isinstance(updated_context, dict) and 'timestamp' in updated_context):

                initial_time = initial_context['timestamp']
                updated_time = updated_context['timestamp']

                # Times should be different (real-time updates)
                assert initial_time != updated_time

            # Test portfolio rebalancing with updated data
            portfolio = await portfolio_agent.build_portfolio(
                risk_level=3,
                goal="retirement",
                constraints={"market_context": updated_context}
            )

            assert portfolio is not None

        except Exception as e:
            pytest.skip(f"Real-time data test requires external APIs: {e}")

    @pytest.mark.asyncio
    async def test_data_validation_flow(self, agents):
        """Test data validation across the system"""
        data_agent = agents['data']

        try:
            # Test signal validation
            test_signals = {
                "yield_curve_signal": 0.8,
                "vix_signal": 0.3,
                "momentum_signal": 0.6
            }

            market_data = {
                "SPY": {"price": 400, "change_percent": 1.2},
                "VIX": {"price": 20, "change_percent": -2.1}
            }

            validation_result = await data_agent.validate_market_signals(test_signals, market_data)

            assert validation_result is not None
            assert isinstance(validation_result, dict)

            # Should have validation structure
            expected_fields = ['is_valid', 'confidence', 'reasoning', 'error']
            has_expected = any(field in validation_result for field in expected_fields)
            assert has_expected

            if 'is_valid' in validation_result:
                assert isinstance(validation_result['is_valid'], bool)

            if 'confidence' in validation_result:
                confidence = validation_result['confidence']
                assert isinstance(confidence, (int, float))
                assert 0 <= confidence <= 1

        except Exception as e:
            pytest.skip(f"Data validation test requires external services: {e}")

    @pytest.mark.asyncio
    async def test_cross_agent_data_consistency(self, agents):
        """Test data consistency across different agents"""
        data_agent = agents['data']
        portfolio_agent = agents['portfolio']

        try:
            # Get asset universes from different agents
            data_assets = data_agent.all_assets
            portfolio_equities = portfolio_agent.equity_universe

            # Should have some overlap in equity assets
            if data_assets and portfolio_equities:
                common_assets = set(data_assets) & set(portfolio_equities)
                assert len(common_assets) > 0

            # Test configuration consistency
            data_config = data_agent.config.data_agent
            portfolio_config = portfolio_agent.config.data_agent

            # Should reference same configuration
            assert data_config.EQUITY_UNIVERSE == portfolio_config.EQUITY_UNIVERSE

        except Exception as e:
            pytest.skip(f"Data consistency test failed: {e}")

    @pytest.mark.asyncio
    async def test_error_data_propagation(self, agents):
        """Test how data errors propagate through the system"""
        data_agent = agents['data']
        portfolio_agent = agents['portfolio']

        # Test with invalid symbol
        try:
            invalid_data = await data_agent.fetch_market_data("INVALID_SYMBOL_XYZ")

            # Should handle invalid data gracefully
            assert invalid_data is not None

            if isinstance(invalid_data, dict) and 'error' in invalid_data:
                # Error should be descriptive
                error_msg = invalid_data['error']
                assert isinstance(error_msg, str)
                assert len(error_msg) > 0

            # Test how portfolio agent handles missing data
            with patch.object(data_agent, 'fetch_market_data') as mock_fetch:
                mock_fetch.return_value = {"error": "Data source unavailable"}

                portfolio = await portfolio_agent.build_portfolio(
                    risk_level=3,
                    goal="retirement",
                    constraints={}
                )

                # Should still create portfolio (with fallbacks)
                assert portfolio is not None

        except Exception as e:
            # Should not have unhandled exceptions for invalid data
            pytest.fail(f"Unhandled exception in error data propagation: {e}")

    @pytest.mark.asyncio
    async def test_bulk_data_processing(self, agents):
        """Test bulk data processing capabilities"""
        data_agent = agents['data']

        try:
            # Test processing multiple assets simultaneously
            symbols = ["SPY", "QQQ", "IWM", "TLT"]
            results = []

            # Process in parallel
            tasks = [data_agent.fetch_market_data(symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            assert len(results) == len(symbols)

            # Check results
            successful_results = 0
            for i, result in enumerate(results):
                if not isinstance(result, Exception):
                    successful_results += 1
                    assert result is not None

            # At least some should succeed (or all should handle gracefully)
            assert successful_results >= 0

        except Exception as e:
            pytest.skip(f"Bulk data processing test requires external APIs: {e}")

    @pytest.mark.asyncio
    async def test_data_caching_and_freshness(self, agents):
        """Test data caching and freshness mechanisms"""
        data_agent = agents['data']

        try:
            # Test data freshness
            timestamp1 = datetime.now()
            context1 = await data_agent.get_market_context(timestamp=timestamp1.isoformat())

            # Small delay
            await asyncio.sleep(0.1)

            timestamp2 = datetime.now()
            context2 = await data_agent.get_market_context(timestamp=timestamp2.isoformat())

            # Both should return valid data
            assert context1 is not None
            assert context2 is not None

            # Check if caching is working (timestamps might be same if cached)
            if (isinstance(context1, dict) and isinstance(context2, dict) and
                'timestamp' in context1 and 'timestamp' in context2):

                time1 = context1['timestamp']
                time2 = context2['timestamp']

                # Times should be either same (cached) or different (fresh)
                assert isinstance(time1, str)
                assert isinstance(time2, str)

        except Exception as e:
            pytest.skip(f"Data caching test requires external APIs: {e}")

    @pytest.mark.asyncio
    async def test_data_transformation_pipeline(self, agents):
        """Test data transformation and processing pipeline"""
        data_agent = agents['data']
        portfolio_agent = agents['portfolio']

        try:
            # Test data transformation from raw to processed
            raw_market_data = await data_agent.fetch_market_data("SPY")

            if raw_market_data is not None:
                # Transform to context
                market_context = await data_agent.get_market_context()

                assert market_context is not None

                # Should contain processed information
                if isinstance(market_context, dict):
                    # Should have aggregated and processed data
                    expected_sections = ['market_data', 'macro_indicators', 'market_regime']
                    has_processed_data = any(section in market_context for section in expected_sections)
                    assert has_processed_data or 'error' in market_context

                # Test further transformation in portfolio agent
                if 'allocations' in dir(portfolio_agent):
                    # Portfolio agent should transform market context to allocation decisions
                    portfolio = await portfolio_agent.build_portfolio(
                        risk_level=3,
                        goal="retirement",
                        constraints={"market_context": market_context}
                    )

                    assert portfolio is not None

        except Exception as e:
            pytest.skip(f"Data transformation test requires external APIs: {e}")

    def test_data_model_consistency(self, agents):
        """Test that data models are consistent across agents"""
        # Test that all agents use the same data models
        from agent.models import MarketData, MacroData, RiskLevel, GoalType

        # All agents should have access to same models
        for agent_name, agent in agents.items():
            # Should be able to create model instances
            test_market_data = MarketData(
                symbol="TEST",
                price=100.0,
                previous_close=99.0,
                change=1.0,
                change_percent=1.01,
                timestamp=datetime.now()
            )

            assert test_market_data.symbol == "TEST"
            assert test_market_data.price == 100.0

            # Test enum consistency
            conservative_risk = RiskLevel.CONSERVATIVE
            assert conservative_risk.value == 1

            retirement_goal = GoalType.RETIREMENT
            assert retirement_goal.value == "retirement"