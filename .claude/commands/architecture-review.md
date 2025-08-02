---
description: "Analyze existing system architecture"
shortcut: "ar"
arguments: true
---

# Architecture Review

Comprehensive analysis of existing system architecture and recommendations for improvements.

## System Overview

Target: **$ARGUMENTS**

!`if [ -n "$ARGUMENTS" ]; then
    component="$ARGUMENTS"
    echo "🔍 Reviewing: $component architecture"
    
    case "$component" in
        "frontend"|"ui")
            echo "🎨 Frontend Architecture Review"
            echo "📊 Analysis focus:"
            echo "• Component structure and hierarchy"
            echo "• State management patterns"
            echo "• Routing and navigation"
            echo "• Performance optimization"
            echo "• Bundle size and code splitting"
            ;;
        "backend"|"api")
            echo "🔧 Backend Architecture Review"
            echo "📡 Analysis focus:"
            echo "• API design and RESTful patterns"
            echo "• Service layer organization"
            echo "• Data flow and processing"
            echo "• Error handling and logging"
            echo "• Scalability and performance"
            ;;
        "database"|"data")
            echo "🗄️  Database Architecture Review"
            echo "📊 Analysis focus:"
            echo "• Schema design and normalization"
            echo "• Index optimization"
            echo "• Query performance"
            echo "• Data integrity and constraints"
            echo "• Backup and recovery strategy"
            ;;
        "security")
            echo "🔒 Security Architecture Review"
            echo "🛡️  Analysis focus:"
            echo "• Authentication and authorization"
            echo "• Data encryption and protection"
            echo "• Input validation and sanitization"
            echo "• Security headers and policies"
            echo "• Vulnerability assessment"
            ;;
        *)
            echo "🏗️  Custom Component: $component"
            echo "💡 Review areas:"
            echo "• Design patterns and principles"
            echo "• Code organization and structure"
            echo "• Dependencies and coupling"
            echo "• Performance characteristics"
            echo "• Maintainability and testability"
            ;;
    esac
else
    echo "🏛️  Full System Architecture Review"
    echo ""
    echo "📋 Components to review:"
    echo "• Frontend architecture"
    echo "• Backend services"
    echo "• Database design"
    echo "• Security implementation"
    echo "• Infrastructure and deployment"
    echo ""
    echo "💡 Usage: /architecture-review [component]"
    echo "Examples: /architecture-review frontend, /architecture-review database"
fi`

## Current Architecture Analysis

!`echo "📊 System architecture assessment:"`

### Technology Stack
!`echo "🔍 Detected architecture patterns:"`
!`if [ -f "package.json" ]; then
    echo "📦 JavaScript/Node.js Ecosystem"
    
    # Frontend frameworks
    if grep -q react package.json; then
        echo "⚛️  React frontend detected"
        if grep -q next package.json; then
            echo "  ▲ Next.js framework (SSR/SSG)"
        fi
        if grep -q "react-router" package.json; then
            echo "  🛣️  React Router (client-side routing)"
        fi
    fi
    
    # State management
    if grep -q redux package.json; then
        echo "📊 Redux state management"
    fi
    if grep -q zustand package.json; then
        echo "📊 Zustand state management"
    fi
    
    # Backend frameworks
    if grep -q express package.json; then
        echo "🚀 Express.js backend"
    fi
    if grep -q fastify package.json; then
        echo "⚡ Fastify backend"
    fi
    
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    echo "🐍 Python Ecosystem"
    
    if grep -q django requirements.txt 2>/dev/null; then
        echo "🎸 Django framework (full-stack)"
    fi
    if grep -q flask requirements.txt 2>/dev/null; then
        echo "🌶️  Flask framework (microframework)"
    fi
    if grep -q fastapi requirements.txt 2>/dev/null; then
        echo "⚡ FastAPI framework (async API)"
    fi
    
elif [ -f "Cargo.toml" ]; then
    echo "🦀 Rust Ecosystem"
    
    if grep -q actix-web Cargo.toml; then
        echo "🕷️  Actix-web framework"
    fi
    if grep -q warp Cargo.toml; then
        echo "🌊 Warp framework"
    fi
    
elif [ -f "go.mod" ]; then
    echo "🐹 Go Ecosystem"
    
    if grep -q gin go.mod; then
        echo "🍸 Gin framework"
    fi
    if grep -q echo go.mod; then
        echo "📢 Echo framework"
    fi
    
else
    echo "❓ Architecture pattern not immediately identifiable"
fi`

### Project Structure Analysis
!`echo "📁 Directory structure assessment:"`
!`find . -maxdepth 3 -type d -name ".*" -prune -o -type d -print | grep -v node_modules | head -15`

### Component Architecture
!`echo "🧩 Component organization:"`
!`if find . -name "components" -type d | head -1 | grep -q .; then
    echo "✅ Components directory structure found"
    find . -name "components" -type d | head -3 | while read comp_dir; do
        comp_count=$(find "$comp_dir" -name "*.jsx" -o -name "*.tsx" -o -name "*.vue" | wc -l)
        echo "  📊 $comp_dir: $comp_count components"
    done
else
    echo "💡 No dedicated components directory detected"
fi

if find . -name "*.jsx" -o -name "*.tsx" -o -name "*.vue" | head -5 | grep -q .; then
    echo "🎨 Frontend components detected:"
    find . -name "*.jsx" -o -name "*.tsx" -o -name "*.vue" | head -5 | sed 's/.*\//  /'
fi`

## Architecture Patterns Assessment

### Design Patterns Used
!`echo "🎯 Design pattern analysis:"`
!`pattern_score=0

# Check for MVC pattern
if find . -name "*controller*" -o -name "*model*" -o -name "*view*" | head -1 | grep -q .; then
    echo "✅ MVC pattern elements detected"
    pattern_score=$((pattern_score + 1))
fi

# Check for component-based architecture
if find . -name "*component*" | head -1 | grep -q .; then
    echo "✅ Component-based architecture"
    pattern_score=$((pattern_score + 1))
fi

# Check for service layer
if find . -name "*service*" -o -name "*services*" | head -1 | grep -q .; then
    echo "✅ Service layer pattern"
    pattern_score=$((pattern_score + 1))
fi

# Check for repository pattern
if find . -name "*repository*" -o -name "*repo*" | head -1 | grep -q .; then
    echo "✅ Repository pattern"
    pattern_score=$((pattern_score + 1))
fi

echo "📊 Architecture pattern score: $pattern_score/4"`

### Code Organization Quality
!`echo "📋 Code organization assessment:"`
!`# Check for separation of concerns
if [ -d "src" ]; then
    echo "✅ Source code organization (src directory)"
fi

if [ -d "tests" ] || [ -d "test" ] || [ -d "__tests__" ]; then
    echo "✅ Test code organization"
fi

if [ -d "docs" ] || [ -d "documentation" ]; then
    echo "✅ Documentation organization"
fi

# Check for configuration organization
if [ -d "config" ] || [ -f "config.js" ] || [ -f "config.json" ]; then
    echo "✅ Configuration management"
fi`

## Performance Architecture

### Build and Bundle Analysis
!`if [ -f "package.json" ]; then
    echo "📦 Build architecture review:"
    
    if grep -q '"build"' package.json; then
        echo "✅ Build process configured"
    fi
    
    if [ -d "build" ] || [ -d "dist" ]; then
        build_dir=$([ -d "build" ] && echo "build" || echo "dist")
        build_size=$(du -sh "$build_dir" 2>/dev/null | cut -f1)
        echo "📊 Build output size: $build_size"
    fi
    
    # Check for optimization tools
    if grep -q webpack package.json; then
        echo "📦 Webpack bundling"
    fi
    if grep -q vite package.json; then
        echo "⚡ Vite build tool"
    fi
    if grep -q parcel package.json; then
        echo "📦 Parcel bundler"
    fi
fi`

### Caching Strategy
!`echo "⚡ Caching architecture assessment:"`
!`if find . -name "*.js" -o -name "*.ts" | xargs grep -l "cache\|Cache\|redis\|Redis" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Caching implementation detected"
    find . -name "*.js" -o -name "*.ts" | xargs grep -l "cache\|Cache\|redis\|Redis" 2>/dev/null | head -3 | while read file; do
        echo "  📄 $(basename "$file")"
    done
else
    echo "💡 No obvious caching strategy detected"
fi`

## Security Architecture

### Authentication & Authorization
!`echo "🔒 Security architecture review:"`
!`if find . -name "*.js" -o -name "*.ts" | xargs grep -l "auth\|jwt\|passport\|oauth" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Authentication system detected"
    
    if find . -name "*.js" -o -name "*.ts" | xargs grep -l "jwt\|jsonwebtoken" 2>/dev/null | head -1 | grep -q .; then
        echo "  🎫 JWT token-based authentication"
    fi
    
    if find . -name "*.js" -o -name "*.ts" | xargs grep -l "passport" 2>/dev/null | head -1 | grep -q .; then
        echo "  📓 Passport.js authentication"
    fi
    
    if find . -name "*.js" -o -name "*.ts" | xargs grep -l "oauth" 2>/dev/null | head -1 | grep -q .; then
        echo "  🔐 OAuth integration"
    fi
else
    echo "⚠️  No authentication system detected"
fi`

### Input Validation
!`if find . -name "*.js" -o -name "*.ts" | xargs grep -l "validate\|joi\|yup\|zod" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Input validation detected"
else
    echo "⚠️  No input validation library detected"
fi`

## Data Architecture

### Database Design
!`echo "🗄️  Data architecture assessment:"`
!`if find . -name "*.js" -o -name "*.ts" -o -name "*.py" | xargs grep -l "database\|db\|mongodb\|mysql\|postgresql" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Database integration detected"
    
    # Check database types
    if find . -name "*.js" -o -name "*.ts" | xargs grep -l "mongodb\|mongoose" 2>/dev/null | head -1 | grep -q .; then
        echo "  🍃 MongoDB (NoSQL)"
    fi
    
    if find . -name "*.js" -o -name "*.ts" | xargs grep -l "mysql\|pg\|postgresql" 2>/dev/null | head -1 | grep -q .; then
        echo "  🐘 SQL Database (MySQL/PostgreSQL)"
    fi
    
    if find . -name "*.js" -o -name "*.ts" | xargs grep -l "sqlite" 2>/dev/null | head -1 | grep -q .; then
        echo "  💎 SQLite"
    fi
else
    echo "💡 No database integration detected"
fi`

### Data Models
!`if find . -name "*model*" -o -name "*schema*" | head -1 | grep -q .; then
    echo "📊 Data models detected:"
    find . -name "*model*" -o -name "*schema*" | head -5 | sed 's/.*\//  /'
else
    echo "💡 No explicit data models found"
fi`

## Architecture Quality Assessment

### Maintainability Score
!`echo "🔧 Maintainability assessment:"`
!`maintainability=0

# Code organization
if [ -d "src" ]; then maintainability=$((maintainability + 1)); fi

# Testing
if [ -d "tests" ] || [ -d "test" ] || [ -d "__tests__" ]; then
    maintainability=$((maintainability + 1))
fi

# Documentation
if [ -f "README.md" ]; then maintainability=$((maintainability + 1)); fi

# Configuration management
if [ -f ".env.example" ] || [ -d "config" ]; then
    maintainability=$((maintainability + 1))
fi

# Linting/formatting
if [ -f ".eslintrc.json" ] || [ -f ".eslintrc.js" ]; then
    maintainability=$((maintainability + 1))
fi

echo "📊 Maintainability score: $maintainability/5"`

### Scalability Assessment
!`echo "📈 Scalability assessment:"`
!`scalability=0

# Modular architecture
if find . -name "*service*" -o -name "*module*" | head -1 | grep -q .; then
    echo "✅ Modular architecture detected"
    scalability=$((scalability + 1))
fi

# Caching
if find . -name "*.js" -o -name "*.ts" | xargs grep -l "cache" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Caching strategy present"
    scalability=$((scalability + 1))
fi

# Database optimization
if find . -name "*.js" -o -name "*.ts" | xargs grep -l "index\|Index" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Database indexing considerations"
    scalability=$((scalability + 1))
fi

echo "📊 Scalability readiness: $scalability/3"`

## Architecture Recommendations

### High Priority Improvements
1. **Security Enhancements**
   - Implement comprehensive input validation
   - Add rate limiting and throttling
   - Enhance authentication and authorization
   - Add security headers and HTTPS enforcement

2. **Performance Optimization**
   - Implement caching strategies
   - Optimize database queries and indexes
   - Add code splitting and lazy loading
   - Implement CDN for static assets

3. **Code Organization**
   - Establish clear separation of concerns
   - Implement consistent design patterns
   - Add comprehensive error handling
   - Enhance logging and monitoring

### Medium Priority Improvements
1. **Testing Infrastructure**
   - Add unit and integration tests
   - Implement end-to-end testing
   - Add code coverage tracking
   - Set up continuous integration

2. **Documentation**
   - Create architecture documentation
   - Add API documentation
   - Document deployment procedures
   - Create developer onboarding guides

3. **Monitoring & Observability**
   - Implement application monitoring
   - Add performance metrics
   - Set up error tracking
   - Create health check endpoints

### Future Considerations
1. **Microservices Migration**
   - Evaluate service boundaries
   - Plan data consistency strategies
   - Design service communication patterns
   - Implement service discovery

2. **Cloud-Native Features**
   - Containerization with Docker
   - Kubernetes orchestration
   - Serverless function integration
   - Multi-region deployment

## Action Items

1. **Immediate Actions**
   - Address critical security vulnerabilities
   - Fix performance bottlenecks
   - Improve error handling
   - Add missing documentation

2. **Short-term Goals (1-3 months)**
   - Implement comprehensive testing
   - Add monitoring and logging
   - Optimize database performance
   - Enhance security measures

3. **Long-term Vision (6-12 months)**
   - Consider architectural refactoring
   - Evaluate new technology adoption
   - Plan scalability improvements
   - Implement advanced monitoring

## Documentation Template

```markdown
# Architecture Review: [Component]

## Current State
- Description of current implementation
- Key components and their responsibilities
- Technology stack and dependencies

## Strengths
- What works well in the current architecture
- Best practices already implemented
- Performance characteristics

## Areas for Improvement
- Identified architectural issues
- Technical debt items
- Performance bottlenecks

## Recommendations
- Short-term improvements
- Long-term architectural changes
- Technology upgrade paths

## Implementation Plan
- Priority order of changes
- Resource requirements
- Timeline estimates
```

## Next Steps

1. **Create Improvement Plan**: Use findings to create targeted improvement roadmap
2. **Technology Analysis**: Use `/tech-stack-analysis` for technology recommendations  
3. **Design New Components**: Use `/design-system` for architecture planning
4. **Performance Review**: Use `/performance-review` for optimization opportunities

Focus on high-impact, low-effort improvements first to maximize architectural benefits.