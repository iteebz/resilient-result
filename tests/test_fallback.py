"""Tests for @resilient.fallback() pattern."""

import pytest

from resilient_result import resilient


class TestResilientFallback:
    """Test @resilient.fallback() pattern."""

    @pytest.mark.asyncio
    async def test_fallback_pattern(self):
        """fallback() should switch modes on error."""

        class MockState:
            def __init__(self):
                self.react_mode = "deep"

        call_count = 0

        @resilient.fallback("react_mode", "fast", retries=2)
        async def failing_function(state):
            nonlocal call_count
            call_count += 1

            if state.react_mode == "deep" and call_count == 1:
                raise ValueError("Deep mode failed")

            return f"Success in {state.react_mode} mode"

        state = MockState()
        result = await failing_function(state)

        # Should have switched to fast mode and succeeded
        assert state.react_mode == "fast"
        assert result.success
        assert result.data == "Success in fast mode"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_fallback_no_attribute(self):
        """fallback() should handle cases where attribute doesn't exist."""

        class MockState:
            pass

        @resilient.fallback("nonexistent_attr", "fast", retries=2)
        async def failing_function(state):
            raise ValueError("Always fails")

        state = MockState()

        # Should fail since no attribute to switch
        result = await failing_function(state)
        assert result.failure
        assert "Always fails" in str(result.error)

    @pytest.mark.asyncio
    async def test_fallback_with_different_attributes(self):
        """fallback() should work with different attribute names."""

        class MockConfig:
            def __init__(self):
                self.complexity = "advanced"

        @resilient.fallback("complexity", "simple", retries=2)
        async def adaptive_processing(config):
            if config.complexity == "advanced":
                raise ValueError("Too complex")
            return f"Processed with {config.complexity} mode"

        config = MockConfig()
        result = await adaptive_processing(config)

        assert config.complexity == "simple"
        assert result.success
        assert result.data == "Processed with simple mode"
