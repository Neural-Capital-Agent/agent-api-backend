"""
Shared Utilities and Models

This module contains shared utilities, models, and configurations:
- models: Pydantic models for data structures
- config: Configuration management
- utils: Utility functions
- shared: Shared helper functions
"""

from .models import *
from .config import config, ConfigManager
from .utils import *
from .shared import *

__all__ = [
    # Models
    "MarketData", "MacroData", "Portfolio", "RiskLevel",
    "GoalParameters", "GoalType", "UserProfile", "InvestmentStrategy",
    "Action", "Context", "ExplanationResponse",
    "CoralMessage", "CoralResponse", "AgentRegistration",

    # Config
    "config", "ConfigManager",

    # Utils and shared functions will be exported from their respective modules
]