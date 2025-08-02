---
description: "Create detailed frontend development tasks for a specific story with cross-team dependencies"
shortcut: "fed"
arguments: true
---

# Frontend Developer

Create comprehensive frontend development tasks for an existing story with detailed specifications and cross-team collaboration tracking.

## Usage

```bash
/frontend-developer [story-id]       # Create frontend tasks for story
/fed [story-id]                      # Shortcut for frontend developer
```

## Frontend Task Creation

### 1. Story Context Loading

🎨 **Frontend Developer Mode**
========================

**Story ID Required**: Please provide a story ID

📋 **Loading story**: $ARGUMENTS  
🔄 **Analyzing frontend requirements**...  
🎨 **Generating detailed frontend tasks**...

Story ID: **$ARGUMENTS**  
Task Type: **Frontend Development**

### 2. Frontend Task Generation

Based on the original story from `/create-story`, detailed frontend tasks will be created:

#### UI Component Development
- **Component Architecture**: Design reusable component structure
- **State Management**: Implement state management (Context/Redux/Zustand)
- **Component Libraries**: Integrate with existing design system
- **Responsive Design**: Mobile-first responsive implementation

#### User Interface Implementation  
- **Layout Components**: Page layouts and navigation structures
- **Interactive Elements**: Forms, buttons, modals, and user controls
- **Data Visualization**: Charts, graphs, and dashboard components
- **Real-time Updates**: WebSocket integration for live data

#### Frontend Performance
- **Code Splitting**: Lazy loading and bundle optimization
- **Performance Optimization**: Memoization and rendering optimization
- **Caching Strategies**: Client-side caching and state persistence
- **SEO & Accessibility**: Search optimization and accessibility compliance

### 3. Cross-Team Dependencies

🔗 **Analyzing cross-team dependencies**...

Each frontend task includes detailed dependency tracking:

#### Dependencies FROM Other Teams:
```
## Cross-Team Dependencies

### Requires:
- /backend-developer - RESTful API endpoints with OpenAPI documentation
- /backend-developer - WebSocket connections for real-time data streaming  
- /database-developer - Data models and API response schemas
- /ux-designer - Component wireframes, design tokens, and interaction specifications
- /ux-designer - Color palette, typography system, and spacing guidelines

### API Requirements:
- Authentication endpoints (login, logout, refresh token)
- User profile management APIs
- Data fetching endpoints with pagination
- File upload/download capabilities
- Error handling and validation responses
```

#### Dependencies TO Other Teams:
```
### Provides:
- /qa-engineer - Testable components with data-testid attributes
- /qa-engineer - Component documentation and usage examples
- /devops-engineer - Built frontend assets and deployment configurations
- /devops-engineer - Environment-specific configuration requirements
- /backend-developer - Frontend API consumption patterns and requirements

### Frontend Deliverables:
- Reusable UI component library
- Frontend routing and navigation structure
- Client-side validation and error handling
- Performance metrics and monitoring hooks
```

### 4. Technical Specifications

⚙️ **Generating technical specifications**...

#### Development Standards
- **Framework**: React/Vue/Angular (based on project tech stack)
- **TypeScript**: Full TypeScript implementation with strict mode
- **Testing**: Unit tests (Jest/Vitest) and component tests (Testing Library)
- **Styling**: CSS-in-JS/SCSS/Tailwind (consistent with project)

#### Architecture Requirements
- **Component Structure**: Atomic design principles
- **State Management**: Centralized state with proper data flow
- **Error Boundaries**: Comprehensive error handling and fallbacks
- **Performance**: Bundle size optimization and Core Web Vitals

#### Quality Assurance
- **Code Quality**: ESLint, Prettier, and Husky pre-commit hooks
- **Accessibility**: WCAG 2.1 AA compliance
- **Browser Support**: Cross-browser compatibility matrix
- **Testing Coverage**: Minimum 80% test coverage

### 5. Task Creation in Jira

📝 **Creating frontend task in Jira**...  
**Title**: [$ARGUMENTS] - FE  
**Type**: Task  
**Labels**: frontend, ui, react, typescript  
**Dependencies**: [CROSS_TEAM_DEPS]

**Task Details Created:**
- **Title Format**: `[Story Name] - FE`
- **Issue Type**: Task (linked to parent story)
- **Labels**: `frontend`, `ui`, `component`, `react`, `typescript`
- **Priority**: Based on story priority
- **Story Points**: Estimated based on complexity

#### Task Description Template:
```markdown
# Frontend Development Task

## Story Context
Original Story: [STORY_ID] - [STORY_TITLE]
Related to: [PARENT_EPIC_IF_EXISTS]

## Frontend Requirements
- UI component development and styling
- User interface interactions and responsive design  
- Client-side state management and real-time updates
- Performance optimization and accessibility compliance

## Technical Specifications
### Framework & Tools
- Frontend Framework: [React/Vue/Angular]
- Language: TypeScript with strict mode
- Styling: [CSS-in-JS/SCSS/Tailwind]
- State Management: [Context/Redux/Zustand]

### Component Requirements
- Responsive design (mobile-first approach)
- Accessibility compliance (WCAG 2.1 AA)
- Performance optimization (lazy loading, memoization)
- Error boundaries and fallback UI

## Cross-Team Dependencies

### Requires:
- /backend-developer - API endpoints and data schemas
- /ux-designer - Component wireframes and design system
- /database-developer - Data models and structure

### Provides:
- /qa-engineer - Testable components with proper data attributes
- /devops-engineer - Built assets and deployment requirements

### Blocking/Blocked Status:
- BLOCKS: QA testing (components must be complete)
- BLOCKED BY: API endpoints (backend) and design specifications (UX)

## Acceptance Criteria
- [ ] All UI components are responsive and accessible
- [ ] Frontend performance meets Core Web Vitals requirements
- [ ] Component tests achieve minimum 80% coverage
- [ ] Cross-browser compatibility verified
- [ ] Design system integration complete
- [ ] API integration functional with error handling
- [ ] Real-time features working (if applicable)

## Definition of Done
- [ ] Code review completed and approved
- [ ] Unit and component tests passing
- [ ] Accessibility audit passed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Deployed to staging environment
```

### 6. Integration Features

#### Story Integration
- Links to parent story issue created by `/create-story`
- Inherits story context and requirements
- Maintains traceability to original narrative

#### Dependency Tracking
- Identifies specific backend API requirements
- Maps design system dependencies
- Tracks QA testing requirements
- Links to DevOps deployment needs

#### Context Awareness
- Prevents duplicate frontend task creation
- Checks existing frontend tasks for the story
- Maintains project-specific frontend standards

## Example Usage

```bash
# After creating story with /create-story
/story-analysis KAN-15
# Activates role-specific commands

/frontend-developer KAN-15
✅ Created: "User Dashboard Analytics - FE" (KAN-25)
📝 Dependencies: Backend API (KAN-24), UX designs (pending)
🔗 Linked to parent story: KAN-15
```

## Error Handling

- **Missing Story ID**: Prompts for required story parameter
- **Story Not Found**: Searches for similar story IDs
- **Duplicate Frontend Task**: Shows existing task, prevents duplicates
- **Missing Dependencies**: Warns about unresolved dependencies

## Next Steps

After creating frontend tasks:
1. Review task details in Jira web interface
2. Coordinate with backend developer for API specifications
3. Work with UX designer for component wireframes
4. Use task for sprint planning and estimation

**Ready to create detailed frontend development tasks with comprehensive cross-team collaboration!**