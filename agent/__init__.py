"""
Neural Capital Agent System

This package contains all four agents for the Neural Capital financial advisory system
organized in a modular structure:

Core Agents (agent.core):
1. DataAgent - Real-time financial data aggregation and macro-economic indicator collection
2. PortfolioAgent - Algorithmic portfolio optimization and dynamic rebalancing
3. PlannerAgent - Natural language goal interpretation and lifecycle-based investment planning
4. ExplainabilityAgent - Financial jargon translation and decision rationale generation


CrewAI Integration (agent.crew):
- Multi-agent collaboration and orchestration
- Task management and workflow coordination

External Clients (agent.clients):
- MistralClient - LLM integration for natural language processing

Shared Utilities (agent.shared):
- Models - Pydantic data models
- Config - Configuration management
- Utils - Utility functions
- Shared - Common helper functions

Tools (agent.tools):
- MCP - Model Context Protocol tools
- Tools - Agent tools and integrations
"""

# Import core agents
from .core import DataAgent, PortfolioAgent, PlannerAgent, ExplainabilityAgent


# Import external clients
from .clients import MistralLLMClient, mistral_client

# Import shared components
from .shared import (
    # Configuration
    config, ConfigManager,
    # Models
    MarketData, MacroData, Portfolio, RiskLevel,
    GoalParameters, GoalType, UserProfile, InvestmentStrategy,
    Action, Context, ExplanationResponse,
)

__all__ = [
    # Agents
    "DataAgent",
    "PortfolioAgent",
    "PlannerAgent",
    "ExplainabilityAgent",


    # External Clients
    "MistralLLMClient",
    "mistral_client",

    # Configuration
    "config",
    "ConfigManager",

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
]

__version__ = "1.0.0"