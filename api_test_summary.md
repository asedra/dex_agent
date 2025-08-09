# DexAgents API Test Report

## 📊 Summary
- **Date**: 2025-08-09 17:22:04
- **Total Tests**: 53
- **Passed**: 0 (0.0%)
- **Failed**: 53
- **Average Response Time**: 0.0ms
- **Test Duration**: 0.0s

## 📈 Results by Category

| Category | Passed | Total | Pass Rate |
|----------|--------|-------|-----------|
| agents | 0 | 14 | 0% |
| auth | 0 | 3 | 0% |
| commands | 0 | 9 | 0% |
| connected | 0 | 1 | 0% |
| health | 0 | 1 | 0% |
| installer | 0 | 3 | 0% |
| metrics | 0 | 1 | 0% |
| other | 0 | 1 | 0% |
| settings | 0 | 8 | 0% |
| software | 0 | 9 | 0% |
| stats | 0 | 1 | 0% |
| system | 0 | 2 | 0% |

## ❌ Failed Tests

- **POST /api/v1/auth/login**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/auth/me**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/auth/logout**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/system/health**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/health**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/system/info**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/stats**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/metrics**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/agents/**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/agents/list**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/agents/connected**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/agents/offline**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/agents/desktop-jk5g34l-dexagent**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **PUT /api/v1/agents/desktop-jk5g34l-dexagent**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/agents/desktop-jk5g34l-dexagent/heartbeat**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/agents/desktop-jk5g34l-dexagent/refresh**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/agents/status/desktop-jk5g34l-dexagent**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/agents/desktop-jk5g34l-dexagent/commands**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/agents/desktop-jk5g34l-dexagent/command**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/agents/bulk**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/agents/register**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/agents/seed**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/commands/saved**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/commands/saved**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/commands/execute**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/commands/execute/batch**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/commands/ai/status**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/commands/ai/generate**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/commands/test/status**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/commands/test/mock-agent**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **DELETE /api/v1/commands/test/mock-agent/mock-test-id**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/software/packages**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/software/packages**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/software/packages/upload**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/software/chocolatey/search**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/software/winget/search**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/software/repositories**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/software/repositories**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/software/bulk-install**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/software/jobs**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/settings/**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/settings/**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/settings/test_setting**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **DELETE /api/v1/settings/test_setting**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/settings/chatgpt/config**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/settings/chatgpt/config**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/settings/chatgpt/test**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/settings/reload-ai-service**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/connected**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **GET /api/v1/installer/config**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/installer/create**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
- **POST /api/v1/installer/create-python**
  - Error: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
