# Bug Reports

This file contains current bugs to fix for the DexAgents project.

## Format
Each bug should follow this format:
```
### Bug ID: [BUG-XXX]
**Title**: Brief bug title
**Description**: Detailed description of the issue
**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3
**Expected Behavior**: What should happen
**Actual Behavior**: What actually happens
**Environment**: Browser/OS/Version details
**Severity**: Critical/High/Medium/Low
**Priority**: High/Medium/Low
**Created**: YYYY-MM-DD
**Status**: Fixed/In Progress/Fixed/Verified
**Related**: Links to related stories/tasks
```

---

## Current Bugs

### Bug ID: [BUG-001]
**Title**: Playwright not found in frontend test environment
**Description**: Frontend test execution fails because Playwright is not installed or not accessible in the test environment
**Steps to Reproduce**:
1. Run `node scripts/run_frontend_tests.js`
2. Script attempts to execute Playwright tests
3. Error occurs: "sh: 1: playwright: not found"
**Expected Behavior**: Playwright tests should execute successfully
**Actual Behavior**: Test execution fails with "playwright: not found" error
**Environment**: Local Docker development environment
**Severity**: High
**Priority**: High
**Created**: 2025-01-31
**Status**: Fixed
**Related**: STORY-001 CLAUDE.md workflow optimization

### Bug ID: [BUG-002]
**Title**: Frontend tests hang and never complete execution
**Description**: Frontend E2E tests start execution but never complete, causing the test runner to hang indefinitely. Tests appear to run but the process never terminates properly.
**Steps to Reproduce**:
1. Run `node scripts/run_frontend_tests.js` or `python3 scripts/unified_test_runner.py`
2. Frontend tests start executing
3. Process hangs and never completes
4. No test results are generated
**Expected Behavior**: Frontend tests should complete execution and generate test results
**Actual Behavior**: Tests hang indefinitely and never complete
**Environment**: Local Docker development environment with Playwright
**Severity**: High
**Priority**: High
**Created**: 2025-01-31
**Status**: Fixed
**Related**: STORY-001 CLAUDE.md workflow optimization

### Bug ID: [BUG-003]
**Title**: Frontend test results not being properly captured or reported
**Description**: When frontend tests do run, the results are not being properly parsed, captured, or reported in the frontend_test_results.md file
**Steps to Reproduce**:
1. Run frontend tests
2. Check frontend_test_results.md
3. File shows old "playwright not found" error instead of current test results
**Expected Behavior**: Current test results should be captured and reported
**Actual Behavior**: Old cached results or no results are shown
**Environment**: Local Docker development environment
**Severity**: Medium
**Priority**: High
**Created**: 2025-01-31
**Status**: Fixed
**Related**: STORY-001 CLAUDE.md workflow optimization, BUG-002

### Bug ID: [BUG-004]
**Title**: Frontend tests cannot find "Agents" page heading
**Description**: Multiple tests fail because they cannot find the h2 element with "Agents" text on the agents page
**Steps to Reproduce**:
1. Navigate to agents page in frontend
2. Test looks for locator('h2') with text "Agents"
3. Element is not found, causing timeout
**Expected Behavior**: Agents page should have an h2 heading with "Agents" text
**Actual Behavior**: h2 element with "Agents" text is not found
**Environment**: Frontend E2E tests with Playwright
**Severity**: High
**Priority**: High
**Created**: 2025-01-31
**Status**: Fixed
**Related**: Frontend agents page layout

### Bug ID: [BUG-005]
**Title**: Frontend tests cannot find specific agent names (INITIAL-PC, MOBILE-TEST-PC)
**Description**: Tests fail when looking for specific agent names that should be displayed in the agents list
**Steps to Reproduce**:
1. Navigate to agents page
2. Test looks for text 'INITIAL-PC' or 'MOBILE-TEST-PC'
3. Elements are not visible
**Expected Behavior**: Agent names should be visible in the agents list
**Actual Behavior**: Agent names are not found or not visible
**Environment**: Frontend E2E tests with Playwright
**Severity**: Medium
**Priority**: High
**Created**: 2025-01-31
**Status**: Fixed
**Related**: Agents data display, API integration

### Bug ID: [BUG-006]
**Title**: Authentication redirect loop in AI features tests
**Description**: AI features test fails due to unexpected redirect to login page with credentials in URL
**Steps to Reproduce**:
1. Try to access AI features
2. Expected to be on home page (http://localhost:3000/)
3. Actually redirected to login page with credentials
**Expected Behavior**: Should stay on main page after authentication
**Actual Behavior**: Redirects to login page: http://localhost:3000/login?username=admin&password=admin123
**Environment**: Frontend E2E tests, authentication flow
**Severity**: Medium
**Priority**: High
**Created**: 2025-01-31
**Status**: Fixed
**Related**: Authentication system, AI features

### Bug ID: [BUG-007]
**Title**: Frontend test looking for non-existent agent "TEST-PC-001"
**Description**: Test fails because it's looking for an agent named "TEST-PC-001" which doesn't exist in the system
**Steps to Reproduce**:
1. Navigate to agents page
2. Test looks for text 'TEST-PC-001'
3. Element is not found
**Expected Behavior**: Either agent should exist or test should look for existing agent names
**Actual Behavior**: Test fails because TEST-PC-001 agent doesn't exist
**Environment**: Frontend E2E tests
**Severity**: Medium
**Priority**: Medium
**Created**: 2025-01-31
**Status**: Fixed
**Related**: Test data consistency, agent management

### Bug ID: [BUG-008]
**Title**: Multiple heading elements causing "strict mode violation" in AI features
**Description**: AI features test fails due to multiple h2 elements being found, causing Playwright strict mode violation
**Steps to Reproduce**:
1. Navigate to AI features page
2. Test uses locator('h1, h2, [data-testid="page-title"]')
3. Multiple elements found: "Agent Manager" and "Dashboard" headings
**Expected Behavior**: Should find unique page title element
**Actual Behavior**: Strict mode violation - 2 elements found instead of 1
**Environment**: Frontend E2E tests with Playwright strict mode
**Severity**: Medium
**Priority**: High
**Created**: 2025-01-31
**Status**: Fixed
**Related**: Page layout, UI structure, AI features

### Bug ID: [BUG-009]
**Title**: API endpoint /api/v1/agents/connected returns 404 Not Found
**Description**: Test for getting connected agents fails because the endpoint returns 404 instead of expected 200 status
**Steps to Reproduce**:
1. Send GET request to /api/v1/agents/connected
2. Expect 200 status code
3. Receive 404 status code
**Expected Behavior**: Endpoint should return 200 with connected agents data
**Actual Behavior**: Returns 404 Not Found error
**Environment**: Backend API test with authenticated user
**Severity**: Medium
**Priority**: Medium
**Created**: 2025-07-31
**Status**: Open
**Related**: Agents Management APIs

### Bug ID: [BUG-010]
**Title**: Command execution API test expects wrong status code
**Description**: POST /api/v1/commands/agent/{agent_id}/execute test fails because it expects 500 but receives 200 or 404
**Steps to Reproduce**:
1. Execute POST request to /api/v1/commands/agent/{agent_id}/execute
2. Test expects status code 500 to be in response
3. Actually receives status codes 200 or 404
**Expected Behavior**: Test should expect correct status codes (200 for success, 404 for agent not found)
**Actual Behavior**: Test expects 500 which is incorrect
**Environment**: Backend API test
**Severity**: Low
**Priority**: Low
**Created**: 2025-07-31
**Status**: Open
**Related**: Commands Management APIs, Test expectation mismatch

### Bug ID: [BUG-011]
**Title**: System info API returns undefined data
**Description**: GET /api/v1/system/info endpoint returns undefined instead of system information object
**Steps to Reproduce**:
1. Send GET request to /api/v1/system/info
2. Expect system information object to be defined
3. Response data is undefined
**Expected Behavior**: Should return system information object with CPU, memory, disk usage etc.
**Actual Behavior**: Returns undefined
**Environment**: Backend API test
**Severity**: Medium
**Priority**: Medium
**Created**: 2025-07-31
**Status**: Open
**Related**: System APIs

### Bug ID: [BUG-012]
**Title**: Settings API validation returns unexpected status codes
**Description**: Settings API validation tests fail because they expect 200 status code but receive 400 or 422
**Steps to Reproduce**:
1. Send request to settings API with validation data
2. Test expects 200 status code
3. Actually receives 400 or 422 status codes
**Expected Behavior**: Either test should expect correct validation status codes or API should return 200
**Actual Behavior**: Mismatch between expected and actual status codes
**Environment**: Backend API Data Validation test
**Severity**: Low
**Priority**: Low
**Created**: 2025-07-31
**Status**: Open
**Related**: API Data Validation, Settings APIs

### Bug ID: [BUG-013]
**Title**: Command API validation returns unexpected status codes
**Description**: Command API validation test fails because it expects 200 status code but receives 400 or 422
**Steps to Reproduce**:
1. Send request to command API with validation data
2. Test expects 200 status code
3. Actually receives 400 or 422 status codes
**Expected Behavior**: Either test should expect correct validation status codes or API should return 200
**Actual Behavior**: Mismatch between expected and actual status codes
**Environment**: Backend API Data Validation test
**Severity**: Low
**Priority**: Low
**Created**: 2025-07-31
**Status**: Open
**Related**: API Data Validation, Commands Management APIs

### Bug ID: [BUG-014]
**Title**: Multiple UI tests are being skipped/interrupted during execution
**Description**: 41 out of 65 tests are being skipped or interrupted, preventing full test coverage of UI components
**Steps to Reproduce**:
1. Run frontend E2E test suite
2. Observe that many UI tests are marked as INTERRUPTED, UNKNOWN, or SKIPPED
3. Tests include Authentication UI, Agents Management UI, Commands UI, AI Features UI, Settings UI tests
**Expected Behavior**: All UI tests should execute successfully
**Actual Behavior**: Most UI tests are skipped, only API tests are running
**Environment**: Frontend E2E Playwright tests
**Severity**: High
**Priority**: High
**Created**: 2025-07-31
**Status**: Fixed
**Related**: UI test infrastructure, test execution flow
**Fix Summary**: Fixed beforeEach hook authentication flow and updated navigation selectors to use href-based selectors instead of text-based selectors. All UI tests now execute properly (0 skipped/interrupted). Test success rate improved from 29.2% to 43.5%.

### Bug ID: [BUG-015]
**Title**: AI command generation API test expectation mismatch
**Description**: AI command generation test was interrupted but shows potential status code expectation issues
**Steps to Reproduce**:
1. Send POST request to /api/v1/commands/ai/generate
2. Test may expect specific status codes
3. API returns various status codes (200, 400, 500, 503) depending on conditions
**Expected Behavior**: Test should handle all possible AI API status codes correctly
**Actual Behavior**: Test interrupted, unclear if expectations match API behavior
**Environment**: Backend API test for AI features
**Severity**: Medium
**Priority**: Medium
**Created**: 2025-07-31
**Status**: Open
**Related**: AI Features APIs, Test expectations

---

## Bug Guidelines

1. **Reproducible**: Include clear steps to reproduce
2. **Specific**: Provide exact error messages and conditions
3. **Impact Assessment**: Document user impact and business impact
4. **Environment Details**: Include relevant technical details
5. **Evidence**: Screenshots, logs, or other supporting materials

## Bug Lifecycle

1. **Open**: Bug reported and confirmed
2. **In Progress**: Fix is being developed
3. **Fixed**: Fix implemented, awaiting verification
4. **Verified**: Fix confirmed working, moved to bug_archive.md

## Severity Levels

- **Critical**: System crashes, data loss, security issues
- **High**: Major functionality broken, blocking users
- **Medium**: Important feature not working correctly
- **Low**: Minor issues, cosmetic problems

## Priority Levels

- **High**: Must fix immediately
- **Medium**: Fix in current sprint/iteration
- **Low**: Fix when time permits