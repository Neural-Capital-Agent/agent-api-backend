from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
import uuid
import re

from .models import (
    GoalType, RiskLevel, GoalParameters, UserProfile, InvestmentStrategy,
    GlidePath, BondLadder
)
from .config import config
from .shared import BaseAgent, ErrorHandler, get_current_timestamp, safe_get, safe_coral_invoke

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """
    Financial Planner Agent responsible for natural language goal interpretation
    and lifecycle-based investment planning.
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555"):
        super().__init__(coral_server_url, "planner_agent")
        from .models import GoalType, RiskLevel

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

    async def parse_goal(self, goal_text: str):
        """Extract goal parameters from natural language text"""
        from .models import GoalParameters

        try:
            # Use LLM agent for advanced parsing via Coral Protocol
            llm_response = await self.process_natural_language_goal(goal_text)

            # Extract goal type
            goal_type = self._extract_goal_type(goal_text, llm_response)

            # Extract target amount
            target_amount = self._extract_amount(goal_text, llm_response)

            # Extract time horizon
            time_horizon = self._extract_time_horizon(goal_text, llm_response)

            # Extract age-related information
            current_age = self._extract_age(goal_text, llm_response)

            # Set defaults based on goal type
            strategy = self.goal_strategies.get(goal_type, {})
            risk_tolerance = strategy.get("risk_level")

            goal_params = GoalParameters(
                goal_type=goal_type,
                target_amount=target_amount,
                time_horizon_years=time_horizon,
                current_age=current_age,
                risk_tolerance=risk_tolerance
            )

            logger.info(f"Parsed goal: {goal_type.value}, ${target_amount:,.0f}, {time_horizon} years")

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
        from .models import InvestmentStrategy, GoalType

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
        from .models import GlidePath

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
        """Use external LLM agents for advanced NLP processing via Coral Protocol"""
        llm_response = await safe_coral_invoke(
            self.coral_client,
            "llm_agent",
            "parse_goal",
            {"text": goal_text, "context": "financial_planning"},
            "process_natural_language_goal"
        )

        if llm_response:
            return llm_response

        # No fallbacks - raise error if LLM processing fails
        raise Exception("Failed to process goal with LLM and no fallback data available")

    def _extract_goal_type(self, goal_text: str, llm_response: Dict):
        """Extract goal type from text and LLM response"""
        from .models import GoalType

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
        from .models import GoalType

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
        # Use Mistral LLM for goal parsing via Coral Protocol
        llm_response = await safe_coral_invoke(
            self.coral_client,
            "llm_agent",
            "parse_goal",
            {"text": goal_text, "context": "financial_planning"},
            "parse_goal"
        )

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
            from .models import GoalType
            goal_type = GoalType[goal.get("type", "RETIREMENT")]
            strategy = self.get_goal_strategy(goal_type)

            # Use Mistral LLM via Coral Protocol for plan creation
            plan_response = await safe_coral_invoke(
                self.coral_client,
                "llm_agent",
                "create_plan",
                {"goal": goal, "strategy": strategy},
                "create_plan"
            )

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