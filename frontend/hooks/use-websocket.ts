'use client'

import { useEffect, useRef, useState, useCallback } from 'react'

export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

export interface WebSocketConfig {
  url: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export interface UseWebSocketReturn {
  socket: WebSocket | null
  lastMessage: WebSocketMessage | null
  readyState: number
  sendMessage: (message: any) => void
  isConnected: boolean
  isConnecting: boolean
  error: string | null
}

export function useWebSocket(config: WebSocketConfig): UseWebSocketReturn {
  const { url, reconnectInterval = 3000, maxReconnectAttempts = 5 } = config
  
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [readyState, setReadyState] = useState<number>(WebSocket.CONNECTING)
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const reconnectAttempts = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  const connect = useCallback(() => {
    if (socket?.readyState === WebSocket.OPEN) {
      return
    }

    setIsConnecting(true)
    setError(null)

    try {
      const ws = new WebSocket(url)
      
      ws.onopen = () => {
        console.log('WebSocket connected')
        setSocket(ws)
        setReadyState(WebSocket.OPEN)
        setIsConnected(true)
        setIsConnecting(false)
        setError(null)
        reconnectAttempts.current = 0
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage({
            ...message,
            timestamp: new Date().toISOString()
          })
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
          setLastMessage({
            type: 'raw',
            data: event.data,
            timestamp: new Date().toISOString()
          })
        }
      }

      ws.onerror = (event) => {
        console.error('WebSocket error:', event)
        setError('WebSocket connection error')
        setIsConnecting(false)
      }

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        setSocket(null)
        setReadyState(WebSocket.CLOSED)
        setIsConnected(false)
        setIsConnecting(false)

        // Attempt to reconnect if not a clean close
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++
          setError(`Connection lost. Retrying... (${reconnectAttempts.current}/${maxReconnectAttempts})`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          setError('Failed to reconnect after maximum attempts')
        }
      }

      setSocket(ws)
      setReadyState(WebSocket.CONNECTING)
      
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err)
      setError('Failed to create WebSocket connection')
      setIsConnecting(false)
    }
  }, [url, reconnectInterval, maxReconnectAttempts])

  const sendMessage = useCallback((message: any) => {
    if (socket?.readyState === WebSocket.OPEN) {
      try {
        socket.send(JSON.stringify(message))
      } catch (err) {
        console.error('Failed to send WebSocket message:', err)
        setError('Failed to send message')
      }
    } else {
      console.warn('WebSocket is not connected')
      setError('WebSocket is not connected')
    }
  }, [socket])

  useEffect(() => {
    connect()
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (socket) {
        socket.close(1000, 'Component unmounting')
      }
    }
  }, [connect])

  return {
    socket,
    lastMessage,
    readyState,
    sendMessage,
    isConnected,
    isConnecting,
    error
  }
}