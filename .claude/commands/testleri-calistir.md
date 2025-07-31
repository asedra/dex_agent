Run comprehensive test suite with Docker restart and AI features

This command will:
1. Stop and restart Docker services for a clean environment
2. Run backend API tests including new AI features (AI command generation, ChatGPT settings)
3. Run frontend E2E tests including new AI features UI tests
4. Run pre-commit comprehensive tests
5. Generate detailed test reports

Steps:
1. Execute the comprehensive test runner script: `./run-all-tests.sh`
2. Monitor test progress and report results
3. Display test summary with pass/fail status
4. Copy any artifacts to test report directory

The test suite includes:
- Docker service restart for clean environment
- Backend API tests with AI functionality
- Frontend Playwright E2E tests with AI UI features
- Performance and security tests
- Comprehensive reporting

Test files covered:
- Backend: comprehensive_api_test.py (with AI command generation and ChatGPT settings tests)
- Frontend: all E2E tests including ai-features.spec.ts (Create Command with AI button, ChatGPT settings)