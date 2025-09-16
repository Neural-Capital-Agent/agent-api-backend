"""
Shared utilities and common patterns to eliminate code duplication across agents.
This module contains reusable components used by multiple agents.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable, Union, List
from datetime import datetime
from functools import wraps
from .config import config

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all agents to eliminate initialization duplication.
    Provides common setup and utility methods.
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555", agent_id: str = None):
        """Initialize base agent with common setup"""
        from .coral_client import CoralClient

        if agent_id is None:
            agent_id = self.__class__.__name__.lower().replace('agent', '_agent')

        self.coral_client = CoralClient(coral_server_url, agent_id=agent_id)
        self.agent_id = agent_id

        # Common configuration access
        self.config = config

        logger.info(f"Initialized {self.__class__.__name__} with agent_id: {agent_id}")

    async def health_check(self) -> Dict[str, Any]:
        """Base health check implementation"""
        return {
            "agent_id": self.agent_id,
            "status": "healthy",
            "timestamp": get_current_timestamp()
        }


class TimestampUtils:
    """Utility class for timestamp operations"""

    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()

    @staticmethod
    def add_timestamp(data: Dict[str, Any], key: str = "timestamp") -> Dict[str, Any]:
        """Add current timestamp to a dictionary"""
        data[key] = datetime.now().isoformat()
        return data

    @staticmethod
    def create_timestamped_response(**kwargs) -> Dict[str, Any]:
        """Create a response dictionary with timestamp"""
        response = dict(kwargs)
        response["timestamp"] = datetime.now().isoformat()
        return response


class ErrorHandler:
    """Centralized error handling utilities"""

    @staticmethod
    def handle_with_fallback(
        operation_name: str,
        agent_type: str,
        fallback_type: str,
        error: Exception,
        **fallback_kwargs
    ) -> Dict[str, Any]:
        """Handle errors with configuration-based fallbacks"""
        logger.error(f"Error in {operation_name}: {error}")

        if config.should_use_fallbacks():
            if config.base_config.log_fallback_usage:
                logger.warning(f"Using fallback for {operation_name} in {agent_type}")

            fallback = config.get_fallback(agent_type, fallback_type, **fallback_kwargs)
            if isinstance(fallback, dict):
                fallback["error"] = str(error)
                fallback["timestamp"] = datetime.now().isoformat()
                return fallback
            else:
                return {
                    "result": fallback,
                    "error": str(error),
                    "timestamp": datetime.now().isoformat()
                }
        else:
            # Re-raise in production when fallbacks are disabled
            raise error

    @staticmethod
    def safe_execute(
        func: Callable,
        operation_name: str,
        agent_type: str = None,
        fallback_type: str = None,
        **fallback_kwargs
    ) -> Any:
        """Safely execute a function with error handling"""
        try:
            return func()
        except Exception as e:
            if agent_type and fallback_type:
                return ErrorHandler.handle_with_fallback(
                    operation_name, agent_type, fallback_type, e, **fallback_kwargs
                )
            else:
                logger.error(f"Error in {operation_name}: {e}")
                raise


class AsyncUtils:
    """Utilities for async operations and patterns"""

    @staticmethod
    async def safe_coral_invoke(
        coral_client,
        target_agent: str,
        method: str,
        params: Dict[str, Any],
        operation_name: str = None
    ) -> Optional[Dict[str, Any]]:
        """Safely invoke coral client with error handling"""
        try:
            return await coral_client.invoke_agent(target_agent, method, params)
        except Exception as e:
            operation = operation_name or f"{target_agent}.{method}"
            logger.warning(f"Coral invocation failed for {operation}: {e}")
            return None

    @staticmethod
    def async_error_handler(
        operation_name: str,
        agent_type: str = None,
        fallback_type: str = None,
        **fallback_kwargs
    ):
        """Decorator for async error handling with fallbacks"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if agent_type and fallback_type:
                        return ErrorHandler.handle_with_fallback(
                            operation_name, agent_type, fallback_type, e, **fallback_kwargs
                        )
                    else:
                        logger.error(f"Error in {operation_name}: {e}")
                        raise
            return wrapper
        return decorator


class DataUtils:
    """Utilities for data processing and validation"""

    @staticmethod
    def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Safely get value from dictionary with optional default"""
        return data.get(key, default) if data else default

    @staticmethod
    def ensure_dict(data: Any) -> Dict[str, Any]:
        """Ensure data is a dictionary, return empty dict if not"""
        return data if isinstance(data, dict) else {}

    @staticmethod
    def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple dictionaries"""
        result = {}
        for d in dicts:
            if isinstance(d, dict):
                result.update(d)
        return result

    @staticmethod
    def filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values from dictionary"""
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that all required fields are present and not None"""
        if not isinstance(data, dict):
            return False

        for field in required_fields:
            if field not in data or data[field] is None:
                logger.warning(f"Missing required field: {field}")
                return False

        return True


class ResponseUtils:
    """Utilities for creating consistent response formats"""

    @staticmethod
    def create_success_response(data: Any = None, **extra_fields) -> Dict[str, Any]:
        """Create a standardized success response"""
        response = {
            "success": True,
            "timestamp": datetime.now().isoformat()
        }

        if data is not None:
            response["data"] = data

        response.update(extra_fields)
        return response

    @staticmethod
    def create_error_response(
        error: Union[str, Exception],
        operation: str = None,
        **extra_fields
    ) -> Dict[str, Any]:
        """Create a standardized error response"""
        error_message = str(error)

        response = {
            "success": False,
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }

        if operation:
            response["operation"] = operation

        response.update(extra_fields)
        return response

    @staticmethod
    def create_health_response(
        status: str,
        checks: Dict[str, Any] = None,
        **extra_fields
    ) -> Dict[str, Any]:
        """Create a standardized health check response"""
        response = {
            "status": status,
            "timestamp": datetime.now().isoformat()
        }

        if checks:
            response["checks"] = checks

        response.update(extra_fields)
        return response


class ConfigUtils:
    """Utilities for configuration access"""

    @staticmethod
    def get_agent_config(agent_type: str) -> Any:
        """Get configuration for specific agent type"""
        return getattr(config, f"{agent_type}_agent", None)

    @staticmethod
    def should_use_fallback(operation: str = None) -> bool:
        """Check if fallbacks should be used with optional logging"""
        use_fallbacks = config.should_use_fallbacks()

        if use_fallbacks and operation and config.base_config.log_fallback_usage:
            logger.info(f"Fallback enabled for operation: {operation}")

        return use_fallbacks


# Convenience functions for common patterns
def get_current_timestamp() -> str:
    """Get current timestamp - convenience function"""
    return TimestampUtils.get_current_timestamp()


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safe dictionary access - convenience function"""
    return DataUtils.safe_get(data, key, default)


def create_timestamped_response(**kwargs) -> Dict[str, Any]:
    """Create timestamped response - convenience function"""
    return TimestampUtils.create_timestamped_response(**kwargs)


async def safe_coral_invoke(
    coral_client,
    target_agent: str,
    method: str,
    params: Dict[str, Any],
    operation_name: str = None
) -> Optional[Dict[str, Any]]:
    """Safe coral invocation - convenience function"""
    return await AsyncUtils.safe_coral_invoke(
        coral_client, target_agent, method, params, operation_name
    )


def log_fallback_usage(agent_type: str, operation: str):
    """Log fallback usage if configured"""
    if config.base_config.log_fallback_usage:
        logger.info(f"Using fallback in {agent_type} for {operation}")


# Common retry logic
class RetryUtils:
    """Utilities for retry logic"""

    @staticmethod
    async def retry_async(
        func: Callable,
        max_retries: int = 3,
        delay: float = 1.0,
        exponential_backoff: bool = True,
        operation_name: str = None
    ):
        """Retry async function with exponential backoff"""
        last_exception = None

        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = delay * (2 ** attempt) if exponential_backoff else delay
                    if operation_name:
                        logger.warning(f"Retry {attempt + 1}/{max_retries} for {operation_name} after {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    if operation_name:
                        logger.error(f"All {max_retries} retries failed for {operation_name}")

        raise last_exception