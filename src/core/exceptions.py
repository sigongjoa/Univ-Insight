"""
Custom exception classes for Univ-Insight.

Defines application-specific exceptions for:
- Crawler errors
- LLM processing errors
- API errors
- Database errors
"""

from typing import Optional, Any, Dict


class UnivInsightException(Exception):
    """Base exception for all Univ-Insight errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}


# ==================== Crawler Errors ====================

class CrawlerError(UnivInsightException):
    """Base exception for crawler-related errors."""

    pass


class CrawlTimeoutError(CrawlerError):
    """Raised when crawler operation times out."""

    def __init__(self, url: str, timeout: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Crawler timeout for {url} after {timeout}s",
            error_code="CRAWL_TIMEOUT",
            details={"url": url, "timeout": timeout, **(details or {})}
        )


class CrawlParseError(CrawlerError):
    """Raised when crawler cannot parse content."""

    def __init__(self, url: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Failed to parse content from {url}: {reason}",
            error_code="CRAWL_PARSE_ERROR",
            details={"url": url, "reason": reason, **(details or {})}
        )


class CrawlConnectionError(CrawlerError):
    """Raised when crawler cannot connect to target URL."""

    def __init__(self, url: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Connection error to {url}: {reason}",
            error_code="CRAWL_CONNECTION_ERROR",
            details={"url": url, "reason": reason, **(details or {})}
        )


# ==================== LLM Errors ====================

class LLMError(UnivInsightException):
    """Base exception for LLM-related errors."""

    pass


class LLMConnectionError(LLMError):
    """Raised when LLM service is unavailable."""

    def __init__(self, service: str, reason: str):
        super().__init__(
            message=f"Cannot connect to LLM service ({service}): {reason}",
            error_code="LLM_CONNECTION_ERROR",
            details={"service": service, "reason": reason}
        )


class LLMTimeoutError(LLMError):
    """Raised when LLM operation times out."""

    def __init__(self, timeout: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"LLM operation timeout after {timeout}s",
            error_code="LLM_TIMEOUT",
            details={"timeout": timeout, **(details or {})}
        )


class LLMParseError(LLMError):
    """Raised when LLM response cannot be parsed."""

    def __init__(self, response: str, reason: str):
        super().__init__(
            message=f"Failed to parse LLM response: {reason}",
            error_code="LLM_PARSE_ERROR",
            details={"response_preview": response[:100], "reason": reason}
        )


class LLMValidationError(LLMError):
    """Raised when LLM response doesn't match expected schema."""

    def __init__(self, expected: str, got: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"LLM response validation failed. Expected {expected}, got {got}",
            error_code="LLM_VALIDATION_ERROR",
            details={"expected": expected, "got": got, **(details or {})}
        )


# ==================== API Errors ====================

class APIError(UnivInsightException):
    """Base exception for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code or "API_ERROR", details)
        self.status_code = status_code


class ValidationError(APIError):
    """Raised when request validation fails."""

    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Validation error in field '{field}': {reason}",
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"field": field, "reason": reason}
        )


class NotFoundError(APIError):
    """Raised when resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with id '{resource_id}' not found",
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class AuthenticationError(APIError):
    """Raised when authentication fails."""

    def __init__(self, reason: str = "Invalid credentials"):
        super().__init__(
            message=f"Authentication failed: {reason}",
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details={"reason": reason}
        )


class AuthorizationError(APIError):
    """Raised when user doesn't have permission."""

    def __init__(self, reason: str = "Insufficient permissions"):
        super().__init__(
            message=f"Access denied: {reason}",
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details={"reason": reason}
        )


class ConflictError(APIError):
    """Raised when resource already exists."""

    def __init__(self, resource_type: str, reason: str):
        super().__init__(
            message=f"Conflict: {resource_type} - {reason}",
            status_code=409,
            error_code="CONFLICT",
            details={"resource_type": resource_type, "reason": reason}
        )


# ==================== Notification Errors ====================

class NotificationError(UnivInsightException):
    """Base exception for notification-related errors."""

    pass


class NotionAPIError(NotificationError):
    """Raised when Notion API call fails."""

    def __init__(self, operation: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Notion API error during {operation}: {reason}",
            error_code="NOTION_API_ERROR",
            details={"operation": operation, "reason": reason, **(details or {})}
        )


class KakaoAPIError(NotificationError):
    """Raised when Kakao API call fails."""

    def __init__(self, operation: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Kakao API error during {operation}: {reason}",
            error_code="KAKAO_API_ERROR",
            details={"operation": operation, "reason": reason, **(details or {})}
        )


# ==================== Database Errors ====================

class DatabaseError(UnivInsightException):
    """Base exception for database-related errors."""

    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Database connection error: {reason}",
            error_code="DB_CONNECTION_ERROR",
            details={"reason": reason}
        )


class DatabaseIntegrityError(DatabaseError):
    """Raised when database integrity constraint is violated."""

    def __init__(self, constraint: str, reason: str):
        super().__init__(
            message=f"Database integrity error: {reason}",
            error_code="DB_INTEGRITY_ERROR",
            details={"constraint": constraint, "reason": reason}
        )


# ==================== Recommendation Errors ====================

class RecommendationError(UnivInsightException):
    """Base exception for recommendation-related errors."""

    pass


class VectorStoreError(RecommendationError):
    """Raised when vector store operation fails."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Vector store error during {operation}: {reason}",
            error_code="VECTOR_STORE_ERROR",
            details={"operation": operation, "reason": reason}
        )


class EmbeddingError(RecommendationError):
    """Raised when embedding generation fails."""

    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Embedding generation failed: {reason}",
            error_code="EMBEDDING_ERROR",
            details={"reason": reason, **(details or {})}
        )
