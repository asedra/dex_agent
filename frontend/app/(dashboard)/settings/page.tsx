'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Settings, Save, RefreshCw, Server, Key, Globe } from 'lucide-react'
import { apiClient } from '@/lib/api'

export default function SettingsPage() {
  const [config, setConfig] = useState({
    server_url: 'http://localhost:8080',
    api_token: 'default_token',
    agent_name: '',
    tags: [] as string[],
    auto_start: true,
    run_as_service: false
  })
  const [loading, setLoading] = useState(false)
  const [systemInfo, setSystemInfo] = useState<any>(null)

  useEffect(() => {
    loadInstallerConfig()
    loadSystemInfo()
  }, [])

  const loadInstallerConfig = async () => {
    try {
      setLoading(true)
      const installerConfig = await apiClient.getInstallerConfig()
      setConfig(prev => ({ ...prev, ...installerConfig }))
    } catch (error) {
      console.error('Failed to load installer config:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSystemInfo = async () => {
    try {
      const info = await apiClient.getSystemInfo()
      setSystemInfo(info)
    } catch (error) {
      console.error('Failed to load system info:', error)
    }
  }

  const handleSave = async () => {
    try {
      setLoading(true)
      // In a real app, you'd save these settings to backend
      console.log('Saving config:', config)
      alert('Settings saved successfully!')
    } catch (error) {
      console.error('Failed to save settings:', error)
      alert('Failed to save settings')
    } finally {
      setLoading(false)
    }
  }

  const handleTestConnection = async () => {
    try {
      setLoading(true)
      const health = await apiClient.getHealthCheck()
      alert(`Connection successful! Server status: ${health.status}`)
    } catch (error) {
      console.error('Connection test failed:', error)
      alert('Connection test failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center space-x-2">
        <Settings className="h-8 w-8" />
        <h1 className="text-3xl font-bold">Settings</h1>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Server className="h-5 w-5" />
              <span>Server Configuration</span>
            </CardTitle>
            <CardDescription>
              Configure your DexAgents server connection settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="server-url">Server URL</Label>
              <Input
                id="server-url"
                value={config.server_url}
                onChange={(e) => setConfig(prev => ({ ...prev, server_url: e.target.value }))}
                placeholder="http://localhost:8080"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="api-token">API Token</Label>
              <Input
                id="api-token"
                type="password"
                value={config.api_token}
                onChange={(e) => setConfig(prev => ({ ...prev, api_token: e.target.value }))}
                placeholder="Your API token"
              />
            </div>

            <div className="flex space-x-2">
              <Button onClick={handleTestConnection} variant="outline" disabled={loading}>
                <Globe className="mr-2 h-4 w-4" />
                Test Connection
              </Button>
              <Button onClick={handleSave} disabled={loading}>
                <Save className="mr-2 h-4 w-4" />
                Save Settings
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Key className="h-5 w-5" />
              <span>Agent Configuration</span>
            </CardTitle>
            <CardDescription>
              Default settings for new agent installations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="agent-name">Default Agent Name</Label>
              <Input
                id="agent-name"
                value={config.agent_name}
                onChange={(e) => setConfig(prev => ({ ...prev, agent_name: e.target.value }))}
                placeholder="Leave empty for auto-generated names"
              />
            </div>

            <div className="space-y-2">
              <Label>Agent Options</Label>
              <div className="flex items-center space-x-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={config.auto_start}
                    onChange={(e) => setConfig(prev => ({ ...prev, auto_start: e.target.checked }))}
                  />
                  <span>Auto Start</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={config.run_as_service}
                    onChange={(e) => setConfig(prev => ({ ...prev, run_as_service: e.target.checked }))}
                  />
                  <span>Run as Service</span>
                </label>
              </div>
            </div>

            {config.tags.length > 0 && (
              <div className="space-y-2">
                <Label>Default Tags</Label>
                <div className="flex flex-wrap gap-2">
                  {config.tags.map((tag, index) => (
                    <Badge key={index} variant="secondary">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {systemInfo && (
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>System Information</CardTitle>
              <CardDescription>
                Current server system details
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <Label className="text-sm font-medium">Hostname</Label>
                  <p className="text-sm text-muted-foreground">{systemInfo.hostname}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">CPU Usage</Label>
                  <p className="text-sm text-muted-foreground">{systemInfo.cpu_usage?.toFixed(1)}%</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Memory Usage</Label>
                  <p className="text-sm text-muted-foreground">{systemInfo.memory_usage?.toFixed(1)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      <Separator />

      <div className="flex justify-between items-center">
        <div>
          <p className="text-sm text-muted-foreground">
            DexAgents Management Platform v1.0.0
          </p>
        </div>
        <Button variant="outline" onClick={() => window.location.reload()}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh Page
        </Button>
      </div>
    </div>
  )
}