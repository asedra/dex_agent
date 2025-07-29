"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Monitor, 
  Terminal, 
  Activity, 
  Settings, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Loader2, 
  AlertTriangle,
  HardDrive,
  Cpu,
  Network,
  Shield,
  RefreshCw,
  Play,
  FileText,
  Download,
  Upload,
  Trash2,
  Power
} from "lucide-react"
import { apiClient, Agent, SystemInfo, PowerShellCommand, CommandResponse } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { useParams } from "next/navigation"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

export default function AgentDetailPage() {
  const params = useParams()
  const agentId = params.id as string
  const [agent, setAgent] = useState<Agent | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [commandDialogOpen, setCommandDialogOpen] = useState(false)
  const [executingCommand, setExecutingCommand] = useState(false)
  const [commandResult, setCommandResult] = useState<CommandResponse | null>(null)
  const [commandInput, setCommandInput] = useState("")
  const [runAsAdmin, setRunAsAdmin] = useState(false)
  const [timeout, setTimeout] = useState(30)
  const [activeTab, setActiveTab] = useState("overview")
  const { toast } = useToast()

  const fetchAgent = async () => {
    try {
      setLoading(true)
      const agentData = await apiClient.getAgent(agentId)
      setAgent(agentData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch agent')
      toast({
        title: "Error",
        description: "Failed to load agent details",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    if (!agent?.id) return
    
    try {
      setRefreshing(true)
      console.log('Refreshing agent:', agent.id)
      
      const result = await apiClient.refreshAgent(agent.id)
      console.log('Refresh result:', result)
      
      // Update agent state with the refreshed data
      setAgent(result)
      
      toast({
        title: "Success",
        description: "Agent information refreshed successfully",
      })
    } catch (err) {
      console.error('Refresh error:', err)
      toast({
        title: "Error",
        description: "Failed to refresh agent information",
        variant: "destructive",
      })
    } finally {
      setRefreshing(false)
    }
  }

  const executeCommand = async () => {
    if (!commandInput.trim()) {
      toast({
        title: "Error",
        description: "Please enter a command",
        variant: "destructive",
      })
      return
    }

    try {
      setExecutingCommand(true)
      setCommandResult(null)

      const command: PowerShellCommand = {
        command: commandInput.trim(),
        timeout: timeout,
        run_as_admin: runAsAdmin,
      }

      // Execute command on the specific agent
      const result = await apiClient.executeAgentCommand(agentId, command.command)
      setCommandResult(result)
      setCommandDialogOpen(true)

      if (result.success) {
        toast({
          title: "Success",
          description: "Command executed successfully on agent",
        })
      } else {
        toast({
          title: "Error",
          description: "Command execution failed on agent",
          variant: "destructive",
        })
      }
    } catch (err) {
      console.error('Command execution error:', err)
      toast({
        title: "Error",
        description: "Failed to execute command on agent",
        variant: "destructive",
      })
    } finally {
      setExecutingCommand(false)
    }
  }

  const handleRestartAgent = async () => {
    try {
      const command: PowerShellCommand = {
        command: "Restart-Computer -Force",
        timeout: 60,
        run_as_admin: true,
      }

      await apiClient.executeCommand(command)
      toast({
        title: "Success",
        description: "Restart command sent to agent",
      })
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to send restart command",
        variant: "destructive",
      })
    }
  }

  const handleShutdownAgent = async () => {
    try {
      const command: PowerShellCommand = {
        command: "Stop-Computer -Force",
        timeout: 60,
        run_as_admin: true,
      }

      await apiClient.executeCommand(command)
      toast({
        title: "Success",
        description: "Shutdown command sent to agent",
      })
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to send shutdown command",
        variant: "destructive",
      })
    }
  }

  const handleGetSystemInfo = async () => {
    try {
      const command: PowerShellCommand = {
        command: "Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory, CsProcessors, CsManufacturer, CsModel",
        timeout: 30,
        run_as_admin: false,
      }

      const result = await apiClient.executeCommand(command)
      setCommandResult(result)
      setCommandInput(command.command)
      setCommandDialogOpen(true)

      if (result.success) {
        toast({
          title: "Success",
          description: "System information retrieved",
        })
      }
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to get system information",
        variant: "destructive",
      })
    }
  }

  const handleGetProcesses = async () => {
    try {
      const command: PowerShellCommand = {
        command: "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet, Id",
        timeout: 30,
        run_as_admin: false,
      }

      const result = await apiClient.executeCommand(command)
      setCommandResult(result)
      setCommandInput(command.command)
      setCommandDialogOpen(true)

      if (result.success) {
        toast({
          title: "Success",
          description: "Process list retrieved",
        })
      }
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to get process list",
        variant: "destructive",
      })
    }
  }

  const handleGetServices = async () => {
    try {
      const command: PowerShellCommand = {
        command: "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name, Status, DisplayName",
        timeout: 30,
        run_as_admin: false,
      }

      const result = await apiClient.executeCommand(command)
      setCommandResult(result)
      setCommandInput(command.command)
      setCommandDialogOpen(true)

      if (result.success) {
        toast({
          title: "Success",
          description: "Services list retrieved",
        })
      }
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to get services list",
        variant: "destructive",
      })
    }
  }

  useEffect(() => {
    if (agentId) {
      fetchAgent()
    }
  }, [agentId])

  // Debug: Log agent state changes
  useEffect(() => {
    console.log('Agent state changed:', agent)
  }, [agent])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "online":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "offline":
        return <XCircle className="h-4 w-4 text-red-600" />
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-600" />
      default:
        return <XCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "online":
        return (
          <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            Online
          </Badge>
        )
      case "offline":
        return <Badge variant="destructive">Offline</Badge>
      case "pending":
        return (
          <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
            Pending
          </Badge>
        )
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-2">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Loading agent details...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error || !agent) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Failed to load agent</h3>
            <p className="text-muted-foreground mb-4">{error || 'Agent not found'}</p>
            <Button onClick={() => window.location.reload()}>
              Retry
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      {/* Debug info */}
      <div className="bg-yellow-100 p-2 rounded text-xs">
        <strong>Debug:</strong> Agent ID: {agent.id}, Status: {agent.status}, Last Seen: {agent.last_seen}
      </div>
      
      <div className="flex items-center justify-between space-y-2">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">{agent.hostname}</h2>
            <p className="text-muted-foreground">Agent details and system information</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {getStatusIcon(agent.status)}
          {getStatusBadge(agent.status)}
          <Button
            onClick={handleRefresh}
            disabled={refreshing}
            variant="outline"
            size="sm"
            className="ml-2"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="system">System Info</TabsTrigger>
          <TabsTrigger value="commands">Commands</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* Agent Info */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Monitor className="h-5 w-5" />
                  Agent Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Hostname</span>
                    <span className="text-sm font-medium">{agent.hostname}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">IP Address</span>
                    <span className="text-sm font-medium">{agent.ip || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Operating System</span>
                    <span className="text-sm font-medium">{agent.os || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Agent Version</span>
                    <span className="text-sm font-medium">{agent.version || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Last Seen</span>
                    <span className="text-sm font-medium">{agent.last_seen || '-'}</span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1">
                  {(agent.tags || []).map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Terminal className="h-5 w-5" />
                  Quick Actions
                </CardTitle>
                <CardDescription>Common PowerShell commands and system operations</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <Dialog open={commandDialogOpen} onOpenChange={setCommandDialogOpen}>
                  <DialogTrigger asChild>
                    <Button className="w-full justify-start" disabled={agent.status !== 'online'}>
                      <Terminal className="mr-2 h-4 w-4" />
                      Run Custom Command
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Execute PowerShell Command</DialogTitle>
                      <DialogDescription>
                        Execute a PowerShell command on {agent.hostname}
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="command">PowerShell Command</Label>
                        <Textarea
                          id="command"
                          placeholder="Enter PowerShell command..."
                          value={commandInput}
                          onChange={(e) => setCommandInput(e.target.value)}
                          rows={4}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="timeout">Timeout (seconds)</Label>
                          <Input
                            id="timeout"
                            type="number"
                            value={timeout}
                            onChange={(e) => setTimeout(Number(e.target.value))}
                            min={1}
                            max={300}
                          />
                        </div>
                        <div className="flex items-center space-x-2 pt-6">
                          <Checkbox
                            id="runAsAdmin"
                            checked={runAsAdmin}
                            onCheckedChange={(checked) => setRunAsAdmin(checked as boolean)}
                          />
                          <Label htmlFor="runAsAdmin">Run as Administrator</Label>
                        </div>
                      </div>
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="outline"
                          onClick={() => setCommandDialogOpen(false)}
                        >
                          Cancel
                        </Button>
                        <Button
                          onClick={executeCommand}
                          disabled={executingCommand || !commandInput.trim()}
                        >
                          {executingCommand ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Executing...
                            </>
                          ) : (
                            <>
                              <Play className="mr-2 h-4 w-4" />
                              Execute
                            </>
                          )}
                        </Button>
                      </div>
                      {commandResult && (
                        <div className="space-y-2">
                          <Label>Command Result</Label>
                          <div className="border rounded-md p-3 bg-muted">
                            <div className="flex items-center gap-2 mb-2">
                              {commandResult.success ? (
                                <CheckCircle className="h-4 w-4 text-green-600" />
                              ) : (
                                <XCircle className="h-4 w-4 text-red-600" />
                              )}
                              <span className="text-sm font-medium">
                                {commandResult.success ? 'Success' : 'Failed'}
                              </span>
                              <span className="text-sm text-muted-foreground">
                                ({commandResult.execution_time?.toFixed(2) || '0.00'}s)
                              </span>
                            </div>
                            {commandResult.output && (
                              <div className="space-y-1">
                                <Label className="text-xs">Output:</Label>
                                <pre className="text-xs bg-background p-2 rounded border overflow-auto max-h-32">
                                  {commandResult.output}
                                </pre>
                              </div>
                            )}
                            {commandResult.error && (
                              <div className="space-y-1">
                                <Label className="text-xs text-red-600">Error:</Label>
                                <pre className="text-xs bg-red-50 dark:bg-red-950 p-2 rounded border overflow-auto max-h-32 text-red-700 dark:text-red-300">
                                  {commandResult.error}
                                </pre>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </DialogContent>
                </Dialog>

                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={handleGetSystemInfo}
                  disabled={agent.status !== 'online'}
                >
                  <Activity className="mr-2 h-4 w-4" />
                  Get System Info
                </Button>

                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={handleGetProcesses}
                  disabled={agent.status !== 'online'}
                >
                  <FileText className="mr-2 h-4 w-4" />
                  Get Processes
                </Button>

                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={handleGetServices}
                  disabled={agent.status !== 'online'}
                >
                  <Settings className="mr-2 h-4 w-4" />
                  Get Services
                </Button>

                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button 
                      variant="outline" 
                      className="w-full justify-start text-orange-600 hover:text-orange-700"
                      disabled={agent.status !== 'online'}
                    >
                      <Power className="mr-2 h-4 w-4" />
                      Restart Agent
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Restart Agent</AlertDialogTitle>
                      <AlertDialogDescription>
                        This will restart the agent {agent.hostname}. The agent will be temporarily unavailable during the restart process.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={handleRestartAgent}>
                        Restart
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>

                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button 
                      variant="outline" 
                      className="w-full justify-start text-red-600 hover:text-red-700"
                      disabled={agent.status !== 'online'}
                    >
                      <Power className="mr-2 h-4 w-4" />
                      Shutdown Agent
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Shutdown Agent</AlertDialogTitle>
                      <AlertDialogDescription>
                        This will shutdown the agent {agent.hostname}. The agent will be offline until manually restarted.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={handleShutdownAgent}>
                        Shutdown
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </CardContent>
            </Card>

            {/* System Health */}
            {agent.system_info && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    System Health
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">CPU Usage</span>
                      <span className="text-sm font-medium">{agent.system_info.cpu_usage.toFixed(1)}%</span>
                    </div>
                    <Progress value={agent.system_info.cpu_usage} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Memory Usage</span>
                      <span className="text-sm font-medium">{agent.system_info.memory_usage.toFixed(1)}%</span>
                    </div>
                    <Progress value={agent.system_info.memory_usage} className="h-2" />
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="system" className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium">System Information</h3>
            <Button
              onClick={handleRefresh}
              disabled={refreshing}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
          {agent.system_info ? (
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Cpu className="h-5 w-5" />
                    CPU Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Usage</span>
                      <span className="text-sm font-medium">{agent.system_info.cpu_usage.toFixed(1)}%</span>
                    </div>
                    <Progress value={agent.system_info.cpu_usage} className="h-2" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Memory Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Usage</span>
                      <span className="text-sm font-medium">{agent.system_info.memory_usage.toFixed(1)}%</span>
                    </div>
                    <Progress value={agent.system_info.memory_usage} className="h-2" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <HardDrive className="h-5 w-5" />
                    Disk Usage
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {agent.system_info.disk_usage && Object.entries(agent.system_info.disk_usage).map(([drive, usage]) => (
                      <div key={drive} className="space-y-1">
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">{drive}</span>
                          <span className="text-sm font-medium">{(usage as number).toFixed(1)}%</span>
                        </div>
                        <Progress value={usage as number} className="h-2" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Network className="h-5 w-5" />
                    Network Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">IP Address</span>
                      <span className="text-sm font-medium">{agent.ip || '-'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Hostname</span>
                      <span className="text-sm font-medium">{agent.system_info.hostname}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">OS Version</span>
                      <span className="text-sm font-medium">{agent.system_info.os_version}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <Activity className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No system information available</h3>
                <p className="text-muted-foreground">System information is not available for this agent.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="commands" className="space-y-4">
          <Card>
            <CardContent className="text-center py-8">
              <Terminal className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">Command History</h3>
              <p className="text-muted-foreground">Command execution history will be displayed here.</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardContent className="text-center py-8">
              <Settings className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">Agent Settings</h3>
              <p className="text-muted-foreground">Agent configuration options will be displayed here.</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
