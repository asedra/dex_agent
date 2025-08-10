# DexAgents API Test Report

## 📊 Summary
- **Date**: 2025-08-10 00:11:39
- **Total Tests**: 121
- **Passed**: 72 (59.5%)
- **Failed**: 49
- **Average Response Time**: 105.5ms
- **Test Duration**: 12.8s

## 📈 Results by Category

| Category | Passed | Total | Pass Rate |
|----------|--------|-------|-----------|
| agents | 30 | 56 | 54% |
| auth | 3 | 3 | 100% |
| commands | 12 | 16 | 75% |
| connected | 1 | 1 | 100% |
| files | 0 | 12 | 0% |
| health | 1 | 1 | 100% |
| installer | 1 | 3 | 33% |
| metrics | 1 | 1 | 100% |
| other | 1 | 1 | 100% |
| send | 0 | 1 | 0% |
| settings | 8 | 8 | 100% |
| software | 11 | 15 | 73% |
| stats | 1 | 1 | 100% |
| system | 2 | 2 | 100% |

## ❌ Failed Tests

- **POST /api/v1/agents/agent_20250809_211035_156/command**
  - Error: HTTP 400
- **POST /api/v1/commands/agent/agent_20250809_211035_156/execute**
  - Error: HTTP 500
- **POST /api/v1/commands/agent/agent_20250809_211035_156/execute/async**
  - Error: HTTP 500
- **POST /api/v1/commands/test/mock-agent**
  - Error: HTTP 403
- **DELETE /api/v1/commands/test/mock-agent/mock-test-id**
  - Error: HTTP 403
- **GET /api/v1/agents/agent_20250809_211035_156/services**
  - Error: HTTP 400
- **GET /api/v1/agents/agent_20250809_211035_156/services/W32Time**
  - Error: HTTP 400
- **GET /api/v1/agents/agent_20250809_211035_156/services/W32Time/dependencies**
  - Error: HTTP 400
- **POST /api/v1/agents/agent_20250809_211035_156/services/action**
  - Error: HTTP 400
- **PUT /api/v1/agents/agent_20250809_211035_156/services/W32Time/config**
  - Error: HTTP 400
- **POST /api/v1/agents/agent_20250809_211035_156/services/batch**
  - Error: HTTP 400
- **GET /api/v1/agents/agent_20250809_211035_156/registry/keys**
  - Error: HTTP 400
- **GET /api/v1/agents/agent_20250809_211035_156/registry/values**
  - Error: HTTP 400
- **POST /api/v1/agents/agent_20250809_211035_156/registry/search**
  - Error: HTTP 400
- **POST /api/v1/agents/agent_20250809_211035_156/registry/values**
  - Error: HTTP 400
- **DELETE /api/v1/agents/agent_20250809_211035_156/registry/values**
  - Error: HTTP 400
- **DELETE /api/v1/agents/agent_20250809_211035_156/registry/keys**
  - Error: HTTP 400
- **POST /api/v1/agents/agent_20250809_211035_156/registry/export**
  - Error: HTTP 400
- **POST /api/v1/agents/agent_20250809_211035_156/registry/import**
  - Error: HTTP 400
- **POST /api/v1/agents/agent_20250809_211035_156/registry/backup**
  - Error: HTTP 400
- **GET /api/v1/files/agents/agent_20250809_211035_156/files**
  - Error: HTTP 400
- **GET /api/v1/files/agents/agent_20250809_211035_156/files/tree**
  - Error: HTTP 400
- **POST /api/v1/files/agents/agent_20250809_211035_156/files/search**
  - Error: HTTP 400
- **GET /api/v1/files/agents/agent_20250809_211035_156/files/preview**
  - Error: HTTP 400
- **POST /api/v1/files/agents/agent_20250809_211035_156/files/folder**
  - Error: HTTP 400
- **POST /api/v1/files/agents/agent_20250809_211035_156/files/upload**
  - Error: HTTP 400
- **GET /api/v1/files/agents/agent_20250809_211035_156/files/download**
  - Error: HTTP 400
- **POST /api/v1/files/agents/agent_20250809_211035_156/files/operation**
  - Error: HTTP 400
- **POST /api/v1/files/agents/agent_20250809_211035_156/files/compress**
  - Error: HTTP 400
- **POST /api/v1/files/agents/agent_20250809_211035_156/files/extract**
  - Error: HTTP 400
- **POST /api/v1/files/agents/agent_20250809_211035_156/files/batch-upload**
  - Error: HTTP 400
- **DELETE /api/v1/files/agents/agent_20250809_211035_156/files**
  - Error: HTTP 400
- **GET /api/v1/agents/agent_20250809_211035_156/network/adapters**
  - Error: HTTP 400
- **GET /api/v1/agents/agent_20250809_211035_156/network/firewall/rules**
  - Error: HTTP 400
- **GET /api/v1/agents/agent_20250809_211035_156/network/routing/table**
  - Error: HTTP 400
- **POST /api/v1/agents/agent_20250809_211035_156/network/test**
  - Error: HTTP 400
- **POST /api/v1/agents/agent_20250809_211035_156/network/configure**
  - Error: HTTP 400
- **GET /api/v1/agents/agent_20250809_211035_156/processes/**
  - Error: HTTP 400
- **GET /api/v1/agents/agent_20250809_211035_156/processes/tree**
  - Error: HTTP 400
- **POST /api/v1/agents/agent_20250809_211035_156/processes/kill**
  - Error: HTTP 400
- **POST /api/v1/agents/agent_20250809_211035_156/processes/priority**
  - Error: HTTP 400
- **POST /api/v1/agents/agent_20250809_211035_156/processes/suspend-resume**
  - Error: HTTP 400
- **GET /api/v1/software/packages/1**
  - Error: HTTP 404
- **POST /api/v1/software/packages/upload**
  - Error: HTTP 422
- **POST /api/v1/software/agents/agent_20250809_211035_156/install**
  - Error: HTTP 422
- **POST /api/v1/software/bulk-install**
  - Error: HTTP 500
- **POST /api/v1/send/agent_20250809_211035_156/command**
  - Error: HTTP 404
- **POST /api/v1/installer/create**
  - Error: HTTP 422
- **POST /api/v1/installer/create-python**
  - Error: HTTP 422
