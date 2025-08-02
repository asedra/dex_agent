---
description: "System status and configuration information"
shortcut: "st"
---

# System Status

Display current status and configuration of the Claude Code hierarchical command system.

## System Information

### Environment
!`echo "🖥️  Environment: $(uname -s) $(uname -r)"`

### Working Directory  
!`echo "📁 Working Directory: $(pwd)"`

### Current Time
!`echo "⏰ Current Time: $(date '+%Y-%m-%d %H:%M:%S %Z')"`

## Command System Status

### Configuration Files
!`echo "🔍 Checking configuration files..."`
!`test -f .claude/integrations/jira-api.json && echo "✅ Jira API config: Found" || echo "❌ Jira API config: Missing"`

### Available Commands
!`echo "📋 Markdown commands in .claude/commands/:"`
!`ls -1 .claude/commands/*.md 2>/dev/null | wc -l | xargs echo "Total commands available:"`

### Command List
!`echo "📝 Available slash commands:"`
!`ls -1 .claude/commands/*.md 2>/dev/null | sed 's|.claude/commands/||' | sed 's|.md||' | sed 's|^|  /|' | head -20 || echo "  No commands found"`

## API Integration Status

### Jira Configuration
!`echo "🔌 Jira REST API Integration:"`
!`if [ -f .claude/integrations/jira-api.json ]; then
    echo "✅ Configuration file exists"
    echo "📍 Location: .claude/integrations/jira-api.json"
    echo "🔗 Instance: Sipsy Atlassian"
    echo "☁️  Cloud ID: e9ed7bab-c21a-4b0c-b996-fa7146d8e58b"
    echo "📊 Projects: KAN, SAM1"
    echo ""
    
    # Load environment variables to check API credentials
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    echo "🔐 API Credentials:"
    if [ -n "$JIRA_EMAIL" ] && [ -n "$JIRA_API_TOKEN" ] && [ -n "$JIRA_BASE_URL" ]; then
        echo "  ✅ Email: $JIRA_EMAIL"
        echo "  ✅ Base URL: $JIRA_BASE_URL"
        echo "  ✅ API Token: [CONFIGURED]"
        echo "  ✅ Org ID: ${JIRA_ORG_ID:-Not set}"
        echo ""
        
        # Test API connection with a quick call
        echo "🔍 Testing API connection..."
        test_response=$(curl -s -w "%{http_code}" -o /dev/null -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
            -H "Accept: application/json" \
            "$JIRA_BASE_URL/rest/api/3/myself" 2>/dev/null)
        
        if [ "$test_response" = "200" ]; then
            echo "  ✅ API Connection: Working"
        else
            echo "  ❌ API Connection: Failed (HTTP $test_response)"
        fi
    else
        echo "  ❌ Missing required environment variables"
        echo "  💡 Check .env file for JIRA_EMAIL, JIRA_API_TOKEN, JIRA_BASE_URL"
    fi
else
    echo "❌ Jira API not configured"
    echo "💡 Create .claude/integrations/jira-api.json to enable"
fi`

## Directory Structure

### Claude Directory Contents
!`echo "📂 Directory structure (.claude/):"`
!`find .claude -type d | sort | sed 's|^|  |' | head -10`

### Command Files
!`echo "📄 Command files:"`
!`find .claude/commands -name "*.md" -type f | wc -l | xargs echo "  Markdown commands:"`
!`find .claude -name "*.json" -type f | wc -l | xargs echo "  JSON configs:"`

## Recent Activity

### Last Modified
!`echo "🕒 Recently modified:"`
!`find .claude -type f -name "*.md" -o -name "*.json" | xargs ls -lt 2>/dev/null | head -5 | awk '{print "  " $6, $7, $8 " - " $9}' || echo "  No recent changes"`

## System Health

### Command Modes
!`echo "🎯 Available modes:"`
!`test -f .claude/commands/developer-mode.md && echo "  ✅ Developer mode" || echo "  ❌ Developer mode"`
!`test -f .claude/commands/reviewer-mode.md && echo "  ✅ Reviewer mode" || echo "  ❌ Reviewer mode"`
!`test -f .claude/commands/architect-mode.md && echo "  ✅ Architect mode" || echo "  ❌ Architect mode"`

### Key Commands
!`echo "🔑 Essential commands:"`
!`test -f .claude/commands/all-modes.md && echo "  ✅ /all-modes" || echo "  ❌ /all-modes"`
!`test -f .claude/commands/help.md && echo "  ✅ /help" || echo "  ❌ /help"`
!`test -f .claude/commands/select-project.md && echo "  ✅ /select-project" || echo "  ❌ /select-project"`

## Quick Actions

### 🚀 Get Started
- Run `/all-modes` to see available workflows
- Use `/help` for command assistance
- Select a project with `/select-project`

### 🔧 Development
- Switch to developer mode: `/developer-mode`
- Create branches: `/create-branch`
- Run tests: `/run-tests`

### 🔍 Code Review
- Switch to reviewer mode: `/reviewer-mode`
- Analyze PRs: `/analyze-pr`
- Check standards: `/check-standards`

### 🏗️ Architecture
- Switch to architect mode: `/architect-mode`
- Design systems: `/design-system`
- Create diagrams: `/create-diagram`

## Status Summary

!`echo "📊 Overall Status:"`
!`command_count=$(find .claude/commands -name "*.md" 2>/dev/null | wc -l)
if [ "$command_count" -gt 15 ]; then
    echo "✅ System fully operational ($command_count commands available)"
else
    echo "⚠️  Limited functionality ($command_count commands available)"
fi`

---

Use `/help` for detailed command information or `/all-modes` to start working.