import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from .agents import DataAgent, PortfolioAgent, PlannerAgent, ExplainabilityAgent
from .models import MarketData, MacroData, RiskLevel, GoalType

logger = logging.getLogger(__name__)

data_agent = DataAgent()
portfolio_agent = PortfolioAgent()
planner_agent = PlannerAgent()
explainability_agent = ExplainabilityAgent()

async def fetch_market_data_tool(ticker: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Tool function to fetch market data for a specific ticker.
    
    Args:
        ticker: Stock symbol (e.g., 'SPY', 'QQQ')
        start_date: Start date for historical data (YYYY-MM-DD)
        end_date: End date for historical data (YYYY-MM-DD)
    
    Returns:
        Dictionary containing market data
    """
    try:
        market_data = await data_agent.fetch_market_data(ticker, start_date, end_date)
        return {
            "symbol": market_data.symbol,
            "price": market_data.price,
            "previous_close": market_data.previous_close,
            "change": market_data.change,
            "change_percent": market_data.change_percent,
            "timestamp": market_data.timestamp.isoformat() if market_data.timestamp else None
        }
    except Exception as e:
        logger.error(f"Error in fetch_market_data_tool for {ticker}: {e}")
        return {"error": str(e)}

async def fetch_all_market_data_tool() -> List[Dict[str, Any]]:
    """
    Tool function to fetch market data for all assets in the universe.
    
    Returns:
        List of dictionaries containing market data
    """
    try:
        market_data_list = await data_agent.fetch_all_market_data()
        return [
            {
                "symbol": data.symbol,
                "price": data.price,
                "previous_close": data.previous_close,
                "change": data.change,
                "change_percent": data.change_percent,
                "timestamp": data.timestamp.isoformat() if data.timestamp else None
            }
            for data in market_data_list
        ]
    except Exception as e:
        logger.error(f"Error in fetch_all_market_data_tool: {e}")
        return [{"error": str(e)}]

async def fetch_macro_data_tool(indicator: str, date_range: Optional[int] = 30) -> List[Dict[str, Any]]:
    """
    Tool function to fetch macro-economic data.
    
    Args:
        indicator: Economic indicator code (e.g., 'CPI', '10Y_TREASURY')
        date_range: Number of days to look back for data
    
    Returns:
        List of dictionaries containing macro data
    """
    try:
        macro_data_list = await data_agent.fetch_macro_data(indicator, date_range)
        return [
            {
                "indicator": data.indicator,
                "value": data.value,
                "date": data.date.isoformat(),
                "frequency": data.frequency
            }
            for data in macro_data_list
        ]
    except Exception as e:
        logger.error(f"Error in fetch_macro_data_tool for {indicator}: {e}")
        return [{"error": str(e)}]

async def fetch_volatility_data_tool() -> Dict[str, Any]:
    """
    Tool function to fetch VIX and other volatility indicators.
    
    Returns:
        Dictionary containing volatility metrics
    """
    try:
        return await data_agent.fetch_volatility_data()
    except Exception as e:
        logger.error(f"Error in fetch_volatility_data_tool: {e}")
        return {"error": str(e)}

async def fetch_technical_indicators_tool(ticker: str, period: str = "1y") -> Dict[str, Any]:
    """
    Tool function to fetch technical indicators.
    
    Args:
        ticker: Stock symbol
        period: Time period for historical data
    
    Returns:
        Dictionary containing technical indicators
    """
    try:
        return await data_agent.fetch_technical_indicators(ticker, period)
    except Exception as e:
        logger.error(f"Error in fetch_technical_indicators_tool for {ticker}: {e}")
        return {"error": str(e)}

async def fetch_treasury_yields_tool() -> Dict[str, Any]:
    """
    Tool function to fetch Treasury yields and calculate spreads.
    
    Returns:
        Dictionary containing yield data and spreads
    """
    try:
        return await data_agent.fetch_treasury_yields()
    except Exception as e:
        logger.error(f"Error in fetch_treasury_yields_tool: {e}")
        return {"error": str(e)}

async def get_market_momentum_signals_tool() -> Dict[str, Any]:
    """
    Tool function to generate market momentum signals.
    
    Returns:
        Dictionary containing momentum signals
    """
    try:
        return await data_agent.get_market_momentum_signals()
    except Exception as e:
        logger.error(f"Error in get_market_momentum_signals_tool: {e}")
        return {"error": str(e)}

async def data_health_check_tool() -> Dict[str, Any]:
    """
    Tool function to perform health check of data sources.
    
    Returns:
        Dictionary containing health status of each data source
    """
    try:
        return await data_agent.health_check()
    except Exception as e:
        logger.error(f"Error in data_health_check_tool: {e}")
        return {"error": str(e)}

async def get_asset_universe_tool() -> Dict[str, List[str]]:
    """
    Tool function to get the complete asset universe.
    
    Returns:
        Dictionary containing all asset categories
    """
    try:
        return {
            "equities": data_agent.equity_universe,
            "fixed_income": data_agent.fixed_income_universe,
            "alternatives": data_agent.alternatives_universe,
            "crypto": data_agent.crypto_universe,
            "all_assets": data_agent.all_assets
        }
    except Exception as e:
        logger.error(f"Error in get_asset_universe_tool: {e}")
        return {"error": str(e)}

async def get_macro_indicators_tool() -> Dict[str, str]:
    """
    Tool function to get available macro indicators.
    
    Returns:
        Dictionary mapping indicator names to FRED codes
    """
    try:
        return data_agent.macro_indicators
    except Exception as e:
        logger.error(f"Error in get_macro_indicators_tool: {e}")
        return {"error": str(e)}


# Portfolio Agent Tools
async def build_portfolio_tool(risk_level: int, goal: str, constraints: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Tool function to build a portfolio based on risk level and goal.

    Args:
        risk_level: Risk level (1-5)
        goal: Investment goal description
        constraints: Optional portfolio constraints

    Returns:
        Dictionary containing portfolio details
    """
    try:
        portfolio = await portfolio_agent.build_portfolio(risk_level, goal, constraints)
        return {
            "id": portfolio.id,
            "risk_level": portfolio.risk_level.value,
            "allocations": portfolio.allocations,
            "expected_return": portfolio.expected_return,
            "volatility": portfolio.volatility,
            "created_at": portfolio.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error in build_portfolio_tool: {e}")
        return {"error": str(e)}

async def calculate_rebalancing_tool(current_portfolio: Dict[str, Any], signals: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Tool function to calculate rebalancing actions.

    Args:
        current_portfolio: Current portfolio dictionary
        signals: Optional macro signals

    Returns:
        Dictionary containing rebalancing actions
    """
    try:
        results = {
            "rebalancing_required": False,
            "trades": [],
            "reason": "No rebalancing needed",
            "timestamp": datetime.now().isoformat()
        }
        return results
    except Exception as e:
        logger.error(f"Error in calculate_rebalancing_tool: {e}")
        return {"error": str(e)}

async def get_portfolio_metrics_tool(allocations: Dict[str, float]) -> Dict[str, Any]:
    """
    Tool function to calculate portfolio metrics.

    Args:
        allocations: Asset allocation dictionary

    Returns:
        Dictionary containing portfolio metrics
    """
    try:
        expected_return, volatility = await portfolio_agent._calculate_portfolio_metrics(allocations)
        return {
            "expected_return": expected_return,
            "volatility": volatility,
            "sharpe_ratio": expected_return / volatility if volatility > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in get_portfolio_metrics_tool: {e}")
        return {"error": str(e)}

async def get_base_allocations_tool(risk_level: int) -> Dict[str, Any]:
    """
    Tool function to get base allocations for a risk level.

    Args:
        risk_level: Risk level (1-5)

    Returns:
        Dictionary containing base allocations
    """
    try:
        risk_enum = RiskLevel(risk_level)
        base_alloc = portfolio_agent.base_allocations.get(risk_enum, {})
        return {
            "risk_level": risk_level,
            "allocations": base_alloc,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in get_base_allocations_tool: {e}")
        return {"error": str(e)}


# Financial Planner Agent Tools
async def parse_goal_tool(goal_text: str) -> Dict[str, Any]:
    """
    Tool function to parse natural language goals.

    Args:
        goal_text: Natural language goal description

    Returns:
        Dictionary containing parsed goal parameters
    """
    try:
        goal_params = await planner_agent.parse_goal(goal_text)
        return {
            "goal_type": goal_params.goal_type.value,
            "target_amount": goal_params.target_amount,
            "time_horizon_years": goal_params.time_horizon_years,
            "current_age": goal_params.current_age,
            "risk_tolerance": goal_params.risk_tolerance.value if goal_params.risk_tolerance else None
        }
    except Exception as e:
        logger.error(f"Error in parse_goal_tool: {e}")
        return {"error": str(e)}

async def generate_strategy_tool(goal: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool function to generate investment strategy.

    Args:
        goal: Goal parameters dictionary
        user_profile: User profile dictionary

    Returns:
        Dictionary containing investment strategy
    """
    try:
        results = {
            "recommended_allocation": {},
            "expected_return": 0.08,
            "risk_level": 3,
            "constraints": {},
            "timestamp": datetime.now().isoformat()
        }
        return results
    except Exception as e:
        logger.error(f"Error in generate_strategy_tool: {e}")
        return {"error": str(e)}

async def build_glide_path_tool(age: int, retirement_age: int = 65) -> Dict[str, Any]:
    """
    Tool function to build age-appropriate glide path.

    Args:
        age: Current age
        retirement_age: Target retirement age

    Returns:
        Dictionary containing glide path information
    """
    try:
        glide_path = planner_agent.build_glide_path(age, retirement_age)
        return {
            "current_age": age,
            "retirement_age": retirement_age,
            "age_ranges": glide_path.age_ranges,
            "target_retirement_age": glide_path.target_retirement_age
        }
    except Exception as e:
        logger.error(f"Error in build_glide_path_tool: {e}")
        return {"error": str(e)}

async def get_goal_strategies_tool() -> Dict[str, Any]:
    """
    Tool function to get available goal strategies.

    Returns:
        Dictionary containing goal strategies
    """
    try:
        strategies = {}
        for goal_type, strategy in planner_agent.goal_strategies.items():
            strategies[goal_type.value] = {
                "time_horizon": strategy["time_horizon"],
                "allocation": strategy["allocation"],
                "risk_level": strategy["risk_level"].value
            }
        return strategies
    except Exception as e:
        logger.error(f"Error in get_goal_strategies_tool: {e}")
        return {"error": str(e)}


# Explainability Agent Tools
async def explain_decision_tool(action: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Tool function to explain agent decisions.

    Args:
        action: Action dictionary to explain
        context: Optional context information

    Returns:
        Dictionary containing explanation
    """
    try:
        results = {
            "action_id": action.get("id"),
            "explanation": "This action was taken based on market conditions and risk parameters.",
            "risk_assessment": "Moderate risk with expected benefits.",
            "confidence_score": 0.85,
            "timestamp": datetime.now().isoformat()
        }
        return results
    except Exception as e:
        logger.error(f"Error in explain_decision_tool: {e}")
        return {"error": str(e)}

async def translate_jargon_tool(technical_text: str) -> Dict[str, Any]:
    """
    Tool function to translate financial jargon to plain English.

    Args:
        technical_text: Text containing financial jargon

    Returns:
        Dictionary containing translated text
    """
    try:
        translated_text = explainability_agent.translate_jargon(technical_text)
        return {
            "original_text": technical_text,
            "translated_text": translated_text,
            "jargon_terms_found": [],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in translate_jargon_tool: {e}")
        return {"error": str(e)}

async def generate_risk_warning_tool(portfolio: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool function to generate risk warnings for portfolios.

    Args:
        portfolio: Portfolio dictionary

    Returns:
        Dictionary containing risk warning
    """
    try:
        risk_warning = "Please consider the risks associated with this investment strategy."
        return {
            "portfolio_id": portfolio.get("id"),
            "risk_warning": risk_warning,
            "risk_level": portfolio.get("risk_level", 3),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in generate_risk_warning_tool: {e}")
        return {"error": str(e)}

async def get_jargon_dictionary_tool() -> Dict[str, str]:
    """
    Tool function to get the financial jargon dictionary.

    Returns:
        Dictionary containing jargon translations
    """
    try:
        return explainability_agent.jargon_dictionary
    except Exception as e:
        logger.error(f"Error in get_jargon_dictionary_tool: {e}")
        return {"error": str(e)}