-- Neural Capital AI Database Schema and Initial Data
-- PostgreSQL Implementation

-- ==========================================
-- CREATE TABLES
-- ==========================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table 1: users
CREATE TABLE IF NOT EXISTS public.users (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    email TEXT NOT NULL UNIQUE,
    id_alpaca TEXT,
    city TEXT,
    contact_email TEXT,
    contact_family TEXT,
    contact_given TEXT,
    country_of_birth TEXT,
    country_of_citizenship TEXT,
    date_of_birth DATE,
    family_name TEXT,
    given_name TEXT,
    phone TEXT,
    postal_code TEXT,
    state TEXT,
    street_address TEXT,
    tax_id TEXT,
    id_user UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL
);

-- Table 2: assets
CREATE TABLE IF NOT EXISTS public.assets (
    AssetID UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    Ticker TEXT NOT NULL UNIQUE,
    AssetName TEXT NOT NULL,
    AssetType TEXT NOT NULL,
    IsOptional BOOLEAN DEFAULT FALSE,
    Description TEXT
);

-- Table 3: risk_tiers
CREATE TABLE IF NOT EXISTS public.risk_tiers (
    RiskTierID INTEGER PRIMARY KEY CHECK (RiskTierID BETWEEN 1 AND 5),
    RiskName TEXT NOT NULL,
    ProfileDescription TEXT,
    InvestmentHorizon TEXT,
    ExpectedReturn NUMERIC(5,4),
    Volatility NUMERIC(5,4),
    SharpeRatio NUMERIC(5,2),
    TargetAllocations JSONB
);

-- Table 4: signal_rules
CREATE TABLE IF NOT EXISTS public.signal_rules (
    SignalID UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    SignalName TEXT NOT NULL,
    Description TEXT,
    Frequency TEXT,
    ConditionTrigger JSONB,
    Action JSONB,
    ApplicableRiskTiers TEXT,
    CooldownPeriodDays INTEGER DEFAULT 0,
    ReversalCondition JSONB
);

-- Table 5: planner_rules
CREATE TABLE IF NOT EXISTS public.planner_rules (
    RuleID UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    RuleName TEXT NOT NULL,
    RuleType TEXT NOT NULL,
    Conditions JSONB,
    ActionAllocations JSONB,
    ExplanationTemplate TEXT
);

-- Table 6: market_time_series
CREATE TABLE IF NOT EXISTS public.market_time_series (
    DataPointID UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    Date TIMESTAMP NOT NULL,
    AssetID UUID NOT NULL REFERENCES assets(AssetID),
    MetricName TEXT NOT NULL,
    Value NUMERIC NOT NULL,
    DataSource TEXT
);

-- Table 7: market_events
CREATE TABLE IF NOT EXISTS public.market_events (
    EventID UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    EventName TEXT NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE,
    Description TEXT
);

-- Table 8: agents
CREATE TABLE IF NOT EXISTS public.agents (
    AgentID UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    AgentName TEXT NOT NULL,
    Description TEXT,
    API_Endpoint TEXT,
    PricingModel TEXT,
    CostPerUnit NUMERIC(10,6),
    OwnerWalletAddress TEXT,
    IsRentable BOOLEAN DEFAULT TRUE
);

-- Table 9: agent_transactions
CREATE TABLE IF NOT EXISTS public.agent_transactions (
    TransactionID UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    AgentID UUID NOT NULL REFERENCES agents(AgentID),
    UserID UUID NOT NULL REFERENCES users(id_user),
    Timestamp TIMESTAMPTZ DEFAULT NOW(),
    InputData JSONB,
    OutputData JSONB,
    CostInSolana NUMERIC(10,6),
    SolanaTxnHash TEXT
);

-- Table 10: user_goals
CREATE TABLE IF NOT EXISTS public.user_goals (
    GoalID UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    UserID UUID NOT NULL REFERENCES users(id_user),
    GoalDescription TEXT NOT NULL,
    GoalType TEXT NOT NULL,
    TargetAmount NUMERIC(12,2),
    TargetDate DATE,
    CurrentSavings NUMERIC(12,2) DEFAULT 0,
    AssignedRiskTierID INTEGER REFERENCES risk_tiers(RiskTierID)
);

-- Table 11: user_portfolios
CREATE TABLE IF NOT EXISTS public.user_portfolios (
    UserPortfolioID UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    UserID UUID NOT NULL REFERENCES users(id_user),
    GoalID UUID REFERENCES user_goals(GoalID),
    PortfolioName TEXT NOT NULL,
    CurrentRiskTierID INTEGER NOT NULL REFERENCES risk_tiers(RiskTierID),
    CreationDate DATE DEFAULT CURRENT_DATE,
    LastRebalanceDate DATE,
    CurrentTotalValue NUMERIC(12,2) DEFAULT 0
);

-- Table 12: user_portfolio_holdings
CREATE TABLE IF NOT EXISTS public.user_portfolio_holdings (
    HoldingID UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    UserPortfolioID UUID NOT NULL REFERENCES user_portfolios(UserPortfolioID),
    AssetID UUID NOT NULL REFERENCES assets(AssetID),
    CurrentAllocationPercentage NUMERIC(5,2),
    TargetAllocationPercentage NUMERIC(5,2),
    NumberOfUnits NUMERIC(15,6),
    AverageCostBasis NUMERIC(10,2),
    CurrentValue NUMERIC(12,2)
);

-- Table 13: portfolio_performance_metrics
CREATE TABLE IF NOT EXISTS public.portfolio_performance_metrics (
    PerformanceRecordID UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    UserPortfolioID UUID NOT NULL REFERENCES user_portfolios(UserPortfolioID),
    Date DATE NOT NULL,
    SharpeRatio NUMERIC(5,2),
    SortinoRatio NUMERIC(5,2),
    MaxDrawdown NUMERIC(5,2),
    Turnover NUMERIC(5,2),
    WinRate NUMERIC(5,2),
    InformationRatio NUMERIC(5,2),
    CAGR NUMERIC(5,2),
    Volatility NUMERIC(5,2),
    ReturnDuringCrash NUMERIC(5,2),
    RecoveryTimeDays INTEGER
);

-- Table 14: transaction_logs
CREATE TABLE IF NOT EXISTS public.transaction_logs (
    LogID UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    UserPortfolioID UUID NOT NULL REFERENCES user_portfolios(UserPortfolioID),
    Timestamp TIMESTAMPTZ DEFAULT NOW(),
    ActionType TEXT NOT NULL,
    AssetID UUID REFERENCES assets(AssetID),
    Quantity NUMERIC(15,6),
    Price NUMERIC(10,2),
    Amount NUMERIC(12,2),
    Reason TEXT,
    SignalID UUID REFERENCES signal_rules(SignalID),
    IsSimulated BOOLEAN DEFAULT FALSE,
    AlpacaOrderID TEXT
);

-- ==========================================
-- CREATE INDEXES FOR PERFORMANCE
-- ==========================================

-- Users table indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_id_user ON users(id_user);

-- Assets table indexes
CREATE INDEX IF NOT EXISTS idx_assets_ticker ON assets(Ticker);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(AssetType);

-- Market time series indexes
CREATE INDEX IF NOT EXISTS idx_market_time_series_date ON market_time_series(Date);
CREATE INDEX IF NOT EXISTS idx_market_time_series_asset ON market_time_series(AssetID);
CREATE INDEX IF NOT EXISTS idx_market_time_series_metric ON market_time_series(MetricName);

-- Transaction logs indexes
CREATE INDEX IF NOT EXISTS idx_transaction_logs_timestamp ON transaction_logs(Timestamp);
CREATE INDEX IF NOT EXISTS idx_transaction_logs_portfolio ON transaction_logs(UserPortfolioID);

-- Agent transactions indexes
CREATE INDEX IF NOT EXISTS idx_agent_transactions_timestamp ON agent_transactions(Timestamp);
CREATE INDEX IF NOT EXISTS idx_agent_transactions_user ON agent_transactions(UserID);

-- ==========================================
-- INSERT INITIAL DATA
-- ==========================================

-- Insert Risk Tiers
INSERT INTO public.risk_tiers (RiskTierID, RiskName, ProfileDescription, InvestmentHorizon, ExpectedReturn, Volatility, SharpeRatio, TargetAllocations) VALUES
(1, 'Conservative', 'Low risk, capital preservation focused', '3-5 years', 0.0400, 0.0500, 0.80, '{"bonds": 70, "stocks": 25, "cash": 5}'),
(2, 'Moderate Conservative', 'Slightly higher risk with modest growth', '5-7 years', 0.0600, 0.0800, 0.75, '{"bonds": 50, "stocks": 45, "cash": 5}'),
(3, 'Balanced', 'Balanced risk and return', '7-10 years', 0.0800, 0.1200, 0.67, '{"bonds": 35, "stocks": 60, "alternatives": 5}'),
(4, 'Growth', 'Higher risk for higher returns', '10-15 years', 0.1000, 0.1600, 0.63, '{"bonds": 20, "stocks": 75, "alternatives": 5}'),
(5, 'Aggressive', 'High risk, maximum growth potential', '15+ years', 0.1200, 0.2000, 0.60, '{"bonds": 10, "stocks": 80, "alternatives": 10}')
ON CONFLICT (RiskTierID) DO NOTHING;

-- Insert Sample Assets
INSERT INTO public.assets (Ticker, AssetName, AssetType, IsOptional, Description) VALUES
('SPY', 'SPDR S&P 500 ETF Trust', 'Equities', FALSE, 'Large-cap US equity ETF tracking S&P 500'),
('VTI', 'Vanguard Total Stock Market ETF', 'Equities', FALSE, 'Total US stock market exposure'),
('VXUS', 'Vanguard Total International Stock ETF', 'Equities', FALSE, 'International developed markets'),
('BND', 'Vanguard Total Bond Market ETF', 'Bonds', FALSE, 'US aggregate bond market'),
('BNDX', 'Vanguard Total International Bond ETF', 'Bonds', TRUE, 'International bond exposure'),
('VNQ', 'Vanguard Real Estate Investment Trust ETF', 'REIT', TRUE, 'Real Estate Investment Trusts'),
('BTC-USD', 'Bitcoin', 'Cryptocurrency', TRUE, 'Bitcoin cryptocurrency'),
('GLD', 'SPDR Gold Shares', 'Commodities', TRUE, 'Gold commodity exposure'),
('TLT', 'iShares 20+ Year Treasury Bond ETF', 'Bonds', TRUE, 'Long-term US Treasury bonds'),
('QQQ', 'Invesco QQQ Trust', 'Equities', TRUE, 'Nasdaq-100 technology focus')
ON CONFLICT (Ticker) DO NOTHING;

-- Insert Sample Market Events
INSERT INTO public.market_events (EventName, StartDate, EndDate, Description) VALUES
('COVID-19 Market Crash', '2020-02-19', '2020-03-23', 'Rapid market decline due to COVID-19 pandemic'),
('2008 Financial Crisis', '2007-10-09', '2009-03-09', 'Global financial crisis and recession'),
('Dot-com Bubble Burst', '2000-03-10', '2002-10-09', 'Technology stock market crash'),
('Black Monday', '1987-10-19', '1987-10-19', 'Single-day stock market crash'),
('2022 Interest Rate Surge', '2022-01-01', '2022-12-31', 'Federal Reserve aggressive interest rate hikes')
ON CONFLICT DO NOTHING;

-- Insert Sample Agents
INSERT INTO public.agents (AgentName, Description, API_Endpoint, PricingModel, CostPerUnit, OwnerWalletAddress, IsRentable) VALUES
('Portfolio Optimizer', 'AI agent for portfolio optimization and rebalancing', 'https://api.neural.capital/optimizer', 'per-call', 0.001, 'GQR8...XYZ', TRUE),
('Risk Analyzer', 'AI agent for portfolio risk analysis and stress testing', 'https://api.neural.capital/risk', 'per-call', 0.0015, 'ABC123...DEF', TRUE),
('Market Sentiment Analyzer', 'AI agent analyzing market sentiment from news and social media', 'https://api.neural.capital/sentiment', 'per-minute', 0.0005, 'XYZ789...GHI', TRUE),
('Economic Indicator Tracker', 'AI agent tracking and analyzing economic indicators', 'https://api.neural.capital/economics', 'per-call', 0.002, 'DEF456...JKL', TRUE),
('ESG Screener', 'AI agent for ESG (Environmental, Social, Governance) screening', 'https://api.neural.capital/esg', 'per-call', 0.0012, 'GHI789...MNO', TRUE)
ON CONFLICT DO NOTHING;

-- Insert Sample Signal Rules
INSERT INTO public.signal_rules (SignalName, Description, Frequency, ConditionTrigger, Action, ApplicableRiskTiers, CooldownPeriodDays, ReversalCondition) VALUES
('VIX Spike Defense', 'Defensive rebalancing when VIX spikes above 30', 'daily', 
 '{"metric": "VIX", "operator": ">", "threshold": 30}',
 '{"reduce_equity": 10, "increase_bonds": 10}',
 '3,4,5', 30,
 '{"metric": "VIX", "operator": "<", "threshold": 20}'),
 
('Economic Recession Indicator', 'Adjust allocations during recession signals', 'weekly',
 '{"indicators": ["unemployment_rate", "yield_curve"], "condition": "recession_probability > 0.7"}',
 '{"reduce_equity": 15, "increase_bonds": 10, "increase_cash": 5}',
 '2,3,4,5', 90,
 '{"condition": "recession_probability < 0.3"}'),

('Momentum Breakout', 'Increase equity allocation on positive momentum', 'weekly',
 '{"metric": "price_momentum_3m", "operator": ">", "threshold": 0.15}',
 '{"increase_equity": 5, "reduce_bonds": 5}',
 '4,5', 14,
 '{"metric": "price_momentum_1m", "operator": "<", "threshold": -0.05}')
ON CONFLICT DO NOTHING;

-- Insert Sample Planner Rules
INSERT INTO public.planner_rules (RuleName, RuleType, Conditions, ActionAllocations, ExplanationTemplate) VALUES
('Young Aggressive Growth', 'Age-Based', 
 '{"age": {"min": 18, "max": 35}, "risk_tolerance": "high"}',
 '{"stocks": 85, "bonds": 10, "alternatives": 5}',
 'At your age of {age}, you have time to weather market volatility for long-term growth.'),
 
('Pre-Retirement Conservative', 'Age-Based',
 '{"age": {"min": 55, "max": 65}, "years_to_retirement": {"max": 10}}',
 '{"stocks": 40, "bonds": 55, "cash": 5}',
 'As you approach retirement in {years_to_retirement} years, we recommend reducing risk.'),

('Education Goal Planning', 'Goal-Based',
 '{"goal_type": "education", "years_to_goal": {"max": 18}}',
 '{"stocks": 60, "bonds": 35, "cash": 5}',
 'For education funding in {years_to_goal} years, balanced growth with some stability is optimal.')
ON CONFLICT DO NOTHING;

-- ==========================================
-- CREATE FUNCTIONS AND TRIGGERS
-- ==========================================

-- Function to update portfolio value automatically
CREATE OR REPLACE FUNCTION update_portfolio_value()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_portfolios 
    SET CurrentTotalValue = (
        SELECT COALESCE(SUM(CurrentValue), 0)
        FROM user_portfolio_holdings 
        WHERE UserPortfolioID = NEW.UserPortfolioID
    )
    WHERE UserPortfolioID = NEW.UserPortfolioID;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update portfolio value when holdings change
DROP TRIGGER IF EXISTS trigger_update_portfolio_value ON user_portfolio_holdings;
CREATE TRIGGER trigger_update_portfolio_value
    AFTER INSERT OR UPDATE OR DELETE ON user_portfolio_holdings
    FOR EACH ROW EXECUTE FUNCTION update_portfolio_value();

-- ==========================================
-- GRANT PERMISSIONS (adjust as needed)
-- ==========================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO PUBLIC;

-- Grant permissions on all tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO PUBLIC;

-- Grant permissions on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO PUBLIC;

-- ==========================================
-- SAMPLE QUERIES FOR TESTING
-- ==========================================

-- View all risk tiers with their allocations
-- SELECT RiskTierID, RiskName, ExpectedReturn, TargetAllocations FROM risk_tiers ORDER BY RiskTierID;

-- View all available assets
-- SELECT Ticker, AssetName, AssetType FROM assets ORDER BY AssetType, Ticker;

-- View all active agents
-- SELECT AgentName, Description, PricingModel, CostPerUnit FROM agents WHERE IsRentable = TRUE;

-- View signal rules summary
-- SELECT SignalName, Description, ApplicableRiskTiers FROM signal_rules;

COMMIT;