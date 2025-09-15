
---------------------

# "public" schema for Neural Capital AI

`This is not final yet, still in brainstorming phase`


---------------------


### Table 1 - "public.users"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| id                   | int8         |              | Internal auto-increment ID                |
| created_at           | timestamptz  |              | Timestamp when user was created           |
| email                | text         |              | User's email address                      |
| id_alpaca            | text         |              | Alpaca trading account ID                 |
| city                 | text         |              | User's city                               |
| contact_email        | text         |              | Contact email address                     |
| contact_family       | text         |              | Family contact name                       |
| contact_given        | text         |              | Given contact name                        |
| country_of_birth     | text         |              | Country of birth                          |
| country_of_citizenship| text         |              | Country of citizenship                    |
| date_of_birth        | date         |              | Date of birth for age-based planning      |
| family_name          | text         |              | User's family name                        |
| given_name           | text         |              | User's given name                         |
| phone                | text         |              | Phone number (changed from float8)        |
| postal_code          | text         |              | Postal code (changed from int8)           |
| state                | text         |              | State or province                        |
| street_address       | text         |              | Street address                            |
| tax_id               | text         |              | Tax ID (changed from int8)                |
| id_user              | uuid         | primary      | Primary key UUID for external referencing |

---------------------

### Table 2 - "assets"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| AssetID              | uuid         | primary      | Primary key, auto-increment or UUID       |
| Ticker               | text         | unique       | Stock ticker symbol (e.g., SPY, BTC)      |
| AssetName            | text         |              | Full asset name (e.g., S&P 500 ETF)       |
| AssetType            | text         |              | Asset category (Equities, Crypto, etc.)   |
| IsOptional           | boolean      |              | Whether asset is optional for portfolios  |
| Description          | text         |              | Optional detailed description             |

---------------------

### Table 3 - "risk_tiers"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| RiskTierID           | integer      | primary      | Primary key (1-5 scale)                   |
| RiskName             | text         |              | Risk level name (Conservative, Aggressive)|
| ProfileDescription   | text         |              | Description of risk profile               |
| InvestmentHorizon    | text         |              | Recommended investment timeframe          |
| ExpectedReturn       | numeric      |              | Expected annual return (e.g., 0.04)      |
| Volatility           | numeric      |              | Expected volatility (e.g., 0.05)         |
| SharpeRatio          | numeric      |              | Risk-adjusted return metric               |
| TargetAllocations    | jsonb        |              | Asset allocation percentages as JSON      |


---------------------


### Table 4 - "signal_rules"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| SignalID             | uuid         | primary      | Primary key for signal rule               |
| SignalName           | text         |              | Name of market signal                     |
| Description          | text         |              | Explanation of signal logic               |
| Frequency            | text         |              | How often signal is checked               |
| ConditionTrigger     | jsonb        |              | Conditions that activate signal           |
| Action               | jsonb        |              | Portfolio adjustments to make             |
| ApplicableRiskTiers  | text         |              | Which risk tiers this applies to          |
| CooldownPeriodDays   | integer      |              | Days to wait before re-triggering         |
| ReversalCondition    | jsonb        |              | Conditions to reverse the action          |


---------------------

### Table 5 - "planner_rules"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| RuleID               | uuid         | primary      | Primary key for planner rule              |
| RuleName             | text         |              | Name of planning rule                     |
| RuleType             | text         |              | Type of rule (Age-Based, Goal-Based)      |
| Conditions           | jsonb        |              | Criteria for applying rule                |
| ActionAllocations    | jsonb        |              | Asset allocations for conditions          |
| ExplanationTemplate  | text         |              | Template for explaining the rule          |


---------------------

### Table 6 - "market_time_series"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| DataPointID          | uuid         | primary      | Primary key for data point                |
| Date                 | timestamp    |              | Date/timestamp of the data point          |
| AssetID              | uuid         | foreign      | Foreign key to assets table               |
| MetricName           | text         |              | Name of metric (ClosePrice, VIX_Level)    |
| Value                | numeric      |              | Numerical value of the metric             |
| DataSource           | text         |              | Source of data (FRED, Polygon, Yahoo)     |

---------------------

### Table 7 - "market_events"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| EventID              | uuid         | primary      | Primary key for market event              |
| EventName            | text         |              | Name of market event or crisis            |
| StartDate            | date         |              | Start date of the event                   |
| EndDate              | date         |              | End date of the event                     |
| Description          | text         |              | Description of the market event           |


---------------------


### Table 8 - "agents"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| AgentID              | uuid         | primary      | Primary key for agent                     |
| AgentName            | text         |              | Name of the Coral Protocol agent          |
| Description          | text         |              | Description of agent's function           |
| API_Endpoint         | text         |              | URL endpoint for agent API                |
| PricingModel         | text         |              | Pricing structure (per-call, per-minute)  |
| CostPerUnit          | numeric      |              | Cost in Solana per unit                   |
| OwnerWalletAddress   | text         |              | Solana wallet address of owner            |
| IsRentable           | boolean      |              | Whether agent is available for rent       |



---------------------

### Table 9 - "agent_transactions"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| TransactionID        | uuid         | primary      | Primary key for transaction               |
| AgentID              | uuid         | foreign      | Foreign key to agents table               |
| UserID               | uuid         | foreign      | Foreign key to users.id_user              |
| Timestamp            | timestamptz  |              | When transaction occurred                 |
| InputData            | jsonb        |              | Input data sent to agent                  |
| OutputData           | jsonb        |              | Output data received from agent           |
| CostInSolana         | numeric      |              | Transaction cost in Solana                |
| SolanaTxnHash        | text         |              | Solana blockchain transaction hash        |


---------------------


### Table 10 - "user_goals"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| GoalID               | uuid         | primary      | Primary key for user goal                 |
| UserID               | uuid         | foreign      | Foreign key to users.id_user              |
| GoalDescription      | text         |              | Description of financial goal             |
| GoalType             | text         |              | Type of goal (Retirement, Education)      |
| TargetAmount         | numeric      |              | Financial target amount                   |
| TargetDate           | date         |              | Desired completion date                   |
| CurrentSavings       | numeric      |              | Current amount saved                      |
| AssignedRiskTierID   | integer      | foreign      | Foreign key to risk_tiers table           |


---------------------

### Table 11 - "user_portfolios"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| UserPortfolioID      | uuid         | primary      | Primary key for user portfolio            |
| UserID               | uuid         | foreign      | Foreign key to users.id_user              |
| GoalID               | uuid         | foreign      | Foreign key to user_goals table           |
| PortfolioName        | text         |              | Name of the portfolio                     |
| CurrentRiskTierID    | integer      | foreign      | Foreign key to risk_tiers table           |
| CreationDate         | date         |              | When portfolio was created                |
| LastRebalanceDate    | date         |              | Last time portfolio was rebalanced        |
| CurrentTotalValue    | numeric      |              | Total current value of holdings           |


---------------------

### Table 12 - "user_portfolio_holdings"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| HoldingID            | uuid         | primary      | Primary key for portfolio holding         |
| UserPortfolioID      | uuid         | foreign      | Foreign key to user_portfolios table      |
| AssetID              | uuid         | foreign      | Foreign key to assets table               |
| CurrentAllocationPercentage| numeric   |              | Current percentage allocation             |
| TargetAllocationPercentage| numeric   |              | Target percentage allocation              |
| NumberOfUnits        | numeric      |              | Number of units/shares held               |
| AverageCostBasis     | numeric      |              | Average cost per unit                     |
| CurrentValue         | numeric      |              | Current total value of holding            |


---------------------

### Table 13 - "portfolio_performance_metrics"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| PerformanceRecordID  | uuid         | primary      | Primary key for performance record        |
| UserPortfolioID      | uuid         | foreign      | Foreign key to user_portfolios table      |
| Date                 | date         |              | Date of performance measurement           |
| SharpeRatio          | numeric      |              | Risk-adjusted return metric               |
| SortinoRatio         | numeric      |              | Downside risk-adjusted return             |
| MaxDrawdown          | numeric      |              | Maximum peak-to-trough decline            |
| Turnover             | numeric      |              | Portfolio turnover rate                   |
| WinRate              | numeric      |              | Percentage of winning trades              |
| InformationRatio     | numeric      |              | Risk-adjusted excess return               |
| CAGR                 | numeric      |              | Compound Annual Growth Rate               |
| Volatility           | numeric      |              | Portfolio volatility                      |
| ReturnDuringCrash    | numeric      |              | Return during market crashes              |
| RecoveryTimeDays     | integer      |              | Days to recover from drawdown             |


---------------------

### Table 14 - "transaction_logs"

| column-name          | data-type    | key          | description-e.g.                          |
|----------------------|--------------|--------------|-------------------------------------------|
| LogID                | uuid         | primary      | Primary key for transaction log           |
| UserPortfolioID      | uuid         | foreign      | Foreign key to user_portfolios table      |
| Timestamp            | timestamptz  |              | When transaction occurred                 |
| ActionType           | text         |              | Type of action (Buy, Sell, Rebalance)     |
| AssetID              | uuid         | foreign      | Foreign key to assets table               |
| Quantity             | numeric      |              | Number of units traded                    |
| Price                | numeric      |              | Price per unit                            |
| Amount               | numeric      |              | Total transaction amount                  |
| Reason               | text         |              | Reason for transaction                    |
| SignalID             | uuid         | foreign      | Foreign key to signal_rules table         |
| IsSimulated          | boolean      |              | Whether this is a simulation/backtest     |
| AlpacaOrderID        | text         |              | Alpaca trading platform order ID          |


---------------------