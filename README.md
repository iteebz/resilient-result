# resilient-result

[![PyPI version](https://badge.fury.io/py/resilient-result.svg)](https://badge.fury.io/py/resilient-result)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Clean error handling with Result pattern and `@resilient` decorators that convert exceptions to Results for both sync and async functions, with full generic typing support.

## Installation

```bash
pip install resilient-result
```

## Quick Start

```python
from resilient_result import Result, resilient

# Basic Result usage
def divide_safely(a: int, b: int) -> Result[int, str]:
    if b == 0:
        return Result.fail("Cannot divide by zero")
    return Result.ok(a // b)

result = divide_safely(10, 2)
if result.success:
    print(f"Result: {result.data}")  # Result: 5
else:
    print(f"Error: {result.error}")

# @resilient decorator converts exceptions to Results
@resilient
def divide(a: int, b: int) -> int:
    return a // b

result = divide(10, 0)  # Returns Result.fail("integer division or modulo by zero")
if not result.success:
    print(f"Division failed: {result.error}")
```

## Core Concepts

### Result Pattern

The `Result` type represents either success (`Result.ok(data)`) or failure (`Result.fail(error)`):

```python
from resilient_result import Result

# Create results
success = Result.ok("data")
failure = Result.fail("error message")

# Check status
if success.success:  # True
    print(success.data)  # "data"

if failure.failure:  # True  
    print(failure.error)  # "error message"

# Boolean evaluation
if success:  # True (success)
    print("Operation succeeded")

if not failure:  # True (failure)
    print("Operation failed")
```

### Guard Clause Pattern

Use guard clauses for clean early returns:

```python
def multi_step_process(data: str) -> Result[str, str]:
    # Step 1
    step1_result = process_step1(data)
    if not step1_result.success:
        return step1_result  # Early return on failure
    
    # Step 2  
    step2_result = process_step2(step1_result.data)
    if not step2_result.success:
        return step2_result  # Early return on failure
        
    # Success path
    return Result.ok(step2_result.data + "_complete")
```

### @resilient Decorator

Convert exception-throwing functions to Result-returning functions:

```python
from resilient_result import resilient

@resilient
def risky_operation(value: str) -> dict:
    if not value:
        raise ValueError("Empty value not allowed")
    return {"processed": value.upper()}

# Usage
result = risky_operation("")  # Result.fail("Empty value not allowed")
result = risky_operation("hello")  # Result.ok({"processed": "HELLO"})

# Works with async functions too
@resilient  
async def async_operation() -> str:
    # ... async work that might raise
    return "success"

result = await async_operation()  # Returns Result
```

## Rust-Style Aliases

For Rust developers, familiar `Ok` and `Err` constructors are available:

```python
from resilient_result import Ok, Err

success = Ok("data")  # Same as Result.ok("data")
failure = Err("error")  # Same as Result.fail("error")
```

## Real-World Example

```python
from resilient_result import resilient, Result

@resilient
def fetch_user(user_id: int) -> dict:
    if user_id <= 0:
        raise ValueError("Invalid user ID")
    # Simulate API call that might fail
    return {"id": user_id, "name": f"User{user_id}"}

@resilient
def fetch_user_posts(user_id: int) -> list:
    if user_id <= 0:
        raise ValueError("Invalid user ID") 
    return [{"title": "Post 1"}, {"title": "Post 2"}]

def get_user_profile(user_id: int) -> Result[dict, str]:
    # Fetch user - early return on failure
    user_result = fetch_user(user_id)
    if not user_result.success:
        return user_result
    
    # Fetch posts - early return on failure  
    posts_result = fetch_user_posts(user_id)
    if not posts_result.success:
        return posts_result
    
    # Combine successful results
    profile = {
        "user": user_result.data,
        "posts": posts_result.data
    }
    return Result.ok(profile)

# Usage
profile_result = get_user_profile(123)
if profile_result.success:
    print(f"User: {profile_result.data['user']['name']}")
    print(f"Posts: {len(profile_result.data['posts'])}")
else:
    print(f"Failed to load profile: {profile_result.error}")
```

## Why resilient-result?

- **Clean Error Handling**: No more try/catch blocks everywhere
- **Explicit Error States**: Errors are part of the type system
- **Composable**: Chain operations with early returns on failure  
- **Readable**: Guard clauses make success/failure paths obvious
- **Zero Dependencies**: Lightweight with no external dependencies
- **Type Safe**: Full type hints for better IDE support

## License

MIT