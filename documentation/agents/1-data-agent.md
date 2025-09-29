# Data Agent Documentation

## Data Storage - Supabase Tables

The Data Agent stores its data in the following Supabase tables:
- **`dashboard_market_data`** - Real-time ETF and market data for dashboard display
- **`dashboard_macro_data`** - Macro-economic indicators (CPI, Treasury yields, Fed funds rate, unemployment)
- **`analysis_sessions`** - Session tracking for multi-agent analysis workflows

## Overview

The **Data Agent** is responsible for **real-time market data collection, processing, and macro-economic signal generation**. It serves as the foundational data layer for all other agents in the Neural Capital system, providing up-to-date market information, economic indicators, and risk signals that drive investment decisions.

## What the Data Agent Does

The Data Agent continuously monitors financial markets and economic indicators to:

1. **Collect Real-Time Market Data**: Fetches current prices, volumes, and market metrics from multiple data sources
2. **Process Economic Indicators**: Tracks key macro-economic signals like inflation, unemployment, and interest rates
3. **Generate Risk Signals**: Analyzes market conditions to identify potential risks and opportunities
4. **Provide Historical Context**: Maintains historical data for trend analysis and backtesting
5. **Monitor Market Regimes**: Identifies current market conditions (normal, crisis, elevated volatility)

## Key Inputs

### 1. Data Source Configuration
```python
{
    "sources": ["yahoo", "fred", "polygon"],
    "symbols": ["SPY", "QQQ", "BND", "GLD", "BTC-USD", "^VIX"],
    "update_frequency": "real-time"
}
```

### 2. Economic Indicators
- **Federal Reserve Economic Data (FRED)**:
  - Consumer Price Index (CPI)
  - Unemployment Rate
  - Federal Funds Rate
  - 10-Year Treasury Yield
  - 2-Year Treasury Yield

### 3. Market Data Sources
- **Yahoo Finance**: Stock prices, ETF data, cryptocurrency prices
- **Polygon.io**: Real-time market data and news
- **Alpha Vantage**: Technical indicators and fundamentals

### 4. Request Parameters
```python
{
    "symbol": "SPY",
    "timeframe": "1d",
    "period": "1y",
    "indicators": ["sma", "rsi", "bollinger_bands"]
}
```

## Key Outputs

### 1. Market Data Object
```python
{
    "symbol": "SPY",
    "price": 445.67,
    "previous_close": 442.30,
    "change": 3.37,
    "change_percent": 0.76,
    "volume": 52847392,
    "market_cap": 410000000000,
    "timestamp": "2024-01-15T16:00:00Z"
}
```

### 2. Economic Indicators
```python
{
    "indicator": "CPI",
    "value": 3.2,
    "date": "2024-01-01",
    "frequency": "monthly",
    "unit": "percent_change",
    "source": "FRED"
}
```

### 3. Macro Signals Object
```python
{
    "yield_curve_inversion": {
        "signal_type": "yield_curve_inversion",
        "condition": "10Y-2Y < 0",
        "triggered": true,
        "trigger_date": "2024-01-15T10:30:00Z",
        "action_description": "Reduce equity allocation by 10%",
        "cooldown_days": 30,
        "severity": "high"
    },
    "volatility_spike": {
        "signal_type": "volatility_spike",
        "condition": "VIX >= 25",
        "triggered": false,
        "trigger_date": null,
        "action_description": "Reduce equity allocation by 5%",
        "cooldown_days": 20,
        "severity": "medium"
    },
    "timestamp": "2024-01-15T16:00:00Z"
}
```

### 4. Market Regime Classification
```python
{
    "current_regime": "elevated_volatility",
    "confidence": 0.87,
    "duration_days": 12,
    "characteristics": [
        "VIX above 20",
        "High correlation across asset classes",
        "Increased trading volume"
    ],
    "timestamp": "2024-01-15T16:00:00Z"
}
```

### 5. Technical Indicators
```python
{
    "symbol": "SPY",
    "indicators": {
        "sma_20": 442.15,
        "sma_50": 438.92,
        "rsi": 58.3,
        "bollinger_upper": 448.50,
        "bollinger_lower": 435.80,
        "macd": 2.14,
        "volume_sma": 45000000
    },
    "timestamp": "2024-01-15T16:00:00Z"
}
```

## Core Features

### 1. Multi-Source Data Integration
- **Yahoo Finance Integration**: Real-time stock, ETF, and crypto prices
- **FRED API Integration**: Official economic data from Federal Reserve
- **Polygon.io Integration**: Professional-grade market data
- **Alpha Vantage Integration**: Technical analysis and fundamental data

```python
# Example: Multi-source data collection
async def collect_market_data(self, symbol: str):
    yahoo_data = await self.yahoo_client.get_quote(symbol)
    polygon_data = await self.polygon_client.get_real_time(symbol)
    return self.merge_data_sources(yahoo_data, polygon_data)
```

### 2. Real-Time Signal Generation
- **Yield Curve Monitoring**: Tracks 10Y-2Y spread for inversion signals
- **Volatility Tracking**: Monitors VIX for fear spikes (>25)
- **Credit Stress Detection**: Watches investment-grade spreads
- **PMI Monitoring**: Tracks Purchasing Managers' Index for economic health
- **Market Momentum**: Analyzes price trends vs. moving averages

```python
# Example: Yield curve inversion detection
def check_yield_curve_inversion(self):
    ten_year = self.get_treasury_yield("10Y")
    two_year = self.get_treasury_yield("2Y")

    if ten_year < two_year:
        return MacroSignal(
            signal_type="yield_curve_inversion",
            triggered=True,
            trigger_date=datetime.now(),
            action_description="Reduce equity allocation by 10%"
        )
```

### 3. Market Regime Classification
- **Normal Market Conditions**: VIX < 20, normal correlations
- **Elevated Volatility**: VIX 20-30, increased uncertainty
- **High Volatility Crisis**: VIX > 30, extreme market stress
- **Yield Curve Inversion**: Interest rate warning signals
- **Low Volatility Complacency**: VIX < 15, potential overconfidence

### 4. Rate Limiting and Error Handling
- **Smart Rate Limiting**: Respects API limits across all data sources
- **Retry Logic**: Automatic retries with exponential backoff
- **Fallback Mechanisms**: Switches to alternative data sources on failure
- **Caching**: Intelligent caching to reduce API calls

```python
# Example: Rate limited data collection
@rate_limit(calls_per_minute=60)
async def get_yahoo_data(self, symbol):
    try:
        return await self.yahoo_client.get_quote(symbol)
    except RateLimitError:
        await asyncio.sleep(1)
        return await self.fallback_data_source(symbol)
```

### 5. Data Quality Assurance
- **Price Validation**: Checks for reasonable price movements
- **Volume Validation**: Identifies suspicious volume spikes
- **Cross-Source Verification**: Compares data across multiple sources
- **Anomaly Detection**: Flags unusual market conditions

### 6. Historical Data Management
- **Time Series Storage**: Maintains historical price and indicator data
- **Data Normalization**: Standardizes data formats across sources
- **Backtesting Support**: Provides historical data for strategy testing
- **Data Retention**: Configurable retention policies

## Data Sources and APIs

### Yahoo Finance
- **Purpose**: Primary source for stock, ETF, and crypto prices
- **Coverage**: Global markets, real-time quotes
- **Rate Limits**: 2000 requests/hour
- **Data Types**: OHLCV, market cap, dividend data

### Federal Reserve Economic Data (FRED)
- **Purpose**: Official U.S. economic indicators
- **Coverage**: 800,000+ economic time series
- **Rate Limits**: Unlimited (with API key)
- **Data Types**: CPI, unemployment, interest rates, GDP

### Polygon.io
- **Purpose**: Professional market data
- **Coverage**: Stocks, options, forex, crypto
- **Rate Limits**: Varies by subscription tier
- **Data Types**: Real-time quotes, news, fundamentals

## Configuration

### Environment Variables
```bash
# Data Source API Keys
YAHOO_FINANCE_API_KEY=your_yahoo_key
FRED_API_KEY=your_fred_key
POLYGON_API_KEY=your_polygon_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Rate Limiting
DATA_AGENT_RATE_LIMIT=60  # requests per minute
DATA_CACHE_TTL=300        # seconds

# Update Frequencies
MARKET_DATA_UPDATE_FREQUENCY=60    # seconds
ECONOMIC_DATA_UPDATE_FREQUENCY=3600 # seconds
```

### Asset Universe Configuration
```python
ASSET_UNIVERSE = {
    "equities": ["SPY", "QQQ", "VXUS", "VTI", "VTIAX"],
    "fixed_income": ["BND", "SHY", "IEF", "TLT", "TIPS"],
    "alternatives": ["GLD", "SLV", "VNQ", "PDBC"],
    "crypto": ["BTC-USD", "ETH-USD", "ADA-USD"],
    "volatility": ["^VIX", "^VIX9D"]
}
```

## Error Handling and Reliability

### Retry Mechanisms
- **Exponential Backoff**: Progressive delays between retries
- **Circuit Breaker**: Prevents cascading failures
- **Health Monitoring**: Tracks API endpoint availability

### Fallback Strategies
- **Multiple Data Sources**: Automatic failover between providers
- **Cached Data**: Uses recent cached data when APIs are unavailable
- **Default Values**: Provides reasonable defaults for missing data

### Monitoring and Alerting
- **Data Quality Metrics**: Tracks completeness and accuracy
- **API Health Monitoring**: Monitors response times and error rates
- **Alert System**: Notifies on data source failures or anomalies

## Integration with Other Agents

### Portfolio Agent Integration
```python
# Portfolio Agent requests market data
market_context = await data_agent.get_market_context(timestamp)
macro_signals = await data_agent.get_current_macro_signals()
```

### Planner Agent Integration
```python
# Planner Agent gets economic indicators
economic_data = await data_agent.get_economic_indicators(["CPI", "UNEMPLOYMENT"])
```

### Explainability Agent Integration
```python
# Explainability Agent gets market regime context
market_regime = await data_agent.get_current_market_regime()
```

## Performance and Scalability

### Caching Strategy
- **Redis Integration**: In-memory caching for frequently accessed data
- **TTL Configuration**: Appropriate cache lifetimes for different data types
- **Cache Invalidation**: Smart invalidation on new data arrival

### Async Processing
- **Concurrent API Calls**: Parallel data collection from multiple sources
- **Background Updates**: Continuous data refresh in background tasks
- **Queue Management**: Handles high-volume data requests efficiently

## Security and Compliance

### API Key Management
- **Environment Variables**: Secure storage of API credentials
- **Key Rotation**: Support for rotating API keys
- **Access Control**: Restricted access to sensitive data sources

### Data Privacy
- **No PII Storage**: Only collects public market data
- **Audit Logging**: Tracks all data access and modifications
- **Compliance**: Adheres to financial data regulations

## Testing and Quality Assurance

### Unit Testing
- **API Integration Tests**: Validates data source connections
- **Signal Generation Tests**: Verifies macro signal accuracy
- **Rate Limiting Tests**: Ensures proper rate limit handling

### Integration Testing
- **End-to-End Tests**: Tests complete data pipeline
- **Performance Tests**: Validates response times under load
- **Failover Tests**: Confirms proper fallback behavior

### Data Validation
- **Schema Validation**: Ensures data structure consistency
- **Range Checking**: Validates data within expected ranges
- **Cross-Source Comparison**: Compares data across providers

## API Endpoints and Examples

### GET `/api/v1/agents/data/health`
**Purpose**: Check Data Agent health and data source availability.

**Input Parameters**: None

**Output Example**:
```json
{
  "agent": "data_agent",
  "status": "healthy",
  "data_sources": {
    "yahoo_finance": "healthy",
    "fred": "healthy"
  },
  "timestamp": "2024-01-15T16:00:00Z"
}
```

### GET `/api/v1/agents/data/market/{ticker}`
**Purpose**: Fetch real-time market data for a specific ticker.

**Input Parameters**:
- `ticker` (path): Stock symbol (e.g., "SPY", "AAPL")
- `start_date` (query, optional): Start date for historical data (YYYY-MM-DD)
- `end_date` (query, optional): End date for historical data (YYYY-MM-DD)
- `user_id` (query, optional): User ID for tracking

**Output Example**:
```json
{
  "success": true,
  "agent": "data_agent",
  "ticker": "SPY",
  "data": {
    "symbol": "SPY",
    "price": 445.67,
    "previous_close": 442.30,
    "change": 3.37,
    "change_percent": 0.76,
    "timestamp": "2024-01-15T16:00:00Z"
  },
  "user_id": "anonymous"
}
```

### GET `/api/v1/agents/data/market`
**Purpose**: Fetch market data for all assets in the universe.

**Input Parameters**:
- `user_id` (query, optional): User ID for tracking

**Output Example**:
```json
{
  "success": true,
  "agent": "data_agent",
  "data": [
    {
      "symbol": "SPY",
      "price": 445.67,
      "previous_close": 442.30,
      "change": 3.37,
      "change_percent": 0.76,
      "timestamp": "2024-01-15T16:00:00Z"
    },
    {
      "symbol": "QQQ",
      "price": 378.92,
      "previous_close": 376.15,
      "change": 2.77,
      "change_percent": 0.74,
      "timestamp": "2024-01-15T16:00:00Z"
    }
  ],
  "user_id": "anonymous"
}
```

### GET `/api/v1/agents/data/macro/{indicator}`
**Purpose**: Fetch macro-economic data from FRED API.

**Input Parameters**:
- `indicator` (path): Economic indicator code (e.g., "CPI", "10Y_TREASURY")
- `date_range` (query, optional): Number of days to look back (default: 30)
- `user_id` (query, optional): User ID for tracking

**Output Example**:
```json
{
  "success": true,
  "agent": "data_agent",
  "indicator": "CPI",
  "data": [
    {
      "indicator": "CPI",
      "value": 3.2,
      "date": "2024-01-01T00:00:00Z",
      "frequency": "monthly"
    },
    {
      "indicator": "CPI",
      "value": 3.1,
      "date": "2023-12-01T00:00:00Z",
      "frequency": "monthly"
    }
  ],
  "user_id": "anonymous"
}
```

### GET `/api/v1/agents/data/volatility`
**Purpose**: Fetch VIX and other volatility indicators.

**Input Parameters**:
- `user_id` (query, optional): User ID for tracking

**Output Example**:
```json
{
  "success": true,
  "agent": "data_agent",
  "data": {
    "vix": 18.45,
    "vix_change": -1.23,
    "vix_change_percent": -6.25,
    "timestamp": "2024-01-15T16:00:00Z"
  },
  "user_id": "anonymous"
}
```

### GET `/api/v1/agents/data/technical/{ticker}`
**Purpose**: Fetch technical indicators for a given ticker.

**Input Parameters**:
- `ticker` (path): Stock symbol (e.g., "SPY")
- `period` (query, optional): Time period for historical data (default: "1y")
- `user_id` (query, optional): User ID for tracking

**Output Example**:
```json
{
  "success": true,
  "agent": "data_agent",
  "ticker": "SPY",
  "data": {
    "sma_20": 442.15,
    "sma_50": 438.92,
    "sma_200": 425.33,
    "rsi": 58.3,
    "current_price": 445.67,
    "timestamp": "2024-01-15T16:00:00Z"
  },
  "user_id": "anonymous"
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": {
    "error": "market_data_fetch_failed",
    "message": "Connection timeout to data provider",
    "ticker": "SPY"
  }
}
```

Common error codes:
- `market_data_fetch_failed`: Unable to fetch market data
- `macro_data_unavailable`: Economic indicator not available
- `invalid_ticker`: Invalid stock symbol provided
- `rate_limit_exceeded`: API rate limit exceeded
- `data_source_unavailable`: External data source is down

## Data Generation and Storage Analysis

### 1. Market Data Types Generated

**Primary Market Data Structure** (`MarketData` object):
```python
{
  "symbol": "SPY",           # Stock/ETF ticker symbol
  "price": 445.67,           # Current/latest price
  "previous_close": 442.30,  # Previous closing price
  "change": 3.37,            # Price change in dollars
  "change_percent": 0.76,    # Price change percentage
  "timestamp": "2024-01-15T16:00:00Z"  # Data collection timestamp
}
```

**Asset Universe Coverage**:
- **Equity ETFs**: SPY, QQQ, VXUS, VTI (Core stock market exposure)
- **Fixed Income**: BND, IEF, SHY, TLT (Bond market coverage)
- **Alternatives**: GLD (Gold), VNQ (Real Estate)
- **Crypto ETFs**: BITO (Bitcoin), ETHE (Ethereum)

### 2. Macro-Economic Data Generation

**FRED API Integration** (`MacroData` objects):
```python
{
  "indicator": "CPI",               # Economic indicator name
  "value": 3.2,                    # Indicator value
  "date": "2024-01-01",            # Data point date
  "frequency": "monthly"           # Update frequency
}
```

**Key Economic Indicators Tracked**:
- **CPI**: Consumer Price Index (inflation measurement)
- **Treasury Yields**: 2-Year and 10-Year government bond yields
- **Fed Funds Rate**: Federal Reserve benchmark interest rate
- **Unemployment Rate**: Labor market health indicator
- **PMI**: Purchasing Managers' Index (economic activity)

### 3. Volatility and Risk Metrics

**VIX Volatility Data** (`fetch_volatility_data()`):
```python
{
  "vix": 18.45,                    # Current VIX level
  "vix_change": -1.23,             # Daily change in VIX
  "vix_change_percent": -6.25,     # Percentage change
  "timestamp": "2024-01-15T16:00:00Z"
}
```

**Treasury Yield Analysis** (`fetch_treasury_yields()`):
```python
{
  "2y_yield": 4.85,                # 2-Year Treasury yield
  "10y_yield": 4.45,               # 10-Year Treasury yield
  "2s_10s_spread": -0.40,          # Yield curve spread (10Y - 2Y)
  "timestamp": "2024-01-15T16:00:00Z"
}
```

### 4. Technical Analysis Data

**Technical Indicators** (`fetch_technical_indicators()`):
```python
{
  "sma_20": 442.15,                # 20-day Simple Moving Average
  "sma_50": 438.92,                # 50-day Simple Moving Average
  "sma_200": 425.33,               # 200-day Simple Moving Average
  "rsi": 58.3,                     # Relative Strength Index (14-period)
  "current_price": 445.67,         # Latest price
  "timestamp": "2024-01-15T16:00:00Z"
}
```

### 5. Market Context and Regime Detection

**Comprehensive Market Context** (`get_market_context()`):
```python
{
  "market_data": {
    "spy_price": 445.67,           # S&P 500 ETF price
    "spy_change_percent": 0.76,    # Daily percentage change
    "vix": 18.45,                  # Volatility index
    "yield_spread_2s10s": -0.40,   # Yield curve spread
    "momentum_signal": "bullish"    # Market direction signal
  },
  "macro_indicators": {
    "CPI": {
      "current_value": 3.2,
      "previous_value": 3.1,
      "trend": "up"
    }
  },
  "market_regime": "normal_market_conditions"
}
```

**Market Regime Classifications**:
- `high_volatility_crisis` (VIX > 30)
- `elevated_volatility` (VIX > 25)
- `yield_curve_inversion` (2s10s spread < 0)
- `flattening_curve` (spread < 0.5)
- `low_volatility_complacency` (VIX < 15)
- `normal_market_conditions` (baseline)

### 6. Database Storage Implementation

**Primary Storage Tables**:

#### `dashboard_market_data` Table
Stores all ETF/stock market data with comprehensive metrics:
```sql
Columns:
- symbol, name, asset_type
- price, previous_close, change_value, change_percent
- volume, market_cap, pe_ratio, dividend_yield
- day_high, day_low, year_high, year_low
- sma_20, sma_50, sma_200, rsi
- beta, expense_ratio, total_assets
- context_data (JSON), data_timestamp, updated_at
```

#### `dashboard_macro_data` Table
Stores macro-economic indicators from FRED API:
```sql
Columns:
- indicator_name, value, date
- source, metadata (JSON)
- created_at, updated_at
```

#### `user_dashboard_settings` Table
Stores user preferences and watchlists:
```sql
Columns:
- user_id, watchlist_symbols
- preferred_charts, layout_config
- created_at, updated_at
```

### 7. Data Storage Services

**DashboardDataService Methods**:
- `save_market_data()`: Saves ETF/stock data to dashboard_market_data
- `save_technical_indicators()`: Updates technical analysis fields
- `save_market_context_data()`: Saves VIX and Treasury data
- `save_macro_data()`: Stores economic indicators
- `get_dashboard_data()`: Retrieves all dashboard data
- `save_user_watchlist()`: Manages user preferences

### 8. Real-time Dashboard Integration

**Dashboard ETF Focus** (`fetch_dashboard_etfs()`):
Core holdings tracked for dashboard display:
- **QQQ**: NASDAQ-100 ETF
- **ETH**: Ethereum ETF (mapped to ETHE)
- **SPY**: S&P 500 ETF
- **VXUS**: International stocks ETF
- **IEF**: 7-10 Year Treasury Bond ETF
- **BTC**: Bitcoin ETF (mapped to BITO)
- **BND**: Total Bond Market ETF
- **SHY**: 1-3 Year Treasury Bond ETF

**Data Refresh Process** (`refresh_dashboard_data()`):
1. Fetches current prices for all dashboard ETFs
2. Calculates technical indicators (SMA, RSI)
3. Updates VIX and Treasury yield data
4. Saves macro-economic indicators
5. Returns comprehensive refresh status

### 9. Signal Validation and Quality Assurance

**Signal Validation** (`validate_signals()`):
- Cross-references macro signals with real market data
- Validates yield curve inversions against actual Treasury spreads
- Confirms volatility spikes with current VIX levels
- Returns confidence scores based on data consistency

**Health Monitoring** (`health_check()`):
```python
{
  "yahoo_finance": "healthy",      # Market data source status
  "fred": "healthy"                # Economic data source status
}
```

### 10. Integration with Other Agents

**Portfolio Agent Integration**:
- Provides market data for portfolio optimization
- Supplies volatility data for stress testing
- Delivers macro signals for rebalancing triggers

**Planner Agent Integration**:
- Supplies economic indicators for Monte Carlo simulations
- Provides market context for goal feasibility analysis

**Explainability Agent Integration**:
- Delivers market regime context for decision explanations
- Provides historical market data for contextual analysis

## Data Flow Architecture

```
External APIs → Data Agent → Database Storage → Other Agents
     ↓              ↓              ↓              ↓
Yahoo Finance  fetch_market_   dashboard_     Portfolio
FRED API    →  data() etc.  →  market_data →  Planner
Polygon.io                     tables        Explainability
```

This Data Agent forms the critical foundation of the Neural Capital system, ensuring all other agents have access to accurate, timely, and comprehensive financial market data for making informed investment decisions.