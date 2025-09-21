"""
Dashboard Data Service - Handles saving market data to Supabase for dashboard display
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import uuid

from api.dependencies.db import supabase
from ..shared.models import MarketData, MacroData

logger = logging.getLogger(__name__)


class DashboardDataService:
    """Service for saving and retrieving dashboard market data from Supabase - Single Table Design"""

    @staticmethod
    async def save_market_data(market_data: MarketData, additional_info: Dict[str, Any] = None) -> bool:
        """
        Save market data to dashboard_data table (simplified single table)

        Args:
            market_data: MarketData object
            additional_info: Additional market info (volume, market_cap, etc.)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get additional info if provided
            additional = additional_info or {}

            # Determine asset type based on symbol
            asset_type = DashboardDataService._get_asset_type(market_data.symbol)

            # Prepare data for insertion
            data = {
                "symbol": market_data.symbol,
                "name": additional.get("name", market_data.symbol),
                "asset_type": asset_type,
                "price": float(market_data.price) if market_data.price else 0.0,
                "previous_close": float(market_data.previous_close) if market_data.previous_close else 0.0,
                "change_value": float(market_data.change) if market_data.change else 0.0,
                "change_percent": float(market_data.change_percent) if market_data.change_percent else 0.0,
                "volume": additional.get("volume"),
                "market_cap": additional.get("market_cap"),
                "day_high": additional.get("day_high"),
                "day_low": additional.get("day_low"),
                "year_high": additional.get("year_high"),
                "year_low": additional.get("year_low"),
                "pe_ratio": additional.get("pe_ratio"),
                "dividend_yield": additional.get("dividend_yield"),
                "expense_ratio": additional.get("expense_ratio"),
                "total_assets": additional.get("total_assets"),
                "beta": additional.get("beta"),
                "data_timestamp": market_data.timestamp.isoformat() if market_data.timestamp else datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # Insert or update (upsert) data
            response = supabase.table("dashboard_market_data").upsert(
                data,
                on_conflict="symbol"
            ).execute()

            if response.data:
                logger.info(f"Successfully saved market data for {market_data.symbol}")
                return True
            else:
                logger.error(f"Failed to save market data for {market_data.symbol}: No data returned")
                return False

        except Exception as e:
            logger.error(f"Error saving market data for {market_data.symbol}: {e}")
            return False

    @staticmethod
    def _get_asset_type(symbol: str) -> str:
        """Determine asset type based on symbol"""
        symbol = symbol.upper()

        if symbol in ['ETHE', 'BITO']:
            return 'CRYPTO_ETF'
        elif symbol in ['IEF', 'BND', 'SHY']:
            return 'BOND_ETF'
        elif symbol in ['QQQ', 'SPY', 'VXUS']:
            return 'ETF'
        elif symbol in ['VIX']:
            return 'INDEX'
        elif symbol.endswith('_TREASURY'):
            return 'YIELD'
        else:
            return 'ETF'  # Default

    @staticmethod
    async def save_technical_indicators(symbol: str, indicators: Dict[str, Any]) -> bool:
        """
        Save technical indicators to dashboard_data table (update existing record)

        Args:
            symbol: Stock symbol
            indicators: Dictionary of technical indicators

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update only the technical indicator fields
            update_data = {
                "sma_20": indicators.get("sma_20"),
                "sma_50": indicators.get("sma_50"),
                "sma_200": indicators.get("sma_200"),
                "rsi": indicators.get("rsi"),
                "updated_at": datetime.now().isoformat()
            }

            # Update existing record
            response = supabase.table("dashboard_market_data").update(update_data).eq("symbol", symbol).execute()

            if response.data:
                logger.info(f"Successfully saved technical indicators for {symbol}")
                return True
            else:
                logger.error(f"Failed to save technical indicators for {symbol}")
                return False

        except Exception as e:
            logger.error(f"Error saving technical indicators for {symbol}: {e}")
            return False

    @staticmethod
    async def save_market_context_data(vix_data: Dict[str, Any] = None, treasury_data: Dict[str, Any] = None, market_regime: str = None) -> bool:
        """
        Save market context data (VIX, Treasury yields) to dashboard_data table

        Args:
            vix_data: VIX data dictionary
            treasury_data: Treasury yields dictionary
            market_regime: Current market regime

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            success_count = 0

            # Save VIX data
            if vix_data:
                vix_record = {
                    "symbol": "VIX",
                    "name": "CBOE Volatility Index",
                    "asset_type": "INDEX",
                    "price": float(vix_data.get("vix", 0)),
                    "change_value": float(vix_data.get("vix_change", 0)),
                    "change_percent": float(vix_data.get("vix_change_percent", 0)),
                    "context_data": {
                        "market_regime": market_regime,
                        "spy_volatility": vix_data.get("spy_volatility")
                    },
                    "data_timestamp": vix_data.get("timestamp", datetime.now().isoformat()),
                    "updated_at": datetime.now().isoformat()
                }

                response = supabase.table("dashboard_market_data").upsert(vix_record, on_conflict="symbol").execute()
                if response.data:
                    success_count += 1

            # Save Treasury yields
            if treasury_data:
                # Save 2Y Treasury
                if treasury_data.get("2y_yield") is not None:
                    treasury_2y = {
                        "symbol": "2Y_TREASURY",
                        "name": "2-Year Treasury Yield",
                        "asset_type": "YIELD",
                        "price": float(treasury_data.get("2y_yield", 0)),
                        "data_timestamp": treasury_data.get("timestamp", datetime.now().isoformat()),
                        "updated_at": datetime.now().isoformat()
                    }
                    response = supabase.table("dashboard_market_data").upsert(treasury_2y, on_conflict="symbol").execute()
                    if response.data:
                        success_count += 1

                # Save 10Y Treasury with spread context
                if treasury_data.get("10y_yield") is not None:
                    treasury_10y = {
                        "symbol": "10Y_TREASURY",
                        "name": "10-Year Treasury Yield",
                        "asset_type": "YIELD",
                        "price": float(treasury_data.get("10y_yield", 0)),
                        "context_data": {
                            "2s_10s_spread": treasury_data.get("2s_10s_spread")
                        },
                        "data_timestamp": treasury_data.get("timestamp", datetime.now().isoformat()),
                        "updated_at": datetime.now().isoformat()
                    }
                    response = supabase.table("dashboard_market_data").upsert(treasury_10y, on_conflict="symbol").execute()
                    if response.data:
                        success_count += 1

            logger.info(f"Successfully saved {success_count} market context records")
            return success_count > 0

        except Exception as e:
            logger.error(f"Error saving market context data: {e}")
            return False

    @staticmethod
    async def get_dashboard_data(symbols: List[str] = None) -> Dict[str, Any]:
        """
        Retrieve dashboard data for specified symbols from single table

        Args:
            symbols: List of symbols to retrieve, None for all

        Returns:
            Dictionary containing dashboard data
        """
        try:
            # Build query for dashboard data
            query = supabase.table("dashboard_market_data").select("*").order("updated_at", desc=True)

            if symbols:
                query = query.in_("symbol", symbols)

            response = query.execute()
            all_data = response.data if response.data else []

            # Separate data by type
            etf_data = []
            market_context = {}

            for record in all_data:
                if record.get("asset_type") in ["ETF", "BOND_ETF", "CRYPTO_ETF"]:
                    etf_data.append(record)
                elif record.get("symbol") == "VIX":
                    market_context["vix"] = {
                        "vix": record.get("price", 0),
                        "vix_change": record.get("change_value", 0),
                        "vix_change_percent": record.get("change_percent", 0),
                        "market_regime": record.get("context_data", {}).get("market_regime", "unknown"),
                        "timestamp": record.get("data_timestamp")
                    }
                elif record.get("symbol") in ["2Y_TREASURY", "10Y_TREASURY"]:
                    if "treasury" not in market_context:
                        market_context["treasury"] = {}

                    if record.get("symbol") == "2Y_TREASURY":
                        market_context["treasury"]["2y_yield"] = record.get("price", 0)
                    elif record.get("symbol") == "10Y_TREASURY":
                        market_context["treasury"]["10y_yield"] = record.get("price", 0)
                        market_context["treasury"]["2s_10s_spread"] = record.get("context_data", {}).get("2s_10s_spread", 0)

            return {
                "etf_data": etf_data,
                "market_context": market_context,
                "timestamp": datetime.now().isoformat(),
                "total_records": len(all_data)
            }

        except Exception as e:
            logger.error(f"Error retrieving dashboard data: {e}")
            return {"error": str(e)}

    @staticmethod
    async def save_macro_data(macro_data_list: List[MacroData]) -> bool:
        """
        Save macro-economic data to dashboard_macro_data table

        Args:
            macro_data_list: List of MacroData objects

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not macro_data_list:
                return True

            success_count = 0
            for macro_data in macro_data_list:
                data = {
                    "indicator_name": macro_data.indicator,
                    "value": float(macro_data.value) if macro_data.value else 0.0,
                    "date": macro_data.date.date() if macro_data.date else datetime.now().date(),
                    "source": "FRED",
                    "metadata": {
                        "frequency": macro_data.frequency if hasattr(macro_data, 'frequency') else "unknown"
                    },
                    "created_at": datetime.now().isoformat()
                }

                response = supabase.table("dashboard_macro_data").upsert(
                    data,
                    on_conflict="indicator_name,date"
                ).execute()

                if response.data:
                    success_count += 1

            logger.info(f"Successfully saved {success_count}/{len(macro_data_list)} macro data records")
            return success_count > 0

        except Exception as e:
            logger.error(f"Error saving macro data: {e}")
            return False

    @staticmethod
    async def save_user_watchlist(user_id: str, symbols: List[str]) -> bool:
        """
        Save user's watchlist symbols

        Args:
            user_id: User ID
            symbols: List of symbols to watch

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data = {
                "user_id": user_id,
                "watchlist_symbols": symbols,
                "updated_at": datetime.now().isoformat()
            }

            response = supabase.table("user_dashboard_settings").upsert(
                data,
                on_conflict="user_id"
            ).execute()

            if response.data:
                logger.info(f"Successfully saved watchlist for user {user_id}")
                return True
            else:
                logger.error(f"Failed to save watchlist for user {user_id}")
                return False

        except Exception as e:
            logger.error(f"Error saving user watchlist: {e}")
            return False