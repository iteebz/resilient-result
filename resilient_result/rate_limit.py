"""Token bucket rate limiting - smooth, configurable, beautiful."""

import asyncio
import time
from functools import wraps
from typing import Dict


class RateLimiter:
    """Token bucket rate limiter - smooth, configurable, beautiful."""

    def __init__(self):
        self._buckets: Dict[str, Dict] = {}

    async def acquire(self, key: str, rps: float = 1.0, burst: int = None) -> None:
        """Acquire permission to proceed - sleeps if rate limit exceeded."""
        burst = burst or max(1, int(rps * 2))  # 2x RPS burst
        now = time.time()

        # Initialize new bucket with full burst allowance
        if key not in self._buckets:
            self._buckets[key] = {"tokens": float(burst), "last_refill": now}

        bucket = self._buckets[key]

        # Refill tokens based on time elapsed
        elapsed = now - bucket["last_refill"]
        bucket["tokens"] = min(burst, bucket["tokens"] + elapsed * rps)
        bucket["last_refill"] = now

        # If no tokens available, sleep until we can get one
        if bucket["tokens"] < 1:
            sleep_time = (1 - bucket["tokens"]) / rps
            await asyncio.sleep(sleep_time)
            bucket["tokens"] = 0  # Consumed the token we waited for
        else:
            bucket["tokens"] -= 1  # Consume a token


# Global instance
rate_limiter = RateLimiter()


def rate_limit(rps: float = 1.0, burst: int = None, key: str = None):
    """Token bucket rate limiting."""

    def decorator(func):
        from .result import Err, Ok, Result

        func_key = key or f"{func.__module__}.{func.__qualname__}"
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @wraps(func)
            async def async_rate_limited(*args, **kwargs):
                try:
                    await rate_limiter.acquire(func_key, rps, burst)
                    result = await func(*args, **kwargs)
                    return Ok(result) if not isinstance(result, Result) else result
                except Exception as e:
                    return Err(e)

            return async_rate_limited
        else:

            @wraps(func)
            def sync_rate_limited(*args, **kwargs):
                try:
                    # Note: Sync functions can't properly rate limit without blocking
                    # Consider using async version for true rate limiting
                    result = func(*args, **kwargs)
                    return Ok(result) if not isinstance(result, Result) else result
                except Exception as e:
                    return Err(e)

            return sync_rate_limited

    return decorator
