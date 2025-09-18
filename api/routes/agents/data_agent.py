"""
Data Agent API Routes
Handles market data, macro indicators, volatility, and technical analysis.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime
import logging

from agent.data_agent import DataAgent
from .shared import get_user_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Data Agent"], prefix="/data")

# Initialize agent
data_agent = DataAgent()


@router.get("/health")
async def data_agent_health():
    """Check Data Agent health and data source availability."""
    try:
        health_status = await data_agent.health_check()
        return {
            "agent": "data_agent",
            "status": "healthy",
            "data_sources": health_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Data agent health check failed: {e}")
        return {
            "agent": "data_agent",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/market/{ticker}")
async def get_market_data(
    ticker: str,
    user_id: str = Depends(get_user_id),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Fetch real-time market data for a specific ticker."""
    try:
        logger.info(f"Fetching market data for {ticker} (user: {user_id})")

        market_data = await data_agent.fetch_market_data(ticker, start_date, end_date)

        return {
            "success": True,
            "agent": "data_agent",
            "ticker": ticker,
            "data": {
                "symbol": market_data.symbol,
                "price": market_data.price,
                "previous_close": market_data.previous_close,
                "change": market_data.change,
                "change_percent": market_data.change_percent,
                "timestamp": market_data.timestamp.isoformat()
            },
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error fetching market data for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "market_data_fetch_failed", "message": str(e), "ticker": ticker}
        )


@router.get("/market")
async def get_all_market_data(user_id: str = Depends(get_user_id)):
    """Fetch market data for all assets in the universe."""
    try:
        market_data_list = await data_agent.fetch_all_market_data()

        return {
            "success": True,
            "agent": "data_agent",
            "total_assets": len(market_data_list),
            "data": [
                {
                    "symbol": data.symbol,
                    "price": data.price,
                    "previous_close": data.previous_close,
                    "change": data.change,
                    "change_percent": data.change_percent,
                    "timestamp": data.timestamp.isoformat()
                }
                for data in market_data_list
            ],
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error fetching all market data: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "market_data_fetch_failed", "message": str(e)}
        )


@router.get("/macro/{indicator}")
async def get_macro_data(
    indicator: str,
    user_id: str = Depends(get_user_id),
    date_range: int = Query(30, description="Number of days to look back")
):
    """Fetch macro-economic data from FRED API."""
    try:
        macro_data = await data_agent.fetch_macro_data(indicator, date_range)

        return {
            "success": True,
            "agent": "data_agent",
            "indicator": indicator,
            "date_range": date_range,
            "data_points": len(macro_data),
            "data": [
                {
                    "indicator": data.indicator,
                    "value": data.value,
                    "date": data.date.isoformat(),
                    "frequency": data.frequency
                }
                for data in macro_data
            ],
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error fetching macro data for {indicator}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "macro_data_fetch_failed", "message": str(e), "indicator": indicator}
        )


@router.get("/volatility")
async def get_volatility_data(user_id: str = Depends(get_user_id)):
    """Fetch VIX and other volatility indicators."""
    try:
        volatility_data = await data_agent.fetch_volatility_data()

        return {
            "success": True,
            "agent": "data_agent",
            "volatility_data": volatility_data,
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error fetching volatility data: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "volatility_data_fetch_failed", "message": str(e)}
        )


@router.get("/technical/{ticker}")
async def get_technical_indicators(
    ticker: str,
    user_id: str = Depends(get_user_id),
    period: str = Query("1y", description="Time period for historical data")
):
    """Fetch technical indicators for a ticker."""
    try:
        technical_data = await data_agent.fetch_technical_indicators(ticker, period)

        return {
            "success": True,
            "agent": "data_agent",
            "ticker": ticker,
            "period": period,
            "indicators": technical_data,
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error fetching technical indicators for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "technical_indicators_failed", "message": str(e), "ticker": ticker}
        )