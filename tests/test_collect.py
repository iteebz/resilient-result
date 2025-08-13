"""Tests for Result.collect() method."""

import pytest

from resilient_result import Err, Ok, Result, resilient


@pytest.mark.asyncio
async def test_collect_success():
    """collect() should succeed when all operations succeed."""

    async def op1():
        return "result1"

    async def op2():
        return "result2"

    async def op3():
        return "result3"

    result = await Result.collect([op1(), op2(), op3()])

    assert result.success
    assert result.unwrap() == ["result1", "result2", "result3"]


@pytest.mark.asyncio
async def test_collect_results():
    """collect() should handle operations that return Result objects."""

    async def success_op():
        return Ok("success_data")

    async def another_success():
        return Ok("more_data")

    result = await Result.collect([success_op(), another_success()])

    assert result.success
    assert result.unwrap() == ["success_data", "more_data"]


@pytest.mark.asyncio
async def test_collect_failure():
    """collect() should fail if any operation fails."""

    async def success_op():
        return "success"

    async def failing_op():
        raise ValueError("operation failed")

    async def another_success():
        return "more success"

    result = await Result.collect([success_op(), failing_op(), another_success()])

    assert result.failure
    assert isinstance(result.error, ValueError)
    assert str(result.error) == "operation failed"


@pytest.mark.asyncio
async def test_collect_result_failure():
    """collect() should handle Result objects that contain failures."""

    async def success_op():
        return Ok("success")

    async def failing_result_op():
        return Err("result error")

    result = await Result.collect([success_op(), failing_result_op()])

    assert result.failure
    assert result.error == "result error"


@pytest.mark.asyncio
async def test_collect_empty():
    """collect() should handle empty operation list."""
    result = await Result.collect([])

    assert result.success
    assert result.unwrap() == []


@pytest.mark.asyncio
async def test_collect_resilient():
    """collect() should work with @resilient decorated functions."""

    @resilient
    async def op1():
        return "data1"

    @resilient
    async def op2():
        return "data2"

    result = await Result.collect([op1(), op2()])

    assert result.success
    assert result.unwrap() == ["data1", "data2"]
