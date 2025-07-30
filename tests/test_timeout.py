"""Lean tests for timeout pattern."""

import asyncio

import pytest

from resilient_result import Ok, timeout


def test_sync_timeout_success():
    @timeout(1.0)
    def fast():
        return "success"

    result = fast()
    assert result == Ok("success")


def test_sync_timeout_error():
    @timeout(1.0)
    def failing():
        raise ValueError("boom")

    result = failing()
    assert result.failure
    assert "boom" in str(result.error)


@pytest.mark.asyncio
async def test_async_timeout_success():
    @timeout(1.0)
    async def fast():
        await asyncio.sleep(0.1)
        return "success"

    result = await fast()
    assert result == Ok("success")


@pytest.mark.asyncio
async def test_async_timeout_exceeded():
    @timeout(0.1)
    async def slow():
        await asyncio.sleep(0.2)
        return "never"

    result = await slow()
    assert result.failure
    assert "Timeout after 0.1s" in str(result.error)


@pytest.mark.asyncio
async def test_async_timeout_error():
    @timeout(1.0)
    async def failing():
        raise ValueError("boom")

    result = await failing()
    assert result.failure
    assert "boom" in str(result.error)
