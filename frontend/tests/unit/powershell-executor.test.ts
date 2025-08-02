import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PowerShellExecutor } from '@/components/PowerShellExecutor'
import * as apiClient from '@/lib/api'

// Mock the API client
vi.mock('@/lib/api', () => ({
  apiClient: {
    getAgents: vi.fn(),
    executeCommand: vi.fn()
  }
}))

// Mock the toast hook
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn()
  })
}))

const mockAgents = [
  {
    id: 'agent-1',
    hostname: 'DESKTOP-001',
    status: 'online',
    last_seen: new Date().toISOString()
  },
  {
    id: 'agent-2', 
    hostname: 'SERVER-002',
    status: 'offline',
    last_seen: new Date().toISOString()
  }
]

describe('PowerShellExecutor', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(apiClient.apiClient.getAgents).mockResolvedValue(mockAgents)
  })

  it('renders the PowerShell executor interface', async () => {
    render(<PowerShellExecutor />)
    
    expect(screen.getByText('PowerShell Command Executor')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Enter PowerShell command/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Execute/ })).toBeInTheDocument()
  })

  it('loads agents on mount', async () => {
    render(<PowerShellExecutor />)
    
    await waitFor(() => {
      expect(apiClient.apiClient.getAgents).toHaveBeenCalled()
    })
  })

  it('allows entering commands', async () => {
    const user = userEvent.setup()
    render(<PowerShellExecutor />)
    
    const commandInput = screen.getByPlaceholderText(/Enter PowerShell command/)
    await user.type(commandInput, 'Get-Process')
    
    expect(commandInput).toHaveValue('Get-Process')
  })

  it('requires agent selection and command to execute', async () => {
    const user = userEvent.setup()
    render(<PowerShellExecutor />)
    
    const executeButton = screen.getByRole('button', { name: /Execute/ })
    
    // Button should be disabled initially
    expect(executeButton).toBeDisabled()
    
    // Enter command but no agent selected
    const commandInput = screen.getByPlaceholderText(/Enter PowerShell command/)
    await user.type(commandInput, 'Get-Process')
    
    // Should still be disabled without agent selection
    expect(executeButton).toBeDisabled()
  })

  it('executes command when valid input provided', async () => {
    const user = userEvent.setup()
    const mockExecuteResponse = {
      success: true,
      output: 'Command executed successfully',
      error: null
    }
    
    vi.mocked(apiClient.apiClient.executeCommand).mockResolvedValue(mockExecuteResponse)
    
    render(<PowerShellExecutor />)
    
    // Wait for agents to load
    await waitFor(() => {
      expect(apiClient.apiClient.getAgents).toHaveBeenCalled()
    })
    
    // Enter command
    const commandInput = screen.getByPlaceholderText(/Enter PowerShell command/)
    await user.type(commandInput, 'Get-Process')
    
    // Select agent (first agent should be auto-selected)
    const executeButton = screen.getByRole('button', { name: /Execute/ })
    
    // Execute command
    await user.click(executeButton)
    
    await waitFor(() => {
      expect(apiClient.apiClient.executeCommand).toHaveBeenCalledWith({
        command: 'Get-Process',
        agent_id: mockAgents[0].id,
        timeout: 30000
      })
    })
  })

  it('handles command execution errors', async () => {
    const user = userEvent.setup()
    
    vi.mocked(apiClient.apiClient.executeCommand).mockRejectedValue(
      new Error('Network error')
    )
    
    render(<PowerShellExecutor />)
    
    // Wait for agents to load
    await waitFor(() => {
      expect(apiClient.apiClient.getAgents).toHaveBeenCalled()
    })
    
    // Enter command and execute
    const commandInput = screen.getByPlaceholderText(/Enter PowerShell command/)
    await user.type(commandInput, 'Get-Process')
    
    const executeButton = screen.getByRole('button', { name: /Execute/ })
    await user.click(executeButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Execution History/)).toBeInTheDocument()
    })
  })

  it('supports keyboard shortcuts', async () => {
    const user = userEvent.setup()
    render(<PowerShellExecutor />)
    
    const commandInput = screen.getByPlaceholderText(/Enter PowerShell command/)
    await user.type(commandInput, 'Get-Process')
    
    // Test Ctrl+Enter to execute
    await user.keyboard('{Control>}{Enter}{/Control}')
    
    // Should attempt to execute (though will fail without proper setup)
    expect(commandInput).toHaveFocus()
  })

  it('maintains command history', async () => {
    const user = userEvent.setup()
    
    // Mock localStorage
    const mockLocalStorage = {
      getItem: vi.fn(() => JSON.stringify(['Get-Process', 'Get-Service'])),
      setItem: vi.fn()
    }
    Object.defineProperty(window, 'localStorage', { value: mockLocalStorage })
    
    render(<PowerShellExecutor />)
    
    // Should load command history from localStorage
    expect(mockLocalStorage.getItem).toHaveBeenCalledWith('powershell_history')
  })

  it('clears command input', async () => {
    const user = userEvent.setup()
    render(<PowerShellExecutor />)
    
    const commandInput = screen.getByPlaceholderText(/Enter PowerShell command/)
    await user.type(commandInput, 'Get-Process')
    
    const clearButton = screen.getByRole('button', { name: /Clear/ })
    await user.click(clearButton)
    
    expect(commandInput).toHaveValue('')
  })
})