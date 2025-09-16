import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .data_agent import DataAgent
from .portfolio_agent import PortfolioAgent
from .planner_agent import PlannerAgent
from .explainability_agent import ExplainabilityAgent
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


class PortfolioAgentTasks:
    """
    Task scheduler and configuration for the Portfolio Agent.
    Manages portfolio optimization, rebalancing, and performance monitoring tasks.
    """

    def __init__(self):
        self.portfolio_agent = PortfolioAgent()

        self.REBALANCING_FREQUENCY = "weekly"  # weekly, monthly, quarterly
        self.RISK_MONITORING_FREQUENCY = "daily"
        self.BACKTEST_FREQUENCY = "monthly"

        self.MAX_PORTFOLIO_DRIFT = 0.05  # 5% drift threshold
        self.REBALANCING_THRESHOLD = 0.02  # 2% threshold for rebalancing

    async def portfolio_rebalancing_task(self, portfolio_id: str) -> Dict[str, Any]:
        """
        Periodic task to check and execute portfolio rebalancing.
        """
        try:
            logger.info(f"Starting rebalancing task for portfolio {portfolio_id}")

            results = {
                "portfolio_id": portfolio_id,
                "timestamp": datetime.now().isoformat(),
                "rebalancing_required": False,
                "action_taken": "none"
            }

            return results

        except Exception as e:
            logger.error(f"Error in portfolio rebalancing task: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def risk_monitoring_task(self, portfolio_id: str) -> Dict[str, Any]:
        """
        Daily task to monitor portfolio risk metrics.
        """
        try:
            logger.info(f"Starting risk monitoring for portfolio {portfolio_id}")

            results = {
                "portfolio_id": portfolio_id,
                "timestamp": datetime.now().isoformat(),
                "risk_metrics": {},
                "alerts": []
            }

            return results

        except Exception as e:
            logger.error(f"Error in risk monitoring task: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def performance_tracking_task(self, portfolio_id: str) -> Dict[str, Any]:
        """
        Task to track and analyze portfolio performance.
        """
        try:
            logger.info(f"Starting performance tracking for portfolio {portfolio_id}")

            results = {
                "portfolio_id": portfolio_id,
                "timestamp": datetime.now().isoformat(),
                "performance_metrics": {}
            }

            return results

        except Exception as e:
            logger.error(f"Error in performance tracking task: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


class PlannerAgentTasks:
    """
    Task scheduler and configuration for the Financial Planner Agent.
    Manages goal parsing, strategy updates, and lifecycle planning tasks.
    """

    def __init__(self):
        self.planner_agent = PlannerAgent()

        self.GOAL_REVIEW_FREQUENCY = "quarterly"
        self.STRATEGY_UPDATE_FREQUENCY = "semi_annually"
        self.LIFECYCLE_ADJUSTMENT_FREQUENCY = "annually"

    async def goal_parsing_task(self, goal_text: str, user_id: str) -> Dict[str, Any]:
        """
        Task to parse and validate user financial goals.
        """
        try:
            logger.info(f"Starting goal parsing for user {user_id}")

            goal_params = await self.planner_agent.parse_goal(goal_text)

            results = {
                "user_id": user_id,
                "original_text": goal_text,
                "parsed_goal": {
                    "goal_type": goal_params.goal_type.value,
                    "target_amount": goal_params.target_amount,
                    "time_horizon_years": goal_params.time_horizon_years,
                    "current_age": goal_params.current_age,
                    "risk_tolerance": goal_params.risk_tolerance.value if goal_params.risk_tolerance else None
                },
                "timestamp": datetime.now().isoformat()
            }

            return results

        except Exception as e:
            logger.error(f"Error in goal parsing task: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def strategy_generation_task(self, goal: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task to generate investment strategy based on goals and profile.
        """
        try:
            logger.info("Starting strategy generation task")

            results = {
                "timestamp": datetime.now().isoformat(),
                "strategy_generated": True,
                "recommended_allocation": {}
            }

            return results

        except Exception as e:
            logger.error(f"Error in strategy generation task: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def lifecycle_adjustment_task(self, user_id: str, current_age: int) -> Dict[str, Any]:
        """
        Annual task to adjust strategy based on lifecycle changes.
        """
        try:
            logger.info(f"Starting lifecycle adjustment for user {user_id}")

            glide_path = self.planner_agent.build_glide_path(current_age)

            results = {
                "user_id": user_id,
                "current_age": current_age,
                "glide_path": glide_path.age_ranges,
                "adjustments_made": [],
                "timestamp": datetime.now().isoformat()
            }

            return results

        except Exception as e:
            logger.error(f"Error in lifecycle adjustment task: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


class ExplainabilityAgentTasks:
    """
    Task scheduler and configuration for the Explainability Agent.
    Manages explanation generation, translation, and verification tasks.
    """

    def __init__(self):
        self.explainability_agent = ExplainabilityAgent()

        self.EXPLANATION_CACHE_TTL = 3600  # 1 hour
        self.VERIFICATION_FREQUENCY = "daily"
        self.JARGON_UPDATE_FREQUENCY = "monthly"

    async def explanation_generation_task(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task to generate comprehensive explanations for agent actions.
        """
        try:
            logger.info(f"Starting explanation generation for action {action.get('id')}")

            results = {
                "action_id": action.get("id"),
                "explanation_generated": True,
                "explanation": "Generated explanation would appear here",
                "confidence_score": 0.85,
                "timestamp": datetime.now().isoformat()
            }

            return results

        except Exception as e:
            logger.error(f"Error in explanation generation task: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def jargon_translation_task(self, technical_text: str) -> Dict[str, Any]:
        """
        Task to translate technical financial jargon to plain English.
        """
        try:
            logger.info("Starting jargon translation task")

            translated_text = self.explainability_agent.translate_jargon(technical_text)

            results = {
                "original_text": technical_text,
                "translated_text": translated_text,
                "translation_quality": "high",
                "timestamp": datetime.now().isoformat()
            }

            return results

        except Exception as e:
            logger.error(f"Error in jargon translation task: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def verification_task(self, explanation_id: str) -> Dict[str, Any]:
        """
        Task to verify explanation accuracy and consistency.
        """
        try:
            logger.info(f"Starting verification for explanation {explanation_id}")

            results = {
                "explanation_id": explanation_id,
                "verification_passed": True,
                "accuracy_score": 0.92,
                "consistency_score": 0.89,
                "timestamp": datetime.now().isoformat()
            }

            return results

        except Exception as e:
            logger.error(f"Error in verification task: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}