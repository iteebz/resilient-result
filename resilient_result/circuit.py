"""Circuit breaker for runaway protection."""

import asyncio
import time
from collections import defaultdict
from functools import wraps
from typing import Dict


class CircuitBreaker:
    """Minimal circuit breaker for runaway protection."""

    def __init__(self):
        self._failures: Dict[str, list] = defaultdict(list)

    def is_open(self, func_name: str, failures: int, window: int) -> bool:
        """Check if circuit is open (too many failures)."""
        now = time.time()
        fails = self._failures[func_name]

        # Remove old failures outside time window
        self._failures[func_name] = [f for f in fails if now - f < window]

        return len(self._failures[func_name]) >= failures

    def record_failure(self, func_name: str) -> None:
        """Record a failure for this function."""
        self._failures[func_name].append(time.time())

    def record_success(self, func_name: str) -> None:
        """Record a success and reset failures."""
        self._failures[func_name] = []


# Global instance
circuit_breaker = CircuitBreaker()


def circuit(failures: int = 3, window: int = 300):
    """Circuit breaker decorator - returns Result types for consistent interface.

    On success: returns Ok(result)
    On failure: records failure and returns Err(exception)
    Circuit open: returns Err(CircuitError)

    This maintains the Result interface while providing circuit breaker functionality.
    """

    def decorator(func):
        func_name = f"{func.__module__}.{func.__qualname__}"
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @wraps(func)
            async def async_circuit_protected(*args, **kwargs):
                from .result import Err, Ok, Result

                # Check if circuit is open
                if circuit_breaker.is_open(func_name, failures, window):
                    from .errors import CircuitError

                    return Err(CircuitError("Circuit breaker open"))

                try:
                    result = await func(*args, **kwargs)
                    circuit_breaker.record_success(func_name)
                    return Ok(result) if not isinstance(result, Result) else result
                except Exception as e:
                    circuit_breaker.record_failure(func_name)
                    return Err(e)

            return async_circuit_protected
        else:

            @wraps(func)
            def sync_circuit_protected(*args, **kwargs):
                from .result import Err, Ok, Result

                # Check if circuit is open
                if circuit_breaker.is_open(func_name, failures, window):
                    from .errors import CircuitError

                    return Err(CircuitError("Circuit breaker open"))

                try:
                    result = func(*args, **kwargs)
                    circuit_breaker.record_success(func_name)
                    return Ok(result) if not isinstance(result, Result) else result
                except Exception as e:
                    circuit_breaker.record_failure(func_name)
                    return Err(e)

            return sync_circuit_protected

    return decorator
