"""
Configuration system for agent fallback responses and default values.
This module centralizes all mock/fallback data that was previously hardcoded in agent files.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AgentConfig:
    """Base configuration for all agents"""
    use_fallbacks: bool = False  # No fallbacks by default - must use real data
    log_fallback_usage: bool = True
    environment: str = "development"  # development, staging, production


class DataAgentConfig:
    """Configuration for DataAgent fallbacks and defaults"""

    # FRED API mappings
    MACRO_INDICATORS = {
        "CPI": "CPIAUCNS",
        "GDP": "GDP",
        "INFLATION": "CPIAUCNS",  # Map to CPI
        "INTEREST_RATES": "FEDFUNDS",  # Map to Fed Funds Rate
        "2Y_TREASURY": "GS2",
        "10Y_TREASURY": "GS10",
        "FED_FUNDS_RATE": "FEDFUNDS",
        "UNEMPLOYMENT": "UNRATE",
        "VIX": "VIXCLS",
        "PMI": "NAPMPMI",
        "DXY": "DTWEXBGS"
    }

    # Asset universe definitions
    EQUITY_UNIVERSE = ["SPY", "QQQ", "VXUS"]
    FIXED_INCOME_UNIVERSE = ["SGOV", "SHY", "IEF", "BND", "TIP"]
    ALTERNATIVES_UNIVERSE = ["GLD"]
    CRYPTO_UNIVERSE = ["BTC-USD", "ETH-USD"]

    # Market regime fallback responses
    MARKET_REGIME_FALLBACK = "normal_market_conditions"

    # Validation fallback responses
    VALIDATION_FALLBACK = {
        "is_valid": True,
        "confidence": 0.5,
        "reasoning": "Default validation due to processing error",
        "risk_level": "medium"
    }

    # Health check fallback responses
    HEALTH_CHECK_FALLBACK = {
        "yahoo_finance": "unavailable",
        "fred": "unavailable",
        "polygon": "unavailable"
    }


class PortfolioAgentConfig:
    """Configuration for PortfolioAgent fallbacks and defaults"""

    # Base allocations by risk level
    BASE_ALLOCATIONS = {
        1: {  # CONSERVATIVE
            "equities": {"SPY": 0.0, "QQQ": 0.0, "VXUS": 0.0},
            "fixed_income": {"BND": 0.25, "IEF": 0.15, "SHY": 0.50},
            "alternatives": {"GLD": 0.10},
            "crypto": {"BTC-USD": 0.0, "ETH-USD": 0.0}
        },
        2: {  # BALANCED_CONSERVATIVE
            "equities": {"SPY": 0.25, "QQQ": 0.0, "VXUS": 0.10},
            "fixed_income": {"BND": 0.35, "IEF": 0.20, "SHY": 0.0},
            "alternatives": {"GLD": 0.10},
            "crypto": {"BTC-USD": 0.0, "ETH-USD": 0.0}
        },
        3: {  # BALANCED
            "equities": {"SPY": 0.40, "QQQ": 0.0, "VXUS": 0.20},
            "fixed_income": {"BND": 0.20, "IEF": 0.10, "SHY": 0.0},
            "alternatives": {"GLD": 0.10},
            "crypto": {"BTC-USD": 0.0, "ETH-USD": 0.0}
        },
        4: {  # GROWTH
            "equities": {"SPY": 0.45, "QQQ": 0.25, "VXUS": 0.20},
            "fixed_income": {"BND": 0.05, "IEF": 0.0, "SHY": 0.0},
            "alternatives": {"GLD": 0.05},
            "crypto": {"BTC-USD": 0.0, "ETH-USD": 0.0}
        },
        5: {  # AGGRESSIVE
            "equities": {"SPY": 0.40, "QQQ": 0.30, "VXUS": 0.20},
            "fixed_income": {"BND": 0.0, "IEF": 0.0, "SHY": 0.0},
            "alternatives": {"GLD": 0.05},
            "crypto": {"BTC-USD": 0.05, "ETH-USD": 0.0}
        }
    }

    # Expected returns for portfolio metrics calculation
    EXPECTED_RETURNS = {
        "SPY": 0.10, "QQQ": 0.12, "VXUS": 0.08,
        "SGOV": 0.05, "SHY": 0.03, "IEF": 0.04, "BND": 0.04, "TIP": 0.03,
        "GLD": 0.05, "BTC-USD": 0.15, "ETH-USD": 0.18
    }

    # Volatilities for portfolio metrics calculation
    VOLATILITIES = {
        "SPY": 0.16, "QQQ": 0.20, "VXUS": 0.18,
        "SGOV": 0.02, "SHY": 0.03, "IEF": 0.05, "BND": 0.04, "TIP": 0.04,
        "GLD": 0.15, "BTC-USD": 0.80, "ETH-USD": 0.90
    }

    # Default portfolio metrics
    DEFAULT_EXPECTED_RETURN = 0.08  # 8%
    DEFAULT_VOLATILITY = 0.15       # 15%

    # Backtest fallback results
    BACKTEST_FALLBACK = {
        "total_return": 0.085,
        "annualized_return": 0.083,
        "volatility": 0.152,
        "sharpe_ratio": 0.54,
        "max_drawdown": 0.087,
        "trades_executed": 12,
        "benchmark_comparison": {
            "spy_return": 0.095,
            "alpha": -0.010,
            "beta": 0.89
        }
    }


class PlannerAgentConfig:
    """Configuration for PlannerAgent fallbacks and defaults"""

    # Goal strategy mappings
    GOAL_STRATEGIES = {
        "house_down_payment": {
            "time_horizon": (3, 7),
            "allocation": {"bonds": 0.80, "equities": 0.20},
            "risk_level": 1  # CONSERVATIVE
        },
        "retirement": {
            "time_horizon": (20, 40),
            "allocation": {"equities": 0.80, "bonds": 0.15, "alternatives": 0.05},
            "risk_level": 4  # GROWTH
        },
        "emergency_fund": {
            "time_horizon": (0, 1),
            "allocation": {"cash": 1.0},
            "risk_level": 1  # CONSERVATIVE
        },
        "child_education": {
            "time_horizon": (10, 18),
            "allocation": {"equities": 0.60, "bonds": 0.40},
            "risk_level": 3  # BALANCED
        },
        "education": {
            "time_horizon": (10, 18),
            "allocation": {"equities": 0.60, "bonds": 0.40},
            "risk_level": 3  # BALANCED
        }
    }

    # Goal keywords for parsing
    GOAL_KEYWORDS = {
        "house_down_payment": [
            "house", "home", "down payment", "mortgage", "property", "real estate"
        ],
        "retirement": [
            "retirement", "retire", "pension", "401k", "ira", "nest egg"
        ],
        "emergency_fund": [
            "emergency", "emergency fund", "safety net", "rainy day"
        ],
        "child_education": [
            "child education", "college", "university", "school", "tuition", "529"
        ],
        "education": [
            "education", "college", "university", "school", "tuition", "529"
        ]
    }

    # Default amounts by goal type
    DEFAULT_AMOUNTS = {
        "house_down_payment": 100000,
        "retirement": 1000000,
        "emergency_fund": 25000,
        "child_education": 200000,
        "education": 500000
    }

    # Default time horizons by goal type
    DEFAULT_HORIZONS = {
        "house_down_payment": 5,
        "retirement": 30,
        "emergency_fund": 1,
        "child_education": 15,
        "education": 15
    }

    # Expected returns by asset class
    EXPECTED_RETURNS = {
        "equities": 0.10,
        "bonds": 0.04,
        "cash": 0.02,
        "alternatives": 0.06
    }

    # Age-based glide path allocations
    GLIDE_PATH_ALLOCATIONS = {
        "under_35": {"equities": 0.90, "bonds": 0.10, "cash": 0.00},
        "35_44": {"equities": 0.80, "bonds": 0.20, "cash": 0.00},
        "45_54": {"equities": 0.70, "bonds": 0.25, "alternatives": 0.05},
        "55_64": {"equities": 0.60, "bonds": 0.35, "alternatives": 0.05},
        "65_plus": {"equities": 0.40, "bonds": 0.50, "cash": 0.10}
    }

    # LLM fallback response for goal parsing
    GOAL_PARSING_FALLBACK = {
        "goal_type": "retirement",
        "target_amount": 1000000,
        "time_horizon": 30
    }

    # Default configuration values
    DEFAULT_RETIREMENT_AGE = 65
    DEFAULT_TIME_HORIZON = 30
    MIN_EMERGENCY_FUND_MONTHS = 6
    MAX_GOAL_HORIZON = 50


class ExplainabilityAgentConfig:
    """Configuration for ExplainabilityAgent fallbacks and defaults"""

    # Financial jargon dictionary
    JARGON_DICTIONARY = {
        "yield_curve_inversion": "When long-term interest rates fall below short-term rates",
        "credit_spreads": "The extra interest risky bonds pay compared to safe government bonds",
        "vix_spike": "When the market fear indicator (VIX) rises sharply",
        "p/e_ratio": "How expensive stocks are compared to their earnings",
        "duration_risk": "How sensitive bond prices are to interest rate changes",
        "market_momentum": "Whether stock prices are trending up or down",
        "volatility": "How much prices move up and down",
        "rebalancing": "Adjusting your investment mix back to target percentages",
        "macro_signals": "Economic indicators that suggest market direction",
        "risk_parity": "Balancing risk equally across different investments",
        "correlation": "How similarly different investments move together",
        "alpha": "Investment returns above what the market provides",
        "beta": "How much an investment moves relative to the overall market",
        "sharpe_ratio": "Risk-adjusted returns (higher is better)",
        "drawdown": "The largest peak-to-trough decline in portfolio value"
    }

    # Risk communication templates
    RISK_TEMPLATES = {
        "low": "Minimal chance of loss, but growth may be limited. Suitable for near-term goals.",
        "moderate": "Some ups and downs expected, but historically recovers within 2-3 years. Good for medium-term goals.",
        "high": "Significant volatility possible, but higher potential returns over long periods. Best for long-term goals only.",
        "very_high": "Large swings in value are common. Only suitable for long-term goals with high risk tolerance."
    }

    # Risk level explanations
    RISK_LEVEL_EXPLANATIONS = {
        "conservative": "This means your money will have fewer ups and downs, but may grow more slowly.",
        "moderate": "This means your money will have some ups and downs, with moderate growth potential.",
        "aggressive": "This means your money could have big ups and downs, but may grow faster over time.",
        "growth": "This means focusing on investments that could grow a lot, but with more ups and downs."
    }

    # Market regime explanations
    MARKET_REGIME_EXPLANATIONS = {
        "normal_market_conditions": "Market conditions are within normal ranges",
        "high_volatility_crisis": "Markets are experiencing extreme volatility and stress",
        "elevated_volatility": "Markets are more volatile than usual, indicating uncertainty",
        "yield_curve_inversion": "Interest rate patterns suggest potential economic slowdown",
        "flattening_curve": "Interest rate differences are narrowing, which may signal caution",
        "low_volatility_complacency": "Markets are unusually calm, which may indicate complacency"
    }

    # Default confidence scores
    DEFAULT_CONFIDENCE_SCORE = 0.5

    # Default explanations
    DEFAULT_EXPLANATION = "This investment decision was made to help you achieve your financial goals based on current market conditions and your risk profile."
    DEFAULT_RISK_WARNING = "Please carefully consider the risks associated with this investment strategy."


class MistralClientConfig:
    """Configuration for MistralClient fallbacks and defaults"""

    # Goal parsing fallback
    GOAL_PARSING_FALLBACK = {
        "goal_type": "retirement",
        "target_amount": None,
        "time_horizon": None,
        "current_age": None,
        "confidence": 0.1,
        "error": "LLM parsing failed"
    }

    # Signal validation fallback
    SIGNAL_VALIDATION_FALLBACK = {
        "is_valid": True,
        "confidence": 0.5,
        "reasoning": "Default validation due to processing error",
        "risk_level": "medium"
    }

    # Investment plan fallback
    INVESTMENT_PLAN_FALLBACK = {
        "monthly_contribution": 1000,
        "asset_allocation": {
            "stocks": 60,
            "bonds": 35,
            "alternatives": 5
        },
        "milestones": ["Review plan quarterly", "Rebalance annually"],
        "risk_considerations": ["Market volatility may affect short-term performance"]
    }

    # Health check settings
    HEALTH_CHECK_RESPONSE = {
        "status": "healthy",
        "test_response": "OK"
    }


class ConfigManager:
    """Central configuration manager for all agents"""

    def __init__(self):
        self.base_config = AgentConfig()
        self.data_agent = DataAgentConfig()
        self.portfolio_agent = PortfolioAgentConfig()
        self.planner_agent = PlannerAgentConfig()
        self.explainability_agent = ExplainabilityAgentConfig()
        self.mistral_client = MistralClientConfig()

        # Load environment-specific overrides
        self._load_environment_config()

    def _load_environment_config(self):
        """Load environment-specific configuration overrides"""
        env = os.getenv("AGENT_ENVIRONMENT", "development")
        self.base_config.environment = env

        # In production, disable fallbacks by default
        if env == "production":
            self.base_config.use_fallbacks = False
            self.base_config.log_fallback_usage = True

    def should_use_fallbacks(self) -> bool:
        """Check if fallbacks should be used based on environment"""
        return self.base_config.use_fallbacks

    def get_fallback(self, agent_type: str, fallback_type: str, **kwargs) -> Any:
        """Get a specific fallback value for an agent"""
        agent_config = getattr(self, agent_type, None)
        if agent_config is None:
            raise ValueError(f"Unknown agent type: {agent_type}")

        fallback_map = {
            "data_agent": {
                "market_regime": lambda: self.data_agent.MARKET_REGIME_FALLBACK,
                "validation": lambda: self.data_agent.VALIDATION_FALLBACK.copy(),
                "health_check": lambda: self.data_agent.HEALTH_CHECK_FALLBACK.copy(),
            },
            "portfolio_agent": {
                "expected_return": lambda: self.portfolio_agent.DEFAULT_EXPECTED_RETURN,
                "volatility": lambda: self.portfolio_agent.DEFAULT_VOLATILITY,
                "backtest": lambda: self.portfolio_agent.BACKTEST_FALLBACK.copy(),
            },
            "planner_agent": {
                "goal_parsing": lambda: self.planner_agent.GOAL_PARSING_FALLBACK.copy(),
                "default_amount": lambda goal_type: self.planner_agent.DEFAULT_AMOUNTS.get(goal_type, 100000),
                "default_horizon": lambda goal_type: self.planner_agent.DEFAULT_HORIZONS.get(goal_type, 10),
            },
            "explainability_agent": {
                "confidence": lambda: self.explainability_agent.DEFAULT_CONFIDENCE_SCORE,
                "explanation": lambda: self.explainability_agent.DEFAULT_EXPLANATION,
                "risk_warning": lambda: self.explainability_agent.DEFAULT_RISK_WARNING,
            },
            "mistral_client": {
                "goal_parsing": lambda: self.mistral_client.GOAL_PARSING_FALLBACK.copy(),
                "signal_validation": lambda: self.mistral_client.SIGNAL_VALIDATION_FALLBACK.copy(),
                "investment_plan": lambda: self.mistral_client.INVESTMENT_PLAN_FALLBACK.copy(),
            }
        }

        agent_fallbacks = fallback_map.get(agent_type, {})
        fallback_func = agent_fallbacks.get(fallback_type)

        if fallback_func is None:
            raise ValueError(f"Unknown fallback type '{fallback_type}' for agent '{agent_type}'")

        # Call the fallback function with any provided kwargs
        try:
            if kwargs:
                return fallback_func(**kwargs)
            else:
                return fallback_func()
        except TypeError:
            # Fallback function doesn't accept kwargs
            return fallback_func()


# Global configuration instance
config = ConfigManager()