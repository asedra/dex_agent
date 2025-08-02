---
description: "Create comprehensive system architecture design"
shortcut: "ds"
arguments: true
---

# Design System

Create comprehensive system architecture and design documentation.

## System Overview

Target: **$ARGUMENTS**

!`if [ -n "$ARGUMENTS" ]; then
    component="$ARGUMENTS"
    echo "🎯 Designing: $component"
    
    case "$component" in
        "database"|"db")
            echo "🗄️  Database Architecture Design"
            echo "📊 Components to consider:"
            echo "• Data models and relationships"
            echo "• Indexing strategy"
            echo "• Scaling approach (vertical/horizontal)"
            echo "• Backup and recovery"
            echo "• Performance optimization"
            ;;
        "api"|"backend")
            echo "🔧 API/Backend Architecture Design"
            echo "📡 Components to consider:"
            echo "• RESTful API design"
            echo "• Authentication/Authorization"
            echo "• Rate limiting and throttling"
            echo "• Error handling and logging"
            echo "• Microservices vs monolith"
            ;;
        "frontend"|"ui")
            echo "🎨 Frontend Architecture Design"
            echo "🖥️  Components to consider:"
            echo "• Component structure and hierarchy"
            echo "• State management strategy"
            echo "• Routing and navigation"
            echo "• Performance optimization"
            echo "• Responsive design patterns"
            ;;
        "security")
            echo "🔒 Security Architecture Design"
            echo "🛡️  Components to consider:"
            echo "• Authentication mechanisms"
            echo "• Data encryption (at rest/in transit)"
            echo "• Security headers and policies"
            echo "• Vulnerability management"
            echo "• Compliance requirements"
            ;;
        *)
            echo "🏗️  Custom Component: $component"
            echo "💡 Consider these aspects:"
            echo "• Purpose and responsibilities"
            echo "• Dependencies and integrations"
            echo "• Scalability requirements"
            echo "• Performance considerations"
            echo "• Maintenance and monitoring"
            ;;
    esac
else
    echo "🏛️  Full System Architecture Design"
    echo ""
    echo "📋 System components to design:"
    echo "• Frontend (User Interface)"
    echo "• Backend API (Business Logic)"
    echo "• Database (Data Storage)"
    echo "• Security (Access Control)"
    echo "• Infrastructure (Deployment)"
    echo ""
    echo "💡 Usage: /design-system [component]"
    echo "Examples: /design-system database, /design-system api"
fi`

## Current System Analysis

!`echo "📊 Current system analysis:"`

### Technology Stack Detection
!`echo "🔍 Detected technologies:"`
!`if [ -f "package.json" ]; then
    echo "📦 Node.js/JavaScript project"
    if grep -q react package.json; then
        echo "⚛️  React frontend detected"
    fi
    if grep -q express package.json; then
        echo "🚀 Express backend detected"
    fi
    if grep -q next package.json; then
        echo "▲ Next.js framework detected"
    fi
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    echo "🐍 Python project"
    if grep -q django requirements.txt 2>/dev/null; then
        echo "🎸 Django framework detected"
    fi
    if grep -q flask requirements.txt 2>/dev/null; then
        echo "🌶️  Flask framework detected"
    fi
elif [ -f "Cargo.toml" ]; then
    echo "🦀 Rust project"
elif [ -f "go.mod" ]; then
    echo "🐹 Go project"
else
    echo "❓ Unknown technology stack"
fi`

### Project Structure
!`echo "📁 Project structure analysis:"`
!`find . -maxdepth 2 -type d -name ".*" -prune -o -type d -print | grep -v node_modules | head -8`

## Architecture Patterns

### Design Patterns
Based on your project, consider these patterns:

#### Frontend Patterns
- **Component-Based Architecture**: Modular, reusable UI components
- **State Management**: Centralized state with Redux/Zustand/Context
- **Routing**: Client-side routing with React Router/Next.js
- **Lazy Loading**: Code splitting and dynamic imports

#### Backend Patterns
- **MVC Pattern**: Model-View-Controller separation
- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic separation
- **Middleware Pattern**: Request/response pipeline

#### Database Patterns
- **Repository Pattern**: Data access abstraction
- **Unit of Work**: Transaction management
- **CQRS**: Command Query Responsibility Segregation
- **Event Sourcing**: Event-driven data management

## System Components

### Core Components
1. **User Interface Layer**
   - Presentation components
   - User interaction handling
   - Responsive design implementation
   - Accessibility features

2. **Business Logic Layer**
   - Application services
   - Domain models and entities
   - Business rules implementation
   - Workflow orchestration

3. **Data Access Layer**
   - Database connections
   - Data models and schemas
   - Query optimization
   - Caching strategies

4. **Infrastructure Layer**
   - Deployment configurations
   - Monitoring and logging
   - Security implementations
   - External service integrations

## Scalability Design

### Horizontal Scaling
- **Load Balancing**: Distribute traffic across multiple servers
- **Database Sharding**: Distribute data across multiple databases
- **Microservices**: Split application into smaller, independent services
- **CDN**: Content delivery network for static assets

### Vertical Scaling
- **Resource Optimization**: CPU, memory, storage optimization
- **Caching**: In-memory caching (Redis, Memcached)
- **Database Optimization**: Indexing, query optimization
- **Code Optimization**: Algorithm and data structure improvements

## Security Design

### Authentication & Authorization
- **Multi-factor Authentication**: Enhanced security measures
- **JWT Tokens**: Stateless authentication
- **Role-Based Access Control**: Permission management
- **OAuth Integration**: Third-party authentication

### Data Protection
- **Encryption**: Data encryption at rest and in transit
- **Input Validation**: Prevent injection attacks
- **Security Headers**: HTTP security headers
- **Audit Logging**: Security event tracking

## Performance Design

### Optimization Strategies
- **Caching Layers**: Multiple levels of caching
- **Database Optimization**: Query optimization and indexing
- **Asset Optimization**: Minification, compression, bundling
- **Lazy Loading**: On-demand resource loading

### Monitoring & Metrics
- **Performance Monitoring**: Real-time performance tracking
- **Error Tracking**: Comprehensive error logging
- **Usage Analytics**: User behavior analysis
- **Infrastructure Monitoring**: Server and database monitoring

## Documentation Template

```markdown
# System Architecture: [Component Name]

## Overview
Brief description of the component's purpose and responsibilities.

## Components
- Component A: Description and responsibilities
- Component B: Description and responsibilities

## Data Flow
1. Step 1: Description
2. Step 2: Description
3. Step 3: Description

## Dependencies
- Internal dependencies
- External dependencies
- Third-party services

## Scalability Considerations
- Current limitations
- Scaling strategies
- Performance requirements

## Security Measures
- Authentication mechanisms
- Data protection measures
- Security vulnerabilities addressed

## Deployment Strategy
- Environment configurations
- Deployment process
- Rollback procedures

## Monitoring & Maintenance
- Health checks
- Performance metrics
- Maintenance procedures
```

## Next Steps

1. **Create Diagrams**: Use `/create-diagram` to visualize the architecture
2. **Technology Analysis**: Use `/tech-stack-analysis` for technology recommendations
3. **Review Existing**: Use `/architecture-review` to analyze current implementation
4. **Document Design**: Create comprehensive architecture documentation

Use specific component names with this command to get targeted design guidance.