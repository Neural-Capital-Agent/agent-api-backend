"""
CrewAI Integration

This module contains CrewAI integration for multi-agent collaboration:
- agents: CrewAI agent definitions
- tasks: CrewAI task definitions
- simple_crew: Simple crew implementation
"""

from .agents import *
from .tasks import *
from .simple_crew import *

__all__ = [
    # Export all from submodules
]