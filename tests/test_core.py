"""Core tests for Option D implementation - resilient decorators + Result returns."""

import pytest

from resilient_result import Err, Ok, Retry, resilient


class CustomError(Exception):
    """Test custom error type."""

    pass


@pytest.mark.asyncio
async def test_basic_success():
    """Test successful operation returns Ok."""

    @resilient()
    async def success_func():
        return "success"

    result = await success_func()
    assert result.success
    assert result.unwrap() == "success"


@pytest.mark.asyncio
async def test_basic_failure():
    """Test failed operation returns Err with Exception."""

    @resilient()
    async def fail_func():
        raise ValueError("test error")

    result = await fail_func()
    assert not result.success
    assert isinstance(result.error, Exception)
    assert "test error" in str(result.error)


@pytest.mark.asyncio
async def test_custom_error():
    """Test custom error_type parameter."""

    @resilient(error_type=CustomError)
    async def fail_func():
        raise ValueError("original error")

    result = await fail_func()
    assert not result.success
    assert isinstance(result.error, CustomError)
    assert "original error" in str(result.error)


@pytest.mark.asyncio
async def test_result_passthrough():
    """Test functions returning Result pass through unchanged."""

    @resilient()
    async def returns_result():
        return Ok("already wrapped")

    result = await returns_result()
    assert result.success
    assert result.unwrap() == "already wrapped"

    @resilient()
    async def returns_err():
        return Err("already error")

    result = await returns_err()
    assert not result.success
    assert result.error == "already error"


@pytest.mark.asyncio
async def test_handler_contract():
    """Test handler return values control retry behavior."""
    call_count = 0

    async def custom_handler(error: Exception):
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            return None  # Retry
        return False  # Stop retrying

    @resilient(retry=Retry(attempts=3), handler=custom_handler)
    async def fail_func():
        raise ValueError("always fails")

    result = await fail_func()
    assert not result.success
    assert call_count == 2  # Handler called twice, then stopped


def test_sync_support():
    """Test sync function support."""

    @resilient(retry=Retry(attempts=1))
    def sync_func():
        return "sync success"

    result = sync_func()
    assert result.success
    assert result.unwrap() == "sync success"


def test_decorator_syntax():
    """Test @resilient vs @resilient() syntax works."""

    @resilient
    def without_parens():
        return "success"

    @resilient()
    def with_parens():
        return "success"

    assert without_parens().success
    assert with_parens().success


@pytest.mark.asyncio
async def test_static_methods():
    """Test @resilient.* static methods return Result types."""

    @resilient.retry()
    async def retry_func():
        return "retry"

    @resilient.circuit(failures=2, window=60)
    async def circuit_func():
        return "circuit"

    @resilient.rate_limit(rps=100, burst=5)
    async def rate_func():
        return "rate"

    assert (await retry_func()).success
    assert (await circuit_func()).success
    assert (await rate_func()).success
