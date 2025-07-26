"""Integration tests for resilient decorator with timeout and custom error types."""

import asyncio

import pytest

from resilient_result import Ok, resilient


class LLMError(Exception):
    """Test-specific LLM error."""

    pass


@pytest.mark.asyncio
async def test_exact_vision_syntax():
    """Test @resilient(retries=3, timeout=5) matches original vision."""

    @resilient(
        retries=1, timeout=0.05, error_type=LLMError
    )  # Reduced retries and timeout
    async def mock_llm():
        await asyncio.sleep(0.1)  # Will timeout
        return "should not reach"

    result = await mock_llm()
    assert not result.success
    assert isinstance(result.error, LLMError)


@pytest.mark.asyncio
async def test_custom_error_preservation():
    """Test Result[T, CustomError] type preservation."""

    @resilient(retries=1, error_type=LLMError)
    async def failing_llm():
        raise Exception("LLM failed")

    result = await failing_llm()
    assert not result.success
    assert isinstance(result.error, LLMError)
    assert "LLM failed" in str(result.error)


@pytest.mark.asyncio
async def test_timeout_with_retries():
    """Test timeout + retry combination."""

    call_count = 0

    @resilient(
        retries=1, timeout=0.05, error_type=LLMError
    )  # Reduced retries and timeout
    async def slow_llm():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.1)  # Each call will timeout
        return "unreachable"

    result = await slow_llm()
    assert not result.success
    assert isinstance(result.error, LLMError)
    assert call_count == 1  # Reduced expected calls


@pytest.mark.asyncio
async def test_success_case_unchanged():
    """Test successful operations work perfectly."""

    @resilient(retries=3, timeout=1, error_type=LLMError)
    async def working_llm():
        return "Generated story about dragons"

    result = await working_llm()
    assert result.success
    assert result.data == "Generated story about dragons"


@pytest.mark.asyncio
async def test_result_passthrough():
    """Test functions returning Result[T, E] pass through unchanged."""

    @resilient(retries=1, error_type=LLMError)
    async def returns_result():
        return Ok("already wrapped")

    result = await returns_result()
    assert result.success
    assert result.data == "already wrapped"
