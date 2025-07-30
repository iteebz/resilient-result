# Changelog

All notable changes to resilient-result will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2024-07-30

### Changed
- Pure mechanism architecture: removed domain-specific patterns
- Independent `@timeout(seconds)` decorator (no longer tied to retry)
- Consolidated error types: `CircuitError`, `RateLimitError`, `RetryError`
- Uses Python's built-in `TimeoutError` for timeout operations

### Added
- Orthogonal decorator composition: `@retry` + `@timeout` + `@circuit` + `@rate_limit`
- `compose()` function for explicit decorator composition
- `Resilient` class with pre-built patterns (`.api()`, `.db()`, `.protected()`)
- Result flattening for clean boundary discipline
- `Result.collect()` for parallel async operations

### Removed
- **BREAKING**: Domain patterns (`.network()`, `.parsing()`) - use pure mechanisms instead
- Registry system - replaced with simple decorator composition

### Fixed
- 16% test reduction (98→82 tests) eliminating redundancy
- Consolidated test files for better maintainability

## [0.2.2] - 2024-07-27

### Added
- `unwrap()` standalone function for Result extraction
- `Result.collect()` method for parallel async operations  
- Enhanced `@resilient` syntax with bare decorator support

## [0.2.1] - 2024-07-26

### Added
- Automatic nested Result flattening (`Result.flatten()` method)
- Auto-flattening in all resilient decorators
- 15 new tests for comprehensive flattening coverage

### Fixed
- Clean boundary discipline - no more manual Result unwrapping needed
- Preserves error propagation through nested Results

## [0.2.0] - 2024-07-26

### Added
- Extensible registry system for domain-specific patterns
- Built-in resilience patterns: `@resilient.network()`, `@resilient.parsing()`, `@resilient.circuit()`, `@resilient.rate_limit()`
- Unified core decorator with consistent API
- Policy objects: `Retry`, `Circuit`, `Backoff`, `Timeout`
- Timeout support with asyncio integration
- Custom error types support
- Sync and async function support
- Smart Result detection and auto-wrapping

### Changed
- **BREAKING**: Complete architecture overhaul from simple Result type to resilience framework
- **BREAKING**: Now requires asyncio (was zero-dependency)

### Fixed
- Eliminated DRY violations with unified decorator core
- Thread-safe, async-first design

## [0.1.0] - 2024-07-25

### Added
- Initial `Result[T, E]` type implementation
- Rust-style API: `Ok()`, `Err()`, `.unwrap()`, `.map()`, `.and_then()`
- Generic type support with proper variance
- Method chaining for functional composition
- Zero dependencies - pure Python implementation
- Comprehensive test coverage

[0.3.1]: https://github.com/iteebz/resilient-result/compare/v0.2.2...v0.3.1
[0.2.2]: https://github.com/iteebz/resilient-result/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/iteebz/resilient-result/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/iteebz/resilient-result/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/iteebz/resilient-result/releases/tag/v0.1.0