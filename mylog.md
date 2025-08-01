root@DESKTOP-JK5G34L:/home/ali/dex_agent#   python3 scripts/unified_test_runner.py
🚀 Unified Test Runner Started
============================================================
Mode: Parallel
Time: 2025-07-31 23:53:06

🐳 Checking Docker services...
✅ Docker services running: postgres, backend, frontend
⏳ Waiting for services to be ready...
⏳ Waiting for services... (Command '['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:8080/api/v1/system/health']' timed out after 5 seconds)
✅ All services are ready

🚀 Running Tests in Parallel
==================================================

🔧 Running Backend Tests
==================================================

🌐 Running Frontend Tests
==================================================
🚀 Frontend Test Runner Started
==================================================
🔍 Checking if frontend services are running...
🚀 Backend Test Runner Started
==================================================
🔍 Checking if backend services are running...
✅ Frontend services are running

🧪 Running frontend E2E tests...
============================================================
🚀 Starting Playwright E2E test execution
📊 Live test results will appear below:
------------------------------------------------------------

> dexagents-frontend@1.0.0 test:e2e
> playwright test --reporter=html,json --timeout=30000

[2025-07-31 23:53:21] ✅ PASS System Health Check
    Status: healthy

✅ Backend services are running

🧪 Running backend API tests...
============================================================
🚀 Starting comprehensive API test execution
📊 Live test results will appear below:
------------------------------------------------------------
============================================================
DexAgents API Comprehensive Test Suite
============================================================

[2025-07-31 23:53:21] ✅ PASS System Health Check
    Status: healthy

[2025-07-31 23:53:21] ✅ PASS User Login
    Token received, expires: 691200

[2025-07-31 23:53:21] ✅ PASS Token Validation
    User: admin

[2025-07-31 23:53:22] ✅ PASS Authorization Protection
    Correctly rejected unauthorized access

[2025-07-31 23:53:22] ✅ PASS Agents List
    Found 1 agents

[2025-07-31 23:53:22] ✅ PASS Saved Commands
    Found 6 saved commands

[2025-07-31 23:53:22] ✅ PASS AI Status
    AI Available: False - ChatGPT API key not configured

[2025-07-31 23:53:22] ✅ PASS AI Command Generation
    Expected failure (test API key or service unavailable): HTTP 500

[2025-07-31 23:53:22] ✅ PASS ChatGPT Settings
    ChatGPT API key setting not found (can be added via UI)

[2025-07-31 23:53:22] ✅ PASS AI Button Always Visible
    AI status properly indicates availability: False

[2025-07-31 23:53:22] ✅ PASS AI Redirect to Settings
    AI generation fails as expected: Failed to generate command

[2025-07-31 23:53:22] ✅ PASS Command Execution
    Command sent successfully

============================================================
TEST SUMMARY
============================================================
Total Tests: 12
Passed: 12
Failed: 0
Success Rate: 100.0%

🎉 ALL TESTS PASSED!

============================================================
🏁 Backend test execution completed!
📄 Test report saved to: /home/ali/dex_agent/backend_test_results.md

📊 Test Summary:
   Total: 12 tests
   Passed: 12
   Failed: 0

✅ All backend tests passed!

🔧 Backend Tests: ✅ PASSED







