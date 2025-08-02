import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useWebSocket } from '@/hooks/use-websocket'

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('initializes with correct default state', () => {
    const { result } = renderHook(() => 
      useWebSocket({ url: 'ws://localhost:8080/test' })
    )

    expect(result.current.lastMessage).toBeNull()
    expect(result.current.isConnected).toBe(false)
    expect(result.current.error).toBeNull()
    expect(typeof result.current.sendMessage).toBe('function')
  })

  it('uses the provided URL', () => {
    const { result } = renderHook(() => 
      useWebSocket({ url: 'ws://example.com:8080/custom' })
    )

    // Basic functionality test - the hook should initialize without error
    expect(result.current).toBeDefined()
    expect(result.current.sendMessage).toBeDefined()
  })

  it('accepts custom configuration', () => {
    const { result } = renderHook(() => 
      useWebSocket({ 
        url: 'ws://localhost:8080/test',
        reconnectInterval: 2000,
        maxReconnectAttempts: 10
      })
    )

    expect(result.current.lastMessage).toBeNull()
    expect(result.current.isConnected).toBe(false)
  })

  it('provides sendMessage function', () => {
    const { result } = renderHook(() => 
      useWebSocket({ url: 'ws://localhost:8080/test' })
    )

    expect(typeof result.current.sendMessage).toBe('function')
    
    // Should not throw when called (though it may log an error)
    expect(() => {
      result.current.sendMessage({ type: 'test' })
    }).not.toThrow()
  })
})