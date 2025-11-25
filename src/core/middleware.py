"""
FastAPI middleware for global exception handling.

Provides:
- Unified error response format
- Logging of all errors
- Proper HTTP status codes
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Callable
from src.core.exceptions import (
    UnivInsightException, APIError, ValidationError, NotFoundError,
    AuthenticationError, AuthorizationError
)
from src.core.logging import get_logger
import uuid

logger = get_logger(__name__)


async def exception_middleware(request: Request, call_next: Callable) -> JSONResponse:
    """
    Middleware to catch and handle exceptions.

    Args:
        request: FastAPI request object
        call_next: Next middleware/route handler

    Returns:
        JSON response with error details
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    try:
        response = await call_next(request)
        return response

    except UnivInsightException as e:
        # Handle Univ-Insight exceptions
        status_code = getattr(e, 'status_code', 500)

        logger.warning(
            f"UnivInsightException: {e.message}",
            extra={
                "request_id": request_id,
                "error_code": e.error_code,
                "status_code": status_code
            }
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": e.error_code,
                    "message": e.message,
                    "details": e.details,
                    "request_id": request_id
                }
            }
        )

    except Exception as e:
        # Handle unexpected exceptions
        error_id = str(uuid.uuid4())

        logger.error(
            f"Unexpected error: {str(e)}",
            extra={
                "request_id": request_id,
                "error_id": error_id,
                "error_type": type(e).__name__
            },
            exc_info=True
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {
                        "error_id": error_id,
                        "error_type": type(e).__name__
                    },
                    "request_id": request_id
                }
            }
        )


# ==================== Error Response Models ====================

def error_response(
    error_code: str,
    message: str,
    status_code: int = 500,
    details: dict = None,
    request_id: str = None
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        error_code: Machine-readable error code
        message: Human-readable message
        status_code: HTTP status code
        details: Additional error details
        request_id: Request tracking ID

    Returns:
        JSONResponse with error details
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {},
                "request_id": request_id or str(uuid.uuid4())
            }
        }
    )


def validation_error_response(
    field: str,
    reason: str,
    request_id: str = None
) -> JSONResponse:
    """Create a validation error response."""
    return error_response(
        error_code="VALIDATION_ERROR",
        message=f"Validation error in field '{field}': {reason}",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"field": field, "reason": reason},
        request_id=request_id
    )


def not_found_response(
    resource_type: str,
    resource_id: str,
    request_id: str = None
) -> JSONResponse:
    """Create a not found error response."""
    return error_response(
        error_code="NOT_FOUND",
        message=f"{resource_type} with id '{resource_id}' not found",
        status_code=status.HTTP_404_NOT_FOUND,
        details={"resource_type": resource_type, "resource_id": resource_id},
        request_id=request_id
    )


def unauthorized_response(
    reason: str = "Invalid credentials",
    request_id: str = None
) -> JSONResponse:
    """Create an unauthorized error response."""
    return error_response(
        error_code="AUTHENTICATION_ERROR",
        message=f"Authentication failed: {reason}",
        status_code=status.HTTP_401_UNAUTHORIZED,
        details={"reason": reason},
        request_id=request_id
    )


def forbidden_response(
    reason: str = "Insufficient permissions",
    request_id: str = None
) -> JSONResponse:
    """Create a forbidden error response."""
    return error_response(
        error_code="AUTHORIZATION_ERROR",
        message=f"Access denied: {reason}",
        status_code=status.HTTP_403_FORBIDDEN,
        details={"reason": reason},
        request_id=request_id
    )


def conflict_response(
    resource_type: str,
    reason: str,
    request_id: str = None
) -> JSONResponse:
    """Create a conflict error response."""
    return error_response(
        error_code="CONFLICT",
        message=f"Conflict: {resource_type} - {reason}",
        status_code=status.HTTP_409_CONFLICT,
        details={"resource_type": resource_type, "reason": reason},
        request_id=request_id
    )
