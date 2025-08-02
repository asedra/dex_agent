import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { WebSocketDashboard } from '@/components/WebSocketDashboard'
import { useWebSocket } from '@/hooks/use-websocket'

// Mock the RealTimeActivityFeed component
vi.mock('@/components/RealTimeActivityFeed', () => ({
  RealTimeActivityFeed: () => React.createElement('div', { 'data-testid': 'activity-feed' }, 'Activity Feed')
}))

// Mock the useWebSocket hook
vi.mock('@/hooks/use-websocket')

const mockUseWebSocket = vi.mocked(useWebSocket)

describe('WebSocketDashboard', () => {
  beforeEach(() => {
    mockUseWebSocket.mockReturnValue({
      lastMessage: null,
      isConnected: false,
      sendMessage: vi.fn(),
      socket: null,
      readyState: 0,
      isConnecting: false,
      error: null
    })
  })

  it('renders without crashing', () => {
    const element = React.createElement(WebSocketDashboard)
    render(element)
    
    expect(screen.getByText('CPU Usage')).toBeInTheDocument()
    expect(screen.getByText('Memory Usage')).toBeInTheDocument()
    expect(screen.getByText('Active Agents')).toBeInTheDocument()
    expect(screen.getByText('Network Activity')).toBeInTheDocument()
  })

  it('displays initial state correctly', () => {
    const element = React.createElement(WebSocketDashboard)
    render(element)
    
    // There are multiple 0.0% values (CPU, Memory, Disk), so use getAllByText
    expect(screen.getAllByText('0.0%')).toHaveLength(3)
    expect(screen.getByText('No agents connected')).toBeInTheDocument()
  })

  it('renders activity feed', () => {
    const element = React.createElement(WebSocketDashboard)
    render(element)
    
    expect(screen.getByTestId('activity-feed')).toBeInTheDocument()
  })

  it('handles custom className', () => {
    const element = React.createElement(WebSocketDashboard, { className: 'custom-test-class' })
    const { container } = render(element)
    
    expect(container.firstChild).toHaveClass('custom-test-class')
  })

  it('processes system metrics data', () => {
    mockUseWebSocket.mockReturnValue({
      lastMessage: {
        type: 'system_metrics',
        data: {
          cpu_usage: 75.5,
          memory_usage: 45.2,
          network_in: 1024,
          network_out: 512,
          active_connections: 10,
          uptime: 3600
        }
      },
      isConnected: true,
      sendMessage: vi.fn(),
      socket: {},
      readyState: 1,
      isConnecting: false,
      error: null
    })

    const element = React.createElement(WebSocketDashboard)
    render(element)
    
    expect(screen.getByText('75.5%')).toBeInTheDocument()
    expect(screen.getByText('45.2%')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getByText('1h 0m')).toBeInTheDocument()
  })
})