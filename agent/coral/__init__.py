"""
Coral Protocol Integration

This module contains all Coral Protocol related functionality:
- CoralClient: Client for interacting with Coral Protocol infrastructure
- CoralRegistry: Service for registering and managing agents
- CoralServer: Mock Coral Protocol server for local development
"""

from .client import CoralClient
from .registry import CoralRegistry, coral_registry
from .server import CoralServer, coral_server

__all__ = [
    "CoralClient",
    "CoralRegistry",
    "coral_registry",
    "CoralServer",
    "coral_server"
]