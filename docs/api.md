# resilient-result v0.3.1 API Reference

## Core Decorators

### @retry
```python
from resilient_result import retry, Backoff

@retry()                                    # 3 attempts, exponential backoff
@retry(attempts=5)                          # Custom attempts
@retry(attempts=3, backoff=Backoff.linear()) # Custom backoff
@retry(attempts=3, error_type=CustomError)  # Custom error type
```

### @timeout
```python
from resilient_result import timeout

@timeout(10.0)                              # 10 second timeout
@timeout(30.0, error_type=MyTimeoutError)   # Custom error type
```

### @circuit
```python
from resilient_result import circuit

@circuit()                                  # 3 failures, 300s window
@circuit(failures=5, window=60)            # Custom configuration
```

### @rate_limit
```python
from resilient_result import rate_limit

@rate_limit()                               # 1 RPS default
@rate_limit(rps=10.0, burst=5)             # Custom rate and burst
```

## Composition

### Manual Composition
```python
from resilient_result import compose, retry, timeout, circuit

@compose(
    circuit(failures=3),
    timeout(10.0),
    retry(attempts=3)
)
async def robust_operation():
    return await external_service()
```

### Resilient Class Patterns
```python
from resilient_result import resilient

# Pre-built patterns
@resilient.api()          # timeout(30) + retry(3)
@resilient.db()           # timeout(60) + retry(5)  
@resilient.protected()    # circuit + retry

# Individual decorators
@resilient.retry(attempts=5)
@resilient.timeout(10.0)
@resilient.circuit(failures=3)
@resilient.rate_limit(rps=100)
```

## Result Types

### Basic Usage
```python
from resilient_result import Result, Ok, Err, unwrap

# Construction
success = Ok("data")
failure = Err("error message")

# Pattern matching
if result.success:
    print(result.data)
else:
    print(result.error)

# Boolean context
if result:
    print("Success!")

# Extraction (raises on error)
data = unwrap(result)
data = result.unwrap()
```

### Advanced Result Operations

#### Flattening
```python
nested = Ok(Ok("data"))
flat = nested.flatten()  # Ok("data")

mixed = Ok(Err("error"))
flat = mixed.flatten()   # Err("error")
```

#### Parallel Collection
```python
# Collect multiple async operations
operations = [fetch_user(1), fetch_user(2), fetch_user(3)]
result = await Result.collect(operations)

if result.success:
    users = result.data  # List of all results
else:
    print(f"First failure: {result.error}")
```

## Policy Objects

### Retry Policies
```python
from resilient_result import Retry

Retry()                   # attempts=3, timeout=None
Retry(attempts=5, timeout=30.0)

# Presets
Retry.api()              # attempts=3, timeout=30
Retry.db()               # attempts=5, timeout=60
Retry.ml()               # attempts=2, timeout=120
```

### Backoff Strategies
```python
from resilient_result import Backoff

# Exponential (default)
Backoff.exp()                           # delay=0.1, factor=2, max=30
Backoff.exp(delay=0.5, factor=1.5)     # Custom parameters

# Linear
Backoff.linear()                        # delay=1.0
Backoff.linear(delay=2.0, max_delay=60)

# Fixed
Backoff.fixed()                         # delay=1.0
Backoff.fixed(delay=5.0)
```

### Circuit Policies
```python
from resilient_result import Circuit

Circuit()                # failures=5, window=300
Circuit(failures=3, window=60)

# Presets
Circuit.fast()           # failures=3, window=60
Circuit.standard()       # failures=5, window=300
```

### Timeout Policies
```python
from resilient_result import Timeout

Timeout(30.0)

# Presets
Timeout.fast()           # 5 seconds
Timeout.api()            # 30 seconds
Timeout.db()             # 60 seconds
Timeout.ml()             # 120 seconds
```

## Error Handling

### Custom Error Types
```python
class APIError(Exception):
    pass

@retry(attempts=3, error_type=APIError)
async def api_call():
    raise ValueError("Connection failed")

# Returns Err(APIError("Connection failed"))
```

### Error Handlers
```python
async def smart_handler(error):
    if "rate_limit" in str(error):
        await asyncio.sleep(60)
        return None  # Continue retrying
    return False     # Stop retrying

@retry(attempts=5, handler=smart_handler)
async def api_with_rate_limits():
    return await external_api()
```

## Complete Examples

### API Client
```python
from resilient_result import resilient, Result

@resilient.api(attempts=3, timeout_s=30.0)
async def fetch_user(user_id: str) -> str:
    response = await httpx.get(f"/users/{user_id}")
    return response.json()

result: Result[dict, Exception] = await fetch_user("123")
if result:
    user = result.data
    print(f"User: {user['name']}")
else:
    print(f"Failed: {result.error}")
```

### Database Operations
```python
@resilient.db(attempts=5, timeout_s=60.0)
async def save_user(user_data: dict) -> str:
    async with database.transaction():
        return await User.create(**user_data)

result = await save_user({"name": "Alice"})
if result:
    print(f"Created user ID: {result.data}")
```

### Protected Service
```python
@resilient.protected(attempts=3, failures=5, window=300)
async def critical_service():
    return await external_dependency()

# Combines circuit breaker + retry for maximum protection
```

All decorators return `Result[T, Exception]` types - never throw exceptions directly.