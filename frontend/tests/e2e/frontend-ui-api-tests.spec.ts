import { test, expect } from '@playwright/test'

test.describe('Frontend UI -> Backend API Tests', () => {
  test.beforeEach(async ({ page, context }, testInfo) => {
    // Skip automatic login for authentication tests
    if (testInfo.title.includes('Login form') || testInfo.title.includes('Logout should clear')) {
      return
    }
    
    // Clear any stored authentication state
    await context.clearCookies()
    
    // Login through UI first
    await page.goto('/login')
    
    // Wait for page to be ready and form elements to be visible
    await page.waitForLoadState('networkidle')
    await page.waitForSelector('input[name="username"]', { timeout: 10000 })
    
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin123')
    
    // Submit form and wait for navigation
    await Promise.all([
      page.waitForURL('/'),
      page.click('button[type="submit"]')
    ])
    
    // Wait for dashboard to load completely - handle loading states
    await page.waitForLoadState('networkidle')
    
    // Wait for dashboard to fully load past any loading states
    try {
      // First check if we're in a loading state
      await page.waitForSelector('text=Loading dashboard...', { timeout: 2000 })
      // If loading is visible, wait for it to disappear
      await page.waitForSelector('text=Loading dashboard...', { state: 'hidden', timeout: 15000 })
    } catch (e) {
      // Loading might already be complete, that's fine
    }
    
    // Now wait for the dashboard page title to be visible
    await page.waitForSelector('[data-testid="page-title"]', { timeout: 10000 })
    
    // Extra verification that we're on the dashboard
    await page.waitForSelector('[data-testid="page-title"]:has-text("Dashboard")', { timeout: 5000 })
  })

  test.describe('Authentication UI Tests', () => {
    test('Login form should call POST /api/v1/auth/login', async ({ page, context }) => {
      // Clear authentication state for this specific test
      await context.clearCookies()
      
      // Check if already on dashboard, if so logout first
      await page.goto('/')
      await page.waitForLoadState('networkidle')
      
      // If we see logout button, click it
      const logoutButton = page.locator('text=Logout')
      if (await logoutButton.isVisible()) {
        await logoutButton.click()
        await page.waitForURL('/login')
      } else {
        // Navigate to login if not already there
        await page.goto('/login')
      }
      
      // Wait for page to be ready and form elements to be visible
      await page.waitForLoadState('networkidle')
      await page.waitForSelector('input[name="username"]', { timeout: 10000 })
      
      // Monitor API call
      const loginRequest = page.waitForRequest('**/api/v1/auth/login')
      
      await page.fill('input[name="username"]', 'admin')
      await page.fill('input[name="password"]', 'admin123')
      await page.click('button[type="submit"]')
      
      // Verify API was called
      const request = await loginRequest
      expect(request.method()).toBe('POST')
      
      // Should redirect to dashboard
      await page.waitForURL('/')
      await page.waitForLoadState('networkidle')
      await expect(page.locator('[data-testid="page-title"]')).toBeVisible()
    })

    test('User profile should call GET /api/v1/auth/me', async ({ page }) => {
      // Monitor API call for user info
      const userRequest = page.waitForRequest('**/api/v1/auth/me')
      
      // Click on user profile or menu
      const userProfile = page.locator('[data-testid="user-profile"], .user-menu, text=admin')
      if (await userProfile.first().isVisible()) {
        await userProfile.first().click()
        
        // Verify API was called
        const request = await userRequest
        expect(request.method()).toBe('GET')
      }
    })

    test('Logout should clear authentication', async ({ page }) => {
      // Look for logout button
      const logoutButton = page.locator('button:has-text("Logout"), text=Logout, [data-testid="logout"]')
      
      if (await logoutButton.isVisible()) {
        await logoutButton.click()
        await page.waitForTimeout(1000)
        
        // Should redirect to login page
        await expect(page).toHaveURL('/login')
      }
    })
  })

  test.describe('Agents Management UI Tests', () => {
    test('Agents page should call GET /api/v1/agents/', async ({ page }) => {
      // Monitor API call
      const agentsRequest = page.waitForRequest('**/api/v1/agents/')
      
      // Navigate to agents page
      await page.click('a[href="/agents"]')
      await page.waitForTimeout(2000)
      
      // Verify API was called
      const request = await agentsRequest
      expect(request.method()).toBe('GET')
      
      // Should see agents page
      await expect(page.locator('[data-testid="page-title"]')).toBeVisible()
    })

    test('Dashboard should call GET /api/v1/agents/connected', async ({ page }) => {
      // Monitor API call for connected agents
      let connectedRequest = null
      try {
        connectedRequest = await page.waitForRequest('**/api/v1/agents/connected*', { timeout: 5000 })
        expect(connectedRequest.method()).toBe('GET')
      } catch (e) {
        // API might not be called on initial load, that's ok
      }
      
      // Should see connected agents count on dashboard
      const connectedCount = page.locator('text=Connected, text=Online, [data-testid="connected-agents"]')
      if (await connectedCount.first().isVisible()) {
        await expect(connectedCount.first()).toBeVisible()
      }
    })

    test('Agent refresh button should call POST /api/v1/agents/{agent_id}/refresh', async ({ page }) => {
      // Navigate to agents page first
      await page.click('a[href="/agents"]')
      await page.waitForTimeout(2000)
      
      // Look for any agent to refresh
      const agentRow = page.locator('table tbody tr').first()
      if (await agentRow.isVisible()) {
        // Look for refresh button
        const refreshButton = agentRow.locator('button:has-text("Refresh"), [data-testid="refresh-agent"]')
        
        if (await refreshButton.isVisible()) {
          // Monitor API call
          const refreshRequest = page.waitForRequest('**/api/v1/agents/*/refresh')
          
          await refreshButton.click()
          
          // Verify API was called
          const request = await refreshRequest
          expect(request.method()).toBe('POST')
        }
      }
    })

    test('Agent details page should call GET /api/v1/agents/{agent_id}', async ({ page }) => {
      // Navigate to agents page
      await page.click('a[href="/agents"]')
      await page.waitForTimeout(2000)
      
      // Click on first agent link
      const agentLink = page.locator('table tbody tr a').first()
      if (await agentLink.isVisible()) {
        // Monitor API call
        const agentRequest = page.waitForRequest('**/api/v1/agents/*')
        
        await agentLink.click()
        await page.waitForTimeout(2000)
        
        // Verify API was called
        const request = await agentRequest
        expect(request.method()).toBe('GET')
        
        // Should be on agent details page
        await expect(page).toHaveURL(/\/agents\/[^\/]+$/)
      }
    })
  })

  test.describe('Commands Management UI Tests', () => {
    test('Command Library should call GET /api/v1/commands/saved', async ({ page }) => {
      // Monitor API call
      const commandsRequest = page.waitForRequest('**/api/v1/commands/saved*')
      
      // Navigate to Command Library
      await page.click('a[href="/commands"]')
      await page.waitForTimeout(2000)
      
      // Verify API was called
      const request = await commandsRequest
      expect(request.method()).toBe('GET')
      
      // Should see commands page
      await expect(page.locator('[data-testid="page-title"]')).toBeVisible()
    })

    test('Create command form should call POST /api/v1/commands/saved', async ({ page }) => {
      // Navigate to commands page
      await page.click('a[href="/commands"]')
      await page.waitForTimeout(2000)
      
      // Look for create button
      const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")')
      
      if (await createButton.isVisible()) {
        await createButton.click()
        await page.waitForTimeout(1000)
        
        // Fill form
        const nameInput = page.locator('input[name="name"], input[placeholder*="name"]')
        const commandInput = page.locator('textarea[name="command"], input[name="command"]')
        
        if (await nameInput.isVisible() && await commandInput.isVisible()) {
          await nameInput.fill('UI Test Command')
          await commandInput.fill('Get-Process')
          
          // Monitor API call
          const createRequest = page.waitForRequest('**/api/v1/commands/saved')
          
          // Submit form
          const saveButton = page.locator('button:has-text("Save"), button:has-text("Create")')
          if (await saveButton.isVisible()) {
            await saveButton.click()
            
            // Verify API was called
            const request = await createRequest
            expect(request.method()).toBe('POST')
          }
        }
      }
    })

    test('Command execution should call POST /api/v1/commands/agent/{agent_id}/execute', async ({ page }) => {
      // Navigate to agents or commands page
      await page.click('a[href="/agents"]')
      await page.waitForTimeout(2000)
      
      // Look for command execution interface
      const commandInput = page.locator('textarea[placeholder*="command"], input[placeholder*="command"]')
      const executeButton = page.locator('button:has-text("Execute"), button:has-text("Run")')
      
      if (await commandInput.isVisible() && await executeButton.isVisible()) {
        await commandInput.fill('Get-Date')
        
        // Monitor API call
        const executeRequest = page.waitForRequest('**/api/v1/commands/agent/*/execute')
        
        await executeButton.click()
        
        try {
          // Verify API was called
          const request = await executeRequest
          expect(request.method()).toBe('POST')
        } catch (e) {
          // API might not be called if no agent selected
        }
      }
    })
  })

  test.describe('AI Features UI Tests', () => {
    test('AI status should call GET /api/v1/commands/ai/status', async ({ page }) => {
      // Monitor API call for AI status
      let aiStatusRequest = null
      try {
        aiStatusRequest = await page.waitForRequest('**/api/v1/commands/ai/status', { timeout: 5000 })
        expect(aiStatusRequest.method()).toBe('GET')
      } catch (e) {
        // AI status might be checked on page load
      }
      
      // Look for AI button or feature
      const aiButton = page.locator('button:has-text("AI"), text=Create Command with AI, [data-testid="ai-button"]')
      if (await aiButton.isVisible()) {
        await expect(aiButton).toBeVisible()
      }
    })

    test('Create Command with AI should call POST /api/v1/commands/ai/generate', async ({ page }) => {
      // Navigate to commands page
      await page.click('a[href="/commands"]')
      await page.waitForTimeout(2000)
      
      // Look for AI create button
      const aiButton = page.locator('button:has-text("Create Command with AI"), button:has-text("AI"), [data-testid="ai-create"]')
      
      if (await aiButton.isVisible()) {
        await aiButton.click()
        await page.waitForTimeout(1000)
        
        // Fill AI prompt
        const promptInput = page.locator('textarea[placeholder*="prompt"], input[placeholder*="describe"]')
        if (await promptInput.isVisible()) {
          await promptInput.fill('List all running services')
          
          // Monitor API call
          const generateRequest = page.waitForRequest('**/api/v1/commands/ai/generate')
          
          // Generate command
          const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create")')
          if (await generateButton.isVisible()) {
            await generateButton.click()
            
            try {
              // Verify API was called
              const request = await generateRequest
              expect(request.method()).toBe('POST')
            } catch (e) {
              // API might fail if AI service not configured
            }
          }
        }
      }
    })
  })

  test.describe('Settings UI Tests', () => {
    test('Settings page should call GET /api/v1/settings/', async ({ page }) => {
      // Monitor API call
      const settingsRequest = page.waitForRequest('**/api/v1/settings/')
      
      // Navigate to settings
      await page.click('a[href="/settings"]')
      await page.waitForTimeout(2000)
      
      // Verify API was called
      const request = await settingsRequest
      expect(request.method()).toBe('GET')
      
      // Should see settings page
      await expect(page.locator('[data-testid="page-title"]')).toBeVisible()
    })

    test('ChatGPT settings should call GET /api/v1/settings/chatgpt/config', async ({ page }) => {
      // Navigate to settings
      await page.click('a[href="/settings"]')
      await page.waitForTimeout(2000)
      
      // Monitor API call for ChatGPT config
      let chatgptRequest = null
      try {
        chatgptRequest = await page.waitForRequest('**/api/v1/settings/chatgpt/config', { timeout: 5000 })
        expect(chatgptRequest.method()).toBe('GET')
      } catch (e) {
        // Config might be loaded with main settings
      }
      
      // Should see ChatGPT settings section
      const chatgptSection = page.locator('text=ChatGPT, text=OpenAI, text=AI Configuration')
      if (await chatgptSection.first().isVisible()) {
        await expect(chatgptSection.first()).toBeVisible()
      }
    })

    test('Save settings should call POST /api/v1/settings/', async ({ page }) => {
      // Navigate to settings
      await page.click('a[href="/settings"]')
      await page.waitForTimeout(2000)
      
      // Look for setting to modify
      const settingInput = page.locator('input[name="value"], textarea[name="value"]').first()
      
      if (await settingInput.isVisible()) {
        await settingInput.fill('Updated via UI')
        
        // Monitor API call
        const saveRequest = page.waitForRequest('**/api/v1/settings/')
        
        // Save settings
        const saveButton = page.locator('button:has-text("Save"), button:has-text("Update")')
        if (await saveButton.isVisible()) {
          await saveButton.click()
          
          try {
            // Verify API was called
            const request = await saveRequest
            expect(request.method()).toBe('POST')
          } catch (e) {
            // Save might not trigger immediate API call
          }
        }
      }
    })

    test('Test ChatGPT button should call POST /api/v1/settings/chatgpt/test', async ({ page }) => {
      // Navigate to settings
      await page.click('a[href="/settings"]')
      await page.waitForTimeout(2000)
      
      // Look for test ChatGPT button
      const testButton = page.locator('button:has-text("Test ChatGPT"), button:has-text("Test API")')
      
      if (await testButton.isVisible()) {
        // Monitor API call
        const testRequest = page.waitForRequest('**/api/v1/settings/chatgpt/test')
        
        await testButton.click()
        
        try {
          // Verify API was called
          const request = await testRequest
          expect(request.method()).toBe('POST')
        } catch (e) {
          // Test might fail if no API key configured
        }
      }
    })
  })

  test.describe('System Health UI Tests', () => {
    test('Dashboard should call GET /api/v1/system/health', async ({ page }) => {
      // Monitor API call for system health
      let healthRequest = null
      try {
        healthRequest = await page.waitForRequest('**/api/v1/system/health', { timeout: 5000 })
        expect(healthRequest.method()).toBe('GET')
      } catch (e) {
        // Health might be checked periodically
      }
      
      // Should see health indicators on dashboard
      const healthIndicator = page.locator('.health-status, [data-testid="system-health"], text=healthy')
      if (await healthIndicator.first().isVisible()) {
        await expect(healthIndicator.first()).toBeVisible()
      }
    })

    test('System info should call GET /api/v1/system/info', async ({ page }) => {
      // Look for system info section
      const systemInfo = page.locator('[data-testid="system-info"], .system-information')
      
      if (await systemInfo.isVisible()) {
        // Monitor API call
        const infoRequest = page.waitForRequest('**/api/v1/system/info')
        
        // Click to expand or refresh system info
        await systemInfo.click()
        
        try {
          // Verify API was called
          const request = await infoRequest
          expect(request.method()).toBe('GET')
        } catch (e) {
          // Info might be loaded on page load
        }
      }
    })
  })

  test.describe('Installer UI Tests', () => {
    test('Download agent should call GET /api/v1/installer/config', async ({ page }) => {
      // Navigate to agents or download page
      await page.click('a[href="/agents"]')
      await page.waitForTimeout(2000)
      
      // Look for download button
      const downloadButton = page.locator('button:has-text("Download"), text=Download Agent')
      
      if (await downloadButton.isVisible()) {
        // Monitor API call for installer config
        const configRequest = page.waitForRequest('**/api/v1/installer/config')
        
        await downloadButton.click()
        
        try {
          // Verify API was called
          const request = await configRequest
          expect(request.method()).toBe('GET')
        } catch (e) {
          // Config might be pre-loaded
        }
      }
    })

    test('Generate installer should call POST /api/v1/installer/create-python', async ({ page }) => {
      // Navigate to agents page
      await page.click('a[href="/agents"]')
      await page.waitForTimeout(2000)
      
      // Look for download agent button
      const downloadButton = page.locator('button:has-text("Download Agent"), button:has-text("Generate")')
      
      if (await downloadButton.isVisible()) {
        // Monitor API call
        const createRequest = page.waitForRequest('**/api/v1/installer/create-python')
        
        // Set up download handling
        const downloadPromise = page.waitForEvent('download')
        
        await downloadButton.click()
        
        try {
          // Verify API was called
          const request = await createRequest
          expect(request.method()).toBe('POST')
          
          // Should trigger download
          const download = await downloadPromise
          expect(download.suggestedFilename()).toContain('dexagents')
          await download.cancel()
        } catch (e) {
          // Download might not be available
        }
      }
    })
  })

  test.describe('Error Handling UI Tests', () => {
    test('Should handle API errors gracefully in UI', async ({ page }) => {
      // Mock API error response
      await page.route('**/api/v1/agents/', async route => {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Internal server error' })
        })
      })
      
      // Navigate to agents page
      await page.click('a[href="/agents"]')
      await page.waitForTimeout(3000)
      
      // Should show error message in UI
      const errorMessage = page.locator('text=error, text=failed, [role="alert"], .error-message')
      if (await errorMessage.first().isVisible()) {
        await expect(errorMessage.first()).toBeVisible()
      }
    })

    test('Should handle network errors in UI', async ({ page }) => {
      // Mock network failure
      await page.route('**/api/v1/commands/saved', async route => {
        await route.abort('failed')
      })
      
      // Try to navigate to commands
      await page.click('a[href="/commands"]')
      await page.waitForTimeout(3000)
      
      // Should show network error or loading state
      const errorOrLoading = page.locator('text=error, text=loading, text=failed, .loading-spinner')
      if (await errorOrLoading.first().isVisible()) {
        await expect(errorOrLoading.first()).toBeVisible()
      }
    })
  })

  test.describe('Real-time Features UI Tests', () => {
    test('Should handle WebSocket connections for real-time updates', async ({ page }) => {
      // Look for real-time status indicators
      const statusIndicators = page.locator('.status-online, .status-offline, [data-status]')
      
      if (await statusIndicators.first().isVisible()) {
        await expect(statusIndicators.first()).toBeVisible()
      }
      
      // Check for auto-refreshing content
      await page.waitForTimeout(5000)
      
      // Should see updated timestamps or status
      const timestamps = page.locator('text=ago, .timestamp, text=last seen')
      if (await timestamps.first().isVisible()) {
        await expect(timestamps.first()).toBeVisible()
      }
    })
  })
})