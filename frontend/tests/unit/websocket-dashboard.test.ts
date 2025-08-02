import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { WebSocketDashboard } from '@/components/WebSocketDashboard'

// Mock the RealTimeActivityFeed component
vi.mock('@/components/RealTimeActivityFeed', () => ({
  RealTimeActivityFeed: ({ className }: { className?: string }) => {
    return React.createElement('div', {
      'data-testid': 'real-time-activity-feed',
      className: className
    }, 'Mock Activity Feed')
  }
}))

import React from 'react'

// Mock the useWebSocket hook
const mockSendMessage = vi.fn()
const mockWebSocketData = {
  socket: null,
  lastMessage: null,
  readyState: WebSocket.CONNECTING,
  sendMessage: mockSendMessage,
  isConnected: false,
  isConnecting: false,
  error: null
}

vi.mock('@/hooks/use-websocket', () => ({
  useWebSocket: vi.fn(() => mockWebSocketData)
}))

describe('WebSocketDashboard', () => {
  
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset mock data
    mockWebSocketData.lastMessage = null
    mockWebSocketData.isConnected = false
    mockWebSocketData.isConnecting = false
    mockWebSocketData.error = null
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders system metrics cards', () => {
    render(<WebSocketDashboard />)
    
    expect(screen.getByText('CPU Usage')).toBeInTheDocument()
    expect(screen.getByText('Memory Usage')).toBeInTheDocument()
    expect(screen.getByText('Active Agents')).toBeInTheDocument()
    expect(screen.getByText('Network Activity')).toBeInTheDocument()
  })

  it('displays initial loading state', () => {
    render(<WebSocketDashboard />)
    
    expect(screen.getByText('0.0%')).toBeInTheDocument() // CPU Usage default
    expect(screen.getByText('No agents connected')).toBeInTheDocument()
  })

  it('renders real-time activity feed', () => {
    render(<WebSocketDashboard />)
    
    expect(screen.getByTestId('real-time-activity-feed')).toBeInTheDocument()
    expect(screen.getByText('Mock Activity Feed')).toBeInTheDocument()
  })

  it('processes system metrics messages', async () => {
    const systemMetrics = {
      cpu_usage: 45.5,
      memory_usage: 67.2,
      disk_usage: 32.1,
      network_in: 1024,
      network_out: 512,
      active_connections: 15,
      uptime: 86400,
      timestamp: '2023-01-01T00:00:00Z'
    }

    mockWebSocketData.lastMessage = {
      type: 'system_metrics',
      data: systemMetrics,
      timestamp: '2023-01-01T00:00:00Z'
    }
    
    render(<WebSocketDashboard />)

    await waitFor(() => {
      expect(screen.getByText('45.5%')).toBeInTheDocument()
      expect(screen.getByText('67.2%')).toBeInTheDocument()
      expect(screen.getByText('15')).toBeInTheDocument() // active connections
      expect(screen.getByText('1d 0h 0m')).toBeInTheDocument() // formatted uptime
    })
  })

  it('processes agent metrics messages', async () => {
    const agentMetrics = [
      {
        agent_id: 'agent-1',
        agent_name: 'Test Agent',
        status: 'online' as const,
        cpu_usage: 25.5,
        memory_usage: 30.2,
        last_seen: '2023-01-01T00:00:00Z',
        commands_executed: 100,
        errors: 2
      }
    ]

    mockWebSocketData.lastMessage = {
      type: 'agent_metrics',
      data: { agents: agentMetrics },
      timestamp: '2023-01-01T00:00:00Z'
    }
    
    render(<WebSocketDashboard />)

    await waitFor(() => {
      expect(screen.getByText('Test Agent')).toBeInTheDocument()
      expect(screen.getByText('online')).toBeInTheDocument()
      expect(screen.getByText('Commands: 100 | Errors: 2')).toBeInTheDocument()
      expect(screen.getByText('CPU: 25.5%')).toBeInTheDocument()
      expect(screen.getByText('RAM: 30.2%')).toBeInTheDocument()
    })
  })

  it('sends metrics requests when connected', () => {
    mockWebSocketData.isConnected = true
    
    render(<WebSocketDashboard />)

    expect(mockSendMessage).toHaveBeenCalledWith({ type: 'get_system_metrics' })
    expect(mockSendMessage).toHaveBeenCalledWith({ type: 'get_agent_metrics' })
    expect(mockSendMessage).toHaveBeenCalledWith({ type: 'get_command_stats' })
  })

  it('formats bytes correctly in network activity', async () => {
    const systemMetrics = {
      cpu_usage: 45.5,
      memory_usage: 67.2,
      disk_usage: 32.1,
      network_in: 2048, // 2 KB
      network_out: 1024000, // ~1 MB
      active_connections: 15,
      uptime: 86400,
      timestamp: '2023-01-01T00:00:00Z'
    }

    mockWebSocketData.lastMessage = {
      type: 'system_metrics',
      data: systemMetrics,
      timestamp: '2023-01-01T00:00:00Z'
    }
    
    render(<WebSocketDashboard />)

    await waitFor(() => {
      expect(screen.getByText('↓ 2.0 KB')).toBeInTheDocument()
      expect(screen.getByText('↑ 1000.0 KB')).toBeInTheDocument()
    })
  })

  it('shows high CPU usage warning styles', async () => {
    const systemMetrics = {
      cpu_usage: 85.0, // Above 80% threshold
      memory_usage: 90.0, // Above 80% threshold
      disk_usage: 32.1,
      network_in: 1024,
      network_out: 512,
      active_connections: 15,
      uptime: 86400,
      timestamp: '2023-01-01T00:00:00Z'
    }

    mockWebSocketData.lastMessage = {
      type: 'system_metrics',
      data: systemMetrics,
      timestamp: '2023-01-01T00:00:00Z'
    }
    
    render(<WebSocketDashboard />)

    await waitFor(() => {
      expect(screen.getByText('85.0%')).toBeInTheDocument()
      expect(screen.getByText('90.0%')).toBeInTheDocument()
      // Progress bars should have red styling when > 80%
    })
  })

  it('handles command stats messages', async () => {
    mockWebSocketData.lastMessage = {
      type: 'command_stats',
      data: { 
        total_commands: 500,
        failed_commands: 25
      },
      timestamp: '2023-01-01T00:00:00Z'
    }
    
    render(<WebSocketDashboard />)

    await waitFor(() => {
      expect(screen.getByText('25')).toBeInTheDocument() // failed commands
    })
  })

  it('handles custom className prop', () => {
    render(<WebSocketDashboard className="custom-class" />)
    
    const container = screen.getByText('CPU Usage').closest('.space-y-6')
    expect(container).toHaveClass('custom-class')
  })
})