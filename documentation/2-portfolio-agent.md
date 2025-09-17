# Portfolio Agent Documentation

## Overview

The **Portfolio Agent** is responsible for **algorithmic portfolio optimization and dynamic rebalancing** based on risk tolerance and macro-economic signals. It creates diversified investment portfolios and automatically adjusts them based on market conditions, ensuring optimal risk-return profiles for different investment objectives.

## What the Portfolio Agent Does

The Portfolio Agent provides sophisticated portfolio management capabilities:

1. **Portfolio Construction**: Creates optimized portfolios based on risk levels and investment goals
2. **Dynamic Rebalancing**: Adjusts portfolio allocations in response to macro-economic signals
3. **Risk Management**: Monitors and controls portfolio risk through various metrics and constraints
4. **Performance Attribution**: Calculates expected returns and volatility based on historical data
5. **Macro Signal Integration**: Incorporates economic indicators into portfolio decisions

## Key Inputs

### 1. Risk Level (1-5 Scale)
```python
{
    "risk_level": 3,  # 1=Conservative, 2=Balanced Conservative, 3=Balanced, 4=Growth, 5=Aggressive
    "description": "Balanced portfolio with moderate risk tolerance"
}
```

### 2. Investment Goal
```python
{
    "goal": "growth",
    "description": "Long-term capital appreciation",
    "time_horizon": 30  # years
}
```

### 3. Portfolio Constraints (Optional)
```python
{
    "constraints": {
        "max_equity": 0.8,           # Maximum equity allocation (80%)
        "min_bonds": 0.2,            # Minimum bond allocation (20%)
        "max_single_position": 0.4,  # Maximum single asset weight
        "esg_only": false,           # Environmental/Social/Governance filter
        "exclude_crypto": false      # Exclude cryptocurrency assets
    }
}
```

### 4. Current Portfolio (For Rebalancing)
```python
{
    "current_allocations": {
        "SPY": 0.6,    # S&P 500 ETF - 60%
        "BND": 0.3,    # Bond ETF - 30%
        "GLD": 0.1     # Gold ETF - 10%
    },
    "portfolio_value": 100000  # Total portfolio value
}
```

### 5. Macro Signals (From Data Agent)
```python
{
    "yield_curve_inversion": {
        "triggered": true,
        "severity": "high",
        "action": "Reduce equity allocation by 10%"
    },
    "volatility_spike": {
        "triggered": false,
        "severity": "medium"
    }
}
```

## Key Outputs

### 1. Portfolio Object
```python
{
    "id": "portfolio_123e4567-e89b-12d3-a456-426614174000",
    "risk_level": 3,
    "allocations": {
        "SPY": 0.50,    # S&P 500 ETF
        "QQQ": 0.20,    # NASDAQ ETF
        "VXUS": 0.10,   # International stocks
        "BND": 0.15,    # Total bond market
        "GLD": 0.05     # Gold
    },
    "expected_return": 0.082,      # 8.2% annual expected return
    "volatility": 0.126,           # 12.6% annual volatility
    "sharpe_ratio": 0.65,          # Risk-adjusted return metric
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### 2. Rebalancing Action
```python
{
    "id": "rebalance_987fcdeb-51f2-45a3-9b2d-8c7f5e4d3c2b",
    "portfolio_id": "portfolio_123e4567-e89b-12d3-a456-426614174000",
    "current_allocations": {
        "SPY": 0.70,
        "BND": 0.30
    },
    "target_allocations": {
        "SPY": 0.60,    # Reduced due to macro signal
        "BND": 0.30,
        "SHY": 0.05,    # Added short-term bonds
        "GLD": 0.05     # Added gold for safety
    },
    "trades": [
        {
            "ticker": "SPY",
            "action": "sell",
            "amount": 0.10,
            "current_weight": 0.70,
            "target_weight": 0.60,
            "dollar_amount": 10000
        },
        {
            "ticker": "SHY",
            "action": "buy",
            "amount": 0.05,
            "current_weight": 0.00,
            "target_weight": 0.05,
            "dollar_amount": 5000
        },
        {
            "ticker": "GLD",
            "action": "buy",
            "amount": 0.05,
            "current_weight": 0.00,
            "target_weight": 0.05,
            "dollar_amount": 5000
        }
    ],
    "reason": "Rebalancing due to yield curve inversion and volatility spike signals",
    "expected_return_change": -0.008,  # Slightly lower expected return
    "volatility_change": -0.020,       # Reduced volatility
    "timestamp": "2024-01-15T14:30:00Z"
}
```

### 3. Portfolio Metrics
```python
{
    "portfolio_id": "portfolio_123e4567-e89b-12d3-a456-426614174000",
    "performance_metrics": {
        "expected_return": 0.082,       # 8.2% annual
        "volatility": 0.126,            # 12.6% annual
        "sharpe_ratio": 0.65,           # Risk-adjusted return
        "max_drawdown": 0.15,           # Maximum historical loss
        "var_95": 0.024,                # 95% Value at Risk (daily)
        "beta": 0.85,                   # Market sensitivity
        "alpha": 0.005,                 # Excess return vs benchmark
        "correlation_sp500": 0.88       # Correlation with S&P 500
    },
    "risk_breakdown": {
        "equity_risk": 0.75,            # Portion from equity exposure
        "interest_rate_risk": 0.15,     # Portion from bond duration
        "currency_risk": 0.05,          # International exposure risk
        "commodity_risk": 0.05          # Alternative asset risk
    },
    "timestamp": "2024-01-15T16:00:00Z"
}
```

## Core Features

### 1. Risk-Based Asset Allocation

The Portfolio Agent uses five distinct risk levels, each with optimized base allocations:

#### Conservative (Risk Level 1)
```python
{
    "equities": {"SPY": 0.00},
    "fixed_income": {"BND": 0.25, "IEF": 0.15, "SHY": 0.50},
    "alternatives": {"GLD": 0.10},
    "crypto": {},
    "expected_return": 0.036,  # 3.6%
    "volatility": 0.046        # 4.6%
}
```

#### Balanced Conservative (Risk Level 2)
```python
{
    "equities": {"SPY": 0.20},
    "fixed_income": {"BND": 0.40, "SHY": 0.30},
    "alternatives": {"GLD": 0.10},
    "crypto": {},
    "expected_return": 0.052,  # 5.2%
    "volatility": 0.068        # 6.8%
}
```

#### Balanced (Risk Level 3)
```python
{
    "equities": {"SPY": 0.40, "QQQ": 0.10},
    "fixed_income": {"BND": 0.35, "SHY": 0.05},
    "alternatives": {"GLD": 0.10},
    "crypto": {},
    "expected_return": 0.068,  # 6.8%
    "volatility": 0.092        # 9.2%
}
```

#### Growth (Risk Level 4)
```python
{
    "equities": {"SPY": 0.50, "QQQ": 0.20, "VXUS": 0.10},
    "fixed_income": {"BND": 0.15},
    "alternatives": {"GLD": 0.05},
    "crypto": {},
    "expected_return": 0.084,  # 8.4%
    "volatility": 0.118        # 11.8%
}
```

#### Aggressive (Risk Level 5)
```python
{
    "equities": {"SPY": 0.40, "QQQ": 0.30, "VXUS": 0.20},
    "fixed_income": {},
    "alternatives": {"GLD": 0.05},
    "crypto": {"BTC-USD": 0.05},
    "expected_return": 0.102,  # 10.2%
    "volatility": 0.154        # 15.4%
}
```

### 2. Macro Signal-Based Rebalancing

The Portfolio Agent responds to six key macro-economic signals:

#### Yield Curve Inversion
```python
def handle_yield_curve_inversion(self, current_allocations):
    # Reduce equity allocation by 10%
    # Increase short-term bonds allocation
    # Historical precedent: Signals recession within 12-18 months
    return self._reduce_equity_allocation(current_allocations, 0.10)
```

#### Volatility Spike (VIX > 25)
```python
def handle_volatility_spike(self, current_allocations):
    # Reduce equity allocation by 5%
    # Increase defensive assets
    # Typically indicates market correction
    return self._reduce_equity_allocation(current_allocations, 0.05)
```

#### Inflation Shock (CPI > 4%)
```python
def handle_inflation_shock(self, current_allocations):
    # Increase TIPS (inflation-protected securities) by 5%
    # Reduce duration risk in bonds
    # Add commodity exposure for inflation hedge
    return self._increase_tips_allocation(current_allocations, 0.05)
```

#### Credit Stress (IG Spreads > 500bp)
```python
def handle_credit_stress(self, current_allocations):
    # Reduce equity allocation by 5%
    # Increase government bond allocation
    # Avoid corporate credit exposure
    return self._flight_to_quality(current_allocations)
```

#### PMI Contraction (PMI < 50)
```python
def handle_pmi_contraction(self, current_allocations):
    # Reduce cyclical equity exposure
    # Increase defensive sectors
    # Prepare for economic slowdown
    return self._reduce_cyclical_exposure(current_allocations)
```

#### Market Momentum (Price vs 200-day MA)
```python
def handle_negative_momentum(self, current_allocations):
    # Reduce equity allocation by 10%
    # Implement trend-following reduction
    # Wait for momentum to turn positive
    return self._reduce_equity_allocation(current_allocations, 0.10)
```

### 3. Portfolio Optimization Engine

```python
async def optimize_portfolio(self, risk_level, constraints=None):
    # Get base allocation for risk level
    base_allocation = self.base_allocations[risk_level]

    # Apply constraints if provided
    if constraints:
        base_allocation = self._apply_constraints(base_allocation, constraints)

    # Calculate expected return and risk
    expected_return, volatility = await self._calculate_portfolio_metrics(base_allocation)

    # Create optimized portfolio
    portfolio = Portfolio(
        id=str(uuid.uuid4()),
        risk_level=risk_level,
        allocations=base_allocation,
        expected_return=expected_return,
        volatility=volatility,
        created_at=datetime.now()
    )

    return portfolio
```

### 4. Risk Management and Constraints

#### Position Size Limits
```python
def _apply_position_limits(self, allocations, max_position=0.4):
    """Ensure no single position exceeds maximum weight"""
    for asset, weight in allocations.items():
        if weight > max_position:
            # Redistribute excess weight proportionally
            excess = weight - max_position
            allocations[asset] = max_position
            self._redistribute_weight(allocations, excess, exclude=[asset])
    return allocations
```

#### Sector Diversification
```python
def _apply_sector_limits(self, allocations):
    """Ensure proper sector diversification"""
    sector_limits = {
        "technology": 0.30,
        "healthcare": 0.20,
        "financials": 0.20,
        "consumer": 0.20
    }
    return self._enforce_sector_limits(allocations, sector_limits)
```

#### Currency Exposure Limits
```python
def _apply_currency_limits(self, allocations):
    """Limit foreign currency exposure"""
    international_assets = ["VXUS", "VEA", "VWO"]
    total_international = sum(allocations.get(asset, 0) for asset in international_assets)

    if total_international > 0.30:  # Max 30% international
        scale_factor = 0.30 / total_international
        for asset in international_assets:
            if asset in allocations:
                allocations[asset] *= scale_factor

    return allocations
```

### 5. Performance Attribution and Analytics

```python
async def calculate_performance_attribution(self, portfolio_id, start_date, end_date):
    """Break down portfolio performance by source"""

    performance_data = {
        "total_return": 0.087,  # 8.7% total return
        "attribution": {
            "asset_allocation": 0.045,    # 4.5% from asset allocation
            "security_selection": 0.032,  # 3.2% from security selection
            "timing": 0.010               # 1.0% from market timing
        },
        "factor_exposure": {
            "market_beta": 0.85,          # Market exposure
            "size_factor": 0.12,          # Small cap tilt
            "value_factor": -0.08,        # Growth tilt
            "momentum": 0.15,             # Momentum exposure
            "quality": 0.10               # Quality factor
        },
        "risk_metrics": {
            "tracking_error": 0.045,      # 4.5% tracking error
            "information_ratio": 0.71,    # Excess return / tracking error
            "maximum_drawdown": 0.12,     # 12% max drawdown
            "calmar_ratio": 0.73          # Return / max drawdown
        }
    }

    return performance_data
```

### 6. Transaction Cost Analysis

```python
def calculate_rebalancing_costs(self, current_allocations, target_allocations, portfolio_value):
    """Calculate estimated transaction costs for rebalancing"""

    trades = self._calculate_trades(current_allocations, target_allocations)

    cost_analysis = {
        "total_turnover": 0.15,           # 15% portfolio turnover
        "estimated_costs": {
            "bid_ask_spread": 245.50,      # $245.50 in spread costs
            "commission": 0.00,            # Commission-free ETFs
            "market_impact": 123.25,       # Market impact costs
            "total": 368.75                # Total transaction costs
        },
        "cost_ratio": 0.000369,           # 0.037% of portfolio value
        "break_even_days": 12,            # Days to recover costs
        "net_benefit": 1250.00            # Net benefit after costs
    }

    return cost_analysis
```

## Asset Universe

### Equity Universe
```python
EQUITY_UNIVERSE = {
    "domestic_broad": ["SPY", "VTI", "ITOT"],           # S&P 500 and Total Market
    "domestic_growth": ["QQQ", "VUG", "VONG"],          # NASDAQ and Growth
    "domestic_value": ["VTV", "VYM", "VONV"],           # Value-focused ETFs
    "international_developed": ["VXUS", "VEA", "VTEB"], # Developed markets
    "emerging_markets": ["VWO", "IEMG", "SCHE"],        # Emerging markets
    "small_cap": ["VB", "IWM", "IJR"]                   # Small capitalization
}
```

### Fixed Income Universe
```python
FIXED_INCOME_UNIVERSE = {
    "short_term": ["SHY", "SGOV", "SCHO"],              # 1-3 year bonds
    "intermediate": ["IEF", "GOVT", "SCHG"],            # 3-10 year bonds
    "long_term": ["TLT", "VGLT", "SPTL"],              # 10+ year bonds
    "broad_market": ["BND", "AGG", "SCHZ"],             # Total bond market
    "inflation_protected": ["TIPS", "SCHP", "VTIP"],    # TIPS
    "high_yield": ["HYG", "JNK", "SHYG"],              # High yield corporate
    "international": ["BNDX", "IAGG", "VTEB"]           # International bonds
}
```

### Alternative Assets Universe
```python
ALTERNATIVES_UNIVERSE = {
    "precious_metals": ["GLD", "SLV", "SGOL"],          # Gold and silver
    "real_estate": ["VNQ", "SCHH", "IYR"],             # REITs
    "commodities": ["PDBC", "DJP", "GSG"],             # Broad commodities
    "infrastructure": ["VGI", "IGF", "TOLZ"],          # Infrastructure
    "private_equity": ["PSP", "BPMP", "PSEC"]          # Private equity ETFs
}
```

### Cryptocurrency Universe
```python
CRYPTO_UNIVERSE = {
    "major_coins": ["BTC-USD", "ETH-USD"],              # Bitcoin and Ethereum
    "altcoins": ["ADA-USD", "DOT-USD", "SOL-USD"],     # Alternative coins
    "defi": ["UNI-USD", "AAVE-USD", "COMP-USD"],       # DeFi tokens
    "crypto_etfs": ["BITO", "ETHE", "GBTC"]            # Crypto ETFs
}
```

## Integration with Other Agents

### Data Agent Integration
```python
# Get current macro signals for rebalancing decisions
macro_signals = await self.data_agent.get_current_macro_signals()
market_regime = await self.data_agent.get_current_market_regime()

# Use signals to determine rebalancing need
if macro_signals.yield_curve_inversion.triggered:
    rebalance_action = await self.calculate_rebalancing(
        current_portfolio, macro_signals
    )
```

### Planner Agent Integration
```python
# Get investment strategy from Planner Agent
investment_strategy = await self.planner_agent.generate_strategy(goal, user_profile)

# Create portfolio based on strategy
portfolio = await self.build_portfolio(
    risk_level=investment_strategy.risk_level,
    goal=investment_strategy.goal_type,
    constraints=investment_strategy.constraints
)
```

### Explainability Agent Integration
```python
# Provide decision rationale to Explainability Agent
async def get_decision_rationale(self, action_id):
    return {
        "action_id": action_id,
        "reasoning": "Portfolio rebalanced due to yield curve inversion",
        "macro_context": self.latest_macro_signals,
        "expected_impact": "Reduced portfolio risk by 2%",
        "confidence": 0.85
    }
```

## Configuration and Customization

### Risk Parameters
```python
RISK_PARAMETERS = {
    "max_portfolio_volatility": 0.25,      # 25% maximum portfolio volatility
    "max_single_position": 0.40,           # 40% maximum single asset weight
    "max_sector_exposure": 0.30,           # 30% maximum sector exposure
    "rebalancing_threshold": 0.05,         # 5% drift threshold for rebalancing
    "minimum_trade_size": 0.01,            # 1% minimum trade size
    "transaction_cost_threshold": 0.005    # 0.5% max transaction cost ratio
}
```

### Rebalancing Configuration
```python
REBALANCING_CONFIG = {
    "frequency": "monthly",                 # Monthly rebalancing schedule
    "macro_signal_override": True,          # Allow macro signals to trigger rebalancing
    "drift_threshold": 0.05,               # 5% allocation drift triggers rebalancing
    "minimum_benefit": 0.001,              # 0.1% minimum benefit to rebalance
    "tax_loss_harvesting": True,           # Enable tax-loss harvesting
    "wash_sale_protection": True           # Avoid wash sale violations
}
```

## Performance and Backtesting

### Historical Performance Metrics
```python
def calculate_historical_metrics(self, portfolio, start_date, end_date):
    return {
        "annualized_return": 0.087,         # 8.7% annual return
        "annualized_volatility": 0.124,     # 12.4% annual volatility
        "sharpe_ratio": 0.70,               # Sharpe ratio
        "sortino_ratio": 1.02,              # Downside deviation adjusted
        "maximum_drawdown": 0.18,           # 18% maximum drawdown
        "calmar_ratio": 0.48,               # Return/Max Drawdown
        "win_rate": 0.62,                   # 62% of periods positive
        "average_win": 0.024,               # 2.4% average winning period
        "average_loss": -0.018,             # -1.8% average losing period
        "profit_factor": 1.83,              # Win amount / Loss amount
        "recovery_time": 180                # Days to recover from drawdown
    }
```

### Backtesting Framework
```python
async def backtest_strategy(self, strategy_config, start_date, end_date):
    """Comprehensive backtesting of portfolio strategy"""

    backtest_results = {
        "strategy_name": strategy_config["name"],
        "period": f"{start_date} to {end_date}",
        "total_return": 0.156,              # 15.6% total return
        "annualized_return": 0.087,         # 8.7% annualized
        "benchmark_return": 0.082,          # 8.2% benchmark return
        "excess_return": 0.005,             # 0.5% excess return
        "tracking_error": 0.045,            # 4.5% tracking error
        "information_ratio": 0.11,          # Excess return / tracking error
        "max_drawdown": 0.18,               # 18% maximum drawdown
        "volatility": 0.124,                # 12.4% volatility
        "sharpe_ratio": 0.70,               # Risk-adjusted return
        "trades_executed": 24,              # Number of rebalancing trades
        "turnover": 0.15,                   # 15% annual turnover
        "transaction_costs": 0.0024         # 0.24% transaction costs
    }

    return backtest_results
```

## API Endpoints and Examples

### POST `/api/v1/agents/portfolio/build`
**Purpose**: Generate initial portfolio allocation based on risk level and goal.

**Input Parameters**:
```json
{
  "risk_level": 3,
  "goal": "growth",
  "constraints": {
    "max_equity": 0.8,
    "min_bonds": 0.2,
    "esg_only": false
  },
  "user_id": "user123"
}
```

**Output Example**:
```json
{
  "success": true,
  "agent": "portfolio_agent",
  "portfolio": {
    "id": "portfolio_123e4567-e89b-12d3-a456-426614174000",
    "risk_level": 3,
    "allocations": {
      "SPY": 0.50,
      "QQQ": 0.20,
      "VXUS": 0.10,
      "BND": 0.15,
      "GLD": 0.05
    },
    "expected_return": 0.082,
    "volatility": 0.126,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "user_id": "user123"
}
```

### POST `/api/v1/agents/portfolio/rebalance`
**Purpose**: Calculate rebalancing actions based on current portfolio and macro signals.

**Input Parameters**:
```json
{
  "current_portfolio": {
    "id": "portfolio_123e4567-e89b-12d3-a456-426614174000",
    "allocations": {
      "SPY": 0.70,
      "BND": 0.30
    }
  },
  "signals": {
    "yield_curve_inversion": {
      "triggered": true,
      "severity": "high"
    },
    "volatility_spike": {
      "triggered": false
    }
  },
  "user_id": "user123"
}
```

**Output Example**:
```json
{
  "success": true,
  "agent": "portfolio_agent",
  "rebalance_action": {
    "id": "rebalance_987fcdeb-51f2-45a3-9b2d-8c7f5e4d3c2b",
    "portfolio_id": "portfolio_123e4567-e89b-12d3-a456-426614174000",
    "current_allocations": {
      "SPY": 0.70,
      "BND": 0.30
    },
    "target_allocations": {
      "SPY": 0.60,
      "BND": 0.30,
      "SHY": 0.05,
      "GLD": 0.05
    },
    "trades": [
      {
        "ticker": "SPY",
        "action": "sell",
        "amount": 0.10,
        "current_weight": 0.70,
        "target_weight": 0.60
      },
      {
        "ticker": "SHY",
        "action": "buy",
        "amount": 0.05,
        "current_weight": 0.00,
        "target_weight": 0.05
      },
      {
        "ticker": "GLD",
        "action": "buy",
        "amount": 0.05,
        "current_weight": 0.00,
        "target_weight": 0.05
      }
    ],
    "reason": "Rebalancing due to: yield curve inversion",
    "timestamp": "2024-01-15T14:30:00Z"
  },
  "user_id": "user123"
}
```

### POST `/api/v1/agents/portfolio/optimize`
**Purpose**: Optimize portfolio weights using mean-variance optimization.

**Input Parameters**:
```json
{
  "expected_returns": {
    "SPY": 0.10,
    "BND": 0.04,
    "GLD": 0.06
  },
  "covariance_matrix": {
    "SPY": {"SPY": 0.025, "BND": 0.002, "GLD": 0.008},
    "BND": {"SPY": 0.002, "BND": 0.001, "GLD": 0.001},
    "GLD": {"SPY": 0.008, "BND": 0.001, "GLD": 0.040}
  },
  "risk_tolerance": 0.7,
  "user_id": "user123"
}
```

**Output Example**:
```json
{
  "success": true,
  "agent": "portfolio_agent",
  "optimized_weights": {
    "SPY": 0.65,
    "BND": 0.25,
    "GLD": 0.10
  },
  "expected_return": 0.085,
  "expected_volatility": 0.142,
  "sharpe_ratio": 0.68,
  "user_id": "user123"
}
```

### POST `/api/v1/agents/portfolio/risk-metrics`
**Purpose**: Calculate comprehensive risk metrics for portfolio.

**Input Parameters**:
```json
{
  "allocations": {
    "SPY": 0.60,
    "BND": 0.30,
    "GLD": 0.10
  },
  "returns_data": {
    "SPY": [0.012, -0.008, 0.015, 0.003, -0.012],
    "BND": [0.002, 0.001, -0.001, 0.002, 0.001],
    "GLD": [0.008, -0.005, 0.012, -0.003, 0.007]
  },
  "user_id": "user123"
}
```

**Output Example**:
```json
{
  "success": true,
  "agent": "portfolio_agent",
  "risk_metrics": {
    "volatility": 0.135,
    "sharpe_ratio": 0.72,
    "max_drawdown": 0.087,
    "var_95": 0.024,
    "beta": 0.85,
    "tracking_error": 0.045
  },
  "user_id": "user123"
}
```

### POST `/api/v1/agents/portfolio/backtest`
**Purpose**: Backtest portfolio performance over specified period.

**Input Parameters**:
```json
{
  "allocations": {
    "SPY": 0.60,
    "BND": 0.30,
    "GLD": 0.10
  },
  "start_date": "2020-01-01",
  "end_date": "2023-12-31",
  "user_id": "user123"
}
```

**Output Example**:
```json
{
  "success": true,
  "agent": "portfolio_agent",
  "backtest_results": {
    "start_date": "2020-01-01",
    "end_date": "2023-12-31",
    "total_return": 0.085,
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
  },
  "user_id": "user123"
}
```

### GET `/api/v1/agents/portfolio/recommendations`
**Purpose**: Get specific rebalancing recommendations based on drift from target.

**Input Parameters**:
- `current_allocations` (query): Current portfolio allocations as JSON string
- `target_allocations` (query): Target portfolio allocations as JSON string
- `threshold` (query, optional): Minimum drift threshold (default: 0.05)
- `user_id` (query, optional): User ID for tracking

**Output Example**:
```json
{
  "success": true,
  "agent": "portfolio_agent",
  "recommendations": [
    {
      "asset": "SPY",
      "action": "sell",
      "current_weight": 0.75,
      "target_weight": 0.60,
      "drift": 0.15,
      "recommended_amount": 0.15,
      "priority": "high"
    },
    {
      "asset": "BND",
      "action": "buy",
      "current_weight": 0.20,
      "target_weight": 0.30,
      "drift": 0.10,
      "recommended_amount": 0.10,
      "priority": "medium"
    }
  ],
  "total_drift": 0.25,
  "rebalancing_needed": true,
  "user_id": "user123"
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": {
    "error": "portfolio_optimization_failed",
    "message": "Invalid risk level provided",
    "risk_level": 6
  }
}
```

Common error codes:
- `portfolio_optimization_failed`: Unable to optimize portfolio
- `invalid_risk_level`: Risk level must be between 1 and 5
- `insufficient_data`: Not enough historical data for analysis
- `constraint_violation`: Portfolio constraints cannot be satisfied
- `rebalancing_calculation_failed`: Unable to calculate rebalancing trades

This Portfolio Agent provides sophisticated, institutional-quality portfolio management capabilities, automatically adapting to changing market conditions while maintaining appropriate risk levels for different investor profiles.