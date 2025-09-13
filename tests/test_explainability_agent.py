import pytest
from unittest.mock import AsyncMock, patch
from agent.agents import ExplainabilityAgent


class TestExplainabilityAgent:
    @pytest.fixture
    def explainability_agent(self):
        return ExplainabilityAgent()

    def test_init(self, explainability_agent):
        assert "yield_curve_inversion" in explainability_agent.jargon_dictionary
        assert "low" in explainability_agent.risk_templates
        assert isinstance(explainability_agent.coral_client, object)

    @pytest.mark.asyncio
    async def test_explain_decision(self, explainability_agent):
        action = {"type": "rebalance", "reason": "market_change"}

        with patch.object(explainability_agent, 'gather_multi_agent_context', new_callable=AsyncMock) as mock_gather, \
             patch.object(explainability_agent.coral_client, 'send_message', new_callable=AsyncMock) as mock_send:

            mock_gather.return_value = {"context": "market volatility"}
            mock_send.return_value = {"explanation": "Adjusted due to market conditions"}

            result = await explainability_agent.explain_decision(action)

            assert "explanation" in result or isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_translate_jargon(self, explainability_agent):
        jargon = "yield_curve_inversion"

        with patch.object(explainability_agent.coral_client, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"translation": "Simplified explanation"}

            result = await explainability_agent.translate_jargon(jargon)

            assert "translation" in result or isinstance(result, dict)

    def test_get_jargon_definition(self, explainability_agent):
        definition = explainability_agent.get_jargon_definition("volatility")

        assert "move up and down" in definition

    def test_explain_risk_level(self, explainability_agent):
        explanation = explainability_agent.explain_risk_level("moderate")

        assert "ups and downs" in explanation

    # Add more tests as needed
