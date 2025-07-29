"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { MoreHorizontal, Search, Filter, Play, Settings, Eye, CheckCircle, XCircle, Clock, Loader2, AlertTriangle, Download, Plus, Server } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import Link from "next/link"
import { apiClient, Agent, AgentInstallerConfig, InstallerConfig } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedAgents, setSelectedAgents] = useState<string[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [installerDialogOpen, setInstallerDialogOpen] = useState(false)
  const [creatingInstaller, setCreatingInstaller] = useState(false)
  const [installerConfig, setInstallerConfig] = useState<InstallerConfig | null>(null)
  const [agentConfig, setAgentConfig] = useState<AgentInstallerConfig>({
    server_url: "",
    api_token: "",
    agent_name: "",
    tags: [],
    auto_start: true,
    run_as_service: true
  })
  const { toast } = useToast()

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true)
        const agentsData = await apiClient.getAgents()
        setAgents(agentsData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch agents')
        toast({
          title: "Error",
          description: "Failed to load agents",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    const fetchInstallerConfig = async () => {
      try {
        const config = await apiClient.getInstallerConfig()
        setInstallerConfig(config)
        setAgentConfig(prev => ({
          ...prev,
          server_url: config.server_url,
          api_token: config.api_token,
          tags: config.tags || []
        }))
      } catch (err) {
        console.error('Failed to fetch installer config:', err)
      }
    }

    fetchAgents()
    fetchInstallerConfig()
  }, [toast])

  const filteredAgents = agents.filter((agent) => {
    const matchesSearch =
      agent.hostname.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (agent.ip && agent.ip.includes(searchTerm)) ||
      (agent.tags || []).some((tag) => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesStatus = statusFilter === "all" || agent.status === statusFilter
    return matchesSearch && matchesStatus
  })

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

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedAgents(filteredAgents.map((agent) => agent.id || '').filter(Boolean))
    } else {
      setSelectedAgents([])
    }
  }

  const handleSelectAgent = (agentId: string, checked: boolean) => {
    if (checked) {
      setSelectedAgents([...selectedAgents, agentId])
    } else {
      setSelectedAgents(selectedAgents.filter((id) => id !== agentId))
    }
  }

  const handleCreateInstaller = async () => {
    if (!agentConfig.server_url || !agentConfig.api_token) {
      toast({
        title: "Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      })
      return
    }

    try {
      setCreatingInstaller(true)
      
      const blob = await apiClient.createAgentInstaller(agentConfig)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `DexAgent_${agentConfig.agent_name || 'Windows'}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.exe`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast({
        title: "Success",
        description: "Agent executable created and downloaded successfully",
      })
      
      setInstallerDialogOpen(false)
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to create agent executable",
        variant: "destructive",
      })
    } finally {
      setCreatingInstaller(false)
    }
  }

  const handleAddTag = (tag: string) => {
    if (tag && !(agentConfig.tags || []).includes(tag)) {
      setAgentConfig(prev => ({
        ...prev,
        tags: [...(prev.tags || []), tag]
      }))
    }
  }

  const handleRemoveTag = (tag: string) => {
    setAgentConfig(prev => ({
      ...prev,
      tags: (prev.tags || []).filter(t => t !== tag)
    }))
  }

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-2">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Loading agents...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Failed to load agents</h3>
            <p className="text-muted-foreground mb-4">{error}</p>
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
      <div className="flex items-center justify-between space-y-2">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Agents</h2>
            <p className="text-muted-foreground">Manage your endpoint agents</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Dialog open={installerDialogOpen} onOpenChange={setInstallerDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Download className="mr-2 h-4 w-4" />
                Download Agent
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create Agent Installer</DialogTitle>
                <DialogDescription>
                  Create a Windows agent executable file for deployment on other computers.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="server_url">Server URL *</Label>
                    <Input
                      id="server_url"
                      value={agentConfig.server_url}
                      onChange={(e) => setAgentConfig(prev => ({ ...prev, server_url: e.target.value }))}
                      placeholder="http://localhost:8000"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="api_token">API Token *</Label>
                    <Input
                      id="api_token"
                      value={agentConfig.api_token}
                      onChange={(e) => setAgentConfig(prev => ({ ...prev, api_token: e.target.value }))}
                      placeholder="default_token"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="agent_name">Agent Name (Optional)</Label>
                  <Input
                    id="agent_name"
                    value={agentConfig.agent_name}
                    onChange={(e) => setAgentConfig(prev => ({ ...prev, agent_name: e.target.value }))}
                    placeholder="Custom agent name"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Tags</Label>
                  <div className="flex flex-wrap gap-2">
                    {(agentConfig.tags || []).map((tag) => (
                      <Badge key={tag} variant="secondary" className="cursor-pointer" onClick={() => handleRemoveTag(tag)}>
                        {tag} ×
                      </Badge>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add tag..."
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault()
                          const input = e.target as HTMLInputElement
                          handleAddTag(input.value)
                          input.value = ''
                        }
                      }}
                    />
                    <Button variant="outline" size="sm" onClick={() => {
                      const input = document.querySelector('input[placeholder="Add tag..."]') as HTMLInputElement
                      if (input && input.value) {
                        handleAddTag(input.value)
                        input.value = ''
                      }
                    }}>
                      Add
                    </Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="auto_start"
                      checked={agentConfig.auto_start}
                      onCheckedChange={(checked) => setAgentConfig(prev => ({ ...prev, auto_start: checked as boolean }))}
                    />
                    <Label htmlFor="auto_start">Auto-start after installation</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="run_as_service"
                      checked={agentConfig.run_as_service}
                      onCheckedChange={(checked) => setAgentConfig(prev => ({ ...prev, run_as_service: checked as boolean }))}
                    />
                    <Label htmlFor="run_as_service">Run as Windows service</Label>
                  </div>
                </div>

                <div className="bg-muted p-3 rounded-md">
                  <h4 className="font-medium mb-2">Installation Instructions</h4>
                  <ol className="text-sm space-y-1 list-decimal list-inside">
                    <li>Download the .exe file (it's actually a ZIP archive)</li>
                    <li>Extract the ZIP file on the target Windows computer</li>
                    <li>Double-click <code className="bg-background px-1 rounded">DexAgent_[Name].bat</code> to run</li>
                    <li>The launcher will auto-install Python dependencies</li>
                    <li>Agent GUI will start and connect automatically</li>
                  </ol>
                </div>

                <div className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setInstallerDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleCreateInstaller}
                    disabled={creatingInstaller || !agentConfig.server_url || !agentConfig.api_token}
                  >
                    {creatingInstaller ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      <>
                        <Download className="mr-2 h-4 w-4" />
                        Create Installer
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search agents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8"
            />
          </div>
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="online">Online</SelectItem>
            <SelectItem value="offline">Offline</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Agents Table */}
      <Card>
        <CardHeader>
          <CardTitle>Agent List</CardTitle>
          <CardDescription>
            {filteredAgents.length} agent{filteredAgents.length !== 1 ? 's' : ''} found
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <Checkbox
                    checked={selectedAgents.length === filteredAgents.length && filteredAgents.length > 0}
                    onCheckedChange={handleSelectAll}
                  />
                </TableHead>
                <TableHead>Agent</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>IP Address</TableHead>
                <TableHead>Operating System</TableHead>
                <TableHead>Last Seen</TableHead>
                <TableHead>Tags</TableHead>
                <TableHead className="w-12"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAgents.map((agent) => (
                <TableRow key={agent.id}>
                  <TableCell>
                    <Checkbox
                      checked={selectedAgents.includes(agent.id || '')}
                      onCheckedChange={(checked) => handleSelectAgent(agent.id || '', checked as boolean)}
                    />
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Server className="h-4 w-4 text-muted-foreground" />
                      <Link href={`/agents/${agent.id}`} className="font-medium hover:underline">
                        {agent.hostname}
                      </Link>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(agent.status)}
                      {getStatusBadge(agent.status)}
                    </div>
                  </TableCell>
                  <TableCell>{agent.ip || '-'}</TableCell>
                  <TableCell>{agent.os || '-'}</TableCell>
                  <TableCell>{agent.last_seen || '-'}</TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {(agent.tags || []).slice(0, 2).map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {(agent.tags || []).length > 2 && (
                        <Badge variant="outline" className="text-xs">
                          +{(agent.tags || []).length - 2}
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                        <DropdownMenuItem asChild>
                          <Link href={`/agents/${agent.id}`}>
                            <Eye className="mr-2 h-4 w-4" />
                            View Details
                          </Link>
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Play className="mr-2 h-4 w-4" />
                          Run Command
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem>
                          <Settings className="mr-2 h-4 w-4" />
                          Configure
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
