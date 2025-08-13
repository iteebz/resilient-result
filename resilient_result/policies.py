"""Policy objects for configurable resilience strategies."""

import random

from .defaults import (
    BACKOFF_JITTER,
    CIRCUIT_FAILURES,
    CIRCUIT_WINDOW,
    RETRY_ATTEMPTS,
    TIMEOUT_SECONDS,
)


class Retry:
    """Pure retry policy - orthogonal, composable, beautiful."""

    def __init__(self, attempts: int = RETRY_ATTEMPTS, timeout: float = None):
        """Create retry policy. Default: 2 attempts, no timeout."""
        self.attempts = attempts
        self.timeout = timeout


class Circuit:
    """Circuit breaker policy - runaway protection."""

    def __init__(self, failures: int = CIRCUIT_FAILURES, window: int = CIRCUIT_WINDOW):
        self.failures = failures
        self.window = window


class Backoff:
    """Backoff strategies - configurable timing."""

    def __init__(
        self,
        strategy: str = "exponential",
        delay: float = 1.0,
        factor: float = 2.0,
        max_delay: float = 30.0,
        jitter: bool = BACKOFF_JITTER,
    ):
        self.strategy = strategy
        self.delay = delay
        self.factor = factor
        self.max_delay = max_delay
        self.jitter = jitter

    def calculate(self, attempt: int) -> float:
        """Calculate delay for given attempt."""
        if self.strategy == "exponential":
            delay = self.delay * (self.factor**attempt)
        elif self.strategy == "linear":
            delay = self.delay * (attempt + 1)
        elif self.strategy == "fixed":
            delay = self.delay
        else:
            delay = self.delay

        # Apply max_delay cap
        delay = min(delay, self.max_delay)

        # Apply jitter to prevent thundering herd
        if self.jitter:
            delay *= 0.5 + random.random() * 0.5  # 50-100% of calculated delay

        return delay

    @classmethod
    def exp(
        cls,
        delay: float = 0.1,
        factor: float = 2.0,
        max_delay: float = 30.0,
        jitter: bool = BACKOFF_JITTER,
    ):
        """Exponential backoff - most common."""
        return cls(
            strategy="exponential",
            delay=delay,
            factor=factor,
            max_delay=max_delay,
            jitter=jitter,
        )

    @classmethod
    def linear(
        cls,
        delay: float = 1.0,
        max_delay: float = 30.0,
        jitter: bool = BACKOFF_JITTER,
    ):
        """Linear backoff - steady increase."""
        return cls(strategy="linear", delay=delay, max_delay=max_delay, jitter=jitter)

    @classmethod
    def fixed(cls, delay: float = 1.0, jitter: bool = BACKOFF_JITTER):
        """Fixed delay - simple constant."""
        return cls(strategy="fixed", delay=delay, jitter=jitter)


class Timeout:
    """Timeout policy for time-based protection."""

    def __init__(self, seconds: float = TIMEOUT_SECONDS):
        self.seconds = seconds
