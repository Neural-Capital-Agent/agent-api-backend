"""
End-to-End Agent Workflow Demonstration - Raw Input/Output Version
This script demonstrates the raw input and output for each of the 4 financial agents:
1. DataAgent: Collects and validates market data
2. PortfolioAgent: Performs algorithmic portfolio optimization
3. PlannerAgent: Parses natural language financial goals
4. ExplainabilityAgent: Provides explanations and jargon translation

This version focuses on printing the input and raw output for each agent.
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, date
from typing import Dict, Any
import uuid
import time

# Global variable to store all outputs for saving to file
ALL_OUTPUTS = []

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def save_output_to_file(content: str, filename: str = "agent_raw_outputs.txt"):
    """Save content to a text file with timestamp in temp_storage folder"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"temp_storage/{timestamp}_{filename}"

    try:
        # Ensure temp_storage directory exists
        os.makedirs("temp_storage", exist_ok=True)

        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nOutputs saved to: {output_filename}")
    except Exception as e:
        print(f"\nError saving outputs to file: {e}")

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
        raise json.JSONDecodeError(
            f"Invalid JSON in file {file_location}: {e.msg}",
            e.doc,
            e.pos
        )
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
    output_buffer = []
    output_buffer.append("\n" + "="*60)
    output_buffer.append("Agent 1")
    output_buffer.append("="*60)
    output_buffer.append("Input:")

    print("\n" + "="*60)
    print("Agent 1")
    print("="*60)
    print("Input:")

    # Get market data for key assets
    tickers = ["AAPL", "MSFT", "SPY", "BTC-USD"]
    output_buffer.append(f"Market data tickers: {tickers}")
    print(f"Market data tickers: {tickers}")

    market_data_results = {}
    all_raw_outputs = []

    for i, ticker in enumerate(tickers):
        print(f"\nFetching data for {ticker}...")
        ticker_data = await make_request("GET", f"/agents/data/market/{ticker}", delay=0.5)
        all_raw_outputs.append({
            "endpoint": f"/agents/data/market/{ticker}",
            "method": "GET",
            "raw_output": ticker_data
        })

        if "error" not in ticker_data and "data" in ticker_data:
            market_data_results[ticker] = ticker_data["data"]

    # Get macro indicators
    indicators = ["GDP", "INFLATION", "UNEMPLOYMENT", "INTEREST_RATES"]
    output_buffer.append(f"\nMacro indicators: {indicators}")
    print(f"\nMacro indicators: {indicators}")

    macro_results = {}

    for i, indicator in enumerate(indicators):
        print(f"\nFetching macro data for {indicator}...")
        macro_data = await make_request("GET", f"/agents/data/macro/{indicator}", delay=0.5)
        all_raw_outputs.append({
            "endpoint": f"/agents/data/macro/{indicator}",
            "method": "GET",
            "raw_output": macro_data
        })

        if "error" not in macro_data and "data" in macro_data:
            macro_results[indicator] = macro_data["data"]

    # Simulate market data structure for compatibility
    market_data = {
        "data": market_data_results,
        "total_assets": len(market_data_results)
    }

    # Simulate macro data structure for compatibility
    macro_data = {
        "indicators": macro_results
    }

    output_buffer.append("\nRaw Output:")
    print("\nRaw Output:")
    for output in all_raw_outputs:
        endpoint_info = f"\nEndpoint: {output['endpoint']}"
        method_info = f"Method: {output['method']}"
        response_info = f"Response: {json.dumps(output['raw_output'], indent=2)}"

        output_buffer.append(endpoint_info)
        output_buffer.append(method_info)
        output_buffer.append(response_info)

        print(endpoint_info)
        print(method_info)
        print(response_info)

    # Create a simple validation result for demo compatibility
    validation_result = {
        "signals": [],
        "validation_method": "rule_based_only",
        "note": "DataAgent now focuses purely on data retrieval - LLM validation commented out"
    }

    # Store Agent 1 output in global variable
    ALL_OUTPUTS.append("\n".join(output_buffer))

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

    output_buffer = []
    output_buffer.append("\n" + "="*60)
    output_buffer.append("Agent 2")
    output_buffer.append("="*60)
    output_buffer.append("Input:")

    print("\n" + "="*60)
    print("Agent 2")
    print("="*60)
    print("Input:")

    # Build initial portfolio
    portfolio_request = {
        "risk_level": 3,  # Balanced
        "investment_amount": 100000,
        "time_horizon_years": 10,
        "goal": "retirement_savings",
        "constraints": {
            "max_single_asset": 0.20,
            "min_assets": 5,
            "excluded_assets": []
        }
    }

    portfolio_request_str = f"Portfolio build request: {json.dumps(portfolio_request, indent=2)}"
    output_buffer.append(portfolio_request_str)
    print(portfolio_request_str)

    portfolio_result = await make_request("POST", "/agents/portfolio/build", portfolio_request, delay=1.0)

    output_buffer.append("\nRaw Output:")
    portfolio_response_str = f"Portfolio build response: {json.dumps(portfolio_result, indent=2)}"
    output_buffer.append(portfolio_response_str)

    print("\nRaw Output:")
    print(portfolio_response_str)

    # Simulate rebalancing
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

    rebalance_request_str = f"\nRebalance request: {json.dumps(rebalance_request, indent=2)}"
    output_buffer.append(rebalance_request_str)
    print(rebalance_request_str)

    rebalance_result = await make_request("POST", "/agents/portfolio/rebalance", rebalance_request, delay=1.0)

    rebalance_response_str = f"\nRebalance response: {json.dumps(rebalance_result, indent=2)}"
    output_buffer.append(rebalance_response_str)
    print(rebalance_response_str)

    # Store Agent 2 output in global variable
    ALL_OUTPUTS.append("\n".join(output_buffer))

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

    output_buffer = []
    output_buffer.append("\n" + "="*60)
    output_buffer.append("Agent 3")
    output_buffer.append("="*60)
    output_buffer.append("Input:")

    print("\n" + "="*60)
    print("Agent 3")
    print("="*60)
    print("Input:")

    # Parse a financial goal
    goal_text = "I want to save $500,000 for my child's college education in 15 years. I'm currently 40 years old and can invest $1,200 per month."

    goal_text_str = f"Goal text: {goal_text}"
    output_buffer.append(goal_text_str)
    print(goal_text_str)

    # The endpoint expects just a string body, not a JSON object
    goal_result = await make_request("POST", "/agents/planner/parse-goal", goal_text, delay=1.0)

    output_buffer.append("\nRaw Output:")
    goal_response_str = f"Goal parsing response: {json.dumps(goal_result, indent=2)}"
    output_buffer.append(goal_response_str)

    print("\nRaw Output:")
    print(goal_response_str)

    # Create investment strategy
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

    strategy_request_str = f"\nStrategy request: {json.dumps(strategy_request, indent=2)}"
    output_buffer.append(strategy_request_str)
    print(strategy_request_str)

    strategy_result = await make_request("POST", "/agents/planner/create-strategy", strategy_request, delay=1.0)

    strategy_response_str = f"\nStrategy response: {json.dumps(strategy_result, indent=2)}"
    output_buffer.append(strategy_response_str)
    print(strategy_response_str)

    # Store Agent 3 output in global variable
    ALL_OUTPUTS.append("\n".join(output_buffer))

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
    output_buffer = []
    output_buffer.append("\n" + "="*60)
    output_buffer.append("Agent 4")
    output_buffer.append("="*60)
    output_buffer.append("Input:")

    print("\n" + "="*60)
    print("Agent 4")
    print("="*60)
    print("Input:")

    # Explain portfolio decision
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

    explanation_request_str = f"Explanation request: {json.dumps(explanation_request, indent=2)}"
    output_buffer.append(explanation_request_str)
    print(explanation_request_str)

    explanation_result = await make_request("POST", "/agents/explainer/explain-decision", explanation_request, delay=1.0)

    output_buffer.append("\nRaw Output:")
    explanation_response_str = f"Explanation response: {json.dumps(explanation_result, indent=2)}"
    output_buffer.append(explanation_response_str)

    print("\nRaw Output:")
    print(explanation_response_str)

    # Translate financial jargon
    jargon_terms = [
        "What is EFT?",
        "Explain Beta in simple terms for a beginner investor",
    ]

    jargon_request_str = f"\nJargon translation requests: {jargon_terms}"
    output_buffer.append(jargon_request_str)
    print(jargon_request_str)

    translation_outputs = []
    for i, term_question in enumerate(jargon_terms):
        # The endpoint expects just a string body
        translation_result = await make_request("POST", "/agents/explainer/translate-jargon", term_question, delay=1.0)
        translation_outputs.append({
            "question": term_question,
            "response": translation_result
        })

    output_buffer.append("\nJargon translation responses:")
    print("\nJargon translation responses:")
    for output in translation_outputs:
        question_str = f"\nQuestion: {output['question']}"
        response_str = f"Response: {json.dumps(output['response'], indent=2)}"

        output_buffer.append(question_str)
        output_buffer.append(response_str)

        print(question_str)
        print(response_str)

    # Store Agent 4 output in global variable
    ALL_OUTPUTS.append("\n".join(output_buffer))

    return explanation_result, translation_outputs

async def main():
    """Main demonstration workflow"""
    print("NEURAL CAPITAL FINANCIAL AGENTS - RAW INPUT/OUTPUT DEMONSTRATION")
    print("="*70)
    print("This demo shows the raw input and output for each of the 4 agents.")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("="*70)

    try:
        # Step 1: Data Collection & Validation [AGENT 1 - DATA AGENT]
        market_data, macro_data, validation_result = await step_1_data_collection()

        # # Save Step 1 results to temp_storage
        # json_read_write("temp_storage/market_data.json", "w", market_data)
        # json_read_write("temp_storage/macro_data.json", "w", macro_data)
        # json_read_write("temp_storage/validation_result.json", "w", validation_result)

        # # Step 2: Portfolio Optimization (load data from temp_storage) [AGENT 2 - PORTFOLIO AGENT]
        # market_data = json_read_write("temp_storage/market_data.json", "r")
        # macro_data = json_read_write("temp_storage/macro_data.json", "r")
        # validation_result = json_read_write("temp_storage/validation_result.json", "r")


        portfolio_result, rebalance_result = await step_2_portfolio_optimization(market_data, macro_data)   # Agent 2: Portfolio Optimization

        # Step 3: Goal Parsing [AGENT 3 - PLANNER AGENT]
        goal_result, strategy_result = await step_3_goal_parsing()

        # Step 4: Explanations & Jargon [AGENT 4 - EXPLAINABILITY AGENT]
        explanation_result, translation_result = await step_4_explanations(portfolio_result, goal_result)

        print("\n" + "="*70)
        print("RAW INPUT/OUTPUT DEMONSTRATION COMPLETED!")
        print("="*70)

        # Save all outputs to a text file
        all_outputs_text = "\n\n".join(ALL_OUTPUTS)
        save_output_to_file(all_outputs_text)

    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        print("Make sure the FastAPI server is running and all dependencies are installed.")

if __name__ == "__main__":
    asyncio.run(main())