"""Tests for nested Result flattening - clean boundary discipline."""

import pytest

from resilient_result import Err, Ok, Result, resilient


def test_no_nesting():
    """Test flatten on non-nested Result."""
    result = Ok("data")
    flattened = result.flatten()
    assert flattened.success
    assert flattened.data == "data"


def test_single_level_success():
    """Test flatten on single-level nested Ok Result."""
    nested = Ok(Ok("inner_data"))
    flattened = nested.flatten()
    assert flattened.success
    assert flattened.data == "inner_data"


def test_single_level_failure():
    """Test flatten when inner Result is Err."""
    nested = Ok(Err("inner_error"))
    flattened = nested.flatten()
    assert not flattened.success
    assert flattened.error == "inner_error"


def test_multiple_levels():
    """Test flatten on deeply nested Results."""
    deeply_nested = Ok(Ok(Ok("deep_data")))
    flattened = deeply_nested.flatten()
    assert flattened.success
    assert flattened.data == "deep_data"


def test_outer_failure():
    """Test flatten when outer Result is already failed."""
    failed = Err("outer_error")
    flattened = failed.flatten()
    assert not flattened.success
    assert flattened.error == "outer_error"


def test_mixed_nesting():
    """Test flatten with mixed success/failure nesting."""
    # Outer Ok, inner Err should become Err
    mixed = Ok(Err("inner_failure"))
    flattened = mixed.flatten()
    assert not flattened.success
    assert flattened.error == "inner_failure"


def test_preserves_non_result():
    """Test flatten doesn't affect non-Result data."""
    result = Ok({"key": "value"})
    flattened = result.flatten()
    assert flattened.success
    assert flattened.data == {"key": "value"}


# Test @resilient decorator automatically flattens nested Results


@pytest.mark.asyncio
async def test_async_nested_ok():
    """Test async function returning nested Ok gets flattened."""

    @resilient()
    async def returns_nested_ok():
        return Ok("inner_data")  # This gets wrapped in another Ok by decorator

    result = await returns_nested_ok()
    assert result.success
    assert result.data == "inner_data"
    # Verify no nested Result structure
    assert not isinstance(result.data, Result)


@pytest.mark.asyncio
async def test_async_nested_err():
    """Test async function returning Err gets flattened properly."""

    @resilient()
    async def returns_err():
        return Err("error_data")

    result = await returns_err()
    assert not result.success
    assert result.error == "error_data"


@pytest.mark.asyncio
async def test_deep_nesting():
    """Test deeply nested Results get completely flattened."""

    @resilient()
    async def returns_deeply_nested():
        # Simulates calling multiple Result-returning functions
        inner_result = Ok("final_data")
        middle_result = Ok(inner_result)
        return middle_result  # Creates Ok(Ok(Ok("final_data")))

    result = await returns_deeply_nested()
    assert result.success
    assert result.data == "final_data"
    assert not isinstance(result.data, Result)


def test_sync_nested():
    """Test sync function nested Result flattening."""

    @resilient()
    def returns_nested_sync():
        return Ok("sync_data")

    result = returns_nested_sync()
    assert result.success
    assert result.data == "sync_data"
    assert not isinstance(result.data, Result)


@pytest.mark.asyncio
async def test_error_inside_nested_result():
    """Test error handling with nested Results."""

    @resilient()
    async def returns_nested_error():
        # Simulate a function that returns Result.fail()
        return Err("nested_error")

    result = await returns_nested_error()
    assert not result.success
    assert result.error == "nested_error"


@pytest.mark.asyncio
async def test_boundary_discipline():
    """Test real-world boundary discipline scenario."""

    # Simulate parse_json function that returns Result
    def parse_json(text: str) -> Result[dict, str]:
        try:
            import json

            return Ok(json.loads(text))
        except Exception as e:
            return Err(e)

    # Simulate LLM function that returns Result
    async def llm_call(prompt: str) -> Result[str, str]:
        return Ok('{"key": "value"}')  # Mock JSON response

    @resilient()
    async def preprocess_function():
        # This is the clean boundary discipline pattern
        llm_response = await llm_call("test prompt")  # Returns Result
        if not llm_response.success:
            return llm_response  # Pass through error

        parsed_data = parse_json(llm_response.data)  # Returns Result
        if not parsed_data.success:
            return parsed_data  # Pass through error

        return parsed_data  # Return the final Result

    result = await preprocess_function()
    assert result.success
    assert result.data == {"key": "value"}
    assert not isinstance(result.data, Result)
