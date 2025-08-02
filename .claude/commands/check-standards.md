---
description: "Code standards compliance verification"
shortcut: "cs"
---

# Check Standards

Verify code compliance with project standards and best practices.

## Code Style Analysis

!`echo "🎨 Code style verification..."`

### Linting Status
!`if [ -f ".eslintrc.json" ] || [ -f ".eslintrc.js" ] || [ -f "eslint.config.js" ]; then
    echo "✅ ESLint configuration found"
    if command -v eslint >/dev/null 2>&1; then
        echo "🔍 Running ESLint..."
        eslint . --ext .js,.ts,.jsx,.tsx 2>/dev/null | head -10 || echo "  ESLint check completed"
    else
        echo "💡 ESLint not installed"
    fi
elif grep -q eslint package.json 2>/dev/null; then
    echo "⚠️  ESLint in package.json but no config file"
else
    echo "❌ No ESLint configuration detected"
fi`

### Prettier Formatting
!`if [ -f ".prettierrc" ] || [ -f "prettier.config.js" ]; then
    echo "✅ Prettier configuration found"
    if command -v prettier >/dev/null 2>&1; then
        echo "🎨 Checking formatting..."
        prettier --check . 2>/dev/null | head -5 || echo "  Formatting check completed"
    else
        echo "💡 Prettier not installed"
    fi
else
    echo "💡 No Prettier configuration detected"
fi`

## Language-Specific Standards

### JavaScript/TypeScript
!`if [ -f "tsconfig.json" ]; then
    echo "📘 TypeScript Standards Check"
    echo "✅ TypeScript configuration found"
    
    # Check strict mode
    if grep -q '"strict": true' tsconfig.json; then
        echo "✅ Strict mode enabled"
    else
        echo "⚠️  Strict mode not enabled"
    fi
    
    # Check for type checking
    npx tsc --noEmit 2>/dev/null && echo "✅ No type errors" || echo "❌ Type errors found"
elif find . -name "*.js" -o -name "*.jsx" | head -1 | grep -q .; then
    echo "📜 JavaScript Standards Check"
    echo "💡 Consider adding TypeScript for better type safety"
fi`

### Python Standards
!`if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || find . -name "*.py" | head -1 | grep -q .; then
    echo "🐍 Python Standards Check"
    
    if command -v black >/dev/null 2>&1; then
        echo "🎨 Black formatter check:"
        black --check . 2>/dev/null | head -5 || echo "  Formatting check completed"
    fi
    
    if command -v flake8 >/dev/null 2>&1; then
        echo "🔍 Flake8 linting:"
        flake8 . 2>/dev/null | head -5 || echo "  Linting completed"
    fi
    
    if command -v mypy >/dev/null 2>&1; then
        echo "📝 MyPy type checking:"
        mypy . 2>/dev/null | head -5 || echo "  Type checking completed"
    fi
fi`

## File Structure Standards

### Directory Organization
!`echo "📁 Directory structure analysis:"`
!`find . -maxdepth 2 -type d -name ".*" -prune -o -type d -print | grep -v node_modules | head -10`

### Naming Conventions
!`echo "📝 File naming conventions:"`
!`find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | head -10 | while read file; do
    basename_file=$(basename "$file")
    if echo "$basename_file" | grep -q "^[a-z][a-zA-Z0-9]*\\."; then
        echo "  ✅ $basename_file (camelCase)"
    elif echo "$basename_file" | grep -q "^[a-z][a-z0-9-]*\\."; then
        echo "  ✅ $basename_file (kebab-case)"
    elif echo "$basename_file" | grep -q "^[A-Z][a-zA-Z0-9]*\\."; then
        echo "  ✅ $basename_file (PascalCase)"
    else
        echo "  ⚠️  $basename_file (non-standard naming)"
    fi
done`

## Documentation Standards

### README Documentation
!`if [ -f "README.md" ]; then
    echo "✅ README.md found"
    readme_lines=$(wc -l < README.md)
    if [ "$readme_lines" -gt 50 ]; then
        echo "✅ Comprehensive README ($readme_lines lines)"
    else
        echo "⚠️  README could be more detailed ($readme_lines lines)"
    fi
else
    echo "❌ README.md missing"
fi`

### Code Comments
!`echo "💬 Code documentation analysis:"`
!`comment_ratio=$(find . -name "*.js" -o -name "*.ts" -o -name "*.py" | head -5 | xargs grep -l "//" 2>/dev/null | wc -l)
total_files=$(find . -name "*.js" -o -name "*.ts" -o -name "*.py" | head -5 | wc -l)
if [ "$total_files" -gt 0 ]; then
    echo "📊 Files with comments: $comment_ratio/$total_files"
else
    echo "💡 No source files to analyze"
fi`

## Dependency Standards

### Package Management
!`if [ -f "package-lock.json" ]; then
    echo "✅ npm lock file found"
elif [ -f "yarn.lock" ]; then
    echo "✅ Yarn lock file found"
elif [ -f "pnpm-lock.yaml" ]; then
    echo "✅ pnpm lock file found"
else
    echo "⚠️  No lock file found"
fi`

### Security Dependencies
!`if [ -f "package.json" ]; then
    echo "🔒 Security audit:"
    npm audit --audit-level moderate 2>/dev/null | head -5 || echo "  No security issues found"
fi`

## Git Standards

### Commit History
!`echo "📝 Git commit standards:"`
!`git log --oneline -5 | while read commit; do
    if echo "$commit" | grep -E "^[a-f0-9]+ (feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+" >/dev/null; then
        echo "  ✅ $(echo "$commit" | cut -c1-60)..."
    else
        echo "  ⚠️  $(echo "$commit" | cut -c1-60)... (non-conventional)"
    fi
done`

### Branch Naming
!`current_branch=$(git branch --show-current)
if echo "$current_branch" | grep -E "^(feature|bugfix|hotfix|chore|docs)/" >/dev/null; then
    echo "✅ Branch follows naming convention: $current_branch"
else
    echo "⚠️  Branch name non-standard: $current_branch"
fi`

## Standards Compliance Report

### Critical Issues (Must Fix)
- Security vulnerabilities in dependencies
- Type errors in TypeScript
- Linting errors that break build
- Missing essential documentation (README)

### Important Issues (Should Fix)
- Inconsistent code formatting
- Non-standard naming conventions
- Missing unit tests for new code
- Outdated or inadequate documentation

### Suggestions (Nice to Have)
- Improve code comments
- Optimize imports and dependencies
- Enhance error handling
- Add performance monitoring

## Recommended Actions

1. **Fix Critical Issues**: Address all critical compliance issues
2. **Update Configuration**: Ensure all tools are properly configured
3. **Run Automated Fixes**: Use `prettier --write .` and `eslint --fix .`
4. **Update Documentation**: Ensure README and comments are current
5. **Review Dependencies**: Update outdated packages and remove unused ones

## Next Steps

- Use `/security-scan` for detailed security analysis
- Use `/performance-review` for performance optimization
- Use `/analyze-pr` for comprehensive code review
- Configure pre-commit hooks to maintain standards automatically