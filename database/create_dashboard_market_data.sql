-- SQL script to create dashboard_market_data table in Supabase
-- This table stores real-time market data from Agent 1 (Data Agent)

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the dashboard_market_data table
CREATE TABLE IF NOT EXISTS dashboard_market_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    asset_type VARCHAR(20) DEFAULT 'ETF',
    price DECIMAL(12, 4) NOT NULL DEFAULT 0,
    previous_close DECIMAL(12, 4) DEFAULT 0,
    change_value DECIMAL(12, 4) DEFAULT 0,
    change_percent DECIMAL(8, 4) DEFAULT 0,
    volume BIGINT DEFAULT 0,
    market_cap BIGINT DEFAULT 0,
    pe_ratio DECIMAL(8, 2) DEFAULT NULL,
    dividend_yield DECIMAL(6, 4) DEFAULT NULL,
    day_high DECIMAL(12, 4) DEFAULT 0,
    day_low DECIMAL(12, 4) DEFAULT 0,
    year_high DECIMAL(12, 4) DEFAULT 0,
    year_low DECIMAL(12, 4) DEFAULT 0,
    expense_ratio DECIMAL(6, 4) DEFAULT NULL,
    total_assets BIGINT DEFAULT NULL,
    beta DECIMAL(6, 3) DEFAULT NULL,
    -- Technical indicators
    sma_20 DECIMAL(12, 4) DEFAULT NULL,
    sma_50 DECIMAL(12, 4) DEFAULT NULL,
    sma_200 DECIMAL(12, 4) DEFAULT NULL,
    rsi DECIMAL(6, 2) DEFAULT NULL,
    -- Context data for special indicators like VIX, Treasury yields
    context_data JSONB DEFAULT NULL,
    -- Timestamps
    data_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_dashboard_market_data_symbol ON dashboard_market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_dashboard_market_data_asset_type ON dashboard_market_data(asset_type);
CREATE INDEX IF NOT EXISTS idx_dashboard_market_data_updated_at ON dashboard_market_data(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_dashboard_market_data_data_timestamp ON dashboard_market_data(data_timestamp DESC);

-- Create function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_dashboard_market_data_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at on row changes
DROP TRIGGER IF EXISTS trigger_update_dashboard_market_data_updated_at ON dashboard_market_data;
CREATE TRIGGER trigger_update_dashboard_market_data_updated_at
    BEFORE UPDATE ON dashboard_market_data
    FOR EACH ROW
    EXECUTE FUNCTION update_dashboard_market_data_updated_at();

-- Insert default data for the dashboard ETFs from Agent 1
INSERT INTO dashboard_market_data (symbol, name, asset_type, price, previous_close, change_value, change_percent)
VALUES
    ('QQQ', 'Invesco QQQ Trust', 'ETF', 0.00, 0.00, 0.00, 0.00),
    ('SPY', 'SPDR S&P 500 ETF', 'ETF', 0.00, 0.00, 0.00, 0.00),
    ('VXUS', 'Vanguard Total International Stock ETF', 'ETF', 0.00, 0.00, 0.00, 0.00),
    ('IEF', 'iShares 7-10 Year Treasury Bond ETF', 'BOND_ETF', 0.00, 0.00, 0.00, 0.00),
    ('BND', 'Vanguard Total Bond Market ETF', 'BOND_ETF', 0.00, 0.00, 0.00, 0.00),
    ('SHY', 'iShares 1-3 Year Treasury Bond ETF', 'BOND_ETF', 0.00, 0.00, 0.00, 0.00),
    ('ETHE', 'Grayscale Ethereum Mini Trust ETF', 'CRYPTO_ETF', 0.00, 0.00, 0.00, 0.00),
    ('BITO', 'ProShares Bitcoin Strategy ETF', 'CRYPTO_ETF', 0.00, 0.00, 0.00, 0.00),
    ('VIX', 'CBOE Volatility Index', 'INDEX', 0.00, 0.00, 0.00, 0.00),
    ('2Y_TREASURY', '2-Year Treasury Yield', 'YIELD', 0.00, 0.00, 0.00, 0.00),
    ('10Y_TREASURY', '10-Year Treasury Yield', 'YIELD', 0.00, 0.00, 0.00, 0.00)
ON CONFLICT (symbol) DO NOTHING;

-- Grant necessary permissions (adjust as needed for your Supabase setup)
-- Note: In Supabase, these permissions are typically managed through the dashboard
-- ALTER TABLE dashboard_market_data ENABLE ROW LEVEL SECURITY;

-- Example RLS policies (uncomment and adjust as needed):
-- CREATE POLICY "Allow public read access" ON dashboard_market_data FOR SELECT USING (true);
-- CREATE POLICY "Allow service role full access" ON dashboard_market_data FOR ALL USING (auth.role() = 'service_role');

-- Comments for documentation
COMMENT ON TABLE dashboard_market_data IS 'Stores real-time market data from Agent 1 (Data Agent) for dashboard display';
COMMENT ON COLUMN dashboard_market_data.symbol IS 'Stock/ETF ticker symbol (e.g., SPY, QQQ)';
COMMENT ON COLUMN dashboard_market_data.asset_type IS 'Type of asset: ETF, BOND_ETF, CRYPTO_ETF, INDEX, YIELD';
COMMENT ON COLUMN dashboard_market_data.context_data IS 'Additional context data for special indicators (JSON format)';
COMMENT ON COLUMN dashboard_market_data.data_timestamp IS 'Timestamp when the market data was collected';
COMMENT ON COLUMN dashboard_market_data.updated_at IS 'Timestamp when the record was last updated in database';

-- Show table structure
\d dashboard_market_data;