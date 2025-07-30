# Extensions

**Turn resilient-result into domain-specific resilience frameworks.**

resilient-result provides pure mechanisms. You provide domain expertise.

## The Extension Pattern

```python
from resilient_result import resilient, Retry, Result
from functools import wraps

def domain_decorator(name: str, default_retry=None):
    """Create domain-specific decorator that composes resilience + domain logic."""
    
    def decorator(retry=None, **domain_kwargs):
        retry = retry or default_retry or Retry.api()
        
        def wrapper(func):
            # 1. Apply base resilience
            resilient_func = resilient(retry=retry)(func)
            
            # 2. Add domain-specific enhancements
            @wraps(resilient_func)
            async def enhanced(*args, **kwargs):
                # Pre-processing hook
                processed_args = your_domain_preprocessing(*args, **kwargs)
                
                # Execute with resilience
                result = await resilient_func(*processed_args, **kwargs)
                
                # Post-processing hook
                if result.success:
                    return your_domain_postprocessing(result, name, **domain_kwargs)
                return result
                
            return enhanced
        return wrapper
    return decorator

# Create semantic decorators
reason = domain_decorator("reasoning", Retry.api())
process = domain_decorator("processing", Retry.db())

# Beautiful usage
@reason()
async def think_step(): ...

@process(retry=Retry(attempts=5))
async def execute_action(): ...
```

## Real-World Example: AI Agents

From production usage in [cogency](https://github.com/iteebz/cogency):

```python
from resilient_result import resilient, Retry, Result
from functools import wraps
import asyncio

def checkpoint_decorator(phase: str, interruptible: bool = True):
    """Add checkpointing to resilient operations."""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            state = args[0]  # Agent state is first argument
            
            # Only checkpoint when in task context
            if hasattr(state, 'task_id') and state.task_id:
                # Save checkpoint before execution
                await save_checkpoint(state, phase)
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Update checkpoint with result
                    if result.success:
                        await update_checkpoint(state, phase, result.data)
                    
                    return result
                    
                except Exception as e:
                    # Recovery from checkpoint on failure
                    if interruptible:
                        await restore_checkpoint(state, phase)
                    raise
            
            # No checkpointing overhead for non-task contexts
            return await func(*args, **kwargs)
            
        return wrapper
    return decorator

def agent_pattern(phase: str, interruptible: bool = True, retry_policy=None):
    """AI agent decorator: resilience + checkpointing + observability."""
    
    def decorator(retry=None, **kwargs):
        retry = retry or retry_policy or Retry.api()
        
        def wrapper(func):
            # Compose: resilience + checkpointing + tracing
            resilient_func = resilient(retry=retry)(func)
            checkpointed_func = checkpoint_decorator(phase, interruptible)(resilient_func)
            
            @wraps(checkpointed_func)
            async def traced(*args, **kwargs):
                with trace_span(f"agent.{phase}"):
                    return await checkpointed_func(*args, **kwargs)
                    
            return traced
        return wrapper
    return decorator

# Domain-specific patterns with smart defaults
reason = agent_pattern("reasoning", interruptible=True, retry_policy=Retry.api())
act = agent_pattern("action", interruptible=True, retry_policy=Retry.db()) 
respond = agent_pattern("response", interruptible=False, retry_policy=Retry(attempts=2))

class AgentDecorators:
    reason = staticmethod(reason)
    act = staticmethod(act)  
    respond = staticmethod(respond)

agent = AgentDecorators()

# Usage - reads like domain language
@agent.reason()
async def reasoning_step(state): 
    """Think through the problem."""
    return await llm.reason(state.context)

@agent.act(retry=Retry(attempts=5))
async def tool_execution(state, tool_call):
    """Execute tool with extra retries."""
    return await tools.execute(tool_call)

@agent.respond()
async def generate_response(state):
    """Generate final response - no interruption."""
    return await llm.generate(state.final_context)
```

## Other Domain Examples

### Web Scraping
```python
from resilient_result import resilient, Retry
import time

def scraping_pattern(site: str, rate_limit_key: str = None):
    """Web scraping with site-specific patterns."""
    
    site_configs = {
        "amazon": Retry(attempts=5, timeout=30),
        "google": Retry(attempts=2, timeout=10), 
        "default": Retry.api()
    }
    
    def decorator(retry=None, **kwargs):
        retry = retry or site_configs.get(site, site_configs["default"])
        rate_key = rate_limit_key or f"scrape_{site}"
        
        def wrapper(func):
            resilient_func = resilient(retry=retry)(func)
            
            @wraps(resilient_func)
            async def rate_limited(*args, **kwargs):
                # Domain-specific rate limiting
                await enforce_site_rate_limit(site, rate_key)
                
                result = await resilient_func(*args, **kwargs)
                
                # Handle site-specific responses
                if result.success:
                    return process_site_response(result.data, site)
                return result
                
            return rate_limited
        return wrapper
    return decorator

# Create site-specific decorators
scrape_amazon = scraping_pattern("amazon")
scrape_google = scraping_pattern("google")

@scrape_amazon()
async def get_product_info(product_id):
    return await fetch(f"https://amazon.com/products/{product_id}")
```

### Database Operations  
```python
def database_pattern(operation_type: str):
    """Database operations with connection management."""
    
    type_configs = {
        "read": Retry(attempts=3, timeout=30),
        "write": Retry(attempts=5, timeout=60),
        "migration": Retry(attempts=1, timeout=300)
    }
    
    def decorator(retry=None, **kwargs):
        retry = retry or type_configs.get(operation_type, Retry.db())
        
        def wrapper(func):
            resilient_func = resilient(retry=retry)(func)
            
            @wraps(resilient_func)
            async def with_connection(*args, **kwargs):
                async with get_db_connection(operation_type) as conn:
                    # Inject connection into function args
                    return await resilient_func(conn, *args, **kwargs)
                    
            return with_connection
        return wrapper
    return decorator

db_read = database_pattern("read")
db_write = database_pattern("write")

@db_write()
async def save_user(conn, user_data):
    return await conn.execute("INSERT INTO users VALUES (?)", user_data)
```

## Extension Guidelines

### ✅ Best Practices

1. **Start with resilient()** - always apply base resilience first
2. **Preserve Result types** - never unwrap Results in extensions  
3. **Use semantic names** - `@agent.reason()` reads better than `@retry_with_checkpoint()`
4. **Encode domain knowledge** - smart defaults based on use case
5. **Keep it simple** - 20 lines of clear code beats complex abstractions

### ❌ Anti-Patterns

```python
# DON'T unwrap Results
def bad_extension(func):
    resilient_func = resilient()(func)
    def wrapper(*args):
        result = resilient_func(*args)
        return result.data  # ❌ Lost error information
    return wrapper

# DON'T ignore base resilience  
def bad_extension(func):
    def wrapper(*args):
        # ❌ No resilience applied
        return your_domain_logic(func(*args))
    return wrapper

# DON'T over-abstract
class BadExtensionBuilder:  # ❌ Too complex
    def with_retry(self, attempts): ...
    def with_timeout(self, seconds): ...
    def build(self): ...
```

### Type Safety

Extensions preserve full type safety:

```python
@agent.reason()
async def typed_reasoning(state: AgentState) -> str:
    return "reasoning result"

# Result type is automatically inferred as Result[str, Exception]
result: Result[str, Exception] = await typed_reasoning(state)
```

## Key Principles

1. **Composition over inheritance** - stack decorators, don't subclass
2. **Domain semantics** - `@agent.reason()` tells a story
3. **Result preservation** - maintain `Result[T, E]` through all layers
4. **Smart defaults** - encode best practices in presets
5. **Zero ceremony** - beautiful APIs that just work

Build your own domain-specific `@robust` equivalent. resilient-result provides the foundation - you provide the expertise.