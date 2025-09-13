from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
import yfinance as yf
import requests
import pandas as pd

from ..utils.yahoo import yahoo
from ..utils.polygon import polygon
from ..utils.fred import fred
from .models import MarketData, MacroData, MacroSignal, MacroSignals

logger = logging.getLogger(__name__)

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

    # Coral Protocol Integration Methods
    async def validate_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate macro signals for other agents via Coral Protocol.

        Args:
            signals: Dictionary containing signal data to validate

        Returns:
            Validation result with confidence score
        """
        try:
            # Fetch current market data for validation
            spy_data = await self.fetch_market_data("SPY")
            vix_data = await self.fetch_volatility_data()
            treasury_data = await self.fetch_treasury_yields()

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
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error validating signals: {e}")
            return {
                "is_valid": False,
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
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
                except:
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
                "timestamp": timestamp or datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting market context: {e}")
            return {
                "error": str(e),
                "timestamp": timestamp or datetime.now().isoformat()
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

        except:
            return "unknown"


# Agent 2: Portfolio Agent
class PortfolioAgent:
    """
    Portfolio Agent responsible for algorithmic portfolio optimization
    and dynamic rebalancing based on risk tolerance and macro signals.
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555"):
        from .coral_client import CoralClient
        from .models import RiskLevel

        self.coral_client = CoralClient(coral_server_url, agent_id="portfolio_agent")

        # Asset universe
        self.equity_universe = ["SPY", "QQQ", "VXUS"]
        self.fixed_income_universe = ["SGOV", "SHY", "IEF", "BND", "TIP"]
        self.alternatives_universe = ["GLD"]
        self.crypto_universe = ["BTC-USD", "ETH-USD"]

        # Risk tier base allocations
        self.base_allocations = {
            RiskLevel.CONSERVATIVE: {
                "equities": {"SPY": 0.0, "QQQ": 0.0, "VXUS": 0.0},
                "fixed_income": {"BND": 0.25, "IEF": 0.15, "SHY": 0.50},
                "alternatives": {"GLD": 0.10},
                "crypto": {"BTC-USD": 0.0, "ETH-USD": 0.0}
            },
            RiskLevel.BALANCED_CONSERVATIVE: {
                "equities": {"SPY": 0.25, "QQQ": 0.0, "VXUS": 0.10},
                "fixed_income": {"BND": 0.35, "IEF": 0.20, "SHY": 0.0},
                "alternatives": {"GLD": 0.10},
                "crypto": {"BTC-USD": 0.0, "ETH-USD": 0.0}
            },
            RiskLevel.BALANCED: {
                "equities": {"SPY": 0.40, "QQQ": 0.0, "VXUS": 0.20},
                "fixed_income": {"BND": 0.20, "IEF": 0.10, "SHY": 0.0},
                "alternatives": {"GLD": 0.10},
                "crypto": {"BTC-USD": 0.0, "ETH-USD": 0.0}
            },
            RiskLevel.GROWTH: {
                "equities": {"SPY": 0.45, "QQQ": 0.25, "VXUS": 0.20},
                "fixed_income": {"BND": 0.05, "IEF": 0.0, "SHY": 0.0},
                "alternatives": {"GLD": 0.05},
                "crypto": {"BTC-USD": 0.0, "ETH-USD": 0.0}
            },
            RiskLevel.AGGRESSIVE: {
                "equities": {"SPY": 0.40, "QQQ": 0.30, "VXUS": 0.20},
                "fixed_income": {"BND": 0.0, "IEF": 0.0, "SHY": 0.0},
                "alternatives": {"GLD": 0.05},
                "crypto": {"BTC-USD": 0.05, "ETH-USD": 0.0}
            }
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
            expected_return, volatility = await self._calculate_portfolio_metrics(allocations)

            portfolio = Portfolio(
                id=portfolio_id,
                risk_level=risk_enum,
                allocations=allocations,
                expected_return=expected_return,
                volatility=volatility,
                created_at=datetime.now()
            )

            logger.info(f"Built portfolio {portfolio_id} with risk level {risk_level}")
            return portfolio

        except Exception as e:
            logger.error(f"Error building portfolio: {e}")
            raise

    async def calculate_rebalancing(self, current, signals=None):
        """Calculate rebalancing actions based on current portfolio and macro signals"""
        from .models import RebalanceAction
        import uuid

        try:
            rebalance_id = str(uuid.uuid4())
            target_allocations = current.allocations.copy()
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
            trades = self._calculate_trades(current.allocations, target_allocations)

            reason = f"Rebalancing due to: {', '.join(reason_parts)}" if reason_parts else "No rebalancing needed"

            rebalance_action = RebalanceAction(
                id=rebalance_id,
                portfolio_id=current.id,
                current_allocations=current.allocations,
                target_allocations=target_allocations,
                trades=trades,
                reason=reason,
                timestamp=datetime.now()
            )

            return rebalance_action

        except Exception as e:
            logger.error(f"Error calculating rebalancing: {e}")
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

        expected_returns = {
            "SPY": 0.10, "QQQ": 0.12, "VXUS": 0.08,
            "SGOV": 0.05, "SHY": 0.03, "IEF": 0.04, "BND": 0.04, "TIP": 0.03,
            "GLD": 0.05, "BTC-USD": 0.15, "ETH-USD": 0.18
        }

        volatilities = {
            "SPY": 0.16, "QQQ": 0.20, "VXUS": 0.18,
            "SGOV": 0.02, "SHY": 0.03, "IEF": 0.05, "BND": 0.04, "TIP": 0.04,
            "GLD": 0.15, "BTC-USD": 0.80, "ETH-USD": 0.90
        }

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


# Agent 3: Financial Planner Agent
class PlannerAgent:
    """
    Financial Planner Agent responsible for natural language goal interpretation
    and lifecycle-based investment planning.
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555"):
        from .coral_client import CoralClient
        from .models import GoalType, RiskLevel

        self.coral_client = CoralClient(coral_server_url, agent_id="planner_agent")

        # Goal-based strategy mapping
        self.goal_strategies = {
            GoalType.HOUSE_DOWN_PAYMENT: {
                "time_horizon": (3, 7),
                "allocation": {"bonds": 0.80, "equities": 0.20},
                "risk_level": RiskLevel.CONSERVATIVE
            },
            GoalType.RETIREMENT: {
                "time_horizon": (20, 40),
                "allocation": {"equities": 0.80, "bonds": 0.15, "alternatives": 0.05},
                "risk_level": RiskLevel.GROWTH
            },
            GoalType.EMERGENCY_FUND: {
                "time_horizon": (0, 1),
                "allocation": {"cash": 1.0},
                "risk_level": RiskLevel.CONSERVATIVE
            },
            GoalType.CHILD_EDUCATION: {
                "time_horizon": (10, 18),
                "allocation": {"equities": 0.60, "bonds": 0.40},
                "risk_level": RiskLevel.BALANCED
            }
        }

        # Keywords for goal parsing
        self.goal_keywords = {
            GoalType.HOUSE_DOWN_PAYMENT: [
                "house", "home", "down payment", "mortgage", "property", "real estate"
            ],
            GoalType.RETIREMENT: [
                "retirement", "retire", "pension", "401k", "ira", "nest egg"
            ],
            GoalType.EMERGENCY_FUND: [
                "emergency", "emergency fund", "safety net", "rainy day"
            ],
            GoalType.CHILD_EDUCATION: [
                "education", "college", "university", "school", "tuition", "529"
            ]
        }

    async def parse_goal(self, goal_text: str):
        """Extract goal parameters from natural language text"""
        from .models import GoalParameters

        try:
            # Use LLM agent for advanced parsing via Coral Protocol
            llm_response = await self.process_natural_language_goal(goal_text)

            # Extract goal type
            goal_type = self._extract_goal_type(goal_text, llm_response)

            # Extract target amount
            target_amount = self._extract_amount(goal_text, llm_response)

            # Extract time horizon
            time_horizon = self._extract_time_horizon(goal_text, llm_response)

            # Extract age-related information
            current_age = self._extract_age(goal_text, llm_response)

            # Set defaults based on goal type
            strategy = self.goal_strategies.get(goal_type, {})
            risk_tolerance = strategy.get("risk_level")

            goal_params = GoalParameters(
                goal_type=goal_type,
                target_amount=target_amount,
                time_horizon_years=time_horizon,
                current_age=current_age,
                risk_tolerance=risk_tolerance
            )

            logger.info(f"Parsed goal: {goal_type.value}, ${target_amount:,.0f}, {time_horizon} years")
            return goal_params

        except Exception as e:
            logger.error(f"Error parsing goal: {e}")
            raise

    async def generate_strategy(self, goal, user_profile):
        """Generate investment strategy based on goal and user profile"""
        from .models import InvestmentStrategy

        try:
            # Get base strategy for goal type
            base_strategy = self.goal_strategies.get(goal.goal_type, {})

            # Adjust allocation based on time horizon and age
            allocation = self._adjust_allocation_for_age_and_horizon(
                base_strategy.get("allocation", {}),
                user_profile.age,
                goal.time_horizon_years
            )

            # Calculate expected return
            expected_return = self._calculate_expected_return(allocation)

            # Build constraints
            constraints = self._build_constraints(goal, user_profile)

            strategy = InvestmentStrategy(
                goal_type=goal.goal_type,
                recommended_allocation=allocation,
                risk_level=goal.risk_tolerance or user_profile.risk_tolerance,
                expected_return=expected_return,
                time_horizon=goal.time_horizon_years,
                constraints=constraints
            )

            return strategy

        except Exception as e:
            logger.error(f"Error generating strategy: {e}")
            raise

    def build_glide_path(self, age: int, retirement_age: int = 65):
        """Calculate age-appropriate allocation glide path"""
        from .models import GlidePath

        try:
            age_ranges = {}

            if age < 35:
                age_ranges["<35"] = {"equities": 0.90, "bonds": 0.10, "cash": 0.00}
            elif age < 45:
                age_ranges["35-44"] = {"equities": 0.80, "bonds": 0.20, "cash": 0.00}
            elif age < 55:
                age_ranges["45-54"] = {"equities": 0.70, "bonds": 0.25, "alternatives": 0.05}
            elif age < 65:
                age_ranges["55-64"] = {"equities": 0.60, "bonds": 0.35, "alternatives": 0.05}
            else:
                age_ranges["65+"] = {"equities": 0.40, "bonds": 0.50, "cash": 0.10}

            glide_path = GlidePath(
                age_ranges=age_ranges,
                target_retirement_age=retirement_age
            )

            return glide_path

        except Exception as e:
            logger.error(f"Error building glide path: {e}")
            raise

    async def process_natural_language_goal(self, goal_text: str):
        """Use external LLM agents for advanced NLP processing via Coral Protocol"""
        try:
            llm_response = await self.coral_client.invoke_agent("llm_agent", "parse_goal", {
                "text": goal_text,
                "context": "financial_planning"
            })
            return llm_response
        except Exception as e:
            logger.error(f"Error processing natural language goal: {e}")
            return {"goal_type": "retirement", "target_amount": 1000000, "time_horizon": 30}

    def _extract_goal_type(self, goal_text: str, llm_response: Dict):
        """Extract goal type from text and LLM response"""
        from .models import GoalType

        goal_text_lower = goal_text.lower()

        # First try LLM response
        if llm_response.get("goal_type"):
            try:
                return GoalType(llm_response["goal_type"])
            except ValueError:
                pass

        # Fallback to keyword matching
        for goal_type, keywords in self.goal_keywords.items():
            if any(keyword in goal_text_lower for keyword in keywords):
                return goal_type

        return GoalType.RETIREMENT

    def _extract_amount(self, goal_text: str, llm_response: Dict):
        """Extract target amount from text"""
        import re
        from .models import GoalType

        if llm_response.get("target_amount"):
            return float(llm_response["target_amount"])

        # Regex extraction logic
        amount_patterns = [
            r'\$?([\d,]+(?:\.\d{2})?)\s*(?:million|mil|m)',
            r'\$?([\d,]+(?:\.\d{2})?)\s*(?:thousand|k)',
            r'\$?([\d,]+(?:\.\d{2})?)'
        ]

        for pattern in amount_patterns:
            matches = re.findall(pattern, goal_text.lower())
            if matches:
                amount_str = matches[0].replace(",", "")
                amount = float(amount_str)

                multipliers = {"million": 1000000, "mil": 1000000, "m": 1000000, "thousand": 1000, "k": 1000}
                for mult_word, mult_value in multipliers.items():
                    if mult_word in goal_text.lower():
                        amount *= mult_value
                        break

                return amount

        # Default amounts
        default_amounts = {
            GoalType.HOUSE_DOWN_PAYMENT: 100000,
            GoalType.RETIREMENT: 1000000,
            GoalType.EMERGENCY_FUND: 25000,
            GoalType.CHILD_EDUCATION: 200000
        }

        goal_type = self._extract_goal_type(goal_text, llm_response)
        return default_amounts.get(goal_type, 100000)

    def _extract_time_horizon(self, goal_text: str, llm_response: Dict):
        """Extract time horizon from text"""
        import re
        from .models import GoalType

        if llm_response.get("time_horizon"):
            return int(llm_response["time_horizon"])

        time_patterns = [
            r'(\d+)\s*years?',
            r'in\s*(\d+)\s*years?',
            r'(\d+)\s*yrs?'
        ]

        for pattern in time_patterns:
            matches = re.findall(pattern, goal_text.lower())
            if matches:
                return int(matches[0])

        goal_type = self._extract_goal_type(goal_text, llm_response)
        default_horizons = {
            GoalType.HOUSE_DOWN_PAYMENT: 5,
            GoalType.RETIREMENT: 30,
            GoalType.EMERGENCY_FUND: 1,
            GoalType.CHILD_EDUCATION: 15
        }

        return default_horizons.get(goal_type, 10)

    def _extract_age(self, goal_text: str, llm_response: Dict):
        """Extract age from text"""
        import re

        age_patterns = [
            r'i.?m\s*(\d+)',
            r'age\s*(\d+)',
            r'(\d+)\s*years?\s*old'
        ]

        for pattern in age_patterns:
            matches = re.findall(pattern, goal_text.lower())
            if matches:
                age = int(matches[0])
                if 18 <= age <= 100:
                    return age
        return None

    def _adjust_allocation_for_age_and_horizon(self, base_allocation, age, horizon):
        """Adjust allocation based on age and time horizon"""
        allocation = base_allocation.copy()

        if age > 60:
            if "bonds" in allocation:
                allocation["bonds"] = min(allocation["bonds"] + 0.1, 0.8)
            if "equities" in allocation:
                allocation["equities"] = max(allocation["equities"] - 0.1, 0.2)

        if horizon < 5:
            if "cash" in allocation:
                allocation["cash"] = allocation.get("cash", 0) + 0.1
            if "equities" in allocation:
                allocation["equities"] = max(allocation["equities"] - 0.1, 0.1)

        # Normalize
        total = sum(allocation.values())
        if total > 0:
            allocation = {k: v / total for k, v in allocation.items()}

        return allocation

    def _calculate_expected_return(self, allocation):
        """Calculate expected portfolio return"""
        expected_returns = {
            "equities": 0.10,
            "bonds": 0.04,
            "cash": 0.02,
            "alternatives": 0.06
        }

        return sum(allocation.get(asset_class, 0) * expected_returns.get(asset_class, 0.05)
                  for asset_class in allocation)

    def _build_constraints(self, goal, user_profile):
        """Build investment constraints"""
        from .models import GoalType

        constraints = {
            "goal_type": goal.goal_type.value,
            "time_horizon": goal.time_horizon_years,
            "liquidity_needs": "high" if goal.goal_type == GoalType.EMERGENCY_FUND else "low"
        }

        if goal.current_age and goal.current_age > 60:
            constraints["max_equity_allocation"] = 0.7
            constraints["min_bond_allocation"] = 0.3

        return constraints


# Agent 4: Explainability Agent
class ExplainabilityAgent:
    """
    Explainability Agent responsible for financial jargon translation
    and decision rationale generation.
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555"):
        from .coral_client import CoralClient

        self.coral_client = CoralClient(coral_server_url, agent_id="explainability_agent")

        # Jargon translation dictionary
        self.jargon_dictionary = {
            "yield_curve_inversion": "When long-term interest rates fall below short-term rates",
            "credit_spreads": "The extra interest risky bonds pay compared to safe government bonds",
            "vix_spike": "When the market fear indicator (VIX) rises sharply",
            "p/e_ratio": "How expensive stocks are compared to their earnings",
            "duration_risk": "How sensitive bond prices are to interest rate changes",
            "market_momentum": "Whether stock prices are trending up or down",
            "volatility": "How much prices move up and down",
            "rebalancing": "Adjusting your investment mix back to target percentages",
            "macro_signals": "Economic indicators that suggest market direction",
            "risk_parity": "Balancing risk equally across different investments",
            "correlation": "How similarly different investments move together",
            "alpha": "Investment returns above what the market provides",
            "beta": "How much an investment moves relative to the overall market",
            "sharpe_ratio": "Risk-adjusted returns (higher is better)",
            "drawdown": "The largest peak-to-trough decline in portfolio value"
        }

        # Risk communication templates
        self.risk_templates = {
            "low": "Minimal chance of loss, but growth may be limited. Suitable for near-term goals.",
            "moderate": "Some ups and downs expected, but historically recovers within 2-3 years. Good for medium-term goals.",
            "high": "Significant volatility possible, but higher potential returns over long periods. Best for long-term goals only.",
            "very_high": "Large swings in value are common. Only suitable for long-term goals with high risk tolerance."
        }

    async def explain_decision(self, action, context=None):
        """Generate comprehensive explanation for a decision"""
        from .models import ExplanationResponse

        try:
            # Gather context from all relevant agents
            comprehensive_context = await self.gather_multi_agent_context(action)

            # Generate explanation
            explanation = await self.generate_comprehensive_explanation(action, comprehensive_context)

            # Generate risk assessment
            risk_assessment = self._generate_risk_assessment(action, comprehensive_context)

            # Provide historical context
            historical_context = self._provide_historical_context(action)

            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(comprehensive_context)

            # Create verification hash
            verification_hash = self.coral_client.create_verification_hash(explanation, action.id)

            response = ExplanationResponse(
                action_id=action.id,
                explanation=explanation,
                risk_assessment=risk_assessment,
                historical_context=historical_context,
                confidence_score=confidence_score,
                verification_hash=verification_hash
            )

            logger.info(f"Generated explanation for action {action.id}")
            return response

        except Exception as e:
            logger.error(f"Error explaining decision: {e}")
            raise

    def translate_jargon(self, technical_text: str):
        """Convert technical financial terms to plain English"""
        try:
            import re
            translated_text = technical_text

            for term, explanation in self.jargon_dictionary.items():
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                translated_text = pattern.sub(f"{explanation}", translated_text)

            return translated_text

        except Exception as e:
            logger.error(f"Error translating jargon: {e}")
            return technical_text

    def generate_risk_warning(self, portfolio):
        """Generate risk warning based on portfolio composition"""
        try:
            risk_level = portfolio.risk_level.value
            volatility = portfolio.volatility

            if risk_level <= 2 and volatility < 0.1:
                risk_category = "low"
            elif risk_level <= 3 and volatility < 0.15:
                risk_category = "moderate"
            elif risk_level <= 4 and volatility < 0.25:
                risk_category = "high"
            else:
                risk_category = "very_high"

            base_warning = self.risk_templates[risk_category]

            # Add specific warnings
            specific_warnings = []

            max_allocation = max(portfolio.allocations.values()) if portfolio.allocations else 0
            if max_allocation > 0.4:
                specific_warnings.append("High concentration in single asset increases risk.")

            crypto_assets = ["BTC-USD", "ETH-USD"]
            crypto_exposure = sum(portfolio.allocations.get(asset, 0) for asset in crypto_assets)
            if crypto_exposure > 0:
                specific_warnings.append("Cryptocurrency investments are highly volatile and speculative.")

            warning = base_warning
            if specific_warnings:
                warning += " Additional considerations: " + " ".join(specific_warnings)

            return warning

        except Exception as e:
            logger.error(f"Error generating risk warning: {e}")
            return "Please carefully consider the risks associated with this investment strategy."

    async def gather_multi_agent_context(self, action):
        """Query all relevant agents for decision context via Coral Protocol"""
        try:
            context = {}

            # Get portfolio reasoning if action is from portfolio agent
            if action.agent_source == "portfolio_agent":
                try:
                    context["portfolio_rationale"] = await self.coral_client.invoke_agent(
                        "portfolio_agent", "get_decision_rationale", {"action_id": action.id}
                    )
                except Exception as e:
                    logger.warning(f"Failed to get portfolio rationale: {e}")
                    context["portfolio_rationale"] = {"error": str(e)}

            # Get market data context
            try:
                context["market_data"] = await self.coral_client.invoke_agent(
                    "data_agent", "get_market_context", {"timestamp": action.timestamp.isoformat()}
                )
            except Exception as e:
                logger.warning(f"Failed to get market context: {e}")
                context["market_data"] = {"error": str(e)}

            return context

        except Exception as e:
            logger.error(f"Error gathering multi-agent context: {e}")
            return {}

    async def generate_comprehensive_explanation(self, action, context):
        """Generate explanation using context from all relevant agents"""
        try:
            explanation_parts = []

            explanation_parts.append(f"Action taken: {action.action_type}")

            portfolio_rationale = context.get("portfolio_rationale", {})
            if portfolio_rationale and not portfolio_rationale.get("error"):
                reason = portfolio_rationale.get("reason", "Portfolio adjustment")
                explanation_parts.append(f"Reason: {reason}")

            market_data = context.get("market_data", {})
            if market_data and not market_data.get("error"):
                market_regime = market_data.get("market_regime", "normal_market_conditions")
                market_regime_explanation = self._explain_market_regime(market_regime)
                explanation_parts.append(f"Market conditions: {market_regime_explanation}")

            full_explanation = " ".join(explanation_parts)
            plain_english_explanation = self.translate_jargon(full_explanation)

            return plain_english_explanation

        except Exception as e:
            logger.error(f"Error generating comprehensive explanation: {e}")
            return f"Decision made based on {action.action_type} with current market conditions."

    def _generate_risk_assessment(self, action, context):
        """Generate risk assessment for the action"""
        try:
            risk_factors = []

            market_data = context.get("market_data", {})
            if market_data and not market_data.get("error"):
                market_regime = market_data.get("market_regime", "normal")

                if "crisis" in market_regime:
                    risk_factors.append("High risk due to crisis market conditions")
                elif "volatility" in market_regime:
                    risk_factors.append("Elevated risk due to increased market volatility")

            if not risk_factors:
                return self.risk_templates["moderate"]

            return "Risk factors identified: " + "; ".join(risk_factors) + ". " + self.risk_templates["moderate"]

        except Exception as e:
            logger.error(f"Error generating risk assessment: {e}")
            return self.risk_templates["moderate"]

    def _provide_historical_context(self, action):
        """Provide historical context for the action"""
        try:
            if action.action_type == "rebalancing":
                if "volatility" in str(action.parameters).lower():
                    return "VIX spikes above 25 historically coincide with market corrections, but markets usually recover within 6 months."
                elif "yield" in str(action.parameters).lower():
                    return "Yield curve inversions historically signal recession within 12-18 months, with markets typically declining 20-30% but recovering within 2-3 years."

            return "Historical patterns suggest similar market conditions typically resolve within 6-12 months."

        except Exception as e:
            logger.error(f"Error providing historical context: {e}")
            return "Historical context analysis is not available."

    def _calculate_confidence_score(self, context):
        """Calculate confidence score based on available context"""
        try:
            confidence_factors = []

            portfolio_rationale = context.get("portfolio_rationale", {})
            if portfolio_rationale and not portfolio_rationale.get("error"):
                conf = portfolio_rationale.get("confidence", 0.5)
                confidence_factors.append(conf)

            market_data = context.get("market_data", {})
            if market_data and not market_data.get("error"):
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.3)

            if confidence_factors:
                return sum(confidence_factors) / len(confidence_factors)
            else:
                return 0.5

        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.5

    def _explain_market_regime(self, market_regime):
        """Explain market regime in plain English"""
        regime_explanations = {
            "normal_market_conditions": "Market conditions are within normal ranges",
            "high_volatility_crisis": "Markets are experiencing extreme volatility and stress",
            "elevated_volatility": "Markets are more volatile than usual, indicating uncertainty",
            "yield_curve_inversion": "Interest rate patterns suggest potential economic slowdown",
            "flattening_curve": "Interest rate differences are narrowing, which may signal caution",
            "low_volatility_complacency": "Markets are unusually calm, which may indicate complacency"
        }

        return regime_explanations.get(market_regime, f"Current market regime: {market_regime}")