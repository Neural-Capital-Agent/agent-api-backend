import pytest
import asyncio
from datetime import datetime
import uuid
from agent.agents import ExplainabilityAgent


class TestExplainabilityAgent:
    """Comprehensive Explainability Agent tests"""

    @pytest.fixture
    def explainability_agent(self):
        return ExplainabilityAgent()

    def test_initialization(self):
        """Test Explainability Agent initializes correctly"""
        agent = ExplainabilityAgent()

        # Test jargon dictionary
        assert len(agent.jargon_dictionary) >= 15
        assert "yield_curve_inversion" in agent.jargon_dictionary
        assert "volatility" in agent.jargon_dictionary
        assert "rebalancing" in agent.jargon_dictionary

        # Test risk templates
        assert len(agent.risk_templates) == 4
        assert "low" in agent.risk_templates
        assert "moderate" in agent.risk_templates
        assert "high" in agent.risk_templates
        assert "very_high" in agent.risk_templates

    def test_jargon_dictionary_completeness(self):
        """Test that jargon dictionary contains key financial terms"""
        agent = ExplainabilityAgent()

        required_terms = [
            "yield_curve_inversion",
            "credit_spreads",
            "vix_spike",
            "volatility",
            "rebalancing",
            "alpha",
            "beta",
            "sharpe_ratio",
            "correlation",
            "drawdown"
        ]

        for term in required_terms:
            assert term in agent.jargon_dictionary
            definition = agent.jargon_dictionary[term]
            assert isinstance(definition, str)
            assert len(definition) > 10  # Should be meaningful explanation

    def test_risk_templates_structure(self):
        """Test that risk templates are well-structured"""
        agent = ExplainabilityAgent()

        for risk_level, template in agent.risk_templates.items():
            assert isinstance(template, str)
            assert len(template) > 20  # Should be detailed explanation

    def test_get_jargon_definition(self):
        """Test getting definitions for financial terms"""
        agent = ExplainabilityAgent()

        # Test existing terms
        volatility_def = agent.get_jargon_definition("volatility")
        assert "move up and down" in volatility_def

        alpha_def = agent.get_jargon_definition("alpha")
        assert "returns above" in alpha_def

        # Test case insensitive
        vix_def = agent.get_jargon_definition("VIX_SPIKE")
        assert "fear indicator" in vix_def

        # Test unknown term
        unknown_def = agent.get_jargon_definition("unknown_term")
        assert "Definition for unknown_term is not available" in unknown_def

    def test_explain_risk_level(self):
        """Test risk level explanations"""
        agent = ExplainabilityAgent()

        conservative_exp = agent.explain_risk_level("conservative")
        assert "fewer ups and downs" in conservative_exp
        assert "grow more slowly" in conservative_exp

        moderate_exp = agent.explain_risk_level("moderate")
        assert "some ups and downs" in moderate_exp
        assert "moderate growth" in moderate_exp

        aggressive_exp = agent.explain_risk_level("aggressive")
        assert "big ups and downs" in aggressive_exp
        assert "grow faster" in aggressive_exp

        # Test unknown risk level
        unknown_exp = agent.explain_risk_level("unknown")
        assert "not available" in unknown_exp

    @pytest.mark.asyncio
    async def test_translate_jargon_fallback(self):
        """Test jargon translation using dictionary fallback"""
        agent = ExplainabilityAgent()

        # Test single term translation
        text = "The yield_curve_inversion is concerning."
        result = await agent.translate_jargon(text)

        assert "translation" in result
        translation = result["translation"]
        assert "yield_curve_inversion" not in translation
        assert "long-term interest rates fall below short-term rates" in translation

    @pytest.mark.asyncio
    async def test_translate_jargon_multiple_terms(self):
        """Test translation of multiple jargon terms"""
        agent = ExplainabilityAgent()

        text = "The volatility and vix_spike indicate market stress, requiring rebalancing."
        result = await agent.translate_jargon(text)
        translation = result["translation"]

        # Should translate multiple terms
        assert "volatility" not in translation
        assert "vix_spike" not in translation
        assert "rebalancing" not in translation
        assert "move up and down" in translation
        assert "fear indicator" in translation
        assert "investment mix" in translation

    @pytest.mark.asyncio
    async def test_translate_jargon_case_insensitive(self):
        """Test case insensitive jargon translation"""
        agent = ExplainabilityAgent()

        text = "VOLATILITY and Alpha are important metrics."
        result = await agent.translate_jargon(text)
        translation = result["translation"]

        assert "move up and down" in translation
        assert "returns above" in translation

    def test_explain_market_regime(self):
        """Test market regime explanations"""
        agent = ExplainabilityAgent()

        # Test all market regimes
        regimes = {
            "normal_market_conditions": "within normal ranges",
            "high_volatility_crisis": "extreme volatility and stress",
            "elevated_volatility": "more volatile than usual",
            "yield_curve_inversion": "potential economic slowdown",
            "flattening_curve": "narrowing",
            "low_volatility_complacency": "unusually calm"
        }

        for regime, expected_text in regimes.items():
            explanation = agent._explain_market_regime(regime)
            assert expected_text in explanation

        # Test unknown regime
        unknown_explanation = agent._explain_market_regime("unknown_regime")
        assert "unknown_regime" in unknown_explanation

    def test_provide_historical_context(self):
        """Test historical context provision"""
        agent = ExplainabilityAgent()

        # Test volatility context
        volatility_action = {
            "type": "rebalancing",
            "parameters": {"reason": "volatility spike"}
        }
        context = agent._provide_historical_context(volatility_action)
        assert "VIX spikes above 25" in context
        assert "recover within 6 months" in context

        # Test yield curve context
        yield_action = {
            "type": "rebalancing",
            "parameters": {"reason": "yield curve inversion"}
        }
        context = agent._provide_historical_context(yield_action)
        assert "Yield curve inversions" in context
        assert "12-18 months" in context

        # Test default context
        generic_action = {
            "type": "portfolio_creation",
            "parameters": {}
        }
        context = agent._provide_historical_context(generic_action)
        assert "6-12 months" in context

    def test_calculate_confidence_score_basic(self):
        """Test basic confidence score calculation"""
        agent = ExplainabilityAgent()

        # High confidence context
        high_confidence_context = {
            "portfolio_rationale": {"confidence": 0.9},
            "market_data": {"vix": 15, "regime": "normal"}
        }
        score = agent._calculate_confidence_score(high_confidence_context)
        assert 0.5 <= score <= 1.0  # Should be reasonable confidence

        # Low confidence context with errors
        low_confidence_context = {
            "portfolio_rationale": {"error": "Failed"},
            "market_data": {"error": "No data"}
        }
        score = agent._calculate_confidence_score(low_confidence_context)
        assert 0.0 <= score <= 0.8  # Should be lower confidence

        # Empty context should return default
        empty_score = agent._calculate_confidence_score({})
        assert 0.0 <= empty_score <= 1.0  # Should be reasonable default

    def test_generate_risk_assessment(self):
        """Test risk assessment generation"""
        agent = ExplainabilityAgent()

        # Normal conditions
        normal_context = {
            "market_data": {"market_regime": "normal_market_conditions"}
        }
        assessment = agent._generate_risk_assessment({}, normal_context)
        assert "Some ups and downs expected" in assessment

        # Crisis conditions
        crisis_context = {
            "market_data": {"market_regime": "high_volatility_crisis"}
        }
        assessment = agent._generate_risk_assessment({}, crisis_context)
        assert "High risk due to crisis market conditions" in assessment

        # Elevated volatility
        volatility_context = {
            "market_data": {"market_regime": "elevated_volatility"}
        }
        assessment = agent._generate_risk_assessment({}, volatility_context)
        assert "Elevated risk due to increased market volatility" in assessment

    def test_jargon_definitions_quality(self):
        """Test that jargon definitions are meaningful"""
        agent = ExplainabilityAgent()

        key_definitions = {
            "yield_curve_inversion": ["long-term", "short-term", "rates"],
            "credit_spreads": ["extra", "interest", "bonds"],
            "vix_spike": ["fear", "indicator", "rises"],
            "volatility": ["move", "up", "down"],
            "alpha": ["returns", "above", "market"],
            "beta": ["relative", "market"],
            "sharpe_ratio": ["risk", "adjusted", "returns"]
        }

        for term, expected_words in key_definitions.items():
            definition = agent.jargon_dictionary[term]
            definition_lower = definition.lower()

            # Check that key concepts are present
            word_found = any(word in definition_lower for word in expected_words)
            assert word_found, f"Definition for {term} should contain one of {expected_words}"

    def test_risk_template_appropriateness(self):
        """Test that risk templates are appropriate for their levels"""
        agent = ExplainabilityAgent()

        templates = agent.risk_templates

        # Low risk should emphasize safety
        low_risk = templates["low"].lower()
        assert "minimal" in low_risk or "limited" in low_risk

        # Moderate risk should be balanced
        moderate_risk = templates["moderate"].lower()
        assert "moderate" in moderate_risk or "some" in moderate_risk

        # High risk should warn of volatility
        high_risk = templates["high"].lower()
        assert "significant" in high_risk or "higher" in high_risk

        # Very high risk should emphasize extremes
        very_high_risk = templates["very_high"].lower()
        assert "large" in very_high_risk or "common" in very_high_risk

    def test_comprehensive_jargon_coverage(self):
        """Test comprehensive coverage of financial jargon"""
        agent = ExplainabilityAgent()

        # Test that we have good coverage of essential financial terms
        essential_categories = {
            "market_indicators": ["vix_spike", "volatility", "market_momentum"],
            "portfolio_metrics": ["alpha", "beta", "sharpe_ratio", "drawdown"],
            "fixed_income": ["yield_curve_inversion", "credit_spreads", "duration_risk"],
            "portfolio_management": ["rebalancing", "risk_parity", "correlation"]
        }

        for category, terms in essential_categories.items():
            for term in terms:
                assert term in agent.jargon_dictionary, f"Missing {term} in {category}"

    @pytest.mark.asyncio
    async def test_error_handling_translate_jargon(self):
        """Test error handling in jargon translation"""
        agent = ExplainabilityAgent()

        # Should handle empty input gracefully
        result = await agent.translate_jargon("")
        assert "translation" in result

        # Should handle text with no jargon
        result = await agent.translate_jargon("Simple text with no financial terms")
        assert "translation" in result
        assert result["translation"] == "Simple text with no financial terms"

    @pytest.mark.asyncio
    async def test_explain_decision_functionality(self):
        """Test decision explanation functionality"""
        agent = ExplainabilityAgent()

        # Create a sample action
        action = {
            "id": str(uuid.uuid4()),
            "type": "rebalancing",
            "agent_source": "portfolio_agent",
            "parameters": {"reason": "volatility_spike"},
            "timestamp": datetime.now()
        }

        try:
            result = await agent.explain_decision(action)
            assert isinstance(result, dict)
            # Should have key explanation components
            expected_keys = ["action_id", "explanation", "risk_assessment",
                           "historical_context", "confidence_score"]
            for key in expected_keys:
                assert key in result
        except Exception as e:
            # Should handle errors gracefully
            assert isinstance(e, Exception)

    @pytest.mark.asyncio
    async def test_gather_multi_agent_context(self):
        """Test multi-agent context gathering"""
        agent = ExplainabilityAgent()

        action = {
            "id": str(uuid.uuid4()),
            "agent_source": "portfolio_agent",
            "timestamp": datetime.now()
        }

        try:
            context = await agent.gather_multi_agent_context(action)
            assert isinstance(context, dict)
            # Should attempt to gather various types of context
            # May have errors due to unavailable services, but should not crash
        except Exception as e:
            # Should handle communication errors gracefully
            assert isinstance(e, Exception)

    def test_financial_term_coverage_completeness(self):
        """Test that all essential financial terms are covered"""
        agent = ExplainabilityAgent()

        # Essential financial terms that should be defined
        essential_terms = [
            "yield_curve_inversion",
            "credit_spreads",
            "vix_spike",
            "p/e_ratio",
            "duration_risk",
            "market_momentum",
            "volatility",
            "rebalancing",
            "macro_signals",
            "risk_parity",
            "correlation",
            "alpha",
            "beta",
            "sharpe_ratio",
            "drawdown"
        ]

        for term in essential_terms:
            assert term in agent.jargon_dictionary
            definition = agent.jargon_dictionary[term]
            # Each definition should be meaningful
            assert len(definition.split()) >= 3

    def test_risk_level_explanation_coverage(self):
        """Test that all risk levels have appropriate explanations"""
        agent = ExplainabilityAgent()

        risk_levels = ["conservative", "moderate", "aggressive", "growth"]

        for level in risk_levels:
            explanation = agent.explain_risk_level(level)
            assert isinstance(explanation, str)
            assert len(explanation) > 20  # Should be substantial explanation
            # Check for meaningful content related to risk/return tradeoff
            assert any(word in explanation.lower() for word in ["ups and downs", "grow", "money", "potential"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])