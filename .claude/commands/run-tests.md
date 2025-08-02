---
description: "Execute test suite with various options"
shortcut: "rt"
arguments: true
---

# Run Tests

Execute the project test suite with various options and configurations.

## Usage

```bash
/run-tests                    # Run all tests
/run-tests unit              # Run unit tests only
/run-tests integration       # Run integration tests  
/run-tests [specific-file]   # Run specific test file
```

## Test Discovery

!`echo "🔍 Detecting test configuration..."`

!`if [ -f "package.json" ]; then
    echo "📦 Node.js project detected"
    if grep -q '"test"' package.json; then
        echo "✅ Test script found in package.json"
        grep '"test"' package.json | head -1
    else
        echo "❌ No test script in package.json"
    fi
elif [ -f "Cargo.toml" ]; then
    echo "🦀 Rust project detected"
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    echo "🐍 Python project detected"
elif [ -f "go.mod" ]; then
    echo "🐹 Go project detected"
else
    echo "❓ Unknown project type"
fi`

## Test Execution

Test target: **$ARGUMENTS**

!`if [ -n "$ARGUMENTS" ]; then
    test_target="$ARGUMENTS"
    echo "🎯 Running tests for: $test_target"
    
    case "$test_target" in
        "unit")
            echo "🧪 Executing unit tests..."
            if [ -f "package.json" ]; then
                npm run test:unit 2>/dev/null || npm test -- --testPathPattern=unit 2>/dev/null || echo "❌ Unit tests not configured"
            else
                echo "💡 Unit test execution varies by project type"
            fi
            ;;
        "integration")
            echo "🔗 Executing integration tests..."
            if [ -f "package.json" ]; then
                npm run test:integration 2>/dev/null || npm test -- --testPathPattern=integration 2>/dev/null || echo "❌ Integration tests not configured"
            else
                echo "💡 Integration test execution varies by project type"
            fi
            ;;
        *)
            echo "🏃 Running: $test_target"
            if [ -f "package.json" ]; then
                npm test "$test_target" 2>/dev/null || echo "❌ Test not found: $test_target"
            else
                echo "💡 Test execution varies by project type"
            fi
            ;;
    esac
else
    echo "🚀 Running all tests..."
    if [ -f "package.json" ]; then
        npm test || echo "❌ Tests failed or not configured"
    elif [ -f "Cargo.toml" ]; then
        cargo test || echo "❌ Tests failed"
    elif [ -f "go.mod" ]; then
        go test ./... || echo "❌ Tests failed"
    else
        echo "💡 Please specify test command for your project type"
        echo "Usage: /run-tests [unit|integration|specific-test]"
    fi
fi`

## Test Categories

### Unit Tests
- **Purpose**: Test individual functions and components in isolation
- **Speed**: Fast execution, typically < 1 second per test
- **Scope**: Single functions, classes, or small modules

### Integration Tests  
- **Purpose**: Test interactions between components
- **Speed**: Moderate execution, may involve databases or APIs
- **Scope**: Multiple components working together

### End-to-End Tests
- **Purpose**: Test complete user workflows
- **Speed**: Slower execution, full application testing
- **Scope**: Entire application from user perspective

## Test Configuration

!`echo "⚙️  Test configuration files:"`
!`ls -la | grep -E "(jest|mocha|pytest|cargo)" | head -5 || echo "  No common test configs found"`

!`if [ -f "jest.config.js" ] || [ -f "jest.config.json" ]; then
    echo "✅ Jest configuration found"
elif [ -f ".mocharc.json" ] || [ -f "mocha.opts" ]; then
    echo "✅ Mocha configuration found"  
elif [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
    echo "✅ Pytest configuration found"
else
    echo "💡 No test configuration detected"
fi`

## Best Practices

1. **Run tests before commits**: Ensure code quality
2. **Use specific test targets**: Faster feedback during development
3. **Check test coverage**: Maintain adequate test coverage
4. **Fix failing tests immediately**: Don't accumulate technical debt

## Next Steps

After running tests:
- ✅ All tests pass → Ready for commit/deploy
- ❌ Tests fail → Fix issues before proceeding
- 📊 Check coverage → Add tests for uncovered code