# Agent Database Usage Documentation

## Agent 1 - Data Agent

  File: agent/core/data_agent.py

 ### INPUT (Reads from):
  - External APIs only (Yahoo Finance, FRED, Polygon)
  - dashboard_market_data (for cached data)

 ### OUTPUT (Writes to):
  - dashboard_market_data - stores market data, stock prices, technical indicators
  - dashboard_macro_data - stores macroeconomic data from FRED API
  - user_dashboard_settings - user dashboard preferences

## Agent 2 - Portfolio Agent

  File: agent/core/portfolio_agent.py

  ### INPUT (Reads from):
  - dashboard_market_data - current market prices and financial metrics
  - portfolios - existing user portfolio data
  - investment_plans - user investment strategies
  - analysis_sessions - previous analysis sessions

  ### OUTPUT (Writes to):
  - portfolio_analysis - portfolio performance metrics, allocations, expected returns
  - stress_tests - stress test scenarios and portfolio loss calculations
  - rebalancing_triggers - sophisticated rebalancing conditions and thresholds
  - analysis_sessions - session metadata

## Agent 3 - Planner Agent

  File: agent/core/planner_agent.py

  ### INPUT (Reads from):
  - user_profiles - user financial information and preferences
  - dashboard_market_data - market conditions
  - investment_plans - existing investment plans
  - analysis_sessions - previous planning sessions

  ### OUTPUT (Writes to):
  - planner_analysis - financial planning results, goals, milestones
  - monte_carlo_results - Monte Carlo simulation data and scenarios
  - investment_plans - personalized investment strategies
  - financial_goals - user financial objectives
  - analysis_sessions - session metadata

  ## Agent 4 - Explainability Agent

  File: agent/core/explainability_agent.py

  ### INPUT (Reads from):
  - portfolio_analysis - AI recommendations to explain
  - planner_analysis - investment strategies for context
  - dashboard_market_data - market data for explanations
  - analysis_sessions - previous explanation sessions

  ### OUTPUT (Writes to):
  - explainability_analysis - natural language explanations, risk frameworks
  - ai_insights - AI-generated insights and reasoning
  - recommendation_explanations - detailed rationale for recommendations
  - analysis_sessions - session metadata

  ## Shared Database Services:

  Primary Service: agent/services/agent_data_service.py
  - Used by Agents 2, 3, and 4
  - Handles analysis_sessions, portfolio_analysis, planner_analysis, explainability_analysis, stress_tests, monte_carlo_results,
  rebalancing_triggers

  Dashboard Service: agent/core/dashboard_data_service.py
  - Used by Agent 1
  - Handles dashboard_market_data, user_dashboard_settings

  The agents work together through the analysis_sessions table which links all their analyses and enables the comprehensive workflow you see
   in the AI Investment Advisor component.