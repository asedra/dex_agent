---
description: "Implement frontend development tasks from Jira with task ID parameter"
shortcut: "fed"
arguments: true
---

# Frontend Developer

Implement specific frontend development tasks from Jira by providing the task ID.

## Usage

```bash
/frontend-developer [task-id]        # Implement frontend task
/fed [task-id]                       # Shortcut for frontend developer
```

## Frontend Task Implementation

### 1. Task Loading & Analysis

🎨 **Frontend Developer Mode**
========================

**Task ID Required**: Please provide a task ID to implement frontend features.

📋 **Loading task**: $ARGUMENTS  
🔄 **Analyzing frontend requirements**...  
🎨 **Starting frontend implementation**...

Task ID: **$ARGUMENTS**  
Implementation Type: **Frontend Development**

### 2. Implementation Workflow

Based on the task details from Jira, the implementation will include:

#### UI Component Development
- **Component Creation**: Build React/Vue/Angular components
- **Styling Implementation**: Apply CSS/SCSS/Tailwind styles
- **Responsive Design**: Mobile-first responsive implementation
- **State Management**: Implement component state and props

#### User Interface Features
- **Interactive Elements**: Forms, buttons, modals, and controls
- **Data Display**: Tables, lists, cards, and data visualization
- **Navigation**: Routing, menus, and user flow implementation
- **Real-time Updates**: WebSocket integration for live data

#### Frontend Integration
- **API Integration**: Connect to backend endpoints
- **Error Handling**: User-friendly error messages and fallbacks
- **Loading States**: Skeleton screens and progress indicators
- **Performance**: Code splitting and optimization

### 3. Development Steps

🔧 **Implementation Process**:

1. **Task Analysis**: Load task details and acceptance criteria
2. **Environment Setup**: Configure development environment
3. **Component Development**: Build required UI components
4. **Styling & Design**: Apply design system and responsive styles
5. **Integration**: Connect with APIs and external services
6. **Testing**: Write and run component tests
7. **Quality Check**: Lint, accessibility, and performance validation

### 4. Code Implementation

#### Component Structure
```javascript
// Example component implementation
import React, { useState, useEffect } from 'react';
import './ComponentName.styles.css';

const ComponentName = ({ props }) => {
  const [state, setState] = useState(null);

  useEffect(() => {
    // Implementation based on task requirements
  }, []);

  return (
    <div className="component-name" data-testid="component-name">
      {/* UI implementation based on task specs */}
    </div>
  );
};

export default ComponentName;
```

#### Testing Implementation
```javascript
// Component tests
import { render, screen, fireEvent } from '@testing-library/react';
import ComponentName from './ComponentName';

describe('ComponentName', () => {
  test('should render correctly', () => {
    render(<ComponentName />);
    expect(screen.getByTestId('component-name')).toBeInTheDocument();
  });
});
```

### 5. Task Completion Validation

✅ **Implementation Checklist**:
- [ ] All UI components implemented according to specifications
- [ ] Responsive design working on all screen sizes
- [ ] API integration functional with proper error handling
- [ ] Component tests written and passing
- [ ] Accessibility compliance validated
- [ ] Performance optimization applied
- [ ] Code review ready

### 6. Integration with Development Tools

#### Build & Development
- Run `npm run dev` or equivalent for development server
- Execute `npm run build` for production build
- Use `npm run test` for component testing

#### Quality Assurance
- ESLint and Prettier for code quality
- Accessibility testing with axe-core
- Performance monitoring with Lighthouse
- Cross-browser compatibility validation

## Example Usage

```bash
# Implement specific frontend task
/frontend-developer KAN-25
📋 Loading task: KAN-25 - "User Dashboard Analytics - FE"
🎨 Implementing dashboard components...
✅ Components created: DashboardLayout, AnalyticsChart, DataTable
🧪 Tests written and passing
🚀 Ready for code review
```

## Error Handling

- **Missing Task ID**: Prompts for required task parameter
- **Task Not Found**: Searches for similar task IDs in project
- **Implementation Errors**: Provides debugging guidance and solutions
- **Dependency Issues**: Guides through dependency resolution

## Integration Features

- **Jira Integration**: Automatic task status updates and progress tracking
- **Git Integration**: Commits with proper task references
- **CI/CD Integration**: Automated testing and build validation
- **Team Collaboration**: Code review requests and team notifications

**Ready to implement frontend tasks efficiently with comprehensive development workflow!**