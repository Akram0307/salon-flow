"""FastAPI middleware for performance optimization."""
import gzip
import json
from typing import Callable, List, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog

logger = structlog.get_logger()


class GZipMiddleware(BaseHTTPMiddleware):
    """Enhanced GZip compression middleware with configurable settings."""

    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 500,
        compress_level: int = 6,
        exclude_paths: Optional[List[str]] = None,
        exclude_content_types: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compress_level = compress_level
        self.exclude_paths = exclude_paths or []
        self.exclude_content_types = exclude_content_types or [
            "image/",
            "video/",
            "audio/",
            "application/pdf",
            "application/zip",
            "application/octet-stream",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return await call_next(request)

        # Check excluded paths
        for exclude_path in self.exclude_paths:
            if request.url.path.startswith(exclude_path):
                return await call_next(request)

        # Get response
        response = await call_next(request)

        # Check content type
        content_type = response.headers.get("content-type", "")
        for excluded_type in self.exclude_content_types:
            if excluded_type in content_type:
                return response

        # Check content length
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < self.minimum_size:
            return response

        # Check if already compressed
        if response.headers.get("content-encoding"):
            return response

        # Compress response body
        try:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            if len(body) < self.minimum_size:
                return JSONResponse(
                    content=json.loads(body),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )

            compressed_body = gzip.compress(body, compresslevel=self.compress_level)

            # Update headers
            headers = dict(response.headers)
            headers["content-encoding"] = "gzip"
            headers["content-length"] = str(len(compressed_body))
            headers["vary"] = "Accept-Encoding"

            return Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=headers,
                media_type=content_type,
            )
        except Exception as e:
            logger.warning("GZip compression failed", error=str(e))
            return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Middleware to add cache control headers for static responses."""

    def __init__(
        self,
        app: ASGIApp,
        default_max_age: int = 300,
        cache_paths: Optional[dict] = None,
    ):
        super().__init__(app)
        self.default_max_age = default_max_age
        self.cache_paths = cache_paths or {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add cache control for GET requests
        if request.method == "GET":
            path = request.url.path

            # Check for specific cache settings
            max_age = self.default_max_age
            for pattern, age in self.cache_paths.items():
                if pattern in path:
                    max_age = age
                    break

            # Don't cache authenticated endpoints by default
            auth_header = request.headers.get("authorization")
            if auth_header:
                response.headers["cache-control"] = "private, no-cache"
            elif max_age > 0:
                response.headers["cache-control"] = f"public, max-age={max_age}"

        return response


class PerformanceHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add performance-related headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import time
        start_time = time.time()

        response = await call_next(request)

        # Add server timing header
        process_time = (time.time() - start_time) * 1000
        response.headers["x-process-time-ms"] = f"{process_time:.2f}"
        response.headers["x-server"] = "salon-flow-api"

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging with performance tracking."""

    def __init__(self, app: ASGIApp, log_body: bool = False):
        super().__init__(app)
        self.log_body = log_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import time
        import uuid

        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        # Log request
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )

        response = await call_next(request)

        # Log response
        process_time = (time.time() - start_time) * 1000
        logger.info(
            "Request completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time_ms=f"{process_time:.2f}",
        )

        response.headers["x-request-id"] = request_id
        return response
