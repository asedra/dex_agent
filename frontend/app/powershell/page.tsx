"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { SidebarTrigger } from "@/components/ui/sidebar"
import {
  Terminal,
  Search,
  Plus,
  Play,
  Edit,
  Copy,
  Filter,
  Settings,
  Network,
  HardDrive,
  Shield,
  Activity,
  Loader2,
  CheckCircle,
  XCircle,
} from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
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
import { apiClient, PowerShellCommand, CommandResponse } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

const categories = [
  { id: "all", name: "All Commands", icon: Terminal, count: 24 },
  { id: "network", name: "Network", icon: Network, count: 8 },
  { id: "disk", name: "Disk & Storage", icon: HardDrive, count: 6 },
  { id: "security", name: "Security", icon: Shield, count: 5 },
  { id: "system", name: "System Info", icon: Settings, count: 3 },
  { id: "monitoring", name: "Monitoring", icon: Activity, count: 2 },
]

const mockCommands = [
  {
    id: "1",
    name: "Get System Information",
    description: "Retrieves comprehensive system information including OS, hardware, and network details",
    category: "system",
    command: "Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory, CsProcessors",
    parameters: [],
    version: "1.2",
    author: "Admin",
    lastModified: "2024-01-15",
    tags: ["system", "hardware", "info"],
  },
  {
    id: "2",
    name: "Check Disk Space",
    description: "Monitors disk space usage across all drives",
    category: "disk",
    command:
      "Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name='Size(GB)';Expression={[math]::Round($_.Size/1GB,2)}}, @{Name='FreeSpace(GB)';Expression={[math]::Round($_.FreeSpace/1GB,2)}}",
    parameters: [],
    version: "1.0",
    author: "Admin",
    lastModified: "2024-01-14",
    tags: ["disk", "storage", "monitoring"],
  },
  {
    id: "3",
    name: "Get Network Configuration",
    description: "Retrieves network adapter configuration and IP settings",
    category: "network",
    command: "Get-NetIPConfiguration | Select-Object InterfaceAlias, IPv4Address, IPv4DefaultGateway",
    parameters: [],
    version: "1.1",
    author: "Network Admin",
    lastModified: "2024-01-13",
    tags: ["network", "ip", "configuration"],
  },
  {
    id: "4",
    name: "Get Event Logs",
    description: "Retrieves system event logs with customizable parameters",
    category: "monitoring",
    command: "Get-EventLog -LogName $LogName -Newest $Count | Where-Object {$_.EntryType -eq '$Level'}",
    parameters: [
      { name: "LogName", type: "string", default: "System", description: "Log name to query" },
      { name: "Count", type: "number", default: "100", description: "Number of entries to retrieve" },
      { name: "Level", type: "string", default: "Error", description: "Event level filter" },
    ],
    version: "2.0",
    author: "SOC Team",
    lastModified: "2024-01-12",
    tags: ["logs", "events", "monitoring", "troubleshooting"],
  },
  {
    id: "5",
    name: "Security Audit",
    description: "Performs basic security audit checks",
    category: "security",
    command:
      "Get-LocalUser | Select-Object Name, Enabled, LastLogon; Get-Service | Where-Object {$_.Status -eq 'Running' -and $_.Name -like '*Remote*'}",
    parameters: [],
    version: "1.3",
    author: "Security Team",
    lastModified: "2024-01-11",
    tags: ["security", "audit", "users", "services"],
  },
]

export default function PowerShellLibraryPage() {
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCommand, setSelectedCommand] = useState<any>(null)
  const [executing, setExecuting] = useState(false)
  const [executionResult, setExecutionResult] = useState<CommandResponse | null>(null)
  const { toast } = useToast()

  const filteredCommands = mockCommands.filter((command) => {
    const matchesCategory = selectedCategory === "all" || command.category === selectedCategory
    const matchesSearch =
      command.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      command.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      command.tags.some((tag) => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    return matchesCategory && matchesSearch
  })

  const getCategoryIcon = (categoryId: string) => {
    const category = categories.find((cat) => cat.id === categoryId)
    return category ? category.icon : Terminal
  }

  const executeCommand = async (command: PowerShellCommand) => {
    try {
      setExecuting(true)
      setExecutionResult(null)
      
      const result = await apiClient.executeCommand(command)
      setExecutionResult(result)
      
      if (result.success) {
        toast({
          title: "Success",
          description: "Command executed successfully",
        })
      } else {
        toast({
          title: "Error",
          description: result.error || "Command execution failed",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to execute command",
        variant: "destructive",
      })
    } finally {
      setExecuting(false)
    }
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">PowerShell Library</h2>
            <p className="text-muted-foreground">Manage and execute PowerShell commands across your agents</p>
          </div>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Command
        </Button>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        {/* Categories Sidebar */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Categories
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {categories.map((category) => {
              const Icon = category.icon
              return (
                <Button
                  key={category.id}
                  variant={selectedCategory === category.id ? "default" : "ghost"}
                  className="w-full justify-start"
                  onClick={() => setSelectedCategory(category.id)}
                >
                  <Icon className="mr-2 h-4 w-4" />
                  <span className="flex-1 text-left">{category.name}</span>
                  <Badge variant="secondary" className="ml-auto">
                    {category.count}
                  </Badge>
                </Button>
              )
            })}
          </CardContent>
        </Card>

        {/* Commands List */}
        <div className="lg:col-span-3 space-y-4">
          {/* Search */}
          <Card>
            <CardContent className="pt-6">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search commands, descriptions, or tags..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </CardContent>
          </Card>

          {/* Commands Grid */}
          <div className="grid gap-4 md:grid-cols-2">
            {filteredCommands.map((command) => {
              const CategoryIcon = getCategoryIcon(command.category)
              return (
                <Card key={command.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <CategoryIcon className="h-5 w-5 text-muted-foreground" />
                        <CardTitle className="text-lg">{command.name}</CardTitle>
                      </div>
                      <Badge variant="outline">v{command.version}</Badge>
                    </div>
                    <CardDescription className="line-clamp-2">{command.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex flex-wrap gap-1">
                      {command.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>

                    <div className="text-xs text-muted-foreground">
                      <p>
                        By {command.author} • Modified {command.lastModified}
                      </p>
                      {command.parameters.length > 0 && <p>{command.parameters.length} parameter(s)</p>}
                    </div>

                    <div className="flex gap-2">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button size="sm" onClick={() => setSelectedCommand(command)}>
                            <Play className="mr-2 h-4 w-4" />
                            Run
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-2xl">
                          <DialogHeader>
                            <DialogTitle>Run Command: {command.name}</DialogTitle>
                            <DialogDescription>Configure parameters and execute the command</DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div>
                              <Label>Command</Label>
                              <Textarea value={command.command} readOnly className="font-mono text-sm" rows={3} />
                            </div>
                            {command.parameters.length > 0 && (
                              <div className="space-y-2">
                                <Label>Parameters</Label>
                                {command.parameters.map((param) => (
                                  <div key={param.name} className="grid grid-cols-3 gap-2 items-center">
                                    <Label className="text-sm">{param.name}</Label>
                                    <Input placeholder={param.default} className="col-span-2" />
                                  </div>
                                ))}
                              </div>
                            )}
                            <div className="flex justify-end gap-2">
                              <Button 
                                variant="outline" 
                                onClick={() => setSelectedCommand(null)}
                              >
                                Cancel
                              </Button>
                              <Button 
                                onClick={() => {
                                  executeCommand({
                                    command: command.command,
                                    timeout: 30
                                  })
                                }}
                                disabled={executing}
                              >
                                {executing ? (
                                  <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Executing...
                                  </>
                                ) : (
                                  <>
                                    <Play className="mr-2 h-4 w-4" />
                                    Execute Command
                                  </>
                                )}
                              </Button>
                            </div>
                            
                            {/* Execution Result */}
                            {executionResult && (
                              <div className="mt-4 p-4 border rounded-lg">
                                <div className="flex items-center gap-2 mb-2">
                                  {executionResult.success ? (
                                    <CheckCircle className="h-4 w-4 text-green-600" />
                                  ) : (
                                    <XCircle className="h-4 w-4 text-red-600" />
                                  )}
                                  <span className="font-medium">
                                    {executionResult.success ? "Success" : "Failed"}
                                  </span>
                                  <span className="text-sm text-muted-foreground">
                                    ({executionResult.execution_time.toFixed(2)}s)
                                  </span>
                                </div>
                                {executionResult.output && (
                                  <div className="mt-2">
                                    <Label className="text-sm">Output:</Label>
                                    <Textarea 
                                      value={executionResult.output} 
                                      readOnly 
                                      className="font-mono text-sm mt-1" 
                                      rows={4}
                                    />
                                  </div>
                                )}
                                {executionResult.error && (
                                  <div className="mt-2">
                                    <Label className="text-sm text-red-600">Error:</Label>
                                    <Textarea 
                                      value={executionResult.error} 
                                      readOnly 
                                      className="font-mono text-sm mt-1 text-red-600" 
                                      rows={2}
                                    />
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </DialogContent>
                      </Dialog>

                      <Button size="sm" variant="outline">
                        <Edit className="mr-2 h-4 w-4" />
                        Edit
                      </Button>

                      <Button size="sm" variant="outline">
                        <Copy className="mr-2 h-4 w-4" />
                        Clone
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {filteredCommands.length === 0 && (
            <Card>
              <CardContent className="text-center py-8">
                <Terminal className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No commands found</h3>
                <p className="text-muted-foreground mb-4">No PowerShell commands match your current filters.</p>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Create New Command
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
