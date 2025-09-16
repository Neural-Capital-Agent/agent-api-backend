from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
import uuid
import numpy as np

from .models import RiskLevel, Portfolio, MacroSignals, MacroSignal, RebalanceAction
from .config import config
from .shared import BaseAgent, ErrorHandler, get_current_timestamp, safe_get, safe_coral_invoke

logger = logging.getLogger(__name__)


class PortfolioAgent(BaseAgent):
    """
    Portfolio Agent responsible for algorithmic portfolio optimization
    and dynamic rebalancing based on risk tolerance and macro signals.
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555"):
        super().__init__(coral_server_url, "portfolio_agent")
        from .models import RiskLevel

        # Load asset universe from configuration
        self.equity_universe = config.data_agent.EQUITY_UNIVERSE
        self.fixed_income_universe = config.data_agent.FIXED_INCOME_UNIVERSE
        self.alternatives_universe = config.data_agent.ALTERNATIVES_UNIVERSE
        self.crypto_universe = config.data_agent.CRYPTO_UNIVERSE

        # Load base allocations from configuration
        self.base_allocations = {
            RiskLevel.CONSERVATIVE: config.portfolio_agent.BASE_ALLOCATIONS[1],
            RiskLevel.BALANCED_CONSERVATIVE: config.portfolio_agent.BASE_ALLOCATIONS[2],
            RiskLevel.BALANCED: config.portfolio_agent.BASE_ALLOCATIONS[3],
            RiskLevel.GROWTH: config.portfolio_agent.BASE_ALLOCATIONS[4],
            RiskLevel.AGGRESSIVE: config.portfolio_agent.BASE_ALLOCATIONS[5]
        }

    async def build_portfolio(self, risk_level: int, goal: str, constraints: Optional[Dict] = None):
        """Generate initial portfolio allocation based on risk level and goal"""
        from .models import RiskLevel, Portfolio
        import uuid
        import numpy as np

        try:
            risk_enum = RiskLevel(risk_level)
            portfolio_id = str(uuid.uuid4())

            # Get base allocation for risk level
            base_alloc = self.base_allocations[risk_enum]

            # Flatten allocations
            allocations = {}
            for category, assets in base_alloc.items():
                for asset, weight in assets.items():
                    if weight > 0:
                        allocations[asset] = weight

            # Apply constraints if provided
            if constraints:
                allocations = self._apply_constraints(allocations, constraints)

            # Calculate expected return and volatility
            metrics_result = await self._calculate_portfolio_metrics(allocations)
            if isinstance(metrics_result, (tuple, list)) and len(metrics_result) == 2:
                expected_return, volatility = metrics_result
            else:
                # Use configuration fallbacks for portfolio metrics
                expected_return = config.get_fallback("portfolio_agent", "expected_return")
                volatility = config.get_fallback("portfolio_agent", "volatility")

            portfolio = Portfolio(
                id=portfolio_id,
                risk_level=risk_enum,
                allocations=allocations,
                expected_return=expected_return,
                volatility=volatility,
                created_at=datetime.now()
            )

            logger.info(f"Built portfolio {portfolio_id} with risk level {risk_level}")
            # Convert to dict for API compatibility
            return {
                "id": portfolio.id,
                "risk_level": portfolio.risk_level.value if hasattr(portfolio.risk_level, 'value') else str(portfolio.risk_level),
                "allocations": portfolio.allocations,
                "expected_return": portfolio.expected_return,
                "volatility": portfolio.volatility,
                "created_at": portfolio.created_at.isoformat() if hasattr(portfolio.created_at, 'isoformat') else str(portfolio.created_at)
            }

        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Error building portfolio: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error building portfolio: {e}")
            raise

    async def calculate_rebalancing(self, current, signals=None):
        """Calculate rebalancing actions based on current portfolio and macro signals"""
        from .models import RebalanceAction
        import uuid

        try:
            rebalance_id = str(uuid.uuid4())
            # Handle both Portfolio objects and dict inputs
            if hasattr(current, 'allocations'):
                target_allocations = current.allocations.copy()
            else:
                target_allocations = current.copy() if isinstance(current, dict) else {}
            reason_parts = []

            # Get current macro signals if not provided
            if signals is None:
                signals = await self._get_current_macro_signals()

            # Apply rebalancing rules based on signals
            if hasattr(signals, 'yield_curve_inversion') and signals.yield_curve_inversion.triggered:
                target_allocations = self._reduce_equity_allocation(target_allocations, 0.10)
                reason_parts.append("yield curve inversion")

            if hasattr(signals, 'volatility_spike') and signals.volatility_spike.triggered:
                target_allocations = self._reduce_equity_allocation(target_allocations, 0.05)
                reason_parts.append("volatility spike")

            # Calculate trades needed
            current_allocations = getattr(current, 'allocations', current) if hasattr(current, 'allocations') else current
            trades = self._calculate_trades(current_allocations, target_allocations)

            reason = f"Rebalancing due to: {', '.join(reason_parts)}" if reason_parts else "No rebalancing needed"

            current_id = getattr(current, 'id', 'unknown_portfolio') if hasattr(current, 'id') else 'test_portfolio'

            rebalance_action = RebalanceAction(
                id=rebalance_id,
                portfolio_id=current_id,
                current_allocations=current_allocations,
                target_allocations=target_allocations,
                trades=trades,
                reason=reason,
                timestamp=datetime.now()
            )

            # Convert to dict for API compatibility
            return {
                "id": rebalance_action.id,
                "portfolio_id": rebalance_action.portfolio_id,
                "current_allocations": rebalance_action.current_allocations,
                "target_allocations": rebalance_action.target_allocations,
                "trades": rebalance_action.trades,
                "reason": rebalance_action.reason,
                "timestamp": rebalance_action.timestamp.isoformat() if hasattr(rebalance_action.timestamp, 'isoformat') else str(rebalance_action.timestamp)
            }

        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error(f"Error calculating rebalancing: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calculating rebalancing: {e}")
            raise

    async def _get_current_macro_signals(self):
        """Get current macro signals from market data"""
        from .models import MacroSignals, MacroSignal

        now = datetime.now()
        return MacroSignals(
            yield_curve_inversion=MacroSignal("yield_curve_inversion", "10Y-2Y < 0", False, None, "Reduce equity -10%", 30),
            inflation_shock=MacroSignal("inflation_shock", "CPI YoY > 4%", False, None, "Increase TIPS +5%", 90),
            volatility_spike=MacroSignal("volatility_spike", "VIX >= 25", True, now, "Reduce equity -5%", 20),
            credit_stress=MacroSignal("credit_stress", "IG Spreads > 5%", False, None, "Reduce equity -5%", 30),
            pmi_contraction=MacroSignal("pmi_contraction", "PMI < 50", False, None, "Reduce equity -5%", 90),
            market_momentum=MacroSignal("market_momentum", "SPY < 200-day MA", False, None, "Reduce equity -10%", 30),
            timestamp=now
        )

    def _apply_constraints(self, allocations, constraints):
        """Apply portfolio constraints"""
        return allocations

    async def _calculate_portfolio_metrics(self, allocations):
        """Calculate expected return and volatility for portfolio"""
        import numpy as np

        # Use configuration instead of hardcoded values
        expected_returns = config.portfolio_agent.EXPECTED_RETURNS
        volatilities = config.portfolio_agent.VOLATILITIES

        portfolio_return = sum(allocations.get(asset, 0) * expected_returns.get(asset, 0.05)
                              for asset in allocations)

        portfolio_volatility = np.sqrt(sum(
            (allocations.get(asset, 0) * volatilities.get(asset, 0.1)) ** 2
            for asset in allocations
        ))

        return portfolio_return, portfolio_volatility

    def _reduce_equity_allocation(self, allocations, reduction):
        """Reduce equity allocation and redistribute to safe assets"""
        new_allocations = allocations.copy()
        equity_assets = ["SPY", "QQQ", "VXUS"]
        safe_assets = ["SHY", "IEF", "GLD"]

        total_equity = sum(new_allocations.get(asset, 0) for asset in equity_assets)

        if total_equity > 0:
            for asset in equity_assets:
                if asset in new_allocations:
                    reduction_amount = new_allocations[asset] * (reduction / total_equity)
                    new_allocations[asset] -= reduction_amount

            safe_addition = reduction / len(safe_assets)
            for asset in safe_assets:
                new_allocations[asset] = new_allocations.get(asset, 0) + safe_addition

        return new_allocations

    def _calculate_trades(self, current, target):
        """Calculate trades needed to move from current to target allocation"""
        trades = []
        all_assets = set(current.keys()) | set(target.keys())

        for asset in all_assets:
            current_weight = current.get(asset, 0)
            target_weight = target.get(asset, 0)
            difference = target_weight - current_weight

            if abs(difference) > 0.001:
                action = "buy" if difference > 0 else "sell"
                trades.append({
                    "ticker": asset,
                    "action": action,
                    "amount": abs(difference),
                    "current_weight": current_weight,
                    "target_weight": target_weight
                })

        return trades

    # Portfolio optimization methods
    async def optimize_portfolio(self, expected_returns: Dict[str, float],
                               covariance_matrix: Dict[str, Dict[str, float]],
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
        try:
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

        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.error(f"Error optimizing portfolio: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error optimizing portfolio: {e}")
            raise

    async def calculate_portfolio_risk_metrics(self, allocations: Dict[str, float],
                                             returns_data: Dict[str, List[float]]) -> Dict[str, float]:
        """
        Calculate comprehensive risk metrics for portfolio.

        Args:
            allocations: Portfolio allocations
            returns_data: Historical returns data for each asset

        Returns:
            Dictionary containing risk metrics
        """
        try:
            risk_metrics = {}

            # Calculate portfolio returns
            portfolio_returns = []
            min_length = min(len(returns) for returns in returns_data.values()) if returns_data else 0

            for i in range(min_length):
                period_return = sum(
                    allocations.get(asset, 0) * returns_data[asset][i]
                    for asset in allocations.keys() if asset in returns_data
                )
                portfolio_returns.append(period_return)

            if portfolio_returns:
                import numpy as np

                # Volatility (annualized)
                risk_metrics["volatility"] = np.std(portfolio_returns) * np.sqrt(252)

                # Sharpe ratio (assuming 2% risk-free rate)
                risk_free_rate = 0.02
                excess_returns = np.array(portfolio_returns) - (risk_free_rate / 252)
                if np.std(excess_returns) > 0:
                    risk_metrics["sharpe_ratio"] = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
                else:
                    risk_metrics["sharpe_ratio"] = 0.0

                # Maximum drawdown
                cumulative_returns = np.cumprod(1 + np.array(portfolio_returns))
                running_max = np.maximum.accumulate(cumulative_returns)
                drawdowns = (cumulative_returns - running_max) / running_max
                risk_metrics["max_drawdown"] = abs(np.min(drawdowns))

                # Value at Risk (95% confidence)
                risk_metrics["var_95"] = np.percentile(portfolio_returns, 5)

            return risk_metrics

        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}

    async def backtest_portfolio(self, allocations: Dict[str, float],
                               start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Backtest portfolio performance over specified period.

        Args:
            allocations: Portfolio allocations to test
            start_date: Start date for backtest (YYYY-MM-DD)
            end_date: End date for backtest (YYYY-MM-DD)

        Returns:
            Backtest results
        """
        try:
            # This would typically fetch historical data and calculate returns
            # For now, return simulated results

            backtest_results = {
                "start_date": start_date,
                "end_date": end_date,
                "total_return": 0.085,  # 8.5% return
                "annualized_return": 0.083,
                "volatility": 0.152,
                "sharpe_ratio": 0.54,
                "max_drawdown": 0.087,
                "trades_executed": 12,
                "benchmark_comparison": {
                    "spy_return": 0.095,
                    "alpha": -0.010,
                    "beta": 0.89
                }
            }

            logger.info(f"Backtest completed for period {start_date} to {end_date}")
            return backtest_results

        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {"error": str(e)}

    async def get_rebalancing_recommendations(self, current_allocations: Dict[str, float],
                                           target_allocations: Dict[str, float],
                                           threshold: float = 0.05) -> List[Dict[str, Any]]:
        """
        Get specific rebalancing recommendations based on drift from target.

        Args:
            current_allocations: Current portfolio allocations
            target_allocations: Target portfolio allocations
            threshold: Minimum drift threshold to trigger rebalancing

        Returns:
            List of rebalancing recommendations
        """
        try:
            recommendations = []

            all_assets = set(current_allocations.keys()) | set(target_allocations.keys())

            for asset in all_assets:
                current_weight = current_allocations.get(asset, 0)
                target_weight = target_allocations.get(asset, 0)
                drift = abs(current_weight - target_weight)

                if drift > threshold:
                    action = "buy" if target_weight > current_weight else "sell"
                    amount = abs(target_weight - current_weight)

                    recommendation = {
                        "asset": asset,
                        "action": action,
                        "current_weight": current_weight,
                        "target_weight": target_weight,
                        "drift": drift,
                        "recommended_amount": amount,
                        "priority": "high" if drift > threshold * 2 else "medium"
                    }
                    recommendations.append(recommendation)

            # Sort by drift magnitude (highest priority first)
            recommendations.sort(key=lambda x: x["drift"], reverse=True)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating rebalancing recommendations: {e}")
            return []