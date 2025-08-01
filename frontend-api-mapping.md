# Frontend-Backend API Mapping for E2E Tests

## 🔐 Authentication APIs
| API Endpoint | Method | Frontend UI Location | Test Scenarios |
|-------------|--------|---------------------|----------------|
| `/api/v1/auth/login` | POST | Login page form | Username/password submission, success/error handling |
| `/api/v1/auth/me` | GET | User profile/header | Display current user info |
| `/api/v1/auth/logout` | POST | Header/sidebar logout button | Logout functionality |

## 👥 Agents Management APIs
| API Endpoint | Method | Frontend UI Location | Test Scenarios |
|-------------|--------|---------------------|----------------|
| `/api/v1/agents/` | GET | Agents page table/list | Display all agents, refresh agents list |
| `/api/v1/agents/{agent_id}` | GET | Agent details page | View specific agent details |
| `/api/v1/agents/{agent_id}` | PUT | Agent edit dialog/form | Update agent information |
| `/api/v1/agents/{agent_id}` | DELETE | Agent delete button | Delete agent confirmation |
| `/api/v1/agents/connected` | GET | Dashboard stats, Agents filter | Show online agents count |
| `/api/v1/agents/offline` | GET | Dashboard alerts, Agents filter | Show offline agents |
| `/api/v1/agents/{agent_id}/refresh` | POST | Agent refresh button | Manual agent refresh |
| `/api/v1/agents/seed` | POST | Debug/dev buttons | Test data creation |

## 💻 Commands Management APIs
| API Endpoint | Method | Frontend UI Location | Test Scenarios |
|-------------|--------|---------------------|----------------|
| `/api/v1/commands/saved` | GET | Commands library page | Load saved commands list |
| `/api/v1/commands/saved` | POST | Create command dialog | Create new saved command |
| `/api/v1/commands/saved/{command_id}` | GET | Command details dialog | View command details |
| `/api/v1/commands/saved/{command_id}` | PUT | Edit command dialog | Update existing command |
| `/api/v1/commands/saved/{command_id}` | DELETE | Delete command button | Delete command confirmation |
| `/api/v1/commands/saved/{command_id}/execute` | POST | Execute command button | Run saved command on agents |
| `/api/v1/commands/agent/{agent_id}/execute` | POST | Agent command execution | Execute command on specific agent |

## 🤖 AI Features APIs
| API Endpoint | Method | Frontend UI Location | Test Scenarios |
|-------------|--------|---------------------|----------------|
| `/api/v1/commands/ai/status` | GET | AI button availability | Check if AI features are enabled |
| `/api/v1/commands/ai/generate` | POST | "Create Command with AI" dialog | Generate commands using AI |
| `/api/v1/commands/ai/test` | POST | AI command test button | Test AI-generated commands |

## ⚙️ Settings APIs
| API Endpoint | Method | Frontend UI Location | Test Scenarios |
|-------------|--------|---------------------|----------------|
| `/api/v1/settings/` | GET | Settings page | Load all settings |
| `/api/v1/settings/` | POST | Settings save buttons | Create/update settings |
| `/api/v1/settings/chatgpt/config` | GET | ChatGPT settings section | Load ChatGPT configuration |
| `/api/v1/settings/chatgpt/config` | POST | ChatGPT save button | Save ChatGPT API key |
| `/api/v1/settings/chatgpt/test` | POST | Test ChatGPT button | Test API connection |

## 🏥 System APIs
| API Endpoint | Method | Frontend UI Location | Test Scenarios |
|-------------|--------|---------------------|----------------|
| `/api/v1/system/health` | GET | Dashboard health indicators | System status check |
| `/api/v1/system/info` | GET | Dashboard system info | Display system information |

## 📦 Installer APIs
| API Endpoint | Method | Frontend UI Location | Test Scenarios |
|-------------|--------|---------------------|----------------|
| `/api/v1/installer/create-python` | POST | "Download Agent" button | Download Python agent package |
| `/api/v1/installer/config` | GET | Agent download dialog | Get installer configuration |

## 🔗 WebSocket APIs
| API Endpoint | Method | Frontend UI Location | Test Scenarios |
|-------------|--------|---------------------|----------------|
| `/api/v1/connected` | GET | Real-time agent status | WebSocket connection status |
| `/api/v1/send/{agent_id}/command` | POST | Real-time command execution | WebSocket command sending |

---

## 📋 Missing Frontend Test Coverage

Based on API analysis, these areas need comprehensive E2E testing:

### 🔴 High Priority Missing Tests:
1. **Agent Details Page** - Individual agent view with all operations
2. **Command Execution Flow** - Complete command execution on agents
3. **Settings Page Integration** - All settings CRUD operations
4. **Real-time Features** - WebSocket communication testing
5. **Agent Download** - Full agent package download flow
6. **Error Handling** - API error scenarios for all endpoints

### 🟡 Medium Priority Missing Tests:
1. **Batch Operations** - Multiple agent operations
2. **Command History** - Historical command execution view
3. **System Health Dashboard** - Real-time system monitoring
4. **Agent Registration** - New agent onboarding flow

### 🟢 Already Covered (but need improvement):
1. **Authentication Flow** - Login/logout (needs stability fixes)
2. **Agents List** - Basic agents display (needs real data)
3. **AI Features** - Basic AI button testing (needs integration)

---

## 🎯 Next Steps for Comprehensive Testing:

1. **Create API Integration Tests** - Test every frontend action against real backend APIs
2. **Add Real Data Tests** - Use actual agent data instead of mocks
3. **Test Error Scenarios** - Network failures, API errors, validation failures
4. **Add Performance Tests** - API response time validation
5. **Test Real-time Features** - WebSocket connection and updates