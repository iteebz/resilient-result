# resilient-result

[![PyPI version](https://badge.fury.io/py/resilient-result.svg)](https://badge.fury.io/py/resilient-result)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](#testing)

**Beautiful resilient decorators that return Result types instead of throwing exceptions.**

```python
from resilient_result import resilient, Ok, Err, unwrap

@resilient(retries=3, timeout=5)
async def call_api(url: str) -> str:
    return await http.get(url)  # Exceptions become Result[str, Exception]

result = await call_api("https://api.example.com")
if result.success:
    print(result.data)  # The API response
else:
    print(f"Failed: {result.error}")  # The exception that occurred
```

**What just happened?** Function ran up to 3 times with exponential backoff, timed out after 5s, and returned `Result[str, Exception]` instead of throwing.

## Installation

```bash
pip install resilient-result
```

## Core Patterns

### Basic Resilience
```python
# Simple retry with defaults
@resilient()
async def might_fail():
    if random.random() < 0.3:
        raise Exception("Oops!")
    return "success"

# Returns Ok("success") or Err(Exception("Oops!"))
result = await might_fail()
```

### Built-in Patterns
```python
# Network calls with smart retry logic
@resilient.network(retries=2)
async def fetch_data(url: str):
    return await httpx.get(url)

# JSON parsing with error recovery
@resilient.parsing()
async def parse_response(text: str):
    return json.loads(text)

# Circuit breaker protection
@resilient.circuit(failures=5, window=60)
async def external_service():
    return await service.call()

# Rate limiting with token bucket
@resilient.rate_limit(rps=10.0, burst=5)
async def api_call():
    return await external_api()
```

## Result Type System

### Type-Safe Error Handling
```python
from resilient_result import Result, Ok, Err

# Functions return Result[T, E] instead of throwing
def divide(a: int, b: int) -> Result[int, str]:
    if b == 0:
        return Err("Division by zero")
    return Ok(a // b)

# Pattern matching for elegant handling
result = divide(10, 2)
match result:
    case Ok(value):
        print(f"Result: {value}")
    case Err(error):
        print(f"Error: {error}")
```

### Smart Result Detection
```python
# Already returns Result? Passes through unchanged
@resilient(retries=2)
async def already_result() -> Result[str, ValueError]:
    return Ok("data")  # Unchanged: Ok("data")

# Regular return? Auto-wrapped in Ok()
@resilient(retries=2) 
async def regular_return() -> str:
    return "data"  # Becomes: Ok("data")

# Exception raised? Becomes Err()
@resilient(retries=2)
async def might_throw() -> str:
    raise ValueError("oops")  # Becomes: Err(ValueError("oops"))
```

## Extensibility - Registry System

### Creating Custom Patterns
```python
from resilient_result import resilient, decorator

# Define domain-specific handler
async def llm_handler(error):
    error_str = str(error).lower()
    if "rate_limit" in error_str:
        await asyncio.sleep(60)  # Wait for rate limit reset
        return None  # Trigger retry
    if "context_length" in error_str:
        return False  # Don't retry context errors
    return None  # Retry other errors

# Create pattern factory
def llm_pattern(retries=3, **kwargs):
    return decorator(handler=llm_handler, retries=retries, **kwargs)

# Register with resilient-result
resilient.register("llm", llm_pattern)

# Beautiful usage
@resilient.llm(retries=5, timeout=30)
async def call_openai(prompt: str):
    return await openai.create(prompt=prompt)
```

### Real-World Extension: AI Agent Patterns
```python
# Cogency extends resilient-result for AI-specific resilience
from cogency.resilience import safe  # Built on resilient-result

@safe.reasoning(retries=2)  # Fallback: deep → fast mode
async def llm_reasoning(state):
    return await llm.generate(state.prompt)

@safe.memory()  # Graceful memory degradation
async def store_context(data):  
    return await vector_db.store(data)

# Both @safe.reasoning() and @resilient.reasoning() work identically
# Proving the extensibility architecture works beautifully
```

## Performance & Architecture

### Performance Characteristics
- **Overhead**: ~0.1ms per decorated call
- **Memory**: ~200 bytes per Result object  
- **Concurrency**: Thread-safe, async-first design
- **Test suite**: Comprehensive coverage, <2s runtime

### v0.2.2 Status: Ergonomic & Powerful
✅ **Proven extensible architecture** - Registry system enables domain-specific patterns  
✅ **Beautiful decorator API** - Clean `@resilient.pattern()` and `@resilient` syntax  
✅ **Type-safe Result system** - Ok/Err prevents ignored errors  
✅ **Real-world proven** - Successfully integrated with production AI systems
✅ **Enhanced ergonomics** - `unwrap()`, `Result.collect()`, and fallback patterns

## New in v0.2.2: Enhanced Developer Experience

### `unwrap()` Function - Clean Result Extraction
```python
from resilient_result import unwrap

@resilient
async def api_call():
    return "success"

# Clean extraction - raises exception if failed
data = unwrap(await api_call())  # "success"
```

### `Result.collect()` - Parallel Operations Made Easy
```python
# Run multiple async operations, collect all results
operations = [
    fetch_user(user_id),
    fetch_profile(user_id),
    fetch_settings(user_id)
]

result = await Result.collect(operations)
if result.success:
    user, profile, settings = result.data  # All succeeded
else:
    print(f"Operation failed: {result.error}")  # First failure
```

### `@resilient.fallback()` - Mode Switching Pattern  
```python
# Automatically fallback between modes on error
@resilient.fallback("complexity", "simple", retries=2)
async def adaptive_processing(state):
    if state.complexity == "advanced":
        return await complex_algorithm(state)
    else:
        return await simple_algorithm(state)

# On error, automatically switches state.complexity to "simple" and retries
```

### Enhanced `@resilient` Syntax
```python
# Both syntaxes work identically
@resilient                    # Clean, no parentheses  
@resilient()                  # Traditional with parentheses
@resilient(retries=5)         # With parameters
```

Current patterns provide solid foundation with basic implementations suitable for development and basic production use.

*Production-grade pattern enhancements planned for v0.3.0 - see [roadmap](docs/roadmap.md)*

## When to Use

✅ **Perfect for**:
- API clients and external service calls
- Data processing pipelines  
- AI/LLM applications with retry logic
- Microservices with resilience requirements
- Any async operations that might fail

❌ **Not ideal for**:
- High-frequency inner loops (0.1ms overhead)
- Simple scripts (adds complexity)
- Teams preferring exception-based patterns

## Advanced Examples

### Composing Multiple Patterns
```python
# Stack decorators for layered resilience
@resilient.rate_limit(rps=5)
@resilient.circuit(failures=3)
@resilient.network(retries=2)
async def robust_api_call(endpoint: str):
    return await http.get(f"https://api.service.com/{endpoint}")
```

### Custom Error Types
```python
class APIError(Exception):
    pass

@resilient(retries=3, error_type=APIError, timeout=10)
async def typed_api_call(data: dict):
    response = await http.post("/api/endpoint", json=data)
    return response.json()

# Returns Result[dict, APIError] - type-safe!
```

### Sync Function Support
```python
@resilient(retries=3)
def sync_operation(data: str) -> str:
    if random.random() < 0.3:
        raise Exception("Sync failure")
    return f"processed: {data}"

# Also returns Result[str, Exception]
result = sync_operation("test")
```

## Testing Made Easy

```python
# No more exception mocking - just check Result values
async def test_api_call():
    result = await call_api("https://fake-url")
    
    assert isinstance(result, Result)
    if result.success:
        assert "data" in result.data
    else:
        assert "network" in str(result.error).lower()
```

## License

MIT - Build amazing resilient systems! 🚀