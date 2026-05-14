"""
Middleware приложения.
"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())

        request.state.request_id = request_id

        logger.info({
            "event": "request_started",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path
        })

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        logger.info({
            "event": "request_finished",
            "request_id": request_id,
            "status_code": response.status_code
        })

        return response
