---
description: "Activate developer mode for development-focused commands"
icon: "🔧"
---

# Developer Mode

Activate developer context for building, testing, and managing development projects with integrated Jira workflow.

## Available Commands

### Project Management
- `/select-project [abbreviation]` - Select project from Jira (KAN, SAM1)

### Development Workflow  
- `/create-branch` - Create new git branch with naming conventions
- `/run-tests` - Execute test suite with various options
- `/deploy` - Deploy to specified environment

## Quick Start

```bash
# Activate developer mode (this command)
/developer-mode

# Select your project
/select-project          # List all projects
/select-project KAN      # Select KAN project directly

# Development workflow
/create-branch feature/new-command-system
/run-tests
/deploy staging
```

## Jira API Integration

Connected to Sipsy Jira via REST API for project management:
- **Projects**: KAN (Claude Code Development), SAM1 (Annual Product Roadmap)
- **Features**: Real-time project data, context switching, issue tracking

## Context Management

Once you select a project with `/select-project`, the developer context will be updated with:
- Current project information
- Available branches and environments
- Project-specific configurations
- Relevant Jira issues and tasks

## Next Steps

1. Start with `/select-project` to choose your working project
2. Use development commands based on your current task
3. Switch between projects as needed during your workflow

**Developer mode activated.** Use the commands above to manage your development workflow efficiently.