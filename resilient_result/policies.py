"""Policy objects for configurable resilience strategies."""

from typing import Optional


class Retry:
    """Retry policy with timeout - beautiful, short, powerful."""

    def __init__(self, attempts: int = 3, timeout: Optional[float] = None):
        """Create retry policy. Default: 3 attempts, no timeout."""
        self.attempts = attempts
        self.timeout = timeout

    @classmethod
    def api(cls, attempts: int = 3, timeout: float = 30.0):
        """API calls - moderate retries, reasonable timeout."""
        return cls(attempts=attempts, timeout=timeout)

    @classmethod
    def db(cls, attempts: int = 5, timeout: float = 60.0):
        """Database operations - more retries, longer timeout."""
        return cls(attempts=attempts, timeout=timeout)

    @classmethod
    def ml(cls, attempts: int = 2, timeout: float = 120.0):
        """ML inference - fewer retries, long timeout."""
        return cls(attempts=attempts, timeout=timeout)


class Circuit:
    """Circuit breaker policy - runaway protection."""

    def __init__(self, failures: int = 5, window: int = 300):
        self.failures = failures
        self.window = window

    @classmethod
    def fast(cls, failures: int = 3, window: int = 60):
        """Fast-tripping circuit - quick protection."""
        return cls(failures=failures, window=window)

    @classmethod
    def standard(cls, failures: int = 5, window: int = 300):
        """Standard circuit - balanced protection."""
        return cls(failures=failures, window=window)


class Backoff:
    """Backoff strategies - configurable timing."""

    def __init__(
        self,
        strategy: str = "exponential",
        delay: float = 1.0,
        factor: float = 2.0,
        max_delay: float = 30.0,
    ):
        self.strategy = strategy
        self.delay = delay
        self.factor = factor
        self.max_delay = max_delay

    def calculate(self, attempt: int) -> float:
        """Calculate delay for given attempt."""
        if self.strategy == "exponential":
            delay = self.delay * (self.factor**attempt)
            return min(delay, self.max_delay)
        elif self.strategy == "linear":
            return min(self.delay * (attempt + 1), self.max_delay)
        elif self.strategy == "fixed":
            return self.delay
        return self.delay

    @classmethod
    def exp(cls, delay: float = 0.1, factor: float = 2.0, max_delay: float = 30.0):
        """Exponential backoff - most common."""
        return cls(
            strategy="exponential", delay=delay, factor=factor, max_delay=max_delay
        )

    @classmethod
    def linear(cls, delay: float = 1.0, max_delay: float = 30.0):
        """Linear backoff - steady increase."""
        return cls(strategy="linear", delay=delay, max_delay=max_delay)

    @classmethod
    def fixed(cls, delay: float = 1.0):
        """Fixed delay - simple constant."""
        return cls(strategy="fixed", delay=delay)
