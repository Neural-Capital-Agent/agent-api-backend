import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .agents import DataAgent
from .utils import SupabaseDataStorage, DataValidator, DataAggregator

logger = logging.getLogger(__name__)

class DataAgentTasks:
    """
    Task scheduler and configuration for the Data Agent.
    Manages periodic data collection, validation, and storage tasks.
    """
    
    def __init__(self):
        self.data_agent = DataAgent()
        self.storage = SupabaseDataStorage()
        self.validator = DataValidator()
        self.aggregator = DataAggregator()
        
        # Configuration constants
        self.DAILY_UPDATE_ASSETS = [
            "SPY", "QQQ", "VXUS",  # Equities
            "SGOV", "SHY", "IEF", "BND", "TIP",  # Fixed Income
            "GLD",  # Alternatives
            "BTC-USD", "ETH-USD"  # Crypto
        ]
        
        self.DAILY_MACRO_INDICATORS = [
            "VIX", "10Y_TREASURY", "DXY"
        ]
        
        self.MONTHLY_MACRO_INDICATORS = [
            "CPI", "UNEMPLOYMENT", "FED_FUNDS_RATE", "PMI"
        ]
        
        # API Rate Limits and Retry Configuration
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 1  # seconds
        self.BATCH_SIZE = 5  # assets per batch for API calls
        
        # Data Quality Thresholds
        self.MIN_DATA_COMPLETENESS = 0.8  # 80% of expected data points
        self.MAX_PRICE_DEVIATION = 0.5  # 50% price deviation threshold
        
    async def daily_market_data_collection(self) -> Dict[str, Any]:
        """
        Daily task to collect market data for all assets in the universe.
        Includes validation, storage, and quality checks.
        
        Returns:
            Summary of collection results
        """
        logger.info("Starting daily market data collection")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_assets": len(self.DAILY_UPDATE_ASSETS),
            "successful": 0,
            "failed": 0,
            "errors": [],
            "data_quality_score": 0.0
        }
        
        successful_data = []
        
        # Process assets in batches to respect rate limits
        for i in range(0, len(self.DAILY_UPDATE_ASSETS), self.BATCH_SIZE):
            batch = self.DAILY_UPDATE_ASSETS[i:i + self.BATCH_SIZE]
            
            for asset in batch:
                try:
                    # Fetch market data with retries
                    market_data = await self._fetch_with_retry(
                        self.data_agent.fetch_market_data, asset
                    )
                    
                    if market_data:
                        # Convert to dictionary for validation
                        data_dict = {
                            "symbol": market_data.symbol,
                            "price": market_data.price,
                            "previous_close": market_data.previous_close,
                            "change": market_data.change,
                            "change_percent": market_data.change_percent,
                            "timestamp": market_data.timestamp.isoformat() if market_data.timestamp else None
                        }
                        
                        # Validate data quality
                        if self.validator.validate_market_data(data_dict):
                            # Store in database if available
                            if self.storage.is_available():
                                await self.storage.store_market_data(data_dict)
                            
                            successful_data.append(data_dict)
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Data validation failed for {asset}")
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"No data returned for {asset}")
                        
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Error fetching {asset}: {str(e)}")
                    logger.error(f"Error in daily collection for {asset}: {e}")
            
            # Rate limiting delay between batches
            if i + self.BATCH_SIZE < len(self.DAILY_UPDATE_ASSETS):
                await asyncio.sleep(self.RETRY_DELAY)
        
        # Calculate data quality score
        results["data_quality_score"] = results["successful"] / results["total_assets"]
        
        # Log summary
        logger.info(f"Daily collection completed: {results['successful']}/{results['total_assets']} successful")
        
        return results
    
    async def daily_macro_data_collection(self) -> Dict[str, Any]:
        """
        Daily task to collect macro-economic data that updates frequently.
        
        Returns:
            Summary of collection results
        """
        logger.info("Starting daily macro data collection")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_indicators": len(self.DAILY_MACRO_INDICATORS),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for indicator in self.DAILY_MACRO_INDICATORS:
            try:
                macro_data_list = await self._fetch_with_retry(
                    self.data_agent.fetch_macro_data, indicator, 1
                )
                
                if macro_data_list:
                    for macro_data in macro_data_list:
                        data_dict = {
                            "indicator": macro_data.indicator,
                            "value": macro_data.value,
                            "date": macro_data.date.isoformat(),
                            "frequency": macro_data.frequency
                        }
                        
                        if self.validator.validate_macro_data(data_dict):
                            if self.storage.is_available():
                                await self.storage.store_macro_data(data_dict)
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Validation failed for {indicator}")
                else:
                    results["failed"] += 1
                    results["errors"].append(f"No data returned for {indicator}")
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error fetching {indicator}: {str(e)}")
                logger.error(f"Error in daily macro collection for {indicator}: {e}")
        
        logger.info(f"Daily macro collection completed: {results['successful']} indicators processed")
        
        return results
    
    async def weekly_technical_analysis(self) -> Dict[str, Any]:
        """
        Weekly task to calculate technical indicators for key assets.
        
        Returns:
            Technical analysis results
        """
        logger.info("Starting weekly technical analysis")
        
        key_assets = ["SPY", "QQQ", "BTC-USD"]  # Focus on key market indicators
        results = {
            "timestamp": datetime.now().isoformat(),
            "analysis": {},
            "market_signals": {}
        }
        
        for asset in key_assets:
            try:
                technical_data = await self.data_agent.fetch_technical_indicators(asset, "1y")
                
                if technical_data:
                    results["analysis"][asset] = technical_data
                    
                    # Generate simple signals
                    current_price = technical_data.get("current_price", 0)
                    sma_200 = technical_data.get("sma_200", 0)
                    rsi = technical_data.get("rsi", 50)
                    
                    signal = "neutral"
                    if current_price > sma_200 and rsi < 70:
                        signal = "bullish"
                    elif current_price < sma_200 and rsi > 30:
                        signal = "bearish"
                    
                    results["market_signals"][asset] = signal
                    
            except Exception as e:
                logger.error(f"Error in technical analysis for {asset}: {e}")
                results["analysis"][asset] = {"error": str(e)}
        
        # Generate overall market momentum
        try:
            momentum = await self.data_agent.get_market_momentum_signals()
            results["overall_momentum"] = momentum
        except Exception as e:
            logger.error(f"Error generating market momentum: {e}")
            results["overall_momentum"] = {"error": str(e)}
        
        return results
    
    async def monthly_data_cleanup(self) -> Dict[str, Any]:
        """
        Monthly task to clean up old data and perform maintenance.
        
        Returns:
            Cleanup results
        """
        logger.info("Starting monthly data cleanup")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "cleanup_performed": False,
            "error": None
        }
        
        try:
            if self.storage.is_available():
                success = await self.storage.cleanup_old_data(days=365)  # Keep 1 year of data
                results["cleanup_performed"] = success
                
                if success:
                    logger.info("Successfully cleaned up old data")
                else:
                    logger.warning("Data cleanup completed with warnings")
            else:
                logger.warning("Supabase storage not available for cleanup")
                results["error"] = "Storage not available"
                
        except Exception as e:
            logger.error(f"Error during monthly cleanup: {e}")
            results["error"] = str(e)
        
        return results
    
    async def health_check_task(self) -> Dict[str, Any]:
        """
        Regular health check of all data sources and services.
        
        Returns:
            Health status results
        """
        logger.info("Performing data agent health check")
        
        try:
            # Check data source health
            health_status = await self.data_agent.health_check()
            
            # Check storage health
            health_status["supabase"] = "healthy" if self.storage.is_available() else "unavailable"
            
            # Add timestamp
            health_status["timestamp"] = datetime.now().isoformat()
            
            # Overall health score
            healthy_sources = sum(1 for status in health_status.values() 
                                if isinstance(status, str) and status == "healthy")
            total_sources = len([k for k, v in health_status.items() 
                               if isinstance(v, str) and k != "timestamp"])
            
            health_status["overall_health_score"] = healthy_sources / total_sources if total_sources > 0 else 0
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "overall_health_score": 0.0
            }
    
    async def _fetch_with_retry(self, fetch_func, *args, **kwargs):
        """
        Execute fetch function with retry logic.
        
        Args:
            fetch_func: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
        
        Returns:
            Function result or None if all retries failed
        """
        last_exception = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                return await fetch_func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))  # Exponential backoff
                logger.warning(f"Fetch attempt {attempt + 1} failed: {e}")
        
        logger.error(f"All {self.MAX_RETRIES} fetch attempts failed. Last error: {last_exception}")
        return None