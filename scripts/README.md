# Test Automation Scripts

This directory contains automated test execution scripts for the DexAgents project, implementing the CLAUDE.md workflow optimization.

## 🚀 Available Scripts

### Backend Test Runner
**File**: `run_backend_tests.py`
**Purpose**: Execute backend API tests with automated reporting
**Usage**: 
```bash
python3 scripts/run_backend_tests.py
```
**Output**: `backend_test_results.md`

### Frontend Test Runner  
**File**: `run_frontend_tests.js`
**Purpose**: Execute Playwright E2E tests with automated reporting
**Usage**:
```bash
node scripts/run_frontend_tests.js
```
**Output**: `frontend_test_results.md`

### Unified Test Runner
**File**: `unified_test_runner.py`
**Purpose**: Execute both backend and frontend tests with combined reporting
**Usage**:
```bash
# Run both test suites in parallel (default)
python3 scripts/unified_test_runner.py

# Run tests sequentially
python3 scripts/unified_test_runner.py --sequential

# Run only backend tests
python3 scripts/unified_test_runner.py --backend-only

# Run only frontend tests  
python3 scripts/unified_test_runner.py --frontend-only
```
**Output**: Both `backend_test_results.md` and `frontend_test_results.md` plus combined summary

## 📋 Prerequisites

### Environment Setup
1. **Docker Services**: All services must be running
   ```bash
   docker-compose up -d --build
   ```

2. **Dependencies**:
   - Python 3.11+ (for backend tests)
   - Node.js 18+ (for frontend tests)
   - All project dependencies installed

### Backend Prerequisites
- Python packages: `requests`, `json`, `time`, `sys`, `datetime`
- Backend service running on http://localhost:8080
- Valid authentication credentials (admin/admin123)

### Frontend Prerequisites  
- Node.js with npm
- Playwright installed: `npx playwright install`
- Frontend service running on http://localhost:3000
- All frontend dependencies: `npm install` in frontend directory

## 🔧 Script Features

### Service Health Checking
- All scripts check service availability before running tests
- Automatic waiting for services to be ready
- Clear error messages for service issues

### Comprehensive Reporting
- **Standardized markdown format** for all reports
- **Visual indicators** (✅❌⏭️) for test status
- **Performance metrics** and execution timing
- **Detailed error reporting** for failed tests
- **Browser compatibility notes** (frontend)
- **API endpoint coverage** (backend)

### Error Handling
- **Timeout protection** for long-running tests
- **Service unavailability** detection and messaging
- **Graceful failure handling** with clear error messages
- **Test parsing fallbacks** for malformed outputs

## 📊 Report Structure

### Backend Test Report (`backend_test_results.md`)
- Test execution summary with pass/fail counts
- Individual test details with timestamps
- Failed test analysis with error messages
- Performance notes and response times
- Overall status and next steps

### Frontend Test Report (`frontend_test_results.md`)
- E2E test execution summary
- Individual test results with browser details
- Failed test analysis with screenshots/errors
- Browser compatibility notes
- Performance observations
- Overall status and recommendations

## 🚀 Integration with CLAUDE.md Workflow

### Manual Test Execution
1. User runs test scripts manually
2. Results automatically saved to markdown files
3. Claude reads and analyzes reports via `test raporunu oku` command

### Commands Integration
- **`testleri çalıştır`**: Instructs user to run these scripts
- **`test raporunu oku`**: Claude analyzes generated reports
- **Approval workflow**: Follows CLAUDE.md approval requirements

### Workflow Process
1. **Planning**: Use `/tasks_start` to plan work
2. **Development**: Implement features following tasks
3. **Testing**: Run scripts manually to generate reports
4. **Analysis**: Claude analyzes reports and fixes issues
5. **Approval**: Get user approval for commits

## 🛠️ Troubleshooting

### Common Issues

#### Script Permission Errors
```bash
chmod +x scripts/*.py
chmod +x scripts/*.js
```

#### Service Not Running
```bash
# Check Docker services
docker-compose ps

# Restart services
docker-compose up -d --build
```

#### Module Import Errors (Backend)
```bash
# Ensure Python path includes backend directory
cd backend
pip install -r requirements.txt
```

#### Playwright Issues (Frontend)
```bash
# Install Playwright browsers
cd frontend
npx playwright install
```

### Script-Specific Issues

#### Backend Script Issues
- **Service unavailable**: Check if backend is running on port 8080
- **Authentication failed**: Verify admin/admin123 credentials work
- **Test timeouts**: Check database connection and service performance

#### Frontend Script Issues  
- **Browser launch failed**: Run `npx playwright install`
- **Service unavailable**: Check if frontend is running on port 3000
- **Test parsing failed**: Check test output format in console

#### Unified Runner Issues
- **Parallel execution failed**: Use `--sequential` flag
- **Service health check failed**: Wait longer for services to start
- **Script not found**: Check script paths and permissions

## 📝 Development Notes

### Adding New Tests
1. **Backend**: Add test methods to `backend/comprehensive_api_test.py`
2. **Frontend**: Add test files to `frontend/tests/e2e/`
3. Test runners will automatically include new tests

### Modifying Report Format
- Backend: Edit `generate_report()` method in `run_backend_tests.py`
- Frontend: Edit `generateReport()` method in `run_frontend_tests.js`

### Performance Optimization
- **Parallel execution**: Use unified runner with parallel mode (default)
- **Service caching**: Scripts cache service health checks
- **Timeout tuning**: Adjust timeouts in script configuration

## 🔗 Related Files

- **CLAUDE.md**: Project workflow documentation
- **commands.md**: Available Claude commands
- **story.md/bug.md/task.md**: Project management files
- **backend_test_results.md**: Generated backend test reports
- **frontend_test_results.md**: Generated frontend test reports
- **test_history.md**: Test modification tracking