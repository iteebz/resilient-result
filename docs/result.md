# Result API

## Type

```python
Result[T, E]  # Generic type: T = success type, E = error type
```

## Methods

```python
result.success  # bool - True if successful
result.failure  # bool - True if failed  
result.error    # E - Error value for inspection
result.unwrap() # T - Extract value or raise exception
result.flatten() # Result[T, E] - Flatten nested Results (auto-called by decorators)
```

## Patterns

**Status checking:**
```python
if result.success:
    data = result.unwrap()
```

**Error inspection:**
```python
if result.failure and "rate_limit" in result.error:
    await asyncio.sleep(60)
elif result.failure:
    log_error(result.error)
```

**Value extraction:**
```python
try:
    data = result.unwrap()
except ApiError as e:
    handle_error(e)
```

**Early return:**
```python
def process_data():
    result = fetch_data()
    if result.failure:
        return result  # Propagate failure
    
    data = result.unwrap()
    return Result.ok(transform(data))
```

## Constructors

```python
from resilient_result import Result, Ok, Err

Result.ok("data")    # Success
Result.fail("error") # Failure
Ok("data")           # Alias
Err("error")         # Alias
```

## Auto-Flattening

**Decorators automatically flatten nested Results:**

```python
@retry()
async def nested_operation():
    inner_result = Result.ok("data")
    return Result.ok(inner_result)  # Nested Result

# Auto-flattened to Result.ok("data")
result = await nested_operation()
assert result.unwrap() == "data"  # Not Result("data")
```