"""
End-to-End Agent Workflow Demonstration
This script demonstrates a complete user journey through all 4 financial agents:
1. DataAgent: Collects and validates market data
2. PortfolioAgent: Performs algorithmic portfolio optimization
3. PlannerAgent: Parses natural language financial goals
4. ExplainabilityAgent: Provides explanations and jargon translation

DATA FLOW:
- Step 1 collects data and saves to temp_storage/ using json_read_write()
- Step 2 loads data from temp_storage/ using json_read_write()
- json_read_write() utility handles both reading and w           print("   Data Flow: Step 1 → json_read_write() → temp_storage/ → json_read_write() → Step 2")
        print("   Persistence: Data saved/loaded using json_read_write() utility function")     print("   Data Flow: Step 1 → json_read_write() → temp_storage/ → json_read_write() → Step 2")
        print("   Persistence: Data saved/loaded using json_read_write() utility function")     print("   Data Flow: Step 1 → json_read_write() → temp_storage/ → json_read_write() → Step 2")
        print("   Persistence: Data saved/loaded using json_read_write() utility function")     print("   Data Flow: Step 1 → json_read_write() → temp_storage/ → json_read_write() → Step 2")
        print("   Persistence: Data saved/loaded using json_read_write() utility function")ting JSON files

UTILITY FUNCTIONS:
- json_read_write(file_location, mode, data): Read/write JSON files
  - mode 'r': Read JSON file
  - mode 'w': Write data to JSON file

This is a demonstration script, not a test with assertions.
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, date
from typing import Dict, Any
import uuid
import time

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def json_read_write(file_location: str, mode: str, data: Any = None) -> Any:
    """
    Utility function for reading and writing JSON files.
    
    Args:
        file_location (str): Path to the JSON file
        mode (str): 'r' for read, 'w' for write
        data (Any): Data to write (only required for write mode)
    
    Returns:
        For read mode: Parsed JSON data
        For write mode: None
    
    Raises:
        FileNotFoundError: If file doesn't exist in read mode
        json.JSONDecodeError: If JSON parsing fails
        Exception: For other file operations
    """
    try:
        if mode == 'r':
            with open(file_location, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif mode == 'w':
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_location), exist_ok=True)
            with open(file_location, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            return None
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'r' for read or 'w' for write.")
    except FileNotFoundError:
        if mode == 'r':
            raise FileNotFoundError(f"File not found: {file_location}")
        else:
            raise
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file {file_location}: {e}")
    except Exception as e:
        raise Exception(f"Error {'reading' if mode == 'r' else 'writing'} file {file_location}: {e}")

# Sample user data based on DATABASE_SCHEMA.md
SAMPLE_USER = {
    "id": 1,  # Internal auto-increment ID
    "created_at": datetime.now().isoformat(),
    "email": "john.doe@example.com",
    "id_alpaca": "ALPACA123456",  # Alpaca trading account ID
    "city": "New York",
    "contact_email": "john.doe@example.com",
    "contact_family": "Jane Doe",
    "contact_given": "John",
    "country_of_birth": "USA",
    "country_of_citizenship": "USA",
    "date_of_birth": "1985-06-15",  # Date of birth for age-based planning
    "family_name": "Doe",
    "given_name": "John",
    "phone": "+1-555-0123",
    "postal_code": "10001",
    "state": "NY",
    "street_address": "123 Main Street",
    "tax_id": "123-45-6789",
    "id_user": str(uuid.uuid4())  # Primary key UUID
}

async def make_request(method: str, endpoint: str, data: Dict[str, Any] = None, delay: float = 0.5) -> Dict[str, Any]:
    """Make an HTTP request to the API with rate limit handling"""
    url = f"{BASE_URL}{endpoint}"
    user_id = SAMPLE_USER["id_user"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer demo_token_{user_id}",  # Use proper auth header
        "X-User-ID": user_id  # Explicit user ID header
    }

    # Add delay to avoid rate limits
    if delay > 0:
        await asyncio.sleep(delay)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                if isinstance(data, str):
                    # For string bodies, use content instead of json
                    headers["Content-Type"] = "text/plain"
                    response = await client.post(url, content=data, headers=headers)
                else:
                    response = await client.post(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limit hit - extract retry time and wait
                try:
                    error_data = response.json()
                    retry_after = error_data.get("retry_after_seconds", 60)
                    print(f"Rate limit hit, waiting {retry_after} seconds...")
                    await asyncio.sleep(retry_after + 1)  # Add 1 second buffer
                    
                    # Retry the request once
                    if method.upper() == "GET":
                        response = await client.get(url, headers=headers)
                    elif method.upper() == "POST":
                        if isinstance(data, str):
                            headers["Content-Type"] = "text/plain"
                            response = await client.post(url, content=data, headers=headers)
                        else:
                            response = await client.post(url, json=data, headers=headers)
                    
                    if response.status_code == 200:
                        return response.json()
                except:
                    pass
                
                print(f"Request failed: {response.status_code} - Rate limited")
                return {"error": "rate_limited", "status_code": response.status_code}
            else:
                print(f"Request failed: {response.status_code} - {response.text}")
                return {"error": response.text, "status_code": response.status_code}

    except Exception as e:
        print(f"Request error: {e}")
        return {"error": str(e)}

## Agent 1: DataAgent
## --------------------------

async def step_1_data_collection():
    """
    STEP 1: DATA AGENT - Market Data Collection & Validation
    
    The DataAgent is responsible for:
    - Fetching real-time market data for stocks, ETFs, and cryptocurrencies
    - Collecting macro-economic indicators (GDP, inflation, unemployment, interest rates)
    - Providing clean, validated financial data to other agents
    - Previously included LLM-based signal validation (now disabled for pure data focus)
    
    This agent serves as the foundation data layer for all investment decisions.
    """
    print("\n" + "="*60)
    print("STEP 1: DATA AGENT - Market Data Collection & Validation")
    print("="*60)

    print(f"User: {SAMPLE_USER['given_name']} {SAMPLE_USER['family_name']} ({SAMPLE_USER['email']})")
    print(f"Location: {SAMPLE_USER['city']}, {SAMPLE_USER['state']} {SAMPLE_USER['postal_code']}")

    # Get market data for key assets
    print("\nCollecting market data for major assets...")
    tickers = ["AAPL", "MSFT", "SPY", "BTC-USD"]
    market_data_results = {}

    for i, ticker in enumerate(tickers):
        ticker_data = await make_request("GET", f"/agents/data/market/{ticker}", delay=0.5)
        if "error" not in ticker_data and "data" in ticker_data:
            market_data_results[ticker] = ticker_data["data"]
            price = ticker_data['data'].get('price', 'N/A')
            change_pct = ticker_data['data'].get('change_percent', 0)
            
            # Handle None values properly
            if price == 'N/A' or price is None:
                print(f"   {ticker}: Price unavailable")
            elif change_pct is None:
                print(f"   {ticker}: ${price:.2f} (change unavailable)")
            else:
                print(f"   {ticker}: ${price:.2f} ({change_pct:+.2f}%)")
        else:
            print(f"   {ticker}: Data fetch failed")

    # Simulate market data structure for compatibility
    market_data = {
        "data": market_data_results,
        "total_assets": len(market_data_results)
    }

    print("Market data collection completed")

    # Get macro indicators
    print("\nCollecting macro-economic indicators...")
    indicators = ["GDP", "INFLATION", "UNEMPLOYMENT", "INTEREST_RATES"]
    macro_results = {}

    for i, indicator in enumerate(indicators):
        macro_data = await make_request("GET", f"/agents/data/macro/{indicator}", delay=0.5)
        if "error" not in macro_data and "data" in macro_data:
            macro_results[indicator] = macro_data["data"]
            if macro_data["data"]:
                latest = macro_data["data"][-1]  # Get latest data point
                value = latest.get('value', 'N/A')
                date = latest.get('date', 'N/A')
                print(f"   {indicator}: {value} ({date})")
        else:
            print(f"   {indicator}: Data fetch failed")

    # Simulate macro data structure for compatibility
    macro_data = {
        "indicators": macro_results
    }

    print("Macro data collection completed")

    # LLM validation commented out - DataAgent now focuses on pure data retrieval
    # print("\nValidating market signals with AI...")
    # signals_to_validate = {
    #     "signals": [
    #         {"type": "momentum", "value": 0.15, "threshold": 0.10},
    #         {"type": "volatility", "value": 0.25, "threshold": 0.20}
    #     ]
    # }
    #
    # validation_result = await make_request("POST", "/llm/validate-signals", signals_to_validate, delay=3.0)
    #
    # if "error" not in validation_result:
    #     print("Signal validation completed")
    #     print(f"   Validation result: {validation_result.get('is_valid', 'Unknown')}")
    #     if "reasoning" in validation_result:
    #         print(f"   AI Reasoning: {validation_result['reasoning'][:100]}...")
    # else:
    #     print("Signal validation failed, continuing with demo...")

    print("Agent 1 - Data Agent completed - Pure data retrieval (LLM validation disabled)\n")
    print("=======================================================================================")
    
    # Create a simple validation result for demo compatibility
    validation_result = {
        "signals": [],
        "validation_method": "rule_based_only",
        "note": "DataAgent now focuses purely on data retrieval - LLM validation commented out"
    }

    return market_data, macro_data, validation_result

## Agent 2: PortfolioAgent
## --------------------------

async def step_2_portfolio_optimization(market_data, macro_data):
    
    
    """

    STEP 2: PORTFOLIO AGENT - Algorithmic Optimization & Risk Management
    
    The PortfolioAgent handles:
    - Modern Portfolio Theory (MPT) based optimization
    - Risk-adjusted asset allocation using mathematical models
    - Portfolio rebalancing with transaction cost considerations
    - Sharpe ratio maximization and efficient frontier calculations
    - Constraint-based optimization (max single asset, minimum diversification, etc.)
    
    This agent uses quantitative methods to build mathematically optimal portfolios
    based on the user's risk tolerance, time horizon, and investment goals.
    
    """


    print("\n" + "="*60)
    print("STEP 2: PORTFOLIO AGENT - Algorithmic Optimization & Risk Management")
    print("="*60)

    # Build initial portfolio
    print("\nBuilding optimized portfolio...")
    portfolio_request = {
        "risk_level": 3,  # Balanced
        "investment_amount": 100000,
        "time_horizon_years": 10,
        "goal": "retirement_savings",  ## This is the GOAL ==============================
        "constraints": {
            "max_single_asset": 0.20,
            "min_assets": 5,
            "excluded_assets": []
        }
    }

    portfolio_result = await make_request("POST", "/agents/portfolio/build", portfolio_request, delay=1.0)

    # Debug: Print the raw API response
    print(f"   DEBUG - Raw portfolio API response: {portfolio_result}")

    if "error" not in portfolio_result:
        print("Portfolio built successfully")
        if "portfolio" in portfolio_result and "portfolio" in portfolio_result["portfolio"]:
            # Fix: Handle the nested portfolio structure
            portfolio = portfolio_result["portfolio"]["portfolio"]
            print(f"   Expected Return: {portfolio.get('expected_return', 0):.1%}")
            print(f"   Expected Risk: {portfolio.get('expected_risk', 0):.1%}")
            print(f"   Sharpe Ratio: {portfolio.get('sharpe_ratio', 0):.2f}")

            print("\n   Asset Allocation:")
            if "allocations" in portfolio and portfolio["allocations"]:
                for asset, weight in portfolio["allocations"].items():
                    print(f"     {asset}: {weight:.1%}")
            else:
                print("     No allocation data available")
        else:
            print("     Portfolio data structure issue")
            print(f"     DEBUG - Full response: {portfolio_result}")
    else:
        print("Portfolio building failed, continuing with demo...")
        print(f"   Error details: {portfolio_result}")

    # Simulate rebalancing
    print("\nSimulating portfolio rebalancing...")
    rebalance_request = {
        "current_portfolio": {
            "AAPL": 0.25,
            "MSFT": 0.20,
            "SPY": 0.30,
            "BTC-USD": 0.15,
            "TLT": 0.10
        },
        "target_allocations": {
            "AAPL": 0.20,
            "MSFT": 0.25,
            "SPY": 0.25,
            "BTC-USD": 0.10,
            "TLT": 0.20
        },
        "transaction_costs": 0.001
    }

    rebalance_result = await make_request("POST", "/agents/portfolio/rebalance", rebalance_request, delay=1.0)

    if "error" not in rebalance_result:
        print("Rebalancing completed")
        if "actions" in rebalance_result:
            print("   Rebalancing actions:")
            for action in rebalance_result["actions"][:3]:  # Show first 3
                print(f"     {action.get('action', 'Unknown')}: {action.get('asset', 'N/A')} {action.get('amount', 0):.2f} shares")
    else:
        print("Rebalancing failed, continuing with demo...")

    return portfolio_result, rebalance_result

## Agent 3: PlannerAgent
## --------------------------

async def step_3_goal_parsing():
    """
    
    STEP 3: PLANNER AGENT - Natural Language Goal Parsing & Strategy Creation
    
    The PlannerAgent specializes in:
    - Parsing natural language financial goals into structured data
    - Converting phrases like "save for my child's college" into quantified targets
    - Extracting key parameters: timeline, amounts, risk tolerance, life stage
    - Creating personalized investment strategies based on parsed goals
    - Age-based financial planning recommendations
    
    This agent bridges the gap between human language and algorithmic planning,
    making financial planning accessible through natural conversation.

    """

    print("\n" + "="*60)
    print("STEP 3: PLANNER AGENT - Natural Language Goal Parsing")
    print("="*60)

    # Parse a financial goal
    print("\nParsing natural language financial goal...")
    goal_text = "I want to save $500,000 for my child's college education in 15 years. I'm currently 40 years old and can invest $1,200 per month."

    # The endpoint expects just a string body, not a JSON object
    goal_result = await make_request("POST", "/agents/planner/parse-goal", goal_text, delay=1.0)

    # Debug: Print the raw API response
    print(f"   DEBUG - Raw goal parsing API response: {goal_result}")

    if "error" not in goal_result:
        print("Goal parsed successfully")
        if "parsed_goal" in goal_result and "parsed_goal" in goal_result["parsed_goal"]:
            # Fix: Handle the nested parsed_goal structure
            parsed = goal_result["parsed_goal"]["parsed_goal"]
            print(f"   Goal Type: {parsed.get('goal_type', 'Unknown')}")
            print(f"   Target Amount: ${parsed.get('target_amount', 0):,}")
            print(f"   Time Horizon: {parsed.get('time_horizon_years', 0)} years")
            print(f"   Risk Level: {parsed.get('risk_level', 'Unknown')}")
            print(f"   Monthly Investment: ${parsed.get('monthly_investment', 0):,}")
        else:
            print(f"   DEBUG - Parsing goal structure issue: {goal_result}")
    else:
        print("Goal parsing failed, continuing with demo...")
        print(f"   Error details: {goal_result}")

    # Create investment strategy
    print("\nCreating investment strategy...")
    strategy_request = {
        "goal": {
            "goal_type": "education",
            "time_horizon": 15,
            "target_amount": 500000,
            "monthly_investment": 1200
        },
        "user_profile": {
            "age": 40,
            "risk_tolerance": 3,
            "initial_investment": 50000,
            "monthly_contribution": 1200
        }
    }

    strategy_result = await make_request("POST", "/agents/planner/create-strategy", strategy_request, delay=1.0)

    # Debug: Print the raw API response
    print(f"   DEBUG - Raw strategy API response: {strategy_result}")

    if "error" not in strategy_result:
        print("Strategy created successfully")
        if "strategy" in strategy_result and "strategy" in strategy_result["strategy"]:
            # Fix: Handle the nested strategy structure
            strategy = strategy_result["strategy"]["strategy"]
            print(f"   Recommended Allocation: {strategy.get('allocation_type', 'Unknown')}")
            print(f"   Projected Value: ${strategy.get('projected_value', 0):,}")
            print(f"   Confidence Level: {strategy.get('confidence_level', 'Unknown')}")
        else:
            print("   Strategy data structure issue")
            print(f"   DEBUG - Full strategy response: {strategy_result}")
    else:
        print("Strategy creation failed, continuing with demo...")
        print(f"   Error details: {strategy_result}")

    return goal_result, strategy_result

## Agent 4: ExplainabilityAgent
## --------------------------

async def step_4_explanations(portfolio_result, goal_result):
    """
    STEP 4: EXPLAINABILITY AGENT - Decision Explanations & Jargon Translation
    
    The ExplainabilityAgent provides:
    - Clear explanations of why specific investment decisions were made
    - Translation of complex financial jargon into plain English
    - Risk assessment explanations with confidence scores
    - Educational content to help users understand their investments
    - Transparency into the AI decision-making process
    
    This agent ensures users understand their financial plans and builds trust
    through clear, educational explanations of complex investment concepts.
    """
    print("\n" + "="*60)
    print("STEP 4: EXPLAINABILITY AGENT - Decision Explanations & Jargon Translation")
    print("="*60)

    # Explain portfolio decision
    print("\nExplaining portfolio decision...")
    explanation_request = {
        "action": {
            "type": "portfolio_allocation",
            "decision": "Balanced portfolio with 25% SPY, 20% AAPL, 20% MSFT, 15% BTC-USD, 20% TLT",
            "allocations": {
                "SPY": 0.25,
                "AAPL": 0.20,
                "MSFT": 0.20,
                "BTC-USD": 0.15,
                "TLT": 0.20
            }
        },
        "context": {
            "user_profile": {
                "age": 40,
                "risk_tolerance": "moderate",
                "investment_horizon": "10 years",
                "goal": "retirement"
            },
            "market_conditions": {
                "volatility": "moderate",
                "economic_growth": "stable"
            }
        }
    }

    explanation_result = await make_request("POST", "/agents/explainer/explain-decision", explanation_request, delay=1.0)

    if "error" not in explanation_result:
        print("Decision explained successfully")
        if "explanation" in explanation_result:
            exp = explanation_result["explanation"]
            print(f"   Summary: {exp.get('summary', '')[:150]}...")
            print(f"   Risk Level: {exp.get('risk_assessment', {}).get('level', 'Unknown')}")
            print(f"   Confidence Score: {exp.get('confidence_score', 0):.1%}")
    else:
        print("Decision explanation failed, continuing with demo...")

    # Translate financial jargon
    print("\nTranslating financial jargon...")
    jargon_terms = [
        "What is EFT?",
        "Explain Beta in simple terms for a beginner investor",
    ]

    for i, term_question in enumerate(jargon_terms):
        # The endpoint expects just a string body
        translation_result = await make_request("POST", "/agents/explainer/translate-jargon", term_question, delay=1.0)

        if "error" not in translation_result:
            term_name = term_question.split()[2] if len(term_question.split()) > 2 else f"Term {i+1}"
            translation_text = translation_result.get('translation', 'Translation failed')
            if isinstance(translation_text, str) and len(translation_text) > 100:
                print(f"   {term_name}: {translation_text[:100]}...")
            else:
                print(f"   {term_name}: {translation_text}")
        else:
            term_name = term_question.split()[2] if len(term_question.split()) > 2 else f"Term {i+1}"
            print(f"   {term_name}: Translation failed")

    return explanation_result, translation_result

async def main():
    """Main demonstration workflow"""
    print("NEURAL CAPITAL FINANCIAL AGENTS - END-TO-END DEMONSTRATION")
    print("="*70)
    print("This demo shows how all 4 agents work together for a complete user journey.")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("="*70)

    # First, set up premium tier for demo user to avoid rate limits (commented out - endpoint doesn't exist)
    # print("Setting up demo user with premium tier...")
    # user_id = SAMPLE_USER["id_user"]
    # 
    # # Setup user tier via direct API call
    # tier_setup = await make_request("POST", "/setup-user-tier", {
    #     "user_id": user_id,
    #     "tier": "premium"
    # }, delay=0)
    # 
    # if "error" not in tier_setup:
    #     print(f"Demo user '{user_id}' configured with premium tier")
    # else:
    #     print("Could not configure premium tier, using default limits")

    print("Rate limiting disabled for testing - proceeding with demo")

    try:
        # # Step 1: Data Collection & Validation [AGENT 1 - DATA AGENT]
        # # ============================================================
        # print("\nStarting Step 1: Data Collection")
        # market_data, macro_data, validation_result = await step_1_data_collection()
        
        # # Save Step 1 results to temp_storage
        # print("\nSaving Step 1 results to temp_storage/...")
        # json_read_write("temp_storage/market_data.json", "w", market_data)
        # json_read_write("temp_storage/macro_data.json", "w", macro_data)
        # json_read_write("temp_storage/validation_result.json", "w", validation_result)
        # print("Data saved successfully!")
        # print("   temp_storage/market_data.json")
        # print("   temp_storage/macro_data.json")
        # print("   temp_storage/validation_result.json")

        
        # Step 2: Portfolio Optimization (load data from temp_storage) [AGENT 2 - PORTFOLIO AGENT]
        # ============================================================
        print("\nLoading data from temp_storage/ for Step 2...")
        market_data = json_read_write("temp_storage/market_data.json", "r")
        macro_data = json_read_write("temp_storage/macro_data.json", "r")
        validation_result = json_read_write("temp_storage/validation_result.json", "r")
        print("Data loaded successfully!")
        print(f"   {market_data.get('total_assets', 0)} assets loaded")
        print(f"   {len(macro_data.get('indicators', {}))} macro indicators loaded")

        # Agent 2: Portfolio Optimization
        portfolio_result, rebalance_result = await step_2_portfolio_optimization(market_data, macro_data)

        # Step 3: Goal Parsing [AGENT 3 - PLANNER AGENT]
        # ============================================================
        goal_result, strategy_result = await step_3_goal_parsing()

        # Step 4: Explanations & Jargon [AGENT 4 - EXPLAINABILITY AGENT]
        # ============================================================
        explanation_result, translation_result = await step_4_explanations(portfolio_result, goal_result)

        # Summary
        print("\n" + "="*70)
        print("DEMONSTRATION COMPLETED!")
        print("="*70)
        print("Summary of agent interactions:")
        print(f"   Data Agent: Collected market data and validated {len(validation_result.get('signals', []))} signals")
        # Fix: Handle the nested portfolio structure in summary
        portfolio_data = portfolio_result.get('portfolio', {}).get('portfolio', {})
        allocations = portfolio_data.get('allocations', {})
        print(f"   Portfolio Agent: Built portfolio with {len(allocations)} assets")
        print("    Data Flow: Step 1 → json_read_write() → temp_storage/ → json_read_write() → Step 2")
        print("    Persistence: Data saved/loaded using json_read_write() utility function")
        # print(f"   Planner Agent: Parsed goal '{goal_result.get('parsed_goal', {}).get('goal_type', 'unknown')}'")
        # print(f"   Explainability Agent: Provided {len(explanation_result.get('explanation', {}))} explanation components")
        
        # print("\nAll agents successfully demonstrated their capabilities!")
        # print("Check the server logs for detailed agent interactions.")

    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        print("Make sure the FastAPI server is running and all dependencies are installed.")

if __name__ == "__main__":
    asyncio.run(main())