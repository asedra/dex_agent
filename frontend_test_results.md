# Frontend Test Results

## Latest Test Run

**Date**: 2025-08-01 05:05
**Tester**: Automated Script
**Test Environment**: Local Docker
**Test Command**: npm run test:e2e
**Browser**: Chromium (Playwright)
**Duration**: Unknown

## Test Results Summary

- **Total Tests**: 65
- **Passed**: 16
- **Failed**: 5
- **Skipped**: 44
- **Success Rate**: 24.6%

## Test Details

### ✅ POST /api/v1/auth/login - User login - PASSED
**File**: Authentication APIs
**Duration**: Unknown

### ✅ GET /api/v1/auth/me - Get current user info - PASSED
**File**: Authentication APIs
**Duration**: Unknown

### ✅ POST /api/v1/auth/login - Invalid credentials - PASSED
**File**: Authentication APIs
**Duration**: Unknown

### ✅ GET /api/v1/auth/me - Unauthorized access - PASSED
**File**: Authentication APIs
**Duration**: Unknown

### ✅ GET /api/v1/agents/ - List all agents - PASSED
**File**: Agents Management APIs
**Duration**: Unknown

### ❌ GET /api/v1/agents/connected - Get connected agents - FAILED
**File**: Agents Management APIs
**Duration**: Unknown
**Error**: Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoBe[2m([22m[32mexpected[39m[2m) // Object.is equality[22m

Expected: [32m200[39m
Received: [31m404[39m

### ⏭️ GET /api/v1/agents/offline - Get offline agents - INTERRUPTED
**File**: Agents Management APIs
**Duration**: Unknown

### ⏭️ GET /api/v1/agents/{agent_id} - Get specific agent (404 for non-existent) - UNKNOWN
**File**: Agents Management APIs
**Duration**: Unknown

### ⏭️ PUT /api/v1/agents/{agent_id} - Update agent (404 for non-existent) - INTERRUPTED
**File**: Agents Management APIs
**Duration**: Unknown

### ⏭️ DELETE /api/v1/agents/{agent_id} - Delete agent (404 for non-existent) - UNKNOWN
**File**: Agents Management APIs
**Duration**: Unknown

### ⏭️ POST /api/v1/agents/{agent_id}/refresh - Refresh agent (404 for non-existent) - UNKNOWN
**File**: Agents Management APIs
**Duration**: Unknown

### ⏭️ POST /api/v1/agents/seed - Create test agents - UNKNOWN
**File**: Agents Management APIs
**Duration**: Unknown

### ⏭️ GET /api/v1/commands/saved - List saved commands - INTERRUPTED
**File**: Commands Management APIs
**Duration**: Unknown

### ⏭️ POST /api/v1/commands/saved - Create new saved command - UNKNOWN
**File**: Commands Management APIs
**Duration**: Unknown

### ⏭️ GET /api/v1/commands/saved/{command_id} - Get specific command - UNKNOWN
**File**: Commands Management APIs
**Duration**: Unknown

### ⏭️ PUT /api/v1/commands/saved/{command_id} - Update existing command - UNKNOWN
**File**: Commands Management APIs
**Duration**: Unknown

### ❌ POST /api/v1/commands/agent/{agent_id}/execute - Execute command on agent - FAILED
**File**: Commands Management APIs
**Duration**: Unknown
**Error**: Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoContain[2m([22m[32mexpected[39m[2m) // indexOf[22m

Expected value: [32m500[39m
Received array: [31m[200, 404][39m

### ⏭️ POST /api/v1/commands/saved/{command_id}/execute - Execute saved command - INTERRUPTED
**File**: Commands Management APIs
**Duration**: Unknown

### ⏭️ DELETE /api/v1/commands/saved/{command_id} - Delete command - UNKNOWN
**File**: Commands Management APIs
**Duration**: Unknown

### ⏭️ GET /api/v1/commands/saved/{command_id} - Get deleted command (404) - UNKNOWN
**File**: Commands Management APIs
**Duration**: Unknown

### ✅ GET /api/v1/commands/ai/status - Check AI service status - PASSED
**File**: AI Features APIs
**Duration**: Unknown

### ⏭️ POST /api/v1/commands/ai/generate - Generate AI command (may fail without API key) - INTERRUPTED
**File**: AI Features APIs
**Duration**: Unknown

### ⏭️ POST /api/v1/commands/ai/test - Test AI service - UNKNOWN
**File**: AI Features APIs
**Duration**: Unknown

### ⏭️ GET /api/v1/settings/ - Get all settings - UNKNOWN
**File**: Settings APIs
**Duration**: Unknown

### ✅ POST /api/v1/settings/ - Create/update setting - PASSED
**File**: Settings APIs
**Duration**: Unknown

### ✅ GET /api/v1/settings/chatgpt/config - Get ChatGPT configuration - PASSED
**File**: Settings APIs
**Duration**: Unknown

### ✅ POST /api/v1/settings/chatgpt/config - Update ChatGPT configuration - PASSED
**File**: Settings APIs
**Duration**: Unknown

### ⏭️ POST /api/v1/settings/chatgpt/test - Test ChatGPT connection - INTERRUPTED
**File**: Settings APIs
**Duration**: Unknown

### ✅ GET /api/v1/system/health - System health check - PASSED
**File**: System APIs
**Duration**: Unknown

### ❌ GET /api/v1/system/info - System information - FAILED
**File**: System APIs
**Duration**: Unknown
**Error**: Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoBeDefined[2m()[22m

Received: [31mundefined[39m

### ⏭️ GET /api/v1/installer/config - Get installer configuration - UNKNOWN
**File**: Installer APIs
**Duration**: Unknown

### ⏭️ POST /api/v1/installer/create-python - Create Python installer - UNKNOWN
**File**: Installer APIs
**Duration**: Unknown

### ✅ Unauthorized access without token - PASSED
**File**: API Error Handling
**Duration**: Unknown

### ✅ Invalid JSON in POST request - PASSED
**File**: API Error Handling
**Duration**: Unknown

### ✅ Missing required fields in POST request - PASSED
**File**: API Error Handling
**Duration**: Unknown

### ⏭️ Invalid HTTP method on endpoint - INTERRUPTED
**File**: API Error Handling
**Duration**: Unknown

### ✅ System health endpoint response time - PASSED
**File**: API Performance Tests
**Duration**: Unknown

### ✅ Authentication endpoint response time - PASSED
**File**: API Performance Tests
**Duration**: Unknown

### ✅ Agents list endpoint response time - PASSED
**File**: API Performance Tests
**Duration**: Unknown

### ❌ Settings API validates key format - FAILED
**File**: API Data Validation
**Duration**: Unknown
**Error**: Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoContain[2m([22m[32mexpected[39m[2m) // indexOf[22m

Expected value: [32m200[39m
Received array: [31m[400, 422][39m

### ⏭️ Command API validates command content - INTERRUPTED
**File**: API Data Validation
**Duration**: Unknown

### ⏭️ AI generate API validates prompt - UNKNOWN
**File**: API Data Validation
**Duration**: Unknown

### ⏭️ Login form should call POST /api/v1/auth/login - INTERRUPTED
**File**: Authentication UI Tests
**Duration**: Unknown

### ⏭️ User profile should call GET /api/v1/auth/me - INTERRUPTED
**File**: Authentication UI Tests
**Duration**: Unknown

### ❌ Logout should clear authentication - FAILED
**File**: Authentication UI Tests
**Duration**: Unknown
**Error**: Error: locator.isVisible: Unexpected token "=" while parsing css selector "button:has-text("Logout"), text=Logout, [data-testid="logout"]". Did you mean to CSS.escape it?
Call log:
[2m    - checking visibility of button:has-text("Logout"), text=Logout, [data-testid="logout"][22m


### ⏭️ Agents page should call GET /api/v1/agents/ - INTERRUPTED
**File**: Agents Management UI Tests
**Duration**: Unknown

### ⏭️ Dashboard should call GET /api/v1/agents/connected - UNKNOWN
**File**: Agents Management UI Tests
**Duration**: Unknown

### ⏭️ Agent refresh button should call POST /api/v1/agents/{agent_id}/refresh - UNKNOWN
**File**: Agents Management UI Tests
**Duration**: Unknown

### ⏭️ Agent details page should call GET /api/v1/agents/{agent_id} - UNKNOWN
**File**: Agents Management UI Tests
**Duration**: Unknown

### ⏭️ Command Library should call GET /api/v1/commands/saved - UNKNOWN
**File**: Commands Management UI Tests
**Duration**: Unknown

### ⏭️ Create command form should call POST /api/v1/commands/saved - UNKNOWN
**File**: Commands Management UI Tests
**Duration**: Unknown

### ⏭️ Command execution should call POST /api/v1/commands/agent/{agent_id}/execute - UNKNOWN
**File**: Commands Management UI Tests
**Duration**: Unknown

### ⏭️ AI status should call GET /api/v1/commands/ai/status - UNKNOWN
**File**: AI Features UI Tests
**Duration**: Unknown

### ⏭️ Create Command with AI should call POST /api/v1/commands/ai/generate - UNKNOWN
**File**: AI Features UI Tests
**Duration**: Unknown

### ⏭️ Settings page should call GET /api/v1/settings/ - UNKNOWN
**File**: Settings UI Tests
**Duration**: Unknown

### ⏭️ ChatGPT settings should call GET /api/v1/settings/chatgpt/config - UNKNOWN
**File**: Settings UI Tests
**Duration**: Unknown

### ⏭️ Save settings should call POST /api/v1/settings/ - UNKNOWN
**File**: Settings UI Tests
**Duration**: Unknown

### ⏭️ Test ChatGPT button should call POST /api/v1/settings/chatgpt/test - UNKNOWN
**File**: Settings UI Tests
**Duration**: Unknown

### ⏭️ Dashboard should call GET /api/v1/system/health - UNKNOWN
**File**: System Health UI Tests
**Duration**: Unknown

### ⏭️ System info should call GET /api/v1/system/info - UNKNOWN
**File**: System Health UI Tests
**Duration**: Unknown

### ⏭️ Download agent should call GET /api/v1/installer/config - UNKNOWN
**File**: Installer UI Tests
**Duration**: Unknown

### ⏭️ Generate installer should call POST /api/v1/installer/create-python - UNKNOWN
**File**: Installer UI Tests
**Duration**: Unknown

### ⏭️ Should handle API errors gracefully in UI - UNKNOWN
**File**: Error Handling UI Tests
**Duration**: Unknown

### ⏭️ Should handle network errors in UI - UNKNOWN
**File**: Error Handling UI Tests
**Duration**: Unknown

### ⏭️ Should handle WebSocket connections for real-time updates - UNKNOWN
**File**: Real-time Features UI Tests
**Duration**: Unknown


## Failed Tests Summary

1. **GET /api/v1/agents/connected - Get connected agents**: Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoBe[2m([22m[32mexpected[39m[2m) // Object.is equality[22m

Expected: [32m200[39m
Received: [31m404[39m
   - File: Agents Management APIs
2. **POST /api/v1/commands/agent/{agent_id}/execute - Execute command on agent**: Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoContain[2m([22m[32mexpected[39m[2m) // indexOf[22m

Expected value: [32m500[39m
Received array: [31m[200, 404][39m
   - File: Commands Management APIs
3. **GET /api/v1/system/info - System information**: Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoBeDefined[2m()[22m

Received: [31mundefined[39m
   - File: System APIs
4. **Settings API validates key format**: Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoContain[2m([22m[32mexpected[39m[2m) // indexOf[22m

Expected value: [32m200[39m
Received array: [31m[400, 422][39m
   - File: API Data Validation
5. **Logout should clear authentication**: Error: locator.isVisible: Unexpected token "=" while parsing css selector "button:has-text("Logout"), text=Logout, [data-testid="logout"]". Did you mean to CSS.escape it?
Call log:
[2m    - checking visibility of button:has-text("Logout"), text=Logout, [data-testid="logout"][22m

   - File: Authentication UI Tests

## Browser Compatibility

- **Chromium**: Tested (Playwright default)
- **Firefox**: Not tested in this run
- **Safari**: Not tested in this run

## Performance Notes

- All UI interactions completed within acceptable timeouts
- Page load times were within normal ranges
- 5 tests failed - see details above
- Test execution completed in Unknown

## New Issues Found

- **GET /api/v1/agents/connected - Get connected agents**: Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoBe[2m([22m[32mexpected[39m[2m) // Object.is equality[22m

Expected: [32m200[39m
Received: [31m404[39m
- **POST /api/v1/commands/agent/{agent_id}/execute - Execute command on agent**: Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoContain[2m([22m[32mexpected[39m[2m) // indexOf[22m

Expected value: [32m500[39m
Received array: [31m[200, 404][39m
- **GET /api/v1/system/info - System information**: Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoBeDefined[2m()[22m

Received: [31mundefined[39m
- **Settings API validates key format**: Error: [2mexpect([22m[31mreceived[39m[2m).[22mtoContain[2m([22m[32mexpected[39m[2m) // indexOf[22m

Expected value: [32m200[39m
Received array: [31m[400, 422][39m
- **Logout should clear authentication**: Error: locator.isVisible: Unexpected token "=" while parsing css selector "button:has-text("Logout"), text=Logout, [data-testid="logout"]". Did you mean to CSS.escape it?
Call log:
[2m    - checking visibility of button:has-text("Logout"), text=Logout, [data-testid="logout"][22m


## Overall Status: ❌ FAILED

Some frontend E2E tests failed. Review failed tests above.
