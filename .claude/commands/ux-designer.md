---
description: "Create detailed UX design tasks for a specific story with wireframes, user research, and design system requirements"
shortcut: "uxd"
arguments: true
---

# UX Designer

Create comprehensive UX design tasks for an existing story with detailed wireframes, user research, and design system specifications.

## Usage

```bash
/ux-designer [story-id]              # Create UX design tasks for story
/uxd [story-id]                      # Shortcut for UX designer
```

## UX Design Task Creation

### 1. Story Context Loading

🎨 **UX Designer Mode**
==================

**Story ID Required**: Please provide a story ID to create UX design tasks.

**Usage**: `/ux-designer [story-id]` or `/uxd [story-id]`

Story ID: **$ARGUMENTS**  
Task Type: **UX Design**

### 2. UX Design Task Generation

Based on the original story from `/create-story`, detailed UX design tasks will be created:

#### User Research & Analysis
- **User Journey Mapping**: End-to-end user experience flow and touchpoints
- **Persona Development**: User persona refinement and behavioral analysis
- **Usability Research**: User interviews, surveys, and behavior analysis
- **Competitive Analysis**: Market research and design pattern analysis

#### Design & Prototyping
- **Wireframe Creation**: Low-fidelity and high-fidelity wireframes
- **Prototype Development**: Interactive prototypes for user testing
- **Visual Design**: UI mockups with branding and visual hierarchy
- **Design System**: Component library and design token management

#### User Experience Optimization
- **Information Architecture**: Content structure and navigation design
- **Interaction Design**: Micro-interactions and animation specifications
- **Accessibility Design**: WCAG compliance and inclusive design practices
- **Responsive Design**: Multi-device experience and breakpoint specifications

### 3. Cross-Team Dependencies

🔗 **UX Design Cross-Team Dependencies Analysis**

Each UX design task includes detailed dependency tracking:

#### Dependencies FROM Other Teams:
```
## Cross-Team Dependencies

### Requires:
- /backend-developer - Data structure and API response formats for UI design
- /frontend-developer - Technical constraints and implementation feasibility
- /ai-developer - AI feature specifications for intelligent UI components
- /database-developer - Data model understanding for form design and validation
- /qa-engineer - Usability testing feedback and accessibility validation

### Research Requirements:
- User research data and behavioral analytics
- Business requirements and success metrics
- Brand guidelines and visual identity standards
- Technical constraints and platform limitations
- Performance requirements for design decisions
```

#### Dependencies TO Other Teams:
```
### Provides:
- /frontend-developer - Component wireframes, design tokens, and style guide
- /frontend-developer - Interactive prototypes and user flow specifications
- /backend-developer - Data visualization requirements and dashboard specifications
- /qa-engineer - Usability testing scenarios and accessibility requirements
- /ai-developer - User interface requirements for AI-powered features

### UX Deliverables:
- Complete design system with components and tokens
- User journey maps and flow diagrams
- Wireframes and interactive prototypes
- Accessibility guidelines and compliance documentation
- Usability testing reports and optimization recommendations
- Design handoff specifications for development
```

### 4. Technical Specifications

⚙️ **UX Design Technical Specifications**

#### Design Standards
- **Design Tools**: Figma/Sketch/Adobe XD for wireframes and prototypes
- **Design System**: Component-based design with reusable elements
- **Accessibility**: WCAG 2.1 AA compliance with inclusive design principles
- **Responsive Design**: Mobile-first approach with fluid grid systems

#### User Experience Requirements
- **Usability**: Intuitive navigation with clear information architecture
- **Performance**: Design optimized for fast loading and smooth interactions
- **Accessibility**: Screen reader compatibility and keyboard navigation
- **Cross-browser**: Consistent experience across modern browsers

#### Design Documentation
- **Style Guide**: Typography, color palette, spacing, and grid systems
- **Component Library**: Reusable UI components with usage guidelines
- **Interaction Specs**: Animation timing, transitions, and micro-interactions
- **Handoff Documentation**: Developer-friendly specifications and assets

### 5. Task Creation in Jira

📝 **UX Design Task Creation in Jira**

**Task Format:**
- **Title**: `[Story Name] - UX`
- **Type**: Task (linked to parent story)
- **Labels**: `ux`, `design`, `wireframes`, `accessibility`, `prototype`
- **Dependencies**: Cross-team dependencies tracked

**Task Details Created:**
- **Title Format**: `[Story Name] - UX`
- **Issue Type**: Task (linked to parent story)
- **Labels**: `ux`, `design`, `wireframes`, `accessibility`, `prototype`, `figma`
- **Priority**: Based on story priority and user impact
- **Story Points**: Estimated based on design complexity and research needs

#### Task Description Template:
```markdown
# UX Design Task

## Story Context
Original Story: [STORY_ID] - [STORY_TITLE]
Related to: [PARENT_EPIC_IF_EXISTS]

## UX Design Requirements
- User experience wireframes and design systems
- User journey mapping and interaction design
- Accessibility compliance and usability testing
- Responsive design across all devices and breakpoints

## Technical Specifications
### Design Tools & Framework
- Design Platform: [Figma/Sketch/Adobe XD]
- Prototyping: Interactive prototypes with micro-interactions
- Design System: Component-based design with design tokens
- Collaboration: Design handoff with developer specifications

### User Experience Goals
- Intuitive navigation and clear information architecture
- Accessibility compliance (WCAG 2.1 AA standards)
- Responsive design with mobile-first approach
- Performance-optimized design decisions

## Design Deliverables

### 1. User Research & Analysis
- User persona validation and behavioral analysis
- User journey mapping with touchpoint identification
- Competitive analysis and design pattern research
- Usability heuristic evaluation

### 2. Wireframes & Prototypes
- Low-fidelity wireframes for concept validation
- High-fidelity mockups with visual design
- Interactive prototypes for user testing
- Responsive design across device breakpoints

### 3. Design System & Components
- Design token system (colors, typography, spacing)
- Component library with usage guidelines
- Icon system and illustration guidelines
- Animation and interaction specifications

### 4. User Testing & Validation
- Usability testing scenarios and tasks
- A/B testing designs for optimization
- Accessibility testing with assistive technologies
- Performance impact assessment of design decisions

## User Experience Specifications

### Information Architecture:
- Navigation structure and menu hierarchy
- Content organization and categorization
- Search functionality and filtering systems
- Breadcrumb navigation and wayfinding

### Interaction Design:
- Button states and hover effects
- Form validation and error messaging
- Loading states and progress indicators
- Micro-interactions and feedback systems

### Responsive Design:
- Mobile breakpoints: 320px, 768px, 1024px, 1440px+
- Touch-friendly interface design for mobile devices
- Progressive enhancement for different capabilities
- Content prioritization across screen sizes

## Accessibility Requirements

### WCAG 2.1 AA Compliance:
- Color contrast ratios (4.5:1 for normal text)
- Keyboard navigation and focus management
- Screen reader compatibility and ARIA labels
- Alternative text for images and media

### Inclusive Design:
- High contrast mode support
- Text scaling up to 200% without horizontal scrolling
- Motion preferences and animation controls
- Cognitive accessibility and clear language

## Cross-Team Dependencies

### Requires:
- /backend-developer - Data structure and API specifications for form design
- /frontend-developer - Technical feasibility validation for design concepts
- /ai-developer - AI feature requirements for intelligent UI components

### Provides:
- /frontend-developer - Complete design system and component specifications
- /qa-engineer - Usability testing scenarios and accessibility requirements
- /backend-developer - Data visualization and dashboard design requirements

### Blocking/Blocked Status:
- BLOCKS: Frontend development (designs must be approved)
- BLOCKED BY: Requirements clarification and user research completion

## Design System Components

### Core Components:
- Navigation (header, sidebar, breadcrumbs)
- Forms (inputs, selectors, validation)
- Data Display (tables, cards, lists)
- Feedback (alerts, notifications, loading)
- Actions (buttons, links, controls)

### Layout Components:
- Grid system and container layouts
- Page templates and section layouts
- Modal and overlay patterns
- Responsive component behavior

## User Testing Plan

### Testing Scenarios:
- Primary user flow completion tasks
- Accessibility testing with screen readers
- Mobile device usability testing
- Performance impact on user experience

### Success Metrics:
- Task completion rate > 90%
- Time to complete primary tasks < [X] seconds
- User satisfaction score > 4.0/5.0
- Accessibility compliance verification

## Acceptance Criteria
- [ ] User journey maps completed and validated
- [ ] Wireframes created for all key screens and flows
- [ ] Interactive prototype ready for user testing
- [ ] Design system components documented
- [ ] Accessibility requirements specified (WCAG 2.1 AA)
- [ ] Responsive design specifications complete
- [ ] Usability testing completed with positive results
- [ ] Design handoff documentation ready for development

## Definition of Done
- [ ] Design review completed and stakeholder approved
- [ ] User testing conducted with positive feedback
- [ ] Accessibility compliance verified
- [ ] Responsive design tested across devices
- [ ] Design system updated with new components
- [ ] Developer handoff completed with specifications
- [ ] Design documentation updated and accessible
- [ ] Frontend implementation review and approval
```

### 6. Integration Features

#### Story Integration
- Links to parent story issue created by `/create-story`
- Inherits story context and user experience requirements
- Maintains traceability to original user-centered narrative

#### Design System Integration
- Manages component library and design tokens
- Tracks design consistency across features
- Integrates with frontend development workflow
- Maintains brand and style guide compliance

#### User Research Integration
- Tracks user feedback and testing results
- Manages persona updates and journey mapping
- Integrates usability testing findings
- Monitors accessibility compliance and improvements

## Example Usage

```bash
# After creating story with /create-story
/story-analysis KAN-15
# Activates role-specific commands

/ux-designer KAN-15
✅ Created: "User Dashboard Analytics - UX" (KAN-30)
📝 Dependencies: Backend API specs (KAN-26), Frontend constraints (KAN-25)
🔗 Linked to parent story: KAN-15
🎨 Deliverables: Wireframes, prototypes, design system components
```

## Error Handling

- **Missing Story ID**: Prompts for required story parameter
- **Story Not Found**: Searches for similar story IDs
- **Duplicate UX Task**: Shows existing task, prevents duplicates
- **Missing Research Data**: Warns about user research requirements

## Next Steps

After creating UX design tasks:
1. Review design requirements in Jira web interface
2. Coordinate with frontend developer for technical constraints
3. Plan user research and testing sessions
4. Set up design system and component library

**Ready to create detailed UX design tasks with comprehensive user experience specifications and cross-team collaboration!**