"""Tests for @resilient alias functionality."""

import pytest

from resilient_result import resilient


class TestResilientAlias:
    """Test @resilient alias functionality."""

    @pytest.mark.asyncio
    async def test_resilient_without_parens(self):
        """@resilient should work without parentheses."""

        @resilient
        async def simple_function():
            return "success"

        result = await simple_function()
        assert result.success
        assert result.data == "success"

    @pytest.mark.asyncio
    async def test_resilient_with_parens(self):
        """@resilient() should work with parentheses."""

        @resilient()
        async def simple_function():
            return "success"

        result = await simple_function()
        assert result.success
        assert result.data == "success"

    @pytest.mark.asyncio
    async def test_resilient_with_params(self):
        """@resilient(retries=5) should work with parameters."""

        call_count = 0

        @resilient(retries=2)
        async def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        result = await failing_function()
        assert result.failure
        assert call_count == 2

    def test_resilient_sync_without_parens(self):
        """@resilient should work with sync functions without parentheses."""

        @resilient
        def simple_sync_function():
            return "sync_success"

        result = simple_sync_function()
        assert result.success
        assert result.data == "sync_success"
