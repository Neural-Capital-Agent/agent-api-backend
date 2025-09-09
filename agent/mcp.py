from mcp.server.fastmcp import FastMCP
import os
import requests
import asyncio
from dotenv import load_dotenv
from .tools import (
    fetch_market_data_tool,
    fetch_all_market_data_tool,
    fetch_macro_data_tool,
    fetch_volatility_data_tool,
    fetch_technical_indicators_tool,
    fetch_treasury_yields_tool,
    get_market_momentum_signals_tool,
    data_health_check_tool,
    get_asset_universe_tool,
    get_macro_indicators_tool
)

load_dotenv()
mcp = FastMCP("Neural Capital Data Agent")


@mcp.tool()
def get_economy_context() -> dict:
    """Get general economy context from existing API endpoint."""
    url="http://localhost:8000/api/v1/economy"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to retrieve economy context"}


@mcp.tool()
def get_stocks_context() -> dict:
    """Get general stocks context from existing API endpoint."""
    url="http://localhost:8000/api/v1/stocks"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to retrieve stocks context"}


@mcp.tool()
def fetch_market_data(ticker: str, start_date: str = None, end_date: str = None) -> dict:
    """
    Fetch real-time market data for a specific ticker.
    
    Args:
        ticker: Stock symbol (e.g., 'SPY', 'QQQ', 'BTC-USD')
        start_date: Optional start date for historical data (YYYY-MM-DD)
        end_date: Optional end date for historical data (YYYY-MM-DD)
    
    Returns:
        Dictionary containing current price, change, and metadata
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fetch_market_data_tool(ticker, start_date, end_date))
        loop.close()
        return result
    except Exception as e:
        return {"error": f"Failed to fetch market data: {str(e)}"}


@mcp.tool()
def fetch_all_market_data() -> list:
    """
    Fetch market data for all assets in the Neural Capital universe.
    Includes equities (SPY, QQQ, VXUS), fixed income (SGOV, SHY, IEF, BND, TIP), 
    alternatives (GLD), and crypto (BTC-USD, ETH-USD).
    
    Returns:
        List of dictionaries containing market data for all assets
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fetch_all_market_data_tool())
        loop.close()
        return result
    except Exception as e:
        return [{"error": f"Failed to fetch all market data: {str(e)}"}]


@mcp.tool()
def fetch_macro_data(indicator: str, date_range: int = 30) -> list:
    """
    Fetch macro-economic data from FRED API.
    
    Args:
        indicator: Economic indicator (CPI, 10Y_TREASURY, FED_FUNDS_RATE, UNEMPLOYMENT, VIX, PMI, DXY)
        date_range: Number of days to look back for data (default: 30)
    
    Returns:
        List of dictionaries containing macro-economic data points
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fetch_macro_data_tool(indicator, date_range))
        loop.close()
        return result
    except Exception as e:
        return [{"error": f"Failed to fetch macro data: {str(e)}"}]


@mcp.tool()
def fetch_volatility_data() -> dict:
    """
    Fetch VIX and other volatility indicators to gauge market fear and sentiment.
    
    Returns:
        Dictionary containing VIX price, change, and timestamp
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fetch_volatility_data_tool())
        loop.close()
        return result
    except Exception as e:
        return {"error": f"Failed to fetch volatility data: {str(e)}"}


@mcp.tool()
def fetch_technical_indicators(ticker: str, period: str = "1y") -> dict:
    """
    Fetch technical indicators including SMA (20, 50, 200), RSI, and current price.
    
    Args:
        ticker: Stock symbol to analyze
        period: Time period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    
    Returns:
        Dictionary containing technical indicators and current price
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fetch_technical_indicators_tool(ticker, period))
        loop.close()
        return result
    except Exception as e:
        return {"error": f"Failed to fetch technical indicators: {str(e)}"}


@mcp.tool()
def fetch_treasury_yields() -> dict:
    """
    Fetch Treasury yields and calculate the 2s-10s spread for yield curve analysis.
    
    Returns:
        Dictionary containing 2Y yield, 10Y yield, and 2s-10s spread
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fetch_treasury_yields_tool())
        loop.close()
        return result
    except Exception as e:
        return {"error": f"Failed to fetch Treasury yields: {str(e)}"}


@mcp.tool()
def get_market_momentum_signals() -> dict:
    """
    Generate market momentum signals based on S&P 500 technical indicators.
    Analyzes SPY price relative to 200-day moving average and RSI.
    
    Returns:
        Dictionary containing momentum signal (bullish/bearish) and supporting data
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_market_momentum_signals_tool())
        loop.close()
        return result
    except Exception as e:
        return {"error": f"Failed to generate momentum signals: {str(e)}"}


@mcp.tool()
def data_health_check() -> dict:
    """
    Perform health check of all data sources (Yahoo Finance, FRED API).
    
    Returns:
        Dictionary showing health status of each data source
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(data_health_check_tool())
        loop.close()
        return result
    except Exception as e:
        return {"error": f"Failed to perform health check: {str(e)}"}


@mcp.tool()
def get_asset_universe() -> dict:
    """
    Get the complete Neural Capital asset universe organized by category.
    
    Returns:
        Dictionary containing equities, fixed income, alternatives, and crypto assets
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_asset_universe_tool())
        loop.close()
        return result
    except Exception as e:
        return {"error": f"Failed to get asset universe: {str(e)}"}


@mcp.tool()
def get_macro_indicators() -> dict:
    """
    Get available macro-economic indicators and their FRED codes.
    
    Returns:
        Dictionary mapping indicator names to FRED API codes
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_macro_indicators_tool())
        loop.close()
        return result
    except Exception as e:
        return {"error": f"Failed to get macro indicators: {str(e)}"}
