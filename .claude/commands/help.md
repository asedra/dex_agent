---
description: "Help system for Claude Code hierarchical commands"
---

# Help System

Welcome to the Claude Code Hierarchical Command System help.

## Quick Start

1. **View All Modes**: `/all-modes` - See all available command modes
2. **Select Mode**: `/developer-mode`, `/reviewer-mode`, or `/architect-mode`
3. **Use Commands**: Each mode provides specific commands for your workflow

## Command Structure

### Root Commands
- `/all-modes` - Display all available modes
- `/help` - Show this help information  
- `/status` - System status and configuration

### Mode Commands
- `/developer-mode` - Development workflow commands
- `/reviewer-mode` - Code review and quality commands
- `/architect-mode` - System design and architecture commands

## Getting Started

```bash
# Start here
/all-modes

# Choose your workflow
/developer-mode

# See what's available in that mode
# Commands will be listed automatically
```

## Jira API Integration

This system integrates with Jira via REST API:
- **Jira URL**: https://sipsy.atlassian.net
- **Projects**: KAN (Claude Code Development), SAM1 (Annual Product Roadmap)
- **Usage**: `/select-project [abbreviation]`

## Troubleshooting

If commands don't appear:
1. Ensure you're in a Claude Code environment
2. Check that `.claude/commands/` directory exists
3. Verify markdown files are properly formatted

## Support

For issues or feature requests, refer to the project documentation in README.md.