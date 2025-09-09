import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from .agents import DataAgent, MarketData, MacroData

logger = logging.getLogger(__name__)

data_agent = DataAgent()

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