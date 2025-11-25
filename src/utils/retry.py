"""
Retry decorator with exponential backoff for handling transient failures.

Provides utilities for retrying failed operations with:
- Exponential backoff delay
- Configurable retry count
- Specific exception handling
- Jitter to prevent thundering herd
"""

import asyncio
import functools
import time
import random
from typing import Callable, Type, Tuple, Optional, Any
from src.core.logging import get_logger

logger = get_logger(__name__)


def retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Decorator for retrying function calls with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts (including initial)
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delay
        exceptions: Tuple of exception types to catch and retry on

    Returns:
        Decorator function

    Example:
        @retry(max_attempts=3, initial_delay=1.0, exceptions=(TimeoutError, ConnectionError))
        def fetch_data(url):
            # Some operation that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 1
            current_delay = initial_delay

            while True:
                try:
                    logger.debug(
                        f"Attempting {func.__name__} (attempt {attempt}/{max_attempts})",
                        extra={"attempt": attempt, "max_attempts": max_attempts}
                    )
                    return func(*args, **kwargs)

                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(
                            f"Failed {func.__name__} after {max_attempts} attempts",
                            extra={"attempt": attempt, "error": str(e)}
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(current_delay, max_delay)
                    if jitter:
                        delay = delay * (0.5 + random.random())

                    logger.warning(
                        f"Retrying {func.__name__} after {delay:.2f}s (attempt {attempt}/{max_attempts})",
                        extra={"attempt": attempt, "delay": delay, "error": str(e)}
                    )

                    time.sleep(delay)
                    current_delay *= exponential_base
                    attempt += 1

        return wrapper

    return decorator


def async_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Decorator for retrying async function calls with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts (including initial)
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delay
        exceptions: Tuple of exception types to catch and retry on

    Returns:
        Decorator function

    Example:
        @async_retry(max_attempts=3, initial_delay=1.0, exceptions=(asyncio.TimeoutError,))
        async def fetch_data_async(url):
            # Some async operation that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 1
            current_delay = initial_delay

            while True:
                try:
                    logger.debug(
                        f"Attempting async {func.__name__} (attempt {attempt}/{max_attempts})",
                        extra={"attempt": attempt, "max_attempts": max_attempts}
                    )
                    return await func(*args, **kwargs)

                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(
                            f"Failed async {func.__name__} after {max_attempts} attempts",
                            extra={"attempt": attempt, "error": str(e)}
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(current_delay, max_delay)
                    if jitter:
                        delay = delay * (0.5 + random.random())

                    logger.warning(
                        f"Retrying async {func.__name__} after {delay:.2f}s (attempt {attempt}/{max_attempts})",
                        extra={"attempt": attempt, "delay": delay, "error": str(e)}
                    )

                    await asyncio.sleep(delay)
                    current_delay *= exponential_base
                    attempt += 1

        return wrapper

    return decorator


class RetryConfig:
    """Configuration class for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def to_decorator(
        self,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ) -> Callable:
        """
        Create a retry decorator from this configuration.

        Args:
            exceptions: Tuple of exception types to retry on

        Returns:
            Decorator function
        """
        return retry(
            max_attempts=self.max_attempts,
            initial_delay=self.initial_delay,
            max_delay=self.max_delay,
            exponential_base=self.exponential_base,
            jitter=self.jitter,
            exceptions=exceptions
        )

    def to_async_decorator(
        self,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ) -> Callable:
        """
        Create an async retry decorator from this configuration.

        Args:
            exceptions: Tuple of exception types to retry on

        Returns:
            Decorator function
        """
        return async_retry(
            max_attempts=self.max_attempts,
            initial_delay=self.initial_delay,
            max_delay=self.max_delay,
            exponential_base=self.exponential_base,
            jitter=self.jitter,
            exceptions=exceptions
        )


# Predefined retry configurations

# For quick operations (API calls, file reads)
QUICK_RETRY = RetryConfig(
    max_attempts=3,
    initial_delay=0.5,
    max_delay=5.0,
    exponential_base=2.0,
    jitter=True
)

# For network operations (web crawling, external APIs)
NETWORK_RETRY = RetryConfig(
    max_attempts=5,
    initial_delay=1.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True
)

# For long-running operations (LLM inference, batch processing)
LONG_RETRY = RetryConfig(
    max_attempts=3,
    initial_delay=2.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True
)
