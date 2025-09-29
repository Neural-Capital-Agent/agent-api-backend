import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
import logging
from core.logging_config import log_api_request, log_api_response, log_error


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Extract user info if available (from auth headers, etc.)
        user_id = request.headers.get("x-user-id") or "anonymous"
        request.state.user_id = user_id

        # Log incoming request
        start_time = time.time()
        endpoint = str(request.url.path)
        method = request.method

        log_api_request(
            endpoint=endpoint,
            method=method,
            user_id=user_id,
            request_id=request_id
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate response time
            process_time = time.time() - start_time

            # Log response
            log_api_response(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                response_time=round(process_time, 4),
                user_id=user_id,
                request_id=request_id
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 4))

            return response

        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger = logging.getLogger("api")

            log_error(
                logger=logger,
                error=e,
                context={
                    "endpoint": endpoint,
                    "method": method,
                    "user_id": user_id,
                    "request_id": request_id,
                    "response_time": round(process_time, 4),
                    "event_type": "request_error"
                }
            )

            # Re-raise the exception to let FastAPI handle it
            raise