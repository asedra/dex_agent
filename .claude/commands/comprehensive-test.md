# Comprehensive Pre-Commit Test Suite

Run the complete pre-commit test suite as defined in CLAUDE.md, covering all test categories in a single comprehensive report.

## Test Coverage

This command runs all test suites mentioned in CLAUDE.md:

1. **Health Check Tests**
   - Backend health endpoint
   - Frontend accessibility 
   - Commands page and AI button presence

2. **Authentication Tests**
   - Unauthorized access protection
   - User login functionality
   - JWT token validation

3. **API Functionality Tests**
   - Agents list retrieval
   - Commands library access
   - Agent registration and management
   - Command execution testing

4. **AI Features Tests**
   - AI service status check
   - ChatGPT API key validation
   - AI command generation
   - AI test command execution

5. **UI Integration Tests**
   - Commands page functionality
   - Dark mode CSS classes detection
   - AI button integration

## Usage

```bash
python3 comprehensive_pre_commit_test.py
```

## Expected Results

- **✅ All Tests Pass:** Ready for commit and production
- **⚠️ Warnings Only:** Acceptable, proceed with caution  
- **❌ Test Failures:** Fix issues before committing

## Output

The script generates:
- Real-time colored console output with test progress
- Comprehensive final report with recommendations
- Detailed JSON report file (`test_report_YYYYMMDD_HHMMSS.json`)

## Test Result Interpretation

### Success Indicators
- All health checks passing
- Authentication working correctly
- API endpoints responding properly
- AI features functional (if configured)
- UI elements properly rendered

### Common Issues
- **Backend not running:** Health check failures
- **Authentication problems:** Login/token validation failures
- **AI service unavailable:** Missing ChatGPT API key or service down
- **Frontend issues:** Commands page not accessible or missing UI elements

## Integration with Development Workflow

This comprehensive test should be run:
- Before committing code changes
- After implementing new features
- Before deploying to production
- When troubleshooting system issues

## Report Analysis

The generated JSON report contains detailed information about:
- Individual test execution times
- Specific failure reasons
- Warning details and recommendations
- Overall system health assessment

Use this report for:
- Identifying performance bottlenecks
- Tracking test trends over time
- Documenting system health for compliance
- Debugging failing components