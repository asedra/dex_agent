---
description: "Activate story-teller mode for converting narratives into structured developer tasks"
icon: "📖"
---

# Story-Teller Mode

Transform narrative stories into structured Jira tasks for different developer roles with integrated MCP workflow.

## Available Commands

### Story Management
- `/create-story` (cs) - Convert narrative into developer tasks
- `/rethink-story` (rs) - Revise and refine existing story breakdown

### Project Integration
- `/select-project [abbreviation]` - Select target project from Jira (KAN, DEX)

## Quick Start

```bash
# Activate story-teller mode (this command)
/story-teller

# Select your target project
/select-project          # List all projects
/select-project KAN      # Select KAN project directly

# Create story from narrative
/create-story            # Start interactive story input
/cs                      # Shortcut for create-story

# Revise existing story
/rethink-story           # Refine story breakdown
/rs                      # Shortcut for rethink-story  
```

## Developer Role Breakdown

Stories are automatically decomposed for these roles:

🎨 **Frontend Developer** - UI components, user interactions, styling  
⚙️ **Backend Developer** - APIs, business logic, data processing  
🤖 **AI Developer** - ML models, AI integrations, intelligent features  
🗄️ **Database Developer** - Schema design, queries, data optimization  
🎨 **UI/UX Designer** - User experience, wireframes, design systems  
🚀 **DevOps Engineer** - Deployment, infrastructure, CI/CD  
🧪 **QA Engineer** - Testing strategies, test cases, quality assurance  

## MCP Jira Integration

Connected to Sipsy Jira via MCP for automatic task creation:
- **Projects**: KAN (Claude Code Development), DEX (Sipsy DEX)  
- **Issue Types**: Story, Task, Subtask with role-specific labels
- **Features**: Real-time task creation, project context awareness

## Story Processing Workflow

1. **Story Input** - Accept free-form narrative text
2. **Context Analysis** - Read project README.md for additional context
3. **Role Decomposition** - Break story into role-specific tasks
4. **Review & Approval** - Present task breakdown for confirmation
5. **Jira Creation** - Create approved tasks in selected project
6. **Story Revision** - Refine and regenerate as needed

## Example Workflow

```bash
# Start with story-teller mode
/story-teller
Story-teller mode activated. Ready to convert narratives into developer tasks.

# Select project context
/sp KAN
✅ Selected: Claude Code Development (KAN)

# Create story from narrative
/cs
📖 Story Input: Enter your narrative story...
User: "I want to build a user dashboard that shows project analytics with real-time updates and AI-powered insights"

🔄 Processing story...
📋 Task Breakdown Generated:

🎨 Frontend Developer Tasks:
- Create dashboard layout component
- Implement real-time data visualization
- Build responsive analytics widgets

⚙️ Backend Developer Tasks:  
- Design analytics data API endpoints
- Implement real-time WebSocket connections
- Create data aggregation services

🤖 AI Developer Tasks:
- Develop insight generation models
- Implement predictive analytics
- Create recommendation algorithms

[Continue for all relevant roles...]

✅ Approve and create 12 tasks in Jira? (y/n)
```

## Context Management

Once activated, story-teller mode maintains:
- Current project selection (KAN/DEX)
- Story context and decomposition history
- Role-specific task templates
- MCP Jira connection state

## Next Steps

1. Start with `/select-project` to choose your target project
2. Use `/create-story` to input your narrative
3. Review generated task breakdown
4. Approve for automatic Jira task creation
5. Use `/rethink-story` for refinements as needed

**Story-teller mode activated.** Ready to transform your narratives into actionable developer tasks.