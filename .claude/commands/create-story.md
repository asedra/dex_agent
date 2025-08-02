---
description: "Convert narrative stories into structured developer tasks via MCP Jira integration"
shortcut: "cs"
arguments: true
---

# Create Story

Transform free-form narrative stories into structured Jira tasks for different developer roles using MCP integration.

## Usage

```bash
/create-story                    # Interactive story input mode
/create-story "Your story..."    # Direct story input
/cs                              # Shortcut for interactive mode
/cs "User story text here"       # Shortcut with direct input
```

## Story Processing Workflow

### 1. Story Input & Context Analysis

!`echo "📖 Story-Teller Mode: Create Story"`
!`echo "================================"`

!`echo "📖 Reading project context from README.md if available..."`

Story text provided: **$ARGUMENTS**

!`echo "🔄 Processing your story..."`

### 2. Developer Role Decomposition

Your story will be analyzed and decomposed for these developer roles:

#### 🎨 Frontend Developer Tasks
- UI component development and styling
- User interface interactions and responsive design
- Client-side state management and real-time updates

#### ⚙️ Backend Developer Tasks
- API endpoint design and implementation
- Business logic development and data processing
- Server-side integrations and real-time streaming

#### 🤖 AI Developer Tasks  
- Machine learning model development and training
- AI feature integration and intelligent data processing
- Predictive analytics and recommendation systems

#### 🗄️ Database Developer Tasks
- Database schema design and optimization
- Query performance tuning and data migration
- Data warehouse and analytics infrastructure

#### 🎨 UI/UX Designer Tasks
- User experience wireframes and design systems
- User journey mapping and interaction design
- Accessibility compliance and usability testing

#### 🚀 DevOps Engineer Tasks
- Deployment pipeline setup and infrastructure
- CI/CD workflow implementation and monitoring
- Performance optimization and scaling solutions

#### 🧪 QA Engineer Tasks
- Test strategy development and automation
- Quality assurance processes and validation
- Performance testing and security validation

### 3. Smart Role Detection

!`echo "🔍 Analyzing story for technical components..."`

The system will automatically detect which developer roles are needed based on your story content:

- **Frontend**: Keywords like dashboard, UI, interface, visualization, responsive
- **Backend**: Keywords like API, server, database, data processing, real-time
- **AI**: Keywords like AI, machine learning, analytics, insights, prediction
- **Database**: Keywords like database, data, storage, schema, migration
- **Design**: Keywords like design, UX, wireframe, prototype, usability
- **DevOps**: Keywords like deploy, infrastructure, pipeline, monitoring, scaling
- **QA**: Always included for comprehensive testing

!`echo "📋 Generated Task Breakdown:"`
!`echo "================================"`

### 4. Example Task Generation

Based on your story, tasks will be generated such as:

**For "Build a real-time analytics dashboard with AI insights":**

🎨 **Frontend Developer Tasks:**
- Create main dashboard interface component
- Implement data visualization components 
- Set up real-time UI updates
- Implement responsive design and styling

⚙️ **Backend Developer Tasks:**
- Design and implement analytics API endpoints
- Develop data processing logic
- Implement real-time data streaming
- Set up business logic and validation

🤖 **AI Developer Tasks:**
- Develop analytics and insight generation models
- Implement predictive modeling
- Create recommendation algorithms
- Integrate AI models with application

🗄️ **Database Developer Tasks:**
- Design database schema for analytics features
- Optimize queries for analytics performance
- Implement data migration and seeding

🎨 **UI/UX Designer Tasks:**
- Create dashboard wireframes and mockups
- Design user experience flow and interactions
- Ensure accessibility and usability standards

🚀 **DevOps Engineer Tasks:**
- Set up deployment pipeline for new features
- Configure infrastructure for performance requirements
- Implement monitoring and logging

🧪 **QA Engineer Tasks:**
- Develop comprehensive test strategy
- Create automated test suites
- Implement performance and load testing
- Execute manual testing and validation

!`echo "📊 Estimated tasks: 15-20 tasks across relevant developer roles"`

### 5. MCP Jira Integration

!`echo "🔌 MCP Jira Integration Ready"`
!`echo "Tasks will be created in the currently selected project with:"`
!`echo "• Issue Type: Story (main story) + Task (individual tasks)"`
!`echo "• Labels: Role-specific tags (frontend, backend, ai, database, design, devops, qa)"`
!`echo "• Descriptions: Detailed task specifications with context"`
!`echo "• Links: Related tasks will be linked appropriately"`

!`echo "✅ Ready to create tasks in Jira via MCP integration"`
!`echo "❓ Proceed with task creation in your selected project?"`
!`echo "💡 Tip: Use /rethink-story or /rs to refine this breakdown later"`

## Integration Features

### Project Context Awareness
- Reads project README.md for additional context
- Uses current project selection (KAN/DEX)
- Adapts task complexity based on project type

### MCP Jira Task Creation
- Creates main Story issue for overall narrative
- Creates individual Task issues for each developer role
- Applies appropriate labels and role assignments
- Links related tasks for traceability

### Smart Role Detection
- Analyzes story content for technical requirements
- Only generates tasks for relevant developer roles
- Provides detailed, actionable task descriptions
- Includes acceptance criteria and technical specs

## Error Handling

- **No Project Selected**: Prompts to use `/select-project` first
- **Empty Story**: Requests narrative input
- **MCP Connection Issues**: Graceful fallback with task summary
- **Invalid Input**: Clear error messages and guidance

## Examples

### Simple Story Example
```bash
/cs "Add a contact form to the website with email validation"

Generated Tasks:
🎨 Frontend: Create contact form component with validation UI
⚙️ Backend: Implement form submission API and email validation
🧪 QA: Test form validation and email delivery
```

### Complex Story Example  
```bash
/cs "Build a real-time analytics dashboard with AI-powered insights and predictive modeling"

Generated Tasks:
🎨 Frontend: 4 tasks (dashboard UI, real-time updates, charts, responsive design)
⚙️ Backend: 3 tasks (analytics API, WebSocket streaming, data processing)
🤖 AI: 3 tasks (insight models, predictive analytics, recommendations)
🗄️ Database: 2 tasks (analytics schema, query optimization)
🎨 Design: 2 tasks (dashboard wireframes, UX flow)
🚀 DevOps: 2 tasks (deployment pipeline, monitoring setup)
🧪 QA: 3 tasks (test strategy, automation, performance testing)
```

## Next Steps

After using this command:
1. Review the generated task breakdown
2. Use `/rethink-story` to refine if needed
3. Tasks will be created in your selected Jira project
4. View created tasks in Jira web interface

**Ready to transform your stories into actionable developer tasks!**