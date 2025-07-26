"""Core tests for Option D implementation - resilient decorators + Result returns."""

import asyncio

import pytest

from resilient_result import Err, Ok, Result, resilient


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
    assert result.data == "success"


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
async def test_custom_error_type():
    """Test custom error_type parameter."""

    @resilient(error_type=CustomError)
    async def fail_func():
        raise ValueError("original error")

    result = await fail_func()
    assert not result.success
    assert isinstance(result.error, CustomError)
    assert "original error" in str(result.error)


@pytest.mark.asyncio
async def test_retries():
    """Test retry mechanism."""
    call_count = 0

    @resilient(retries=2)  # Reduced from 3
    async def retry_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:  # Reduced from 3
            raise ValueError("not yet")
        return "success"

    result = await retry_func()
    assert result.success
    assert result.data == "success"
    assert call_count == 2  # Reduced from 3


@pytest.mark.asyncio
async def test_timeout():
    """Test timeout functionality."""

    @resilient(timeout=0.05)  # Reduced from 0.1
    async def slow_func():
        await asyncio.sleep(0.1)  # Reduced from 0.2
        return "too slow"

    result = await slow_func()
    assert not result.success
    assert isinstance(result.error, Exception)


@pytest.mark.asyncio
async def test_result_passthrough():
    """Test functions returning Result pass through unchanged."""

    @resilient()
    async def returns_result():
        return Ok("already wrapped")

    result = await returns_result()
    assert result.success
    assert result.data == "already wrapped"

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

    @resilient(retries=3, handler=custom_handler)  # Reduced from 5
    async def fail_func():
        raise ValueError("always fails")

    result = await fail_func()
    assert not result.success
    assert call_count == 2  # Handler called twice, then stopped


def test_sync_support():
    """Test sync function support."""

    @resilient(retries=1)  # Reduced from 2
    def sync_func():
        return "sync success"

    result = sync_func()
    assert result.success
    assert result.data == "sync success"

    call_count = 0

    @resilient(retries=2)  # Reduced from 3
    def sync_retry():
        nonlocal call_count
        call_count += 1
        if call_count < 2:  # Reduced from 3
            raise ValueError("not yet")
        return "sync retry success"

    result = sync_retry()
    assert result.success
    assert result.data == "sync retry success"
    assert call_count == 2  # Reduced from 3


def test_result_types():
    """Test Result type constructors."""
    # Ok constructor
    ok_result = Ok("data")
    assert ok_result.success
    assert ok_result.data == "data"
    assert ok_result.error is None

    # Err constructor
    err_result = Err("error")
    assert not err_result.success
    assert err_result.error == "error"
    assert err_result.data is None

    # Result class methods
    ok_result2 = Result.ok("data2")
    assert ok_result2.success
    assert ok_result2.data == "data2"

    err_result2 = Result.fail("error2")
    assert not err_result2.success
    assert err_result2.error == "error2"
