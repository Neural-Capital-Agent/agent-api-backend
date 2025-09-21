# Neural Capital Agent Architecture

## Agent 1: Data Agent

**Primary Function:** Real-time financial data aggregation and macro-economic indicator collection

**Implementation Status:** ✅ Implemented

### Core Responsibilities
- Real-time market data ingestion for predefined asset universe
- Macro-economic indicator collection from external APIs
- Technical indicator calculation and momentum signal generation
- Data validation, storage, and historical record maintenance

### Asset Universe
```
Equities: SPY, QQQ, VXUS
Fixed Income: SGOV, SHY, IEF, BND, TIP  
Alternatives: GLD
Crypto (Optional): BTC-USD, ETH-USD
```

### Data Sources & APIs
| Source | Data Type | Frequency |
|--------|-----------|-----------|
| Yahoo Finance | Market prices, technical indicators | Daily |
| FRED | Macro indicators (CPI, Fed Funds, Unemployment) | Monthly |
| Treasury FiscalData | Yield curve data | Daily |
| Polygon | OHLC, volume, volatility metrics | Daily |

### Technical Implementation
```python
class DataAgent:
    def fetch_market_data(ticker: str) -> MarketData
    def fetch_macro_data(indicator: str) -> List[MacroData]  
    def fetch_technical_indicators(ticker: str) -> Dict[str, Any]
    def get_market_momentum_signals() -> Dict[str, Any]
```

### API Endpoints
- `GET /data/market/{ticker}` - Real-time market data
- `GET /data/macro/{indicator}` - Macro-economic indicators  
- `GET /data/technical/{ticker}` - Technical analysis metrics
- `GET /data/health` - Data source health check

### Storage Layer
- **Database:** Supabase integration for historical data persistence
- **Caching:** Redis for high-frequency data retrieval optimization
- **Data Validation:** Built-in sanitization and quality checks 

## Agent 2: Portfolio Agent / Rebalancer

**Primary Function:** Algorithmic portfolio optimization and dynamic rebalancing based on risk tolerance and macro signals

**Implementation Status:** ✅ Implemented

### Core Algorithm Flow
```
Input: (risk_level: 1-5, goal: string) 
→ Risk Tier Mapping 
→ Base Allocation 
→ Macro Signal Analysis 
→ Dynamic Adjustments 
→ Output: (allocation: Dict, expected_return: float, volatility: float)
```

### Risk Tier Allocations

| Risk Level | Equities | Fixed Income | Alternatives | Cash/Short-Term |
|------------|----------|--------------|--------------|-----------------|
| 1 (Conservative) | 0% | 40% (BND 25%, IEF 15%) | 10% (GLD) | 50% (SHY) |
| 2 (Balanced Conservative) | 35% (SPY 25%, VXUS 10%) | 55% (BND 35%, IEF 20%) | 10% (GLD) | 0% |
| 3 (Balanced) | 60% (SPY 40%, VXUS 20%) | 30% (BND 20%, IEF 10%) | 10% (GLD) | 0% |
| 4 (Growth) | 90% (SPY 45%, QQQ 25%, VXUS 20%) | 5% (BND) | 5% (GLD) | 0% |
| 5 (Aggressive) | 90% (SPY 40%, QQQ 30%, VXUS 20%) | 0% | 10% (GLD 5%, BTC 5%) | 0% |

### Dynamic Rebalancing Rules Engine

#### Macro Signal Triggers
| Signal | Condition | Action | Cooldown |
|--------|-----------|--------|----------|
| Yield Curve Inversion | 10Y-2Y < 0 (10 days) | Equity cap -10%, shift to SHY | 30 days |
| Inflation Shock | CPI YoY > 4% (2+ months) | +5% TIPS (from BND) | 3 months |
| Volatility Spike | VIX ≥ 25 (3 days) | Equity cap -5% to SHY | 20 days |
| Credit Stress | IG Spreads > 5% | Equity cap -5% to IEF/BND | 30 days |
| PMI Contraction | PMI < 50 (2 months) | Equity -5% to IEF/BND | 3 months |
| Market Momentum | SPY < 200-day MA (5 days) | Equity -10% to SHY/IEF/GLD | 30 days |

### Technical Implementation

#### Core Agent Structure
```python
class PortfolioAgent:
    def __init__(self, coral_server_url: str = "http://localhost:5555"):
        from .coral_client import CoralClient
        from .models import RiskLevel

        self.coral_client = CoralClient(coral_server_url, agent_id="portfolio_agent")

        # Base allocations for different risk levels
        self.base_allocations = {
            RiskLevel.CONSERVATIVE: {
                "equities": {"SPY": 0.0, "QQQ": 0.0, "VXUS": 0.0},
                "fixed_income": {"BND": 0.25, "IEF": 0.15, "SHY": 0.50},
                "alternatives": {"GLD": 0.10},
                "crypto": {"BTC-USD": 0.0, "ETH-USD": 0.0}
            },
            # ... other risk levels
        }

    async def build_portfolio(self, risk_level: int, goal: str, constraints: Optional[Dict] = None) -> Portfolio
    async def calculate_rebalancing(self, current: Portfolio, signals: MacroSignals) -> RebalanceAction
    async def _calculate_portfolio_metrics(self, allocations: Dict[str, float]) -> Tuple[float, float]

    # Utility methods
    def _reduce_equity_allocation(self, allocations, reduction) -> Dict[str, float]
    def _calculate_trades(self, current, target) -> List[Dict[str, Any]]
```

#### Task Management
```python
class PortfolioAgentTasks:
    def __init__(self):
        self.portfolio_agent = PortfolioAgent()
        self.REBALANCING_FREQUENCY = "weekly"
        self.RISK_MONITORING_FREQUENCY = "daily"

    async def portfolio_rebalancing_task(self, portfolio_id: str) -> Dict[str, Any]
    async def risk_monitoring_task(self, portfolio_id: str) -> Dict[str, Any]
    async def performance_tracking_task(self, portfolio_id: str) -> Dict[str, Any]
```

#### Tools & Utilities
```python
# Portfolio optimization utilities
class PortfolioOptimizer:
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float
    @staticmethod
    def calculate_maximum_drawdown(prices: List[float]) -> float
    @staticmethod
    def optimize_weights(expected_returns: Dict, covariance_matrix: Dict, risk_tolerance: float) -> Dict

class RiskCalculator:
    @staticmethod
    def calculate_var(returns: List[float], confidence_level: float = 0.95) -> float
    @staticmethod
    def calculate_beta(asset_returns: List[float], market_returns: List[float]) -> float
```

#### MCP Integration
```python
@mcp.tool()
def build_portfolio(risk_level: int, goal: str, constraints: dict = None) -> dict:
    """Build an optimized portfolio based on risk level and investment goal."""

@mcp.tool()
def calculate_rebalancing(current_portfolio: dict, signals: dict = None) -> dict:
    """Calculate portfolio rebalancing actions based on current allocation and market signals."""

@mcp.tool()
def get_portfolio_metrics(allocations: dict) -> dict:
    """Calculate portfolio metrics including expected return, volatility, and Sharpe ratio."""
```

### Coral Protocol Integration
- **Agent Communication**: Secure requests to Data Agent for market data validation
- **Payment System**: CORAL token micropayments for premium data sources
- **Cross-Agent Coordination**: Real-time signal validation with other agents
- **Trust Layer**: Blockchain verification of data source integrity

### API Endpoints
- `POST /portfolio/build` - Generate initial allocation
- `POST /portfolio/rebalance` - Calculate rebalancing actions
- `GET /portfolio/backtest` - Historical performance simulation
- `POST /portfolio/execute` - Trade execution (simulated)

## Agent 3: Financial Planner Agent

**Primary Function:** Natural language goal interpretation and lifecycle-based investment planning

**Implementation Status:** ✅ Implemented  
**LLM Integration:** ✅ Required for NLP goal parsing

### Core Capabilities
- Goal-to-strategy mapping via natural language processing
- Age-based retirement glide path optimization
- Bond ladder construction and management
- Cash flow projection and timeline modeling

### Goal-Based Strategy Mapping

| Goal Type | Time Horizon | Recommended Allocation | Risk Level |
|-----------|--------------|----------------------|------------|
| House Down Payment | 3-7 years | 80% Bonds/T-Bills, 20% Equities | 1-2 |
| Retirement | 20+ years | 80% Equities, 20% Bonds/Gold | 4-5 |
| Emergency Fund | Immediate | 100% Cash/Short-term | 1 |
| Child Education | 10-18 years | 60% Equities, 40% Bonds | 3 |

### Retirement Glide Path Algorithm

```python
def calculate_glide_path(age: int) -> Dict[str, float]:
    if age < 35: return {"equities": 0.90, "bonds": 0.10, "cash": 0.00}
    elif age < 45: return {"equities": 0.80, "bonds": 0.20, "cash": 0.00} 
    elif age < 55: return {"equities": 0.70, "bonds": 0.25, "gold": 0.05}
    elif age < 65: return {"equities": 0.60, "bonds": 0.35, "gold": 0.05}
    else: return {"equities": 0.40, "bonds": 0.50, "cash": 0.10}
```

### Bond Ladder Construction
**Input:** Investment amount, time horizon  
**Output:** Staggered maturity schedule

```
Example 5-Year Ladder ($100k):
3M T-Bills: $20k
6M T-Bills: $20k  
1Y Treasury: $20k
2Y Treasury: $20k
5Y Treasury: $20k
```

### Technical Implementation

#### Core Agent Structure
```python
class PlannerAgent:
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
            # ... other goal types
        }

        # Keywords for goal parsing
        self.goal_keywords = {
            GoalType.HOUSE_DOWN_PAYMENT: ["house", "home", "down payment", "mortgage"],
            GoalType.RETIREMENT: ["retirement", "retire", "pension", "401k"],
            # ... other keywords
        }

    async def parse_goal(self, goal_text: str) -> GoalParameters
    async def generate_strategy(self, goal: GoalParameters, user_profile: UserProfile) -> InvestmentStrategy
    def build_glide_path(self, age: int, retirement_age: int = 65) -> GlidePath

    # Advanced NLP processing
    async def process_natural_language_goal(self, goal_text: str) -> Dict[str, Any]

    # Private helper methods
    def _extract_goal_type(self, goal_text: str, llm_response: Dict) -> GoalType
    def _extract_amount(self, goal_text: str, llm_response: Dict) -> float
    def _extract_time_horizon(self, goal_text: str, llm_response: Dict) -> int
```

#### Task Management
```python
class PlannerAgentTasks:
    def __init__(self):
        self.planner_agent = PlannerAgent()
        self.GOAL_REVIEW_FREQUENCY = "quarterly"
        self.STRATEGY_UPDATE_FREQUENCY = "semi_annually"

    async def goal_parsing_task(self, goal_text: str, user_id: str) -> Dict[str, Any]
    async def strategy_generation_task(self, goal: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]
    async def lifecycle_adjustment_task(self, user_id: str, current_age: int) -> Dict[str, Any]
```

#### Tools & Utilities
```python
class GoalAnalyzer:
    @staticmethod
    def calculate_required_savings(target_amount: float, current_savings: float,
                                 years: int, expected_return: float = 0.07) -> float
    @staticmethod
    def assess_goal_feasibility(target_amount: float, monthly_savings: float,
                              years: int, expected_return: float = 0.07) -> Dict[str, Any]

class LifecyclePlanner:
    @staticmethod
    def calculate_retirement_needs(current_age: int, retirement_age: int,
                                 current_income: float, replacement_ratio: float = 0.8) -> Dict[str, Any]
```

#### MCP Integration
```python
@mcp.tool()
def parse_goal(goal_text: str) -> dict:
    """Parse natural language financial goal into structured parameters."""

@mcp.tool()
def generate_strategy(goal: dict, user_profile: dict) -> dict:
    """Generate investment strategy based on financial goal and user profile."""

@mcp.tool()
def build_glide_path(age: int, retirement_age: int = 65) -> dict:
    """Build age-appropriate investment glide path for lifecycle planning."""
```

### Coral Protocol Integration
- **LLM Services**: Pay external LLM agents for advanced natural language processing
- **Strategy Coordination**: Seamless communication with Portfolio Agent for strategy execution
- **Multi-Agent Workflows**: Orchestrate complex financial planning workflows across agents
- **Goal Validation**: Cross-reference goal feasibility with market data from Data Agent

### API Endpoints
- `POST /planner/parse-goal` - Extract goal parameters from natural language
- `POST /planner/generate-strategy` - Create investment strategy
- `GET /planner/glide-path/{age}` - Calculate age-appropriate allocation
- `POST /planner/bond-ladder` - Design bond ladder structure 
## Agent 4: Explainability Agent

**Primary Function:** Financial jargon translation and decision rationale generation

**Implementation Status:** ✅ Implemented  
**LLM Integration:** ✅ Required for natural language generation

### Core Capabilities
- Real-time financial jargon translation
- Structured decision explanation generation
- Risk communication and historical contextualization
- Conversational financial advisory interface

### Explanation Template Structure
```
Action → Driver → Risk Assessment → Historical Context
```

**Example Output:**
> "Your portfolio shifted 10% from equities to Treasuries (Action) because the yield curve inverted (Driver), which historically signals recession risk where equities typically decline 20-30% (Historical Context). This protects your capital but may limit growth if the signal proves false (Risk Assessment)."

### Jargon Translation Dictionary

| Financial Term | Plain English Translation |
|----------------|---------------------------|
| Yield Curve Inversion | Long-term rates below short-term rates |
| Credit Spreads | Extra interest risky bonds pay vs safe bonds |
| VIX Spike | Market fear indicator rising |
| P/E Ratio | How expensive stocks are vs earnings |
| Duration Risk | Bond price sensitivity to interest rates |

### Risk Communication Framework

#### Risk Levels
- **Low:** "Minimal chance of loss, but growth may be limited"
- **Moderate:** "Some ups and downs expected, historically recovers within 2-3 years"
- **High:** "Significant volatility possible, suitable for long-term goals only"

### Technical Implementation

#### Core Agent Structure
```python
class ExplainabilityAgent:
    def __init__(self, coral_server_url: str = "http://localhost:5555"):
        from .coral_client import CoralClient

        self.coral_client = CoralClient(coral_server_url, agent_id="explainability_agent")

        # Jargon translation dictionary
        self.jargon_dictionary = {
            "yield_curve_inversion": "When long-term interest rates fall below short-term rates",
            "credit_spreads": "The extra interest risky bonds pay compared to safe government bonds",
            "vix_spike": "When the market fear indicator (VIX) rises sharply",
            # ... more translations
        }

        # Risk communication templates
        self.risk_templates = {
            "low": "Minimal chance of loss, but growth may be limited",
            "moderate": "Some ups and downs expected, but historically recovers within 2-3 years",
            "high": "Significant volatility possible, but higher potential returns over long periods",
            # ... more templates
        }

    async def explain_decision(self, action: Action, context: Optional[Context] = None) -> ExplanationResponse
    def translate_jargon(self, technical_text: str) -> str
    def generate_risk_warning(self, portfolio: Portfolio) -> str

    # Multi-agent context gathering
    async def gather_multi_agent_context(self, action: Action) -> Dict[str, Any]
    async def generate_comprehensive_explanation(self, action: Action, context: Dict[str, Any]) -> str

    # Analysis and calculation methods
    def _generate_risk_assessment(self, action: Action, context: Dict[str, Any]) -> str
    def _provide_historical_context(self, action: Action) -> str
    def _calculate_confidence_score(self, context: Dict[str, Any]) -> float
```

#### Task Management
```python
class ExplainabilityAgentTasks:
    def __init__(self):
        self.explainability_agent = ExplainabilityAgent()
        self.EXPLANATION_CACHE_TTL = 3600  # 1 hour
        self.VERIFICATION_FREQUENCY = "daily"

    async def explanation_generation_task(self, action: Dict[str, Any]) -> Dict[str, Any]
    async def jargon_translation_task(self, technical_text: str) -> Dict[str, Any]
    async def verification_task(self, explanation_id: str) -> Dict[str, Any]
```

#### Tools & Utilities
```python
class ExplanationGenerator:
    @staticmethod
    def complexity_score(text: str) -> float
    @staticmethod
    def generate_summary(text: str, max_length: int = 200) -> str

class ConfidenceCalculator:
    @staticmethod
    def calculate_explanation_confidence(explanation: str, context: Dict[str, Any]) -> float
```

#### MCP Integration
```python
@mcp.tool()
def explain_decision(action: dict, context: dict = None) -> dict:
    """Generate comprehensive explanation for agent decisions and actions."""

@mcp.tool()
def translate_jargon(technical_text: str) -> dict:
    """Translate financial jargon and technical terms to plain English."""

@mcp.tool()
def generate_risk_warning(portfolio: dict) -> dict:
    """Generate risk warnings and disclaimers for portfolio recommendations."""
```

#### Advanced Coral Protocol Features
```python
# Enhanced CoralClient methods for explainability
async def get_explanation_context(self, action: Dict[str, Any]) -> Dict[str, Any]:
    """Gather context for explanations from multiple agents via Coral Protocol."""

async def cross_validate_decision(self, decision: Dict[str, Any], validators: List[str]) -> Dict[str, Any]:
    """Cross-validate decisions with multiple agents via Coral Protocol."""

def create_verification_hash(self, data: Any, action_id: str) -> str:
    """Create a verification hash for blockchain storage."""
```

### Coral Protocol Integration
- **Multi-Agent Context Gathering**: Query all agents for comprehensive decision explanations
- **Unified Explanation Interface**: Single endpoint for explaining any system decision
- **Blockchain Verification**: Immutable verification of explanation accuracy and completeness
- **Cross-Agent Communication**: Secure access to decision rationale from all system components
- **LLM Integration**: Leverage external language models for enhanced explanation generation

### API Endpoints
- `POST /explain/decision` - Generate decision explanation
- `POST /explain/translate` - Convert technical terms to plain English
- `GET /explain/risks/{portfolio_id}` - Risk assessment summary
- `POST /explain/chat` - Conversational financial Q&A

---

## Implementation Status

| Agent | Status | MVP Priority | Dependencies | Files Updated |
|-------|--------|--------------|-------------|---------------|
| Data Agent | ✅ Complete | Critical | External APIs | agents.py, tasks.py, tools.py, mcp.py |
| Portfolio Agent | ✅ Complete | High | Data Agent | agents.py, tasks.py, tools.py, utils.py, mcp.py |
| Planner Agent | ✅ Complete | Medium | Portfolio Agent, LLM | agents.py, tasks.py, tools.py, utils.py, mcp.py |
| Explainability Agent | ✅ Complete | High | All Agents, LLM | agents.py, tasks.py, tools.py, utils.py, mcp.py |

## Code Structure & Organization

### File Distribution
The agent code is now properly structured across the following files:

#### `agent/tasks.py` - Task Management
- **DataAgentTasks**: Periodic data collection, validation, and storage tasks
- **PortfolioAgentTasks**: Portfolio rebalancing, risk monitoring, performance tracking
- **PlannerAgentTasks**: Goal parsing, strategy generation, lifecycle adjustments
- **ExplainabilityAgentTasks**: Explanation generation, jargon translation, verification

#### `agent/tools.py` - Tool Functions
```python
# Data Agent Tools
async def fetch_market_data_tool(ticker: str) -> Dict[str, Any]
async def fetch_macro_data_tool(indicator: str) -> List[Dict[str, Any]]

# Portfolio Agent Tools
async def build_portfolio_tool(risk_level: int, goal: str) -> Dict[str, Any]
async def calculate_rebalancing_tool(current_portfolio: Dict, signals: Dict) -> Dict[str, Any]

# Planner Agent Tools
async def parse_goal_tool(goal_text: str) -> Dict[str, Any]
async def generate_strategy_tool(goal: Dict, user_profile: Dict) -> Dict[str, Any]

# Explainability Agent Tools
async def explain_decision_tool(action: Dict, context: Dict) -> Dict[str, Any]
async def translate_jargon_tool(technical_text: str) -> Dict[str, Any]
```

#### `agent/models.py` - Data Models & Configuration
- **Core Models**: MarketData, MacroData, Portfolio, GoalParameters, etc.
- **Agent Configs**: DataAgentConfig, PortfolioAgentConfig, PlannerAgentConfig, ExplainabilityAgentConfig
- **Performance Models**: AgentPerformanceMetrics, TaskExecutionResult, AgentHealthStatus

#### `agent/utils.py` - Utility Classes
```python
# Portfolio Agent Utilities
class PortfolioOptimizer:
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float]) -> float

class RiskCalculator:
    @staticmethod
    def calculate_var(returns: List[float]) -> float

# Planner Agent Utilities
class GoalAnalyzer:
    @staticmethod
    def calculate_required_savings(target: float, current: float, years: int) -> float

class LifecyclePlanner:
    @staticmethod
    def calculate_retirement_needs(age: int, retirement_age: int) -> Dict[str, Any]

# Explainability Agent Utilities
class ExplanationGenerator:
    @staticmethod
    def complexity_score(text: str) -> float

class ConfidenceCalculator:
    @staticmethod
    def calculate_explanation_confidence(explanation: str, context: Dict) -> float
```

#### `agent/mcp.py` - MCP Protocol Integration
- **Complete Coverage**: All 15+ agent tools exposed via MCP protocol
- **Consistent Interface**: Standardized async/await patterns for all tools
- **Error Handling**: Comprehensive error handling and logging

#### `agent/coral_client.py` - Inter-Agent Communication
- **Enhanced Methods**: Agent-specific helper methods for each agent type
- **Cross-Validation**: Multi-agent decision validation capabilities
- **Network Health**: Comprehensive agent health monitoring
- **Context Gathering**: Automated context collection from multiple agents

## Technical Stack

- **Backend:** FastAPI + Python 3.11+
- **Database:** Supabase (PostgreSQL)
- **Cache:** Redis
- **LLM:** OpenAI GPT-4 / Anthropic Claude / Mistral
- **Data Sources:** Yahoo Finance, FRED, Polygon
- **Agent Communication:** Coral Protocol (3 of 4 agents)
- **Blockchain:** CORAL token for agent micropayments
- **Deployment:** Docker + Kubernetes

## Coral Protocol Integration Summary

### Integrated Agents (4/4) ✅ Complete
- **Data Agent**: Signal validation and market context provision for other agents
- **Portfolio Agent**: Data validation, cross-agent coordination, and decision rationale
- **Financial Planner Agent**: LLM services, strategy coordination, and goal processing
- **Explainability Agent**: Multi-agent context gathering, cross-validation, and verification

### Enhanced Integration Features
```python
# CoralClient enhanced methods
async def get_market_context_from_data_agent(self, timestamp: Optional[str] = None) -> Dict[str, Any]
async def validate_macro_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]
async def get_portfolio_rationale(self, action_id: str) -> Dict[str, Any]
async def process_natural_language_goal(self, goal_text: str) -> Dict[str, Any]
async def get_explanation_context(self, action: Dict[str, Any]) -> Dict[str, Any]
async def cross_validate_decision(self, decision: Dict[str, Any], validators: List[str]) -> Dict[str, Any]
async def health_check_all_agents(self) -> Dict[str, Any]
```

### Implementation Benefits Achieved
- **✅ Secure Communication**: All agents communicate via CoralClient with proper error handling
- **✅ Modular Architecture**: Clean separation of concerns across 6 core files
- **✅ Comprehensive Tooling**: 15+ MCP tools covering all agent functionalities
- **✅ Cross-Agent Validation**: Multi-agent decision validation and context gathering
- **✅ Professional Structure**: Production-ready code organization and patterns
- **✅ Enhanced Utilities**: Specialized utility classes for each agent domain
- **✅ Task Management**: Structured task classes for periodic operations
- **✅ Configuration Management**: Agent-specific configuration models
- **✅ Performance Monitoring**: Built-in health checks and performance metrics

### Technical Achievements
1. **Code Distribution**: Properly separated agent functionality across tasks.py, tools.py, models.py, utils.py, mcp.py, and coral_client.py
2. **MCP Integration**: Complete MCP protocol coverage for all agent tools with consistent async patterns
3. **Inter-Agent Communication**: Enhanced CoralClient with agent-specific methods and cross-validation
4. **Utility Classes**: Domain-specific utilities for portfolio optimization, goal analysis, and explanation generation
5. **Task Scheduling**: Structured task management for periodic operations like rebalancing and health checks
6. **Model Configuration**: Comprehensive data models and agent configuration classes
7. **Error Handling**: Robust error handling and logging throughout all components
