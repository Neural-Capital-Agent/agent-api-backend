from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
import uuid
import re

from ..shared.models import ExplanationResponse
from ..shared.config import config
from ..shared.shared import BaseAgent, ErrorHandler, get_current_timestamp, safe_get, safe_coral_invoke

logger = logging.getLogger(__name__)


class ExplainabilityAgent(BaseAgent):
    """
    Explainability Agent responsible for financial jargon translation
    and decision rationale generation.
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555"):
        super().__init__(coral_server_url, "explainability_agent")

        # Load configuration instead of hardcoded dictionaries
        self.jargon_dictionary = config.explainability_agent.JARGON_DICTIONARY
        self.risk_templates = config.explainability_agent.RISK_TEMPLATES

    async def explain_decision(self, action, context=None):
        """Generate comprehensive explanation for a decision"""
        from ..shared.models import ExplanationResponse

        try:
            # Gather context from all relevant agents
            comprehensive_context = await self.gather_multi_agent_context(action)

            # Generate explanation
            explanation = await self.generate_comprehensive_explanation(action, comprehensive_context)

            # Generate risk assessment
            risk_assessment = self._generate_risk_assessment(action, comprehensive_context)

            # Provide historical context
            historical_context = self._provide_historical_context(action)

            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(comprehensive_context)

            # Create verification hash
            action_id = getattr(action, 'id', None) or (action.get('id') if isinstance(action, dict) else str(uuid.uuid4()))
            verification_hash = self.coral_client.create_verification_hash(explanation, action_id)

            response = ExplanationResponse(
                action_id=action_id,
                explanation=explanation,
                risk_assessment=risk_assessment,
                historical_context=historical_context,
                confidence_score=confidence_score,
                verification_hash=verification_hash
            )

            logger.info(f"Generated explanation for action {action_id}")
            # Convert to dict for API compatibility
            return {
                "summary": response.explanation,
                "risk_assessment": {"level": "moderate"},  # Simplified risk assessment
                "confidence_score": response.confidence_score,
                "verification_hash": response.verification_hash
            }

        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error(f"Error explaining decision: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error explaining decision: {e}")
            raise

    async def translate_jargon(self, technical_text: str):
        """Convert technical financial terms to plain English"""
        try:
            # First try using Mistral LLM via Coral Protocol
            llm_response = await safe_coral_invoke(
                self.coral_client,
                "llm_agent",
                "translate_jargon",
                {"text": technical_text},
                "translate_jargon"
            )
            if llm_response and llm_response.get("translation") and not llm_response.get("error"):
                return {"translation": llm_response["translation"]}

            # Fallback to dictionary-based translation
            import re
            translated_text = technical_text

            for term, explanation in self.jargon_dictionary.items():
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                translated_text = pattern.sub(f"{explanation}", translated_text)

            return {"translation": translated_text}

        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error translating jargon: {e}")
            return {"translation": technical_text}
        except Exception as e:
            logger.error(f"Unexpected error translating jargon: {e}")
            return {"translation": technical_text}

    def get_jargon_definition(self, term: str):
        """Get plain English definition for a financial term"""
        return self.jargon_dictionary.get(term.lower(), f"Definition for {term} is not available.")

    def explain_risk_level(self, risk_level: str):
        """Explain what a risk level means in plain English"""
        explanations = config.explainability_agent.RISK_LEVEL_EXPLANATIONS
        return explanations.get(risk_level.lower(), "Risk level explanation not available.")

    def generate_risk_warning(self, portfolio):
        """Generate risk warning based on portfolio composition"""
        try:
            risk_level = portfolio.risk_level.value
            volatility = portfolio.volatility

            if risk_level <= 2 and volatility < 0.1:
                risk_category = "low"
            elif risk_level <= 3 and volatility < 0.15:
                risk_category = "moderate"
            elif risk_level <= 4 and volatility < 0.25:
                risk_category = "high"
            else:
                risk_category = "very_high"

            base_warning = self.risk_templates[risk_category]

            # Add specific warnings
            specific_warnings = []

            max_allocation = max(portfolio.allocations.values()) if portfolio.allocations else 0
            if max_allocation > 0.4:
                specific_warnings.append("High concentration in single asset increases risk.")

            crypto_assets = ["BTC-USD", "ETH-USD"]
            crypto_exposure = sum(portfolio.allocations.get(asset, 0) for asset in crypto_assets)
            if crypto_exposure > 0:
                specific_warnings.append("Cryptocurrency investments are highly volatile and speculative.")

            warning = base_warning
            if specific_warnings:
                warning += " Additional considerations: " + " ".join(specific_warnings)

            return warning

        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error(f"Error generating risk warning: {e}")
            return "Please carefully consider the risks associated with this investment strategy."
        except Exception as e:
            logger.error(f"Unexpected error generating risk warning: {e}")
            return "Please carefully consider the risks associated with this investment strategy."

    async def gather_multi_agent_context(self, action):
        """Query all relevant agents for decision context via Coral Protocol"""
        try:
            context = {}

            # Get portfolio reasoning if action is from portfolio agent
            agent_source = getattr(action, 'agent_source', None) or (action.get('agent_source') if isinstance(action, dict) else None)
            action_id = getattr(action, 'id', None) or (action.get('id') if isinstance(action, dict) else str(uuid.uuid4()))

            if agent_source == "portfolio_agent":
                portfolio_rationale = await safe_coral_invoke(
                    self.coral_client,
                    "portfolio_agent",
                    "get_decision_rationale",
                    {"action_id": action_id},
                    "get_portfolio_rationale"
                )
                context["portfolio_rationale"] = portfolio_rationale or {"error": "Failed to get portfolio rationale"}

            # Get market data context
            action_timestamp = getattr(action, 'timestamp', None) or (action.get('timestamp') if isinstance(action, dict) else datetime.now())
            timestamp_str = action_timestamp.isoformat() if hasattr(action_timestamp, 'isoformat') else str(action_timestamp)
            market_data = await safe_coral_invoke(
                self.coral_client,
                "data_agent",
                "get_market_context",
                {"timestamp": timestamp_str},
                "get_market_context"
            )
            context["market_data"] = market_data or {"error": "Failed to get market context"}

            return context

        except Exception as e:
            logger.error(f"Error gathering multi-agent context: {e}")
            return {}

    async def generate_comprehensive_explanation(self, action, context):
        """Generate explanation using context from all relevant agents"""
        try:
            explanation_parts = []

            action_type = getattr(action, 'action_type', None) or (action.get('type') if isinstance(action, dict) else 'unknown')
            explanation_parts.append(f"Action taken: {action_type}")

            portfolio_rationale = context.get("portfolio_rationale", {})
            if portfolio_rationale and not portfolio_rationale.get("error"):
                reason = portfolio_rationale.get("reason", "Portfolio adjustment")
                explanation_parts.append(f"Reason: {reason}")

            market_data = context.get("market_data", {})
            if market_data and not market_data.get("error"):
                market_regime = market_data.get("market_regime", "normal_market_conditions")
                market_regime_explanation = self._explain_market_regime(market_regime)
                explanation_parts.append(f"Market conditions: {market_regime_explanation}")

            full_explanation = " ".join(explanation_parts)
            translation_result = await self.translate_jargon(full_explanation)
            plain_english_explanation = translation_result.get("translation", full_explanation)

            return plain_english_explanation

        except Exception as e:
            logger.error(f"Error generating comprehensive explanation: {e}")
            action_type = getattr(action, 'action_type', None) or (action.get('type') if isinstance(action, dict) else 'action')
            return f"Decision made based on {action_type} with current market conditions."

    def _generate_risk_assessment(self, action, context):
        """Generate risk assessment for the action"""
        try:
            risk_factors = []

            market_data = context.get("market_data", {})
            if market_data and not market_data.get("error"):
                market_regime = market_data.get("market_regime", "normal")

                if "crisis" in market_regime:
                    risk_factors.append("High risk due to crisis market conditions")
                elif "volatility" in market_regime:
                    risk_factors.append("Elevated risk due to increased market volatility")

            if not risk_factors:
                return self.risk_templates["moderate"]

            return "Risk factors identified: " + "; ".join(risk_factors) + ". " + self.risk_templates["moderate"]

        except Exception as e:
            logger.error(f"Error generating risk assessment: {e}")
            return self.risk_templates["moderate"]

    def _provide_historical_context(self, action):
        """Provide historical context for the action"""
        try:
            action_type = getattr(action, 'action_type', None) or (action.get('type') if isinstance(action, dict) else 'unknown')
            action_parameters = getattr(action, 'parameters', None) or (action.get('parameters') if isinstance(action, dict) else {})

            if action_type == "rebalancing":
                if "volatility" in str(action_parameters).lower():
                    return "VIX spikes above 25 historically coincide with market corrections, but markets usually recover within 6 months."
                elif "yield" in str(action_parameters).lower():
                    return "Yield curve inversions historically signal recession within 12-18 months, with markets typically declining 20-30% but recovering within 2-3 years."

            return "Historical patterns suggest similar market conditions typically resolve within 6-12 months."

        except Exception as e:
            logger.error(f"Error providing historical context: {e}")
            return "Historical context analysis is not available."

    def _calculate_confidence_score(self, context):
        """Calculate confidence score based on available context"""
        try:
            confidence_factors = []

            portfolio_rationale = context.get("portfolio_rationale", {})
            if portfolio_rationale and not portfolio_rationale.get("error"):
                conf = portfolio_rationale.get("confidence", config.explainability_agent.DEFAULT_CONFIDENCE_SCORE)
                confidence_factors.append(conf)

            market_data = context.get("market_data", {})
            if market_data and not market_data.get("error"):
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.3)

            if confidence_factors:
                return sum(confidence_factors) / len(confidence_factors)
            else:
                return 0.0  # No confidence if no data available

        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.0  # No confidence if calculation fails

    def _explain_market_regime(self, market_regime):
        """Explain market regime in plain English"""
        regime_explanations = config.explainability_agent.MARKET_REGIME_EXPLANATIONS
        return regime_explanations.get(market_regime, f"Current market regime: {market_regime}")

    # Advanced explanation methods
    async def generate_decision_narrative(self, action: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """
        Generate a personalized narrative explanation for a decision.

        Args:
            action: Action to explain
            user_profile: User profile for personalization

        Returns:
            Personalized narrative explanation
        """
        try:
            # Get comprehensive context
            context = await self.gather_multi_agent_context(action)

            # Personalize based on user profile
            user_age = user_profile.get("age", 35)
            risk_tolerance = user_profile.get("risk_tolerance", "moderate")
            goals = user_profile.get("goals", [])

            narrative_parts = []

            # Opening based on user context
            if user_age < 35:
                narrative_parts.append("Given your young age and long investment horizon,")
            elif user_age < 50:
                narrative_parts.append("At your current life stage,")
            else:
                narrative_parts.append("Considering your approaching retirement,")

            # Action explanation
            action_type = action.get("type", "investment decision")
            narrative_parts.append(f"this {action_type} is designed to")

            # Goal alignment
            if goals:
                primary_goal = goals[0].get("type", "financial security")
                narrative_parts.append(f"help you achieve your {primary_goal} goal")

            # Risk context
            risk_explanation = self.explain_risk_level(risk_tolerance)
            narrative_parts.append(f"while maintaining your {risk_tolerance} risk preference.")
            narrative_parts.append(risk_explanation)

            # Market context
            market_data = context.get("market_data", {})
            if market_data and not market_data.get("error"):
                market_regime = market_data.get("market_regime", "normal_market_conditions")
                market_explanation = self._explain_market_regime(market_regime)
                narrative_parts.append(f"Current market conditions show {market_explanation.lower()}")

            return " ".join(narrative_parts)

        except Exception as e:
            logger.error(f"Error generating decision narrative: {e}")
            return "This investment decision was made to help you achieve your financial goals based on current market conditions and your risk profile."

    async def explain_portfolio_performance(self, performance_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Explain portfolio performance in plain English.

        Args:
            performance_data: Portfolio performance metrics

        Returns:
            Plain English explanations for each metric
        """
        try:
            explanations = {}

            # Total return explanation
            total_return = performance_data.get("total_return", 0)
            if total_return > 0.1:
                explanations["total_return"] = f"Your portfolio gained {total_return:.1%} over the period, which is strong performance."
            elif total_return > 0.05:
                explanations["total_return"] = f"Your portfolio gained {total_return:.1%}, which is solid performance."
            else:
                explanations["total_return"] = f"Your portfolio returned {total_return:.1%}. While modest, this is within expectations given market conditions."

            # Volatility explanation
            volatility = performance_data.get("volatility", 0)
            if volatility > 0.2:
                explanations["volatility"] = "Your portfolio experienced high ups and downs, typical of growth-focused investments."
            elif volatility > 0.1:
                explanations["volatility"] = "Your portfolio had moderate ups and downs, which is normal for balanced investments."
            else:
                explanations["volatility"] = "Your portfolio was relatively stable with minimal ups and downs."

            # Sharpe ratio explanation
            sharpe_ratio = performance_data.get("sharpe_ratio", 0)
            if sharpe_ratio > 1.0:
                explanations["sharpe_ratio"] = "Your portfolio provided excellent returns relative to the risk taken."
            elif sharpe_ratio > 0.5:
                explanations["sharpe_ratio"] = "Your portfolio provided good returns for the level of risk."
            else:
                explanations["sharpe_ratio"] = "Your portfolio's returns could be improved relative to the risk level."

            # Max drawdown explanation
            max_drawdown = performance_data.get("max_drawdown", 0)
            if max_drawdown > 0.2:
                explanations["max_drawdown"] = f"At its worst point, your portfolio was down {max_drawdown:.1%} from its peak."
            else:
                explanations["max_drawdown"] = f"Your portfolio's largest decline was {max_drawdown:.1%}, showing good downside protection."

            return explanations

        except Exception as e:
            logger.error(f"Error explaining portfolio performance: {e}")
            return {"error": "Unable to generate performance explanations"}

    async def create_educational_content(self, topic: str, complexity_level: str = "beginner") -> Dict[str, Any]:
        """
        Create educational content about financial topics.

        Args:
            topic: Financial topic to explain
            complexity_level: beginner, intermediate, or advanced

        Returns:
            Educational content with explanations and examples
        """
        try:
            content = {
                "topic": topic,
                "complexity_level": complexity_level,
                "explanation": "",
                "key_points": [],
                "examples": [],
                "related_terms": []
            }

            # Define content based on topic and complexity
            if topic.lower() in ["diversification", "portfolio diversification"]:
                if complexity_level == "beginner":
                    content["explanation"] = "Diversification means not putting all your eggs in one basket. By spreading your investments across different types of assets, you reduce the risk that one bad investment will hurt your entire portfolio."
                    content["key_points"] = [
                        "Spread investments across different asset types",
                        "Reduces overall portfolio risk",
                        "May limit maximum gains but protects against large losses"
                    ]
                    content["examples"] = [
                        "Instead of buying only tech stocks, buy stocks, bonds, and real estate",
                        "Invest in both US and international markets"
                    ]
                else:
                    content["explanation"] = "Diversification is a risk management strategy that mixes a wide variety of investments within a portfolio to minimize the impact of any single security's poor performance on the overall portfolio."
                    content["key_points"] = [
                        "Correlation coefficients determine effective diversification",
                        "Modern Portfolio Theory provides mathematical framework",
                        "Optimal diversification balances risk and return"
                    ]

            elif topic.lower() in ["rebalancing", "portfolio rebalancing"]:
                content["explanation"] = "Rebalancing means adjusting your portfolio back to your target allocation when market movements cause it to drift from your intended mix."
                content["key_points"] = [
                    "Maintains desired risk level",
                    "Forces disciplined buying low and selling high",
                    "Can be done on schedule or when allocations drift too far"
                ]
                content["examples"] = [
                    "If stocks do well and become 70% of your portfolio instead of 60%, you sell some stocks and buy bonds",
                    "Quarterly or annual rebalancing schedules"
                ]

            # Add related terms
            if topic.lower() in ["diversification"]:
                content["related_terms"] = [
                    "Asset allocation", "Correlation", "Risk management", "Modern Portfolio Theory"
                ]
            elif topic.lower() in ["rebalancing"]:
                content["related_terms"] = [
                    "Asset allocation", "Portfolio drift", "Target allocation", "Dollar-cost averaging"
                ]

            return content

        except Exception as e:
            logger.error(f"Error creating educational content: {e}")
            return {"error": str(e)}

    async def generate_glossary_term(self, term: str) -> Dict[str, str]:
        """
        Generate comprehensive glossary entry for a financial term.

        Args:
            term: Financial term to define

        Returns:
            Glossary entry with definition, example, and context
        """
        try:
            glossary_entry = {
                "term": term,
                "simple_definition": "",
                "detailed_definition": "",
                "example": "",
                "context": ""
            }

            # Check if term exists in jargon dictionary
            if term.lower() in self.jargon_dictionary:
                glossary_entry["simple_definition"] = self.jargon_dictionary[term.lower()]

            # Add detailed definitions for common terms
            term_lower = term.lower()
            if "sharpe ratio" in term_lower:
                glossary_entry["detailed_definition"] = "A measure of risk-adjusted return calculated as (portfolio return - risk-free rate) divided by portfolio volatility."
                glossary_entry["example"] = "A Sharpe ratio of 1.0 means you earned 1% of extra return for each 1% of extra risk taken."
                glossary_entry["context"] = "Higher Sharpe ratios indicate better risk-adjusted performance. Generally, ratios above 1.0 are considered good."

            elif "beta" in term_lower:
                glossary_entry["detailed_definition"] = "A measure of how much an investment moves relative to the overall market."
                glossary_entry["example"] = "A beta of 1.2 means the stock typically moves 20% more than the market in either direction."
                glossary_entry["context"] = "Beta of 1.0 = moves with market, >1.0 = more volatile than market, <1.0 = less volatile than market."

            return glossary_entry

        except Exception as e:
            logger.error(f"Error generating glossary term: {e}")
            return {"error": str(e)}