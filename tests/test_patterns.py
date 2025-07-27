"""Test built-in patterns with v0.2.3 policy API."""

import pytest

from resilient_result import NetworkError, ParsingError, Retry, resilient


@pytest.mark.asyncio
async def test_network_pattern():
    """Test @resilient.network built-in pattern."""

    @resilient.network()
    async def network_call():
        raise ConnectionError("network timeout")

    result = await network_call()
    assert not result.success
    assert isinstance(result.error, NetworkError)


@pytest.mark.asyncio
async def test_parsing_pattern():
    """Test @resilient.parsing built-in pattern."""

    @resilient.parsing()
    async def parse_data():
        raise ValueError("invalid json")

    result = await parse_data()
    assert not result.success
    assert isinstance(result.error, ParsingError)


@pytest.mark.asyncio
async def test_custom_registry():
    """Test custom pattern registration with policy API."""

    class DatabaseError(Exception):
        pass

    async def db_handler(error: Exception):
        if "deadlock" in str(error):
            return None  # Retry deadlocks
        return False  # Don't retry other errors

    from resilient_result.resilient import decorator

    resilient.register(
        "database",
        lambda retry=None, **kwargs: decorator(
            handler=db_handler,
            retry=retry or Retry.db(),
            error_type=DatabaseError,
            **kwargs,
        ),
    )

    @resilient.database()
    async def db_operation():
        raise Exception("database deadlock detected")

    result = await db_operation()
    assert not result.success
    assert isinstance(result.error, DatabaseError)


@pytest.mark.asyncio
async def test_registry_error_handling():
    """Test registry error handling for unknown patterns."""
    try:
        resilient.unknown_plugin()
        raise AssertionError("Should have raised AttributeError")
    except AttributeError as e:
        assert "unknown_plugin" in str(e)
        assert "Available:" in str(e)


@pytest.mark.asyncio
async def test_direct_pattern_imports():
    """Test direct pattern imports with v0.2.3 API."""
    from resilient_result import network, parsing

    @network()
    async def network_call():
        raise ConnectionError("timeout")

    @parsing()
    async def parse_call():
        raise ValueError("invalid json")

    net_result = await network_call()
    parse_result = await parse_call()

    assert not net_result.success
    assert not parse_result.success
