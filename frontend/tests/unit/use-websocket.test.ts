import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useWebSocket } from '@/hooks/use-websocket'

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = MockWebSocket.CONNECTING
  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  url: string

  constructor(url: string) {
    this.url = url
    // Simulate async connection
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 10)
  }

  send = vi.fn()

  close = vi.fn((code?: number, reason?: string) => {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close', { code, reason }))
    }
  })
}

// Create a spy for WebSocket constructor
const MockWebSocketSpy = vi.fn().mockImplementation((url: string) => new MockWebSocket(url))
global.WebSocket = MockWebSocketSpy as any

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    MockWebSocketSpy.mockClear()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('initializes with correct default state', () => {
    const { result } = renderHook(() => 
      useWebSocket({ url: 'ws://localhost:8080/test' })
    )

    expect(result.current.lastMessage).toBeNull()
    expect(result.current.readyState).toBe(WebSocket.CONNECTING)
    expect(result.current.isConnected).toBe(false)
    expect(result.current.isConnecting).toBe(true)
    expect(result.current.error).toBeNull()
    expect(typeof result.current.sendMessage).toBe('function')
  })

  it('establishes WebSocket connection', async () => {
    const { result } = renderHook(() => 
      useWebSocket({ url: 'ws://localhost:8080/test' })
    )

    expect(result.current.isConnecting).toBe(true)

    // Fast-forward timers to trigger connection
    act(() => {
      vi.advanceTimersByTime(50)
    })

    expect(result.current.isConnected).toBe(true)
    expect(result.current.isConnecting).toBe(false)
    expect(result.current.readyState).toBe(WebSocket.OPEN)
  })

  it('handles incoming messages', async () => {
    const { result } = renderHook(() => 
      useWebSocket({ url: 'ws://localhost:8080/test' })
    )

    // Wait for connection
    act(() => {
      vi.advanceTimersByTime(50)
    })

    const testMessage = {
      type: 'test_message',
      data: { value: 'hello world' }
    }

    // Simulate receiving a message
    act(() => {
      const mockSocket = result.current.socket as any
      if (mockSocket && mockSocket.onmessage) {
        mockSocket.onmessage({
          data: JSON.stringify(testMessage)
        } as MessageEvent)
      }
    })

    expect(result.current.lastMessage).toMatchObject({
      type: 'test_message',
      data: { value: 'hello world' }
    })
    expect(result.current.lastMessage?.timestamp).toBeDefined()
  })

  it('handles raw message data when JSON parsing fails', async () => {
    const { result } = renderHook(() => 
      useWebSocket({ url: 'ws://localhost:8080/test' })
    )

    // Wait for connection
    act(() => {
      vi.advanceTimersByTime(50)
    })

    // Simulate receiving invalid JSON
    act(() => {
      const mockSocket = result.current.socket as any
      if (mockSocket && mockSocket.onmessage) {
        mockSocket.onmessage({
          data: 'invalid json'
        } as MessageEvent)
      }
    })

    expect(result.current.lastMessage).toMatchObject({
      type: 'raw',
      data: 'invalid json'
    })
  })

  it('sends messages when connected', async () => {
    const { result } = renderHook(() => 
      useWebSocket({ url: 'ws://localhost:8080/test' })
    )

    // Wait for connection
    act(() => {
      vi.advanceTimersByTime(50)
    })

    const testMessage = { type: 'ping', data: 'test' }

    act(() => {
      result.current.sendMessage(testMessage)
    })

    const mockSocket = result.current.socket as any
    expect(mockSocket.send).toHaveBeenCalledWith(JSON.stringify(testMessage))
  })

  it('handles send message when not connected', async () => {
    const { result } = renderHook(() => 
      useWebSocket({ url: 'ws://localhost:8080/test' })
    )

    // Don't wait for connection, try to send immediately
    const testMessage = { type: 'ping', data: 'test' }

    act(() => {
      result.current.sendMessage(testMessage)
    })

    expect(result.current.error).toBe('WebSocket is not connected')
  })

  it('handles WebSocket errors', async () => {
    const { result } = renderHook(() => 
      useWebSocket({ url: 'ws://localhost:8080/test' })
    )

    // Simulate WebSocket error
    act(() => {
      const mockSocket = result.current.socket as any
      if (mockSocket && mockSocket.onerror) {
        mockSocket.onerror(new Event('error'))
      }
    })

    expect(result.current.error).toBe('WebSocket connection error')
    expect(result.current.isConnecting).toBe(false)
  })

  it('handles WebSocket close and attempts reconnection', async () => {
    const { result } = renderHook(() => 
      useWebSocket({ 
        url: 'ws://localhost:8080/test',
        reconnectInterval: 1000,
        maxReconnectAttempts: 3
      })
    )

    // Wait for initial connection
    act(() => {
      vi.advanceTimersByTime(50)
    })

    expect(result.current.isConnected).toBe(true)

    // Simulate connection close (not clean close)
    act(() => {
      const mockSocket = result.current.socket as any
      if (mockSocket && mockSocket.onclose) {
        mockSocket.onclose(new CloseEvent('close', { code: 1006, reason: 'Connection lost' }))
      }
    })

    expect(result.current.isConnected).toBe(false)
    expect(result.current.error).toContain('Connection lost. Retrying... (1/3)')

    // Fast-forward to trigger reconnection attempt
    act(() => {
      vi.advanceTimersByTime(1000)
    })

    // Should create a new WebSocket instance for reconnection
    expect(MockWebSocketSpy).toHaveBeenCalledTimes(2)
  })

  it('stops reconnecting after max attempts', async () => {
    const { result } = renderHook(() => 
      useWebSocket({ 
        url: 'ws://localhost:8080/test',
        reconnectInterval: 100,
        maxReconnectAttempts: 2
      })
    )

    // Wait for initial connection
    act(() => {
      vi.advanceTimersByTime(50)
    })

    // Simulate connection failures
    act(() => {
      const mockSocket = MockWebSocketSpy.mock.results[0].value
      if (mockSocket.onclose) {
        mockSocket.onclose(new CloseEvent('close', { code: 1006, reason: 'Connection lost' }))
      }
    })

    // Wait for first reconnection attempt
    act(() => {
      vi.advanceTimersByTime(150)
    })

    // Simulate second connection failure
    act(() => {
      const mockSocket = MockWebSocketSpy.mock.results[1].value
      if (mockSocket.onclose) {
        mockSocket.onclose(new CloseEvent('close', { code: 1006, reason: 'Connection lost' }))
      }
    })

    // Wait for second reconnection attempt
    act(() => {
      vi.advanceTimersByTime(150)
    })

    // Simulate third connection failure (should exceed max attempts)
    act(() => {
      const mockSocket = MockWebSocketSpy.mock.results[2].value
      if (mockSocket.onclose) {
        mockSocket.onclose(new CloseEvent('close', { code: 1006, reason: 'Connection lost' }))
      }
    })

    expect(result.current.error).toBe('Failed to reconnect after maximum attempts')
  })

  it('does not reconnect on clean close', async () => {
    const { result } = renderHook(() => 
      useWebSocket({ url: 'ws://localhost:8080/test' })
    )

    // Wait for connection
    act(() => {
      vi.advanceTimersByTime(50)
    })

    // Simulate clean close (code 1000)
    act(() => {
      const mockSocket = result.current.socket as any
      if (mockSocket && mockSocket.onclose) {
        mockSocket.onclose(new CloseEvent('close', { code: 1000, reason: 'Normal closure' }))
      }
    })

    expect(result.current.isConnected).toBe(false)
    expect(result.current.error).toBeNull()

    // Should not attempt to reconnect
    act(() => {
      vi.advanceTimersByTime(5000)
    })

    expect(MockWebSocketSpy).toHaveBeenCalledTimes(1) // Only initial connection
  })

  it('cleans up on unmount', async () => {
    const { result, unmount } = renderHook(() => 
      useWebSocket({ url: 'ws://localhost:8080/test' })
    )

    // Wait for connection
    act(() => {
      vi.advanceTimersByTime(50)
    })

    // Get the mock socket instance from the constructor calls
    const mockSocketInstance = MockWebSocketSpy.mock.results[0].value

    act(() => {
      unmount()
    })

    expect(mockSocketInstance.close).toHaveBeenCalledWith(1000, 'Component unmounting')
  })

  it('uses custom reconnect configuration', () => {
    const { result } = renderHook(() => 
      useWebSocket({ 
        url: 'ws://localhost:8080/test',
        reconnectInterval: 2000,
        maxReconnectAttempts: 10
      })
    )

    // Wait for connection
    act(() => {
      vi.advanceTimersByTime(50)
    })

    // Simulate connection close
    act(() => {
      const mockSocket = result.current.socket as any
      if (mockSocket && mockSocket.onclose) {
        mockSocket.onclose(new CloseEvent('close', { code: 1006, reason: 'Connection lost' }))
      }
    })

    expect(result.current.error).toContain('Connection lost. Retrying... (1/10)')

    // Should use custom reconnect interval
    act(() => {
      vi.advanceTimersByTime(1999)
    })
    expect(MockWebSocketSpy).toHaveBeenCalledTimes(1) // No reconnection yet

    act(() => {
      vi.advanceTimersByTime(1)
    })
    expect(MockWebSocketSpy).toHaveBeenCalledTimes(2) // Reconnection triggered
  })
})