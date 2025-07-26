"""Test registry system and built-in patterns."""

import pytest

from resilient_result import NetworkError, ParsingError, resilient


@pytest.mark.asyncio
async def test_network_pattern():
    """Test @resilient.network built-in pattern."""

    @resilient.network(retries=2)
    async def network_call():
        raise ConnectionError("network timeout")

    result = await network_call()
    assert not result.success
    assert isinstance(result.error, NetworkError)


@pytest.mark.asyncio
async def test_parsing_pattern():
    """Test @resilient.parsing built-in pattern."""

    @resilient.parsing(retries=2)
    async def parse_data():
        raise ValueError("invalid json")

    result = await parse_data()
    assert not result.success
    assert isinstance(result.error, ParsingError)


@pytest.mark.asyncio
async def test_custom_registry():
    """Test custom pattern registration."""

    class DatabaseError(Exception):
        pass

    async def db_handler(error: Exception):
        if "deadlock" in str(error):
            return None  # Retry deadlocks
        return False  # Don't retry other errors

    from resilient_result.resilient import decorator

    resilient.register(
        "database",
        lambda retries=3, **kwargs: decorator(
            handler=db_handler, retries=retries, error_type=DatabaseError, **kwargs
        ),
    )

    @resilient.database(retries=2)
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
async def test_direct_network_import():
    """Test direct network pattern import."""
    from resilient_result import network

    @network(retries=1)
    async def network_call():
        raise ConnectionError("timeout")

    result = await network_call()
    assert not result.success


@pytest.mark.asyncio
async def test_direct_parsing_import():
    """Test direct parsing pattern import."""
    from resilient_result import parsing

    @parsing(retries=1)
    async def parse_call():
        raise ValueError("invalid json")

    result = await parse_call()
    assert not result.success
