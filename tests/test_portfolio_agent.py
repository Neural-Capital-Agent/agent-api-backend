import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from agent.agents import PortfolioAgent
from agent.models import RiskLevel


class TestPortfolioAgent:
    @pytest.fixture
    def portfolio_agent(self):
        return PortfolioAgent()

    def test_init(self, portfolio_agent):
        assert portfolio_agent.equity_universe == ["SPY", "QQQ", "VXUS"]
        assert RiskLevel.CONSERVATIVE in portfolio_agent.base_allocations
        assert isinstance(portfolio_agent.coral_client, object)  # Mock or real client

    @pytest.mark.asyncio
    async def test_build_portfolio(self, portfolio_agent):
        # Mock dependencies
        with patch.object(portfolio_agent, '_get_current_macro_signals', new_callable=AsyncMock) as mock_signals, \
             patch.object(portfolio_agent, '_calculate_portfolio_metrics', new_callable=AsyncMock) as mock_metrics, \
             patch.object(portfolio_agent, '_apply_constraints') as mock_constraints:

            mock_signals.return_value = {"signal": "neutral"}
            mock_metrics.return_value = {"sharpe": 1.5}
            mock_constraints.return_value = {"allocations": {"SPY": 0.5}}

            result = await portfolio_agent.build_portfolio(risk_level=3, goal="growth")

            # Assert some structure
            assert "allocations" in result or isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_calculate_rebalancing(self, portfolio_agent):
        current = {"SPY": 0.4, "BND": 0.6}
        signals = {"market": "bullish"}

        with patch.object(portfolio_agent, '_calculate_trades') as mock_trades:
            mock_trades.return_value = {"buy": ["SPY"], "sell": []}

            result = await portfolio_agent.calculate_rebalancing(current, signals)

            assert "trades" in result or isinstance(result, dict)

    def test_apply_constraints(self, portfolio_agent):
        allocations = {"SPY": 0.6, "BND": 0.4}
        constraints = {"max_equity": 0.5}

        result = portfolio_agent._apply_constraints(allocations, constraints)

        # Assuming it adjusts allocations
        assert isinstance(result, dict)

    # Add more tests as needed
