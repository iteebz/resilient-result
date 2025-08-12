# Resilience Decorators

## Core Decorators

```python
@retry()                    # 3 attempts, exponential backoff
@retry(attempts=5)          # Custom attempts
@timeout(10.0)              # 10 second timeout
@circuit(failures=5)        # Circuit breaker
@rate_limit(rps=100)        # Rate limiting
```

## Composition

```python
@retry(attempts=3)
@timeout(10.0) 
@circuit(failures=5)
@rate_limit(rps=100)
async def api_call():
    return await http.get(url)
```

## Policies

```python
from resilient_result import Retry, Backoff

@retry(attempts=5, backoff=Backoff.linear(start=1.0, step=0.5))
@retry(attempts=3, backoff=Backoff.exponential(base=2.0))
@retry(attempts=3, backoff=Backoff.fixed(delay=1.0))
```

## Presets

```python
from resilient_result import resilient

@resilient.api()       # timeout(30) + retry(3)
@resilient.db()        # timeout(60) + retry(5) 
@resilient.protected() # circuit + retry
```

## Manual Composition

```python
from resilient_result import compose

@compose(
    circuit(failures=3),
    timeout(10.0),
    retry(attempts=3)
)
async def robust_operation():
    return await external_service()
```

## Error Handlers

```python
async def smart_handler(error):
    if "rate_limit" in str(error):
        await asyncio.sleep(60)
        return None  # Continue retrying
    return False     # Stop retrying

@retry(attempts=5, handler=smart_handler)
async def api_with_backoff():
    return await rate_limited_api()
```

## Parallel Operations

```python
from resilient_result import Result

operations = [fetch_user(1), fetch_user(2), fetch_user(3)]
result = await Result.collect(operations)
```