-- Dashboard Market Data Tables for Supabase

-- Table for storing real-time market data for dashboard display
CREATE TABLE IF NOT EXISTS dashboard_market_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(12, 4) NOT NULL,
    previous_close DECIMAL(12, 4),
    change_value DECIMAL(12, 4),
    change_percent DECIMAL(8, 4),
    volume BIGINT,
    market_cap BIGINT,
    pe_ratio DECIMAL(8, 2),
    dividend_yield DECIMAL(6, 4),
    day_high DECIMAL(12, 4),
    day_low DECIMAL(12, 4),
    year_high DECIMAL(12, 4),
    year_low DECIMAL(12, 4),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for storing technical indicators
CREATE TABLE IF NOT EXISTS dashboard_technical_indicators (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    sma_20 DECIMAL(12, 4),
    sma_50 DECIMAL(12, 4),
    sma_200 DECIMAL(12, 4),
    rsi DECIMAL(6, 2),
    macd DECIMAL(12, 6),
    macd_signal DECIMAL(12, 6),
    macd_histogram DECIMAL(12, 6),
    bollinger_upper DECIMAL(12, 4),
    bollinger_lower DECIMAL(12, 4),
    bollinger_middle DECIMAL(12, 4),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for storing macro economic indicators
CREATE TABLE IF NOT EXISTS dashboard_macro_indicators (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    indicator_name VARCHAR(50) NOT NULL,
    indicator_code VARCHAR(20) NOT NULL,
    value DECIMAL(12, 6) NOT NULL,
    previous_value DECIMAL(12, 6),
    change_value DECIMAL(12, 6),
    change_percent DECIMAL(8, 4),
    frequency VARCHAR(20) DEFAULT 'daily',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for storing market volatility data
CREATE TABLE IF NOT EXISTS dashboard_volatility_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    vix DECIMAL(8, 4) NOT NULL,
    vix_change DECIMAL(8, 4),
    vix_change_percent DECIMAL(8, 4),
    spy_volatility DECIMAL(8, 4),
    market_regime VARCHAR(50),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for storing treasury yield data
CREATE TABLE IF NOT EXISTS dashboard_treasury_yields (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    yield_1m DECIMAL(8, 4),
    yield_3m DECIMAL(8, 4),
    yield_6m DECIMAL(8, 4),
    yield_1y DECIMAL(8, 4),
    yield_2y DECIMAL(8, 4),
    yield_5y DECIMAL(8, 4),
    yield_10y DECIMAL(8, 4),
    yield_30y DECIMAL(8, 4),
    spread_2s_10s DECIMAL(8, 4),
    spread_3m_10y DECIMAL(8, 4),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for user dashboard preferences
CREATE TABLE IF NOT EXISTS user_dashboard_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id_user) ON DELETE CASCADE,
    watchlist_symbols TEXT[], -- Array of symbols user wants to track
    preferred_charts JSONB, -- User's chart preferences
    refresh_interval INTEGER DEFAULT 300, -- Refresh interval in seconds
    theme VARCHAR(20) DEFAULT 'dark',
    layout_config JSONB, -- Dashboard layout configuration
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_dashboard_market_data_symbol ON dashboard_market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_dashboard_market_data_timestamp ON dashboard_market_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dashboard_technical_symbol ON dashboard_technical_indicators(symbol);
CREATE INDEX IF NOT EXISTS idx_dashboard_technical_timestamp ON dashboard_technical_indicators(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dashboard_macro_indicator ON dashboard_macro_indicators(indicator_code);
CREATE INDEX IF NOT EXISTS idx_dashboard_macro_timestamp ON dashboard_macro_indicators(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dashboard_volatility_timestamp ON dashboard_volatility_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dashboard_treasury_timestamp ON dashboard_treasury_yields(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_dashboard_user_id ON user_dashboard_settings(user_id);

-- Insert default watchlist for your requested ETFs
INSERT INTO dashboard_market_data (symbol, name, price, previous_close, change_value, change_percent)
VALUES
    ('QQQ', 'Invesco QQQ Trust', 0.00, 0.00, 0.00, 0.00),
    ('SPY', 'SPDR S&P 500 ETF', 0.00, 0.00, 0.00, 0.00),
    ('VXUS', 'Vanguard Total International Stock Index Fund ETF', 0.00, 0.00, 0.00, 0.00),
    ('IEF', 'iShares 7-10 Year Treasury Bond ETF', 0.00, 0.00, 0.00, 0.00),
    ('BND', 'Vanguard Total Bond Market Index Fund', 0.00, 0.00, 0.00, 0.00),
    ('SHY', 'iShares 1-3 Year Treasury Bond ETF', 0.00, 0.00, 0.00, 0.00),
    ('ETHE', 'Grayscale Ethereum Mini Trust ETF', 0.00, 0.00, 0.00, 0.00),
    ('BITO', 'ProShares Bitcoin Strategy ETF', 0.00, 0.00, 0.00, 0.00)
ON CONFLICT DO NOTHING;