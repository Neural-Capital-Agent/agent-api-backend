import logging
import logging.handlers
import os
from datetime import datetime, date
from pathlib import Path
import json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id

        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id

        if hasattr(record, 'endpoint'):
            log_entry["endpoint"] = record.endpoint

        if hasattr(record, 'method'):
            log_entry["method"] = record.method

        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code

        if hasattr(record, 'response_time'):
            log_entry["response_time"] = record.response_time

        return json.dumps(log_entry)


def setup_logging():
    """Configure comprehensive logging for the FastAPI application."""

    # Create logs directory
    logs_dir = Path("logs_store")
    logs_dir.mkdir(exist_ok=True)

    # Get current date for log file naming
    current_date = date.today().strftime("%Y-%m-%d")

    # Define log files with date stamps
    error_log = logs_dir / f"errors_{current_date}.log"
    api_log = logs_dir / f"api_{current_date}.log"
    general_log = logs_dir / f"application_{current_date}.log"

    # Clean up old log files (keep last 30 days)
    cleanup_old_logs(logs_dir, days_to_keep=30)

    # Clear any existing handlers
    logging.getLogger().handlers.clear()

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # JSON formatter for structured logging
    json_formatter = JSONFormatter()

    # Console formatter for development
    console_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Error log handler (JSON format)
    error_handler = logging.handlers.RotatingFileHandler(
        error_log, maxBytes=10*1024*1024, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    root_logger.addHandler(error_handler)

    # API log handler (JSON format)
    api_handler = logging.handlers.RotatingFileHandler(
        api_log, maxBytes=10*1024*1024, backupCount=5
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(json_formatter)

    # API logger for request/response logging
    api_logger = logging.getLogger("api")
    api_logger.setLevel(logging.INFO)
    api_logger.addHandler(api_handler)
    api_logger.propagate = False  # Prevent duplicate logs

    # General application log handler
    app_handler = logging.handlers.RotatingFileHandler(
        general_log, maxBytes=10*1024*1024, backupCount=5
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(json_formatter)
    root_logger.addHandler(app_handler)

    # Create loggers for different components
    loggers = {
        "fastapi": logging.getLogger("fastapi"),
        "uvicorn": logging.getLogger("uvicorn"),
        "agent": logging.getLogger("agent"),
        "api": logging.getLogger("api"),
        "database": logging.getLogger("database"),
        "auth": logging.getLogger("auth"),
        "crewai": logging.getLogger("crewai"),
        "mistral": logging.getLogger("mistral"),
    }

    # Set levels for specific loggers
    loggers["uvicorn"].setLevel(logging.WARNING)
    loggers["fastapi"].setLevel(logging.INFO)

    return loggers


def get_logger(name: str = None):
    """Get a logger instance with the specified name."""
    return logging.getLogger(name or __name__)


def log_error(logger, error, context=None, **kwargs):
    """Standardized error logging with context."""
    extra = kwargs.copy()
    if context:
        extra.update(context)

    logger.error(f"Error occurred: {str(error)}", extra=extra, exc_info=True)


def log_api_request(endpoint: str, method: str, user_id: str = None, request_id: str = None):
    """Log API request."""
    api_logger = logging.getLogger("api")
    api_logger.info(
        f"API Request: {method} {endpoint}",
        extra={
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "request_id": request_id,
            "event_type": "request"
        }
    )


def log_api_response(endpoint: str, method: str, status_code: int, response_time: float = None,
                    user_id: str = None, request_id: str = None):
    """Log API response."""
    api_logger = logging.getLogger("api")
    api_logger.info(
        f"API Response: {method} {endpoint} - {status_code}",
        extra={
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
            "user_id": user_id,
            "request_id": request_id,
            "event_type": "response"
        }
    )


def log_agent_activity(agent_name: str, action: str, details: dict = None, user_id: str = None):
    """Log agent activity."""
    agent_logger = logging.getLogger("agent")
    extra = {
        "agent_name": agent_name,
        "action": action,
        "user_id": user_id,
        "event_type": "agent_activity"
    }
    if details:
        extra.update(details)

    agent_logger.info(f"Agent {agent_name}: {action}", extra=extra)


def log_database_operation(operation: str, table: str = None, user_id: str = None, details: dict = None):
    """Log database operations."""
    db_logger = logging.getLogger("database")
    extra = {
        "operation": operation,
        "table": table,
        "user_id": user_id,
        "event_type": "database_operation"
    }
    if details:
        extra.update(details)

    db_logger.info(f"Database {operation}: {table}", extra=extra)


def cleanup_old_logs(logs_dir: Path, days_to_keep: int = 30):
    """Clean up old log files to prevent disk space issues."""
    try:
        import glob
        from datetime import timedelta

        cutoff_date = date.today() - timedelta(days=days_to_keep)

        # Find all log files with date patterns
        log_patterns = [
            "errors_*.log*",
            "api_*.log*",
            "application_*.log*"
        ]

        for pattern in log_patterns:
            for log_file in glob.glob(str(logs_dir / pattern)):
                log_path = Path(log_file)

                # Extract date from filename (format: prefix_YYYY-MM-DD.log)
                try:
                    # Extract date part from filename
                    filename = log_path.stem  # Gets filename without extension
                    if filename.count('_') >= 2:  # e.g., errors_2025-09-29
                        date_part = filename.split('_')[-1]  # Get the last part (date)
                        log_date = datetime.strptime(date_part, "%Y-%m-%d").date()

                        if log_date < cutoff_date:
                            log_path.unlink()  # Delete the file
                            print(f"Cleaned up old log file: {log_path}")

                except (ValueError, IndexError):
                    # Skip files that don't match expected date format
                    continue

    except Exception as e:
        # Don't fail startup if log cleanup fails
        print(f"Warning: Failed to clean up old logs: {e}")


def get_log_files_info(logs_dir: Path = None):
    """Get information about current log files."""
    if logs_dir is None:
        logs_dir = Path("logs_store")

    current_date = date.today().strftime("%Y-%m-%d")

    log_files = {
        "errors": logs_dir / f"errors_{current_date}.log",
        "api": logs_dir / f"api_{current_date}.log",
        "application": logs_dir / f"application_{current_date}.log"
    }

    info = {}
    for log_type, log_path in log_files.items():
        if log_path.exists():
            stat = log_path.stat()
            info[log_type] = {
                "path": str(log_path),
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        else:
            info[log_type] = {"path": str(log_path), "exists": False}

    return info