from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
import requests
import uuid

import yfinance as yf
import pandas as pd

from utils.yahoo import yahoo
from utils.polygon import polygon
from .dashboard_data_service import DashboardDataService

# Set up logger
logger = logging.getLogger(__name__)

# Use real FRED API with fallback for missing API keys
try:
    from utils.fred_real import fred
    logger.info("Using real FRED API")
except (ImportError, ValueError) as e:
    # Fallback to mock FRED if real API not available or API key missing
    logger.warning(f"Real FRED API not available ({e}), using mock fallback")
    from utils.fred import fred
from ..shared.models import MarketData, MacroData, MacroSignal, MacroSignals
from ..shared.config import config
from ..shared.shared import BaseAgent, ErrorHandler, get_current_timestamp, safe_get, safe_coral_invoke
# LLM imports commented out for pure data retrieval focus
# try:
#     from .mistral_client import mistral_client
# except ImportError:
#     mistral_client = None

logger = logging.getLogger(__name__)


class DataAgent(BaseAgent):
    """
    Data Agent responsible for collecting and providing financial data.
    Focuses purely on data retrieval from external sources.
    LLM validation capabilities are commented out to maintain pure data focus.
    Provides real-time market prices and macro-economic data to other agents.
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555"):
        super().__init__(coral_server_url, "data_agent")

        # Load configuration instead of hardcoded values
        self.equity_universe = config.data_agent.EQUITY_UNIVERSE
        self.fixed_income_universe = config.data_agent.FIXED_INCOME_UNIVERSE
        self.alternatives_universe = config.data_agent.ALTERNATIVES_UNIVERSE
        self.crypto_universe = config.data_agent.CRYPTO_UNIVERSE

        self.all_assets = (
            self.equity_universe +
            self.fixed_income_universe +
            self.alternatives_universe +
            self.crypto_universe
        )

        self.macro_indicators = config.data_agent.MACRO_INDICATORS

        # Dashboard ETFs - your requested list
        self.dashboard_etfs = {
            "QQQ": "Invesco QQQ Trust",
            "ETH": "Grayscale Ethereum Mini Trust ETF",  # Using ETHE as ticker
            "SPY": "SPDR S&P 500 ETF",
            "VXUS": "Vanguard Total International Stock Index Fund ETF Shares",
            "IEF": "iShares 7-10 Year Treasury Bond ETF",
            "BTC": "Grayscale Bitcoin Mini Trust ETF",  # Using BITO as ticker
            "BND": "Vanguard Total Bond Market Index Fund",
            "SHY": "iShares 1-3 Year Treasury Bond ETF"
        }

        # Map display names to actual tickers
        self.ticker_mapping = {
            "ETH": "ETHE",  # Grayscale Ethereum Mini Trust ETF
            "BTC": "BITO"   # ProShares Bitcoin Strategy ETF
        }

        self.update_frequencies = {
            "daily": ["market_data", "vix", "yield_curve", "credit_spreads", "dxy"],
            "monthly": ["cpi", "unemployment", "fed_funds", "pmi", "equity_valuations"]
        }

    async def fetch_market_data(self, ticker: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> MarketData:
        """
        Fetch real-time market data for a specific ticker.

        Args:
            ticker: Stock symbol (e.g., 'SPY', 'QQQ')
            start_date: Start date for historical data (YYYY-MM-DD)
            end_date: End date for historical data (YYYY-MM-DD)

        Returns:
            MarketData object containing price and metadata
        """
        try:
            stock_data = yahoo.fetch_stock_data(ticker)

            return MarketData(
                symbol=safe_get(stock_data, "symbol", ticker),
                price=safe_get(stock_data, "current_price", 0),
                previous_close=safe_get(stock_data, "price", 0),
                change=safe_get(stock_data, "change", 0),
                change_percent=safe_get(stock_data, "changePercent", 0),
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to fetch market data for {ticker}: {e}")
            # Don't use fallback - let the error propagate up
            raise Exception(f"Market data fetch failed for {ticker}: {str(e)}")

    async def fetch_all_market_data(self) -> List[MarketData]:
        """
        Fetch market data for all assets in the universe.

        Returns:
            List of MarketData objects
        """
        market_data = []
        for ticker in self.all_assets:
            try:
                data = await self.fetch_market_data(ticker)
                market_data.append(data)
            except Exception as e:
                logger.error(f"Failed to fetch data for {ticker}: {e}")
                continue

        return market_data

    async def fetch_macro_data(self, indicator: str, date_range: Optional[int] = 30) -> List[MacroData]:
        """
        Fetch macro-economic data from FRED API.

        Args:
            indicator: Economic indicator code (e.g., 'CPI', '10Y_TREASURY')
            date_range: Number of days to look back for data

        Returns:
            List of MacroData objects
        """
        try:
            if indicator not in self.macro_indicators:
                raise ValueError(f"Unknown indicator: {indicator}")

            fred_code = self.macro_indicators[indicator]
            # fred.get_fred_data is async in the real client
            try:
                data = await fred.get_fred_data(fred_code)
            except TypeError:
                # Fallback if fred is the sync shim (not expected) - call directly
                data = fred.get_fred_data(fred_code)

            macro_data = []
            if data:
                for entry in data:
                    macro_data.append(MacroData(
                        indicator=indicator,
                        value=entry.get("value", 0),
                        date=datetime.fromisoformat(entry.get("date", get_current_timestamp())),
                        frequency="daily"
                    ))

            return macro_data
        except Exception as e:
            logger.error(f"Error fetching macro data for {indicator}: {e}")
            raise

    async def fetch_volatility_data(self) -> Dict[str, float]:
        """
        Fetch VIX and other volatility indicators.

        Returns:
            Dictionary containing volatility metrics
        """
        try:
            vix_data = await self.fetch_market_data("^VIX")

            # Only return real data - no defaults
            if not vix_data or (vix_data.price == 0 and vix_data.previous_close == 0):
                raise Exception("No real VIX data available from Yahoo Finance")

            vix_price = vix_data.price if vix_data.price is not None and vix_data.price > 0 else vix_data.previous_close
            if not vix_price or vix_price <= 0:
                raise Exception("Invalid VIX data - price is 0 or None")

            return {
                "vix": vix_price,
                "vix_change": vix_data.change or 0,
                "vix_change_percent": vix_data.change_percent or 0,
                "timestamp": get_current_timestamp()
            }
        except Exception as e:
            logger.error(f"Error fetching volatility data: {e}")
            raise

    async def fetch_technical_indicators(self, ticker: str, period: str = "1y") -> Dict[str, Any]:
        """
        Fetch technical indicators like SMA, MACD, RSI for a given ticker.

        Args:
            ticker: Stock symbol
            period: Time period for historical data

        Returns:
            Dictionary containing technical indicators
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if hist.empty:
                return {}

            sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            sma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]

            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            return {
                "sma_20": float(sma_20) if not pd.isna(sma_20) else None,
                "sma_50": float(sma_50) if not pd.isna(sma_50) else None,
                "sma_200": float(sma_200) if not pd.isna(sma_200) else None,
                "rsi": float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
                "current_price": float(hist['Close'].iloc[-1]),
                "timestamp": get_current_timestamp()
            }
        except Exception as e:
            logger.error(f"Error fetching technical indicators for {ticker}: {e}")
            return {}

    async def fetch_treasury_yields(self) -> Dict[str, float]:
        """
        Fetch Treasury yields and calculate spreads.

        Returns:
            Dictionary containing yield data and spreads
        """
        try:
            two_year = await self.fetch_macro_data("2Y_TREASURY")
            ten_year = await self.fetch_macro_data("10Y_TREASURY")

            if not two_year or not ten_year:
                return {}

            two_year_rate = two_year[-1].value if two_year else 0
            ten_year_rate = ten_year[-1].value if ten_year else 0

            return {
                "2y_yield": two_year_rate,
                "10y_yield": ten_year_rate,
                "2s_10s_spread": ten_year_rate - two_year_rate,
                "timestamp": get_current_timestamp()
            }
        except Exception as e:
            logger.error(f"Error fetching Treasury yields: {e}")
            return {}

    async def get_market_momentum_signals(self) -> Dict[str, Any]:
        """
        Generate market momentum signals based on technical indicators.

        Returns:
            Dictionary containing momentum signals
        """
        try:
            spy_indicators = await self.fetch_technical_indicators("SPY")

            if not spy_indicators:
                return {}

            current_price = spy_indicators.get("current_price", 0)
            sma_200 = spy_indicators.get("sma_200", 0)

            momentum_signal = "bullish" if current_price > sma_200 else "bearish"

            return {
                "spy_momentum": momentum_signal,
                "current_price": current_price,
                "sma_200": sma_200,
                "rsi": spy_indicators.get("rsi"),
                "timestamp": get_current_timestamp()
            }
        except Exception as e:
            logger.error(f"Error generating momentum signals: {e}")
            return {}

    async def health_check(self) -> Dict[str, str]:
        """
        Perform health check of data sources.

        Returns:
            Dictionary containing health status of each data source
        """
        health_status = {}

        try:
            test_data = await self.fetch_market_data("SPY")
            health_status["yahoo_finance"] = "healthy" if test_data else "error"
        except (ValueError, ConnectionError, TimeoutError, Exception) as e:
            logger.warning(f"Yahoo Finance health check failed: {e}")
            health_status["yahoo_finance"] = "error"

        try:
            test_macro = await self.fetch_macro_data("10Y_TREASURY")
            health_status["fred"] = "healthy" if test_macro else "error"
        except (ValueError, ConnectionError, TimeoutError, Exception) as e:
            logger.warning(f"FRED API health check failed: {e}")
            health_status["fred"] = "error"

        return health_status

    # Coral Protocol Integration Methods
    async def validate_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate macro signals using rule-based logic only.
        LLM validation is commented out to focus on pure data operations.

        Args:
            signals: Dictionary containing signal data to validate

        Returns:
            Validation result with confidence score based on market data
        """
        try:
            # Fetch current market data for validation
            spy_data = await self.fetch_market_data("SPY")
            vix_data = await self.fetch_volatility_data()
            treasury_data = await self.fetch_treasury_yields()

            market_data = {
                "spy_data": {
                    "price": spy_data.price if spy_data else 0,
                    "change": spy_data.change if spy_data else 0,
                    "change_percent": spy_data.change_percent if spy_data else 0
                },
                "vix_data": vix_data,
                "treasury_data": treasury_data
            }

            # LLM validation commented out for pure data focus
            # llm_validation = await safe_coral_invoke(
            #     self.coral_client,
            #     "llm_agent",
            #     "validate_signals",
            #     {"signals": signals, "market_data": market_data},
            #     "validate_signals"
            # )
            #
            # if llm_validation and llm_validation.get("is_valid") is not None and not llm_validation.get("error"):
            #     return llm_validation

            # Use rule-based validation with real data only
            validation_score = 0.0
            validation_details = {}

            # Validate yield curve signal
            if "yield_curve_inversion" in signals:
                current_spread = treasury_data.get("2s_10s_spread", 0)
                is_inverted = current_spread < 0
                validation_details["yield_curve"] = {
                    "current_spread": current_spread,
                    "is_inverted": is_inverted,
                    "signal_valid": is_inverted == signals["yield_curve_inversion"]
                }
                validation_score += 0.2 if validation_details["yield_curve"]["signal_valid"] else 0

            # Validate volatility signal
            if "volatility_spike" in signals:
                current_vix = vix_data.get("vix", 0)
                is_spike = current_vix >= 25
                validation_details["volatility"] = {
                    "current_vix": current_vix,
                    "is_spike": is_spike,
                    "signal_valid": is_spike == signals["volatility_spike"]
                }
                validation_score += 0.2 if validation_details["volatility"]["signal_valid"] else 0

            # Validate market momentum
            if "market_momentum" in signals:
                momentum_data = await self.get_market_momentum_signals()
                is_bearish = momentum_data.get("spy_momentum") == "bearish"
                validation_details["momentum"] = {
                    "current_momentum": momentum_data.get("spy_momentum"),
                    "is_bearish": is_bearish,
                    "signal_valid": is_bearish == signals["market_momentum"]
                }
                validation_score += 0.3 if validation_details["momentum"]["signal_valid"] else 0

            # Base validation score
            validation_score += 0.3

            return {
                "is_valid": validation_score >= 0.7,
                "confidence": min(validation_score, 1.0),
                "validation_details": validation_details,
                "timestamp": get_current_timestamp()
            }

        except Exception as e:
            logger.error(f"Error validating signals: {e}")
            # No fallbacks - return error information only
            return {
                "is_valid": False,
                "confidence": 0.0,
                "error": str(e),
                "timestamp": get_current_timestamp()
            }

    async def get_market_context(self, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive market context for explanations via Coral Protocol.

        Args:
            timestamp: Optional timestamp for historical context

        Returns:
            Comprehensive market context data
        """
        try:
            # Fetch all relevant market data
            spy_data = await self.fetch_market_data("SPY")
            vix_data = await self.fetch_volatility_data()
            treasury_data = await self.fetch_treasury_yields()
            momentum_data = await self.get_market_momentum_signals()

            # Get macro data
            macro_context = {}
            for indicator in ["CPI", "10Y_TREASURY", "FED_FUNDS_RATE", "UNEMPLOYMENT"]:
                try:
                    data = await self.fetch_macro_data(indicator, date_range=30)
                    if data:
                        macro_context[indicator] = {
                            "current_value": data[-1].value,
                            "previous_value": data[-2].value if len(data) > 1 else None,
                            "trend": "up" if len(data) > 1 and data[-1].value > data[-2].value else "down"
                        }
                except (ValueError, KeyError, IndexError, AttributeError) as e:
                    logger.warning(f"Failed to process macro indicator {indicator}: {e}")
                    continue

            return {
                "market_data": {
                    "spy_price": spy_data.price if spy_data else None,
                    "spy_change_percent": spy_data.change_percent if spy_data else None,
                    "vix": vix_data.get("vix"),
                    "vix_change": vix_data.get("vix_change"),
                    "yield_spread_2s10s": treasury_data.get("2s_10s_spread"),
                    "momentum_signal": momentum_data.get("spy_momentum")
                },
                "macro_indicators": macro_context,
                "market_regime": self._determine_market_regime(spy_data, vix_data, treasury_data),
                "timestamp": timestamp or get_current_timestamp()
            }

        except Exception as e:
            logger.error(f"Error getting market context: {e}")
            return {
                "error": str(e),
                "timestamp": timestamp or get_current_timestamp()
            }

    def _determine_market_regime(self, spy_data: MarketData, vix_data: Dict, treasury_data: Dict) -> str:
        """
        Determine current market regime based on available data.

        Returns:
            Market regime description
        """
        try:
            vix = vix_data.get("vix", 20)
            spread = treasury_data.get("2s_10s_spread", 1)

            if vix > 30:
                return "high_volatility_crisis"
            elif vix > 25:
                return "elevated_volatility"
            elif spread < 0:
                return "yield_curve_inversion"
            elif spread < 0.5:
                return "flattening_curve"
            elif vix < 15:
                return "low_volatility_complacency"
            else:
                return "normal_market_conditions"

        except (KeyError, TypeError, AttributeError) as e:
            logger.warning(f"Error determining market regime: {e}")
            return "unknown"

    async def fetch_dashboard_etfs(self, save_to_db: bool = True) -> Dict[str, Any]:
        """
        Fetch market data for all dashboard ETFs and optionally save to database.

        Args:
            save_to_db: Whether to save data to Supabase dashboard tables

        Returns:
            Dictionary containing market data for all dashboard ETFs
        """
        try:
            etf_data = {}
            failed_fetches = []

            for display_symbol, name in self.dashboard_etfs.items():
                try:
                    # Get actual ticker (handle mapping for crypto ETFs)
                    actual_ticker = self.ticker_mapping.get(display_symbol, display_symbol)

                    # Fetch market data
                    market_data = await self.fetch_market_data(actual_ticker)

                    # Fetch additional info using yfinance
                    additional_info = await self._get_additional_etf_info(actual_ticker)

                    etf_data[display_symbol] = {
                        "market_data": market_data,
                        "additional_info": additional_info,
                        "name": name,
                        "ticker": actual_ticker
                    }

                    # Save to database if requested
                    if save_to_db:
                        success = await DashboardDataService.save_market_data(
                            market_data,
                            {**additional_info, "name": name}
                        )
                        if not success:
                            logger.warning(f"Failed to save {display_symbol} to database")

                except Exception as e:
                    logger.error(f"Failed to fetch data for {display_symbol}: {e}")
                    failed_fetches.append(display_symbol)
                    continue

            # Fetch and save additional dashboard data
            if save_to_db:
                await self._save_dashboard_supplementary_data()

            return {
                "etf_data": etf_data,
                "failed_fetches": failed_fetches,
                "timestamp": get_current_timestamp(),
                "total_fetched": len(etf_data),
                "total_failed": len(failed_fetches)
            }

        except Exception as e:
            logger.error(f"Error fetching dashboard ETFs: {e}")
            return {"error": str(e), "timestamp": get_current_timestamp()}

    async def _get_additional_etf_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get additional ETF information using yfinance.

        Args:
            ticker: ETF ticker symbol

        Returns:
            Dictionary containing additional ETF info
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1y")

            if hist.empty:
                return {}

            return {
                "volume": info.get("volume"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "year_high": float(hist['High'].max()) if not hist.empty else None,
                "year_low": float(hist['Low'].min()) if not hist.empty else None,
                "expense_ratio": info.get("annualReportExpenseRatio"),
                "total_assets": info.get("totalAssets"),
                "beta": info.get("beta")
            }

        except Exception as e:
            logger.error(f"Error getting additional info for {ticker}: {e}")
            return {}

    async def _save_dashboard_supplementary_data(self) -> None:
        """Save supplementary dashboard data (volatility, treasury, macro)."""
        try:
            # Fetch volatility and treasury data
            vix_data = await self.fetch_volatility_data()
            treasury_data = await self.fetch_treasury_yields()

            # Determine market regime
            market_regime = None
            if vix_data:
                market_regime = self._determine_market_regime(None, vix_data, treasury_data or {})

            # Save market context data using simplified service
            if vix_data or treasury_data:
                await DashboardDataService.save_market_context_data(
                    vix_data=vix_data,
                    treasury_data=treasury_data,
                    market_regime=market_regime
                )

        except Exception as e:
            logger.error(f"Error saving supplementary dashboard data: {e}")

    async def get_dashboard_data(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data from database.

        Args:
            user_id: Optional user ID to get personalized watchlist

        Returns:
            Dictionary containing all dashboard data
        """
        try:
            # Get user's watchlist or default to dashboard ETFs
            symbols = list(self.dashboard_etfs.keys())

            # Map display symbols to actual tickers for database lookup
            db_symbols = [self.ticker_mapping.get(symbol, symbol) for symbol in symbols]

            # Get data from database
            dashboard_data = await DashboardDataService.get_dashboard_data(db_symbols)

            # Add ETF names and display symbols
            if dashboard_data.get("etf_data"):
                for item in dashboard_data["etf_data"]:
                    ticker = item.get("symbol", "")
                    # Find display symbol from ticker
                    display_symbol = ticker
                    for display, actual in self.ticker_mapping.items():
                        if actual == ticker:
                            display_symbol = display
                            break

                    item["display_symbol"] = display_symbol
                    item["etf_name"] = self.dashboard_etfs.get(display_symbol, ticker)

            return dashboard_data

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {"error": str(e), "timestamp": get_current_timestamp()}

    async def refresh_dashboard_data(self) -> Dict[str, Any]:
        """
        Refresh all dashboard data by fetching new data and saving to database.

        Returns:
            Dictionary containing refresh status and data
        """
        try:
            logger.info("Starting dashboard data refresh...")

            # Fetch and save all ETF data
            etf_result = await self.fetch_dashboard_etfs(save_to_db=True)

            # Fetch technical indicators for main ETFs
            technical_results = {}
            main_etfs = ["SPY", "QQQ", "VXUS", "IEF"]

            for symbol in main_etfs:
                try:
                    actual_ticker = self.ticker_mapping.get(symbol, symbol)
                    indicators = await self.fetch_technical_indicators(actual_ticker)
                    if indicators:
                        await DashboardDataService.save_technical_indicators(actual_ticker, indicators)
                        technical_results[symbol] = indicators
                except Exception as e:
                    logger.warning(f"Failed to fetch technical indicators for {symbol}: {e}")

            logger.info("Dashboard data refresh completed")

            return {
                "status": "success",
                "etf_data": etf_result,
                "technical_indicators": technical_results,
                "timestamp": get_current_timestamp()
            }

        except Exception as e:
            logger.error(f"Error refreshing dashboard data: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": get_current_timestamp()
            }