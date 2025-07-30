"""Lean tests for pattern composition."""

import asyncio

import pytest

from resilient_result import Ok, circuit, compose, rate_limit, retry, timeout


@pytest.mark.asyncio
async def test_compose_timeout_retry():
    @compose(timeout(0.5), retry(2))
    async def flaky():
        if not hasattr(flaky, "calls"):
            flaky.calls = 0
        flaky.calls += 1
        if flaky.calls == 1:
            raise ValueError("first fail")
        await asyncio.sleep(0.1)
        return "success"

    result = await flaky()
    assert result == Ok("success")
    assert flaky.calls == 2


@pytest.mark.asyncio
async def test_compose_all_patterns():
    @compose(
        circuit(failures=2, window=60), rate_limit(rps=10.0), timeout(1.0), retry(3)
    )
    async def protected():
        return "success"

    result = await protected()
    assert result == Ok("success")
