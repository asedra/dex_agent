# DexAgents API Test Report

## 📊 Summary
- **Date**: 2025-08-12 13:52:11
- **Total Tests**: 117
- **Passed**: 104 (88.9%)
- **Failed**: 13
- **Average Response Time**: 288.2ms
- **Test Duration**: 34.3s

## 📈 Results by Category

| Category | Passed | Total | Pass Rate |
|----------|--------|-------|-----------|
| agents | 48 | 51 | 94% |
| auth | 3 | 3 | 100% |
| commands | 15 | 17 | 88% |
| connected | 1 | 1 | 100% |
| files | 10 | 12 | 83% |
| health | 1 | 1 | 100% |
| installer | 1 | 3 | 33% |
| metrics | 1 | 1 | 100% |
| other | 1 | 1 | 100% |
| send | 1 | 1 | 100% |
| settings | 8 | 8 | 100% |
| software | 11 | 15 | 73% |
| stats | 1 | 1 | 100% |
| system | 2 | 2 | 100% |

## ❌ Failed Tests

- **POST /api/v1/commands/test/mock-agent**
  - Error: HTTP 403
- **DELETE /api/v1/commands/test/mock-agent/mock-test-id**
  - Error: HTTP 403
- **DELETE /api/v1/agents/desktop-jk5g34l-dexagent/registry/values**
  - Error: HTTP 500
- **DELETE /api/v1/agents/desktop-jk5g34l-dexagent/registry/keys**
  - Error: HTTP 500
- **POST /api/v1/agents/desktop-jk5g34l-dexagent/registry/import**
  - Error: HTTP 500
- **GET /api/v1/files/agents/desktop-jk5g34l-dexagent/files/preview**
  - Error: HTTP 500
- **POST /api/v1/files/agents/desktop-jk5g34l-dexagent/files/upload**
  - Error: HTTP 500
- **GET /api/v1/software/packages/1**
  - Error: HTTP 404
- **POST /api/v1/software/packages/upload**
  - Error: HTTP 422
- **POST /api/v1/software/agents/desktop-jk5g34l-dexagent/install**
  - Error: HTTP 422
- **POST /api/v1/software/bulk-install**
  - Error: HTTP 500
- **POST /api/v1/installer/create**
  - Error: HTTP 422
- **POST /api/v1/installer/create-python**
  - Error: HTTP 422
