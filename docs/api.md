# resilient-result v0.2.3 API Reference

## Policy-Based Configuration

### Core Decorator
```python
from resilient_result import resilient, Retry, Circuit, Backoff

@resilient()                                    # Beautiful defaults
@resilient(retry=Retry.api())                   # API preset
@resilient(retry=Retry.db(), backoff=Backoff.linear())  # Combined policies
@resilient(retry=Retry(attempts=5, timeout=10)) # Custom configuration
```

### Policy Classes

#### Retry Policy
```python
# Default constructor
Retry()          # attempts=3, timeout=None (no timeout)
Retry(attempts=5, timeout=10)  # Custom values

# Factory methods
Retry.api()      # attempts=3, timeout=30
Retry.db()       # attempts=5, timeout=60  
Retry.ml()       # attempts=2, timeout=120
```

#### Backoff Policy
```python
# Factory methods
Backoff.exp()     # delay=0.1, factor=2, max_delay=30
Backoff.linear()  # delay=1.0
Backoff.fixed()   # delay=1.0

# Custom
Backoff.exp(delay=0.5, factor=1.5, max_delay=60)
```

#### Circuit Policy
```python
# Factory methods
Circuit.fast()     # failures=3, window=60
Circuit.standard() # failures=5, window=300

# Custom
Circuit(failures=3, window=60)
```

## Result Types

### Basic Usage
```python
from resilient_result import Result, Ok, Err, unwrap

# Construction
success = Ok("data")
failure = Err("error")

# Pattern matching
if result.success:
    print(result.data)
else:
    print(result.error)

# Extraction
data = unwrap(result)  # Raises if error
```

### Parallel Operations
```python
# Collect multiple async operations
operations = [fetch_user(id), fetch_profile(id)]
result = await Result.collect(operations)

if result.success:
    user, profile = result.data  # All succeeded
else:
    print(f"Failed: {result.error}")  # First failure
```

## Built-in Patterns

### Network Pattern
```python
@resilient.network()
async def api_call():
    return await httpx.get(url)
```

### Parsing Pattern  
```python
@resilient.parsing()
async def parse_json(text):
    return json.loads(text)
```

### Circuit Breaker
```python
@resilient.circuit(failures=3, window=60)
async def external_service():
    return await service.call()
```

### Rate Limiting
```python
@resilient.rate_limit(rps=10.0, burst=5)
async def api_call():
    return await external_api()
```

## Advanced Features

### Custom Error Types
```python
@resilient(retry=Retry.api(), error_type=CustomError)
async def typed_operation():
    return "data"
# Returns Result[str, CustomError]
```

### Custom Handlers
```python
async def smart_handler(error):
    if "rate_limit" in str(error):
        await asyncio.sleep(60)
        return None  # Retry
    return False  # Don't retry

@resilient(retry=Retry(attempts=3), handler=smart_handler)
async def operation():
    return await api_call()
```

### Registry System
```python
# Register custom patterns
resilient.register("custom", lambda **kwargs: decorator(**kwargs))

# Use registered patterns
@resilient.custom()
async def operation():
    return "data"
```

## Key Principles

- **Policy objects over primitives**: `retry=Retry.api()` not `retries=3`
- **Beautiful factory methods**: Short, memorable presets
- **Result types over exceptions**: Explicit error handling
- **Zero ceremony**: Clean, readable decorators