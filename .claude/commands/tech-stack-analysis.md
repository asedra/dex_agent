---
description: "Technology evaluation and recommendations"
shortcut: "tsa"
arguments: true
---

# Tech Stack Analysis

Comprehensive technology evaluation and recommendations for optimal development stack.

## Technology Assessment

Target: **$ARGUMENTS**

!`if [ -n "$ARGUMENTS" ]; then
    tech_area="$ARGUMENTS"
    echo "🔍 Analyzing: $tech_area technology stack"
    
    case "$tech_area" in
        "frontend"|"ui"|"client")
            echo "🎨 Frontend Technology Analysis"
            echo "📊 Evaluation areas:"
            echo "• JavaScript frameworks (React, Vue, Angular)"
            echo "• Build tools and bundlers"
            echo "• State management solutions"
            echo "• CSS frameworks and styling"
            echo "• Testing frameworks"
            ;;
        "backend"|"server"|"api")
            echo "🔧 Backend Technology Analysis"
            echo "📡 Evaluation areas:"
            echo "• Server frameworks and runtimes"
            echo "• Database technologies"
            echo "• API design and protocols"
            echo "• Authentication and security"
            echo "• Caching and performance"
            ;;
        "database"|"data"|"storage")
            echo "🗄️  Database Technology Analysis"
            echo "📊 Evaluation areas:"
            echo "• SQL vs NoSQL considerations"
            echo "• Database engines and performance"
            echo "• Data modeling approaches"
            echo "• Scaling and replication strategies"
            echo "• Backup and recovery solutions"
            ;;
        "devops"|"deployment"|"infrastructure")
            echo "🚀 DevOps Technology Analysis"
            echo "☁️  Evaluation areas:"
            echo "• Cloud platforms and services"
            echo "• Containerization and orchestration"
            echo "• CI/CD pipelines and automation"
            echo "• Monitoring and logging tools"
            echo "• Infrastructure as Code"
            ;;
        *)
            echo "🛠️  Custom Technology Area: $tech_area"
            echo "💡 Analysis approach:"
            echo "• Current technology evaluation"
            echo "• Alternative solutions comparison"
            echo "• Performance and scalability assessment"
            echo "• Cost and maintenance considerations"
            echo "• Migration path recommendations"
            ;;
    esac
else
    echo "🏗️  Full Technology Stack Analysis"
    echo ""
    echo "📋 Technology areas to analyze:"
    echo "• Frontend technologies"
    echo "• Backend frameworks"
    echo "• Database solutions"
    echo "• DevOps and infrastructure"
    echo "• Development tools"
    echo ""
    echo "💡 Usage: /tech-stack-analysis [area]"
    echo "Examples: /tech-stack-analysis frontend, /tech-stack-analysis database"
fi`

## Current Stack Detection

!`echo "📊 Current technology stack analysis:"`

### Language & Runtime Analysis
!`echo "🔍 Detected languages and runtimes:"`
!`languages_detected=0

if [ -f "package.json" ]; then
    echo "📦 JavaScript/Node.js Ecosystem"
    node_version=$(node --version 2>/dev/null || echo "not installed")
    npm_version=$(npm --version 2>/dev/null || echo "not installed") 
    echo "  Node.js: $node_version"
    echo "  npm: $npm_version"
    languages_detected=$((languages_detected + 1))
fi

if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    echo "🐍 Python Ecosystem"
    python_version=$(python3 --version 2>/dev/null || python --version 2>/dev/null || echo "not installed")
    pip_version=$(pip3 --version 2>/dev/null | cut -d' ' -f2 || echo "not available")
    echo "  Python: $python_version"
    echo "  pip: $pip_version"
    languages_detected=$((languages_detected + 1))
fi

if [ -f "Cargo.toml" ]; then
    echo "🦀 Rust Ecosystem"
    rust_version=$(rustc --version 2>/dev/null || echo "not installed")
    cargo_version=$(cargo --version 2>/dev/null || echo "not installed")
    echo "  Rust: $rust_version"
    echo "  Cargo: $cargo_version"
    languages_detected=$((languages_detected + 1))
fi

if [ -f "go.mod" ] || [ -f "go.sum" ]; then
    echo "🐹 Go Ecosystem"
    go_version=$(go version 2>/dev/null || echo "not installed")
    echo "  Go: $go_version"
    languages_detected=$((languages_detected + 1))
fi

if [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
    echo "☕ Java Ecosystem"
    java_version=$(java --version 2>/dev/null | head -1 || echo "not installed")
    echo "  Java: $java_version"
    languages_detected=$((languages_detected + 1))
fi

if [ "$languages_detected" -eq 0 ]; then
    echo "❓ No obvious language ecosystem detected"
fi`

### Framework Detection
!`echo "🏗️  Framework analysis:"`
!`if [ -f "package.json" ]; then
    echo "📦 JavaScript frameworks and libraries:"
    
    # Frontend frameworks
    if grep -q '"react"' package.json; then
        react_version=$(grep '"react"' package.json | sed 's/.*: "//; s/".*//')
        echo "  ⚛️  React: $react_version"
    fi
    
    if grep -q '"vue"' package.json; then
        vue_version=$(grep '"vue"' package.json | sed 's/.*: "//; s/".*//')
        echo "  💚 Vue.js: $vue_version"
    fi
    
    if grep -q '"@angular/core"' package.json; then
        angular_version=$(grep '"@angular/core"' package.json | sed 's/.*: "//; s/".*//')
        echo "  🅰️  Angular: $angular_version"
    fi
    
    if grep -q '"next"' package.json; then
        next_version=$(grep '"next"' package.json | sed 's/.*: "//; s/".*//')
        echo "  ▲ Next.js: $next_version"
    fi
    
    # Backend frameworks
    if grep -q '"express"' package.json; then
        express_version=$(grep '"express"' package.json | sed 's/.*: "//; s/".*//')
        echo "  🚀 Express.js: $express_version"
    fi
    
    if grep -q '"fastify"' package.json; then
        fastify_version=$(grep '"fastify"' package.json | sed 's/.*: "//; s/".*//')
        echo "  ⚡ Fastify: $fastify_version"
    fi
fi

if [ -f "requirements.txt" ]; then
    echo "🐍 Python frameworks:"
    
    if grep -q django requirements.txt; then
        echo "  🎸 Django framework"
    fi
    
    if grep -q flask requirements.txt; then
        echo "  🌶️  Flask framework"
    fi
    
    if grep -q fastapi requirements.txt; then
        echo "  ⚡ FastAPI framework"
    fi
fi`

### Database Technology
!`echo "🗄️  Database technology detection:"`
!`database_found=0

if [ -f "package.json" ]; then
    if grep -q mongodb package.json; then
        echo "🍃 MongoDB (NoSQL)"
        database_found=1
    fi
    
    if grep -q mysql package.json; then
        echo "🐬 MySQL (SQL)"
        database_found=1
    fi
    
    if grep -q postgresql package.json || grep -q '"pg"' package.json; then
        echo "🐘 PostgreSQL (SQL)"
        database_found=1
    fi
    
    if grep -q sqlite package.json; then
        echo "💎 SQLite (SQL)"
        database_found=1
    fi
    
    if grep -q redis package.json; then
        echo "⚡ Redis (Cache/Memory Store)"
        database_found=1
    fi
fi

if [ -f "requirements.txt" ]; then
    if grep -q psycopg2 requirements.txt || grep -q postgresql requirements.txt; then
        echo "🐘 PostgreSQL (SQL)"
        database_found=1
    fi
    
    if grep -q pymongo requirements.txt; then
        echo "🍃 MongoDB (NoSQL)"
        database_found=1
    fi
    
    if grep -q mysql requirements.txt; then
        echo "🐬 MySQL (SQL)"
        database_found=1
    fi
fi

if [ "$database_found" -eq 0 ]; then
    echo "💡 No database dependencies detected"
fi`

## Technology Stack Recommendations

### Frontend Technology Evaluation

#### JavaScript Frameworks Comparison
!`echo "⚛️  Frontend framework recommendations:"`
!`if [ -f "package.json" ]; then
    current_frontend=""
    
    if grep -q react package.json; then
        current_frontend="React"
    elif grep -q vue package.json; then
        current_frontend="Vue.js"
    elif grep -q "@angular/core" package.json; then
        current_frontend="Angular"
    fi
    
    if [ -n "$current_frontend" ]; then
        echo "📊 Current: $current_frontend"
        echo ""
        echo "🎯 Framework comparison:"
        echo "• React: Large ecosystem, flexible, great for complex apps"
        echo "• Vue.js: Gentle learning curve, excellent documentation"
        echo "• Angular: Full framework, great for enterprise applications"
        echo "• Svelte: Compile-time optimization, smaller bundle sizes"
    else
        echo "💡 No frontend framework detected"
        echo ""
        echo "🎯 Recommended frameworks for new projects:"
        echo "• React: Most popular, extensive ecosystem"
        echo "• Vue.js: Beginner-friendly, progressive adoption"
        echo "• Next.js: React with SSR/SSG capabilities"
        echo "• Vite + Vue/React: Fast development experience"
    fi
fi`

#### Build Tools & Development Experience
!`if [ -f "package.json" ]; then
    echo "🛠️  Build tool analysis:"
    
    if grep -q webpack package.json; then
        echo "📦 Current: Webpack"
        echo "💡 Consider: Vite for faster development builds"
    elif grep -q vite package.json; then
        echo "⚡ Current: Vite (excellent choice)"
    elif grep -q parcel package.json; then
        echo "📦 Current: Parcel"
    else
        echo "💡 Recommended: Vite for modern development"
    fi
    
    echo ""
    echo "🎯 Build tool comparison:"
    echo "• Vite: Fastest dev server, modern tooling"
    echo "• Webpack: Most mature, extensive plugin ecosystem"
    echo "• Parcel: Zero configuration, good for simple projects"
    echo "• esbuild: Extremely fast, good for production builds"
fi`

### Backend Technology Evaluation

#### Server Framework Analysis
!`echo "🔧 Backend framework recommendations:"`
!`if [ -f "package.json" ]; then
    if grep -q express package.json; then
        echo "📊 Current: Express.js"
        echo "💡 Alternatives: Fastify (faster), Koa (modern async)"
    elif grep -q fastify package.json; then
        echo "📊 Current: Fastify (excellent performance choice)"
    else
        echo "💡 Node.js framework recommendations:"
        echo "• Express.js: Most popular, extensive middleware"
        echo "• Fastify: High performance, modern architecture"
        echo "• Koa.js: Modern async/await support"
        echo "• NestJS: Enterprise-grade, TypeScript-first"
    fi
elif [ -f "requirements.txt" ]; then
    if grep -q django requirements.txt; then
        echo "📊 Current: Django"
        echo "💡 Great choice for: Full-featured web applications"
    elif grep -q flask requirements.txt; then
        echo "📊 Current: Flask"
        echo "💡 Consider: FastAPI for API-first applications"
    elif grep -q fastapi requirements.txt; then
        echo "📊 Current: FastAPI (excellent for APIs)"
    else
        echo "💡 Python framework recommendations:"
        echo "• Django: Full-featured, batteries included"
        echo "• FastAPI: Modern, fast, automatic API docs"
        echo "• Flask: Lightweight, flexible microframework"
    fi
fi`

#### Database Recommendations
!`echo "🗄️  Database technology recommendations:"`
!`echo "📊 Database selection criteria:"
echo ""
echo "🏗️  SQL Databases (ACID compliance, relations):"
echo "• PostgreSQL: Feature-rich, excellent for complex queries"
echo "• MySQL: Fast, widely supported, good for web apps"
echo "• SQLite: Lightweight, perfect for development/small apps"
echo ""
echo "🌱 NoSQL Databases (flexible schema, horizontal scaling):"
echo "• MongoDB: Document store, great for rapid development"
echo "• Redis: In-memory, perfect for caching and sessions"
echo "• CouchDB: Document store with built-in replication"
echo ""
echo "🎯 Recommendations by use case:"
echo "• Complex relationships: PostgreSQL"
echo "• High-performance reads: MySQL with Redis cache"
echo "• Flexible schemas: MongoDB"
echo "• Rapid prototyping: SQLite + upgrade path"`

### DevOps & Infrastructure

#### Deployment Options
!`echo "🚀 Deployment technology analysis:"`
!`echo "☁️  Cloud Platform Comparison:"
echo ""
echo "🌟 Platform-as-a-Service (PaaS):"
echo "• Vercel: Excellent for frontend/Next.js apps"
echo "• Netlify: Great for static sites and JAMstack"
echo "• Heroku: Easy deployment, good for prototypes"
echo "• Railway: Modern alternative to Heroku"
echo ""
echo "🏗️  Infrastructure-as-a-Service (IaaS):"
echo "• AWS: Most comprehensive, enterprise-grade"
echo "• Google Cloud: Great for ML/AI applications"
echo "• DigitalOcean: Developer-friendly, cost-effective"
echo "• Hetzner: European provider, excellent value"
echo ""
echo "🐳 Containerization:"
echo "• Docker: Standard containerization"  
echo "• Kubernetes: Container orchestration for scale"
echo "• Docker Compose: Multi-container development"`

#### CI/CD Pipeline Tools
!`echo "🔄 CI/CD recommendations:"`
!`if [ -d ".github/workflows" ]; then
    echo "✅ GitHub Actions configured"
elif [ -f ".gitlab-ci.yml" ]; then
    echo "✅ GitLab CI configured"
elif [ -f "Jenkinsfile" ]; then
    echo "✅ Jenkins pipeline configured"
else
    echo "💡 CI/CD setup needed"
fi

echo ""
echo "🎯 CI/CD platform comparison:"
echo "• GitHub Actions: Integrated with GitHub, generous free tier"
echo "• GitLab CI: Powerful features, self-hosted options"
echo "• CircleCI: Fast execution, good Docker support"
echo "• Jenkins: Self-hosted, extensive plugin ecosystem"`

## Performance & Scalability Analysis

### Current Performance Characteristics
!`echo "⚡ Performance technology assessment:"`
!`performance_score=0

# Check for caching
if find . -name "*.js" -o -name "*.ts" | xargs grep -l "cache\|redis" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Caching implementation detected"
    performance_score=$((performance_score + 1))
else
    echo "💡 No caching strategy detected"
fi

# Check for database optimization
if find . -name "*.js" -o -name "*.ts" -o -name "*.py" | xargs grep -l "index\|Index\|optimize" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Database optimization considerations"
    performance_score=$((performance_score + 1))
fi

# Check for build optimization
if [ -f "package.json" ] && grep -q '"build"' package.json; then
    echo "✅ Build process configured"
    performance_score=$((performance_score + 1))
fi

echo "📊 Performance readiness: $performance_score/3"`

### Technology Performance Comparison
!`echo "🏆 Performance-focused technology recommendations:"`
!`echo ""
echo "🚀 High-Performance Backend Options:"
echo "• Go: Compiled, fast, excellent for APIs"
echo "• Rust: Memory safe, zero-cost abstractions"
echo "• Node.js (Fastify): Fast JavaScript runtime"
echo "• C# (.NET Core): High performance, cross-platform"
echo ""
echo "⚡ Database Performance Leaders:"
echo "• Redis: In-memory, microsecond latency"
echo "• PostgreSQL: Excellent query optimization"
echo "• ClickHouse: Analytics and big data"
echo "• CockroachDB: Distributed SQL with scaling"`

## Security Technology Assessment

### Security Framework Analysis
!`echo "🔒 Security technology evaluation:"`
!`security_score=0

# Authentication
if find . -name "*.js" -o -name "*.ts" | xargs grep -l "jwt\|passport\|auth" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Authentication framework detected"
    security_score=$((security_score + 1))
else
    echo "💡 Authentication framework needed"
fi

# Input validation
if find . -name "*.js" -o -name "*.ts" | xargs grep -l "joi\|yup\|zod\|validate" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Input validation library detected"
    security_score=$((security_score + 1))
else
    echo "💡 Input validation library recommended"
fi

# HTTPS/SSL
if find . -name "*.js" -o -name "*.ts" | xargs grep -l "https\|ssl\|tls" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ HTTPS/SSL implementation"
    security_score=$((security_score + 1))
fi

echo "📊 Security implementation: $security_score/3"`

### Security Technology Recommendations
!`echo "🛡️  Security technology stack:"`
!`echo ""
echo "🔐 Authentication & Authorization:"
echo "• Auth0: Managed identity platform"
echo "• Firebase Auth: Google's authentication service"  
echo "• Passport.js: Node.js authentication middleware"
echo "• JWT: Stateless token-based authentication"
echo ""
echo "✅ Input Validation:"
echo "• Joi: Object schema validation for Node.js"
echo "• Yup: Schema validation with async support"
echo "• Zod: TypeScript-first schema validation"
echo "• express-validator: Express.js validation middleware"
echo ""
echo "🔒 Security Headers & Protection:"
echo "• Helmet.js: Security headers for Express"
echo "• CORS: Cross-origin resource sharing"
echo "• Rate limiting: express-rate-limit, fastify-rate-limit"
echo "• HTTPS enforcement: Let's Encrypt, Cloudflare"`

## Cost Analysis & Resource Optimization

### Technology Cost Comparison
!`echo "💰 Cost optimization analysis:"`
!`echo ""
echo "💸 Cost-Effective Technology Choices:"
echo ""
echo "🆓 Free Tier Friendly:"
echo "• Vercel: Generous free tier for frontend apps"
echo "• PlanetScale: Serverless MySQL with free tier"
echo "• Supabase: Open source Firebase alternative"
echo "• Railway: Modern deployment with free tier"
echo ""
echo "💡 Cost Optimization Strategies:"
echo "• Use serverless for variable workloads"
echo "• Implement proper caching to reduce compute"
echo "• Choose appropriate database size/tier"
echo "• Monitor and optimize resource usage"
echo ""
echo "📊 Total Cost of Ownership (TCO) Factors:"
echo "• Development time and team expertise"
echo "• Infrastructure and hosting costs"
echo "• Maintenance and support requirements"
echo "• Scaling costs as application grows"`

## Migration Path & Adoption Strategy

### Technology Migration Planning
!`echo "🔄 Technology adoption recommendations:"`
!`echo ""
echo "🎯 Migration Strategy:"
echo ""
echo "📈 Gradual Adoption (Recommended):"
echo "• Start with new features in new technology"
echo "• Gradually migrate critical components"
echo "• Maintain backward compatibility"
echo "• Parallel run during transition"
echo ""
echo "⚡ Quick Wins (Low Risk, High Impact):"
echo "• Add TypeScript for better development experience"
echo "• Implement caching layer (Redis)"
echo "• Upgrade to latest framework versions"
echo "• Add automated testing and CI/CD"
echo ""
echo "🚀 Long-term Goals (6-12 months):"
echo "• Consider microservices architecture"
echo "• Evaluate cloud-native technologies"
echo "• Implement comprehensive monitoring"
echo "• Optimize for performance and scale"`

## Technology Decision Matrix

### Evaluation Criteria
!`echo "📊 Technology selection framework:"`
!`echo ""
echo "🎯 Decision Criteria (weighted by importance):"
echo ""
echo "🏆 High Priority (40%):"
echo "• Team expertise and learning curve"
echo "• Performance and scalability requirements"
echo "• Community support and ecosystem"
echo "• Long-term maintenance and support"
echo ""
echo "📈 Medium Priority (35%):"
echo "• Development velocity and productivity"
echo "• Integration with existing systems"
echo "• Security and compliance requirements"
echo "• Cost of implementation and operation"
echo ""
echo "💡 Lower Priority (25%):"
echo "• Novelty and innovation factor"
echo "• Industry trends and adoption"
echo "• Vendor lock-in considerations"
echo "• Future roadmap and updates"`

## Recommendation Summary

### Technology Stack Recommendations

#### For New Projects
!`echo "🆕 New project technology recommendations:"`
!`echo ""
echo "🎨 Frontend Stack:"
echo "• Framework: Next.js (React) or Nuxt.js (Vue)"
echo "• Language: TypeScript for type safety"
echo "• Styling: Tailwind CSS for rapid development"
echo "• Build: Vite for fast development experience"
echo ""
echo "🔧 Backend Stack:"
echo "• Runtime: Node.js with TypeScript"
echo "• Framework: Fastify or Express.js"
echo "• Database: PostgreSQL with Prisma ORM"
echo "• Cache: Redis for session and API caching"
echo ""
echo "🚀 DevOps Stack:"
echo "• Deployment: Vercel (frontend) + Railway (backend)"
echo "• CI/CD: GitHub Actions"
echo "• Monitoring: Sentry for error tracking"
echo "• Analytics: Plausible or Google Analytics"`

#### For Existing Projects
!`echo "🔄 Existing project upgrade recommendations:"`
!`echo ""
echo "📈 Immediate Improvements (1-4 weeks):"
echo "• Add TypeScript gradually"
echo "• Implement proper error handling"
echo "• Add input validation"
echo "• Set up basic monitoring"
echo ""
echo "🎯 Medium-term Goals (1-3 months):"
echo "• Add comprehensive testing"
echo "• Implement caching strategy"
echo "• Optimize database queries"
echo "• Set up proper CI/CD pipeline"
echo ""
echo "🚀 Long-term Vision (3-12 months):"
echo "• Consider architectural refactoring"
echo "• Evaluate cloud migration"
echo "• Implement advanced monitoring"
echo "• Plan for horizontal scaling"`

## Next Steps

1. **Technology Audit**: Review current stack against recommendations
2. **Create Migration Plan**: Prioritize technology upgrades and migrations  
3. **Performance Testing**: Benchmark current and proposed technologies
4. **Team Training**: Plan learning and development for new technologies
5. **Pilot Implementation**: Start with low-risk proof of concept

## Integration with Other Commands

- Use `/architecture-review` to analyze current system architecture
- Use `/design-system` for designing new components with recommended technologies
- Use `/performance-review` to validate technology performance claims
- Use `/security-scan` to assess security implications of technology choices

Choose technologies that align with your team's expertise and project requirements rather than just following trends.