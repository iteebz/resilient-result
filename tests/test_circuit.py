"""Test circuit breaker for runaway protection."""

import asyncio

import pytest

from resilient_result.circuit import circuit


@pytest.mark.asyncio
async def test_opens_after_failures(call_counter, always_failing_func):
    """Circuit opens after max failures."""

    @circuit(failures=2, window=60)
    async def func():
        call_counter.increment()
        raise ValueError("fail")

    # Two failures
    result1 = await func()
    assert result1.failure
    assert isinstance(result1.error, ValueError)

    result2 = await func()
    assert result2.failure
    assert isinstance(result2.error, ValueError)

    # Third call - circuit open
    result = await func()
    assert result.failure
    assert "Circuit breaker open" in str(result.error)


@pytest.mark.asyncio
async def test_resets_after_window(call_counter):
    """Circuit resets after time window."""

    @circuit(failures=1, window=0.1)
    async def func():
        count = call_counter.increment()
        if count == 1:
            raise ValueError("fail")
        return "success"

    # Fail and open circuit
    result1 = await func()
    assert result1.failure
    assert isinstance(result1.error, ValueError)

    result = await func()
    assert result.failure
    assert "Circuit breaker open" in str(result.error)

    # Wait and retry
    await asyncio.sleep(0.11)
    result = await func()
    assert result.success
    assert result.data == "success"


@pytest.mark.asyncio
async def test_isolation():
    """Circuits isolate per function."""

    @circuit(failures=1, window=60)
    async def func_a():
        raise ValueError("fail")

    @circuit(failures=1, window=60)
    async def func_b():
        return "success"

    # A fails and opens
    result_a1 = await func_a()
    assert result_a1.failure
    assert isinstance(result_a1.error, ValueError)

    result_a = await func_a()
    assert result_a.failure
    assert "Circuit breaker open" in str(result_a.error)

    # B still works
    result_b = await func_b()
    assert result_b.is_ok()
    assert result_b.unwrap() == "success"


@pytest.mark.asyncio
async def test_success_doesnt_trigger(call_counter):
    """Success calls don't trigger circuit."""

    @circuit(failures=2, window=60)
    async def func():
        count = call_counter.increment()
        if count in [1, 3]:  # Fail on 1st and 3rd
            raise ValueError("fail")
        return f"success {count}"

    # Fail, succeed, fail - should still work
    result1 = await func()
    assert result1.is_err()

    result2 = await func()
    assert result2.is_ok()
    assert result2.unwrap() == "success 2"

    result3 = await func()
    assert result3.is_err()

    # 4th call should work (only 2 failures)
    result4 = await func()
    assert result4.is_ok()
    assert result4.unwrap() == "success 4"
