"""Beautiful @resilient decorators for resilient operations."""

import asyncio
from functools import wraps
from typing import TYPE_CHECKING, Callable, Dict, Optional

if TYPE_CHECKING:
    from .policies import Backoff, Circuit, Retry

# All plugins now unified in plugins.py


def decorator(
    handler: Optional[Callable] = None,
    retry: Optional["Retry"] = None,
    circuit: Optional["Circuit"] = None,
    backoff: Optional["Backoff"] = None,
    error_type: Optional[type] = None,
):
    """Policy-based decorator with configurable retry, circuit, and backoff strategies."""
    from .policies import Backoff, Retry

    # Set beautiful defaults
    if retry is None:
        retry = Retry()
    if backoff is None:
        backoff = Backoff.exp()
    if error_type is None:
        error_type = Exception

    # Smart default handler - no ceremony for basic retry
    if handler is None:

        async def default_handler(error: Exception) -> Optional[bool]:
            """Default handler returns None to trigger retry."""
            return None  # Always retry until max attempts

        handler = default_handler

    def decorator_factory(func):
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                from .result import Err, Ok, Result

                for attempt in range(retry.attempts):
                    try:
                        # Apply timeout if specified in retry policy
                        if retry.timeout:
                            result = await asyncio.wait_for(
                                func(*args, **kwargs), timeout=retry.timeout
                            )
                        else:
                            result = await func(*args, **kwargs)

                        # Smart return detection - preserve Result types, wrap others, flatten nested Results
                        if isinstance(result, Result):
                            return (
                                result.flatten()
                            )  # Automatically flatten nested Results
                        return Ok(result)

                    except Exception as e:
                        if attempt < retry.attempts - 1:
                            # Call handler to determine if we should retry
                            should_retry = await handler(e)
                            if should_retry is False:
                                # Handler says stop retrying
                                return Err(error_type(str(e)))
                            # None or True means continue retrying - use configurable backoff
                            await asyncio.sleep(backoff.calculate(attempt))
                            continue

                        # Final attempt failed
                        return Err(error_type(str(e)))

                # Should never reach here
                return Err(error_type("Max retries exceeded"))

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                import time

                from .result import Err, Ok, Result

                for attempt in range(retry.attempts):
                    try:
                        result = func(*args, **kwargs)

                        # Smart return detection - preserve Result types, wrap others, flatten nested Results
                        if isinstance(result, Result):
                            return (
                                result.flatten()
                            )  # Automatically flatten nested Results
                        return Ok(result)

                    except Exception as e:
                        if attempt < retry.attempts - 1:
                            # For sync functions, use configurable backoff
                            time.sleep(backoff.calculate(attempt))
                            continue

                        # Final attempt failed
                        return Err(error_type(str(e)))

                return Err(error_type("Max retries exceeded"))

            return sync_wrapper

    return decorator_factory


class Resilient:
    """Extensible resilience patterns with registry architecture."""

    _registry: Dict[str, Callable] = {}

    def __call__(
        self,
        func=None,
        retry=None,
        circuit=None,
        backoff=None,
        error_type: Optional[type] = None,
        handler=None,
    ):
        """Enable both @resilient and @resilient(retry=Retry.api()) syntax."""
        if func is None:
            # Called as @resilient(retry=Retry.api()) - return decorator factory
            return decorator(
                retry=retry,
                circuit=circuit,
                backoff=backoff,
                error_type=error_type,
                handler=handler,
            )
        else:
            # Called as @resilient - apply decorator directly
            return decorator(
                retry=retry,
                circuit=circuit,
                backoff=backoff,
                error_type=error_type,
                handler=handler,
            )(func)

    # Built-in patterns - all return Result types
    @classmethod
    def network(cls, *args, **kwargs):
        """@resilient.network - Network calls with retry."""
        from .network import network

        return network(*args, **kwargs)

    @classmethod
    def parsing(cls, *args, **kwargs):
        """@resilient.parsing - JSON parsing with correction."""
        from .parsing import parsing

        return parsing(*args, **kwargs)

    @classmethod
    def circuit(cls, failures: int = 5, window: int = 60, **kwargs):
        """@resilient.circuit - Circuit breaker that returns Results."""
        from .circuit import circuit

        def result_circuit_decorator(func):
            # Apply circuit breaker first, then wrap in Result converter
            circuit_wrapped = circuit(failures=failures, window=window)(func)
            return decorator(**kwargs)(circuit_wrapped)

        return result_circuit_decorator

    @classmethod
    def rate_limit(cls, rps: float = 10.0, burst: int = 1, **kwargs):
        """@resilient.rate_limit - Rate limiting that returns Results."""
        from .rate_limit import rate_limit

        def result_rate_limit_decorator(func):
            # Apply rate limiting first, then wrap in Result converter
            rate_limited = rate_limit(rps=rps, burst=burst)(func)
            return decorator(**kwargs)(rate_limited)

        return result_rate_limit_decorator

    @classmethod
    def fallback(cls, primary_mode: str, fallback_mode: str, **kwargs):
        """@resilient.fallback - Fallback between modes on error."""

        async def fallback_handler(error):
            # Access function args through handler closure
            if (
                hasattr(fallback_handler, "_current_args")
                and len(fallback_handler._current_args) > 0
                and hasattr(fallback_handler._current_args[0], primary_mode)
            ):
                # Switch mode and retry
                setattr(fallback_handler._current_args[0], primary_mode, fallback_mode)
                return None  # Retry with modified state
            return False  # No recovery possible

        def decorator_with_fallback(func):
            decorated_func = decorator(handler=fallback_handler, **kwargs)(func)

            @wraps(decorated_func)
            async def wrapper(*args, **func_kwargs):
                fallback_handler._current_args = args
                try:
                    return await decorated_func(*args, **func_kwargs)
                finally:
                    if hasattr(fallback_handler, "_current_args"):
                        delattr(fallback_handler, "_current_args")

            return wrapper

        return decorator_with_fallback

    @classmethod
    def register(cls, name: str, decorator_factory: Callable):
        """Register a domain-specific @resilient pattern."""
        cls._registry[name] = decorator_factory

    def __getattr__(self, name: str):
        """Enable @resilient.custom_pattern syntax via dynamic attribute access."""
        if name in self._registry:
            return self._registry[name]
        raise AttributeError(
            f"'{self.__class__.__name__}' has no pattern '{name}'. Available: {list(self._registry.keys())}"
        )


# Create instance for beautiful usage
resilient = Resilient()
