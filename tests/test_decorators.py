"""Test suite for @resilient decorator."""

import asyncio

import pytest

from resilient_result import Result, resilient


class TestResilientDecorator:
    """Test @resilient decorator functionality."""

    def test_sync_success(self):
        """Test @resilient with successful sync function."""

        @resilient
        def divide(a: int, b: int) -> int:
            return a // b

        result = divide(10, 2)
        assert result.success is True
        assert result.data == 5
        assert result.error is None

    def test_sync_failure(self):
        """Test @resilient with failing sync function."""

        @resilient
        def divide(a: int, b: int) -> int:
            return a // b

        result = divide(10, 0)
        assert result.success is False
        assert result.data is None
        assert "division" in result.error.lower()

    def test_sync_with_exception_types(self):
        """Test @resilient with different exception types."""

        @resilient
        def raise_value_error():
            raise ValueError("Custom value error")

        @resilient
        def raise_type_error():
            raise TypeError("Custom type error")

        @resilient
        def raise_runtime_error():
            raise RuntimeError("Custom runtime error")

        result1 = raise_value_error()
        assert result1.failure is True
        assert "Custom value error" in result1.error

        result2 = raise_type_error()
        assert result2.failure is True
        assert "Custom type error" in result2.error

        result3 = raise_runtime_error()
        assert result3.failure is True
        assert "Custom runtime error" in result3.error

    @pytest.mark.asyncio
    async def test_async_success(self):
        """Test @resilient with successful async function."""

        @resilient
        async def fetch_data(value: str) -> dict:
            await asyncio.sleep(0.01)  # Simulate async work
            return {"data": value}

        result = await fetch_data("test")
        assert result.success is True
        assert result.data == {"data": "test"}
        assert result.error is None

    @pytest.mark.asyncio
    async def test_async_failure(self):
        """Test @resilient with failing async function."""

        @resilient
        async def failing_fetch():
            await asyncio.sleep(0.01)
            raise ConnectionError("Network failed")

        result = await failing_fetch()
        assert result.success is False
        assert result.data is None
        assert "Network failed" in result.error

    def test_return_types(self):
        """Test @resilient with various return types."""

        @resilient
        def return_string() -> str:
            return "hello world"

        @resilient
        def return_dict() -> dict:
            return {"key": "value", "number": 42}

        @resilient
        def return_list() -> list:
            return [1, 2, 3, "four"]

        @resilient
        def return_none() -> None:
            return None

        result1 = return_string()
        assert result1.success is True
        assert result1.data == "hello world"

        result2 = return_dict()
        assert result2.success is True
        assert result2.data == {"key": "value", "number": 42}

        result3 = return_list()
        assert result3.success is True
        assert result3.data == [1, 2, 3, "four"]

        result4 = return_none()
        assert result4.success is True
        assert result4.data is None

    def test_guard_clause_integration(self):
        """Test @resilient with guard clause patterns."""

        @resilient
        def step1(data: str) -> str:
            if not data:
                raise ValueError("Empty data")
            return data.upper()

        @resilient
        def step2(data: str) -> str:
            if len(data) < 3:
                raise ValueError("Data too short")
            return data + "_processed"

        def multi_step_process(input_data: str) -> Result:
            # Step 1
            result1 = step1(input_data)
            if not result1.success:
                return result1

            # Step 2
            result2 = step2(result1.data)
            if not result2.success:
                return result2

            return Result.ok(result2.data + "_complete")

        # Success path
        result = multi_step_process("hello")
        assert result.success is True
        assert result.data == "HELLO_processed_complete"

        # Fail at step 1
        result = multi_step_process("")
        assert result.failure is True
        assert "Empty data" in result.error

        # Fail at step 2
        result = multi_step_process("hi")
        assert result.failure is True
        assert "Data too short" in result.error

    @pytest.mark.asyncio
    async def test_async_guard_clause_integration(self):
        """Test @resilient with async guard clause patterns."""

        @resilient
        async def async_step1(data: str) -> str:
            await asyncio.sleep(0.01)
            if not data:
                raise ValueError("Empty data")
            return data.upper()

        @resilient
        async def async_step2(data: str) -> str:
            await asyncio.sleep(0.01)
            if len(data) < 3:
                raise ValueError("Data too short")
            return data + "_processed"

        async def async_multi_step_process(input_data: str) -> Result:
            # Step 1
            result1 = await async_step1(input_data)
            if not result1.success:
                return result1

            # Step 2
            result2 = await async_step2(result1.data)
            if not result2.success:
                return result2

            return Result.ok(result2.data + "_complete")

        # Success path
        result = await async_multi_step_process("hello")
        assert result.success is True
        assert result.data == "HELLO_processed_complete"

        # Fail at step 1
        result = await async_multi_step_process("")
        assert result.failure is True
        assert "Empty data" in result.error

    def test_preserves_function_metadata(self):
        """Test that @resilient preserves function metadata."""

        @resilient
        def documented_function(x: int, y: int) -> int:
            """Add two numbers together."""
            return x + y

        assert documented_function.__name__ == "documented_function"
        assert "Add two numbers together" in documented_function.__doc__

    @pytest.mark.asyncio
    async def test_preserves_async_metadata(self):
        """Test that @resilient preserves async function metadata."""

        @resilient
        async def async_documented_function(x: int) -> int:
            """Multiply by 2 asynchronously."""
            await asyncio.sleep(0.01)
            return x * 2

        assert async_documented_function.__name__ == "async_documented_function"
        assert "Multiply by 2 asynchronously" in async_documented_function.__doc__


class TestRealWorldPatterns:
    """Test realistic usage patterns."""

    def test_api_client_pattern(self):
        """Test typical API client usage."""

        @resilient
        def fetch_user(user_id: int) -> dict:
            if user_id <= 0:
                raise ValueError("Invalid user ID")
            if user_id == 404:
                raise RuntimeError("User not found")
            return {"id": user_id, "name": f"User{user_id}"}

        @resilient
        def fetch_user_posts(user_id: int) -> list:
            if user_id <= 0:
                raise ValueError("Invalid user ID")
            return [{"id": 1, "title": "Post 1"}, {"id": 2, "title": "Post 2"}]

        def get_user_with_posts(user_id: int) -> Result:
            # Fetch user
            user_result = fetch_user(user_id)
            if not user_result.success:
                return user_result

            # Fetch posts
            posts_result = fetch_user_posts(user_id)
            if not posts_result.success:
                return posts_result

            # Combine data
            combined_data = {"user": user_result.data, "posts": posts_result.data}
            return Result.ok(combined_data)

        # Success case
        result = get_user_with_posts(123)
        assert result.success is True
        assert result.data["user"]["id"] == 123
        assert len(result.data["posts"]) == 2

        # User fetch failure
        result = get_user_with_posts(0)
        assert result.failure is True
        assert "Invalid user ID" in result.error

        # User not found
        result = get_user_with_posts(404)
        assert result.failure is True
        assert "User not found" in result.error

    def test_file_processing_pattern(self):
        """Test file processing usage pattern."""

        @resilient
        def read_config(filename: str) -> dict:
            if not filename.endswith(".json"):
                raise ValueError("Only JSON files supported")
            if filename == "missing.json":
                raise FileNotFoundError("File not found")
            return {"setting1": "value1", "setting2": "value2"}

        @resilient
        def validate_config(config: dict) -> dict:
            required_keys = ["setting1", "setting2"]
            for key in required_keys:
                if key not in config:
                    raise ValueError(f"Missing required setting: {key}")
            return config

        def load_validated_config(filename: str) -> Result:
            # Read config
            config_result = read_config(filename)
            if not config_result.success:
                return config_result

            # Validate config
            validated_result = validate_config(config_result.data)
            if not validated_result.success:
                return validated_result

            return Result.ok(validated_result.data)

        # Success case
        result = load_validated_config("config.json")
        assert result.success is True
        assert result.data["setting1"] == "value1"

        # Wrong file type
        result = load_validated_config("config.txt")
        assert result.failure is True
        assert "Only JSON files supported" in result.error

        # Missing file
        result = load_validated_config("missing.json")
        assert result.failure is True
        assert "File not found" in result.error
