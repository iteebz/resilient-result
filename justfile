# Minimal justfile for resilient-result development

# Run tests
test:
    poetry run pytest

# Run tests with coverage
test-cov:
    poetry run pytest --cov=resilient_result --cov-report=term-missing

# Format code with black and ruff
format:
    poetry run black .
    poetry run ruff format .

# Lint and check with ruff
lint:
    poetry run ruff check .

# Lint and auto-fix with ruff  
fix:
    poetry run ruff check --fix .

# Install dependencies
install:
    poetry install

# Build package
build:
    poetry build

# Clean Python artifacts and cache directories
clean:
    @echo "Cleaning Python artifacts..."
    @rm -rf dist build .venv .pytest_cache .ruff_cache __pycache__ .coverage htmlcov
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @find . -name "*.pyc" -delete 2>/dev/null || true
    @find . -name "*.pyo" -delete 2>/dev/null || true

# Run all checks (test + lint)
check: lint test

# Development setup
dev: install format fix test

# Run CI checks locally (format + fix + test + build)
ci: format fix test build
    @echo "CI checks completed successfully!"