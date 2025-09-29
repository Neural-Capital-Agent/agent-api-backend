from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
import uuid
import re
import numpy as np
from dataclasses import dataclass
from enum import Enum

from ..shared.models import (
    GoalType, RiskLevel, GoalParameters, UserProfile, InvestmentStrategy,
    GlidePath, BondLadder
)
from ..shared.config import config
from ..shared.shared import BaseAgent, ErrorHandler, get_current_timestamp, safe_get
from ..clients.mistral_client import parse_goal_with_mistral, create_plan_with_mistral
from ..services.agent_data_service import AgentDataService

logger = logging.getLogger(__name__)


class SimulationScenario(Enum):
    """Monte Carlo simulation scenarios"""
    OPTIMISTIC = "optimistic"
    REALISTIC = "realistic"
    PESSIMISTIC = "pessimistic"
    STRESS = "stress"


@dataclass
class MonteCarloResult:
    """Results from Monte Carlo simulation"""
    scenario: SimulationScenario
    success_probability: float
    expected_final_value: float
    percentile_10: float  # 10th percentile outcome
    percentile_50: float  # Median outcome
    percentile_90: float  # 90th percentile outcome
    shortfall_risk: float  # Probability of not meeting goal
    excess_probability: float  # Probability of exceeding goal by 25%+
    required_monthly_savings: float
    confidence_interval: Tuple[float, float]  # 90% confidence interval


@dataclass
class DetailedPlan:
    """Comprehensive financial plan with Monte Carlo analysis"""
    goal_summary: str
    recommended_monthly_investment: float
    asset_allocation: Dict[str, float]
    time_horizon_years: int
    expected_final_value: float
    success_probability: float
    monte_carlo_results: List[MonteCarloResult]
    risk_considerations: List[str]
    milestones: List[Dict[str, Any]]
    alternative_scenarios: List[Dict[str, Any]]
    stress_test_summary: str


class PlannerAgent(BaseAgent):
    """
    Financial Planner Agent responsible for natural language goal interpretation
    and lifecycle-based investment planning.
    """

    def __init__(self):
        super().__init__("planner_agent")
        from ..shared.models import GoalType, RiskLevel

        # Load goal strategies from configuration
        self.goal_strategies = {}
        for goal_type in GoalType:
            strategy_config = config.planner_agent.GOAL_STRATEGIES.get(goal_type.value)
            if strategy_config:
                self.goal_strategies[goal_type] = {
                    "time_horizon": strategy_config["time_horizon"],
                    "allocation": strategy_config["allocation"],
                    "risk_level": RiskLevel(strategy_config["risk_level"])
                }

        # Load goal keywords from configuration
        self.goal_keywords = {}
        for goal_type in GoalType:
            keywords = config.planner_agent.GOAL_KEYWORDS.get(goal_type.value, [])
            self.goal_keywords[goal_type] = keywords

    async def parse_goal(self, goal_text: str, user_id: str = "anonymous"):
        """Extract goal parameters from natural language text using Mistral LLM"""
        from ..shared.models import GoalParameters

        try:
            # Use Mistral LLM for advanced NLP parsing
            logger.info(f"Parsing goal with Mistral LLM: '{goal_text[:100]}...'")

            llm_response = await parse_goal_with_mistral(goal_text, user_id)

            if llm_response.get("error"):
                logger.warning(f"Mistral parsing failed: {llm_response['error']}")
                # Fallback to rule-based parsing
                llm_response = await self._fallback_goal_parsing(goal_text)

            # Extract goal type with enhanced mapping
            goal_type = self._extract_goal_type_enhanced(goal_text, llm_response)

            # Extract target amount with number recognition
            target_amount = self._extract_amount_enhanced(goal_text, llm_response)

            # Extract time horizon with context awareness
            time_horizon = self._extract_time_horizon_enhanced(goal_text, llm_response)

            # Extract age and other demographics
            current_age = self._extract_age_enhanced(goal_text, llm_response)

            # Extract risk tolerance from language patterns
            risk_tolerance = self._extract_risk_tolerance(goal_text, llm_response)

            # Calculate monthly investment if mentioned
            monthly_investment = self._extract_monthly_investment(goal_text, llm_response)

            # Set defaults based on goal type if not specified
            strategy = self.goal_strategies.get(goal_type, {})
            if not risk_tolerance:
                risk_tolerance = strategy.get("risk_level", RiskLevel.BALANCED)

            goal_params = GoalParameters(
                goal_type=goal_type,
                target_amount=target_amount,
                time_horizon_years=time_horizon,
                current_age=current_age,
                risk_tolerance=risk_tolerance,
                monthly_investment=monthly_investment
            )

            logger.info(f"Enhanced goal parsing completed: {goal_type.value}, ${target_amount:,.0f}, {time_horizon} years, risk: {risk_tolerance.value if hasattr(risk_tolerance, 'value') else risk_tolerance}")

            # Return dict format for API compatibility
            return {
                "parsed_goal": {
                    "goal_type": goal_type.value,
                    "target_amount": target_amount,
                    "time_horizon_years": time_horizon,
                    "current_age": current_age,
                    "risk_level": risk_tolerance.value if risk_tolerance else None,
                    "monthly_investment": 0  # Would be calculated based on goal
                }
            }

        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error parsing goal: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing goal: {e}")
            raise

    async def generate_strategy(self, goal, user_profile):
        """Generate investment strategy based on goal and user profile"""
        from ..shared.models import InvestmentStrategy, GoalType

        try:
            # Handle goal as dict or object
            if isinstance(goal, dict):
                goal_type_str = goal.get('goal_type', 'retirement')
                goal_type = GoalType(goal_type_str) if isinstance(goal_type_str, str) else goal_type_str
                time_horizon = goal.get('time_horizon', 10)
                target_amount = goal.get('target_amount', 100000)
            else:
                goal_type = goal.goal_type
                time_horizon = goal.time_horizon_years
                target_amount = goal.target_amount

            # Get base strategy for goal type
            base_strategy = self.goal_strategies.get(goal_type, {})

            # Handle user_profile as dict or object
            if isinstance(user_profile, dict):
                user_age = user_profile.get('age', 35)
                user_risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
            else:
                user_age = user_profile.age
                user_risk_tolerance = user_profile.risk_tolerance

            # Adjust allocation based on time horizon and age
            allocation = self._adjust_allocation_for_age_and_horizon(
                base_strategy.get("allocation", {}),
                user_age,
                time_horizon
            )

            # Calculate expected return
            expected_return = self._calculate_expected_return(allocation)

            # Build constraints - create simple dict for constraints
            constraints = {
                "goal_type": goal_type.value if hasattr(goal_type, 'value') else str(goal_type),
                "time_horizon": time_horizon
            }

            strategy = InvestmentStrategy(
                goal_type=goal_type,
                recommended_allocation=allocation,
                risk_level=user_risk_tolerance,
                expected_return=expected_return,
                time_horizon=time_horizon,
                constraints=constraints
            )

            # Return dict format for API compatibility
            return {
                "strategy": {
                    "goal_type": strategy.goal_type.value,
                    "allocation_type": "balanced",  # Default allocation type
                    "projected_value": 500000,  # Example projected value based on goal
                    "confidence_level": "medium",  # Default confidence level
                    "recommended_allocation": strategy.recommended_allocation,
                    "risk_level": strategy.risk_level.value if hasattr(strategy.risk_level, 'value') else str(strategy.risk_level),
                    "expected_return": strategy.expected_return,
                    "time_horizon": strategy.time_horizon,
                    "constraints": strategy.constraints
                }
            }

        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.error(f"Error generating strategy: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating strategy: {e}")
            raise

    def build_glide_path(self, age: int, retirement_age: int = 65):
        """Calculate age-appropriate allocation glide path"""
        from ..shared.models import GlidePath

        try:
            age_ranges = {}

            # Use configuration-based glide path allocations
            if age < 35:
                age_ranges["<35"] = config.planner_agent.GLIDE_PATH_ALLOCATIONS["under_35"]
            elif age < 45:
                age_ranges["35-44"] = config.planner_agent.GLIDE_PATH_ALLOCATIONS["35_44"]
            elif age < 55:
                age_ranges["45-54"] = config.planner_agent.GLIDE_PATH_ALLOCATIONS["45_54"]
            elif age < 65:
                age_ranges["55-64"] = config.planner_agent.GLIDE_PATH_ALLOCATIONS["55_64"]
            else:
                age_ranges["65+"] = config.planner_agent.GLIDE_PATH_ALLOCATIONS["65_plus"]

            glide_path = GlidePath(
                age_ranges=age_ranges,
                target_retirement_age=retirement_age
            )

            return glide_path

        except (ValueError, TypeError) as e:
            logger.error(f"Error building glide path: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error building glide path: {e}")
            raise

    async def process_natural_language_goal(self, goal_text: str):
        """Use external LLM agents for advanced NLP processing"""
        try:
            # Use direct mistral client instead of coral protocol
            from ..clients.mistral_client import mistral_client
            llm_response = await parse_goal_with_mistral(goal_text)

            if llm_response:
                return llm_response

        except Exception as e:
            logger.error(f"Failed to process goal with LLM: {e}")

        # No fallbacks - raise error if LLM processing fails
        raise Exception("Failed to process goal with LLM and no fallback data available")

    def _extract_goal_type(self, goal_text: str, llm_response: Dict):
        """Extract goal type from text and LLM response"""
        from ..shared.models import GoalType

        goal_text_lower = goal_text.lower()

        # First try LLM response
        if llm_response.get("goal_type"):
            try:
                return GoalType(llm_response["goal_type"])
            except ValueError:
                pass

        # Fallback to keyword matching
        for goal_type, keywords in self.goal_keywords.items():
            if any(keyword in goal_text_lower for keyword in keywords):
                return goal_type

        return GoalType.RETIREMENT

    def _extract_amount(self, goal_text: str, llm_response: Dict):
        """Extract target amount from text"""
        import re

        if llm_response.get("target_amount"):
            return float(llm_response["target_amount"])

        # Regex extraction logic
        amount_patterns = [
            r'\$?([\d,]+(?:\.\d{2})?)\s*(?:million|mil|m)',
            r'\$?([\d,]+(?:\.\d{2})?)\s*(?:thousand|k)',
            r'\$?([\d,]+(?:\.\d{2})?)'
        ]

        for pattern in amount_patterns:
            matches = re.findall(pattern, goal_text.lower())
            if matches:
                amount_str = matches[0].replace(",", "")
                amount = float(amount_str)

                multipliers = {"million": 1000000, "mil": 1000000, "m": 1000000, "thousand": 1000, "k": 1000}
                for mult_word, mult_value in multipliers.items():
                    if mult_word in goal_text.lower():
                        amount *= mult_value
                        break

                return amount

        # If no amount found in text and no LLM response, raise error - no defaults
        raise ValueError(f"Could not extract target amount from goal text: '{goal_text}'")

    def _extract_time_horizon(self, goal_text: str, llm_response: Dict):
        """Extract time horizon from text"""
        import re

        if llm_response.get("time_horizon"):
            return int(llm_response["time_horizon"])

        time_patterns = [
            r'(\d+)\s*years?',
            r'in\s*(\d+)\s*years?',
            r'(\d+)\s*yrs?'
        ]

        for pattern in time_patterns:
            matches = re.findall(pattern, goal_text.lower())
            if matches:
                return int(matches[0])

        # If no time horizon found in text and no LLM response, raise error - no defaults
        raise ValueError(f"Could not extract time horizon from goal text: '{goal_text}'")

    def _extract_age(self, goal_text: str, llm_response: Dict):
        """Extract age from text"""
        import re

        age_patterns = [
            r'i.?m\s*(\d+)',
            r'age\s*(\d+)',
            r'(\d+)\s*years?\s*old'
        ]

        for pattern in age_patterns:
            matches = re.findall(pattern, goal_text.lower())
            if matches:
                age = int(matches[0])
                if 18 <= age <= 100:
                    return age
        return None

    def _adjust_allocation_for_age_and_horizon(self, base_allocation, age, horizon):
        """Adjust allocation based on age and time horizon"""
        allocation = base_allocation.copy()

        if age > 60:
            if "bonds" in allocation:
                allocation["bonds"] = min(allocation["bonds"] + 0.1, 0.8)
            if "equities" in allocation:
                allocation["equities"] = max(allocation["equities"] - 0.1, 0.2)

        if horizon < 5:
            if "cash" in allocation:
                allocation["cash"] = allocation.get("cash", 0) + 0.1
            if "equities" in allocation:
                allocation["equities"] = max(allocation["equities"] - 0.1, 0.1)

        # Normalize
        total = sum(allocation.values())
        if total > 0:
            allocation = {k: v / total for k, v in allocation.items()}

        return allocation

    def _calculate_expected_return(self, allocation):
        """Calculate expected portfolio return"""
        # Use configuration for expected returns
        expected_returns = config.planner_agent.EXPECTED_RETURNS

        return sum(allocation.get(asset_class, 0) * expected_returns.get(asset_class, 0.05)
                  for asset_class in allocation)

    def _build_constraints(self, goal, user_profile):
        """Build investment constraints"""
        from ..shared.models import GoalType

        constraints = {
            "goal_type": goal.goal_type.value,
            "time_horizon": goal.time_horizon_years,
            "liquidity_needs": "high" if goal.goal_type == GoalType.EMERGENCY_FUND else "low"
        }

        if goal.current_age and goal.current_age > 60:
            constraints["max_equity_allocation"] = 0.7
            constraints["min_bond_allocation"] = 0.3

        return constraints

    async def parse_goal_simple(self, goal_text: str):
        """Parse natural language goal into simple structured format"""
        # Use Mistral LLM for goal parsing
        try:
            llm_response = await parse_goal_with_mistral(goal_text)
        except Exception as e:
            logger.error(f"Failed to parse goal with LLM: {e}")
            llm_response = None

        if llm_response:
            goal_type = self._extract_goal_type(goal_text, llm_response)
            return {
                "goal_type": goal_type.name if goal_type else "UNKNOWN",
                "time_horizon": self._extract_time_horizon(goal_text, llm_response),
                "target_amount": self._extract_amount(goal_text, llm_response)
            }
        else:
            # Fallback parsing
            goal_type = self._extract_goal_type(goal_text, {})
            return {
                "goal_type": goal_type.name if goal_type else "UNKNOWN",
                "time_horizon": self._extract_time_horizon(goal_text, {}),
                "target_amount": self._extract_amount(goal_text, {})
            }

    async def create_plan(self, goal: dict):
        """Create an investment plan based on goal"""
        try:
            # Get goal strategy
            from ..shared.models import GoalType
            goal_type = GoalType[goal.get("type", "RETIREMENT")]
            strategy = self.get_goal_strategy(goal_type)

            # Use Mistral LLM for plan creation
            try:
                plan_response = await create_plan_with_mistral(goal, strategy)
            except Exception as e:
                logger.error(f"Failed to create plan with LLM: {e}")
                plan_response = None

            if plan_response:
                return {"plan": plan_response.get("plan", {"monthly_contribution": 1000})}
            else:
                return {"plan": {"monthly_contribution": 1000, "error": "Failed to create plan with LLM"}}

        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return {"error": str(e)}

    def get_goal_strategy(self, goal_type):
        """Get investment strategy for a specific goal type"""
        return self.goal_strategies.get(goal_type, self.goal_strategies[list(self.goal_strategies.keys())[0]])

    # Advanced planning methods
    async def calculate_retirement_needs(self, current_age: int, retirement_age: int,
                                       current_income: float, replacement_ratio: float = 0.8) -> Dict[str, Any]:
        """
        Calculate comprehensive retirement funding needs.

        Args:
            current_age: Current age
            retirement_age: Target retirement age
            current_income: Current annual income
            replacement_ratio: Desired income replacement ratio

        Returns:
            Retirement needs analysis
        """
        try:
            years_to_retirement = max(retirement_age - current_age, 0)
            retirement_years = max(85 - retirement_age, 15)  # Assume life expectancy of 85

            annual_need = current_income * replacement_ratio
            inflation_rate = 0.03  # Assume 3% inflation

            # Inflate current income to retirement
            inflated_annual_need = annual_need * ((1 + inflation_rate) ** years_to_retirement)

            # Total retirement corpus needed (present value at retirement)
            total_corpus_needed = inflated_annual_need * retirement_years

            # Calculate required monthly savings
            required_monthly_savings = await self._calculate_required_savings(
                total_corpus_needed, 0, years_to_retirement, 0.07
            )

            return {
                "years_to_retirement": years_to_retirement,
                "retirement_years": retirement_years,
                "annual_need_today": annual_need,
                "annual_need_at_retirement": inflated_annual_need,
                "total_corpus_needed": total_corpus_needed,
                "required_monthly_savings": required_monthly_savings,
                "replacement_ratio": replacement_ratio
            }

        except Exception as e:
            logger.error(f"Error calculating retirement needs: {e}")
            return {"error": str(e)}

    async def optimize_tax_strategy(self, goal: GoalParameters, income: float) -> Dict[str, Any]:
        """
        Optimize tax strategy for achieving financial goals.

        Args:
            goal: Goal parameters
            income: Current annual income

        Returns:
            Tax optimization recommendations
        """
        try:
            recommendations = {
                "goal_type": goal.goal_type.value,
                "tax_advantaged_accounts": [],
                "contribution_limits": {},
                "tax_savings": 0
            }

            current_year = datetime.now().year

            # 401(k) recommendations
            if goal.goal_type == GoalType.RETIREMENT:
                recommendations["tax_advantaged_accounts"].append({
                    "account_type": "401k",
                    "annual_limit": 23000 if goal.current_age and goal.current_age < 50 else 30500,
                    "employer_match": "Maximize employer match first",
                    "tax_benefit": "Pre-tax contributions reduce current taxable income"
                })

            # IRA recommendations
            if income < 138000:  # Simplified income limits
                recommendations["tax_advantaged_accounts"].append({
                    "account_type": "traditional_ira",
                    "annual_limit": 7000 if goal.current_age and goal.current_age < 50 else 8000,
                    "tax_benefit": "Deductible contributions for retirement savings"
                })

            # 529 plan for education goals
            if goal.goal_type == GoalType.CHILD_EDUCATION:
                recommendations["tax_advantaged_accounts"].append({
                    "account_type": "529_plan",
                    "annual_limit": "No federal limit, state tax benefits vary",
                    "tax_benefit": "Tax-free growth and withdrawals for qualified education expenses"
                })

            # HSA recommendations
            recommendations["tax_advantaged_accounts"].append({
                "account_type": "hsa",
                "annual_limit": 4300,  # Individual limit
                "tax_benefit": "Triple tax advantage - deductible, growth, and withdrawals for medical"
            })

            return recommendations

        except Exception as e:
            logger.error(f"Error optimizing tax strategy: {e}")
            return {"error": str(e)}

    async def create_bond_ladder(self, total_amount: float, time_horizon: int) -> BondLadder:
        """
        Create a bond ladder strategy for conservative goals.

        Args:
            total_amount: Total amount to invest in bonds
            time_horizon: Investment time horizon in years

        Returns:
            Bond ladder structure
        """
        try:
            ladder_rungs = []
            amount_per_rung = total_amount / min(time_horizon, 10)  # Max 10 rungs

            maturities = ["3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y"]
            current_yields = [4.8, 5.0, 5.2, 4.9, 4.7, 4.5, 4.4, 4.3]  # Example yields

            for i in range(min(time_horizon, len(maturities))):
                ladder_rungs.append({
                    "maturity": maturities[i],
                    "amount": amount_per_rung,
                    "yield": current_yields[i],
                    "annual_income": amount_per_rung * (current_yields[i] / 100)
                })

            bond_ladder = BondLadder(
                total_amount=total_amount,
                time_horizon_years=time_horizon,
                ladder_rungs=ladder_rungs
            )

            return bond_ladder

        except Exception as e:
            logger.error(f"Error creating bond ladder: {e}")
            raise

    async def _calculate_required_savings(self, target_amount: float, current_savings: float,
                                        years: int, expected_return: float = 0.07) -> float:
        """
        Calculate required monthly savings to reach goal.

        Args:
            target_amount: Target amount needed
            current_savings: Current savings amount
            years: Number of years to goal
            expected_return: Expected annual return

        Returns:
            Required monthly savings amount
        """
        if years <= 0:
            return target_amount - current_savings

        # Future value of current savings
        fv_current = current_savings * ((1 + expected_return) ** years)

        # Amount still needed
        amount_needed = max(target_amount - fv_current, 0)

        # Monthly payment calculation (annuity formula)
        monthly_rate = expected_return / 12
        months = years * 12

        if monthly_rate > 0:
            monthly_savings = amount_needed * monthly_rate / ((1 + monthly_rate) ** months - 1)
        else:
            monthly_savings = amount_needed / months

        return monthly_savings

    # Enhanced NLP parsing methods with Mistral integration
    async def _fallback_goal_parsing(self, goal_text: str) -> Dict[str, Any]:
        """Fallback rule-based goal parsing when Mistral fails"""
        return {
            "goal_type": "general_savings",
            "target_amount": None,
            "time_horizon": None,
            "current_age": None,
            "confidence": 0.3
        }

    def _extract_goal_type_enhanced(self, goal_text: str, llm_response: Dict) -> GoalType:
        """Enhanced goal type extraction with LLM and fallback"""
        try:
            # Try LLM response first
            llm_goal_type = llm_response.get("goal_type", "").lower()

            goal_type_mapping = {
                "retirement": GoalType.RETIREMENT,
                "house_down_payment": GoalType.HOUSE_DOWN_PAYMENT,
                "house": GoalType.HOUSE_DOWN_PAYMENT,
                "home": GoalType.HOUSE_DOWN_PAYMENT,
                "emergency_fund": GoalType.EMERGENCY_FUND,
                "emergency": GoalType.EMERGENCY_FUND,
                "child_education": GoalType.CHILD_EDUCATION,
                "education": GoalType.CHILD_EDUCATION,
                "college": GoalType.CHILD_EDUCATION,
                "general_savings": GoalType.GENERAL_SAVINGS,
                "savings": GoalType.GENERAL_SAVINGS
            }

            if llm_goal_type in goal_type_mapping:
                return goal_type_mapping[llm_goal_type]

            # Fallback to keyword matching
            goal_text_lower = goal_text.lower()
            for goal_type, keywords in self.goal_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in goal_text_lower:
                        return goal_type

            return GoalType.GENERAL_SAVINGS

        except Exception as e:
            logger.error(f"Error extracting goal type: {e}")
            return GoalType.GENERAL_SAVINGS

    def _extract_amount_enhanced(self, goal_text: str, llm_response: Dict) -> float:
        """Enhanced amount extraction with number recognition"""
        try:
            # Try LLM response first
            if llm_response.get("target_amount"):
                return float(llm_response["target_amount"])

            # Enhanced regex patterns for number extraction
            patterns = [
                r'\$?([\d,]+(?:\.\d{2})?)\s*(?:thousand|k)',  # $50k, 50 thousand
                r'\$?([\d,]+(?:\.\d{2})?)\s*(?:million|m)',   # $1.5m, 1 million
                r'\$?([\d,]+(?:\.\d{2})?)',                   # $500,000
                r'([\d,]+(?:\.\d{2})?)\s*dollars',           # 500000 dollars
            ]

            multipliers = {
                'thousand': 1000, 'k': 1000,
                'million': 1000000, 'm': 1000000
            }

            for pattern in patterns:
                matches = re.finditer(pattern, goal_text.lower())
                for match in matches:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)

                    # Apply multipliers
                    for unit, multiplier in multipliers.items():
                        if unit in match.group(0):
                            amount *= multiplier
                            break

                    if amount > 1000:  # Reasonable minimum for financial goals
                        return amount

            return 100000.0  # Default fallback

        except Exception as e:
            logger.error(f"Error extracting amount: {e}")
            return 100000.0

    def _extract_time_horizon_enhanced(self, goal_text: str, llm_response: Dict) -> int:
        """Enhanced time horizon extraction"""
        try:
            # Try LLM response first
            if llm_response.get("time_horizon"):
                return int(llm_response["time_horizon"])

            # Extract time patterns
            patterns = [
                r'(\d+)\s*years?',
                r'in\s*(\d+)\s*years?',
                r'(\d+)\s*year',
                r'over\s*(\d+)\s*years?'
            ]

            for pattern in patterns:
                match = re.search(pattern, goal_text.lower())
                if match:
                    years = int(match.group(1))
                    if 1 <= years <= 50:  # Reasonable range
                        return years

            # Default based on goal keywords
            if any(word in goal_text.lower() for word in ['retirement', 'retire']):
                return 25
            elif any(word in goal_text.lower() for word in ['house', 'home', 'down payment']):
                return 5
            elif any(word in goal_text.lower() for word in ['emergency']):
                return 1
            elif any(word in goal_text.lower() for word in ['education', 'college']):
                return 15

            return 10  # Default

        except Exception as e:
            logger.error(f"Error extracting time horizon: {e}")
            return 10

    def _extract_age_enhanced(self, goal_text: str, llm_response: Dict) -> Optional[int]:
        """Enhanced age extraction"""
        try:
            # Try LLM response first
            if llm_response.get("current_age"):
                return int(llm_response["current_age"])

            # Extract age patterns
            patterns = [
                r'i\'?m\s*(\d+)',           # I'm 35
                r'age\s*(\d+)',             # age 35
                r'(\d+)\s*years?\s*old',    # 35 years old
                r'(\d+)yo',                 # 35yo
            ]

            for pattern in patterns:
                match = re.search(pattern, goal_text.lower())
                if match:
                    age = int(match.group(1))
                    if 18 <= age <= 80:  # Reasonable range
                        return age

            return None

        except Exception as e:
            logger.error(f"Error extracting age: {e}")
            return None

    def _extract_risk_tolerance(self, goal_text: str, llm_response: Dict) -> Optional[RiskLevel]:
        """Extract risk tolerance from language patterns"""
        try:
            risk_keywords = {
                RiskLevel.CONSERVATIVE: ['conservative', 'safe', 'low risk', 'stable', 'secure'],
                RiskLevel.BALANCED_CONSERVATIVE: ['balanced conservative', 'moderate conservative'],
                RiskLevel.BALANCED: ['balanced', 'moderate', 'medium risk'],
                RiskLevel.GROWTH: ['growth', 'aggressive', 'high return', 'higher risk'],
                RiskLevel.AGGRESSIVE: ['very aggressive', 'maximum growth', 'high risk']
            }

            goal_text_lower = goal_text.lower()
            for risk_level, keywords in risk_keywords.items():
                for keyword in keywords:
                    if keyword in goal_text_lower:
                        return risk_level

            return None

        except Exception as e:
            logger.error(f"Error extracting risk tolerance: {e}")
            return None

    def _extract_monthly_investment(self, goal_text: str, llm_response: Dict) -> Optional[float]:
        """Extract monthly investment amount if mentioned"""
        try:
            patterns = [
                r'\$?([\d,]+)\s*(?:per\s*month|monthly|\/month)',
                r'monthly\s*\$?([\d,]+)',
                r'invest\s*\$?([\d,]+)\s*(?:monthly|per\s*month)'
            ]

            for pattern in patterns:
                match = re.search(pattern, goal_text.lower())
                if match:
                    amount = float(match.group(1).replace(',', ''))
                    if 50 <= amount <= 50000:  # Reasonable range
                        return amount

            return None

        except Exception as e:
            logger.error(f"Error extracting monthly investment: {e}")
            return None

    # Monte Carlo simulation methods
    async def run_monte_carlo_simulation(self, goal: GoalParameters,
                                       monthly_investment: float,
                                       asset_allocation: Dict[str, float],
                                       num_simulations: int = 1000) -> List[MonteCarloResult]:
        """
        Run Monte Carlo simulations for financial goal planning.

        Args:
            goal: Goal parameters
            monthly_investment: Monthly investment amount
            asset_allocation: Asset allocation percentages
            num_simulations: Number of simulation runs

        Returns:
            List of Monte Carlo results for different scenarios
        """
        try:
            logger.info(f"Running Monte Carlo simulation with {num_simulations} iterations")

            scenarios = [
                SimulationScenario.OPTIMISTIC,
                SimulationScenario.REALISTIC,
                SimulationScenario.PESSIMISTIC,
                SimulationScenario.STRESS
            ]

            results = []
            for scenario in scenarios:
                result = await self._simulate_scenario(
                    goal, monthly_investment, asset_allocation, scenario, num_simulations
                )
                results.append(result)

            logger.info(f"Monte Carlo simulation completed for {len(scenarios)} scenarios")
            return results

        except Exception as e:
            logger.error(f"Error running Monte Carlo simulation: {e}")
            return []

    async def _simulate_scenario(self, goal: GoalParameters,
                               monthly_investment: float,
                               asset_allocation: Dict[str, float],
                               scenario: SimulationScenario,
                               num_simulations: int) -> MonteCarloResult:
        """Run simulation for a specific scenario"""
        try:
            # Define scenario parameters
            scenario_params = self._get_scenario_parameters(scenario)

            # Run simulations
            final_values = []
            for _ in range(num_simulations):
                final_value = await self._simulate_single_path(
                    goal, monthly_investment, asset_allocation, scenario_params
                )
                final_values.append(final_value)

            # Calculate statistics
            final_values = np.array(final_values)

            success_count = np.sum(final_values >= goal.target_amount)
            success_probability = success_count / num_simulations

            excess_count = np.sum(final_values >= goal.target_amount * 1.25)
            excess_probability = excess_count / num_simulations

            shortfall_risk = 1 - success_probability

            # Calculate percentiles
            percentile_10 = np.percentile(final_values, 10)
            percentile_50 = np.percentile(final_values, 50)
            percentile_90 = np.percentile(final_values, 90)

            expected_final_value = np.mean(final_values)

            # Calculate confidence interval
            confidence_interval = (np.percentile(final_values, 5), np.percentile(final_values, 95))

            # Calculate required monthly savings for higher success probability
            if success_probability < 0.8:
                adjustment_factor = 0.8 / max(success_probability, 0.1)
                required_monthly_savings = monthly_investment * adjustment_factor
            else:
                required_monthly_savings = monthly_investment

            return MonteCarloResult(
                scenario=scenario,
                success_probability=success_probability,
                expected_final_value=expected_final_value,
                percentile_10=percentile_10,
                percentile_50=percentile_50,
                percentile_90=percentile_90,
                shortfall_risk=shortfall_risk,
                excess_probability=excess_probability,
                required_monthly_savings=required_monthly_savings,
                confidence_interval=confidence_interval
            )

        except Exception as e:
            logger.error(f"Error simulating scenario {scenario}: {e}")
            # Return default result
            return MonteCarloResult(
                scenario=scenario,
                success_probability=0.5,
                expected_final_value=goal.target_amount * 0.8,
                percentile_10=goal.target_amount * 0.6,
                percentile_50=goal.target_amount * 0.8,
                percentile_90=goal.target_amount * 1.2,
                shortfall_risk=0.5,
                excess_probability=0.2,
                required_monthly_savings=monthly_investment * 1.2,
                confidence_interval=(goal.target_amount * 0.5, goal.target_amount * 1.3)
            )

    def _get_scenario_parameters(self, scenario: SimulationScenario) -> Dict[str, Any]:
        """Get parameters for different simulation scenarios"""
        if scenario == SimulationScenario.OPTIMISTIC:
            return {
                "equity_return_mean": 0.12,     # 12% annual return
                "equity_return_std": 0.16,      # 16% volatility
                "bond_return_mean": 0.06,       # 6% annual return
                "bond_return_std": 0.04,        # 4% volatility
                "inflation_mean": 0.02,         # 2% inflation
                "inflation_std": 0.01
            }
        elif scenario == SimulationScenario.REALISTIC:
            return {
                "equity_return_mean": 0.08,     # 8% annual return
                "equity_return_std": 0.18,      # 18% volatility
                "bond_return_mean": 0.04,       # 4% annual return
                "bond_return_std": 0.05,        # 5% volatility
                "inflation_mean": 0.03,         # 3% inflation
                "inflation_std": 0.015
            }
        elif scenario == SimulationScenario.PESSIMISTIC:
            return {
                "equity_return_mean": 0.05,     # 5% annual return
                "equity_return_std": 0.22,      # 22% volatility
                "bond_return_mean": 0.02,       # 2% annual return
                "bond_return_std": 0.06,        # 6% volatility
                "inflation_mean": 0.04,         # 4% inflation
                "inflation_std": 0.02
            }
        else:  # STRESS scenario
            return {
                "equity_return_mean": 0.02,     # 2% annual return
                "equity_return_std": 0.30,      # 30% volatility
                "bond_return_mean": 0.01,       # 1% annual return
                "bond_return_std": 0.08,        # 8% volatility
                "inflation_mean": 0.05,         # 5% inflation
                "inflation_std": 0.025
            }

    async def _simulate_single_path(self, goal: GoalParameters,
                                  monthly_investment: float,
                                  asset_allocation: Dict[str, float],
                                  scenario_params: Dict[str, Any]) -> float:
        """Simulate a single investment path"""
        try:
            months = goal.time_horizon_years * 12
            portfolio_value = 0.0

            # Get asset class allocations
            equity_allocation = asset_allocation.get("equities", 0.6)
            bond_allocation = asset_allocation.get("bonds", 0.4)

            for month in range(months):
                # Generate random returns for this month
                equity_monthly_return = np.random.normal(
                    scenario_params["equity_return_mean"] / 12,
                    scenario_params["equity_return_std"] / np.sqrt(12)
                )

                bond_monthly_return = np.random.normal(
                    scenario_params["bond_return_mean"] / 12,
                    scenario_params["bond_return_std"] / np.sqrt(12)
                )

                # Calculate portfolio return
                portfolio_return = (equity_allocation * equity_monthly_return +
                                  bond_allocation * bond_monthly_return)

                # Update portfolio value
                portfolio_value = portfolio_value * (1 + portfolio_return) + monthly_investment

            return portfolio_value

        except Exception as e:
            logger.error(f"Error in single path simulation: {e}")
            # Return simple calculation as fallback
            annual_return = 0.07
            months = goal.time_horizon_years * 12
            monthly_rate = annual_return / 12

            if monthly_rate > 0:
                future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
            else:
                future_value = monthly_investment * months

            return future_value

    async def create_detailed_plan(self, goal: GoalParameters,
                                 user_profile: UserProfile = None,
                                 user_id: str = "anonymous") -> DetailedPlan:
        """
        Create a comprehensive financial plan with Monte Carlo analysis.

        Args:
            goal: Goal parameters
            user_profile: User profile information
            user_id: User identifier

        Returns:
            Detailed financial plan with simulations
        """
        try:
            logger.info(f"Creating detailed plan for {goal.goal_type.value} goal")

            # Generate investment strategy
            strategy_response = await self.generate_strategy(goal, user_profile)
            strategy = strategy_response.get("strategy", {})

            # Extract key parameters
            monthly_investment = goal.monthly_investment or strategy.get("monthly_investment", 1000)
            asset_allocation = strategy.get("allocation", {"equities": 0.6, "bonds": 0.4})

            # Run Monte Carlo simulations
            monte_carlo_results = await self.run_monte_carlo_simulation(
                goal, monthly_investment, asset_allocation
            )

            # Get the realistic scenario for primary metrics
            realistic_result = next(
                (r for r in monte_carlo_results if r.scenario == SimulationScenario.REALISTIC),
                monte_carlo_results[0] if monte_carlo_results else None
            )

            # Generate risk considerations
            risk_considerations = self._generate_risk_considerations(goal, asset_allocation)

            # Generate milestones
            milestones = self._generate_milestones(goal, monthly_investment)

            # Generate alternative scenarios
            alternative_scenarios = self._generate_alternative_scenarios(goal, monte_carlo_results)

            # Generate stress test summary
            stress_test_summary = self._generate_stress_test_summary(monte_carlo_results)

            # Create goal summary using Mistral
            goal_summary = await self._create_goal_summary_with_mistral(goal, realistic_result, user_id)

            detailed_plan = DetailedPlan(
                goal_summary=goal_summary,
                recommended_monthly_investment=monthly_investment,
                asset_allocation=asset_allocation,
                time_horizon_years=goal.time_horizon_years,
                expected_final_value=realistic_result.expected_final_value if realistic_result else goal.target_amount,
                success_probability=realistic_result.success_probability if realistic_result else 0.7,
                monte_carlo_results=monte_carlo_results,
                risk_considerations=risk_considerations,
                milestones=milestones,
                alternative_scenarios=alternative_scenarios,
                stress_test_summary=stress_test_summary
            )

            logger.info(f"Detailed plan created successfully with {len(monte_carlo_results)} simulation scenarios")
            return detailed_plan

        except Exception as e:
            logger.error(f"Error creating detailed plan: {e}")
            raise

    async def _create_goal_summary_with_mistral(self, goal: GoalParameters,
                                              result: MonteCarloResult,
                                              user_id: str) -> str:
        """Create goal summary using Mistral LLM"""
        try:
            plan_data = {
                "goal_type": goal.goal_type.value,
                "target_amount": goal.target_amount,
                "time_horizon": goal.time_horizon_years,
                "success_probability": result.success_probability if result else 0.7,
                "monthly_investment": goal.monthly_investment or 1000
            }

            # Use Mistral to create a natural language summary
            mistral_response = await create_plan_with_mistral(goal.__dict__, plan_data, user_id)

            if mistral_response and not mistral_response.get("error"):
                return mistral_response.get("summary", self._default_goal_summary(goal, result))
            else:
                return self._default_goal_summary(goal, result)

        except Exception as e:
            logger.error(f"Error creating goal summary with Mistral: {e}")
            return self._default_goal_summary(goal, result)

    def _default_goal_summary(self, goal: GoalParameters, result: MonteCarloResult) -> str:
        """Default goal summary fallback"""
        return f"""Your {goal.goal_type.value.replace('_', ' ')} goal targets ${goal.target_amount:,.0f}
        over {goal.time_horizon_years} years. Based on Monte Carlo analysis, there's a
        {result.success_probability:.0%} probability of achieving this goal with the recommended strategy."""

    def _generate_risk_considerations(self, goal: GoalParameters,
                                    asset_allocation: Dict[str, float]) -> List[str]:
        """Generate risk considerations for the plan"""
        considerations = []

        equity_allocation = asset_allocation.get("equities", 0.6)
        if equity_allocation > 0.8:
            considerations.append("High equity allocation increases volatility but potential for higher returns")
        elif equity_allocation < 0.3:
            considerations.append("Conservative allocation may struggle to keep pace with inflation")

        if goal.time_horizon_years < 5:
            considerations.append("Short time horizon limits ability to recover from market downturns")
        elif goal.time_horizon_years > 20:
            considerations.append("Long time horizon allows for more aggressive growth strategies")

        if goal.target_amount > 1000000:
            considerations.append("Large goal amount may require periodic strategy adjustments")

        return considerations

    def _generate_milestones(self, goal: GoalParameters, monthly_investment: float) -> List[Dict[str, Any]]:
        """Generate milestone checkpoints"""
        milestones = []

        # Calculate milestones at 25%, 50%, 75% of time horizon
        milestone_points = [0.25, 0.5, 0.75]

        for point in milestone_points:
            years = int(goal.time_horizon_years * point)
            target_value = goal.target_amount * point

            milestones.append({
                "year": years,
                "target_value": target_value,
                "description": f"Reach ${target_value:,.0f} by year {years}",
                "action": f"Review and rebalance portfolio"
            })

        return milestones

    def _generate_alternative_scenarios(self, goal: GoalParameters,
                                      monte_carlo_results: List[MonteCarloResult]) -> List[Dict[str, Any]]:
        """Generate alternative scenario recommendations"""
        scenarios = []

        for result in monte_carlo_results:
            if result.success_probability < 0.7:
                scenarios.append({
                    "scenario": result.scenario.value,
                    "issue": f"Only {result.success_probability:.0%} success probability",
                    "recommendation": f"Increase monthly investment to ${result.required_monthly_savings:.0f}",
                    "impact": f"Would improve success rate significantly"
                })

        return scenarios

    def _generate_stress_test_summary(self, monte_carlo_results: List[MonteCarloResult]) -> str:
        """Generate summary of stress test results"""
        stress_result = next(
            (r for r in monte_carlo_results if r.scenario == SimulationScenario.STRESS),
            None
        )

        if stress_result:
            return f"""Under stress conditions (market crashes, high inflation), your plan has a
            {stress_result.success_probability:.0%} chance of success. The 10th percentile outcome
            would be ${stress_result.percentile_10:,.0f}, suggesting you should prepare for
            potential shortfalls in adverse scenarios."""
        else:
            return "Stress testing not available - recommend periodic plan review."

    # Data persistence methods
    async def save_analysis_to_supabase(self, session_id: str, user_id: str,
                                      detailed_plan: DetailedPlan,
                                      goal_parameters: GoalParameters) -> bool:
        """
        Save complete planner analysis to Supabase.

        Args:
            session_id: Analysis session ID
            user_id: User identifier
            detailed_plan: Complete detailed plan with Monte Carlo results
            goal_parameters: Original goal parameters

        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Saving planner analysis to Supabase for session {session_id}")

            # Prepare Monte Carlo results data
            monte_carlo_data = []
            for result in detailed_plan.monte_carlo_results:
                monte_carlo_data.append({
                    "scenario": result.scenario.value if hasattr(result.scenario, 'value') else str(result.scenario),
                    "success_probability": result.success_probability,
                    "expected_final_value": result.expected_final_value,
                    "percentile_10": result.percentile_10,
                    "percentile_50": result.percentile_50,
                    "percentile_90": result.percentile_90,
                    "shortfall_risk": result.shortfall_risk,
                    "excess_probability": result.excess_probability,
                    "required_monthly_savings": result.required_monthly_savings,
                    "confidence_interval": result.confidence_interval
                })

            # Compile complete planner data
            planner_data = {
                "goal_type": goal_parameters.goal_type.value if hasattr(goal_parameters.goal_type, 'value') else str(goal_parameters.goal_type),
                "target_amount": goal_parameters.target_amount,
                "time_horizon_years": detailed_plan.time_horizon_years,
                "current_age": goal_parameters.current_age,
                "risk_tolerance": goal_parameters.risk_tolerance.value if hasattr(goal_parameters.risk_tolerance, 'value') else str(goal_parameters.risk_tolerance),
                "monthly_investment": detailed_plan.recommended_monthly_investment,
                "success_probability": detailed_plan.success_probability,
                "expected_final_value": detailed_plan.expected_final_value,
                "goal_summary": detailed_plan.goal_summary,
                "asset_allocation": detailed_plan.asset_allocation,
                "risk_considerations": detailed_plan.risk_considerations,
                "milestones": detailed_plan.milestones,
                "alternative_scenarios": detailed_plan.alternative_scenarios,
                "stress_test_summary": detailed_plan.stress_test_summary,
                "monte_carlo_results": monte_carlo_data
            }

            # Save to Supabase
            success = await AgentDataService.save_planner_analysis(session_id, user_id, planner_data)

            if success:
                logger.info(f"Successfully saved planner analysis for session {session_id}")
            else:
                logger.error(f"Failed to save planner analysis for session {session_id}")

            return success

        except Exception as e:
            logger.error(f"Error saving planner analysis to Supabase: {e}")
            return False

    async def create_complete_plan_analysis(self, goal_text: str, user_id: str, session_id: str,
                                          user_profile: UserProfile = None) -> Dict[str, Any]:
        """
        Create complete plan analysis including goal parsing, Monte Carlo simulations,
        and detailed planning, then save to Supabase.

        Args:
            goal_text: Natural language goal description
            user_id: User identifier
            session_id: Analysis session ID
            user_profile: Optional user profile information

        Returns:
            Complete plan analysis results
        """
        try:
            logger.info(f"Creating complete plan analysis for session {session_id}")

            # Parse goal using enhanced Mistral LLM parsing
            goal_response = await self.parse_goal(goal_text, user_id)
            if "error" in goal_response:
                raise Exception(f"Goal parsing failed: {goal_response['error']}")

            # Extract goal parameters
            parsed_goal = goal_response.get("parsed_goal", {})
            goal_type = GoalType(parsed_goal.get("goal_type", "general_savings"))

            goal_parameters = GoalParameters(
                goal_type=goal_type,
                target_amount=parsed_goal.get("target_amount", 100000),
                time_horizon_years=parsed_goal.get("time_horizon_years", 10),
                current_age=parsed_goal.get("current_age"),
                risk_tolerance=RiskLevel(parsed_goal.get("risk_tolerance", 3)),
                monthly_investment=parsed_goal.get("monthly_investment")
            )

            # Create detailed plan with Monte Carlo analysis
            detailed_plan = await self.create_detailed_plan(goal_parameters, user_profile, user_id)

            # Save to Supabase
            await self.save_analysis_to_supabase(
                session_id=session_id,
                user_id=user_id,
                detailed_plan=detailed_plan,
                goal_parameters=goal_parameters
            )

            # Compile complete response
            complete_analysis = {
                "goal_parsing": goal_response,
                "goal_parameters": {
                    "goal_type": goal_parameters.goal_type.value if hasattr(goal_parameters.goal_type, 'value') else str(goal_parameters.goal_type),
                    "target_amount": goal_parameters.target_amount,
                    "time_horizon_years": goal_parameters.time_horizon_years,
                    "current_age": goal_parameters.current_age,
                    "risk_tolerance": goal_parameters.risk_tolerance.value if hasattr(goal_parameters.risk_tolerance, 'value') else str(goal_parameters.risk_tolerance),
                    "monthly_investment": goal_parameters.monthly_investment
                },
                "detailed_plan": {
                    "goal_summary": detailed_plan.goal_summary,
                    "recommended_monthly_investment": detailed_plan.recommended_monthly_investment,
                    "asset_allocation": detailed_plan.asset_allocation,
                    "time_horizon_years": detailed_plan.time_horizon_years,
                    "expected_final_value": detailed_plan.expected_final_value,
                    "success_probability": detailed_plan.success_probability,
                    "risk_considerations": detailed_plan.risk_considerations,
                    "milestones": detailed_plan.milestones,
                    "alternative_scenarios": detailed_plan.alternative_scenarios,
                    "stress_test_summary": detailed_plan.stress_test_summary
                },
                "monte_carlo_results": [
                    {
                        "scenario": result.scenario.value if hasattr(result.scenario, 'value') else str(result.scenario),
                        "success_probability": result.success_probability,
                        "expected_final_value": result.expected_final_value,
                        "percentile_10": result.percentile_10,
                        "percentile_50": result.percentile_50,
                        "percentile_90": result.percentile_90,
                        "shortfall_risk": result.shortfall_risk,
                        "excess_probability": result.excess_probability,
                        "required_monthly_savings": result.required_monthly_savings
                    } for result in detailed_plan.monte_carlo_results
                ],
                "analysis_metadata": {
                    "session_id": session_id,
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    "data_saved": True,
                    "simulation_count": len(detailed_plan.monte_carlo_results) * 1000  # Assuming 1000 sims per scenario
                }
            }

            logger.info(f"Complete plan analysis created and saved for session {session_id}")
            return complete_analysis

        except Exception as e:
            logger.error(f"Error creating complete plan analysis: {e}")
            return {"error": str(e)}

    async def enhance_existing_plan_with_monte_carlo(self, session_id: str, user_id: str,
                                                   existing_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance an existing plan with Monte Carlo analysis and save updated data.

        Args:
            session_id: Analysis session ID
            user_id: User identifier
            existing_plan: Existing plan data to enhance

        Returns:
            Enhanced plan with Monte Carlo results
        """
        try:
            logger.info(f"Enhancing existing plan with Monte Carlo for session {session_id}")

            # Extract goal parameters from existing plan
            goal_type = GoalType(existing_plan.get("goal_type", "general_savings"))
            goal_parameters = GoalParameters(
                goal_type=goal_type,
                target_amount=existing_plan.get("target_amount", 100000),
                time_horizon_years=existing_plan.get("time_horizon_years", 10),
                current_age=existing_plan.get("current_age"),
                risk_tolerance=RiskLevel(existing_plan.get("risk_tolerance", 3)),
                monthly_investment=existing_plan.get("monthly_investment", 1000)
            )

            # Extract asset allocation
            asset_allocation = existing_plan.get("asset_allocation", {"equities": 0.6, "bonds": 0.4})

            # Run Monte Carlo simulations
            monte_carlo_results = await self.run_monte_carlo_simulation(
                goal_parameters, goal_parameters.monthly_investment, asset_allocation
            )

            # Update success probability with realistic scenario
            realistic_result = next(
                (r for r in monte_carlo_results if r.scenario == SimulationScenario.REALISTIC),
                monte_carlo_results[0] if monte_carlo_results else None
            )

            enhanced_plan = {
                **existing_plan,
                "success_probability": realistic_result.success_probability if realistic_result else 0.7,
                "expected_final_value": realistic_result.expected_final_value if realistic_result else goal_parameters.target_amount,
                "monte_carlo_results": monte_carlo_results,
                "enhanced_at": datetime.now().isoformat()
            }

            # Create DetailedPlan object for saving
            detailed_plan = DetailedPlan(
                goal_summary=existing_plan.get("goal_summary", "Enhanced investment plan"),
                recommended_monthly_investment=goal_parameters.monthly_investment,
                asset_allocation=asset_allocation,
                time_horizon_years=goal_parameters.time_horizon_years,
                expected_final_value=realistic_result.expected_final_value if realistic_result else goal_parameters.target_amount,
                success_probability=realistic_result.success_probability if realistic_result else 0.7,
                monte_carlo_results=monte_carlo_results,
                risk_considerations=existing_plan.get("risk_considerations", []),
                milestones=existing_plan.get("milestones", []),
                alternative_scenarios=existing_plan.get("alternative_scenarios", []),
                stress_test_summary=existing_plan.get("stress_test_summary", "")
            )

            # Save enhanced plan to Supabase
            await self.save_analysis_to_supabase(session_id, user_id, detailed_plan, goal_parameters)

            logger.info(f"Enhanced plan saved for session {session_id}")
            return enhanced_plan

        except Exception as e:
            logger.error(f"Error enhancing plan with Monte Carlo: {e}")
            return {"error": str(e)}

    async def assess_goal_feasibility(self, target_amount: float, monthly_savings: float,
                                    years: int, expected_return: float = 0.07) -> Dict[str, Any]:
        """
        Assess feasibility of reaching a financial goal.

        Args:
            target_amount: Target amount needed
            monthly_savings: Available monthly savings
            years: Number of years to goal
            expected_return: Expected annual return

        Returns:
            Feasibility assessment dictionary
        """
        try:
            monthly_rate = expected_return / 12
            months = years * 12

            # Future value of monthly savings
            if monthly_rate > 0:
                fv_savings = monthly_savings * (((1 + monthly_rate) ** months - 1) / monthly_rate)
            else:
                fv_savings = monthly_savings * months

            shortfall = max(target_amount - fv_savings, 0)
            surplus = max(fv_savings - target_amount, 0)

            feasibility_score = min(fv_savings / target_amount, 1.0) if target_amount > 0 else 1.0

            recommendations = []
            if shortfall > 0:
                additional_monthly = shortfall / months if months > 0 else shortfall
                recommendations.append(f"Increase monthly savings by ${additional_monthly:,.2f}")

                if feasibility_score < 0.7:
                    recommendations.append("Consider extending time horizon")
                    recommendations.append("Explore higher-return investments")

            return {
                "is_feasible": shortfall == 0,
                "projected_amount": fv_savings,
                "shortfall": shortfall,
                "surplus": surplus,
                "feasibility_score": feasibility_score,
                "recommended_adjustments": recommendations
            }

        except Exception as e:
            logger.error(f"Error assessing goal feasibility: {e}")
            return {"error": str(e)}