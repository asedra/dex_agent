---
description: "Select a Jira project via MCP integration"
shortcut: "sp"
arguments: true
---

# Select Project

List and select Jira projects using MCP integration. Fetches real project data from your Jira instance.

## Usage

```bash
/select-project              # Fetch and list all projects via MCP
/select-project KAN          # Select specific project by key
/sp                          # Shortcut to list projects
/sp DEX                      # Shortcut to select project
```

## Available Projects

Based on live data from Sipsy Jira via MCP:

### 🎯 KAN - Claude Code Development
- **Project ID**: 10001
- **Type**: Software (Next-gen)
- **Issue Types**: Epic, Feature, Story, Task, Bug, Subtask, Project Files
- **URL**: https://sipsy.atlassian.net/browse/KAN

**Development Commands Available:**
- `/create-branch` - Create feature branches
- `/run-tests` - Execute project tests
- `/deploy` - Deploy to environments
- `/developer-mode` - Switch to development workflow

### 🎯 DEX - Sipsy DEX
- **Project ID**: 10002  
- **Type**: Software (Next-gen)
- **Issue Types**: Epic, Task, Subtask
- **URL**: https://sipsy.atlassian.net/browse/DEX

**Development Commands Available:**
- `/create-branch` - Create feature branches
- `/run-tests` - Execute project tests
- `/developer-mode` - Switch to development workflow

## Project Selection

**To select KAN project:**
```bash
/select-project KAN
/sp KAN
```

**Expected Output:**
```
✅ Selected: Claude Code Development (KAN)
🎯 Project context updated

📋 Project Details:
• Key: KAN
• Name: Claude Code Development
• Instance: sipsy.atlassian.net
• URL: https://sipsy.atlassian.net/browse/KAN
• Project ID: 10001
• Type: Software (Next-gen)

📊 Available Issue Types:
• Epic - Collections of related features
• Feature - Broad functionality pieces
• Story - User goals and requirements
• Task - Small distinct work items
• Bug - Problems and errors
• Subtask - Parts of larger tasks
• Project Files - Documentation and files

🔧 Next Steps:
• Use /developer-mode for development workflows
• Create branches with /create-branch feature/[name]
• Run tests with /run-tests
```

**To select DEX project:**
```bash
/select-project DEX
/sp DEX
```

**Expected Output:**
```
✅ Selected: Sipsy DEX (DEX)
🎯 Project context updated

📋 Project Details:
• Key: DEX
• Name: Sipsy DEX
• Instance: sipsy.atlassian.net
• URL: https://sipsy.atlassian.net/browse/DEX
• Project ID: 10002
• Type: Software (Next-gen)

📊 Available Issue Types:
• Epic - Collections of related features
• Task - Small distinct work items
• Subtask - Parts of larger tasks

🔧 Next Steps:
• Use /developer-mode for development workflows
• Create branches with /create-branch feature/[name]
• Run tests with /run-tests
```

## MCP Integration Details

This command integrates with Jira using Model Context Protocol (MCP):

### Connection Information
- **Instance**: Sipsy Atlassian
- **Cloud ID**: e9ed7bab-c21a-4b0c-b996-fa7146d8e58b
- **URL**: https://sipsy.atlassian.net
- **Integration**: Active MCP connection
- **Permissions**: Read access to projects and issue types

### Live Data Features
- **Real-time project information**: Current project configurations
- **Issue type synchronization**: Up-to-date issue type definitions  
- **Project metadata**: Live project settings and permissions
- **Automatic updates**: No manual configuration needed

### MCP Tools Used
- `getVisibleJiraProjects` - Fetch available projects
- `getJiraProjectIssueTypesMetadata` - Get issue type information
- Real-time data synchronization with Jira instance

## Context Management

Once you select a project with this command:

1. **Project Context**: Active project metadata loaded
2. **Issue Types**: Available issue types for the project
3. **Workflows**: Project-specific development workflows
4. **Commands**: Relevant commands for the selected project

## Quick Selection Reference

| Command | Project | Description |
|---------|---------|-------------|
| `/sp KAN` | Claude Code Development | Main development project |
| `/sp DEX` | Sipsy DEX | DEX platform project |
| `/sp` | - | List all available projects |

## Troubleshooting

### Common Issues
1. **MCP connection failed**: Check MCP server is running
2. **No projects shown**: Verify Jira instance permissions
3. **Invalid project key**: Use exact keys (KAN, DEX)
4. **Permission errors**: MCP tools require proper access

### Debug Steps
1. Ensure MCP integration is properly configured
2. Check Jira instance accessibility
3. Verify project permissions in Jira web interface
4. Use exact project keys (case sensitive)

## Next Steps

After selecting a project:
1. **Development**: Use `/developer-mode` for development workflows
2. **Branching**: Create branches with `/create-branch feature/[name]`
3. **Testing**: Run tests with `/run-tests`
4. **Issue Management**: Access issues via Jira web interface
5. **Context Switching**: Switch projects anytime with this command

---

**Note**: This command provides static project information based on MCP integration data. For real-time project updates, the system connects to Sipsy Atlassian via Model Context Protocol.