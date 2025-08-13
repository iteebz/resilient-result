"""Beautiful @resilient decorators for resilient operations."""

import asyncio
import logging
import time
from functools import wraps
from typing import TYPE_CHECKING, Optional

from .circuit import circuit
from .defaults import (
    CIRCUIT_FAILURES,
    CIRCUIT_WINDOW,
    RATE_LIMIT_RPS,
    RETRY_ATTEMPTS,
    TIMEOUT_SECONDS,
)
from .rate_limit import rate_limit
from .result import Err, Ok, Result
from .timeout import timeout

if TYPE_CHECKING:
    from .policies import Backoff

logger = logging.getLogger("resilient_result")


def retry(
    attempts: int = RETRY_ATTEMPTS,
    backoff: Optional["Backoff"] = None,
    error_type: Optional[type] = None,
    handler=None,
):
    """2 attempts, 1s fixed backoff - reasonable everywhere."""
    from .policies import Backoff

    if backoff is None:
        backoff = Backoff.fixed(1.0)

    if error_type is None:
        error_type = Exception

    async def _should_stop_async(e, attempt):
        """Check if we should stop retrying based on async handler."""
        if handler and asyncio.iscoroutinefunction(handler):
            result = await handler(e)
            if result is False:
                return True
        elif handler:
            result = handler(e)
            if result is False:
                return True
        return False

    def _should_stop_sync(e, attempt):
        """Check if we should stop retrying based on sync handler."""
        if handler and not asyncio.iscoroutinefunction(handler):
            result = handler(e)
            if result is False:
                return True
        return False

    def _format_error(e):
        """Format error according to error_type preference."""
        return e if error_type is Exception else error_type(str(e))

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                error = None
                for attempt in range(attempts):
                    try:
                        result = await func(*args, **kwargs)
                        # Log success if we had retries
                        if attempt > 0:
                            logger.info(
                                "%s succeeded after %d attempts",
                                func.__name__,
                                attempt + 1,
                            )
                        return (
                            Ok(result)
                            if not isinstance(result, Result)
                            else result.flatten()
                        )
                    except Exception as e:
                        error = e

                        # Check if we should stop retrying
                        if await _should_stop_async(e, attempt):
                            return Err(_format_error(e))

                        # If this is the last attempt, don't sleep or log
                        if attempt < attempts - 1:
                            delay = backoff.calculate(attempt)
                            logger.debug(
                                "Retrying %s (attempt %d/%d) after %s: waiting %.1fs",
                                func.__name__,
                                attempt + 2,
                                attempts,
                                type(e).__name__,
                                delay,
                            )
                            await asyncio.sleep(delay)

                # Return the last exception we caught
                return Err(_format_error(error))

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            error = None
            for attempt in range(attempts):
                try:
                    result = func(*args, **kwargs)
                    # Log success if we had retries
                    if attempt > 0:
                        logger.info(
                            "%s succeeded after %d attempts", func.__name__, attempt + 1
                        )
                    return (
                        Ok(result)
                        if not isinstance(result, Result)
                        else result.flatten()
                    )
                except Exception as e:
                    error = e

                    # Check if we should stop retrying
                    if _should_stop_sync(e, attempt):
                        return Err(_format_error(e))

                    # If this is the last attempt, don't sleep or log
                    if attempt < attempts - 1:
                        delay = backoff.calculate(attempt)
                        logger.debug(
                            "Retrying %s (attempt %d/%d) after %s: waiting %.1fs",
                            func.__name__,
                            attempt + 2,
                            attempts,
                            type(e).__name__,
                            delay,
                        )
                        time.sleep(delay)

            # Return the last exception we caught
            return Err(_format_error(error))

        return sync_wrapper

    return decorator


class Resilient:
    """Beautiful resilience patterns - clean composition."""

    def __call__(
        self,
        func=None,
        *,
        retry=None,
        timeout=None,
        circuit=None,
        backoff=None,
        error_type=None,
        handler=None,
    ):
        """@resilient or @resilient() - Main decorator with policy composition."""
        from .policies import Backoff, Retry

        if func is not None:
            # Called as @resilient (no parentheses)
            return self()(func)

        # Called as @resilient() or @resilient(params)
        retry_policy = retry if retry is not None else Retry()
        backoff_policy = backoff if backoff is not None else Backoff.fixed(1.0)

        # Handle timeout from retry policy or direct parameter
        timeout_seconds = timeout or (retry_policy.timeout if retry else None)

        if timeout_seconds:
            # Manual composition since we deleted compose()
            def decorator(func):
                # Apply timeout first, then retry
                timeout_func = self.timeout(timeout_seconds)(func)
                return globals()["retry"](
                    attempts=retry_policy.attempts,
                    backoff=backoff_policy,
                    error_type=error_type,
                    handler=handler,
                )(timeout_func)

            return decorator
        # Just retry
        return globals()["retry"](
            attempts=retry_policy.attempts,
            backoff=backoff_policy,
            error_type=error_type,
            handler=handler,
        )

    # Direct pattern access
    @staticmethod
    def retry(attempts: int = RETRY_ATTEMPTS, **kwargs):
        """@resilient.retry - Pure retry logic."""
        return retry(attempts, **kwargs)

    @staticmethod
    def timeout(seconds: float = TIMEOUT_SECONDS, error_type: type = TimeoutError):
        """@resilient.timeout - Pure timeout logic."""
        return timeout(seconds, error_type)

    @staticmethod
    def circuit(failures: int = CIRCUIT_FAILURES, window: int = CIRCUIT_WINDOW):
        """@resilient.circuit - Circuit breaker that returns Result types."""
        return circuit(failures, window)

    @staticmethod
    def rate_limit(rps: float = RATE_LIMIT_RPS, burst: int = None):
        """@resilient.rate_limit - Rate limiting with Result wrapper."""

        def result_wrapper(func):
            rate_limit_func = rate_limit(rps, burst)(func)

            if asyncio.iscoroutinefunction(func):

                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    result = await rate_limit_func(*args, **kwargs)
                    return Ok(result) if not isinstance(result, Result) else result

                return async_wrapper

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                result = rate_limit_func(*args, **kwargs)
                return Ok(result) if not isinstance(result, Result) else result

            return sync_wrapper

        return result_wrapper


# Create instance for beautiful usage
resilient = Resilient()
