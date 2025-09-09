import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseDataStorage:
    """
    Supabase integration for storing and retrieving financial data.
    Maintains historical records and improves data retrieval efficiency.
    """
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not found in environment variables")
            self.client = None
        else:
            try:
                self.client: Client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if Supabase client is available and connected."""
        return self.client is not None
    
    async def store_market_data(self, market_data: Dict[str, Any]) -> bool:
        """
        Store market data in Supabase.
        
        Args:
            market_data: Dictionary containing market data
        
        Returns:
            Boolean indicating success
        """
        if not self.client:
            logger.warning("Supabase client not available")
            return False
        
        try:
            data = {
                "symbol": market_data.get("symbol"),
                "price": market_data.get("price"),
                "previous_close": market_data.get("previous_close"),
                "change": market_data.get("change"),
                "change_percent": market_data.get("change_percent"),
                "volume": market_data.get("volume"),
                "market_cap": market_data.get("market_cap"),
                "timestamp": market_data.get("timestamp", datetime.now().isoformat()),
                "created_at": datetime.now().isoformat()
            }
            
            result = self.client.table("market_data").insert(data).execute()
            
            if result.data:
                logger.debug(f"Successfully stored market data for {market_data.get('symbol')}")
                return True
            else:
                logger.error(f"Failed to store market data for {market_data.get('symbol')}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing market data: {e}")
            return False
    
    async def store_macro_data(self, macro_data: Dict[str, Any]) -> bool:
        """
        Store macro-economic data in Supabase.
        
        Args:
            macro_data: Dictionary containing macro data
        
        Returns:
            Boolean indicating success
        """
        if not self.client:
            logger.warning("Supabase client not available")
            return False
        
        try:
            data = {
                "indicator": macro_data.get("indicator"),
                "value": macro_data.get("value"),
                "date": macro_data.get("date"),
                "frequency": macro_data.get("frequency"),
                "created_at": datetime.now().isoformat()
            }
            
            result = self.client.table("macro_data").insert(data).execute()
            
            if result.data:
                logger.debug(f"Successfully stored macro data for {macro_data.get('indicator')}")
                return True
            else:
                logger.error(f"Failed to store macro data for {macro_data.get('indicator')}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing macro data: {e}")
            return False
    
    async def get_historical_market_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Retrieve historical market data from Supabase.
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
        
        Returns:
            List of historical market data
        """
        if not self.client:
            logger.warning("Supabase client not available")
            return []
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            result = self.client.table("market_data")\
                .select("*")\
                .eq("symbol", symbol)\
                .gte("created_at", cutoff_date)\
                .order("created_at", desc=True)\
                .execute()
            
            if result.data:
                logger.debug(f"Retrieved {len(result.data)} historical records for {symbol}")
                return result.data
            else:
                logger.debug(f"No historical data found for {symbol}")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving historical market data: {e}")
            return []
    
    async def get_historical_macro_data(self, indicator: str, days: int = 90) -> List[Dict[str, Any]]:
        """
        Retrieve historical macro-economic data from Supabase.
        
        Args:
            indicator: Economic indicator name
            days: Number of days to look back
        
        Returns:
            List of historical macro data
        """
        if not self.client:
            logger.warning("Supabase client not available")
            return []
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            result = self.client.table("macro_data")\
                .select("*")\
                .eq("indicator", indicator)\
                .gte("created_at", cutoff_date)\
                .order("date", desc=True)\
                .execute()
            
            if result.data:
                logger.debug(f"Retrieved {len(result.data)} historical records for {indicator}")
                return result.data
            else:
                logger.debug(f"No historical data found for {indicator}")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving historical macro data: {e}")
            return []
    
    async def cleanup_old_data(self, days: int = 365) -> bool:
        """
        Clean up old data beyond specified retention period.
        
        Args:
            days: Retention period in days
        
        Returns:
            Boolean indicating success
        """
        if not self.client:
            logger.warning("Supabase client not available")
            return False
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            market_result = self.client.table("market_data")\
                .delete()\
                .lt("created_at", cutoff_date)\
                .execute()
            
            macro_result = self.client.table("macro_data")\
                .delete()\
                .lt("created_at", cutoff_date)\
                .execute()
            
            logger.info(f"Cleaned up old data before {cutoff_date}")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return False

class DataValidator:
    """
    Utility class for validating and sanitizing financial data.
    """
    
    @staticmethod
    def validate_market_data(data: Dict[str, Any]) -> bool:
        """
        Validate market data structure and values.
        
        Args:
            data: Market data dictionary
        
        Returns:
            Boolean indicating if data is valid
        """
        required_fields = ["symbol", "price", "previous_close"]
        
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return False
            
            if data[field] is None:
                logger.warning(f"Null value for required field: {field}")
                return False
        
        if not isinstance(data["price"], (int, float)) or data["price"] < 0:
            logger.warning("Invalid price value")
            return False
        
        if not isinstance(data["previous_close"], (int, float)) or data["previous_close"] < 0:
            logger.warning("Invalid previous_close value")
            return False
        
        return True
    
    @staticmethod
    def validate_macro_data(data: Dict[str, Any]) -> bool:
        """
        Validate macro-economic data structure and values.
        
        Args:
            data: Macro data dictionary
        
        Returns:
            Boolean indicating if data is valid
        """
        required_fields = ["indicator", "value", "date"]
        
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return False
            
            if data[field] is None:
                logger.warning(f"Null value for required field: {field}")
                return False
        
        if not isinstance(data["value"], (int, float)):
            logger.warning("Invalid value type")
            return False
        
        return True
    
    @staticmethod
    def sanitize_symbol(symbol: str) -> str:
        """
        Sanitize stock symbol for consistency.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Sanitized symbol
        """
        if not symbol:
            return ""
        
        return symbol.upper().strip()

class DataAggregator:
    """
    Utility class for aggregating and processing financial data.
    """
    
    @staticmethod
    def calculate_moving_average(data: List[float], window: int) -> Optional[float]:
        """
        Calculate simple moving average.
        
        Args:
            data: List of price values
            window: Moving average window size
        
        Returns:
            Moving average value or None if insufficient data
        """
        if len(data) < window:
            return None
        
        return sum(data[-window:]) / window
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: List of price values
            period: RSI calculation period
        
        Returns:
            RSI value or None if insufficient data
        """
        if len(prices) < period + 1:
            return None
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        if len(gains) < period or len(losses) < period:
            return None
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def aggregate_portfolio_data(asset_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate data across portfolio assets.
        
        Args:
            asset_data: List of asset data dictionaries
        
        Returns:
            Aggregated portfolio metrics
        """
        if not asset_data:
            return {}
        
        total_change = sum(data.get("change", 0) for data in asset_data if data.get("change"))
        total_assets = len([data for data in asset_data if data.get("price")])
        
        positive_changes = len([data for data in asset_data if data.get("change", 0) > 0])
        negative_changes = len([data for data in asset_data if data.get("change", 0) < 0])
        
        return {
            "total_assets": total_assets,
            "total_change": total_change,
            "positive_changes": positive_changes,
            "negative_changes": negative_changes,
            "market_breadth": positive_changes / total_assets if total_assets > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }