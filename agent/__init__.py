"""
Neural Capital Agent System

This package contains all four agents for the Neural Capital financial advisory system:
1. DataAgent - Real-time financial data aggregation and macro-economic indicator collection
2. PortfolioAgent - Algorithmic portfolio optimization and dynamic rebalancing
3. PlannerAgent - Natural language goal interpretation and lifecycle-based investment planning
4. ExplainabilityAgent - Financial jargon translation and decision rationale generation

Coral Protocol Integration:
- 3 out of 4 agents use Coral Protocol for inter-agent communication
- DataAgent operates independently as a data source
- Secure agent-to-agent messaging with CORAL token micropayments
- Blockchain verification for decision transparency
"""

from .agents import DataAgent, PortfolioAgent, PlannerAgent, ExplainabilityAgent
from .coral_client import CoralClient
from .models import (
    # Core models
    MarketData, MacroData, Portfolio, RiskLevel,
    GoalParameters, GoalType, UserProfile, InvestmentStrategy,
    Action, Context, ExplanationResponse,

    # Coral Protocol models
    CoralMessage, CoralResponse, AgentRegistration
)

__all__ = [
    # Agents
    "DataAgent",
    "PortfolioAgent",
    "PlannerAgent",
    "ExplainabilityAgent",

    # Coral Protocol
    "CoralClient",

    # Models
    "MarketData",
    "MacroData",
    "Portfolio",
    "RiskLevel",
    "GoalParameters",
    "GoalType",
    "UserProfile",
    "InvestmentStrategy",
    "Action",
    "Context",
    "ExplanationResponse",
    "CoralMessage",
    "CoralResponse",
    "AgentRegistration"
]

__version__ = "1.0.0"