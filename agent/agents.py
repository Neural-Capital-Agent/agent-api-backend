from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass
import yfinance as yf
import requests
import pandas as pd

from ..utils.yahoo import yahoo
from ..utils.polygon import polygon
from ..utils.fred import fred

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    symbol: str
    price: float
    previous_close: float
    change: float
    change_percent: float
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    timestamp: Optional[datetime] = None

@dataclass
class MacroData:
    indicator: str
    value: float
    date: datetime
    frequency: str

class DataAgent:
    """
    Data Agent responsible for collecting, processing, and providing financial news,
    real-time market prices, and macro-economic data to other agents.
    """
    
    def __init__(self):
        self.equity_universe = ["SPY", "QQQ", "VXUS"]
        self.fixed_income_universe = ["SGOV", "SHY", "IEF", "BND", "TIP"]
        self.alternatives_universe = ["GLD"]
        self.crypto_universe = ["BTC-USD", "ETH-USD"]
        
        self.all_assets = (
            self.equity_universe + 
            self.fixed_income_universe + 
            self.alternatives_universe + 
            self.crypto_universe
        )
        
        self.macro_indicators = {
            "CPI": "CPIAUCNS",
            "10Y_TREASURY": "GS10",
            "FED_FUNDS_RATE": "FEDFUNDS",
            "UNEMPLOYMENT": "UNRATE",
            "VIX": "VIXCLS",
            "PMI": "NAPMPMI",
            "DXY": "DTWEXBGS"
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
                symbol=stock_data["symbol"],
                price=stock_data["current_price"] or 0,
                previous_close=stock_data["price"] or 0,
                change=stock_data["change"] or 0,
                change_percent=stock_data["changePercent"] or 0,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error fetching market data for {ticker}: {e}")
            raise
    
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
            data = fred.get_fred_data(fred_code)
            
            macro_data = []
            if data:
                for entry in data:
                    macro_data.append(MacroData(
                        indicator=indicator,
                        value=entry.get("value", 0),
                        date=datetime.fromisoformat(entry.get("date", datetime.now().isoformat())),
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
            
            return {
                "vix": vix_data.price,
                "vix_change": vix_data.change,
                "vix_change_percent": vix_data.change_percent,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching volatility data: {e}")
            return {}
    
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
                "timestamp": datetime.now().isoformat()
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
                "timestamp": datetime.now().isoformat()
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
                "timestamp": datetime.now().isoformat()
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
        except:
            health_status["yahoo_finance"] = "error"
        
        try:
            test_macro = await self.fetch_macro_data("10Y_TREASURY")
            health_status["fred"] = "healthy" if test_macro else "error"
        except:
            health_status["fred"] = "error"
        
        return health_status