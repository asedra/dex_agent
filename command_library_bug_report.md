# Command Library Page - Bug Report

## Test Execution Summary
- **Date**: 2025-08-12
- **Page Tested**: Command Library (/commands)
- **Test Type**: Frontend functionality and API integration

## Issues Found

### 1. Critical Issues
1. **Get-ComputerInfo Command Failure**
   - The "Get System Information" command uses `Get-ComputerInfo` which is not recognized
   - Error: "The term 'Get-ComputerInfo' is not recognized as a name of a cmdlet"
   - Impact: Core functionality failure for system information retrieval

### 2. Frontend Issues
2. **Frontend Test Timeout**
   - Playwright tests timeout when trying to access the Command Library page
   - Tests fail to complete within 30-60 second timeout period
   - Impact: Automated testing cannot be performed reliably

### 3. UI/UX Issues
3. **AI Button Behavior**
   - "Create Command with AI" button is always visible even when AI is not configured
   - Clicking the button redirects to settings page instead of showing an inline message
   - Impact: Confusing user experience

4. **Command Execution Dependencies**
   - Command execution requires agent to be online
   - No clear indication when no online agents are available
   - Impact: Users may not understand why commands fail

5. **Search and Filter Limitations**
   - Search functionality may not filter commands in real-time
   - Category filter might not work properly
   - Impact: Difficulty finding specific commands in large lists

### 4. API Issues
6. **Agent Response Format Inconsistency**
   - `/api/v1/agents` endpoint returns inconsistent data formats (sometimes strings, sometimes objects)
   - Makes it difficult to reliably parse agent information
   - Impact: Integration issues with frontend

## Reproduction Steps

### For Get-ComputerInfo Issue:
1. Login to the application (admin/admin123)
2. Navigate to Command Library
3. Find or create "Get System Information" command
4. Select an agent and execute the command
5. Command fails with PowerShell error

### For Frontend Test Timeout:
1. Run Playwright tests: `npx playwright test commands.spec.ts`
2. Tests timeout after 30-60 seconds

### For AI Button Issue:
1. Without OpenAI API key configured
2. Navigate to Command Library
3. Click "Create Command with AI"
4. Redirects to settings instead of showing inline message

## Expected Behavior
1. System information commands should use compatible PowerShell cmdlets
2. Frontend tests should complete within reasonable time
3. AI button should indicate when not configured
4. Clear feedback when no agents are available
5. Real-time search and filtering
6. Consistent API response formats

## Severity: High
Multiple core functionality issues affecting user experience and system reliability.

## Affected Components
- Frontend: Command Library page
- Backend: Command execution API
- Agent: PowerShell command compatibility
- Testing: Playwright test suite