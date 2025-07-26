"""Test decorator syntax variations."""

import pytest

from resilient_result import resilient


@pytest.mark.asyncio
async def test_bare_decorator():
    """Test @resilient without parentheses."""

    @resilient
    async def simple_func():
        return "works"

    result = await simple_func()
    assert result.success
    assert result.data == "works"


@pytest.mark.asyncio
async def test_parameterized_decorator():
    """Test @resilient(retries=3, timeout=5) syntax."""

    @resilient(retries=2, timeout=1)
    async def param_func():
        return "configured"

    result = await param_func()
    assert result.success
    assert result.data == "configured"


@pytest.mark.asyncio
async def test_plugin_syntax():
    """Test @resilient.network syntax."""

    @resilient.network()
    async def network_func():
        return "network call"

    result = await network_func()
    assert result.success
    assert result.data == "network call"


@pytest.mark.asyncio
async def test_circuit_syntax():
    """Test @resilient.circuit syntax."""

    @resilient.circuit(failures=2, window=60)
    async def circuit_func():
        return "circuit call"

    result = await circuit_func()
    assert result.success  # Now returns Result type
    assert result.data == "circuit call"


@pytest.mark.asyncio
async def test_rate_limit_syntax():
    """Test @resilient.rate_limit syntax."""

    @resilient.rate_limit(rps=100, burst=5)
    async def rate_func():
        return "rate limited call"

    result = await rate_func()
    assert result.success  # Now returns Result type
    assert result.data == "rate limited call"
