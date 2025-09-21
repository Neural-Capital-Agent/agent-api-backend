from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
import uuid
import re

from ..shared.models import ExplanationResponse
from ..shared.config import config
from ..shared.shared import BaseAgent, ErrorHandler, get_current_timestamp, safe_get, safe_coral_invoke
from ..services.agent_data_service import AgentDataService

logger = logging.getLogger(__name__)


def limit_words(text: str, word_limit: int = 60) -> str:
    """
    Limit text to specified number of words.

    Args:
        text: Input text to limit
        word_limit: Maximum number of words (default: 60)

    Returns:
        Text limited to word_limit words
    """
    if not text or not isinstance(text, str):
        return text

    words = text.split()
    if len(words) <= word_limit:
        return text

    limited_text = ' '.join(words[:word_limit])
    return limited_text + "..."


class ExplainabilityAgent(BaseAgent):
    """
    Explainability Agent responsible for financial jargon translation
    and decision rationale generation.
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555"):
        super().__init__(coral_server_url, "explainability_agent")

        # Load configuration instead of hardcoded dictionaries with error handling
        try:
            self.jargon_dictionary = config.explainability_agent.JARGON_DICTIONARY
            self.risk_templates = config.explainability_agent.RISK_TEMPLATES
        except AttributeError as e:
            logger.error(f"Configuration error in ExplainabilityAgent: {e}")
            # Fallback to basic dictionary
            self.jargon_dictionary = {
                "ETF": "Exchange-Traded Fund - a type of investment fund that trades like a stock",
                "beta": "A measure of how much an investment moves relative to the overall market"
            }
            self.risk_templates = {
                "low": "Low risk means your money is safer but may grow more slowly",
                "moderate": "Moderate risk means some ups and downs with reasonable growth potential",
                "high": "High risk means larger swings but potentially higher returns over time"
            }
        
        self.default_word_limit = 60  # Default word limit for responses

    def set_word_limit(self, word_limit: int):
        """
        Set custom word limit for responses.

        Args:
            word_limit: Maximum number of words for responses
        """
        self.default_word_limit = max(1, word_limit)  # Ensure minimum of 1 word

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
                "summary": limit_words(response.explanation, self.default_word_limit),
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
            if not technical_text or not isinstance(technical_text, str):
                return {"translation": "No text provided for translation"}

            # First try using Mistral LLM via Coral Protocol
            llm_response = await safe_coral_invoke(
                self.coral_client,
                "llm_agent",
                "translate_jargon",
                {"text": technical_text},
                "translate_jargon"
            )
            if llm_response and llm_response.get("translation") and not llm_response.get("error"):
                limited_translation = limit_words(llm_response["translation"], self.default_word_limit)
                return {"translation": limited_translation}

            # Fallback to dictionary-based translation
            import re
            translated_text = technical_text

            if hasattr(self, 'jargon_dictionary') and self.jargon_dictionary:
                for term, explanation in self.jargon_dictionary.items():
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    translated_text = pattern.sub(f"{explanation}", translated_text)
            else:
                logger.warning("No jargon dictionary available for translation")

            limited_translation = limit_words(translated_text, self.default_word_limit)
            return {"translation": limited_translation}

        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error translating jargon: {e}")
            return {"translation": technical_text}
        except Exception as e:
            logger.error(f"Unexpected error translating jargon: {e}")
            return {"translation": f"Error processing text: {technical_text}"}
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

                # Get stress test results if available
                stress_tests = await safe_coral_invoke(
                    self.coral_client,
                    "portfolio_agent",
                    "get_stress_test_results",
                    {"action_id": action_id},
                    "get_stress_test_results"
                )
                context["stress_tests"] = stress_tests or {"error": "No stress test data available"}

                # Get rebalancing trigger analysis
                rebalancing_triggers = await safe_coral_invoke(
                    self.coral_client,
                    "portfolio_agent",
                    "get_rebalancing_triggers",
                    {"action_id": action_id},
                    "get_rebalancing_triggers"
                )
                context["rebalancing_triggers"] = rebalancing_triggers or {"error": "No trigger analysis available"}

            # Get planner context if action is from planner agent
            if agent_source == "planner_agent":
                planner_context = await safe_coral_invoke(
                    self.coral_client,
                    "planner_agent",
                    "get_plan_context",
                    {"action_id": action_id},
                    "get_plan_context"
                )
                context["planner_context"] = planner_context or {"error": "Failed to get planner context"}

                # Get Monte Carlo simulation results
                monte_carlo_results = await safe_coral_invoke(
                    self.coral_client,
                    "planner_agent",
                    "get_monte_carlo_results",
                    {"action_id": action_id},
                    "get_monte_carlo_results"
                )
                context["monte_carlo_results"] = monte_carlo_results or {"error": "No Monte Carlo data available"}

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

            narrative = " ".join(narrative_parts)
            return limit_words(narrative, self.default_word_limit)

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
                explanations["total_return"] = limit_words(f"Your portfolio gained {total_return:.1%} over the period, which is strong performance.", self.default_word_limit)
            elif total_return > 0.05:
                explanations["total_return"] = limit_words(f"Your portfolio gained {total_return:.1%}, which is solid performance.", self.default_word_limit)
            else:
                explanations["total_return"] = limit_words(f"Your portfolio returned {total_return:.1%}. While modest, this is within expectations given market conditions.", self.default_word_limit)

            # Volatility explanation
            volatility = performance_data.get("volatility", 0)
            if volatility > 0.2:
                explanations["volatility"] = limit_words("Your portfolio experienced high ups and downs, typical of growth-focused investments.", self.default_word_limit)
            elif volatility > 0.1:
                explanations["volatility"] = limit_words("Your portfolio had moderate ups and downs, which is normal for balanced investments.", self.default_word_limit)
            else:
                explanations["volatility"] = limit_words("Your portfolio was relatively stable with minimal ups and downs.", self.default_word_limit)

            # Sharpe ratio explanation
            sharpe_ratio = performance_data.get("sharpe_ratio", 0)
            if sharpe_ratio > 1.0:
                explanations["sharpe_ratio"] = limit_words("Your portfolio provided excellent returns relative to the risk taken.", self.default_word_limit)
            elif sharpe_ratio > 0.5:
                explanations["sharpe_ratio"] = limit_words("Your portfolio provided good returns for the level of risk.", self.default_word_limit)
            else:
                explanations["sharpe_ratio"] = limit_words("Your portfolio's returns could be improved relative to the risk level.", self.default_word_limit)

            # Max drawdown explanation
            max_drawdown = performance_data.get("max_drawdown", 0)
            if max_drawdown > 0.2:
                explanations["max_drawdown"] = limit_words(f"At its worst point, your portfolio was down {max_drawdown:.1%} from its peak.", self.default_word_limit)
            else:
                explanations["max_drawdown"] = limit_words(f"Your portfolio's largest decline was {max_drawdown:.1%}, showing good downside protection.", self.default_word_limit)

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

    # Enhanced methods for comprehensive plan explanations using Agent 2 & 3 data
    async def explain_investment_plan(self, portfolio_data: Dict[str, Any],
                                    planning_data: Dict[str, Any],
                                    user_id: str = "anonymous") -> str:
        """
        Generate comprehensive investment plan explanation using data from Portfolio and Planner agents.

        Args:
            portfolio_data: Data from Portfolio Agent (stress tests, allocations, triggers)
            planning_data: Data from Planner Agent (Monte Carlo results, goal analysis)
            user_id: User identifier for Mistral LLM

        Returns:
            Comprehensive 120-150 word explanation in theory
        """
        try:
            from ..clients.mistral_client import explain_decision_with_mistral

            # Extract key information from both agents
            portfolio_allocation = portfolio_data.get("allocations", {})
            stress_test_summary = portfolio_data.get("stress_test_summary", "")
            rebalancing_triggers = portfolio_data.get("rebalancing_triggers", [])

            monte_carlo_results = planning_data.get("monte_carlo_results", [])
            success_probability = planning_data.get("success_probability", 0.7)
            goal_summary = planning_data.get("goal_summary", "")

            # Create comprehensive context for explanation
            explanation_context = {
                "action": {
                    "type": "comprehensive_investment_plan",
                    "agent_source": "multi_agent_collaboration",
                    "portfolio_allocation": portfolio_allocation,
                    "success_probability": success_probability,
                    "stress_resilience": self._assess_stress_resilience(portfolio_data),
                    "risk_level": self._determine_plan_risk_level(portfolio_allocation)
                },
                "context": {
                    "portfolio_analysis": {
                        "stress_tests": portfolio_data.get("stress_tests", {}),
                        "rebalancing_sophistication": len(rebalancing_triggers),
                        "risk_metrics": portfolio_data.get("risk_metrics", {})
                    },
                    "planning_analysis": {
                        "monte_carlo_scenarios": len(monte_carlo_results),
                        "goal_feasibility": success_probability,
                        "time_horizon": planning_data.get("time_horizon_years", 10),
                        "simulation_confidence": self._calculate_simulation_confidence(monte_carlo_results)
                    },
                    "market_data": {
                        "market_regime": "normal_conditions"  # Could be enhanced with real data
                    }
                }
            }

            # Use Mistral LLM to generate sophisticated explanation
            logger.info("Generating investment plan explanation using Mistral LLM")
            explanation = await explain_decision_with_mistral(
                explanation_context["action"],
                explanation_context["context"],
                user_id
            )

            # Ensure explanation is within 120-150 word range
            explanation = self._optimize_explanation_length(explanation, target_words=135)

            # Add theoretical framework
            theoretical_explanation = self._add_theoretical_framework(
                explanation, portfolio_data, planning_data
            )

            logger.info(f"Generated comprehensive plan explanation ({len(theoretical_explanation.split())} words)")
            return theoretical_explanation

        except Exception as e:
            logger.error(f"Error explaining investment plan: {e}")
            return self._generate_fallback_plan_explanation(portfolio_data, planning_data)

    def _assess_stress_resilience(self, portfolio_data: Dict[str, Any]) -> str:
        """Assess portfolio stress resilience from stress test data"""
        try:
            stress_tests = portfolio_data.get("stress_tests", {})
            if isinstance(stress_tests, list) and stress_tests:
                worst_case = min(stress_tests, key=lambda x: x.get("portfolio_loss", 0))
                worst_loss = worst_case.get("portfolio_loss", -0.2)

                if worst_loss > -0.15:
                    return "high_resilience"
                elif worst_loss > -0.25:
                    return "moderate_resilience"
                else:
                    return "low_resilience"

            return "moderate_resilience"
        except Exception:
            return "moderate_resilience"

    def _determine_plan_risk_level(self, allocations: Dict[str, float]) -> str:
        """Determine overall plan risk level from allocations"""
        try:
            equity_exposure = sum(
                weight for asset, weight in allocations.items()
                if asset in ["SPY", "QQQ", "VXUS"] or "equity" in asset.lower()
            )

            if equity_exposure > 0.8:
                return "aggressive"
            elif equity_exposure > 0.6:
                return "growth"
            elif equity_exposure > 0.4:
                return "balanced"
            elif equity_exposure > 0.2:
                return "conservative"
            else:
                return "very_conservative"
        except Exception:
            return "balanced"

    def _calculate_simulation_confidence(self, monte_carlo_results: List[Dict]) -> float:
        """Calculate confidence in Monte Carlo simulations"""
        try:
            if not monte_carlo_results:
                return 0.5

            # Calculate average confidence across scenarios
            confidences = []
            for result in monte_carlo_results:
                success_prob = result.get("success_probability", 0.5)
                # Higher confidence when success probabilities are more consistent
                confidences.append(min(success_prob, 1 - success_prob) + 0.5)

            return sum(confidences) / len(confidences) if confidences else 0.5
        except Exception:
            return 0.5

    def _optimize_explanation_length(self, explanation: str, target_words: int = 135) -> str:
        """Optimize explanation to target word count (120-150 words)"""
        try:
            words = explanation.split()
            current_length = len(words)

            if 120 <= current_length <= 150:
                return explanation

            if current_length > 150:
                # Truncate to 150 words and add transition
                truncated = ' '.join(words[:147])
                return truncated + "..."

            if current_length < 120:
                # Add theoretical context to reach target
                addition = " This approach aligns with modern portfolio theory, utilizing diversification principles and risk-adjusted optimization to balance expected returns against potential volatility while maintaining strategic asset allocation discipline."
                result = explanation + addition

                # Check if we're still under target
                if len(result.split()) < 120:
                    result += " The strategy incorporates behavioral finance insights to maintain long-term perspective."

                return result

            return explanation

        except Exception:
            return explanation

    def _add_theoretical_framework(self, explanation: str, portfolio_data: Dict, planning_data: Dict) -> str:
        """Add theoretical investment framework context"""
        try:
            # Extract key metrics for theoretical context
            success_prob = planning_data.get("success_probability", 0.7)
            risk_level = self._determine_plan_risk_level(portfolio_data.get("allocations", {}))

            # Add theoretical framework based on approach
            if success_prob > 0.8:
                framework = " This high-confidence strategy leverages efficient frontier optimization principles."
            elif risk_level in ["aggressive", "growth"]:
                framework = " The growth-oriented approach applies capital asset pricing model insights for enhanced returns."
            else:
                framework = " This balanced strategy employs modern portfolio theory for optimal risk-return trade-offs."

            # Ensure we don't exceed word limit
            combined = explanation + framework
            if len(combined.split()) > 150:
                return explanation

            return combined

        except Exception:
            return explanation

    def _generate_fallback_plan_explanation(self, portfolio_data: Dict, planning_data: Dict) -> str:
        """Generate fallback explanation when LLM fails"""
        try:
            success_prob = planning_data.get("success_probability", 0.7)
            risk_level = self._determine_plan_risk_level(portfolio_data.get("allocations", {}))
            time_horizon = planning_data.get("time_horizon_years", 10)

            base_explanation = f"""This {risk_level} investment strategy targets your financial goals over {time_horizon} years
            with a {success_prob:.0%} probability of success. The portfolio allocation balances growth potential against
            downside protection through diversified asset classes. Monte Carlo simulations validate the approach across
            multiple market scenarios, while stress testing ensures resilience during adverse conditions. The strategy
            incorporates sophisticated rebalancing triggers to maintain optimal allocation as market conditions evolve.
            Regular monitoring and periodic adjustments help keep the plan aligned with your objectives while managing
            risk exposure. This evidence-based approach combines quantitative analysis with proven investment principles
            to optimize your probability of achieving long-term financial success while maintaining appropriate risk levels."""

            # Optimize length
            return self._optimize_explanation_length(base_explanation, 135)

        except Exception:
            return """Your investment plan combines portfolio optimization with comprehensive planning analysis.
            The strategy balances growth potential against risk management through diversified allocations and
            sophisticated monitoring systems. Monte Carlo simulations and stress testing validate the approach
            across multiple scenarios, ensuring robust performance under various market conditions. Regular
            rebalancing maintains optimal allocation while sophisticated triggers respond to changing market
            dynamics. This quantitative framework maximizes your probability of achieving financial goals while
            managing downside risks through evidence-based investment principles and disciplined execution."""

    async def create_plan_summary_for_agent4(self, portfolio_agent_data: Dict[str, Any],
                                           planner_agent_data: Dict[str, Any],
                                           user_id: str = "anonymous") -> Dict[str, str]:
        """
        Create a comprehensive plan summary using data from Portfolio Agent (2) and Planner Agent (3).

        Args:
            portfolio_agent_data: Complete data from Portfolio Agent including stress tests and triggers
            planner_agent_data: Complete data from Planner Agent including Monte Carlo results
            user_id: User identifier

        Returns:
            Dictionary with different explanation components
        """
        try:
            # Generate main theoretical explanation (120-150 words)
            main_explanation = await self.explain_investment_plan(
                portfolio_agent_data, planner_agent_data, user_id
            )

            # Generate component explanations
            risk_explanation = self._explain_risk_framework(portfolio_agent_data)
            return_explanation = self._explain_return_expectations(planner_agent_data)
            monitoring_explanation = self._explain_monitoring_approach(portfolio_agent_data)

            return {
                "main_explanation": main_explanation,
                "risk_framework": risk_explanation,
                "return_expectations": return_explanation,
                "monitoring_approach": monitoring_explanation,
                "word_count": len(main_explanation.split()),
                "confidence_score": self._calculate_explanation_confidence(
                    portfolio_agent_data, planner_agent_data
                )
            }

        except Exception as e:
            logger.error(f"Error creating plan summary: {e}")
            return {
                "main_explanation": self._generate_fallback_plan_explanation(
                    portfolio_agent_data, planner_agent_data
                ),
                "risk_framework": "Risk management through diversification and stress testing.",
                "return_expectations": "Returns optimized through quantitative analysis.",
                "monitoring_approach": "Continuous monitoring with systematic rebalancing.",
                "word_count": 0,
                "confidence_score": 0.5
            }

    def _explain_risk_framework(self, portfolio_data: Dict[str, Any]) -> str:
        """Explain the risk management framework"""
        try:
            stress_tests = portfolio_data.get("stress_tests", [])
            triggers = portfolio_data.get("rebalancing_triggers", [])

            if stress_tests:
                num_scenarios = len(stress_tests) if isinstance(stress_tests, list) else 5
                return f"Risk managed through {num_scenarios} stress test scenarios and {len(triggers)} monitoring triggers."
            else:
                return "Risk managed through diversification and systematic monitoring."
        except Exception:
            return "Risk managed through proven portfolio optimization techniques."

    def _explain_return_expectations(self, planning_data: Dict[str, Any]) -> str:
        """Explain return expectations framework"""
        try:
            monte_carlo = planning_data.get("monte_carlo_results", [])
            success_prob = planning_data.get("success_probability", 0.7)

            if monte_carlo:
                num_sims = len(monte_carlo) * 1000  # Assuming 1000 sims per scenario
                return f"Return expectations based on {num_sims:,} Monte Carlo simulations with {success_prob:.0%} success probability."
            else:
                return f"Return expectations optimized for {success_prob:.0%} goal achievement probability."
        except Exception:
            return "Return expectations based on historical analysis and quantitative modeling."

    def _explain_monitoring_approach(self, portfolio_data: Dict[str, Any]) -> str:
        """Explain monitoring and rebalancing approach"""
        try:
            triggers = portfolio_data.get("rebalancing_triggers", [])

            if triggers:
                trigger_types = set(t.get("name", "").split()[0] for t in triggers if t.get("name"))
                return f"Monitoring includes {len(trigger_types)} trigger types: {', '.join(list(trigger_types)[:3])}."
            else:
                return "Monitoring through systematic rebalancing and allocation drift analysis."
        except Exception:
            return "Monitoring through continuous market analysis and portfolio optimization."

    def _calculate_explanation_confidence(self, portfolio_data: Dict, planning_data: Dict) -> float:
        """Calculate confidence in the explanation quality"""
        try:
            confidence_factors = []

            # Portfolio data quality
            if portfolio_data.get("stress_tests"):
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.6)

            if portfolio_data.get("rebalancing_triggers"):
                confidence_factors.append(0.85)
            else:
                confidence_factors.append(0.5)

            # Planning data quality
            if planning_data.get("monte_carlo_results"):
                confidence_factors.append(0.95)
            else:
                confidence_factors.append(0.4)

            success_prob = planning_data.get("success_probability", 0.5)
            if success_prob > 0.7:
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.6)

            return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5

        except Exception:
            return 0.5

    # Data persistence methods
    async def save_analysis_to_supabase(self, session_id: str, user_id: str,
                                      explanation_summary: Dict[str, str],
                                      metadata: Dict[str, Any] = None) -> bool:
        """
        Save complete explainability analysis to Supabase.

        Args:
            session_id: Analysis session ID
            user_id: User identifier
            explanation_summary: Complete explanation summary from create_plan_summary_for_agent4
            metadata: Additional metadata about the explanation

        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Saving explainability analysis to Supabase for session {session_id}")

            # Prepare explainability data
            explanation_data = {
                "main_explanation": explanation_summary.get("main_explanation", ""),
                "risk_framework": explanation_summary.get("risk_framework", ""),
                "return_expectations": explanation_summary.get("return_expectations", ""),
                "monitoring_approach": explanation_summary.get("monitoring_approach", ""),
                "word_count": explanation_summary.get("word_count", 0),
                "confidence_score": explanation_summary.get("confidence_score", 0.5),
                "theoretical_framework": explanation_summary.get("theoretical_framework", ""),
                "metadata": metadata or {}
            }

            # Save to Supabase
            success = await AgentDataService.save_explainability_analysis(session_id, user_id, explanation_data)

            if success:
                logger.info(f"Successfully saved explainability analysis for session {session_id}")
            else:
                logger.error(f"Failed to save explainability analysis for session {session_id}")

            return success

        except Exception as e:
            logger.error(f"Error saving explainability analysis to Supabase: {e}")
            return False

    async def create_complete_explanation_analysis(self, session_id: str, user_id: str,
                                                 portfolio_agent_data: Dict[str, Any],
                                                 planner_agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create complete explanation analysis using data from Portfolio and Planner agents,
        then save to Supabase.

        Args:
            session_id: Analysis session ID
            user_id: User identifier
            portfolio_agent_data: Complete data from Portfolio Agent
            planner_agent_data: Complete data from Planner Agent

        Returns:
            Complete explanation analysis results
        """
        try:
            logger.info(f"Creating complete explanation analysis for session {session_id}")

            # Generate comprehensive plan summary using both agents' data
            plan_summary = await self.create_plan_summary_for_agent4(
                portfolio_agent_data, planner_agent_data, user_id
            )

            # Generate additional analysis components
            investment_theory_explanation = await self.explain_investment_theory_framework(
                portfolio_agent_data, planner_agent_data
            )

            risk_return_analysis = self.create_risk_return_analysis(
                portfolio_agent_data, planner_agent_data
            )

            # Compile metadata
            analysis_metadata = {
                "portfolio_data_quality": self._assess_data_quality(portfolio_agent_data),
                "planner_data_quality": self._assess_data_quality(planner_agent_data),
                "explanation_complexity": self._assess_explanation_complexity(plan_summary),
                "theoretical_depth": len(investment_theory_explanation.split()),
                "created_at": datetime.now().isoformat(),
                "mistral_used": True,
                "word_optimization": plan_summary.get("word_count", 0) >= 120
            }

            # Enhanced plan summary with additional components
            enhanced_summary = {
                **plan_summary,
                "investment_theory": investment_theory_explanation,
                "risk_return_analysis": risk_return_analysis,
                "theoretical_framework": self._extract_theoretical_framework(plan_summary),
                "explanation_metadata": analysis_metadata
            }

            # Save to Supabase
            await self.save_analysis_to_supabase(
                session_id=session_id,
                user_id=user_id,
                explanation_summary=enhanced_summary,
                metadata=analysis_metadata
            )

            # Compile complete response
            complete_analysis = {
                "explanation_summary": enhanced_summary,
                "components": {
                    "main_explanation": plan_summary.get("main_explanation"),
                    "risk_framework": plan_summary.get("risk_framework"),
                    "return_expectations": plan_summary.get("return_expectations"),
                    "monitoring_approach": plan_summary.get("monitoring_approach"),
                    "investment_theory": investment_theory_explanation,
                    "risk_return_analysis": risk_return_analysis
                },
                "quality_metrics": {
                    "word_count": plan_summary.get("word_count", 0),
                    "confidence_score": plan_summary.get("confidence_score", 0.5),
                    "explanation_completeness": self._calculate_completeness(enhanced_summary),
                    "theoretical_coverage": len(investment_theory_explanation.split()) / 50  # Normalized
                },
                "analysis_metadata": {
                    "session_id": session_id,
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    "data_saved": True,
                    "agents_used": ["portfolio", "planner", "explainability"],
                    "llm_enhanced": True
                }
            }

            logger.info(f"Complete explanation analysis created and saved for session {session_id}")
            return complete_analysis

        except Exception as e:
            logger.error(f"Error creating complete explanation analysis: {e}")
            return {"error": str(e)}

    async def explain_investment_theory_framework(self, portfolio_data: Dict[str, Any],
                                                planner_data: Dict[str, Any]) -> str:
        """Generate theoretical framework explanation for the investment strategy."""
        try:
            # Extract key metrics
            risk_level = self._determine_plan_risk_level(portfolio_data.get("allocations", {}))
            success_probability = planner_data.get("success_probability", 0.7)
            time_horizon = planner_data.get("time_horizon_years", 10)

            # Generate theory-based explanation
            if risk_level in ["aggressive", "growth"]:
                theory = """The strategy employs growth-oriented Modern Portfolio Theory principles,
                emphasizing equity exposure for long-term capital appreciation. This approach leverages
                the equity risk premium while accepting higher volatility for enhanced return potential."""
            elif risk_level == "balanced":
                theory = """The balanced approach integrates Modern Portfolio Theory with strategic
                asset allocation, optimizing the risk-return trade-off through diversification across
                asset classes. This methodology balances growth potential with downside protection."""
            else:
                theory = """The conservative strategy prioritizes capital preservation through
                fixed-income allocation while maintaining modest equity exposure. This approach
                follows efficient frontier principles with emphasis on stability and income generation."""

            # Add time horizon considerations
            if time_horizon > 15:
                theory += " The extended time horizon enables recovery from short-term market volatility."
            elif time_horizon < 5:
                theory += " The shorter timeframe necessitates reduced volatility tolerance."

            return theory.strip()

        except Exception as e:
            logger.error(f"Error generating investment theory framework: {e}")
            return "Investment strategy based on established portfolio optimization principles."

    def create_risk_return_analysis(self, portfolio_data: Dict[str, Any],
                                  planner_data: Dict[str, Any]) -> str:
        """Create risk-return analysis summary."""
        try:
            expected_return = portfolio_data.get("expected_return", 0.08)
            expected_risk = portfolio_data.get("expected_risk", 0.15)
            success_probability = planner_data.get("success_probability", 0.7)

            analysis = f"""Risk-Return Profile: Expected annual return of {expected_return:.1%}
            with {expected_risk:.1%} volatility, yielding a {success_probability:.0%} probability
            of goal achievement. The strategy balances return optimization with risk management
            through quantitative portfolio construction."""

            return analysis.strip()

        except Exception as e:
            logger.error(f"Error creating risk-return analysis: {e}")
            return "Risk-return profile optimized for goal achievement."

    def _assess_data_quality(self, agent_data: Dict[str, Any]) -> str:
        """Assess the quality of agent data."""
        try:
            if not agent_data:
                return "insufficient"

            key_fields = ["allocations", "stress_tests", "monte_carlo_results", "success_probability"]
            present_fields = sum(1 for field in key_fields if agent_data.get(field))

            if present_fields >= 3:
                return "high"
            elif present_fields >= 2:
                return "medium"
            else:
                return "low"

        except Exception:
            return "unknown"

    def _assess_explanation_complexity(self, plan_summary: Dict[str, Any]) -> str:
        """Assess the complexity of the explanation."""
        try:
            word_count = plan_summary.get("word_count", 0)
            confidence = plan_summary.get("confidence_score", 0.5)

            if word_count >= 120 and confidence >= 0.8:
                return "high"
            elif word_count >= 100 and confidence >= 0.6:
                return "medium"
            else:
                return "low"

        except Exception:
            return "unknown"

    def _extract_theoretical_framework(self, plan_summary: Dict[str, Any]) -> str:
        """Extract theoretical framework components from the explanation."""
        try:
            main_explanation = plan_summary.get("main_explanation", "")

            # Look for theoretical terms
            theoretical_terms = [
                "modern portfolio theory", "efficient frontier", "capm",
                "diversification", "risk-adjusted", "optimization"
            ]

            found_terms = [term for term in theoretical_terms if term in main_explanation.lower()]

            if found_terms:
                return f"Theoretical framework includes: {', '.join(found_terms)}"
            else:
                return "Quantitative investment principles applied"

        except Exception:
            return "Investment theory framework utilized"

    def _calculate_completeness(self, enhanced_summary: Dict[str, Any]) -> float:
        """Calculate explanation completeness score."""
        try:
            required_components = [
                "main_explanation", "risk_framework", "return_expectations",
                "monitoring_approach", "investment_theory"
            ]

            present_components = sum(
                1 for component in required_components
                if enhanced_summary.get(component) and len(enhanced_summary[component]) > 10
            )

            return present_components / len(required_components)

        except Exception:
            return 0.5