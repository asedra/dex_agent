Test Raporunu Oku - Read and Fix Test Report with Comprehensive API Testing

This command reads a test report from C:\test_report.md, analyzes issues, implements fixes, runs comprehensive API tests, and handles the git workflow with user approval.

## Workflow Steps:

1. **Read Test Report**: Read test report from Windows path `C:\test_report.md` (WSL: `/mnt/c/test_report.md`)
2. **Analyze Issues**: Parse findings and identify problems that need fixing
3. **Implement Fixes**: Apply code changes to resolve identified issues
4. **Start Docker Environment**: Run `docker-compose up -d --build` to start services
5. **Wait for Services**: Allow services to fully initialize (30 seconds)
6. **Run Comprehensive API Tests**: Execute full API test suite including:
   - Health endpoint testing
   - User login and JWT token generation
   - Token validation via /me endpoint
   - Agent registration and management
   - Command execution testing (gracefully handles no WebSocket agent)
   - PowerShell commands library access
   - Authorization testing
7. **Fix API Issues**: If tests fail, analyze and fix issues, then re-test
8. **Request Commit Approval**: Ask user "Değişiklikleri commit etmemi onaylıyor musunuz?"
9. **Git Operations**: After user approval:
   - Read GitHub token from `/home/ali/gitkey.md`
   - Configure git remote with token
   - Add, commit, and push changes
10. **Stop Services**: Run `docker-compose down` ONLY after successful commit

## API Test Coverage:

The comprehensive API tests validate:
- **System Health**: `/api/v1/system/health` endpoint
- **Authentication**: Login with username/password, JWT token generation
- **Authorization**: Protected endpoint access control
- **Token Management**: Token validation and user profile retrieval
- **Agent Management**: Registration, listing, and status checking
- **Command Execution**: PowerShell command execution via API
- **Data Integrity**: Response format and data validation

## Error Handling:

- If Docker startup fails, retry once before reporting error
- If API tests fail, implement fixes and re-run tests automatically
- If git operations fail, configure token and retry
- Keep services running until commit is complete

## Important Notes:

- Services remain running during user testing and approval process
- API tests are designed to work without requiring live WebSocket agents
- Command execution tests gracefully handle "agent not connected" scenarios
- All test results are logged with timestamps and detailed output
- Git token is automatically configured from `/home/ali/gitkey.md`