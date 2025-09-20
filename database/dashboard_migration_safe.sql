-- Safe Migration Script for Dashboard Data Table
-- This preserves existing data while updating the schema

-- Step 1: Create backup of existing data (if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'dashboard_data') THEN
        -- Create temporary backup table
        CREATE TABLE dashboard_data_backup AS SELECT * FROM dashboard_data;

        -- Drop the existing table
        DROP TABLE dashboard_data CASCADE;

        RAISE NOTICE 'Existing dashboard_data backed up and dropped';
    ELSE
        RAISE NOTICE 'No existing dashboard_data table found';
    END IF;
END $$;

-- Step 2: Create new dashboard_data table with correct schema
CREATE TABLE dashboard_data (
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

-- Step 3: Create indexes for performance
CREATE INDEX idx_dashboard_data_symbol ON dashboard_data(symbol);
CREATE INDEX idx_dashboard_data_asset_type ON dashboard_data(asset_type);
CREATE INDEX idx_dashboard_data_updated_at ON dashboard_data(updated_at DESC);
CREATE INDEX idx_dashboard_data_timestamp ON dashboard_data(data_timestamp DESC);

-- Step 4: Restore data from backup (if it exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'dashboard_data_backup') THEN
        -- Insert data from backup, handling the new schema
        INSERT INTO dashboard_data (
            symbol, name, asset_type, price, previous_close, change_value, change_percent,
            volume, market_cap, day_high, day_low, year_high, year_low,
            pe_ratio, dividend_yield, expense_ratio, total_assets, beta,
            sma_20, sma_50, sma_200, rsi, context_data,
            data_timestamp, updated_at, created_at
        )
        SELECT
            CASE
                WHEN LENGTH(symbol) <= 20 THEN symbol
                ELSE LEFT(symbol, 20) -- Truncate if too long
            END,
            CASE
                WHEN LENGTH(name) <= 150 THEN name
                ELSE LEFT(name, 150) -- Truncate if too long
            END,
            asset_type, price, previous_close, change_value, change_percent,
            volume, market_cap, day_high, day_low, year_high, year_low,
            pe_ratio, dividend_yield, expense_ratio, total_assets, beta,
            sma_20, sma_50, sma_200, rsi, context_data,
            data_timestamp, updated_at, created_at
        FROM dashboard_data_backup
        ON CONFLICT (symbol) DO UPDATE SET
            name = EXCLUDED.name,
            asset_type = EXCLUDED.asset_type,
            price = EXCLUDED.price,
            previous_close = EXCLUDED.previous_close,
            change_value = EXCLUDED.change_value,
            change_percent = EXCLUDED.change_percent,
            volume = EXCLUDED.volume,
            market_cap = EXCLUDED.market_cap,
            day_high = EXCLUDED.day_high,
            day_low = EXCLUDED.day_low,
            year_high = EXCLUDED.year_high,
            year_low = EXCLUDED.year_low,
            pe_ratio = EXCLUDED.pe_ratio,
            dividend_yield = EXCLUDED.dividend_yield,
            expense_ratio = EXCLUDED.expense_ratio,
            total_assets = EXCLUDED.total_assets,
            beta = EXCLUDED.beta,
            sma_20 = EXCLUDED.sma_20,
            sma_50 = EXCLUDED.sma_50,
            sma_200 = EXCLUDED.sma_200,
            rsi = EXCLUDED.rsi,
            context_data = EXCLUDED.context_data,
            data_timestamp = EXCLUDED.data_timestamp,
            updated_at = NOW();

        -- Drop backup table after successful migration
        DROP TABLE dashboard_data_backup;

        RAISE NOTICE 'Data successfully migrated from backup';
    ELSE
        RAISE NOTICE 'No backup data to restore';
    END IF;
END $$;

-- Step 5: Insert default ETF records if they don't exist
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

RAISE NOTICE 'Dashboard data migration completed successfully!';