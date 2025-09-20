"""
Agent API routes for serving agent results and managing agent operations
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, Dict, Any
import logging
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Agents"], prefix="/agents")


@router.get("/results")
async def get_agent_results(
    agent_id: Optional[str] = Query(None, description="Specific agent ID to get results for")
):
    """
    Get the latest agent results from temp storage.

    Args:
        agent_id: Optional specific agent ID to filter results

    Returns:
        Dictionary containing agent results
    """
    try:
        # Path to the agent results file
        results_file = "temp_storage/agent-raw-answer-1.txt"

        if not os.path.exists(results_file):
            raise HTTPException(
                status_code=404,
                detail={"error": "agent_results_not_found", "message": "Agent results file not found"}
            )

        # Read the raw agent results file
        with open(results_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Parse the agent results
        parsed_results = parse_agent_results(raw_content)

        # Filter by specific agent if requested
        if agent_id:
            agent_key = f"{agent_id.lower()}Agent"
            if agent_key in parsed_results:
                return {
                    "status": "success",
                    "agent_id": agent_id,
                    "data": parsed_results[agent_key],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise HTTPException(
                    status_code=404,
                    detail={"error": "agent_not_found", "message": f"Agent {agent_id} not found in results"}
                )

        return {
            "status": "success",
            "data": parsed_results,
            "timestamp": datetime.now().isoformat()
        }

    except FileNotFoundError:
        logger.error("Agent results file not found")
        raise HTTPException(
            status_code=404,
            detail={"error": "file_not_found", "message": "Agent results file not found"}
        )
    except Exception as e:
        logger.error(f"Error getting agent results: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "agent_results_failed", "message": str(e)}
        )


@router.get("/results/{agent_id}")
async def get_specific_agent_result(
    agent_id: str = Path(..., description="Agent ID (data, portfolio, planner, explainability)")
):
    """
    Get results for a specific agent.

    Args:
        agent_id: The agent ID to get results for

    Returns:
        Dictionary containing specific agent results
    """
    return await get_agent_results(agent_id=agent_id)


@router.get("/results/raw")
async def get_raw_agent_results():
    """
    Get the raw agent results file content.

    Returns:
        Raw text content of the agent results file
    """
    try:
        results_file = "temp_storage/agent-raw-answer-1.txt"

        if not os.path.exists(results_file):
            raise HTTPException(
                status_code=404,
                detail={"error": "file_not_found", "message": "Agent results file not found"}
            )

        with open(results_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "status": "success",
            "raw_content": content,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting raw agent results: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "raw_results_failed", "message": str(e)}
        )


@router.post("/analyze")
async def run_agent_analysis(analysis_params: Dict[str, Any]):
    """
    Trigger a new agent analysis with given parameters.

    Args:
        analysis_params: Parameters for the analysis

    Returns:
        Status of the analysis trigger
    """
    try:
        # This would trigger your agent pipeline
        # For now, return a success response
        logger.info(f"Agent analysis triggered with params: {analysis_params}")

        return {
            "status": "success",
            "message": "Agent analysis triggered successfully",
            "analysis_id": f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "params": analysis_params,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error triggering agent analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "analysis_trigger_failed", "message": str(e)}
        )


def parse_agent_results(raw_content: str) -> Dict[str, Any]:
    """
    Parse the raw agent results file into structured data.

    Args:
        raw_content: Raw text content from the agent results file

    Returns:
        Structured dictionary of agent results
    """
    results = {
        "dataAgent": None,
        "portfolioAgent": None,
        "plannerAgent": None,
        "explainabilityAgent": None,
        "timestamp": datetime.now().isoformat()
    }

    try:
        # Split by agent sections
        sections = raw_content.split('============================================================')

        for section in sections:
            if 'Agent 1' in section:
                results["dataAgent"] = parse_data_agent(section)
            elif 'Agent 2' in section:
                results["portfolioAgent"] = parse_portfolio_agent(section)
            elif 'Agent 3' in section:
                results["plannerAgent"] = parse_planner_agent(section)
            elif 'Agent 4' in section:
                results["explainabilityAgent"] = parse_explainability_agent(section)

    except Exception as e:
        logger.error(f"Error parsing agent results: {e}")

    return results


def parse_data_agent(section: str) -> Dict[str, Any]:
    """Parse Data Agent (Agent 1) section."""
    market_data = []
    macro_data = {}

    try:
        # Extract market data from JSON responses
        import re

        # Find all Response: {...} patterns
        response_pattern = r'Response: (\{.*?\n\})'
        responses = re.findall(response_pattern, section, re.DOTALL)

        for response_text in responses:
            try:
                response_json = json.loads(response_text)

                # Check if it's market data (has ticker and data fields)
                if 'ticker' in response_json and 'data' in response_json and not 'indicator' in response_json:
                    data = response_json['data']
                    market_data.append({
                        "symbol": data.get("symbol", ""),
                        "price": data.get("price", 0),
                        "previousClose": data.get("previous_close", 0),
                        "change": data.get("change", 0),
                        "changePercent": data.get("change_percent", 0),
                        "timestamp": data.get("timestamp", "")
                    })

                # Check if it's macro data (has indicator field)
                elif 'indicator' in response_json and 'data' in response_json:
                    indicator = response_json['indicator']
                    data_points = response_json['data']

                    if data_points and len(data_points) > 0:
                        latest = data_points[0]
                        previous = data_points[1] if len(data_points) > 1 else latest

                        # Calculate trend
                        trend = 'stable'
                        if latest['value'] > previous['value'] * 1.01:
                            trend = 'up'
                        elif latest['value'] < previous['value'] * 0.99:
                            trend = 'down'

                        macro_data[indicator] = {
                            "value": latest.get("value", 0),
                            "date": latest.get("date", ""),
                            "trend": trend
                        }

            except (json.JSONDecodeError, KeyError) as e:
                continue

    except Exception as e:
        logger.warning(f"Error parsing data agent section: {e}")

    return {"marketData": market_data, "macroData": macro_data}


def parse_portfolio_agent(section: str) -> Dict[str, Any]:
    """Parse Portfolio Agent (Agent 2) section."""
    portfolio = {}
    rebalance = {"actions": []}

    try:
        import re

        # Extract portfolio build response
        portfolio_pattern = r'Portfolio build response: (\{.*?\n\})'
        portfolio_matches = re.findall(portfolio_pattern, section, re.DOTALL)

        for match in portfolio_matches:
            try:
                data = json.loads(match)
                if 'portfolio' in data and 'portfolio' in data['portfolio']:
                    p = data['portfolio']['portfolio']
                    portfolio = {
                        "id": p.get("id", ""),
                        "allocations": p.get("allocations", {}),
                        "expectedReturn": p.get("expected_return", 0),
                        "expectedRisk": p.get("expected_risk", 0),
                        "sharpeRatio": p.get("sharpe_ratio", 0),
                        "riskLevel": p.get("risk_level", 0)
                    }
                break
            except (json.JSONDecodeError, KeyError):
                continue

        # Extract rebalance response
        rebalance_pattern = r'Rebalance response: (\{.*?\n\})'
        rebalance_matches = re.findall(rebalance_pattern, section, re.DOTALL)

        for match in rebalance_matches:
            try:
                data = json.loads(match)
                if 'rebalance_action' in data and 'actions' in data['rebalance_action']:
                    actions = data['rebalance_action']['actions']
                    rebalance["actions"] = [
                        {
                            "ticker": action.get("ticker", ""),
                            "action": action.get("action", ""),
                            "amount": action.get("amount", 0),
                            "currentWeight": action.get("current_weight", 0),
                            "targetWeight": action.get("target_weight", 0),
                            "reason": f"{'Increase' if action.get('action') == 'buy' else 'Reduce'} position"
                        }
                        for action in actions
                    ]
                break
            except (json.JSONDecodeError, KeyError):
                continue

    except Exception as e:
        logger.warning(f"Error parsing portfolio agent section: {e}")

    return {"portfolio": portfolio, "rebalance": rebalance}


def parse_planner_agent(section: str) -> Dict[str, Any]:
    """Parse Planner Agent (Agent 3) section."""
    goal = {}
    strategy = {}

    try:
        import re

        # Extract goal parsing response
        goal_pattern = r'Goal parsing response: (\{.*?\n\})'
        goal_matches = re.findall(goal_pattern, section, re.DOTALL)

        for match in goal_matches:
            try:
                data = json.loads(match)
                if 'parsed_goal' in data and 'parsed_goal' in data['parsed_goal']:
                    g = data['parsed_goal']['parsed_goal']
                    goal = {
                        "goalType": g.get("goal_type", ""),
                        "targetAmount": g.get("target_amount", 0),
                        "timeHorizon": g.get("time_horizon_years", 0),
                        "currentAge": g.get("current_age", 0),
                        "riskLevel": g.get("risk_level", 0),
                        "monthlyInvestment": g.get("monthly_investment", 0)
                    }
                break
            except (json.JSONDecodeError, KeyError):
                continue

        # Extract strategy response
        strategy_pattern = r'Strategy response: (\{.*?\n\})'
        strategy_matches = re.findall(strategy_pattern, section, re.DOTALL)

        for match in strategy_matches:
            try:
                data = json.loads(match)
                if 'strategy' in data and 'strategy' in data['strategy']:
                    s = data['strategy']['strategy']
                    strategy = {
                        "allocationType": s.get("allocation_type", ""),
                        "expectedReturn": s.get("expected_return", 0),
                        "confidenceLevel": s.get("confidence_level", ""),
                        "allocation": s.get("recommended_allocation", {}),
                        "riskLevel": s.get("risk_level", "")
                    }

                # Update goal with monthly investment from strategy response
                if 'goal' in data and data['goal'].get('monthly_investment'):
                    goal["monthlyInvestment"] = data['goal']['monthly_investment']
                break
            except (json.JSONDecodeError, KeyError):
                continue

    except Exception as e:
        logger.warning(f"Error parsing planner agent section: {e}")

    return {"goal": goal, "strategy": strategy}


def parse_explainability_agent(section: str) -> Dict[str, Any]:
    """Parse Explainability Agent (Agent 4) section."""
    explanation = {}

    try:
        import re

        # Extract explanation response
        explanation_pattern = r'Explanation response: (\{.*?\n\})'
        explanation_matches = re.findall(explanation_pattern, section, re.DOTALL)

        for match in explanation_matches:
            try:
                data = json.loads(match)
                if 'explanation' in data:
                    exp = data['explanation']
                    explanation = {
                        "summary": exp.get("summary", ""),
                        "riskLevel": exp.get("risk_assessment", {}).get("level", "unknown"),
                        "confidence": exp.get("confidence_score", 0),
                        "timestamp": data.get("timestamp", "")
                    }
                break
            except (json.JSONDecodeError, KeyError):
                continue

    except Exception as e:
        logger.warning(f"Error parsing explainability agent section: {e}")

    return explanation