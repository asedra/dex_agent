---
description: "Security vulnerability assessment"
shortcut: "ss"
---

# Security Scan

Comprehensive security vulnerability assessment and recommendations.

## Dependency Security

### npm Security Audit
!`if [ -f "package.json" ]; then
    echo "🔒 npm security audit:"
    npm audit --audit-level moderate 2>/dev/null || echo "  ✅ No security vulnerabilities found"
    echo ""
    echo "📊 Audit summary:"
    npm audit --json 2>/dev/null | jq -r '.metadata | "High: \(.vulnerabilities.high // 0), Moderate: \(.vulnerabilities.moderate // 0), Low: \(.vulnerabilities.low // 0)"' 2>/dev/null || echo "  Audit data not available"
else
    echo "💡 No package.json found - skipping npm audit"
fi`

### Outdated Dependencies
!`if [ -f "package.json" ]; then
    echo "📦 Outdated packages check:"
    npm outdated --depth=0 2>/dev/null | head -5 || echo "  All packages up to date"
fi`

## Environment Security

### Environment Variables
!`echo "🔐 Environment security check:"`
!`if [ -f ".env" ]; then
    echo "⚠️  .env file detected - ensure it's in .gitignore"
    if grep -q ".env" .gitignore 2>/dev/null; then
        echo "✅ .env is gitignored"
    else
        echo "❌ .env is NOT in .gitignore - SECURITY RISK!"
    fi
    
    echo "🔍 Checking for potential secrets in .env:"
    grep -E "(password|secret|key|token)" .env 2>/dev/null | sed 's/=.*/=***' | head -3 || echo "  No obvious secrets found"
else
    echo "💡 No .env file found"
fi`

### Git Security
!`echo "📝 Git security check:"`
!`if git log --all --grep="password\|secret\|key\|token" --oneline | head -3 | grep -q .; then
    echo "⚠️  Potential secrets in commit messages:"
    git log --all --grep="password\|secret\|key\|token" --oneline | head -3
else
    echo "✅ No obvious secrets in commit messages"
fi`

## Code Security Analysis

### Hardcoded Secrets
!`echo "🔍 Scanning for hardcoded secrets:"`
!`find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" -o -name "*.py" | head -10 | xargs grep -l "password\|secret\|key\|token" 2>/dev/null | while read file; do
    echo "⚠️  Potential secrets in: $file"
    grep -n "password\|secret\|key\|token" "$file" | head -2 | sed 's/:.*/: ***redacted***/'
done`

### Dangerous Functions
!`echo "⚡ Checking for dangerous functions:"`
!`dangerous_patterns="eval\|innerHTML\|document.write\|exec\|shell_exec"
find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | head -10 | xargs grep -l "$dangerous_patterns" 2>/dev/null | while read file; do
    echo "⚠️  Dangerous patterns in: $file"
    grep -n "$dangerous_patterns" "$file" | head -2
done || echo "✅ No dangerous functions detected"`

## File Permission Security

### Sensitive Files
!`echo "📁 File permissions check:"`
!`for file in .env .env.local .env.production id_rsa id_dsa ~/.ssh/id_rsa; do
    if [ -f "$file" ]; then
        perms=$(ls -l "$file" | cut -d' ' -f1)
        echo "🔒 $file: $perms"
        if [ "$file" = ".env" ] || [ "$file" = ".env.local" ] || [ "$file" = ".env.production" ]; then
            if echo "$perms" | grep -q "r..r..r.."; then
                echo "❌ $file is world-readable - SECURITY RISK!"
            fi
        fi
    fi
done`

### Executable Files
!`echo "⚡ Executable files check:"`
!`find . -type f -executable -name "*.sh" -o -name "*.py" -o -name "*.js" | head -5 | while read file; do
    echo "🔧 Executable: $file"
done`

## Network Security

### Port Usage
!`echo "🌐 Network security check:"`
!`if command -v netstat >/dev/null 2>&1; then
    echo "📡 Open ports:"
    netstat -tulpn 2>/dev/null | grep LISTEN | head -5 || echo "  No listening ports detected"
else
    echo "💡 netstat not available"
fi`

### HTTPS Configuration
!`if find . -name "*.js" -o -name "*.ts" | xargs grep -l "http://" 2>/dev/null | head -3 | grep -q .; then
    echo "⚠️  HTTP URLs found (consider HTTPS):"
    find . -name "*.js" -o -name "*.ts" | xargs grep -n "http://" 2>/dev/null | head -3
else
    echo "✅ No HTTP URLs detected"
fi`

## Framework-Specific Security

### React Security
!`if grep -q react package.json 2>/dev/null; then
    echo "⚛️  React security check:"
    
    # Check for dangerouslySetInnerHTML
    if find . -name "*.jsx" -o -name "*.tsx" | xargs grep -l "dangerouslySetInnerHTML" 2>/dev/null | head -1 | grep -q .; then
        echo "⚠️  dangerouslySetInnerHTML usage detected"
        find . -name "*.jsx" -o -name "*.tsx" | xargs grep -n "dangerouslySetInnerHTML" 2>/dev/null | head -2
    else
        echo "✅ No dangerouslySetInnerHTML usage"
    fi
fi`

### Node.js Security
!`if [ -f "package.json" ]; then
    echo "🟢 Node.js security check:"
    
    # Check for process.env usage
    if find . -name "*.js" -o -name "*.ts" | xargs grep -l "process.env" 2>/dev/null | head -1 | grep -q .; then
        echo "💡 process.env usage detected - ensure proper validation"
    fi
    
    # Check for require() with variables
    if find . -name "*.js" -o -name "*.ts" | xargs grep "require(" 2>/dev/null | grep -v require.*[\'\"]\\./ | head -1 | grep -q .; then
        echo "⚠️  Dynamic require() usage - potential security risk"
    fi
fi`

## Database Security

### SQL Injection Prevention
!`echo "🗄️  Database security check:"`
!`if find . -name "*.js" -o -name "*.ts" -o -name "*.py" | xargs grep -l "SELECT\|INSERT\|UPDATE\|DELETE" 2>/dev/null | head -3 | grep -q .; then
    echo "⚠️  SQL queries detected - ensure parameterized queries:"
    find . -name "*.js" -o -name "*.ts" -o -name "*.py" | xargs grep -n "SELECT\|INSERT\|UPDATE\|DELETE" 2>/dev/null | head -3
else
    echo "💡 No direct SQL queries detected"
fi`

## Security Headers

### HTTP Security Headers
!`echo "🛡️  Security headers check:"`
!`if find . -name "*.js" -o -name "*.ts" | xargs grep -l "Content-Security-Policy\|X-Frame-Options\|X-XSS-Protection" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Security headers implementation found"
else
    echo "⚠️  No security headers detected - consider implementing:"
    echo "   • Content-Security-Policy"
    echo "   • X-Frame-Options" 
    echo "   • X-XSS-Protection"
    echo "   • Strict-Transport-Security"
fi`

## Security Recommendations

### High Priority (Critical)
1. **Fix Dependency Vulnerabilities**: Update packages with security issues
2. **Remove Hardcoded Secrets**: Use environment variables and secret management
3. **Secure File Permissions**: Restrict access to sensitive files
4. **Enable HTTPS**: Use HTTPS for all communications

### Medium Priority (Important)
1. **Input Validation**: Validate all user inputs
2. **Security Headers**: Implement security headers
3. **Error Handling**: Don't expose sensitive information in errors
4. **Access Control**: Implement proper authentication and authorization

### Low Priority (Recommended)
1. **Security Monitoring**: Add security logging and monitoring
2. **Regular Audits**: Schedule regular security audits
3. **Dependency Updates**: Keep dependencies updated
4. **Security Training**: Ensure team is security-aware

## Security Checklist

### Authentication & Authorization
- [ ] Strong password policies implemented
- [ ] Multi-factor authentication enabled
- [ ] Proper session management
- [ ] Role-based access control

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] Secure data transmission (HTTPS/TLS)
- [ ] Proper data sanitization
- [ ] Secure backup procedures

### Input Validation
- [ ] All inputs validated and sanitized
- [ ] SQL injection protection
- [ ] XSS prevention measures
- [ ] CSRF protection implemented

### Infrastructure Security
- [ ] Regular security updates
- [ ] Firewall configuration
- [ ] Intrusion detection systems
- [ ] Security monitoring and logging

## Next Steps

1. **Address Critical Issues**: Fix high-priority security vulnerabilities immediately
2. **Update Dependencies**: Run `npm audit fix` to auto-fix issues
3. **Review Code**: Manual review of flagged security concerns
4. **Implement Security Headers**: Add security headers to web applications
5. **Regular Monitoring**: Set up continuous security monitoring

Use `/check-standards` for code quality and `/performance-review` for performance security aspects.