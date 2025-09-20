-- Simplified Dashboard Data Table for Supabase
-- Single table to store latest ETF data with timestamps

-- Drop existing dashboard tables if they exist
DROP TABLE IF EXISTS dashboard_market_data CASCADE;
DROP TABLE IF EXISTS dashboard_technical_indicators CASCADE;
DROP TABLE IF EXISTS dashboard_macro_indicators CASCADE;
DROP TABLE IF EXISTS dashboard_volatility_data CASCADE;
DROP TABLE IF EXISTS dashboard_treasury_yields CASCADE;

-- Drop the old dashboard_data table if it exists (to apply new schema)
DROP TABLE IF EXISTS dashboard_data CASCADE;

-- Create single dashboard data table
CREATE TABLE IF NOT EXISTS dashboard_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE, -- Increased from 10 to 20 for symbols like "2Y_TREASURY"
    name VARCHAR(150) NOT NULL, -- Increased from 100 to 150 for longer ETF names
    asset_type VARCHAR(20) NOT NULL, -- 'ETF', 'CRYPTO_ETF', 'BOND_ETF', 'INDEX', 'YIELD'

    -- Price data
    price DECIMAL(12, 4) DEFAULT 0.00,
    previous_close DECIMAL(12, 4),
    change_value DECIMAL(12, 4),
    change_percent DECIMAL(8, 4),

    -- Volume and market data
    volume BIGINT,
    market_cap BIGINT,
    day_high DECIMAL(12, 4),
    day_low DECIMAL(12, 4),
    year_high DECIMAL(12, 4),
    year_low DECIMAL(12, 4),

    -- Additional ETF info
    pe_ratio DECIMAL(8, 2),
    dividend_yield DECIMAL(6, 4),
    expense_ratio DECIMAL(6, 4),
    total_assets BIGINT,
    beta DECIMAL(6, 3),

    -- Technical indicators (latest values only)
    sma_20 DECIMAL(12, 4),
    sma_50 DECIMAL(12, 4),
    sma_200 DECIMAL(12, 4),
    rsi DECIMAL(6, 2),

    -- Market context (for special symbols like VIX, Treasury yields)
    context_data JSONB, -- For storing flexible market data like VIX, yields, etc.

    -- Timestamps
    data_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- When the market data was generated
    updated_at TIMESTAMPTZ DEFAULT NOW(), -- When record was last updated
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_dashboard_data_symbol ON dashboard_data(symbol);
CREATE INDEX IF NOT EXISTS idx_dashboard_data_asset_type ON dashboard_data(asset_type);
CREATE INDEX IF NOT EXISTS idx_dashboard_data_updated_at ON dashboard_data(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_dashboard_data_timestamp ON dashboard_data(data_timestamp DESC);

-- Insert default ETF records with placeholder data
INSERT INTO dashboard_data (symbol, name, asset_type, price, previous_close, change_value, change_percent, data_timestamp)
VALUES
    ('QQQ', 'Invesco QQQ Trust', 'ETF', 0.00, 0.00, 0.00, 0.00, NOW()),
    ('SPY', 'SPDR S&P 500 ETF', 'ETF', 0.00, 0.00, 0.00, 0.00, NOW()),
    ('VXUS', 'Vanguard Total International Stock Index Fund ETF', 'ETF', 0.00, 0.00, 0.00, 0.00, NOW()),
    ('IEF', 'iShares 7-10 Year Treasury Bond ETF', 'BOND_ETF', 0.00, 0.00, 0.00, 0.00, NOW()),
    ('BND', 'Vanguard Total Bond Market Index Fund', 'BOND_ETF', 0.00, 0.00, 0.00, 0.00, NOW()),
    ('SHY', 'iShares 1-3 Year Treasury Bond ETF', 'BOND_ETF', 0.00, 0.00, 0.00, 0.00, NOW()),
    ('ETHE', 'Grayscale Ethereum Mini Trust ETF', 'CRYPTO_ETF', 0.00, 0.00, 0.00, 0.00, NOW()),
    ('BITO', 'ProShares Bitcoin Strategy ETF', 'CRYPTO_ETF', 0.00, 0.00, 0.00, 0.00, NOW()),
    ('VIX', 'CBOE Volatility Index', 'INDEX', 0.00, 0.00, 0.00, 0.00, NOW()),
    ('2Y_TREASURY', '2-Year Treasury Yield', 'YIELD', 0.00, 0.00, 0.00, 0.00, NOW()),
    ('10Y_TREASURY', '10-Year Treasury Yield', 'YIELD', 0.00, 0.00, 0.00, 0.00, NOW())
ON CONFLICT (symbol) DO NOTHING;

-- User dashboard preferences (keep this simple table)
CREATE TABLE IF NOT EXISTS user_dashboard_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL, -- Reference to users table (will add foreign key constraint if users table exists)
    watchlist_symbols TEXT[] DEFAULT ARRAY[]::TEXT[], -- Array of symbols user wants to track
    layout_preferences JSONB DEFAULT '{}'::JSONB, -- User's dashboard layout preferences
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Add foreign key constraint if users table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        -- Check if the foreign key constraint doesn't already exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints
            WHERE constraint_name = 'fk_user_dashboard_settings_user_id'
            AND table_name = 'user_dashboard_settings'
        ) THEN
            ALTER TABLE user_dashboard_settings
            ADD CONSTRAINT fk_user_dashboard_settings_user_id
            FOREIGN KEY (user_id) REFERENCES users(id_user) ON DELETE CASCADE;
        END IF;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_user_dashboard_user_id ON user_dashboard_settings(user_id);