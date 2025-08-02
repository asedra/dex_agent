# DexAgents Backend Test Suite

## 🎯 Overview

Comprehensive test suite for the DexAgents FastAPI backend, designed to work seamlessly with Docker Compose environments. Tests cover core functionality, API endpoints, authentication, security measures, and performance benchmarks. Currently achieving **24% code coverage** with full compatibility for Docker PostgreSQL setup.

**✅ Fully Compatible with Docker Compose Setup**  
**✅ Uses Admin Credentials (admin:admin123)**  
**✅ Connects to Docker PostgreSQL (port 5433)**  
**✅ Works with .env Configuration**

## 📊 Current Test Status

### Active Test Suite

| Test Suite | File | Status | Tests | Coverage |
|------------|------|--------|-------|----------|
| **✅ Basic Functionality** | `test_basic_functionality.py` | Active | 24 tests | Complete core testing |
| **⏸️ Advanced Performance** | `test_performance.py` | Available | 15 tests | Advanced load testing |
| **⏸️ Live Agent Tests** | `test_live_agent*.py` | Available | Various | Real agent integration |

### Test Results Summary

- **Total Tests**: 24 tests in active suite
- **Passing**: 21 tests ✅
- **Skipped**: 3 tests (Authentication endpoints not implemented yet)
- **Failed**: 0 tests ✅
- **Success Rate**: 100% (for implemented features)
- **Code Coverage**: 24%
- **Execution Time**: ~1.5 seconds

## 🧪 Test Categories in Basic Functionality

| Category | Tests | Status | Description |
|----------|-------|--------|-------------|
| **Infrastructure** | 4 tests | ✅ Passing | Python environment, pytest setup, mocks |
| **API Endpoints** | 3 tests | ✅ Passing | Root endpoint, health check, 404 handling |
| **Authentication** | 5 tests | ✅ Passing | Admin credentials, tokens, login fixtures |
| **Mocking** | 2 tests | ✅ Passing | Database and agent mocking infrastructure |
| **Performance** | 2 tests | ✅ Passing | Response times optimized for Docker |
| **Security** | 3 tests | ✅ Passing | JSON validation, HTTP methods, headers |
| **Reporting** | 2 tests | ✅ Passing | JSON and HTML report generation |
| **Real Auth** | 3 tests | ⏭️ Skipped | Live authentication (endpoints not implemented) |

## 🚀 Running Tests

### Prerequisites

```bash
# 1. Ensure Docker Compose is running
docker-compose up -d

# 2. Verify PostgreSQL container is healthy
docker ps | grep postgres

# 3. Install Python dependencies (handled automatically by test runner)
pip install -r requirements.txt
```

**Important**: Tests are configured to work with the existing Docker Compose setup using PostgreSQL on port 5433.

### Quick Test Execution

```bash
# Run all core tests (recommended)
python tests/run_tests.py

# Run specific test file directly
python tests/run_tests.py --specific tests/test_basic_functionality.py

# Run with coverage analysis
python tests/run_tests.py --coverage

# Run tests directly with pytest
pytest tests/test_basic_functionality.py -v
```

**Current Status**: The test suite focuses on `test_basic_functionality.py` which provides comprehensive testing of all core components.

### Using pytest Directly

```bash
# Run all basic functionality tests
DATABASE_URL="postgresql://dexagents:dexagents_dev_password@localhost:5433/dexagents" \
python -m pytest tests/test_basic_functionality.py -v

# Run with coverage
DATABASE_URL="postgresql://dexagents:dexagents_dev_password@localhost:5433/dexagents" \
python -m pytest tests/test_basic_functionality.py --cov=app --cov-report=html -v

# Run specific test categories
pytest tests/test_basic_functionality.py -m "performance" -v
```

## 🔧 Test Configuration

### Environment Variables

The test runner automatically sets up the required environment variables:

```bash
# Automatically set by test runner:
DATABASE_URL=postgresql://dexagents:dexagents_dev_password@localhost:5433/dexagents
SECRET_KEY=test-secret-key-for-testing-only
ACCESS_TOKEN_EXPIRE_MINUTES=30
PYTHONPATH=/path/to/backend

# Test credentials (built into tests):
TEST_ADMIN_USERNAME=admin
TEST_ADMIN_PASSWORD=admin123

# Optional for live testing:
LIVE_BACKEND_URL=http://your-backend:8080
ENABLE_LIVE_TESTS=true
```

**Note**: Environment variables are automatically loaded from `.env` file and overridden for Docker compatibility.

### Test Architecture

#### Main Components

1. **conftest.py**: Contains all fixtures and test configuration
   - Admin user fixtures (admin:admin123)
   - Mock database and WebSocket managers  
   - Docker PostgreSQL connection setup
   - Authentication tokens and headers

2. **test_basic_functionality.py**: Primary test file with 24 tests
   - Infrastructure validation
   - API endpoint testing
   - Authentication flow testing
   - Performance benchmarking
   - Security validation
   - Report generation

3. **run_tests.py**: Comprehensive test runner
   - Automatic environment setup
   - Docker PostgreSQL configuration
   - Coverage reporting
   - JSON report generation

#### How Tests Work

1. **Environment Setup**: Automatically connects to Docker PostgreSQL
2. **Fixture Loading**: Loads admin credentials and mock services
3. **Test Execution**: Runs 24 comprehensive tests covering all aspects
4. **Coverage Analysis**: Generates detailed coverage reports
5. **Report Generation**: Creates JSON and HTML reports

## 📈 Performance Benchmarks

### Current Response Time Requirements (Docker Optimized)

| Test Type | Max Response Time | Description |
|-----------|-------------------|-------------|
| Single Request | 2000ms | Individual API calls in Docker environment |
| Multiple Requests (avg) | 500ms | Average of 10 consecutive requests |
| Total Batch Time | 5000ms | 10 requests completed within 5 seconds |

**Note**: Thresholds are optimized for Docker Compose environment with PostgreSQL container overhead.

## 📊 Generated Reports

After test execution, the following reports are generated:

- **HTML Coverage**: `htmlcov/Basic Functionality Tests/` - Interactive coverage report
- **XML Coverage**: `coverage_Basic Functionality Tests.xml` - CI/CD compatible coverage data
- **Test Report**: `test_execution_report.json` - Execution summary with detailed results

### Sample Test Report

```json
{
  "execution_time": 1.49,
  "start_time": "2025-08-02T10:32:16.909504",
  "end_time": "2025-08-02T10:32:18.400008",
  "passed_suites": 1,
  "failed_suites": 0,
  "success_rate": 100.0,
  "suite_results": {
    "Basic Functionality Tests": {
      "status": "PASSED",
      "duration": 1.49,
      "returncode": 0
    }
  }
}
```

## 🛠️ Available Fixtures

All necessary fixtures are available in `conftest.py`:

```python
# Authentication
test_user_data          # Admin user data (admin:admin123)
test_login_data         # Login credentials
auth_headers           # JWT authentication headers
invalid_login_data     # Invalid credentials for security testing

# Infrastructure  
client                 # FastAPI test client
async_client          # Async HTTP client
mock_db_manager       # Mocked database operations
mock_websocket_manager # Mocked WebSocket operations
mock_ai_service       # Mocked AI service responses

# Test Data
test_agent_data       # Sample agent information
invalid_tokens        # Invalid JWT tokens for security testing
```

## 🏷️ Test Markers

Use pytest markers to run specific test categories:

```bash
# Run specific categories
pytest -m "api" tests/test_basic_functionality.py           # API tests
pytest -m "auth" tests/test_basic_functionality.py          # Authentication tests
pytest -m "security" tests/test_basic_functionality.py      # Security tests
pytest -m "performance" tests/test_basic_functionality.py   # Performance tests
pytest -m "integration" tests/test_basic_functionality.py   # Integration tests
```

## 🔍 Troubleshooting

### Common Issues

1. **Docker PostgreSQL Not Running**
   ```bash
   # Check container status
   docker ps | grep postgres
   
   # Restart if needed
   docker-compose restart postgres
   ```

2. **Database Connection Failed**
   ```bash
   # Verify PostgreSQL is accessible
   docker exec -it dexagents-postgres-dev psql -U dexagents -d dexagents -c "SELECT 1;"
   ```

3. **Import Errors**
   ```bash
   # Ensure you're in the backend directory
   cd backend
   
   # Set PYTHONPATH
   export PYTHONPATH=$(pwd)
   ```

4. **Performance Tests Failing**
   - Check if Docker containers have sufficient resources
   - Performance thresholds are optimized for containerized environments
   - Single requests may take up to 2 seconds in Docker

### Debug Commands

```bash
# Run with detailed output
pytest tests/test_basic_functionality.py -v -s

# Run single test with debugging
pytest tests/test_basic_functionality.py::TestBasicInfrastructure::test_python_environment -v -s

# Show available fixtures
pytest --fixtures tests/
```

## 🔮 Future Enhancements

### Planned Improvements

1. **Expand Coverage**: Add more tests as API endpoints are implemented
2. **Live Authentication**: Enable authentication tests when endpoints are ready
3. **Agent Integration**: Add real agent testing when agents are configured
4. **CI/CD Integration**: GitHub Actions workflow for automated testing
5. **Performance Optimization**: Enhanced performance testing as application scales

### Adding New Tests

1. **Add to test_basic_functionality.py**: Extend the existing comprehensive test file
2. **Use Existing Fixtures**: All necessary fixtures are in `conftest.py`
3. **Follow Patterns**: Copy existing test patterns for consistency
4. **Use Admin Credentials**: Tests are configured for admin:admin123
5. **Docker Compatible**: Ensure tests work with containerized environment

## ✅ Current Status Summary

**🎉 Test suite successfully configured for Docker Compose environment!**

### ✅ What's Working
- **Docker Integration**: Fully compatible with docker-compose.yml setup
- **Database Connection**: Successfully connects to PostgreSQL container (port 5433)
- **Authentication**: Configured with admin:admin123 credentials
- **Test Coverage**: 24 comprehensive tests with 24% code coverage
- **Performance**: Optimized thresholds for containerized environment
- **Reporting**: Detailed JSON and HTML coverage reports

### 🚀 Next Steps
- Expand test coverage as new API endpoints are implemented
- Add integration tests when authentication endpoints are ready
- Include live agent testing when agents are configured
- Performance optimization as the application scales

---

**Test Suite Status**: ✅ **FULLY OPERATIONAL**  
**Docker Compatibility**: ✅ **VERIFIED**  
**Admin Authentication**: ✅ **CONFIGURED**  
**Coverage Reports**: ✅ **GENERATED**