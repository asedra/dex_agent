---
description: "Deploy to specified environment"
shortcut: "dep"
arguments: true
---

# Deploy

Deploy the application to specified environment with pre-deployment checks.

## Usage

```bash
/deploy                      # Interactive deployment
/deploy staging             # Deploy to staging environment
/deploy production          # Deploy to production environment  
/deploy development         # Deploy to development environment
```

## Pre-deployment Checks

!`echo "🔍 Pre-deployment validation..."`

### Git Status
!`echo "📂 Git repository status:"`
!`if git status --porcelain | grep -q .; then
    echo "⚠️  Uncommitted changes detected:"
    git status --porcelain | head -3
    echo "💡 Consider committing changes before deployment"
else
    echo "✅ Working directory clean"
fi`

### Current Branch
!`echo "🌿 Current branch: $(git branch --show-current)"`
!`if [ "$(git branch --show-current)" != "main" ] && [ "$(git branch --show-current)" != "master" ]; then
    echo "⚠️  Not on main/master branch"
    echo "💡 Consider merging to main before production deployment"
fi`

### Test Status  
!`echo "🧪 Test verification:"`
!`if [ -f "package.json" ]; then
    if npm test --silent >/dev/null 2>&1; then
        echo "✅ All tests passing"
    else
        echo "❌ Tests failing - fix before deployment"
    fi
else
    echo "⚠️  No test configuration detected"
fi`

## Environment Deployment

Target environment: **$ARGUMENTS**

!`if [ -n "$ARGUMENTS" ]; then
    environment="$ARGUMENTS"
    echo "🎯 Deploying to: $environment"
    
    case "$environment" in
        "development"|"dev")
            echo "🧪 Development Environment Deployment"
            echo "• Purpose: Testing and development"
            echo "• Risk Level: Low"
            echo "• Rollback: Easy"
            echo ""
            echo "🚀 Deployment steps:"
            echo "1. Build application"
            echo "2. Run development-specific configurations"  
            echo "3. Deploy to dev server"
            echo "4. Run smoke tests"
            ;;
        "staging"|"stage")
            echo "🎭 Staging Environment Deployment"
            echo "• Purpose: Pre-production testing"
            echo "• Risk Level: Medium"
            echo "• Rollback: Moderate"
            echo ""
            echo "🚀 Deployment steps:"
            echo "1. Build production-like version"
            echo "2. Deploy to staging server"
            echo "3. Run integration tests"
            echo "4. Performance validation"
            ;;
        "production"|"prod")
            echo "🏭 Production Environment Deployment"
            echo "• Purpose: Live user environment"
            echo "• Risk Level: High"
            echo "• Rollback: Critical process"
            echo ""
            echo "⚠️  PRODUCTION DEPLOYMENT CHECKLIST:"
            echo "✓ All tests passing"
            echo "✓ Code review completed"
            echo "✓ Staging deployment successful"
            echo "✓ Database migrations tested"
            echo "✓ Rollback plan ready"
            echo ""
            echo "🚀 Production deployment requires additional confirmation"
            ;;
        *)
            echo "❌ Unknown environment: $environment"
            echo "💡 Available environments:"
            echo "   development  - Dev testing environment"
            echo "   staging      - Pre-production environment"  
            echo "   production   - Live production environment"
            ;;
    esac
else
    echo "🛠️  Interactive deployment selection:"
    echo ""
    echo "Available environments:"
    echo "🧪 development  - Development and testing"
    echo "🎭 staging      - Pre-production validation"
    echo "🏭 production   - Live production environment"
    echo ""
    echo "💡 Usage: /deploy [environment]"
    echo "Example: /deploy staging"
fi`

## Deployment Configuration

!`echo "⚙️  Deployment configuration:"`
!`if [ -f "Dockerfile" ]; then
    echo "🐳 Docker deployment detected"
elif [ -f "vercel.json" ]; then
    echo "▲ Vercel deployment detected"
elif [ -f "netlify.toml" ]; then
    echo "🌐 Netlify deployment detected"
elif [ -f ".github/workflows" ]; then
    echo "⚡ GitHub Actions CI/CD detected"
else
    echo "💡 No deployment configuration detected"
fi`

## Environment Variables

!`echo "🔒 Environment variables check:"`
!`if [ -f ".env.example" ]; then
    echo "✅ Environment template found (.env.example)"
elif [ -f ".env" ]; then
    echo "⚠️  .env file present (ensure secrets are configured per environment)"
else
    echo "💡 No environment configuration detected"
fi`

## Deployment Best Practices

### Before Deployment
1. **Run tests**: Ensure all tests pass
2. **Code review**: Get peer review approval
3. **Staging test**: Deploy to staging first
4. **Database migrations**: Test schema changes

### During Deployment
1. **Monitor logs**: Watch for errors during deployment
2. **Health checks**: Verify application starts correctly
3. **Smoke tests**: Test critical functionality
4. **Performance**: Monitor response times

### After Deployment
1. **Verification**: Confirm deployment success
2. **Monitoring**: Watch metrics and alerts
3. **Rollback plan**: Be ready to revert if needed
4. **Documentation**: Update deployment notes

## Emergency Procedures

### Rollback Process
- **Development**: Redeploy previous version
- **Staging**: Reset to last known good state
- **Production**: Execute rollback plan immediately

### Monitoring
- Application logs and error rates
- Performance metrics and response times
- User feedback and support tickets