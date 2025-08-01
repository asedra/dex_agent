# Claude Commands

This file contains all available Claude commands for the DexAgents project.

## 🚀 Primary Commands

### `/tasks_start`
**Description**: Start task planning process  
**Action**: Enters planning mode with ultrathink, analyzes stories/bugs/tasks and creates implementation plan  
**Usage**: Simply type `/tasks_start`  
**When to Use**: 
- Beginning a new development cycle
- When you have stories that need to be broken down into tasks
- Planning implementation of new features

### `test raporunu oku`
**Description**: Read and fix test report  
**Action**: Reads test results from `backend_test_results.md` and `frontend_test_results.md`, analyzes findings, implements fixes  
**Usage**: Type `test raporunu oku`  
**When to Use**: 
- After manual test execution is complete
- When test results files have been updated with findings
- To analyze and fix reported test failures

### `projeyi başlat`
**Description**: Start the project  
**Action**: Runs `docker-compose up -d --build` to start all services  
**Usage**: Type `projeyi başlat`  
**When to Use**: 
- Starting development session
- After system restart
- When all Docker services need to be launched

### `testleri çalıştır`
**Description**: Run comprehensive tests  
**Action**: User will manually run tests and document results in test result files  
**Usage**: Type `testleri çalıştır`  
**When to Use**: 
- After completing development work
- Before committing changes
- For quality assurance validation

## 📋 Workflow Commands

These commands are part of the standard development workflow:

### Planning Phase
1. **`/tasks_start`** - Analyze requirements and create implementation plan
2. Review generated tasks in `story.md`, `bug.md`, `task.md`

### Development Phase  
1. **`projeyi başlat`** - Start Docker services
2. Implement features based on tasks
3. Follow test preservation rules

### Testing Phase
1. **`testleri çalıştır`** - Manual test execution by user
2. **`test raporunu oku`** - Analyze results and fix issues

### Completion Phase
1. Archive completed items to archive files
2. Request approval for commits
3. Request approval for Docker shutdown

## 🔧 Command Guidelines

### Command Usage Rules
- Commands are case-sensitive
- Turkish commands should be typed exactly as shown
- Commands with `/` prefix are special planning commands
- Commands without `/` are workflow commands

### Response Expectations
- **Planning Commands**: Will enter planning mode, no code changes
- **Workflow Commands**: Will execute specific actions
- **Analysis Commands**: Will read files and provide analysis

### Approval Requirements
Commands that require user approval:
- Any commit operations (after development)
- Docker service shutdown (`docker-compose down`)
- Test modifications (changes to existing tests)

## 📝 Command Reference

| Command | Type | Approval Required | Output |
|---------|------|------------------|--------|
| `/tasks_start` | Planning | No | Task analysis and planning |
| `test raporunu oku` | Analysis | No | Test result analysis and fixes |
| `projeyi başlat` | Action | No | Docker services started |
| `testleri çalıştır` | Instruction | No | Manual test guidance |

## 🚨 Important Notes

1. **Planning Mode**: `/tasks_start` enters planning mode - no code changes during planning
2. **Manual Testing**: Tests are executed manually by user, not automatically by Claude
3. **Test Preservation**: Existing tests are never deleted, modifications require approval
4. **Approval Gates**: Commits and Docker shutdown require explicit user approval
5. **File Integration**: Commands work with project management files (story.md, bug.md, etc.)

## 💡 Command Tips

- Use `/tasks_start` at the beginning of each development cycle
- Run `projeyi başlat` before any development work
- Use `test raporunu oku` only after test results files are populated
- Commands can be run in sequence for complete workflow automation

## 🔄 Typical Command Flow

```
1. /tasks_start                    # Plan the work
2. projeyi başlat                 # Start services  
3. [Development work happens]      # Implement features
4. testleri çalıştır             # Manual testing
5. test raporunu oku              # Fix any issues
6. [Request commit approval]       # Get approval to commit
```

## 📚 Related Documentation

- **CLAUDE.md**: Full project documentation and guidelines
- **story.md/bug.md/task.md**: Project management files
- **backend_test_results.md/frontend_test_results.md**: Test result files
- **test_history.md**: Test modification tracking