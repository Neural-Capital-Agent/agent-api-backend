"""
Core Financial Agents

This module contains the four main financial agents:
- DataAgent: Real-time financial data aggregation and macro-economic indicators
- PortfolioAgent: Algorithmic portfolio optimization and dynamic rebalancing
- PlannerAgent: Natural language goal interpretation and lifecycle planning
- ExplainabilityAgent: Financial jargon translation and decision explanations
"""

from .data_agent import DataAgent
from .portfolio_agent import PortfolioAgent
from .planner_agent import PlannerAgent
from .explainability_agent import ExplainabilityAgent

__all__ = [
    "DataAgent",
    "PortfolioAgent",
    "PlannerAgent",
    "ExplainabilityAgent"
]