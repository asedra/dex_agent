---
description: "Pull request analysis and recommendations"
shortcut: "apr"
arguments: true
---

# Analyze Pull Request

Comprehensive pull request analysis with code quality metrics and recommendations.

## Usage

```bash
/analyze-pr                  # Analyze current branch changes
/analyze-pr #123            # Analyze specific PR number
/analyze-pr branch-name     # Analyze specific branch
```

## Current Changes Analysis

!`echo "📊 Analyzing current repository changes..."`

### Git Diff Summary
!`echo "📝 Changes in working directory:"`
!`git diff --stat 2>/dev/null | head -10 || echo "  No changes detected"`

### Modified Files
!`echo "📁 Modified files:"`
!`git diff --name-only HEAD~1 2>/dev/null | head -5 || echo "  No recent changes"`

### Code Statistics
!`echo "📈 Code changes:"`
!`git diff --numstat HEAD~1 2>/dev/null | awk '{added+=$1; deleted+=$2} END {print "  +" added " lines added, -" deleted " lines deleted"}' || echo "  No changes to analyze"`

## Pull Request Analysis

Target: **$ARGUMENTS**

!`if [ -n "$ARGUMENTS" ]; then
    target="$ARGUMENTS"
    echo "🎯 Analyzing: $target"
    
    if echo "$target" | grep -q "^#[0-9]"; then
        pr_number=$(echo "$target" | sed 's/#//')
        echo "🔍 Pull Request #$pr_number Analysis"
        echo "💡 Integration with GitHub API would show:"
        echo "   • PR title and description"
        echo "   • Changed files and diff stats"
        echo "   • Review status and comments"
        echo "   • CI/CD build status"
    elif git rev-parse --verify "$target" >/dev/null 2>&1; then
        echo "🌿 Branch Analysis: $target"
        echo "📊 Comparing $target with main/master:"
        main_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@refs/remotes/origin/@@' || echo "main")
        git diff --stat "$main_branch..$target" 2>/dev/null || echo "  Cannot compare branches"
    else
        echo "❌ Target not found: $target"
        echo "💡 Use: #PR-number, branch-name, or omit for current changes"
    fi
else
    echo "🔄 Analyzing current branch changes..."
    current_branch=$(git branch --show-current)
    echo "📍 Current branch: $current_branch"
    
    if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
        main_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@refs/remotes/origin/@@' || echo "main")
        echo "🔍 Changes since $main_branch:"
        git diff --stat "$main_branch" 2>/dev/null || echo "  Cannot determine changes"
    else
        echo "⚠️  On main branch - analyzing recent commits"
        git log --oneline -5 || echo "  No commit history"
    fi
fi`

## Code Quality Analysis

### File Type Analysis
!`echo "📄 File types in changes:"`
!`git diff --name-only HEAD~1 2>/dev/null | sed 's/.*\.//' | sort | uniq -c | sort -nr | head -5 || echo "  No files to analyze"`

### Complexity Indicators
!`echo "🔬 Complexity analysis:"`
!`changed_files=$(git diff --name-only HEAD~1 2>/dev/null)
if [ -n "$changed_files" ]; then
    for file in $changed_files; do
        if [ -f "$file" ]; then
            lines=$(wc -l < "$file" 2>/dev/null || echo "0")
            echo "  $file: $lines lines"
        fi
    done | head -5
else
    echo "  No files to analyze"
fi`

## Review Checklist

### Code Quality
- [ ] **Code Style**: Follows project conventions
- [ ] **Naming**: Clear and descriptive variable/function names
- [ ] **Documentation**: Adequate comments and docs
- [ ] **Complexity**: Functions are reasonably sized
- [ ] **DRY Principle**: No unnecessary code duplication

### Functionality
- [ ] **Requirements**: Meets acceptance criteria
- [ ] **Edge Cases**: Handles error conditions
- [ ] **Performance**: No obvious performance issues
- [ ] **Security**: No security vulnerabilities
- [ ] **Backwards Compatibility**: Doesn't break existing features

### Testing
- [ ] **Test Coverage**: New code is adequately tested
- [ ] **Test Quality**: Tests are meaningful and maintainable
- [ ] **Integration**: Integration tests updated if needed
- [ ] **Manual Testing**: Manual verification completed

### Documentation
- [ ] **README**: Updated if user-facing changes
- [ ] **API Docs**: API documentation updated
- [ ] **Comments**: Complex logic is commented
- [ ] **Changelog**: Notable changes documented

## Automated Checks

!`echo "🤖 Automated analysis:"`

### Linting
!`if [ -f "package.json" ] && grep -q eslint package.json; then
    echo "🔍 ESLint check:"
    npm run lint --silent 2>/dev/null || echo "  ❌ Linting issues found"
elif [ -f ".eslintrc" ] || [ -f ".eslintrc.json" ]; then
    echo "🔍 ESLint configured but not run"
else
    echo "💡 No linting configuration detected"
fi`

### Type Checking
!`if [ -f "tsconfig.json" ]; then
    echo "📘 TypeScript check:"
    npx tsc --noEmit 2>/dev/null && echo "  ✅ Type check passed" || echo "  ❌ Type errors found"
elif grep -q typescript package.json 2>/dev/null; then
    echo "📘 TypeScript project but no type checking"
else
    echo "💡 No TypeScript configuration"
fi`

## Recommendations

### High Priority
1. **Security Review**: Check for potential security vulnerabilities
2. **Performance Impact**: Analyze performance implications
3. **Breaking Changes**: Identify any breaking changes

### Medium Priority  
1. **Code Style**: Ensure consistent formatting
2. **Documentation**: Update relevant documentation
3. **Test Coverage**: Verify adequate test coverage

### Low Priority
1. **Refactoring Opportunities**: Identify code improvement opportunities
2. **Dependencies**: Check for unnecessary dependencies
3. **Optimization**: Look for optimization opportunities

## Next Steps

1. **Run Tests**: Use `/run-tests` to verify functionality
2. **Security Check**: Use `/security-scan` for vulnerability assessment
3. **Standards Check**: Use `/check-standards` for coding standards
4. **Performance Review**: Use `/performance-review` for optimization analysis