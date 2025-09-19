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
            except (ValueError, ConnectionError, ImportError) as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
            except Exception as e:
                logger.error(f"Unexpected error initializing Supabase client: {e}")
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
                
        except (ValueError, TypeError, ConnectionError, KeyError) as e:
            logger.error(f"Error storing market data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error storing market data: {e}")
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
                
        except (ValueError, TypeError, ConnectionError, KeyError) as e:
            logger.error(f"Error storing macro data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error storing macro data: {e}")
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


# Portfolio Agent Utilities
class PortfolioOptimizer:
    """
    Utility class for portfolio optimization calculations.
    """

    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio for a series of returns.

        Args:
            returns: List of return values
            risk_free_rate: Risk-free rate for calculation

        Returns:
            Sharpe ratio
        """
        if not returns or len(returns) < 2:
            return 0.0

        import numpy as np
        excess_returns = np.array(returns) - risk_free_rate
        return np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) > 0 else 0.0

    @staticmethod
    def calculate_maximum_drawdown(prices: List[float]) -> float:
        """
        Calculate maximum drawdown from price series.

        Args:
            prices: List of price values

        Returns:
            Maximum drawdown as percentage
        """
        if not prices or len(prices) < 2:
            return 0.0

        import numpy as np
        prices_array = np.array(prices)
        running_max = np.maximum.accumulate(prices_array)
        drawdown = (prices_array - running_max) / running_max
        return abs(np.min(drawdown))

    @staticmethod
    def optimize_weights(expected_returns: Dict[str, float], covariance_matrix: Dict[str, Dict[str, float]],
                        risk_tolerance: float = 0.5) -> Dict[str, float]:
        """
        Optimize portfolio weights using mean-variance optimization.

        Args:
            expected_returns: Dictionary of expected returns for each asset
            covariance_matrix: Covariance matrix as nested dictionary
            risk_tolerance: Risk tolerance parameter (0-1)

        Returns:
            Optimized weights dictionary
        """
        # Simplified optimization - in practice would use scipy.optimize
        total_assets = len(expected_returns)
        equal_weight = 1.0 / total_assets if total_assets > 0 else 0.0

        optimized_weights = {}
        for asset in expected_returns.keys():
            # Simple risk-adjusted weighting
            risk_adj_return = expected_returns[asset] * risk_tolerance
            optimized_weights[asset] = min(max(equal_weight * risk_adj_return, 0.01), 0.4)

        # Normalize weights to sum to 1
        total_weight = sum(optimized_weights.values())
        if total_weight > 0:
            optimized_weights = {k: v / total_weight for k, v in optimized_weights.items()}

        return optimized_weights

class RiskCalculator:
    """
    Utility class for risk calculations and metrics.
    """

    @staticmethod
    def calculate_var(returns: List[float], confidence_level: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR).

        Args:
            returns: List of return values
            confidence_level: Confidence level for VaR calculation

        Returns:
            VaR value
        """
        if not returns:
            return 0.0

        import numpy as np
        sorted_returns = np.sort(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        return abs(sorted_returns[index]) if index < len(sorted_returns) else 0.0

    @staticmethod
    def calculate_beta(asset_returns: List[float], market_returns: List[float]) -> float:
        """
        Calculate beta relative to market.

        Args:
            asset_returns: Asset return series
            market_returns: Market return series

        Returns:
            Beta value
        """
        if not asset_returns or not market_returns or len(asset_returns) != len(market_returns):
            return 1.0

        import numpy as np
        asset_array = np.array(asset_returns)
        market_array = np.array(market_returns)

        covariance = np.cov(asset_array, market_array)[0, 1]
        market_variance = np.var(market_array)

        return covariance / market_variance if market_variance > 0 else 1.0


# Financial Planner Agent Utilities
class GoalAnalyzer:
    """
    Utility class for analyzing and processing financial goals.
    """

    @staticmethod
    def calculate_required_savings(target_amount: float, current_savings: float,
                                 years: int, expected_return: float = 0.07) -> float:
        """
        Calculate required monthly savings to reach goal.

        Args:
            target_amount: Target amount needed
            current_savings: Current savings amount
            years: Number of years to goal
            expected_return: Expected annual return

        Returns:
            Required monthly savings amount
        """
        if years <= 0:
            return target_amount - current_savings

        # Future value of current savings
        fv_current = current_savings * ((1 + expected_return) ** years)

        # Amount still needed
        amount_needed = max(target_amount - fv_current, 0)

        # Monthly payment calculation (annuity formula)
        monthly_rate = expected_return / 12
        months = years * 12

        if monthly_rate > 0:
            monthly_savings = amount_needed * monthly_rate / ((1 + monthly_rate) ** months - 1)
        else:
            monthly_savings = amount_needed / months

        return monthly_savings

    @staticmethod
    def assess_goal_feasibility(target_amount: float, monthly_savings: float,
                              years: int, expected_return: float = 0.07) -> Dict[str, Any]:
        """
        Assess feasibility of reaching a financial goal.

        Args:
            target_amount: Target amount needed
            monthly_savings: Available monthly savings
            years: Number of years to goal
            expected_return: Expected annual return

        Returns:
            Feasibility assessment dictionary
        """
        monthly_rate = expected_return / 12
        months = years * 12

        # Future value of monthly savings
        if monthly_rate > 0:
            fv_savings = monthly_savings * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        else:
            fv_savings = monthly_savings * months

        shortfall = max(target_amount - fv_savings, 0)
        surplus = max(fv_savings - target_amount, 0)

        feasibility_score = min(fv_savings / target_amount, 1.0) if target_amount > 0 else 1.0

        return {
            "is_feasible": shortfall == 0,
            "projected_amount": fv_savings,
            "shortfall": shortfall,
            "surplus": surplus,
            "feasibility_score": feasibility_score,
            "recommended_adjustments": []
        }

class LifecyclePlanner:
    """
    Utility class for lifecycle-based financial planning.
    """

    @staticmethod
    def calculate_retirement_needs(current_age: int, retirement_age: int,
                                 current_income: float, replacement_ratio: float = 0.8) -> Dict[str, Any]:
        """
        Calculate retirement funding needs.

        Args:
            current_age: Current age
            retirement_age: Target retirement age
            current_income: Current annual income
            replacement_ratio: Desired income replacement ratio

        Returns:
            Retirement needs analysis
        """
        years_to_retirement = max(retirement_age - current_age, 0)
        retirement_years = max(85 - retirement_age, 15)  # Assume life expectancy of 85

        annual_need = current_income * replacement_ratio
        inflation_rate = 0.03  # Assume 3% inflation

        # Inflate current income to retirement
        inflated_annual_need = annual_need * ((1 + inflation_rate) ** years_to_retirement)

        # Total retirement corpus needed (present value at retirement)
        total_corpus_needed = inflated_annual_need * retirement_years

        return {
            "years_to_retirement": years_to_retirement,
            "retirement_years": retirement_years,
            "annual_need_today": annual_need,
            "annual_need_at_retirement": inflated_annual_need,
            "total_corpus_needed": total_corpus_needed
        }


# Explainability Agent Utilities
class ExplanationGenerator:
    """
    Utility class for generating explanations and translations.
    """

    @staticmethod
    def complexity_score(text: str) -> float:
        """
        Calculate complexity score of financial text.

        Args:
            text: Text to analyze

        Returns:
            Complexity score (0-1, higher = more complex)
        """
        if not text:
            return 0.0

        # Simple complexity metrics
        words = text.split()
        long_words = [w for w in words if len(w) > 7]
        sentences = text.split('.')

        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        long_word_ratio = len(long_words) / len(words) if words else 0
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        # Weighted complexity score
        complexity = (
            (avg_word_length / 10) * 0.3 +
            long_word_ratio * 0.4 +
            (avg_sentence_length / 20) * 0.3
        )

        return min(complexity, 1.0)

    @staticmethod
    def generate_summary(text: str, max_length: int = 200) -> str:
        """
        Generate summary of financial explanation.

        Args:
            text: Text to summarize
            max_length: Maximum length of summary

        Returns:
            Summary text
        """
        if not text or len(text) <= max_length:
            return text

        # Simple extractive summarization
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            return text[:max_length]

        # Take first and most important sentences
        summary_sentences = []
        current_length = 0

        for sentence in sentences:
            if current_length + len(sentence) <= max_length:
                summary_sentences.append(sentence)
                current_length += len(sentence) + 1
            else:
                break

        summary = '. '.join(summary_sentences)
        if summary and not summary.endswith('.'):
            summary += '.'

        return summary if summary else text[:max_length]

class ConfidenceCalculator:
    """
    Utility class for calculating confidence scores in explanations.
    """

    @staticmethod
    def calculate_explanation_confidence(explanation: str, context: Dict[str, Any]) -> float:
        """
        Calculate confidence score for an explanation.

        Args:
            explanation: Generated explanation text
            context: Context information used for explanation

        Returns:
            Confidence score (0-1)
        """
        if not explanation:
            return 0.0

        confidence_factors = []

        # Length factor - reasonable explanations should have adequate length
        length_factor = min(len(explanation) / 200, 1.0)
        confidence_factors.append(length_factor * 0.2)

        # Context availability factor
        context_factor = min(len(context) / 5, 1.0) if context else 0.0
        confidence_factors.append(context_factor * 0.3)

        # Explanation completeness (has key components)
        has_reason = any(word in explanation.lower() for word in ['because', 'due to', 'reason', 'caused by'])
        has_impact = any(word in explanation.lower() for word in ['will', 'should', 'expect', 'likely'])
        has_data = any(word in explanation.lower() for word in ['data', 'shows', 'indicates', 'suggests'])

        completeness_score = sum([has_reason, has_impact, has_data]) / 3
        confidence_factors.append(completeness_score * 0.5)

        return sum(confidence_factors)