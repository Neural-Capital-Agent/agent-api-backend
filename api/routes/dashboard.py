"""
Dashboard API routes for market data display
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from agent.core.data_agent import DataAgent
from agent.core.dashboard_data_service import DashboardDataService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Dashboard"], prefix="/dashboard")

# Initialize data agent
data_agent = DataAgent()


@router.get("/etfs")
async def get_dashboard_etfs(
    refresh: Optional[bool] = Query(False, description="Whether to refresh data from live sources"),
    save: Optional[bool] = Query(True, description="Whether to save refreshed data to database")
):
    """
    Get market data for dashboard ETFs.

    Args:
        refresh: If True, fetch fresh data from Yahoo Finance
        save: If True, save refreshed data to database

    Returns:
        Dictionary containing ETF market data
    """
    try:
        if refresh:
            # Fetch fresh data and optionally save to database
            result = await data_agent.fetch_dashboard_etfs(save_to_db=save)
        else:
            # Get data from database
            result = await data_agent.get_dashboard_data()

        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting dashboard ETFs: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "dashboard_etfs_failed", "message": str(e)}
        )


@router.get("/etfs/{symbol}")
async def get_single_etf(
    symbol: str = Path(..., description="ETF symbol (QQQ, SPY, etc.)"),
    refresh: Optional[bool] = Query(False, description="Whether to refresh data from live sources")
):
    """
    Get market data for a specific ETF.

    Args:
        symbol: ETF symbol (QQQ, SPY, ETH, BTC, etc.)
        refresh: If True, fetch fresh data

    Returns:
        Dictionary containing single ETF data
    """
    try:
        if refresh:
            # Get actual ticker for the symbol
            actual_ticker = data_agent.ticker_mapping.get(symbol.upper(), symbol.upper())

            # Fetch fresh market data
            market_data = await data_agent.fetch_market_data(actual_ticker)
            additional_info = await data_agent._get_additional_etf_info(actual_ticker)

            # Save to database
            await DashboardDataService.save_market_data(
                market_data,
                {**additional_info, "name": data_agent.dashboard_etfs.get(symbol.upper(), symbol)}
            )

            result = {
                "symbol": symbol.upper(),
                "ticker": actual_ticker,
                "name": data_agent.dashboard_etfs.get(symbol.upper(), symbol),
                "market_data": market_data.__dict__,
                "additional_info": additional_info
            }
        else:
            # Get from database
            dashboard_data = await DashboardDataService.get_dashboard_data([symbol.upper()])
            etf_data_list = dashboard_data.get("etf_data", [])

            if not etf_data_list:
                raise HTTPException(
                    status_code=404,
                    detail={"error": "etf_not_found", "message": f"No data found for {symbol}"}
                )

            result = etf_data_list[0]

        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ETF {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "etf_fetch_failed", "message": str(e)}
        )


@router.get("/market-overview")
async def get_market_overview(refresh: Optional[bool] = Query(False)):
    """
    Get comprehensive market overview including VIX, treasury yields, and key indicators.

    Args:
        refresh: If True, fetch fresh data from live sources

    Returns:
        Dictionary containing market overview data
    """
    try:
        if refresh:
            # Fetch fresh volatility data
            vix_data = await data_agent.fetch_volatility_data()

            # Fetch treasury yields
            treasury_data = await data_agent.fetch_treasury_yields()

            # Fetch market momentum
            momentum_data = await data_agent.get_market_momentum_signals()

            # Save to database
            if vix_data or treasury_data:
                market_regime = data_agent._determine_market_regime(None, vix_data or {}, treasury_data or {})
                await DashboardDataService.save_market_context_data(
                    vix_data=vix_data,
                    treasury_data=treasury_data,
                    market_regime=market_regime
                )

            result = {
                "volatility": vix_data,
                "treasury_yields": treasury_data,
                "market_momentum": momentum_data,
                "market_regime": data_agent._determine_market_regime(None, vix_data, treasury_data)
            }
        else:
            # Get from database
            dashboard_data = await DashboardDataService.get_dashboard_data()
            market_context = dashboard_data.get("market_context", {})
            result = {
                "volatility": market_context.get("vix", {}),
                "treasury_yields": market_context.get("treasury", {}),
                "market_regime": market_context.get("vix", {}).get("market_regime", "unknown")
            }

        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "market_overview_failed", "message": str(e)}
        )


@router.get("/technical-indicators/{symbol}")
async def get_technical_indicators(
    symbol: str = Path(..., description="ETF symbol"),
    period: Optional[str] = Query("1y", description="Time period for technical analysis")
):
    """
    Get technical indicators for a specific ETF.

    Args:
        symbol: ETF symbol
        period: Time period (1y, 6m, 3m, etc.)

    Returns:
        Dictionary containing technical indicators
    """
    try:
        # Get actual ticker
        actual_ticker = data_agent.ticker_mapping.get(symbol.upper(), symbol.upper())

        # Fetch technical indicators
        indicators = await data_agent.fetch_technical_indicators(actual_ticker, period)

        if not indicators:
            raise HTTPException(
                status_code=404,
                detail={"error": "no_technical_data", "message": f"No technical data available for {symbol}"}
            )

        # Save to database
        await DashboardDataService.save_technical_indicators(actual_ticker, indicators)

        return {
            "status": "success",
            "symbol": symbol.upper(),
            "ticker": actual_ticker,
            "data": indicators,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting technical indicators for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "technical_indicators_failed", "message": str(e)}
        )


@router.post("/refresh")
async def refresh_dashboard_data():
    """
    Refresh all dashboard data by fetching from live sources and saving to database.

    Returns:
        Status of the refresh operation
    """
    try:
        result = await data_agent.refresh_dashboard_data()

        return {
            "status": "success",
            "message": "Dashboard data refreshed successfully",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error refreshing dashboard data: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "refresh_failed", "message": str(e)}
        )


@router.get("/")
async def get_full_dashboard_data(
    user_id: Optional[str] = Query(None, description="User ID for personalized data"),
    refresh: Optional[bool] = Query(False, description="Whether to refresh data")
):
    """
    Get complete dashboard data including ETFs, market overview, and user preferences.

    Args:
        user_id: Optional user ID for personalized dashboard
        refresh: If True, refresh data from live sources

    Returns:
        Complete dashboard data
    """
    try:
        if refresh:
            # Refresh all data
            await data_agent.refresh_dashboard_data()

        # Get comprehensive dashboard data
        dashboard_data = await data_agent.get_dashboard_data(user_id)

        return {
            "status": "success",
            "data": dashboard_data,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting full dashboard data: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "dashboard_data_failed", "message": str(e)}
        )


@router.post("/watchlist/{user_id}")
async def save_user_watchlist(
    user_id: str = Path(..., description="User ID"),
    symbols: List[str] = []
):
    """
    Save user's custom watchlist symbols.

    Args:
        user_id: User ID
        symbols: List of symbols to watch

    Returns:
        Success status
    """
    try:
        success = await DashboardDataService.save_user_watchlist(user_id, symbols)

        if not success:
            raise HTTPException(
                status_code=500,
                detail={"error": "watchlist_save_failed", "message": "Failed to save watchlist"}
            )

        return {
            "status": "success",
            "message": "Watchlist saved successfully",
            "user_id": user_id,
            "symbols": symbols,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving watchlist for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "watchlist_save_failed", "message": str(e)}
        )


# Scheduler endpoints removed - using manual refresh only