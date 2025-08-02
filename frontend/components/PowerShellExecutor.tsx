'use client'

import { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { 
  Terminal, 
  Play, 
  Square, 
  Copy, 
  Download, 
  History, 
  Loader2,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Bot
} from 'lucide-react'
import { apiClient, type Agent } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

interface CommandExecution {
  id: string
  command: string
  target: string
  status: 'running' | 'completed' | 'failed' | 'cancelled'
  output: string
  error?: string
  startTime: string
  endTime?: string
  duration?: number
}

interface PowerShellExecutorProps {
  className?: string
  preselectedAgent?: string
}

export function PowerShellExecutor({ 
  className = '', 
  preselectedAgent 
}: PowerShellExecutorProps) {
  const [command, setCommand] = useState('')
  const [selectedAgent, setSelectedAgent] = useState(preselectedAgent || '')
  const [agents, setAgents] = useState<Agent[]>([])
  const [executions, setExecutions] = useState<CommandExecution[]>([])
  const [isExecuting, setIsExecuting] = useState(false)
  const [commandHistory, setCommandHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [showAIAssist, setShowAIAssist] = useState(false)
  const [aiSuggestion, setAiSuggestion] = useState('')
  const [loadingAI, setLoadingAI] = useState(false)
  
  const commandRef = useRef<HTMLTextAreaElement>(null)
  const outputRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  // Load agents on mount
  useEffect(() => {
    loadAgents()
    loadCommandHistory()
  }, [])

  const loadAgents = async () => {
    try {
      const agentsData = await apiClient.getAgents()
      setAgents(agentsData)
      
      if (!selectedAgent && agentsData.length > 0) {
        setSelectedAgent(agentsData[0].id || '')
      }
    } catch (error) {
      console.error('Failed to load agents:', error)
      toast({
        title: "Error",
        description: "Failed to load agents",
        variant: "destructive"
      })
    }
  }

  const loadCommandHistory = () => {
    const saved = localStorage.getItem('powershell_history')
    if (saved) {
      setCommandHistory(JSON.parse(saved))
    }
  }

  const saveCommandHistory = (newCommand: string) => {
    const updated = [newCommand, ...commandHistory.filter(cmd => cmd !== newCommand)].slice(0, 50)
    setCommandHistory(updated)
    localStorage.setItem('powershell_history', JSON.stringify(updated))
  }

  const executeCommand = async () => {
    if (!command.trim() || !selectedAgent) {
      toast({
        title: "Error",
        description: "Please enter a command and select an agent",
        variant: "destructive"
      })
      return
    }

    const executionId = crypto.randomUUID()
    const startTime = new Date().toISOString()

    const newExecution: CommandExecution = {
      id: executionId,
      command: command.trim(),
      target: selectedAgent,
      status: 'running',
      output: '',
      startTime
    }

    setExecutions(prev => [newExecution, ...prev])
    setIsExecuting(true)
    saveCommandHistory(command.trim())

    try {
      const response = await apiClient.executeCommand(selectedAgent, {
        command: command.trim(),
        timeout: 30000
      })

      const endTime = new Date().toISOString()
      const duration = new Date(endTime).getTime() - new Date(startTime).getTime()

      setExecutions(prev => prev.map(exec => 
        exec.id === executionId 
          ? {
              ...exec,
              status: response.success ? 'completed' : 'failed',
              output: response.output || '',
              error: response.error,
              endTime,
              duration
            }
          : exec
      ))

      toast({
        title: response.success ? "Success" : "Error",
        description: response.success ? "Command executed successfully" : "Command execution failed",
        variant: response.success ? "default" : "destructive"
      })

    } catch (error) {
      const endTime = new Date().toISOString()
      const duration = new Date(endTime).getTime() - new Date(startTime).getTime()

      setExecutions(prev => prev.map(exec => 
        exec.id === executionId 
          ? {
              ...exec,
              status: 'failed',
              error: error instanceof Error ? error.message : 'Unknown error',
              endTime,
              duration
            }
          : exec
      ))

      toast({
        title: "Error",
        description: "Failed to execute command",
        variant: "destructive"
      })
    } finally {
      setIsExecuting(false)
    }
  }

  const cancelExecution = () => {
    // In a real implementation, this would cancel the running command
    setIsExecuting(false)
    
    setExecutions(prev => prev.map(exec => 
      exec.status === 'running' 
        ? { ...exec, status: 'cancelled' as const, endTime: new Date().toISOString() }
        : exec
    ))

    toast({
      title: "Cancelled",
      description: "Command execution cancelled"
    })
  }

  const copyOutput = (output: string) => {
    navigator.clipboard.writeText(output)
    toast({
      title: "Copied",
      description: "Output copied to clipboard"
    })
  }

  const getAISuggestion = async () => {
    if (!command.trim()) {
      toast({
        title: "Error",
        description: "Please enter a command first",
        variant: "destructive"
      })
      return
    }

    setLoadingAI(true)
    try {
      const response = await fetch('/api/v1/ai/powershell-suggest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          command: command.trim(),
          context: 'windows_endpoint'
        })
      })

      if (response.ok) {
        const result = await response.json()
        setAiSuggestion(result.suggestion || 'No suggestions available')
        setShowAIAssist(true)
      } else {
        throw new Error('AI service unavailable')
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "AI assistance unavailable",
        variant: "destructive"
      })
    } finally {
      setLoadingAI(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      executeCommand()
    } else if (e.key === 'ArrowUp' && e.ctrlKey) {
      e.preventDefault()
      if (historyIndex < commandHistory.length - 1) {
        const newIndex = historyIndex + 1
        setHistoryIndex(newIndex)
        setCommand(commandHistory[newIndex])
      }
    } else if (e.key === 'ArrowDown' && e.ctrlKey) {
      e.preventDefault()
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1
        setHistoryIndex(newIndex)
        setCommand(commandHistory[newIndex])
      } else if (historyIndex === 0) {
        setHistoryIndex(-1)
        setCommand('')
      }
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'cancelled':
        return <Square className="h-4 w-4 text-yellow-500" />
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-500" />
    }
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Terminal className="h-5 w-5" />
            PowerShell Command Executor
          </CardTitle>
          <CardDescription>
            Execute PowerShell commands on selected agents with real-time output
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Agent Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Target Agent</label>
            <Select value={selectedAgent} onValueChange={setSelectedAgent}>
              <SelectTrigger>
                <SelectValue placeholder="Select an agent" />
              </SelectTrigger>
              <SelectContent>
                {agents.map(agent => (
                  <SelectItem key={agent.id} value={agent.id || ''}>
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${
                        agent.status === 'online' ? 'bg-green-500' : 'bg-gray-500'
                      }`} />
                      {agent.hostname || agent.id} ({agent.status})
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Command Input */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">PowerShell Command</label>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={getAISuggestion}
                  disabled={loadingAI}
                >
                  {loadingAI ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                  AI Assist
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCommand('')}
                  disabled={!command}
                >
                  Clear
                </Button>
              </div>
            </div>
            <Textarea
              ref={commandRef}
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter PowerShell command... (Ctrl+Enter to execute)"
              className="min-h-[80px] font-mono"
            />
            <div className="flex items-center justify-between">
              <p className="text-xs text-muted-foreground">
                Use Ctrl+↑/↓ for command history, Ctrl+Enter to execute
              </p>
              <div className="flex items-center gap-2">
                <Button
                  onClick={cancelExecution}
                  disabled={!isExecuting}
                  variant="outline"
                  size="sm"
                >
                  <Square className="h-4 w-4 mr-1" />
                  Cancel
                </Button>
                <Button
                  onClick={executeCommand}
                  disabled={!command.trim() || !selectedAgent || isExecuting}
                >
                  {isExecuting ? (
                    <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4 mr-1" />
                  )}
                  Execute
                </Button>
              </div>
            </div>
          </div>

          {/* AI Suggestions */}
          {showAIAssist && aiSuggestion && (
            <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Bot className="h-4 w-4" />
                  AI Suggestion
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-blue-700 dark:text-blue-300 mb-2">
                  {aiSuggestion}
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setShowAIAssist(false)}
                >
                  Dismiss
                </Button>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>

      {/* Command History & Output */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Execution History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-96">
            {executions.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                No commands executed yet
              </div>
            ) : (
              <div className="space-y-4">
                {executions.map((execution) => (
                  <div key={execution.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(execution.status)}
                        <Badge variant={execution.status === 'completed' ? 'default' : 'destructive'}>
                          {execution.status}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {new Date(execution.startTime).toLocaleTimeString()}
                        </span>
                        {execution.duration && (
                          <span className="text-sm text-muted-foreground">
                            ({execution.duration}ms)
                          </span>
                        )}
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyOutput(execution.output || execution.error || '')}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                    
                    <div className="mb-2">
                      <p className="text-sm font-medium">Command:</p>
                      <code className="text-sm bg-muted p-2 rounded block">
                        {execution.command}
                      </code>
                    </div>

                    {execution.output && (
                      <div>
                        <p className="text-sm font-medium mb-1">Output:</p>
                        <pre className="text-sm bg-muted p-2 rounded whitespace-pre-wrap max-h-32 overflow-y-auto">
                          {execution.output}
                        </pre>
                      </div>
                    )}

                    {execution.error && (
                      <div>
                        <p className="text-sm font-medium mb-1 text-red-600">Error:</p>
                        <pre className="text-sm bg-red-50 dark:bg-red-950 p-2 rounded whitespace-pre-wrap text-red-700 dark:text-red-300">
                          {execution.error}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  )
}