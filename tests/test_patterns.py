"""Test mechanism-focused resilience patterns."""

import pytest

from resilient_result import Retry, RetryError, resilient, retry


@pytest.mark.asyncio
async def test_retry_exhausted():
    """Test retry exhaustion returns RetryError."""

    @retry(attempts=2, error_type=RetryError)
    async def always_fails():
        raise ValueError("always fails")

    result = await always_fails()
    assert not result.success
    assert isinstance(result.error, RetryError)


@pytest.mark.asyncio
async def test_composition_patterns():
    """Test composing decorators with stacking."""
    from resilient_result import timeout

    @timeout(seconds=1.0)
    @retry(attempts=2)
    async def complex_operation():
        return "composed success"

    result = await complex_operation()
    assert result.success
    assert result.unwrap() == "composed success"


@pytest.mark.asyncio
async def test_resilient_basic():
    """Test basic resilient decorator."""

    @resilient()  # Basic retry pattern
    async def api_call():
        return "api success"

    result = await api_call()
    assert result.success
    assert result.unwrap() == "api success"


@pytest.mark.asyncio
async def test_policy_based_retry():
    """Test policy-based retry configuration."""

    @resilient(retry=Retry(attempts=5))  # Explicit configuration
    async def db_operation():
        return {"data": "from_database"}

    result = await db_operation()
    assert result.success
    assert result.unwrap() == {"data": "from_database"}
