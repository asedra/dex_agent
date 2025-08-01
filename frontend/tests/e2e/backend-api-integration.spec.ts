import { test, expect } from '@playwright/test'

test.describe('Backend API Integration Tests', () => {
  let authToken: string

  test.beforeAll(async ({ request }) => {
    // Get authentication token for API calls
    const loginResponse = await request.post('http://localhost:8080/api/v1/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    })
    
    if (loginResponse.ok()) {
      const loginData = await loginResponse.json()
      authToken = loginData.access_token
    }
  })

  test.describe('Authentication APIs', () => {
    test('POST /api/v1/auth/login - User login', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/auth/login', {
        data: {
          username: 'admin',
          password: 'admin123'
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(data.access_token).toBeDefined()
      expect(data.token_type).toBe('bearer')
    })

    test('GET /api/v1/auth/me - Get current user info', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(data.username).toBe('admin')
    })

    test('POST /api/v1/auth/login - Invalid credentials', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/auth/login', {
        data: {
          username: 'admin',
          password: 'wrongpassword'
        }
      })
      
      expect(response.status()).toBe(401)
    })

    test('GET /api/v1/auth/me - Unauthorized access', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/auth/me', {
        headers: {
          'Authorization': 'Bearer invalid-token'
        }
      })
      
      expect(response.status()).toBe(401)
    })
  })

  test.describe('Agents Management APIs', () => {
    test('GET /api/v1/agents/ - List all agents', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/agents/', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(Array.isArray(data)).toBe(true)
    })

    test('GET /api/v1/agents/connected - Get connected agents', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/agents/connected', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(Array.isArray(data)).toBe(true)
    })

    test('GET /api/v1/agents/offline - Get offline agents', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/agents/offline', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(Array.isArray(data)).toBe(true)
    })

    test('GET /api/v1/agents/{agent_id} - Get specific agent (404 for non-existent)', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/agents/non-existent-agent', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(404)
    })

    test('PUT /api/v1/agents/{agent_id} - Update agent (404 for non-existent)', async ({ request }) => {
      const response = await request.put('http://localhost:8080/api/v1/agents/non-existent-agent', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          tags: ['updated-tag']
        }
      })
      
      expect(response.status()).toBe(404)
    })

    test('DELETE /api/v1/agents/{agent_id} - Delete agent (404 for non-existent)', async ({ request }) => {
      const response = await request.delete('http://localhost:8080/api/v1/agents/non-existent-agent', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(404)
    })

    test('POST /api/v1/agents/{agent_id}/refresh - Refresh agent (404 for non-existent)', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/agents/non-existent-agent/refresh', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(404)
    })

    test('POST /api/v1/agents/seed - Create test agents', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/agents/seed', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect([200, 201, 409]).toContain(response.status()) // Success or already exists
    })
  })

  test.describe('Commands Management APIs', () => {
    let createdCommandId: string

    test('GET /api/v1/commands/saved - List saved commands', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/commands/saved', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(Array.isArray(data)).toBe(true)
    })

    test('POST /api/v1/commands/saved - Create new saved command', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/commands/saved', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          name: 'Test Command API',
          command: 'Get-Date',
          description: 'Test command created via API'
        }
      })
      
      expect(response.status()).toBe(201)
      const data = await response.json()
      expect(data.name).toBe('Test Command API')
      expect(data.command).toBe('Get-Date')
      createdCommandId = data.id
    })

    test('GET /api/v1/commands/saved/{command_id} - Get specific command', async ({ request }) => {
      if (!createdCommandId) {
        test.skip()
      }

      const response = await request.get(`http://localhost:8080/api/v1/commands/saved/${createdCommandId}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(data.id).toBe(createdCommandId)
      expect(data.name).toBe('Test Command API')
    })

    test('PUT /api/v1/commands/saved/{command_id} - Update existing command', async ({ request }) => {
      if (!createdCommandId) {
        test.skip()
      }

      const response = await request.put(`http://localhost:8080/api/v1/commands/saved/${createdCommandId}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          name: 'Updated Test Command API',
          command: 'Get-Date -Format "yyyy-MM-dd"',
          description: 'Updated test command'
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(data.name).toBe('Updated Test Command API')
    })

    test('POST /api/v1/commands/agent/{agent_id}/execute - Execute command on agent', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/commands/agent/test-agent/execute', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          command: 'Get-Date'
        }
      })
      
      // Should return success or agent not found
      expect([200, 404]).toContain(response.status())
    })

    test('POST /api/v1/commands/saved/{command_id}/execute - Execute saved command', async ({ request }) => {
      if (!createdCommandId) {
        test.skip()
      }

      const response = await request.post(`http://localhost:8080/api/v1/commands/saved/${createdCommandId}/execute`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          agent_ids: ['test-agent']
        }
      })
      
      // Should return success or validation error
      expect([200, 400, 404]).toContain(response.status())
    })

    test('DELETE /api/v1/commands/saved/{command_id} - Delete command', async ({ request }) => {
      if (!createdCommandId) {
        test.skip()
      }

      const response = await request.delete(`http://localhost:8080/api/v1/commands/saved/${createdCommandId}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(200)
    })

    test('GET /api/v1/commands/saved/{command_id} - Get deleted command (404)', async ({ request }) => {
      if (!createdCommandId) {
        test.skip()
      }

      const response = await request.get(`http://localhost:8080/api/v1/commands/saved/${createdCommandId}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(404)
    })
  })

  test.describe('AI Features APIs', () => {
    test('GET /api/v1/commands/ai/status - Check AI service status', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/commands/ai/status', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(data.available).toBeDefined()
      expect(typeof data.available).toBe('boolean')
    })

    test('POST /api/v1/commands/ai/generate - Generate AI command (may fail without API key)', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/commands/ai/generate', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          prompt: 'List running processes'
        }
      })
      
      // May succeed or fail depending on AI service configuration
      expect([200, 400, 500, 503]).toContain(response.status())
    })

    test('POST /api/v1/commands/ai/test - Test AI service', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/commands/ai/test', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      // May succeed or fail depending on AI service configuration  
      expect([200, 400, 500, 503]).toContain(response.status())
    })
  })

  test.describe('Settings APIs', () => {
    test('GET /api/v1/settings/ - Get all settings', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/settings/', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(Array.isArray(data)).toBe(true)
    })

    test('POST /api/v1/settings/ - Create/update setting', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/settings/', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          key: 'test_setting',
          value: 'test_value',
          description: 'Test setting for API testing'
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(data.key).toBe('test_setting')
      expect(data.value).toBe('test_value')
    })

    test('GET /api/v1/settings/chatgpt/config - Get ChatGPT configuration', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/settings/chatgpt/config', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(data).toBeDefined()
    })

    test('POST /api/v1/settings/chatgpt/config - Update ChatGPT configuration', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/settings/chatgpt/config', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          api_key: 'test-api-key',
          model: 'gpt-3.5-turbo',
          max_tokens: 1000,
          temperature: 0.7
        }
      })
      
      expect(response.status()).toBe(200)
    })

    test('POST /api/v1/settings/chatgpt/test - Test ChatGPT connection', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/settings/chatgpt/test', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      // May succeed or fail depending on API key validity
      expect([200, 400, 401, 500]).toContain(response.status())
    })
  })

  test.describe('System APIs', () => {
    test('GET /api/v1/system/health - System health check', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/system/health')
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(data.status).toBeDefined()
    })

    test('GET /api/v1/system/info - System information', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/system/info', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(data.version).toBeDefined()
    })
  })

  test.describe('Installer APIs', () => {
    test('GET /api/v1/installer/config - Get installer configuration', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/installer/config', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(200)
      const data = await response.json()
      expect(data.server_url).toBeDefined()
    })

    test('POST /api/v1/installer/create-python - Create Python installer', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/installer/create-python', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect([200, 500]).toContain(response.status()) // Success or generation error
      
      if (response.status() === 200) {
        expect(response.headers()['content-type']).toMatch(/application\/octet-stream|application\/zip/)
      }
    })
  })

  test.describe('API Error Handling', () => {
    test('Unauthorized access without token', async ({ request }) => {
      const response = await request.get('http://localhost:8080/api/v1/agents/')
      expect(response.status()).toBe(401)
    })

    test('Invalid JSON in POST request', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/commands/saved', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: 'invalid-json'
      })
      
      expect([400, 422]).toContain(response.status())
    })

    test('Missing required fields in POST request', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/commands/saved', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          // Missing required 'name' and 'command' fields
          description: 'Test'
        }
      })
      
      expect([400, 422]).toContain(response.status())
    })

    test('Invalid HTTP method on endpoint', async ({ request }) => {
      const response = await request.patch('http://localhost:8080/api/v1/system/health', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      expect(response.status()).toBe(405) // Method Not Allowed
    })
  })

  test.describe('API Performance Tests', () => {
    test('System health endpoint response time', async ({ request }) => {
      const startTime = Date.now()
      
      const response = await request.get('http://localhost:8080/api/v1/system/health')
      
      const responseTime = Date.now() - startTime
      expect(response.status()).toBe(200)
      expect(responseTime).toBeLessThan(5000) // Should respond within 5 seconds
    })

    test('Authentication endpoint response time', async ({ request }) => {
      const startTime = Date.now()
      
      const response = await request.post('http://localhost:8080/api/v1/auth/login', {
        data: {
          username: 'admin',
          password: 'admin123'
        }
      })
      
      const responseTime = Date.now() - startTime
      expect(response.status()).toBe(200)
      expect(responseTime).toBeLessThan(3000) // Should authenticate within 3 seconds
    })

    test('Agents list endpoint response time', async ({ request }) => {
      const startTime = Date.now()
      
      const response = await request.get('http://localhost:8080/api/v1/agents/', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      
      const responseTime = Date.now() - startTime
      expect(response.status()).toBe(200)
      expect(responseTime).toBeLessThan(2000) // Should respond within 2 seconds
    })
  })

  test.describe('API Data Validation', () => {
    test('Settings API validates key format', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/settings/', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          key: '', // Empty key should be invalid
          value: 'test',
          description: 'Test'
        }
      })
      
      expect([400, 422]).toContain(response.status())
    })

    test('Command API validates command content', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/commands/saved', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          name: 'Test Command',
          command: '', // Empty command should be invalid
          description: 'Test'
        }
      })
      
      expect([400, 422]).toContain(response.status())
    })

    test('AI generate API validates prompt', async ({ request }) => {
      const response = await request.post('http://localhost:8080/api/v1/commands/ai/generate', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          prompt: '' // Empty prompt should be invalid
        }
      })
      
      expect([400, 422]).toContain(response.status())
    })
  })
})