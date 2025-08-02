'use client'

import { SidebarTrigger } from "@/components/ui/sidebar"
import { PowerShellExecutor } from "@/components/PowerShellExecutor"
import { ChatGPTAssistant } from "@/components/ChatGPTAssistant"
import { Terminal, Bot } from "lucide-react"

export default function ExecuteCommandsPage() {
  return (
    <div className="flex-1 space-y-6 p-4 md:p-8 pt-6">
      <div className="flex items-center gap-4">
        <SidebarTrigger />
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Execute Commands</h2>
          <p className="text-muted-foreground">
            Execute PowerShell commands on agents with AI assistance
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* PowerShell Executor */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Terminal className="h-5 w-5" />
            <h3 className="text-xl font-semibold">PowerShell Executor</h3>
          </div>
          <PowerShellExecutor />
        </div>

        {/* ChatGPT Assistant */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            <h3 className="text-xl font-semibold">AI Assistant</h3>
          </div>
          <ChatGPTAssistant 
            context="powershell"
            prefilledPrompt=""
          />
        </div>
      </div>
    </div>
  )
}