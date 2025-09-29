from api.dependencies.db import supabase
from api.schemas.user_portafolio import (
    UserPortafolioCreate, UserGoalsCreate, UserPortafolioHoldingsCreate, 
    UserPreferencesCreate, UserInput
)
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

def process_onboarding_form(user_input: UserInput, user_id: str) -> Dict[str, Any]:
    """
    Main entry point for processing the onboarding form.
    Takes the UserInput model directly from the frontend and sets up the complete portfolio.
    """
    # Convert the UserInput model to a dict
    preferences_data = user_input.dict()
    
    # Process the portfolio setup
    result = set_up_portfolio_from_preferences(preferences_data, user_id)
    
    return result

def determine_risk_tier(user_preferences: UserPreferencesCreate) -> int:
    """
    Maps user preferences to a risk tier ID (1-5 scale)
    
    1 = Conservative
    2 = Moderately Conservative
    3 = Moderate
    4 = Moderately Aggressive
    5 = Aggressive
    
    The mapping considers:
    - risk_tolerance (direct input, scaled appropriately)
    - investment_horizon (longer horizon allows more risk)
    - primary_goal (capital preservation is more conservative)
    - experience_level (beginners get more conservative allocations)
    """
    base_score = 0
    
    # Map risk tolerance (1-10 scale) to a 1-5 scale
    risk_score = max(1, min(5, round(user_preferences.risk_tolerance / 2)))
    base_score += risk_score
    
    # Adjust for investment horizon
    horizon_adjustment = {
        "<1y": -1,
        "1–3y": -0.5,
        "3–5y": 0,
        "5–10y": 0.5,
        "10+y": 1
    }
    base_score += horizon_adjustment.get(user_preferences.investment_horizon, 0)
    
    # Adjust for primary goal
    if "preserve capital" in user_preferences.primary_goal.lower():
        base_score -= 1
    elif "growth" in user_preferences.primary_goal.lower():
        base_score += 0.5
        
    # Adjust for experience level
    experience_adjustment = {
        "Beginner": -0.5,
        "Intermediate": 0,
        "Advanced": 0.5
    }
    base_score += experience_adjustment.get(user_preferences.experience_level, 0)
    
    # Ensure the final score is between 1-5
    final_risk_tier = max(1, min(5, round(base_score)))
    
    return final_risk_tier

def validate_user_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and normalizes user preference inputs
    """
    validated = {}
    
    # Convert snake_case to camelCase for frontend-backend compatibility
    key_mapping = {
        "primaryGoal": "primary_goal",
        "investmentHorizon": "investment_horizon",
        "experienceLevel": "experience_level",
        "riskTolerance": "risk_tolerance",
        "startingAmount": "starting_amount",
        "monthlyContribution": "monthly_contribution",
        "assetsToAvoid": "assets_to_avoid",
        "comfortableAssets": "comfortable_assets",
        "autoPayAmount": "auto_pay_amount",
        "autoPayCadence": "auto_pay_cadence",
        "autoPayToSavings": "auto_pay_to_savings",
        "budgetGuardrail": "budget_guardrail",
        "concentrationCap": "concentration_cap",
        "consentToAutomation": "consent_to_automation",
        "contributionDay": "contribution_day",
        "createAutoSplit": "create_auto_split",
        "dcaCadence": "dca_cadence",
        "equityStopLoss": "equity_stop_loss",
        "equityTakeProfit": "equity_take_profit",
        "marginAllowed": "margin_allowed",
        "maxDrawdown": "max_drawdown",
        "portfolioDrawdownAlert": "portfolio_drawdown_alert",
        "rebalancing": "rebalancing",
        "sectorCaps": "sector_caps",
        "splitRecipe": "split_recipe",
        "stateOfResidence": "state_of_residence",
        "taxWrapper": "tax_wrapper"
    }
    
    # Transform keys and perform basic validation
    for key, value in preferences.items():
        if key in key_mapping:
            snake_key = key_mapping[key]
            
            # Handle empty strings
            if isinstance(value, str) and value == "":
                if snake_key in ["auto_pay_amount"]:
                    validated[snake_key] = 0
                else:
                    validated[snake_key] = None
            # Handle boolean or yes/no strings for specific fields
            elif snake_key in ["auto_pay_to_savings", "create_auto_split"]:
                if isinstance(value, bool):
                    validated[snake_key] = "yes" if value else "no"
                elif isinstance(value, str):
                    validated[snake_key] = value.lower()
                else:
                    validated[snake_key] = "no"
            # Handle numeric values
            elif snake_key in ["starting_amount", "monthly_contribution", "auto_pay_amount"]:
                try:
                    validated[snake_key] = float(value)
                except (ValueError, TypeError):
                    validated[snake_key] = 0
            # Handle percentage values
            elif snake_key in ["risk_tolerance", "budget_guardrail", "concentration_cap", 
                              "equity_stop_loss", "equity_take_profit", "max_drawdown",
                              "portfolio_drawdown_alert"]:
                try:
                    validated[snake_key] = int(value)
                except (ValueError, TypeError):
                    validated[snake_key] = None
            else:
                validated[snake_key] = value
    
    return validated

def set_user_preferences(preferences_data: Dict[str, Any], user_id: str) -> Optional[str]:
    """
    Stores user investment preferences in the database
    """
    validated_data = validate_user_preferences(preferences_data)
    
    # Create a preferences ID
    preferences_id = str(uuid.uuid4())
    
    # Convert data format to match the database schema
    preferences_db_data = {
        "preferences_id": preferences_id,
        "user_id": user_id,
        "primary_goal": validated_data.get("primary_goal"),
        "investment_horizon": validated_data.get("investment_horizon"),
        "experience_level": validated_data.get("experience_level"),
        "tax_wrapper": validated_data.get("tax_wrapper"),
        "risk_tolerance": validated_data.get("risk_tolerance"),
        "max_drawdown": validated_data.get("max_drawdown"),
        "comfortable_assets": validated_data.get("comfortable_assets", []),
        "assets_to_avoid": validated_data.get("assets_to_avoid", []),
        "starting_amount": validated_data.get("starting_amount"),
        "monthly_contribution": validated_data.get("monthly_contribution"),
        "contribution_day": validated_data.get("contribution_day"),
        "dca_cadence": validated_data.get("dca_cadence"),
        "budget_guardrail": validated_data.get("budget_guardrail"),
        "equity_stop_loss": validated_data.get("equity_stop_loss"),
        "equity_take_profit": validated_data.get("equity_take_profit"),
        "portfolio_drawdown_alert": validated_data.get("portfolio_drawdown_alert"),
        "rebalancing": validated_data.get("rebalancing"),
        "create_auto_split": validated_data.get("create_auto_split"),
        "split_recipe": validated_data.get("split_recipe"),
        "auto_pay_to_savings": validated_data.get("auto_pay_to_savings"),
        "auto_pay_amount": validated_data.get("auto_pay_amount"),
        "auto_pay_cadence": validated_data.get("auto_pay_cadence"),
        "state_of_residence": validated_data.get("state_of_residence"),
        "margin_allowed": validated_data.get("margin_allowed"),
        "concentration_cap": validated_data.get("concentration_cap"),
        "sector_caps": validated_data.get("sector_caps"),
        "consent_to_automation": validated_data.get("consent_to_automation"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Insert data into user_preferences table
    response = supabase.table("user_preferences").insert(preferences_db_data).execute()
    return preferences_id if response.data else None

def set_up_portfolio_from_preferences(preferences_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Creates a complete user portfolio setup from the preferences form data
    """
    # Step 1: Store user preferences
    preferences_id = set_user_preferences(preferences_data,user_id)
    if not preferences_id:
        raise Exception("Failed to store user preferences")
    
    # Convert raw preferences to validated format
    validated_prefs = validate_user_preferences(preferences_data)
    user_preferences = UserPreferencesCreate(**validated_prefs)
    
    # Step 2: Determine risk tier
    risk_tier_id = determine_risk_tier(user_preferences)
    
    # Step 3: Create user goal
    target_date = datetime.now().replace(year=datetime.now().year + 10)
    goal_data = UserGoalsCreate(
        user_id=user_id,
        financial_goal=user_preferences.primary_goal,
        target_amount=user_preferences.starting_amount * 1.5,
        target_date=target_date.isoformat(),  # Convert to ISO format string
        risk_tiers_id=risk_tier_id
    )
    goal_id = set_user_goals(goal_data, user_id)
    if not goal_id:
        raise Exception("Failed to create user goal")
    
    # Step 4: Create portfolio
    creation_date = datetime.now()
    portfolio_data = UserPortafolioCreate(
        user_id=user_id,
        goal_id=goal_id,
        portfolio_name=f"{user_preferences.primary_goal} Portfolio",
        current_risk_tier_id=risk_tier_id,
        creation_date=creation_date.isoformat(),  # Convert to ISO format string
        current_total_value=user_preferences.starting_amount,
        preferences_id=preferences_id
    )
    portfolio_id = set_user_portfolio(portfolio_data)
    if not portfolio_id:
        raise Exception("Failed to create portfolio")
    
    # Step 5: Set up initial portfolio holdings (simplified version)
    # In a real implementation, you would create multiple holdings based on the risk tier
    # and recommended asset allocation
    
    # Get sample asset ID and name from database
    asset_query = supabase.table("assets").select("assetid, assetname, ticker").eq("ticker", "SPY").execute()
    asset_data = asset_query.data[0] if asset_query.data else {"assetid": str(uuid.uuid4()), "assetname": "S&P 500 ETF", "ticker": "SPY"}
    
    # Calculate price per unit
    price_per_unit = 400  # Sample price
    units = user_preferences.starting_amount / price_per_unit if user_preferences.starting_amount > 0 else 0
    
    # For now, we'll create a sample holding (e.g., SPY ETF)
    holding_data = UserPortafolioHoldingsCreate(
        user_portfolio_id=portfolio_id,
        asset_id=asset_data["assetid"],
        asset_symbol=asset_data["ticker"],
        asset_name=asset_data["assetname"],
        number_of_units=units,
        average_cost_basis=price_per_unit,
        current_value=user_preferences.starting_amount,
        current_allocation_percentage=100.0,
        target_allocation_percentage=100.0,
        quantity=units,
        average_cost=price_per_unit,
        current_price=price_per_unit,
        market_value=user_preferences.starting_amount,
        allocation_percentage=100.0
    )
    holding_id = set_user_portfolio_holdings(holding_data)
    
    # Return summary of all created data
    return {
        "preferences_id": preferences_id,
        "goal_id": goal_id,
        "portfolio_id": portfolio_id,
        "risk_tier_id": risk_tier_id,
        "total_value": user_preferences.starting_amount,
        "holdings": [{"holding_id": holding_id, "asset": "SPY"}] if holding_id else []
    }

def set_user_goals(user_goals: UserGoalsCreate, user_id: str) -> Optional[str]:
    """
    Stores user financial goals in the database
    """
    goal_data = user_goals.dict()
    
    # Add goal_id and user_id
    goal_data["goal_id"] = str(uuid.uuid4())
    goal_data["user_id"] = user_id
    
    # Convert datetime objects to ISO format strings
    if isinstance(goal_data.get("target_date"), datetime):
        goal_data["target_date"] = goal_data["target_date"].isoformat()
    
    # Use lowercase column names to match the actual database schema
    renamed_data = {
        "goalid": goal_data["goal_id"],
        "userid": goal_data["user_id"],
        "goaldescription": goal_data["financial_goal"],
        "goaltype": "Investment",
        "targetamount": goal_data["target_amount"],
        "targetdate": goal_data["target_date"],
        "currentsavings": goal_data.get("starting_amount", 0),
        "assignedrisktierid": goal_data["risk_tiers_id"]
    }
    
    response = supabase.table("user_goals").insert(renamed_data).execute()
    return renamed_data["goalid"] if response.data else None

def set_user_portfolio(user_portfolio: UserPortafolioCreate) -> Optional[str]:
    """
    Stores user portfolio in the database
    """
    portfolio_data = user_portfolio.dict()
    
    # If portfolio_id is not set, create one
    if not portfolio_data.get("user_portfolio_id"):
        portfolio_data["user_portfolio_id"] = str(uuid.uuid4())
    
    # Convert datetime objects to ISO format strings
    if isinstance(portfolio_data.get("creation_date"), datetime):
        portfolio_data["creation_date"] = portfolio_data["creation_date"].isoformat()
    
    if isinstance(portfolio_data.get("last_rebalance_date"), datetime):
        portfolio_data["last_rebalance_date"] = portfolio_data["last_rebalance_date"].isoformat()
    
    # Rename fields to match database schema with lowercase column names
    renamed_data = {
        "userportfolioid": portfolio_data["user_portfolio_id"],
        "userid": portfolio_data["user_id"],
        "goalid": portfolio_data["goal_id"],
        "portfolioname": portfolio_data["portfolio_name"],
        "currentrisktierid": portfolio_data["current_risk_tier_id"],
        "creationdate": portfolio_data["creation_date"],
        "lastrebalancedate": portfolio_data.get("last_rebalance_date"),
        "currenttotalvalue": portfolio_data["current_total_value"]
    }
    
    response = supabase.table("user_portfolios").insert(renamed_data).execute()
    return renamed_data["userportfolioid"] if response.data else None

def set_user_portfolio_holdings(user_portfolio_holdings: UserPortafolioHoldingsCreate) -> Optional[str]:
    """
    Stores user portfolio holdings in the database
    """
    holdings_data = user_portfolio_holdings.dict()
    
    # Add holding_id if not already set
    if not holdings_data.get("holding_id"):
        holdings_data["holding_id"] = str(uuid.uuid4())
    
    # Set required fields that might be missing
    if "asset_name" not in holdings_data or not holdings_data["asset_name"]:
        asset_name_query = supabase.table("assets").select("assetname").eq("assetid", holdings_data["asset_id"]).execute()
        holdings_data["asset_name"] = asset_name_query.data[0]["assetname"] if asset_name_query.data else "Unknown Asset"
    
    # Set additional required fields
    holdings_data["quantity"] = holdings_data.get("number_of_units", 0)
    holdings_data["average_cost"] = holdings_data.get("average_cost_basis", 0)
    holdings_data["current_price"] = holdings_data.get("current_value", 0) / holdings_data.get("number_of_units", 1) if holdings_data.get("number_of_units", 0) > 0 else 0
    holdings_data["market_value"] = holdings_data.get("current_value", 0)
    holdings_data["allocation_percentage"] = holdings_data.get("current_allocation_percentage", 0)
    
    # Rename fields to match database schema with lowercase column names
    renamed_data = {
        "holdingid": holdings_data["holding_id"],
        "userportfolioid": holdings_data["user_portfolio_id"],
        "assetid": holdings_data["asset_id"],
        "currentallocationpercentage": holdings_data["current_allocation_percentage"],
        "targetallocationpercentage": holdings_data["target_allocation_percentage"],
        "numberofunits": holdings_data["number_of_units"],
        "averagecostbasis": holdings_data["average_cost_basis"],
        "currentvalue": holdings_data["current_value"]
    }
    
    response = supabase.table("user_portfolio_holdings").insert(renamed_data).execute()
    return renamed_data["holdingid"] if response.data else None

def log_portfolio_creation(user_portfolio_id: str, asset_ids: list, user_id: str) -> None:
    """
    Logs the portfolio creation as transactions in the transaction_logs table
    """
    for asset_id in asset_ids:
        log_data = {
            "logid": str(uuid.uuid4()),
            "userportfolioid": user_portfolio_id,
            "timestamp": datetime.now().isoformat(),
            "actiontype": "Initialize",
            "assetid": asset_id,
            "quantity": 0,  # Initial allocation
            "price": 0,     # No price for initialization
            "amount": 0,    # No amount for initialization
            "reason": "Portfolio Creation",
            "issimulated": False
        }
        
        try:
            supabase.table("transaction_logs").insert(log_data).execute()
        except Exception as e:
            print(f"Error logging transaction: {e}")
            # Continue even if logging fails
def get_user_goals(user_id: str) -> bool:
    """
    Checks if the user has set up financial goals
    """
    response = supabase.table("user_goals").select("*").eq("userid", user_id).execute()
    return len(response.data) > 0 if response.data is not None else False