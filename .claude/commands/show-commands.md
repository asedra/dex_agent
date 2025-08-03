Show available custom commands for this project.

## Available Custom Commands

| Command | Description | Action |
|---------|-------------|--------|
| **"test raporunu oku"** | Read and fix test report | Reads `C:\test_report.md`, analyzes findings, implements fixes, tests in Docker, and requests commit approval |

Simply type any of these commands to execute the corresponding workflow.

## How to use:
- Type the command exactly as shown in quotes
- Commands are case-sensitive
- Wait for Claude to complete the full workflow

## Test Report Command Details:
When you say "test raporunu oku":
1. Reads test report from `C:\test_report.md` (WSL path: `/mnt/c/test_report.md`)
2. Analyzes findings and issues in the report
3. Implements fixes for identified problems in the project
4. Starts Docker containers: `docker-compose up -d --build`
5. Performs testing to verify fixes work
6. Asks for approval before committing changes
7. After approval, commits with descriptive message
8. Stops Docker containers: `docker-compose down`