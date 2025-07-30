"""Timeout pattern - orthogonal time-based protection."""

import asyncio
from functools import wraps

from .result import Err, Ok, Result


def timeout(seconds: float, error_type: type = TimeoutError):
    """Pure timeout decorator - orthogonal to all other patterns."""

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    result = await asyncio.wait_for(
                        func(*args, **kwargs), timeout=seconds
                    )
                    return Ok(result) if not isinstance(result, Result) else result
                except asyncio.TimeoutError:
                    return Err(error_type(f"Timeout after {seconds}s"))
                except Exception as e:
                    return Err(e)

            return async_wrapper
        else:
            # Sync functions can't have true timeouts, but wrap in Result
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    return Ok(result) if not isinstance(result, Result) else result
                except Exception as e:
                    return Err(e)

            return sync_wrapper

    return decorator
