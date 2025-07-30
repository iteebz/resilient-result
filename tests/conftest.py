"""Shared fixtures for resilient-result tests."""

import asyncio

import pytest

from resilient_result import Backoff, Retry, resilient


@pytest.fixture
def call_counter():
    """Reusable call counter fixture."""

    class Counter:
        def __init__(self):
            self.count = 0

        def increment(self):
            self.count += 1
            return self.count

        def reset(self):
            self.count = 0

    return Counter()


@pytest.fixture
def fast_retry():
    """Fast retry policy for tests."""
    return Retry(attempts=2)


@pytest.fixture
def fast_backoff():
    """Fast backoff for tests."""
    return Backoff.fixed(delay=0.001)


@pytest.fixture
def test_policies(fast_retry, fast_backoff):
    """Combined fast policies for testing."""
    return {"retry": fast_retry, "backoff": fast_backoff}


@pytest.fixture
def failing_func(call_counter):
    """Function that fails on first call, succeeds on second."""

    @resilient()
    async def func():
        count = call_counter.increment()
        if count < 2:
            raise ValueError("Test error")
        return "success"

    return func


@pytest.fixture
def always_failing_func():
    """Function that always fails."""

    @resilient()
    async def func():
        raise ValueError("Always fails")

    return func


@pytest.fixture
def simple_success_func():
    """Function that always succeeds."""

    @resilient()
    async def func():
        return "success"

    return func


@pytest.fixture
def slow_func():
    """Function that takes time (for timeout tests)."""

    @resilient()
    async def func():
        await asyncio.sleep(0.1)
        return "too slow"

    return func
