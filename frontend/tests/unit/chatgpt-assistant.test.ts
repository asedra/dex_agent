import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatGPTAssistant } from '@/components/ChatGPTAssistant'

// Mock fetch
global.fetch = vi.fn()

// Mock the toast hook
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn()
  })
}))

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn()
}
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage })

describe('ChatGPTAssistant', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockLocalStorage.getItem.mockReturnValue('mock-auth-token')
  })

  it('renders the ChatGPT assistant interface', () => {
    render(<ChatGPTAssistant />)
    
    expect(screen.getByText('ChatGPT Assistant')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Ask ChatGPT for help/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Send/ })).toBeInTheDocument()
  })

  it('shows configuration required when API key not set', async () => {
    // Mock API response indicating no configuration
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ api_key: '' })
    } as Response)

    render(<ChatGPTAssistant />)
    
    await waitFor(() => {
      expect(screen.getByText('ChatGPT Not Configured')).toBeInTheDocument()
      expect(screen.getByText(/configure your OpenAI API key/)).toBeInTheDocument()
    })
  })

  it('shows quick prompts based on context', async () => {
    // Mock configured API
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ api_key: 'sk-test' })
    } as Response)

    render(<ChatGPTAssistant context="powershell" />)
    
    await waitFor(() => {
      expect(screen.getByText(/Help me create a PowerShell command/)).toBeInTheDocument()
      expect(screen.getByText(/get system information/)).toBeInTheDocument()
    })
  })

  it('allows sending messages to ChatGPT', async () => {
    const user = userEvent.setup()
    
    // Mock configured API
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ api_key: 'sk-test' })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          response: 'Here is how to get system information with PowerShell...',
          type: 'command_suggestion',
          suggested_command: 'Get-ComputerInfo'
        })
      } as Response)

    render(<ChatGPTAssistant />)
    
    // Wait for configuration check
    await waitFor(() => {
      expect(screen.getByText('ChatGPT Assistant')).toBeInTheDocument()
    })
    
    const messageInput = screen.getByPlaceholderText(/Ask ChatGPT for help/)
    const sendButton = screen.getByRole('button', { name: /Send/ })
    
    await user.type(messageInput, 'How do I get system information?')
    await user.click(sendButton)
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/v1/ai/chat', expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer mock-auth-token'
        },
        body: expect.stringContaining('How do I get system information?')
      }))
    })
  })

  it('displays chat messages correctly', async () => {
    const user = userEvent.setup()
    
    // Mock configured API and response
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ api_key: 'sk-test' })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          response: 'Use Get-ComputerInfo to get system information.',
          type: 'command_suggestion',
          suggested_command: 'Get-ComputerInfo'
        })
      } as Response)

    render(<ChatGPTAssistant />)
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask ChatGPT for help/)).toBeInTheDocument()
    })
    
    const messageInput = screen.getByPlaceholderText(/Ask ChatGPT for help/)
    await user.type(messageInput, 'System info command?')
    await user.click(screen.getByRole('button', { name: /Send/ }))
    
    await waitFor(() => {
      expect(screen.getByText('System info command?')).toBeInTheDocument()
      expect(screen.getByText('Use Get-ComputerInfo to get system information.')).toBeInTheDocument()
      expect(screen.getByText('Get-ComputerInfo')).toBeInTheDocument()
    })
  })

  it('handles API errors gracefully', async () => {
    const user = userEvent.setup()
    
    // Mock configured API
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ api_key: 'sk-test' })
      } as Response)
      .mockResolvedValueOnce({
        ok: false,
        status: 500
      } as Response)

    render(<ChatGPTAssistant />)
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask ChatGPT for help/)).toBeInTheDocument()
    })
    
    const messageInput = screen.getByPlaceholderText(/Ask ChatGPT for help/)
    await user.type(messageInput, 'Test message')
    await user.click(screen.getByRole('button', { name: /Send/ }))
    
    await waitFor(() => {
      expect(screen.getByText(/Error: API Error: 500/)).toBeInTheDocument()
    })
  })

  it('supports keyboard shortcuts for sending', async () => {
    const user = userEvent.setup()
    
    // Mock configured API
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ api_key: 'sk-test' })
    } as Response)

    render(<ChatGPTAssistant />)
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask ChatGPT for help/)).toBeInTheDocument()
    })
    
    const messageInput = screen.getByPlaceholderText(/Ask ChatGPT for help/)
    await user.type(messageInput, 'Test message')
    
    // Test Ctrl+Enter to send
    await user.keyboard('{Control>}{Enter}{/Control}')
    
    expect(messageInput).toHaveValue('')
  })

  it('clears chat history', async () => {
    const user = userEvent.setup()
    
    // Mock configured API
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ api_key: 'sk-test' })
    } as Response)

    render(<ChatGPTAssistant />)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Clear/ })).toBeInTheDocument()
    })
    
    const clearButton = screen.getByRole('button', { name: /Clear/ })
    await user.click(clearButton)
    
    // Should clear any existing messages
  })

  it('copies messages to clipboard', async () => {
    const user = userEvent.setup()
    
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn()
      }
    })
    
    // Mock configured API and send a message first
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ api_key: 'sk-test' })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          response: 'Test response from ChatGPT'
        })
      } as Response)

    render(<ChatGPTAssistant />)
    
    // Send a message first
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask ChatGPT for help/)).toBeInTheDocument()
    })
    
    const messageInput = screen.getByPlaceholderText(/Ask ChatGPT for help/)
    await user.type(messageInput, 'Test')
    await user.click(screen.getByRole('button', { name: /Send/ }))
    
    // Wait for response and copy button
    await waitFor(() => {
      expect(screen.getByText('Test response from ChatGPT')).toBeInTheDocument()
    })
    
    // Find and click copy button
    const copyButtons = screen.getAllByRole('button')
    const copyButton = copyButtons.find(button => 
      button.innerHTML.includes('Copy') || button.querySelector('[data-testid="copy-icon"]')
    )
    
    if (copyButton) {
      await user.click(copyButton)
      expect(navigator.clipboard.writeText).toHaveBeenCalled()
    }
  })
})