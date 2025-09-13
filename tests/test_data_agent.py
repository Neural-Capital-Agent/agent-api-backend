import pytest
from unittest.mock import AsyncMock, patch
from agent.agents import DataAgent


class TestDataAgent:
    @pytest.fixture
    def data_agent(self):
        return DataAgent()

    def test_init(self, data_agent):
        assert data_agent.equity_universe == ["SPY", "QQQ", "VXUS"]
        assert "CPI" in data_agent.macro_indicators
        assert "daily" in data_agent.update_frequencies

    @pytest.mark.asyncio
    async def test_health_check(self, data_agent):
        # Mock the fetch methods
        with patch.object(data_agent, 'fetch_market_data', new_callable=AsyncMock) as mock_fetch_market, \
             patch.object(data_agent, 'fetch_macro_data', new_callable=AsyncMock) as mock_fetch_macro:

            mock_fetch_market.return_value = {"price": 100}  # Mock successful response
            mock_fetch_macro.return_value = [{"value": 1.5}]  # Mock successful response

            result = await data_agent.health_check()

            assert result["yahoo_finance"] == "healthy"
            assert result["fred"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_error(self, data_agent):
        # Mock the fetch methods to raise exceptions
        with patch.object(data_agent, 'fetch_market_data', new_callable=AsyncMock) as mock_fetch_market, \
             patch.object(data_agent, 'fetch_macro_data', new_callable=AsyncMock) as mock_fetch_macro:

            mock_fetch_market.side_effect = Exception("API error")
            mock_fetch_macro.side_effect = Exception("API error")

            result = await data_agent.health_check()

            assert result["yahoo_finance"] == "error"
            assert result["fred"] == "error"

    @pytest.mark.asyncio
    async def test_fetch_market_data(self, data_agent):
        # This would require mocking yfinance or the utils
        # For now, just test that it doesn't raise
        with patch('agent.agents.yahoo') as mock_yahoo:
            mock_yahoo.get_historical_data.return_value = {"data": []}
            # Assuming the method exists, test basic call
            pass  # Placeholder

    # Add more tests for other methods as needed
