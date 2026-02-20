"""Custom exception handlers for Salon Flow API.

This module provides standardized exception handling across the API:
- Custom exception classes for different error types
- FastAPI exception handlers for consistent error responses
- Error response models following the {message, code} format
"""

# Standard library imports
from typing import Any, Dict, Optional

# Third-party imports
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()


# ============================================================================
# Error Response Models
# ============================================================================

class ErrorDetail(BaseModel):
    """Standard error detail format for API responses.
    
    Attributes:
        message: Human-readable error message
        code: Machine-readable error code for programmatic handling
        details: Optional additional error context
    """
    message: str
    code: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response wrapper.
    
    Attributes:
        success: Always False for error responses
        error: Error detail object
    """
    success: bool = False
    error: ErrorDetail


# ============================================================================
# Custom Exception Classes
# ============================================================================

class SalonFlowException(Exception):
    """Base exception for all Salon Flow API errors.
    
    All custom exceptions should inherit from this class.
    
    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        status_code: HTTP status code to return
        details: Optional additional context
    """
    
    def __init__(
        self,
        message: str,
        code: str = "internal_error",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        result = {
            "message": self.message,
            "code": self.code,
        }
        if self.details:
            result["details"] = self.details
        return result


class NotFoundError(SalonFlowException):
    """Resource not found exception.
    
    Use when a requested resource does not exist.
    """
    
    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "not_found",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ValidationError(SalonFlowException):
    """Validation error exception.
    
    Use when input data fails validation rules.
    """
    
    def __init__(
        self,
        message: str = "Validation failed",
        code: str = "validation_error",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class AuthenticationError(SalonFlowException):
    """Authentication failed exception.
    
    Use when authentication credentials are invalid or missing.
    """
    
    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "authentication_failed",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationError(SalonFlowException):
    """Authorization failed exception.
    
    Use when user lacks permission for the requested action.
    """
    
    def __init__(
        self,
        message: str = "Access denied",
        code: str = "access_denied",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class ConflictError(SalonFlowException):
    """Resource conflict exception.
    
    Use when a resource already exists or conflicts with existing state.
    """
    
    def __init__(
        self,
        message: str = "Resource conflict",
        code: str = "conflict",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class RateLimitError(SalonFlowException):
    """Rate limit exceeded exception.
    
    Use when API rate limits are exceeded.
    """
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: str = "rate_limit_exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        retry_details = details or {}
        if retry_after:
            retry_details["retry_after"] = retry_after
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=retry_details
        )
        self.retry_after = retry_after


class ServiceUnavailableError(SalonFlowException):
    """Service unavailable exception.
    
    Use when an external service or dependency is unavailable.
    """
    
    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        code: str = "service_unavailable",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


# ============================================================================
# Exception Handlers
# ============================================================================

async def salon_flow_exception_handler(
    request: Request,
    exc: SalonFlowException
) -> JSONResponse:
    """Handle all SalonFlowException instances.
    
    Args:
        request: The FastAPI request object
        exc: The raised SalonFlowException
        
    Returns:
        JSONResponse with standardized error format
    """
    logger.error(
        "API exception occurred",
        exception_type=type(exc).__name__,
        message=exc.message,
        code=exc.code,
        path=request.url.path,
        method=request.method,
    )
    
    response = ErrorResponse(
        error=ErrorDetail(
            message=exc.message,
            code=exc.code,
            details=exc.details
        )
    )
    
    headers = {}
    if isinstance(exc, RateLimitError) and exc.retry_after:
        headers["Retry-After"] = str(exc.retry_after)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
        headers=headers if headers else None
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """Handle standard HTTPException instances.
    
    Converts HTTPException to standardized error format.
    
    Args:
        request: The FastAPI request object
        exc: The raised HTTPException
        
    Returns:
        JSONResponse with standardized error format
    """
    # Extract message and code from detail
    if isinstance(exc.detail, dict):
        message = exc.detail.get("message", "An error occurred")
        code = exc.detail.get("code", "http_error")
        details = exc.detail.get("details")
    else:
        message = str(exc.detail)
        code = "http_error"
        details = None
    
    logger.error(
        "HTTP exception occurred",
        status_code=exc.status_code,
        message=message,
        code=code,
        path=request.url.path,
        method=request.method,
    )
    
    response = ErrorResponse(
        error=ErrorDetail(
            message=message,
            code=code,
            details=details
        )
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
        headers=exc.headers
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions.
    
    Logs the full exception and returns a generic error response.
    
    Args:
        request: The FastAPI request object
        exc: The raised exception
        
    Returns:
        JSONResponse with generic error message
    """
    logger.exception(
        "Unexpected exception occurred",
        exception_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
    )
    
    response = ErrorResponse(
        error=ErrorDetail(
            message="An unexpected error occurred",
            code="internal_error"
        )
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump()
    )


# ============================================================================
# Registration Function
# ============================================================================

def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with a FastAPI application.
    
    This should be called during application initialization.
    
    Args:
        app: The FastAPI application instance
        
    Example:
        >>> from fastapi import FastAPI
        >>> from app.core.exceptions import register_exception_handlers
        
        >>> app = FastAPI()
        >>> register_exception_handlers(app)
    """
    app.add_exception_handler(SalonFlowException, salon_flow_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registered")


__all__ = [
    # Error models
    "ErrorDetail",
    "ErrorResponse",
    # Exception classes
    "SalonFlowException",
    "NotFoundError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "RateLimitError",
    "ServiceUnavailableError",
    # Handlers
    "register_exception_handlers",
    "salon_flow_exception_handler",
    "http_exception_handler",
    "generic_exception_handler",
]
