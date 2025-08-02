'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Activity, 
  Server, 
  Monitor, 
  Cpu, 
  HardDrive, 
  MemoryStick,
  Network,
  Zap,
  TrendingUp,
  AlertTriangle
} from 'lucide-react'
import { useWebSocket } from '@/hooks/use-websocket'
import { RealTimeActivityFeed } from './RealTimeActivityFeed'

interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_in: number
  network_out: number
  active_connections: number
  uptime: number
  timestamp: string
}

interface AgentMetrics {
  agent_id: string
  agent_name: string
  status: 'online' | 'offline' | 'error'
  cpu_usage: number
  memory_usage: number
  last_seen: string
  commands_executed: number
  errors: number
}

interface WebSocketDashboardProps {
  className?: string
}

export function WebSocketDashboard({ className = '' }: WebSocketDashboardProps) {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null)
  const [agentMetrics, setAgentMetrics] = useState<AgentMetrics[]>([])
  const [connectionStats, setConnectionStats] = useState({
    total_agents: 0,
    online_agents: 0,
    offline_agents: 0,
    total_commands: 0,
    failed_commands: 0
  })

  // Get WebSocket URL for metrics
  const wsUrl = typeof window !== 'undefined' 
    ? `ws://${window.location.hostname}:8080/ws/metrics`
    : 'ws://localhost:8080/ws/metrics'
  
  const { lastMessage, isConnected, sendMessage } = useWebSocket({
    url: wsUrl,
    reconnectInterval: 5000,
    maxReconnectAttempts: 10
  })

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      switch (lastMessage.type) {
        case 'system_metrics':
          setSystemMetrics(lastMessage.data)
          break
        
        case 'agent_metrics':
          setAgentMetrics(lastMessage.data.agents || [])
          setConnectionStats(prev => ({
            ...prev,
            total_agents: lastMessage.data.agents?.length || 0,
            online_agents: lastMessage.data.agents?.filter((a: AgentMetrics) => a.status === 'online').length || 0,
            offline_agents: lastMessage.data.agents?.filter((a: AgentMetrics) => a.status === 'offline').length || 0
          }))
          break

        case 'command_stats':
          setConnectionStats(prev => ({
            ...prev,
            total_commands: lastMessage.data.total_commands || 0,
            failed_commands: lastMessage.data.failed_commands || 0
          }))
          break

        default:
          break
      }
    }
  }, [lastMessage])

  // Request metrics when connected
  useEffect(() => {
    if (isConnected) {
      // Request initial metrics
      sendMessage({ type: 'get_system_metrics' })
      sendMessage({ type: 'get_agent_metrics' })
      sendMessage({ type: 'get_command_stats' })

      // Set up periodic updates
      const interval = setInterval(() => {
        sendMessage({ type: 'get_system_metrics' })
        sendMessage({ type: 'get_agent_metrics' })
      }, 5000) // Update every 5 seconds

      return () => clearInterval(interval)
    }
  }, [isConnected, sendMessage])

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
  }

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) return `${days}d ${hours}h ${minutes}m`
    if (hours > 0) return `${hours}h ${minutes}m`
    return `${minutes}m`
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Real-time System Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemMetrics?.cpu_usage?.toFixed(1) || '0.0'}%
            </div>
            <Progress 
              value={systemMetrics?.cpu_usage || 0} 
              className={`mt-2 ${systemMetrics?.cpu_usage && systemMetrics.cpu_usage > 80 ? '[&>div]:bg-red-500' : ''}`}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
            <MemoryStick className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemMetrics?.memory_usage?.toFixed(1) || '0.0'}%
            </div>
            <Progress 
              value={systemMetrics?.memory_usage || 0} 
              className={`mt-2 ${systemMetrics?.memory_usage && systemMetrics.memory_usage > 80 ? '[&>div]:bg-red-500' : ''}`}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
            <Monitor className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {connectionStats.online_agents}
            </div>
            <p className="text-xs text-muted-foreground">
              of {connectionStats.total_agents} total agents
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Network Activity</CardTitle>
            <Network className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-sm font-bold">
              ↓ {formatBytes(systemMetrics?.network_in || 0)}
            </div>
            <div className="text-sm font-bold">
              ↑ {formatBytes(systemMetrics?.network_out || 0)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent Status Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" />
              Agent Status Overview
            </CardTitle>
            <CardDescription>
              Real-time status of all connected agents
            </CardDescription>
          </CardHeader>
          <CardContent>
            {agentMetrics.length === 0 ? (
              <div className="text-center text-muted-foreground py-4">
                No agents connected
              </div>
            ) : (
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {agentMetrics.slice(0, 5).map((agent) => (
                  <div key={agent.agent_id} className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1">
                        <div className={`w-2 h-2 rounded-full ${
                          agent.status === 'online' ? 'bg-green-500' : 
                          agent.status === 'offline' ? 'bg-gray-500' : 'bg-red-500'
                        }`} />
                        <Badge variant={agent.status === 'online' ? 'default' : 'secondary'}>
                          {agent.status}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-sm font-medium">{agent.agent_name || agent.agent_id}</p>
                        <p className="text-xs text-muted-foreground">
                          Commands: {agent.commands_executed} | Errors: {agent.errors}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground">
                        CPU: {agent.cpu_usage?.toFixed(1) || '0.0'}%
                      </p>
                      <p className="text-xs text-muted-foreground">
                        RAM: {agent.memory_usage?.toFixed(1) || '0.0'}%
                      </p>
                    </div>
                  </div>
                ))}
                {agentMetrics.length > 5 && (
                  <p className="text-sm text-muted-foreground text-center">
                    ... and {agentMetrics.length - 5} more agents
                  </p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Performance Metrics
            </CardTitle>
            <CardDescription>
              System performance and statistics
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-yellow-500" />
                  <span className="text-sm">Uptime</span>
                </div>
                <p className="text-lg font-semibold">
                  {systemMetrics?.uptime ? formatUptime(systemMetrics.uptime) : '--'}
                </p>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-blue-500" />
                  <span className="text-sm">Connections</span>
                </div>
                <p className="text-lg font-semibold">
                  {systemMetrics?.active_connections || 0}
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <HardDrive className="h-4 w-4 text-purple-500" />
                  <span className="text-sm">Disk Usage</span>
                </div>
                <p className="text-lg font-semibold">
                  {systemMetrics?.disk_usage?.toFixed(1) || '0.0'}%
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                  <span className="text-sm">Failed Commands</span>
                </div>
                <p className="text-lg font-semibold">
                  {connectionStats.failed_commands}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Real-time Activity Feed */}
      <RealTimeActivityFeed className="col-span-full" />
    </div>
  )
}