"""Beautiful @resilient decorators for resilient operations."""

import asyncio
from functools import wraps
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .policies import Backoff

# All plugins now unified in plugins.py


def retry(
    attempts: int = 3,
    backoff: Optional["Backoff"] = None,
    error_type: Optional[type] = None,
    handler=None,
):
    """Pure retry decorator - clean, orthogonal, beautiful."""
    from .policies import Backoff

    if backoff is None:
        backoff = Backoff.exp()
    if error_type is None:
        error_type = Exception

    async def _should_stop_retrying_async(e, attempt):
        """Check if we should stop retrying based on async handler."""
        if handler and asyncio.iscoroutinefunction(handler):
            handler_result = await handler(e)
            if handler_result is False:
                return True
        elif handler:
            handler_result = handler(e)
            if handler_result is False:
                return True
        return False

    def _should_stop_retrying_sync(e, attempt):
        """Check if we should stop retrying based on sync handler."""
        if handler and not asyncio.iscoroutinefunction(handler):
            handler_result = handler(e)
            if handler_result is False:
                return True
        return False

    def _format_error(e):
        """Format error according to error_type preference."""
        return e if error_type is Exception else error_type(str(e))

    def decorator(func):
        from .result import Err, Ok, Result

        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(attempts):
                    try:
                        result = await func(*args, **kwargs)
                        return (
                            Ok(result)
                            if not isinstance(result, Result)
                            else result.flatten()
                        )
                    except Exception as e:
                        last_exception = e

                        # Check if we should stop retrying
                        if await _should_stop_retrying_async(e, attempt):
                            return Err(_format_error(e))

                        # If this is the last attempt, don't sleep
                        if attempt < attempts - 1:
                            await asyncio.sleep(backoff.calculate(attempt))

                # Return the last exception we caught
                return Err(_format_error(last_exception))

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            import time

            last_exception = None
            for attempt in range(attempts):
                try:
                    result = func(*args, **kwargs)
                    return (
                        Ok(result)
                        if not isinstance(result, Result)
                        else result.flatten()
                    )
                except Exception as e:
                    last_exception = e

                    # Check if we should stop retrying
                    if _should_stop_retrying_sync(e, attempt):
                        return Err(_format_error(e))

                    # If this is the last attempt, don't sleep
                    if attempt < attempts - 1:
                        time.sleep(backoff.calculate(attempt))

            # Return the last exception we caught
            return Err(_format_error(last_exception))

        return sync_wrapper

    return decorator


def compose(*decorators):
    """Compose decorators beautifully - right to left application."""

    def composed(func):
        for decorator in reversed(decorators):
            func = decorator(func)
        return func

    return composed


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
        backoff_policy = backoff if backoff is not None else Backoff.exp()

        # Handle timeout from retry policy or direct parameter
        timeout_seconds = timeout or (retry_policy.timeout if retry else None)

        if timeout_seconds:
            # Compose timeout + retry
            return compose(
                self.timeout(timeout_seconds),
                globals()["retry"](
                    attempts=retry_policy.attempts,
                    backoff=backoff_policy,
                    error_type=error_type,
                    handler=handler,
                ),
            )
        # Just retry
        return globals()["retry"](
            attempts=retry_policy.attempts,
            backoff=backoff_policy,
            error_type=error_type,
            handler=handler,
        )

    # Direct pattern access
    @staticmethod
    def retry(attempts: int = 3, **kwargs):
        """@resilient.retry - Pure retry logic."""
        return retry(attempts, **kwargs)

    @staticmethod
    def timeout(seconds: float, error_type: type = TimeoutError):
        """@resilient.timeout - Pure timeout logic."""
        from .timeout import timeout

        return timeout(seconds, error_type)

    @staticmethod
    def circuit(failures: int = 3, window: int = 300):
        """@resilient.circuit - Circuit breaker that returns Result types."""
        from .circuit import circuit

        return circuit(failures, window)

    @staticmethod
    def rate_limit(rps: float = 1.0, burst: int = None):
        """@resilient.rate_limit - Rate limiting with Result wrapper."""
        import asyncio
        from functools import wraps

        from .rate_limit import rate_limit

        def result_wrapper(func):
            rate_limit_func = rate_limit(rps, burst)(func)
            from .result import Ok, Result

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

    # Composition helpers - common patterns
    @classmethod
    def api(cls, attempts: int = 3, timeout_s: float = 30.0):
        """@resilient.api - Common API pattern: timeout + retry."""
        return compose(cls.timeout(timeout_s), cls.retry(attempts))

    @classmethod
    def db(cls, attempts: int = 5, timeout_s: float = 60.0):
        """@resilient.db - Database pattern: timeout + retry."""
        return compose(cls.timeout(timeout_s), cls.retry(attempts))

    @classmethod
    def protected(cls, attempts: int = 3, failures: int = 5, window: int = 300):
        """@resilient.protected - Full protection: circuit + retry."""
        return compose(cls.circuit(failures, window), cls.retry(attempts))


# Create instance for beautiful usage
resilient = Resilient()
