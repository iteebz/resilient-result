"""Test token bucket rate limiting."""

import time

import pytest

from resilient_result.rate_limit import rate_limit


@pytest.mark.asyncio
async def test_enforces_rate():
    """Rate limiting enforces RPS."""

    @rate_limit(rps=50.0, burst=1)
    async def func():
        return time.time()

    start = time.time()
    for _ in range(3):
        await func()
    elapsed = time.time() - start

    assert elapsed >= 0.020
    assert elapsed < 0.08


@pytest.mark.asyncio
async def test_burst():
    """Burst allows rapid initial calls."""

    @rate_limit(rps=25.0, burst=3)
    async def func():
        return time.time()

    # First 3 immediate
    start = time.time()
    for _ in range(3):
        await func()
    burst_time = time.time() - start
    assert burst_time < 0.01

    # 4th waits
    fourth_start = time.time()
    await func()
    fourth_time = time.time() - fourth_start
    assert fourth_time >= 0.035


@pytest.mark.asyncio
async def test_isolation():
    """Rate limits isolate per function."""

    @rate_limit(rps=50.0, burst=1)
    async def func_a():
        return "A"

    @rate_limit(rps=50.0, burst=1)
    async def func_b():
        return "B"

    # A gets rate limited
    await func_a()
    start_a = time.time()
    await func_a()
    elapsed_a = time.time() - start_a

    # B still fast
    start_b = time.time()
    result_b = await func_b()
    elapsed_b = time.time() - start_b

    assert elapsed_a >= 0.015
    assert elapsed_b < 0.005
    assert result_b.success
    assert result_b.data == "B"


@pytest.mark.asyncio
async def test_custom_key():
    """Custom key shares rate limit."""

    @rate_limit(rps=50.0, burst=1, key="shared")
    async def func_x():
        return "X"

    @rate_limit(rps=50.0, burst=1, key="shared")
    async def func_y():
        return "Y"

    # X consumes token
    await func_x()
    start = time.time()

    # Y rate limited (shared key)
    result = await func_y()
    elapsed = time.time() - start

    assert elapsed >= 0.015
    assert result.success
    assert result.data == "Y"
