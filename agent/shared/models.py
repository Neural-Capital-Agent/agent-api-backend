from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid

# Existing models from agents.py
@dataclass
class MarketData:
    symbol: str
    price: float
    previous_close: float
    change: float
    change_percent: float
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    timestamp: Optional[datetime] = None

@dataclass
class MacroData:
    indicator: str
    value: float
    date: datetime
    frequency: str

# Portfolio Agent Models
class RiskLevel(Enum):
    CONSERVATIVE = 1
    BALANCED_CONSERVATIVE = 2
    BALANCED = 3
    GROWTH = 4
    AGGRESSIVE = 5

@dataclass
class Portfolio:
    id: str
    risk_level: RiskLevel
    allocations: Dict[str, float]  # ticker -> allocation percentage
    expected_return: float
    volatility: float
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class MacroSignal:
    signal_type: str
    condition: str
    triggered: bool
    trigger_date: Optional[datetime]
    action_description: str
    cooldown_days: int

@dataclass
class MacroSignals:
    yield_curve_inversion: MacroSignal
    inflation_shock: MacroSignal
    volatility_spike: MacroSignal
    credit_stress: MacroSignal
    pmi_contraction: MacroSignal
    market_momentum: MacroSignal
    timestamp: datetime

@dataclass
class RebalanceAction:
    id: str
    portfolio_id: str
    current_allocations: Dict[str, float]
    target_allocations: Dict[str, float]
    trades: List[Dict[str, Any]]  # [{"ticker": "SPY", "action": "sell", "amount": 0.1}]
    reason: str
    timestamp: datetime

@dataclass
class ExecutionResults:
    rebalance_id: str
    executed_trades: List[Dict[str, Any]]
    execution_status: str
    total_cost: float
    timestamp: datetime

@dataclass
class BacktestResults:
    portfolio_id: str
    start_date: datetime
    end_date: datetime
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    trades_executed: int

# Financial Planner Agent Models
class GoalType(Enum):
    HOUSE_DOWN_PAYMENT = "house_down_payment"
    RETIREMENT = "retirement"
    EMERGENCY_FUND = "emergency_fund"
    CHILD_EDUCATION = "child_education"
    EDUCATION = "education"  # Add this for test compatibility
    GENERAL_SAVINGS = "general_savings"  # Add this missing value

@dataclass
class GoalParameters:
    goal_type: GoalType
    target_amount: float
    time_horizon_years: int
    current_age: Optional[int] = None
    retirement_age: Optional[int] = None
    risk_tolerance: Optional[RiskLevel] = None
    monthly_investment: Optional[float] = None  # Add monthly investment field

@dataclass
class UserProfile:
    age: int
    income: float
    current_savings: float
    risk_tolerance: RiskLevel
    goals: List[GoalParameters]

@dataclass
class InvestmentStrategy:
    goal_type: GoalType
    recommended_allocation: Dict[str, float]
    risk_level: RiskLevel
    expected_return: float
    time_horizon: int
    constraints: Dict[str, Any]

@dataclass
class GlidePath:
    age_ranges: Dict[str, Dict[str, float]]  # age_range -> asset_allocation
    target_retirement_age: int

@dataclass
class BondLadder:
    total_amount: float
    time_horizon_years: int
    ladder_rungs: List[Dict[str, Any]]  # [{"maturity": "3M", "amount": 20000, "yield": 5.2}]

# Explainability Agent Models
@dataclass
class Action:
    id: str
    agent_source: str
    action_type: str
    parameters: Dict[str, Any]
    timestamp: datetime
    related_goal: Optional[str] = None

@dataclass
class Context:
    market_conditions: Dict[str, Any]
    macro_signals: MacroSignals
    portfolio_state: Optional[Portfolio]
    user_goals: List[GoalParameters]
    historical_context: Dict[str, Any]

@dataclass
class ExplanationResponse:
    action_id: str
    explanation: str
    risk_assessment: str
    historical_context: str
    confidence_score: float
    verification_hash: Optional[str] = None

# Coral Protocol Models
@dataclass
class CoralMessage:
    agent_id: str
    target_agent: str
    method: str
    parameters: Dict[str, Any]
    timestamp: datetime
    message_id: str = None

    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())

@dataclass
class CoralResponse:
    message_id: str
    agent_id: str
    response_data: Any
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class AgentRegistration:
    agent_id: str
    agent_type: str
    capabilities: List[str]
    endpoint: str
    status: str = "active"
    registered_at: datetime = None

    def __post_init__(self):
        if self.registered_at is None:
            self.registered_at = datetime.now()

# Agent-specific configuration models
@dataclass
class AgentConfig:
    agent_id: str
    agent_type: str
    enabled: bool = True
    max_concurrent_tasks: int = 5
    retry_attempts: int = 3
    timeout_seconds: int = 300
    log_level: str = "INFO"
    config_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.config_params is None:
            self.config_params = {}

@dataclass
class DataAgentConfig(AgentConfig):
    update_frequencies: Dict[str, str] = None
    data_sources: List[str] = None
    batch_size: int = 5
    rate_limit_delay: int = 1

    def __post_init__(self):
        super().__post_init__()
        if self.update_frequencies is None:
            self.update_frequencies = {
                "daily": ["market_data", "vix", "yield_curve"],
                "monthly": ["cpi", "unemployment", "fed_funds"]
            }
        if self.data_sources is None:
            self.data_sources = ["yahoo", "fred", "polygon"]

@dataclass
class PortfolioAgentConfig(AgentConfig):
    rebalancing_threshold: float = 0.02
    max_position_size: float = 0.4
    risk_budget: float = 0.15
    asset_universe: List[str] = None

    def __post_init__(self):
        super().__post_init__()
        if self.asset_universe is None:
            self.asset_universe = ["SPY", "QQQ", "BND", "GLD"]

@dataclass
class PlannerAgentConfig(AgentConfig):
    default_retirement_age: int = 65
    default_time_horizon: int = 30
    min_emergency_fund_months: int = 6
    max_goal_horizon: int = 50

@dataclass
class ExplainabilityAgentConfig(AgentConfig):
    explanation_cache_ttl: int = 3600
    min_confidence_threshold: float = 0.7
    max_explanation_length: int = 500
    jargon_complexity_level: str = "simple"  # simple, intermediate, advanced

# Performance and monitoring models
@dataclass
class AgentPerformanceMetrics:
    agent_id: str
    success_rate: float
    avg_response_time: float
    error_count: int
    total_requests: int
    last_updated: datetime = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

@dataclass
class TaskExecutionResult:
    task_id: str
    agent_id: str
    task_type: str
    status: str  # pending, running, completed, failed
    start_time: datetime
    end_time: Optional[datetime] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

@dataclass
class AgentHealthStatus:
    agent_id: str
    status: str  # healthy, degraded, unhealthy, offline
    last_heartbeat: datetime
    error_count_24h: int = 0
    response_time_p95: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0