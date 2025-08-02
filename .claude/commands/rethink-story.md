---
description: "Revise and refine existing story breakdowns with enhanced developer task generation"
shortcut: "rs"
arguments: true
---

# Rethink Story

Revise, refine, and regenerate your story breakdown with enhanced focus on specific developer roles or requirements.

## Usage

```bash
/rethink-story                           # Interactive story revision mode
/rethink-story "Updated story text..."   # Direct story update
/rs                                      # Shortcut for interactive mode
/rs "Refined story requirements"         # Shortcut with direct update
```

## Story Revision Options

### 1. Story Refinement Mode

!`echo "🔄 Story Rethinking Mode"`
!`echo "========================"`

Updated story text: **$ARGUMENTS**

!`echo "🤔 Choose your revision approach:"`
!`echo "1. 📝 Update story text (modify the original narrative)"`
!`echo "2. 🎯 Focus on specific roles (emphasize certain developer roles)"`
!`echo "3. 📊 Change complexity level (simple/standard/complex breakdown)"`
!`echo "4. 🔧 Technical emphasis (focus on specific technical aspects)"`
!`echo "5. ⚡ Quick regenerate (same story, different perspective)"`

### 2. Revision Strategies

#### Focus on Specific Roles
Emphasize certain developer roles for specialized features:
- **Frontend Focus**: Enhanced UI/UX with advanced interactions
- **Backend Focus**: Robust APIs, microservices, performance
- **AI Focus**: Advanced ML models, intelligent features
- **Database Focus**: Complex data architecture, analytics

#### Technical Emphasis Options
- **Performance & Scalability**: High-traffic, optimization-focused tasks
- **Security & Compliance**: Security-first development approach
- **User Experience**: Accessibility, usability, design-focused
- **Data & Analytics**: Data-driven features, reporting, insights
- **AI & Machine Learning**: Intelligent features, automation

#### Complexity Levels
- **Simple**: High-level tasks, faster implementation
- **Standard**: Balanced granularity, typical breakdown
- **Complex**: Detailed tasks, enterprise-grade requirements

### 3. Enhanced Task Generation

!`echo "🔄 Processing your revision..."`

Based on your revision choice, tasks will be enhanced with:

#### Role-Focused Enhancements
**Frontend Focus Example:**
- [ENHANCED] Advanced UI component architecture
- [ENHANCED] State management optimization
- [ENHANCED] Performance optimization and lazy loading
- [ENHANCED] Advanced animation and interaction design

**Backend Focus Example:**
- [ENHANCED] Microservices architecture design
- [ENHANCED] Advanced API versioning and documentation
- [ENHANCED] Caching and performance optimization
- [ENHANCED] Event-driven architecture implementation

**AI Focus Example:**
- [ENHANCED] Advanced machine learning pipeline design
- [ENHANCED] Model versioning and A/B testing framework
- [ENHANCED] Real-time inference optimization
- [ENHANCED] Automated model retraining system

#### Technical Emphasis Enhancements
**Performance & Scalability:**
- [PERFORMANCE] High-performance API endpoints
- [PERFORMANCE] Database connection pooling
- [PERFORMANCE] Auto-scaling infrastructure setup
- [PERFORMANCE] Performance monitoring and optimization

**Security & Compliance:**
- [SECURITY] Secure API authentication and authorization
- [SECURITY] Input validation and sanitization
- [SECURITY] Security testing and penetration testing
- [SECURITY] Compliance and audit testing

**User Experience:**
- [UX FOCUS] Accessibility-first component development
- [UX FOCUS] Comprehensive user journey mapping
- [UX FOCUS] User testing and feedback integration
- [UX FOCUS] Responsive design across all devices

### 4. Update Options

!`echo "🔄 Revision Complete!"`
!`echo "Available actions:"`
!`echo "1. ✅ Create revised tasks in Jira (new tasks)"`
!`echo "2. 🔄 Update existing Jira tasks (if previously created)"`
!`echo "3. 📋 Preview task details before creation"`
!`echo "4. 🎯 Further refine specific roles"`
!`echo "5. ❌ Cancel and keep original breakdown"`

### 5. Smart Task Enhancement

The revision system includes:
- **Context Preservation**: Remembers previous story context
- **Task Relationships**: Maintains dependencies and links
- **Role Optimization**: Enhances tasks for selected focus areas
- **Complexity Scaling**: Adjusts task granularity as needed

!`echo "📊 Revised tasks will be created with enhanced specifications"`
!`echo "🔌 Using MCP integration for Jira task creation/updates"`

## Integration Features

### Smart Task Enhancement
- Analyzes original story for improvement opportunities
- Suggests additional technical considerations
- Adds industry best practices and patterns
- Includes non-functional requirements

### MCP Jira Updates
- Creates new revised tasks or updates existing ones
- Maintains task relationships and dependencies
- Adds revision history and change tracking
- Links to original story for traceability

### Context Preservation
- Remembers previous story context
- Builds upon existing task breakdown
- Maintains project-specific requirements
- Preserves developer role assignments

## Examples

### Role-Focused Revision
```bash
/rs
Choose revision: 2 (Focus on specific roles)
Roles: frontend, ai
Result: Enhanced frontend components + advanced AI features
```

### Technical Emphasis Revision
```bash
/rs
Choose revision: 4 (Technical emphasis)  
Emphasis: 1 (Performance & Scalability)
Result: Performance-optimized tasks across all roles
```

### Story Update Revision
```bash
/rs "Add mobile app support to the dashboard with offline capabilities"
Result: Mobile-first tasks + offline functionality across roles
```

## Best Practices

### When to Rethink Your Story
- After stakeholder feedback and requirement changes
- When technical constraints become apparent
- For iterative development and sprint planning
- When scaling requirements or adding complexity

### Effective Revision Techniques
- Start with high-level changes, then refine details
- Focus on 2-3 roles for specialized features
- Consider technical debt and maintenance requirements
- Include deployment and monitoring considerations

## Error Handling

- **No Original Story**: Prompts to use `/create-story` first
- **Empty Revision**: Requests update or revision choice
- **MCP Connection Issues**: Graceful fallback with enhanced summary
- **Invalid Options**: Clear guidance and retry prompts

## Next Steps

After story revision:
1. Review enhanced task breakdown
2. Approve task creation or updates in Jira
3. Use `/create-story` for completely new stories
4. Monitor created tasks in Jira web interface

**Ready to refine and enhance your story breakdown!**