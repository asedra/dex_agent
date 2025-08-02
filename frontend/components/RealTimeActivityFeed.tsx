'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Button } from '@/components/ui/button'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Server, 
  Terminal, 
  Wifi,
  WifiOff,
  Loader2
} from 'lucide-react'
import { useWebSocket, type WebSocketMessage } from '@/hooks/use-websocket'
import { formatDistanceToNow } from 'date-fns'

interface ActivityEvent {
  id: string
  type: 'agent_status' | 'command_executed' | 'system_alert' | 'user_action'
  title: string
  description: string
  timestamp: string
  status: 'success' | 'warning' | 'error' | 'info'
  source: string
  metadata?: Record<string, any>
}

interface RealTimeActivityFeedProps {
  className?: string
  maxEvents?: number
}

export function RealTimeActivityFeed({ 
  className = '', 
  maxEvents = 50 
}: RealTimeActivityFeedProps) {
  const [activities, setActivities] = useState<ActivityEvent[]>([])
  const [isAutoScroll, setIsAutoScroll] = useState(true)
  
  // Get WebSocket URL from environment or construct from current location
  const wsUrl = typeof window !== 'undefined' 
    ? `ws://${window.location.hostname}:8080/ws/activity`
    : 'ws://localhost:8080/ws/activity'
  
  const { lastMessage, isConnected, isConnecting, error, sendMessage } = useWebSocket({
    url: wsUrl,
    reconnectInterval: 3000,
    maxReconnectAttempts: 5
  })

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        let activityEvent: ActivityEvent

        switch (lastMessage.type) {
          case 'agent_status_change':
            activityEvent = {
              id: crypto.randomUUID(),
              type: 'agent_status',
              title: `Agent ${lastMessage.data.status === 'online' ? 'Connected' : 'Disconnected'}`,
              description: `${lastMessage.data.agent_name || lastMessage.data.agent_id} is now ${lastMessage.data.status}`,
              timestamp: lastMessage.timestamp,
              status: lastMessage.data.status === 'online' ? 'success' : 'warning',
              source: lastMessage.data.agent_name || lastMessage.data.agent_id,
              metadata: lastMessage.data
            }
            break

          case 'command_executed':
            activityEvent = {
              id: crypto.randomUUID(),
              type: 'command_executed',
              title: 'Command Executed',
              description: `${lastMessage.data.command_name || 'PowerShell command'} executed on ${lastMessage.data.target || 'unknown target'}`,
              timestamp: lastMessage.timestamp,
              status: lastMessage.data.success ? 'success' : 'error',
              source: lastMessage.data.agent_name || lastMessage.data.target,
              metadata: lastMessage.data
            }
            break

          case 'system_alert':
            activityEvent = {
              id: crypto.randomUUID(),
              type: 'system_alert',
              title: lastMessage.data.title || 'System Alert',
              description: lastMessage.data.message || 'System event occurred',
              timestamp: lastMessage.timestamp,
              status: lastMessage.data.severity || 'warning',
              source: 'System',
              metadata: lastMessage.data
            }
            break

          default:
            // Generic activity event
            activityEvent = {
              id: crypto.randomUUID(),
              type: 'user_action',
              title: lastMessage.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
              description: JSON.stringify(lastMessage.data),
              timestamp: lastMessage.timestamp,
              status: 'info',
              source: 'System',
              metadata: lastMessage.data
            }
        }

        setActivities(prev => {
          const updated = [activityEvent, ...prev].slice(0, maxEvents)
          return updated
        })

      } catch (err) {
        console.error('Failed to process WebSocket message:', err)
      }
    }
  }, [lastMessage, maxEvents])

  // Request initial activity history when connected
  useEffect(() => {
    if (isConnected) {
      sendMessage({
        type: 'get_recent_activity',
        data: { limit: maxEvents }
      })
    }
  }, [isConnected, sendMessage, maxEvents])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-600" />
      default:
        return <Clock className="h-4 w-4 text-blue-600" />
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'agent_status':
        return <Server className="h-4 w-4" />
      case 'command_executed':
        return <Terminal className="h-4 w-4" />
      case 'system_alert':
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <Activity className="h-4 w-4" />
    }
  }

  const clearActivities = () => {
    setActivities([])
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            <CardTitle>Real-time Activity</CardTitle>
            <div className="flex items-center gap-1">
              {isConnecting ? (
                <Loader2 className="h-4 w-4 animate-spin text-yellow-500" />
              ) : isConnected ? (
                <Wifi className="h-4 w-4 text-green-500" />
              ) : (
                <WifiOff className="h-4 w-4 text-red-500" />
              )}
              <Badge variant={isConnected ? "default" : "destructive"} className="text-xs">
                {isConnected ? 'Live' : 'Disconnected'}
              </Badge>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={clearActivities}
            disabled={activities.length === 0}
          >
            Clear
          </Button>
        </div>
        <CardDescription>
          Live feed of system events and agent activities
          {error && (
            <div className="text-red-600 text-sm mt-1">
              Connection error: {error}
            </div>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-80">
          {activities.length === 0 ? (
            <div className="flex items-center justify-center h-40 text-muted-foreground">
              <div className="text-center">
                <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No recent activity</p>
                <p className="text-xs">
                  {isConnected ? 'Waiting for events...' : 'Connect to see live activity'}
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {activities.map((activity) => (
                <div 
                  key={activity.id}
                  className="flex items-start gap-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-1 mt-1">
                    {getTypeIcon(activity.type)}
                    {getStatusIcon(activity.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">{activity.title}</p>
                      <Badge variant="outline" className="text-xs">
                        {activity.source}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {activity.description}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}