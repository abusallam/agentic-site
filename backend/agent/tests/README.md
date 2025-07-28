# Agentic AI Platform - Test Suite

This directory contains the comprehensive test suite for the agentic AI platform, including unit tests, integration tests, and end-to-end testing frameworks.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
├── integration/             # Integration tests for service connections
│   ├── test_service_connections.py    # Service connection testing
│   └── test_runner.py                 # Comprehensive test runner
├── fixtures/                # Test fixtures and mock implementations
│   ├── service_mocks.py              # Mock service implementations
│   └── test_database.py              # Test database management
├── smoke/                   # Smoke tests for basic functionality
├── conftest.py             # Pytest configuration and fixtures
├── pytest.ini             # Pytest configuration
└── README.md               # This file
```

## Running Tests

### Prerequisites

1. **Python Environment**: Ensure you have Python 3.11+ and `uv` installed
2. **Dependencies**: Install test dependencies with `uv sync`
3. **Environment**: Set up test environment variables

### Quick Start

```bash
# Navigate to agent directory
cd agent

# Install dependencies
uv sync
uv pip install pytest pytest-asyncio pytest-cov

# Run all tests
uv run pytest

# Run specific test categories
uv run pytest tests/unit/          # Unit tests only
uv run pytest tests/integration/   # Integration tests only
uv run pytest tests/smoke/         # Smoke tests only
```

### Integration Test Runner

The comprehensive integration test runner provides advanced testing capabilities:

```bash
# Run comprehensive integration test suite
uv run python tests/integration/test_runner.py --mode mock --verbose

# Run with different modes
uv run python tests/integration/test_runner.py --mode live    # Live services
uv run python tests/integration/test_runner.py --mode hybrid # Mixed mode

# Generate reports
uv run python tests/integration/test_runner.py \
  --mode mock \
  --output results.json \
  --report report.txt
```

### Test Modes

- **Mock Mode** (`mock`): Uses mock implementations for all external services
- **Live Mode** (`live`): Tests against real external services (requires configuration)
- **Hybrid Mode** (`hybrid`): Mix of mock and live services based on availability

### Environment Variables

Set these environment variables for testing:

```bash
# Test configuration
export TEST_MODE=mock                    # Test mode (mock, live, hybrid)
export TEST_DB_MODE=mock                 # Database test mode
export TEST_DATABASE_URL=...             # Test database URL (for postgres mode)

# Service configuration (for live testing)
export SUPABASE_URL=...                  # Supabase URL
export SUPABASE_ANON_KEY=...             # Supabase anonymous key
export GOOGLE_API_KEY=...                # Google Gemini API key
export MCP_SERVER_URL=...                # MCP server URL
```

## Test Categories

### Unit Tests (`tests/unit/`)

Test individual components in isolation:
- Agent classes and methods
- Service implementations
- Utility functions
- Data models

### Integration Tests (`tests/integration/`)

Test service integrations and component interactions:
- **Service Connections**: Database, MCP, monitoring, external APIs
- **Workflow Integration**: End-to-end workflow testing
- **Agent Coordination**: Multi-agent interaction testing

### Smoke Tests (`tests/smoke/`)

Basic functionality and health checks:
- System startup and initialization
- Basic API endpoints
- Critical path validation

## Mock Services

The test suite includes comprehensive mock implementations:

### Available Mocks
- **MockSupabaseService**: Database operations
- **MockMCPService**: n8n workflow automation
- **MockMonitoringService**: Metrics and monitoring
- **MockExternalAPIs**: Google Gemini, Stripe, Livekit

### Using Mocks

```python
from tests.fixtures.service_mocks import create_test_environment

# Create complete test environment
test_env = create_test_environment()
supabase_mock = test_env["supabase"]
mcp_mock = test_env["mcp"]

# Use in tests
customer = await supabase_mock.create_customer({"email": "test@example.com"})
workflow = await mcp_mock.trigger_workflow("test_workflow", {"data": "test"})
```

## Database Testing

The test suite includes comprehensive database testing capabilities:

### Test Database Modes
- **SQLite**: Local file-based testing
- **PostgreSQL**: Full database testing
- **Mock**: In-memory mock database

### Usage

```python
from tests.fixtures.test_database import TestDatabaseManager

# Create test database
db_manager = TestDatabaseManager(test_mode="mock")
await db_manager.setup_test_database()

# Use in tests
customer_data = await db_manager.get_test_data("customers", "customer_id")

# Cleanup
await db_manager.cleanup_test_database()
```

## CI/CD Integration

The test suite is integrated with GitHub Actions:

### Workflows
- **CI Pipeline** (`.github/workflows/ci.yml`): Runs on every push/PR
- **Integration Tests** (`.github/workflows/integration-tests.yml`): Comprehensive testing

### Artifacts
- Test results (JSON format)
- Coverage reports (HTML, XML)
- Test reports (text format)

## Coverage Requirements

- **Minimum Coverage**: 80%
- **Unit Tests**: 90%+ coverage expected
- **Integration Tests**: Focus on critical paths
- **Reports**: Generated in HTML, XML, and terminal formats

## Best Practices

### Writing Tests

1. **Isolation**: Each test should be independent
2. **Mocking**: Use mocks for external dependencies
3. **Assertions**: Clear, specific assertions
4. **Documentation**: Document complex test scenarios

### Test Data

1. **Fixtures**: Use pytest fixtures for reusable test data
2. **Factories**: Create data factories for complex objects
3. **Cleanup**: Always clean up test data
4. **Realistic**: Use realistic test data

### Performance

1. **Fast Tests**: Keep unit tests fast (< 1s each)
2. **Parallel**: Run tests in parallel when possible
3. **Selective**: Use markers to run specific test categories
4. **Caching**: Cache expensive setup operations

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure PYTHONPATH includes agent directory
2. **Database Errors**: Check database connection and permissions
3. **Service Errors**: Verify service configurations and availability
4. **Timeout Errors**: Increase timeout values for slow operations

### Debug Mode

```bash
# Run tests with debug output
uv run pytest -v -s --tb=long

# Run specific test with debugging
uv run pytest tests/integration/test_service_connections.py::test_supabase_integration -v -s
```

### Logging

Enable detailed logging for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Add appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
3. Include docstrings explaining test purpose
4. Update this README if adding new test categories
5. Ensure tests pass in CI/CD pipeline

## Support

For questions about the test suite:
- Check existing test examples
- Review pytest documentation
- Consult the project documentation
- Ask in team channels

---

**Last Updated**: January 23, 2025  
**Test Framework**: pytest + asyncio  
**Coverage Tool**: pytest-cov  
**CI/CD**: GitHub Actions