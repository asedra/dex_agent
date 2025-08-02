'use client'

import { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { 
  Bot, 
  Send, 
  Copy, 
  Trash2,
  User,
  RefreshCw,
  Settings,
  MessageSquare,
  Loader2,
  Terminal,
  Lightbulb,
  AlertTriangle
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: {
    type?: 'command_suggestion' | 'analysis' | 'general'
    command?: string
    confidence?: number
  }
}

interface ChatGPTAssistantProps {
  className?: string
  context?: 'powershell' | 'system_analysis' | 'general'
  prefilledPrompt?: string
}

export function ChatGPTAssistant({ 
  className = '', 
  context = 'general',
  prefilledPrompt = ''
}: ChatGPTAssistantProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState(prefilledPrompt)
  const [isLoading, setIsLoading] = useState(false)
  const [isConfigured, setIsConfigured] = useState(false)
  const [apiStatus, setApiStatus] = useState<'unknown' | 'working' | 'error'>('unknown')
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const { toast } = useToast()

  useEffect(() => {
    checkAPIConfiguration()
    scrollToBottom()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (prefilledPrompt) {
      setInputMessage(prefilledPrompt)
    }
  }, [prefilledPrompt])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const checkAPIConfiguration = async () => {
    try {
      const response = await fetch('/api/v1/settings/chatgpt/config', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })
      
      if (response.ok) {
        const config = await response.json()
        setIsConfigured(!!config.api_key)
        setApiStatus('working')
      } else {
        setIsConfigured(false)
        setApiStatus('error')
      }
    } catch (error) {
      console.error('Failed to check ChatGPT configuration:', error)
      setIsConfigured(false)
      setApiStatus('error')
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/v1/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          message: userMessage.content,
          context: context,
          conversation_history: messages.slice(-10) // Last 10 messages for context
        })
      })

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`)
      }

      const result = await response.json()
      
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: result.response || 'No response received',
        timestamp: new Date().toISOString(),
        metadata: {
          type: result.type || 'general',
          command: result.suggested_command,
          confidence: result.confidence
        }
      }

      setMessages(prev => [...prev, assistantMessage])
      
    } catch (error) {
      console.error('Failed to send message:', error)
      
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to get AI response'}`,
        timestamp: new Date().toISOString()
      }
      
      setMessages(prev => [...prev, errorMessage])
      
      toast({
        title: "Error",
        description: "Failed to get AI response",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
    toast({
      title: "Copied",
      description: "Message copied to clipboard"
    })
  }

  const clearChat = () => {
    setMessages([])
    toast({
      title: "Cleared",
      description: "Chat history cleared"
    })
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getContextPrompts = () => {
    switch (context) {
      case 'powershell':
        return [
          "Help me create a PowerShell command to list all running services",
          "What's the best way to get system information using PowerShell?",
          "How can I check disk space on all drives with PowerShell?",
          "Show me how to get network adapter information"
        ]
      case 'system_analysis':
        return [
          "Analyze the current system performance metrics",
          "What should I look for in system logs?",
          "Help me troubleshoot high CPU usage",
          "Explain Windows Event Log analysis"
        ]
      default:
        return [
          "What can you help me with?",
          "Explain Windows endpoint management",
          "Best practices for system administration",
          "How to automate common tasks?"
        ]
    }
  }

  const getMessageIcon = (role: string, type?: string) => {
    if (role === 'user') return <User className="h-4 w-4" />
    if (role === 'system') return <AlertTriangle className="h-4 w-4 text-red-500" />
    if (type === 'command_suggestion') return <Terminal className="h-4 w-4 text-blue-500" />
    return <Bot className="h-4 w-4 text-green-500" />
  }

  if (!isConfigured) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            ChatGPT Assistant
          </CardTitle>
          <CardDescription>
            AI-powered assistance for system administration
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 space-y-4">
            <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto" />
            <div>
              <h3 className="text-lg font-medium">ChatGPT Not Configured</h3>
              <p className="text-muted-foreground mt-2">
                Please configure your OpenAI API key in the settings to use AI assistance.
              </p>
            </div>
            <Button asChild>
              <a href="/settings">
                <Settings className="h-4 w-4 mr-2" />
                Go to Settings
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            <CardTitle>ChatGPT Assistant</CardTitle>
            <Badge variant={apiStatus === 'working' ? 'default' : 'destructive'}>
              {apiStatus === 'working' ? 'Ready' : 'Error'}
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={checkAPIConfiguration}
              disabled={isLoading}
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={clearChat}
              disabled={messages.length === 0}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <CardDescription>
          AI-powered assistance for {context === 'powershell' ? 'PowerShell commands' : 
          context === 'system_analysis' ? 'system analysis' : 'general help'}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Quick Prompts */}
        {messages.length === 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium">Quick Prompts:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {getContextPrompts().map((prompt, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="justify-start text-left h-auto p-2"
                  onClick={() => setInputMessage(prompt)}
                >
                  <Lightbulb className="h-3 w-3 mr-2 flex-shrink-0" />
                  <span className="text-xs">{prompt}</span>
                </Button>
              ))}
            </div>
            <Separator />
          </div>
        )}

        {/* Chat Messages */}
        <ScrollArea className="h-64 w-full">
          <div className="space-y-4">
            {messages.map((message) => (
              <div key={message.id} className="space-y-2">
                <div className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                    <div className="flex items-center gap-2 mb-1">
                      {getMessageIcon(message.role, message.metadata?.type)}
                      <span className="text-xs text-muted-foreground">
                        {message.role === 'user' ? 'You' : message.role === 'system' ? 'System' : 'ChatGPT'}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                      {message.metadata?.confidence && (
                        <Badge variant="outline" className="text-xs">
                          {Math.round(message.metadata.confidence * 100)}% confident
                        </Badge>
                      )}
                    </div>
                    <div className={`rounded-lg p-3 ${
                      message.role === 'user' 
                        ? 'bg-primary text-primary-foreground' 
                        : message.role === 'system'
                        ? 'bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300'
                        : 'bg-muted'
                    }`}>
                      <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                      
                      {message.metadata?.command && (
                        <div className="mt-2 pt-2 border-t border-border/50">
                          <p className="text-xs font-medium mb-1">Suggested Command:</p>
                          <code className="text-xs bg-background/20 px-2 py-1 rounded">
                            {message.metadata.command}
                          </code>
                        </div>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="mt-1 h-6 px-2"
                      onClick={() => copyMessage(message.content)}
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-3 justify-start">
                <div className="bg-muted rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">ChatGPT is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="space-y-2">
          <Textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask ChatGPT for help... (Ctrl+Enter to send)"
            className="min-h-[60px] resize-none"
            disabled={isLoading}
          />
          <div className="flex items-center justify-between">
            <p className="text-xs text-muted-foreground">
              Use Ctrl+Enter to send message
            </p>
            <Button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              size="sm"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 mr-1 animate-spin" />
              ) : (
                <Send className="h-4 w-4 mr-1" />
              )}
              Send
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}