---
description: "Create new git branch with naming conventions"
shortcut: "cb"
arguments: true
---

# Create Branch

Create a new git branch following project naming conventions and best practices.

## Usage

```bash
/create-branch feature/new-feature    # Create feature branch
/create-branch bugfix/fix-issue       # Create bugfix branch  
/create-branch hotfix/urgent-fix      # Create hotfix branch
/create-branch                        # Interactive branch creation
```

## Current Git Status

!`echo "📂 Current repository status:"`
!`git status --porcelain | head -5 || echo "  No changes detected"`

!`echo "🌿 Current branch:"`
!`git branch --show-current || echo "  Not in a git repository"`

!`echo "🔀 Recent branches:"`
!`git branch --sort=-committerdate | head -5 || echo "  No branches found"`

## Branch Creation

Branch name provided: **$ARGUMENTS**

!`if [ -n "$ARGUMENTS" ]; then
    branch_name="$ARGUMENTS"
    
    # Validate branch name format
    if echo "$branch_name" | grep -E "^(feature|bugfix|hotfix|chore|docs)/" > /dev/null; then
        echo "✅ Valid branch name format: $branch_name"
        
        # Check if branch already exists
        if git rev-parse --verify "$branch_name" >/dev/null 2>&1; then
            echo "❌ Branch already exists: $branch_name"
            echo "💡 Try a different name or checkout existing branch:"
            echo "   git checkout $branch_name"
        else
            echo "🚀 Creating branch: $branch_name"
            if git checkout -b "$branch_name"; then
                echo "✅ Branch created and checked out successfully"
                echo "🎯 Ready for development on: $branch_name"
            else
                echo "❌ Failed to create branch"
            fi
        fi
    else
        echo "❌ Invalid branch name format: $branch_name"
        echo "💡 Use one of these prefixes:"
        echo "   feature/  - New features"
        echo "   bugfix/   - Bug fixes"
        echo "   hotfix/   - Urgent fixes"
        echo "   chore/    - Maintenance tasks"
        echo "   docs/     - Documentation"
        echo ""
        echo "Example: /create-branch feature/user-authentication"
    fi
else
    echo "🛠️  Interactive branch creation:"
    echo ""
    echo "Common branch types:"
    echo "• feature/[description]  - New features and enhancements"
    echo "• bugfix/[description]   - Bug fixes and corrections"  
    echo "• hotfix/[description]   - Urgent production fixes"
    echo "• chore/[description]    - Maintenance and refactoring"
    echo "• docs/[description]     - Documentation updates"
    echo ""
    echo "💡 Usage: /create-branch [type]/[description]"
    echo "Example: /create-branch feature/command-system-improvements"
fi`

## Branch Naming Conventions

### Recommended Formats

- **Features**: `feature/command-hierarchies`, `feature/jira-api-integration`
- **Bug Fixes**: `bugfix/json-to-markdown`, `bugfix/command-parsing`
- **Hotfixes**: `hotfix/critical-security-patch`, `hotfix/production-error`
- **Chores**: `chore/update-dependencies`, `chore/cleanup-configs`
- **Documentation**: `docs/api-documentation`, `docs/setup-guide`

### Best Practices

1. **Use descriptive names**: Clearly describe what the branch does
2. **Keep it concise**: Aim for 2-4 words after the prefix
3. **Use kebab-case**: Separate words with hyphens
4. **Include ticket numbers**: `feature/KAN-123-new-commands` (if applicable)

## Next Steps

After creating a branch:
1. Make your changes and commits
2. Use `/run-tests` to verify your changes
3. Push the branch: `git push -u origin [branch-name]`
4. Create a pull request for code review