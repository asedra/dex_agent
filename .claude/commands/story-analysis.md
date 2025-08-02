---
description: "Activate role-specific task creation for existing stories with cross-team collaboration tracking"
shortcut: "sa"
arguments: true
---

# Story Analysis

Deep dive into role-specific task creation for existing stories with enhanced cross-team collaboration and dependency tracking.

## Usage

```bash
/story-analysis [story-id]           # Analyze specific story for role-based tasks
/story-analysis                      # List available stories for analysis
/sa [story-id]                       # Shortcut with story ID
/sa                                  # Shortcut for story list
```

## Workflow Overview

### 1. Story Selection & Context Loading

🔍 **Story Analysis Mode**
=====================

**Story ID**: $ARGUMENTS

**Usage**: `/story-analysis [story-id]` or `/sa [story-id]`

When story ID is provided:
- 📋 Loading story details from Jira
- 📊 Analyzing existing task breakdown
- 🎯 Activating role-specific commands

Without story ID:
- 📚 Shows available stories for analysis

Story ID: **$ARGUMENTS**

### 2. Activated Role-Specific Commands

Once a story is selected, the following developer role commands become available:

#### 🎨 Frontend Development
```bash
/frontend_developer_story [story-id]       # UI components and interactions
/fed [story-id]                      # Shortcut for frontend developer
```

#### ⚙️ Backend Development  
```bash
/backend_developer_story [story-id]        # APIs and business logic
/bed [story-id]                      # Shortcut for backend developer
```

#### 🤖 AI Development
```bash
/ai-developer [story-id]             # ML models and intelligent features
/aid [story-id]                      # Shortcut for AI developer
```

#### 🗄️ Database Development
```bash
/database_developer_story [story-id]       # Schema design and optimization
/dbd [story-id]                      # Shortcut for database developer
```

#### 🎨 UX Design
```bash
/ux-designer [story-id]              # User experience and design systems
/uxd [story-id]                      # Shortcut for UX designer
```

#### 🚀 DevOps Engineering
```bash
/devops-engineer [story-id]          # Deployment and infrastructure
/doe [story-id]                      # Shortcut for devops engineer
```

#### 🧪 QA Engineering
```bash
/qa_engineer_story [story-id]              # Testing strategies and quality
/qae [story-id]                      # Shortcut for QA engineer
```

### 3. Context Awareness Features

🧠 **Context Awareness Active:**
• Story ID: [TRACKED]
• Project: [CURRENT_PROJECT]  
• Created Tasks: [TRACKING]
• Cross-Dependencies: [MONITORING]

**Active Context:**
- **Story Tracking**: Maintains focus on selected story
- **Task History**: Prevents duplicate task creation
- **Dependency Mapping**: Tracks cross-team requirements
- **Project Integration**: Uses current project (KAN/DEX)

### 4. Cross-Team Dependencies System

Each role-specific task includes:

#### Dependency Identification
- **Requires from other teams**: What this role needs from others
- **Provides to other teams**: What this role delivers to others
- **Blocks other tasks**: Dependencies that must be completed first
- **Blocked by tasks**: External dependencies affecting this role

#### Dependency Format
```
## Cross-Team Dependencies

### Requires:
- /backend_developer_story - User authentication API endpoints
- /database_developer_story - User profile schema and migrations
- /ux-designer - Component wireframes and design tokens

### Provides:
- /qa_engineer_story - Testable UI components with data-testid attributes
- /devops-engineer - Built frontend assets for deployment pipeline

### Dependencies:
- BLOCKS: QA testing (until components are complete)
- BLOCKED BY: API endpoints (backend) and design system (UX)
```

### 5. Task Creation Format

Tasks created by role-specific commands follow this format:

**Title**: `[Story Name] - [Role Abbreviation]`
- Examples: "User Dashboard Analytics - FE", "Analytics API - BE"

**Description includes**:
- Detailed acceptance criteria
- Technical specifications  
- Cross-team dependencies section
- Implementation guidance
- Testing requirements

### 6. Smart Duplicate Prevention

🔒 **Duplicate Prevention Active:**
• Checking existing tasks for story
• Validating role assignments
• Preventing duplicate task creation

The system tracks:
- Which developer roles have tasks created for the story
- Task IDs and creation timestamps
- Role-specific task completion status
- Cross-dependencies already established

## Integration Features

### Story Context Loading
- Fetches original story details from Jira
- Loads existing task breakdown if available
- Analyzes story complexity and scope
- Identifies required developer roles

### MCP Jira Integration
- Creates tasks with standardized naming: "[Story Name] - [Role]"
- Applies role-specific labels and assignments
- Links tasks to parent story issue
- Includes cross-team dependency tracking

### Enhanced Task Specifications
- Detailed acceptance criteria per role
- Technical implementation guidelines
- Cross-team collaboration requirements
- Testing and validation criteria

## Example Workflow

```bash
# Step 1: Select story for analysis
/story-analysis KAN-15
📋 Loading story: KAN-15 - "User Dashboard Analytics"
🎯 Role-specific commands activated for KAN-15

# Step 2: Create frontend tasks
/frontend_developer_story KAN-15
✅ Created: "User Dashboard Analytics - FE" (KAN-23)
📝 Added cross-team dependencies: requires backend API, UX wireframes

# Step 3: Create backend tasks  
/backend_developer_story KAN-15
✅ Created: "User Dashboard Analytics - BE" (KAN-24)
📝 Added cross-team dependencies: provides API to frontend, requires database schema

# Step 4: Check dependencies
/story-analysis KAN-15
📊 Story Status: 2/7 role tasks created
🔗 Active Dependencies: FE→BE (API), BE→DB (schema), FE→UX (designs)
```

## Error Handling

- **Invalid Story ID**: Prompts for valid story selection
- **Story Not Found**: Searches available stories for suggestions
- **Duplicate Task**: Prevents creation, shows existing task
- **MCP Connection Issues**: Graceful fallback with task summary
- **Missing Dependencies**: Warns about potential blocking issues

## Advanced Features

### Dependency Visualization
```bash
/story-analysis KAN-15 --dependencies
📊 Cross-Team Dependency Map:
🎨 Frontend ← Backend (API) ← Database (schema)
🎨 Frontend ← UX Design (wireframes, tokens)
🧪 QA ← Frontend (components) ← Backend (endpoints)
🚀 DevOps ← Frontend (assets) ← Backend (services)
```

### Role Progress Tracking
```bash
/story-analysis KAN-15 --progress
📈 Story Progress: KAN-15
✅ Frontend Developer: Task created (KAN-23)
✅ Backend Developer: Task created (KAN-24)
⏳ Database Developer: Pending task creation
⏳ UX Designer: Pending task creation
❌ AI Developer: Not required for this story
❌ DevOps Engineer: Not required for this story
❌ QA Engineer: Not required for this story
```

## Next Steps

After using story analysis:
1. Use role-specific commands to create detailed tasks
2. Review cross-team dependencies in created tasks
3. Monitor task progress in Jira web interface
4. Use dependency information for sprint planning

**Ready to dive deep into role-specific task creation with enhanced collaboration tracking!**