# Planner Agent Documentation

## Overview

The **Planner Agent** is responsible for **natural language goal interpretation and lifecycle-based investment planning**. It converts natural language financial goals into structured investment strategies with specific allocations, time horizons, and risk levels, making financial planning accessible through conversational interfaces.

## What the Planner Agent Does

The Planner Agent provides comprehensive financial planning capabilities:

1. **Natural Language Goal Parsing**: Converts conversational text into structured financial goals
2. **Investment Strategy Generation**: Creates appropriate strategies based on goals and user profiles
3. **Lifecycle Planning**: Adjusts recommendations based on age and life stage
4. **Glide Path Construction**: Builds age-appropriate asset allocation progressions
5. **Goal-Based Asset Allocation**: Optimizes portfolios for specific financial objectives

## Key Inputs

### 1. Natural Language Goal Text
```python
{
    "goal_text": "I want to save $500,000 for retirement in 30 years. I'm 35 years old and have moderate risk tolerance.",
    "context": "retirement_planning",
    "user_id": "user_123"
}
```

### 2. User Profile
```python
{
    "age": 35,
    "income": 75000,                    # Annual income
    "current_savings": 50000,           # Existing savings
    "risk_tolerance": "BALANCED",       # Risk appetite
    "investment_experience": "intermediate",
    "time_horizon": 30,                 # Years to goal
    "liquidity_needs": "low",           # Near-term cash needs
    "tax_status": "taxable_account",    # Account type
    "goals": [                          # Existing goals
        {
            "type": "emergency_fund",
            "target_amount": 25000,
            "priority": "high"
        }
    ]
}
```

### 3. Goal Parameters (Structured)
```python
{
    "goal_type": "RETIREMENT",
    "target_amount": 500000,
    "time_horizon_years": 30,
    "current_age": 35,
    "retirement_age": 65,
    "risk_tolerance": "BALANCED",
    "priority": "high",
    "current_progress": 25000,          # Already saved
    "monthly_contribution": 1000        # Available monthly savings
}
```

### 4. Market Context (From Data Agent)
```python
{
    "interest_rates": {
        "fed_funds_rate": 0.0525,       # 5.25%
        "10_year_treasury": 0.045       # 4.5%
    },
    "inflation_rate": 0.032,            # 3.2%
    "market_regime": "normal_conditions"
}
```

## Key Outputs

### 1. Parsed Goal Parameters
```python
{
    "goal_id": "goal_789a1b2c-3d4e-5f6g-7h8i-9j0k1l2m3n4o",
    "goal_type": "RETIREMENT",
    "target_amount": 500000,
    "time_horizon_years": 30,
    "current_age": 35,
    "retirement_age": 65,
    "risk_tolerance": "BALANCED",
    "confidence_score": 0.92,           # Goal parsing confidence
    "extracted_keywords": ["retirement", "save", "$500,000", "30 years", "35 years old"],
    "fallback_used": false,             # Whether defaults were used
    "parsed_at": "2024-01-15T10:30:00Z"
}
```

### 2. Investment Strategy
```python
{
    "strategy_id": "strategy_456d7e8f-9g0h-1i2j-3k4l-5m6n7o8p9q0r",
    "goal_type": "RETIREMENT",
    "recommended_allocation": {
        "equities": 0.70,               # 70% stocks
        "bonds": 0.25,                  # 25% bonds
        "alternatives": 0.05            # 5% alternatives
    },
    "detailed_allocation": {
        "domestic_equity": 0.45,        # 45% U.S. stocks
        "international_equity": 0.25,   # 25% international stocks
        "bonds": 0.25,                  # 25% bonds
        "alternatives": 0.05            # 5% REITs/commodities
    },
    "risk_level": "BALANCED",
    "expected_return": 0.075,           # 7.5% annual expected return
    "expected_volatility": 0.12,        # 12% annual volatility
    "time_horizon": 30,
    "constraints": {
        "min_bond_allocation": 0.20,    # Minimum 20% bonds
        "max_single_asset": 0.30,       # Max 30% in single asset
        "rebalancing_frequency": "quarterly"
    },
    "projected_outcomes": {
        "median_outcome": 687500,       # 50th percentile outcome
        "conservative_outcome": 425000, # 25th percentile
        "optimistic_outcome": 950000,   # 75th percentile
        "probability_of_success": 0.78  # Chance of meeting goal
    },
    "monthly_contribution_needed": 856, # Required monthly savings
    "created_at": "2024-01-15T10:30:00Z"
}
```

### 3. Glide Path
```python
{
    "glide_path_id": "glide_123e4567-e89b-12d3-a456-426614174000",
    "target_retirement_age": 65,
    "current_age": 35,
    "age_ranges": {
        "25-34": {
            "equities": 0.90,           # 90% stocks when young
            "bonds": 0.10,              # 10% bonds
            "alternatives": 0.00
        },
        "35-44": {
            "equities": 0.80,           # 80% stocks
            "bonds": 0.20,              # 20% bonds
            "alternatives": 0.00
        },
        "45-54": {
            "equities": 0.70,           # 70% stocks
            "bonds": 0.25,              # 25% bonds
            "alternatives": 0.05        # 5% alternatives
        },
        "55-64": {
            "equities": 0.60,           # 60% stocks
            "bonds": 0.35,              # 35% bonds
            "alternatives": 0.05        # 5% alternatives
        },
        "65+": {
            "equities": 0.40,           # 40% stocks in retirement
            "bonds": 0.50,              # 50% bonds
            "cash": 0.10                # 10% cash for liquidity
        }
    },
    "rebalancing_triggers": {
        "age_milestone": true,          # Rebalance at age milestones
        "allocation_drift": 0.05,       # 5% drift threshold
        "market_conditions": true       # Adjust for macro signals
    }
}
```

### 4. Financial Plan
```python
{
    "plan_id": "plan_987f6e5d-4c3b-2a19-8e7f-6d5c4b3a2190",
    "goal_id": "goal_789a1b2c-3d4e-5f6g-7h8i-9j0k1l2m3n4o",
    "user_id": "user_123",
    "plan_summary": {
        "goal": "Accumulate $500,000 for retirement by age 65",
        "time_horizon": "30 years",
        "required_monthly_savings": 856,
        "current_monthly_capacity": 1000,
        "surplus_capacity": 144,
        "probability_of_success": 0.78
    },
    "implementation_steps": [
        {
            "step": 1,
            "action": "Open target-date retirement fund",
            "description": "Start with a 2055 target-date fund for automatic diversification",
            "priority": "immediate",
            "estimated_time": "1 week"
        },
        {
            "step": 2,
            "action": "Set up automatic contributions",
            "description": "Automate $856/month contributions from paycheck",
            "priority": "immediate",
            "estimated_time": "1 day"
        },
        {
            "step": 3,
            "action": "Annual review and rebalancing",
            "description": "Review allocation annually and adjust for age",
            "priority": "ongoing",
            "frequency": "annual"
        }
    ],
    "milestones": [
        {
            "age": 40,
            "target_balance": 125000,
            "allocation_review": "Consider reducing equity to 75%"
        },
        {
            "age": 50,
            "target_balance": 275000,
            "allocation_review": "Reduce equity to 65%, increase bonds"
        },
        {
            "age": 60,
            "target_balance": 425000,
            "allocation_review": "Conservative shift: 55% equity, 40% bonds"
        }
    ],
    "assumptions": {
        "inflation_rate": 0.025,        # 2.5% inflation assumption
        "salary_growth": 0.03,          # 3% annual salary increases
        "contribution_increases": 0.03, # 3% annual contribution increases
        "tax_rate": 0.22,              # 22% effective tax rate
        "social_security": 2400        # Monthly SS benefit estimate
    },
    "risk_factors": [
        "Market volatility could impact returns",
        "Inflation may reduce purchasing power",
        "Job loss could interrupt contributions",
        "Healthcare costs may increase in retirement"
    ],
    "created_at": "2024-01-15T10:30:00Z"
}
```

## Core Features

### 1. Goal Type Recognition and Strategy Mapping

The Planner Agent recognizes four primary goal types, each with distinct characteristics:

#### Retirement Goals
```python
RETIREMENT_STRATEGY = {
    "time_horizon": (20, 40),          # 20-40 years
    "base_allocation": {
        "equities": 0.80,              # 80% stocks for growth
        "bonds": 0.15,                 # 15% bonds for stability
        "alternatives": 0.05           # 5% alternatives for diversification
    },
    "risk_level": "GROWTH",
    "keywords": ["retirement", "retire", "pension", "401k", "ira", "nest egg"],
    "default_amount": 1000000,
    "considerations": [
        "Long time horizon allows for equity focus",
        "Tax-advantaged accounts preferred",
        "Consider Roth vs traditional IRA",
        "Social Security integration"
    ]
}
```

#### House Down Payment Goals
```python
HOUSE_STRATEGY = {
    "time_horizon": (3, 7),            # 3-7 years
    "base_allocation": {
        "bonds": 0.80,                 # 80% bonds for stability
        "equities": 0.20               # 20% stocks for modest growth
    },
    "risk_level": "CONSERVATIVE",
    "keywords": ["house", "home", "down payment", "mortgage", "property", "real estate"],
    "default_amount": 100000,
    "considerations": [
        "Capital preservation is critical",
        "Liquidity needed at specific date",
        "Consider high-yield savings accounts",
        "Avoid market risk near purchase date"
    ]
}
```

#### Emergency Fund Goals
```python
EMERGENCY_STRATEGY = {
    "time_horizon": (0, 1),            # Immediate need
    "base_allocation": {
        "cash": 1.0                    # 100% cash for liquidity
    },
    "risk_level": "CONSERVATIVE",
    "keywords": ["emergency", "emergency fund", "safety net", "rainy day"],
    "default_amount": 25000,
    "considerations": [
        "Maximum liquidity required",
        "No market risk acceptable",
        "High-yield savings or money market",
        "3-6 months of expenses typically"
    ]
}
```

#### Child Education Goals
```python
EDUCATION_STRATEGY = {
    "time_horizon": (10, 18),          # 10-18 years
    "base_allocation": {
        "equities": 0.60,              # 60% stocks
        "bonds": 0.40                  # 40% bonds
    },
    "risk_level": "BALANCED",
    "keywords": ["education", "college", "university", "school", "tuition", "529"],
    "default_amount": 200000,
    "considerations": [
        "529 plan tax advantages",
        "Age-based allocation adjustment",
        "State tax deduction considerations",
        "Alternative funding sources"
    ]
}
```

### 2. Natural Language Processing Engine

#### Text Parsing and Extraction
```python
async def parse_goal(self, goal_text: str):
    """Extract structured information from natural language"""

    # Primary extraction via LLM (when available)
    try:
        llm_response = await self.coral_client.invoke_agent("llm_agent", "parse_goal", {
            "text": goal_text,
            "context": "financial_planning"
        })

        if llm_response and not llm_response.get("error"):
            return self._structure_llm_response(llm_response)

    except Exception:
        # Fallback to rule-based extraction
        pass

    # Rule-based extraction as fallback
    goal_type = self._extract_goal_type(goal_text)
    target_amount = self._extract_amount(goal_text)
    time_horizon = self._extract_time_horizon(goal_text)
    current_age = self._extract_age(goal_text)

    return {
        "goal_type": goal_type.name,
        "target_amount": target_amount,
        "time_horizon": time_horizon,
        "current_age": current_age,
        "extraction_method": "rule_based"
    }
```

#### Amount Extraction with Pattern Matching
```python
def _extract_amount(self, text: str, llm_response: dict = None):
    """Extract monetary amounts from text with sophisticated pattern matching"""

    if llm_response and llm_response.get("target_amount"):
        return float(llm_response["target_amount"])

    # Regex patterns for different amount formats
    amount_patterns = [
        r'\$?([\d,]+(?:\.\d{2})?)\s*(?:million|mil|m)',      # $2.5 million
        r'\$?([\d,]+(?:\.\d{2})?)\s*(?:thousand|k)',         # $250 thousand
        r'\$?([\d,]+(?:\.\d{2})?)',                          # $100,000
        r'([\d,]+(?:\.\d{2})?)\s*dollars?',                 # 500000 dollars
    ]

    for pattern in amount_patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            amount_str = matches[0].replace(",", "")
            amount = float(amount_str)

            # Apply multipliers
            text_lower = text.lower()
            if any(word in text_lower for word in ["million", "mil", "m"]):
                amount *= 1_000_000
            elif any(word in text_lower for word in ["thousand", "k"]):
                amount *= 1_000

            return amount

    # Return default based on detected goal type
    goal_type = self._extract_goal_type(text, llm_response or {})
    return self._get_default_amount(goal_type)
```

#### Time Horizon Extraction
```python
def _extract_time_horizon(self, text: str, llm_response: dict = None):
    """Extract time horizons with flexible pattern matching"""

    if llm_response and llm_response.get("time_horizon"):
        return int(llm_response["time_horizon"])

    # Time patterns
    patterns = [
        r'in\s*(\d+)\s*years?',          # "in 30 years"
        r'(\d+)\s*years?\s*away',        # "30 years away"
        r'(\d+)\s*yrs?',                 # "30 yrs"
        r'(\d+)\s*year\s*horizon',       # "30 year horizon"
        r'by\s*age\s*(\d+)',            # "by age 65" -> calculate years
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            years = int(matches[0])

            # Handle "by age X" pattern
            if "by age" in pattern:
                current_age = self._extract_age(text, llm_response or {})
                if current_age:
                    years = years - current_age

            return max(1, years)  # Minimum 1 year

    # Default based on goal type
    goal_type = self._extract_goal_type(text, llm_response or {})
    return self._get_default_horizon(goal_type)
```

### 3. Age-Based Allocation Adjustments

```python
def _adjust_allocation_for_age_and_horizon(self, base_allocation, age, horizon):
    """Dynamically adjust allocation based on age and time horizon"""

    allocation = base_allocation.copy()

    # Age-based adjustments (older = more conservative)
    if age and age > 60:
        if "bonds" in allocation:
            allocation["bonds"] = min(allocation["bonds"] + 0.10, 0.80)
        if "equities" in allocation:
            allocation["equities"] = max(allocation["equities"] - 0.10, 0.20)

    # Time horizon adjustments (shorter = more conservative)
    if horizon and horizon < 5:
        # Short-term goals need more liquidity
        if "cash" not in allocation:
            allocation["cash"] = 0.0
        allocation["cash"] += 0.10

        if "equities" in allocation:
            allocation["equities"] = max(allocation["equities"] - 0.10, 0.10)

    # Normalize allocations to sum to 1.0
    total = sum(allocation.values())
    if total > 0:
        allocation = {k: v / total for k, v in allocation.items()}

    return allocation
```

### 4. Lifecycle Glide Path Construction

```python
def build_glide_path(self, current_age: int, retirement_age: int = 65):
    """Create age-appropriate asset allocation progression"""

    glide_path_rules = {
        "young_aggressive": {
            "age_range": (20, 35),
            "equity_percentage": 0.90,
            "rationale": "Long time horizon allows maximum growth focus"
        },
        "middle_balanced": {
            "age_range": (35, 50),
            "equity_percentage": 0.75,
            "rationale": "Balance growth with increasing stability needs"
        },
        "pre_retirement": {
            "age_range": (50, 65),
            "equity_percentage": 0.60,
            "rationale": "Reduce risk as retirement approaches"
        },
        "retirement": {
            "age_range": (65, 100),
            "equity_percentage": 0.40,
            "rationale": "Focus on income and capital preservation"
        }
    }

    age_ranges = {}

    # Build glide path based on current age
    for stage, rules in glide_path_rules.items():
        min_age, max_age = rules["age_range"]
        equity_pct = rules["equity_percentage"]

        if current_age < 35:
            age_ranges["<35"] = {"equities": 0.90, "bonds": 0.10, "cash": 0.00}
        elif current_age < 45:
            age_ranges["35-44"] = {"equities": 0.80, "bonds": 0.20, "cash": 0.00}
        elif current_age < 55:
            age_ranges["45-54"] = {"equities": 0.70, "bonds": 0.25, "alternatives": 0.05}
        elif current_age < 65:
            age_ranges["55-64"] = {"equities": 0.60, "bonds": 0.35, "alternatives": 0.05}
        else:
            age_ranges["65+"] = {"equities": 0.40, "bonds": 0.50, "cash": 0.10}

    return GlidePath(
        age_ranges=age_ranges,
        target_retirement_age=retirement_age,
        rebalancing_frequency="annual",
        created_at=datetime.now()
    )
```

### 5. Expected Return Calculation

```python
def _calculate_expected_return(self, allocation: dict):
    """Calculate portfolio expected return based on asset class assumptions"""

    # Long-term expected returns by asset class
    expected_returns = {
        "equities": 0.10,               # 10% stocks
        "domestic_equity": 0.10,        # 10% U.S. stocks
        "international_equity": 0.09,   # 9% international stocks
        "bonds": 0.04,                  # 4% bonds
        "cash": 0.02,                   # 2% cash
        "alternatives": 0.06,           # 6% REITs/commodities
        "real_estate": 0.07,            # 7% REITs
        "commodities": 0.05             # 5% commodities
    }

    portfolio_return = 0.0
    for asset_class, weight in allocation.items():
        asset_return = expected_returns.get(asset_class, 0.05)  # Default 5%
        portfolio_return += weight * asset_return

    return portfolio_return
```

### 6. Goal Success Probability Modeling

```python
def calculate_goal_success_probability(self, strategy, current_savings, monthly_contribution):
    """Monte Carlo simulation to estimate goal achievement probability"""

    # Simulation parameters
    num_simulations = 10000
    annual_return = strategy["expected_return"]
    annual_volatility = strategy["expected_volatility"]
    years = strategy["time_horizon"]
    target_amount = strategy["target_amount"]

    success_count = 0

    for simulation in range(num_simulations):
        balance = current_savings

        for year in range(years):
            # Add annual contributions
            balance += monthly_contribution * 12

            # Apply random market return
            annual_return_sim = np.random.normal(annual_return, annual_volatility)
            balance *= (1 + annual_return_sim)

        if balance >= target_amount:
            success_count += 1

    probability = success_count / num_simulations

    return {
        "success_probability": probability,
        "expected_outcome": self._calculate_expected_outcome(
            current_savings, monthly_contribution, annual_return, years
        ),
        "pessimistic_outcome": self._calculate_percentile_outcome(
            current_savings, monthly_contribution, annual_return,
            annual_volatility, years, 0.25
        ),
        "optimistic_outcome": self._calculate_percentile_outcome(
            current_savings, monthly_contribution, annual_return,
            annual_volatility, years, 0.75
        )
    }
```

### 7. Constraint Integration

```python
def _build_constraints(self, goal, user_profile):
    """Build comprehensive investment constraints"""

    constraints = {
        "goal_type": goal.goal_type.value,
        "time_horizon": goal.time_horizon_years,
        "liquidity_needs": self._assess_liquidity_needs(goal),
        "tax_considerations": self._assess_tax_implications(goal, user_profile),
        "risk_constraints": self._build_risk_constraints(goal, user_profile)
    }

    # Age-based constraints
    if goal.current_age and goal.current_age > 60:
        constraints.update({
            "max_equity_allocation": 0.70,
            "min_bond_allocation": 0.30,
            "max_volatility": 0.15,
            "liquidity_buffer": 0.10
        })

    # Goal-specific constraints
    if goal.goal_type == GoalType.EMERGENCY_FUND:
        constraints.update({
            "max_equity_allocation": 0.00,
            "required_liquidity": 1.00,
            "maximum_risk": "none"
        })
    elif goal.goal_type == GoalType.HOUSE_DOWN_PAYMENT:
        constraints.update({
            "max_equity_allocation": 0.30,
            "required_liquidity": 0.90,
            "time_sensitivity": "high"
        })

    return constraints
```

## Integration with Other Agents

### Portfolio Agent Integration
```python
# Generate investment strategy, then request portfolio construction
strategy = await planner_agent.generate_strategy(goal, user_profile)

portfolio = await portfolio_agent.build_portfolio(
    risk_level=strategy.risk_level,
    goal=strategy.goal_type,
    constraints=strategy.constraints
)
```

### Data Agent Integration
```python
# Get economic context for planning assumptions
economic_indicators = await data_agent.get_economic_indicators([
    "inflation_rate", "interest_rates", "unemployment"
])

# Adjust planning assumptions based on economic data
planning_assumptions = planner_agent.adjust_assumptions(
    base_assumptions, economic_indicators
)
```

### Explainability Agent Integration
```python
# Provide plan rationale for user explanation
plan_explanation = {
    "goal_interpretation": "Retirement savings goal of $500K in 30 years",
    "strategy_rationale": "Growth-focused allocation appropriate for long time horizon",
    "risk_assessment": "Moderate risk balanced with growth potential",
    "key_assumptions": ["7.5% annual return", "2.5% inflation", "3% salary growth"]
}
```

## Configuration and Defaults

### Default Amounts by Goal Type
```python
DEFAULT_AMOUNTS = {
    GoalType.HOUSE_DOWN_PAYMENT: 100000,    # $100K down payment
    GoalType.RETIREMENT: 1000000,           # $1M retirement goal
    GoalType.EMERGENCY_FUND: 25000,         # $25K emergency fund
    GoalType.CHILD_EDUCATION: 200000        # $200K education fund
}
```

### Default Time Horizons
```python
DEFAULT_HORIZONS = {
    GoalType.HOUSE_DOWN_PAYMENT: 5,         # 5 years
    GoalType.RETIREMENT: 30,                # 30 years
    GoalType.EMERGENCY_FUND: 1,             # 1 year (immediate)
    GoalType.CHILD_EDUCATION: 15            # 15 years
}
```

### Planning Assumptions
```python
PLANNING_ASSUMPTIONS = {
    "inflation_rate": 0.025,                # 2.5% long-term inflation
    "salary_growth": 0.03,                  # 3% annual salary increases
    "social_security_replacement": 0.40,    # 40% income replacement
    "healthcare_cost_growth": 0.06,         # 6% annual healthcare inflation
    "tax_rates": {
        "federal": 0.22,                    # 22% federal tax rate
        "state": 0.05,                      # 5% state tax rate
        "fica": 0.0765                      # FICA taxes
    },
    "market_assumptions": {
        "equity_return": 0.10,              # 10% long-term equity return
        "bond_return": 0.04,                # 4% long-term bond return
        "equity_volatility": 0.16,          # 16% equity volatility
        "bond_volatility": 0.04             # 4% bond volatility
    }
}
```

## Advanced Features

### Stress Testing and Scenario Analysis
```python
async def stress_test_plan(self, financial_plan, stress_scenarios):
    """Test plan robustness under various scenarios"""

    scenarios = {
        "market_crash": {
            "equity_return": -0.30,         # -30% equity crash
            "duration_years": 1,
            "recovery_years": 3
        },
        "high_inflation": {
            "inflation_rate": 0.06,         # 6% inflation
            "duration_years": 5,
            "impact_on_returns": -0.02
        },
        "job_loss": {
            "contribution_interruption": 2, # 2 years no contributions
            "emergency_withdrawal": 10000   # $10K emergency withdrawal
        },
        "interest_rate_shock": {
            "rate_change": 0.04,            # +4% rate increase
            "bond_impact": -0.15,           # -15% bond value
            "duration_years": 1
        }
    }

    stress_results = {}

    for scenario_name, parameters in scenarios.items():
        adjusted_plan = self._apply_stress_scenario(financial_plan, parameters)
        outcome_probability = self.calculate_goal_success_probability(
            adjusted_plan, parameters
        )

        stress_results[scenario_name] = {
            "success_probability": outcome_probability,
            "expected_shortfall": self._calculate_shortfall(adjusted_plan),
            "recovery_time": self._calculate_recovery_time(adjusted_plan),
            "mitigation_strategies": self._suggest_mitigations(scenario_name)
        }

    return stress_results
```

### Dynamic Plan Adjustment
```python
async def update_plan(self, plan_id, new_circumstances):
    """Dynamically update financial plan based on life changes"""

    current_plan = await self.get_plan(plan_id)

    # Life event adjustments
    adjustments = {
        "salary_increase": self._adjust_for_income_change,
        "marriage": self._adjust_for_marriage,
        "child_birth": self._adjust_for_new_dependent,
        "home_purchase": self._adjust_for_major_purchase,
        "job_change": self._adjust_for_career_change,
        "market_change": self._adjust_for_market_conditions
    }

    updated_plan = current_plan
    for circumstance, details in new_circumstances.items():
        if circumstance in adjustments:
            updated_plan = adjustments[circumstance](updated_plan, details)

    # Recalculate projections
    updated_plan["projections"] = self.calculate_goal_success_probability(
        updated_plan, updated_plan["current_savings"],
        updated_plan["monthly_contribution"]
    )

    return updated_plan
```

This Planner Agent provides sophisticated financial planning capabilities that translate natural language goals into actionable, personalized investment strategies with appropriate risk management and lifecycle considerations.