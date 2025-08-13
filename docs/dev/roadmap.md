# Roadmap

## v0.5.0 - Next

**Circuit Breaker Evolution:**
- Half-open state for graceful recovery testing
- Exponential backoff for circuit recovery attempts
- Health check integration for dependency awareness

**Rate Limiting Improvements:**
- Distributed rate limiting with Redis backend
- Sliding window algorithms for smoother rate control
- HTTP rate limit headers (`X-RateLimit-*` compliance)

**Observability Integration:**
- OpenTelemetry spans for all resilience operations
- Prometheus metrics for failure rates and latencies
- Structured logging with correlation IDs

## v0.6.0 - Advanced Patterns

**New Mechanisms:**
```python
# Bulkhead isolation
@resilient.bulkhead(max_concurrent=10, queue_size=100)
async def protected_operation(): ...

# Fallback chains  
@resilient.fallback([primary_service, cache_fallback])
async def resilient_fetch(): ...

# Multi-level timeouts
@resilient.timeout(operation=5.0, request=30.0, total=300.0)
async def complex_operation(): ...
```

**Quality Improvements:**
- Connection pool awareness for network operations
- Graceful degradation patterns with automatic fallbacks

## Long-term Vision

**Core Principles (Never Change):**
1. **Pure Mechanisms** - No domain-specific assumptions
2. **Result Types** - Explicit error handling, no hidden exceptions
3. **Orthogonal Composition** - Decorators stack predictably  
4. **Zero Ceremony** - Beautiful APIs with smart defaults
5. **One Clear Way** - Eliminates API multiplication and AI confusion

**Breaking Changes Policy:**
- v0.x: Minor breaking changes with clear migration guide
- v1.0+: Semantic versioning with strict backwards compatibility

**Success Metrics:**
- 10k+ downloads/month by v1.0
- Production usage at 100+ companies
- <0.1% failure rate in decorator composition

**The roadmap prioritizes reliability over features** - every addition must maintain the canonical, AI-friendly foundation that makes resilient-result predictable.