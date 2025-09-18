from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum

class InvestmentHorizon(str, Enum):
    LESS_THAN_1Y = "≤1y"  # Updated to match frontend
    ONE_TO_3Y = "1–3y"
    THREE_TO_5Y = "3–5y"
    FIVE_TO_10Y = "5–10y"
    TEN_PLUS_Y = "10y+"

class ExperienceLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

class AutoPayCadence(str, Enum):
    WEEKLY = "Weekly"
    BIWEEKLY = "Biweekly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"

class RebalancingStrategy(str, Enum):
    QUARTERLY = "Quarterly"
    SEMIANNUAL = "Semiannual"
    THRESHOLD = "Threshold-based (±5%)"
    OFF = "Off"  # Added to match frontend "Off" option

class TaxWrapper(str, Enum):
    ROTH = "Roth"
    TRADITIONAL = "Traditional"
    TAXABLE = "Taxable"

class UserPreferencesCreate(BaseModel):
    primary_goal: str
    investment_horizon: InvestmentHorizon
    experience_level: ExperienceLevel
    risk_tolerance: int = Field(..., ge=1, le=10)
    starting_amount: float
    monthly_contribution: float
    
    # Optional fields
    assets_to_avoid: Optional[List[str]] = []
    comfortable_assets: Optional[List[str]] = []
    auto_pay_amount: Optional[float] = None
    auto_pay_cadence: Optional[AutoPayCadence] = None
    auto_pay_to_savings: Optional[str] = "no"
    budget_guardrail: Optional[int] = None
    concentration_cap: Optional[int] = None
    consent_to_automation: Optional[bool] = False
    contribution_day: Optional[int] = 1
    create_auto_split: Optional[str] = "no"
    dca_cadence: Optional[AutoPayCadence] = None
    equity_stop_loss: Optional[int] = None
    equity_take_profit: Optional[int] = None
    margin_allowed: Optional[bool] = False
    max_drawdown: Optional[int] = None
    portfolio_drawdown_alert: Optional[int] = None
    rebalancing: Optional[RebalancingStrategy] = None
    sector_caps: Optional[List[Dict[str, Any]]] = []
    split_recipe: Optional[Dict[str, int]] = None
    state_of_residence: Optional[str] = None
    tax_wrapper: Optional[TaxWrapper] = None

class UserGoalsCreate(BaseModel):
    user_id: str
    financial_goal: str
    target_amount: float
    target_date: datetime
    risk_tiers_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserPortafolioCreate(BaseModel):
    user_portfolio_id: Optional[str] = None  # UUID, primary key
    user_id: str  # UUID, foreign key to users.id_user
    goal_id: str  # UUID, foreign key to user_goals.goal_id
    portfolio_name: str
    current_risk_tier_id: int  # integer, foreign key to risk_tiers
    creation_date: Optional[datetime] = None
    last_rebalance_date: Optional[datetime] = None
    current_total_value: float
    preferences_id: Optional[str] = None  # Link to user preferences

class UserPortafolioHoldingsCreate(BaseModel):
    holding_id: Optional[str] = None  # UUID, primary key
    user_portfolio_id: str  # UUID, foreign key to user_portfolios table
    asset_id: str  # UUID, foreign key to assets table
    asset_symbol: str  # For reference
    asset_name: str = "Unknown"  # Adding required field
    current_allocation_percentage: float
    target_allocation_percentage: float
    number_of_units: float
    average_cost_basis: float
    current_value: float
    
    # Adding required fields that were missing
    quantity: float = 0  
    average_cost: float = 0
    current_price: float = 0
    market_value: float = 0
    allocation_percentage: float = 0
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True

class UserInput(BaseModel):
    """
    This class handles the complete user input from the frontend onboarding form.
    It contains all preferences and can be passed directly to the setup function.
    """
    # Core preferences
    primaryGoal: str
    investmentHorizon: str
    experienceLevel: str
    riskTolerance: int
    startingAmount: Union[float, str]  # Allow string input that will be converted
    monthlyContribution: Union[float, str]  # Allow string input that will be converted
    
    # Optional preferences with defaults
    assetsToAvoid: Optional[List[str]] = []
    comfortableAssets: Optional[List[str]] = []
    autoPayAmount: Optional[Union[str, float]] = ""
    autoPayCadence: Optional[str] = "Monthly"
    autoPayToSavings: Optional[Union[str, bool]] = "no"  # Accept either string or boolean
    budgetGuardrail: Optional[Union[int, str, float]] = None
    concentrationCap: Optional[int] = None
    consentToAutomation: Optional[bool] = False
    contributionDay: Optional[int] = 1
    createAutoSplit: Optional[Union[str, bool]] = "no"  # Accept either string or boolean
    dcaCadence: Optional[str] = "Monthly"
    equityStopLoss: Optional[Union[int, str, float]] = None
    equityTakeProfit: Optional[Union[int, str, float]] = None
    marginAllowed: Optional[bool] = False
    maxDrawdown: Optional[Union[int, str, float]] = None
    portfolioDrawdownAlert: Optional[Union[int, str, float]] = None
    rebalancing: Optional[str] = None
    sectorCaps: Optional[List[Dict[str, Any]]] = []
    splitRecipe: Optional[Dict[str, int]] = None
    stateOfResidence: Optional[str] = None
    taxWrapper: Optional[str] = None

    # Validators to convert string values to appropriate types
    @validator('startingAmount', 'monthlyContribution', 'autoPayAmount', 'budgetGuardrail', 
               'equityStopLoss', 'equityTakeProfit', 'maxDrawdown', 'portfolioDrawdownAlert', pre=True)
    def convert_numeric_strings(cls, v):
        if isinstance(v, str) and v.strip():
            try:
                return float(v)
            except ValueError:
                pass
        return v
    
    @validator('createAutoSplit', 'autoPayToSavings', pre=True)
    def convert_bool_to_str(cls, v):
        """Convert boolean values to yes/no strings for compatibility"""
        if isinstance(v, bool):
            return "yes" if v else "no"
        return v