# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT: When Claude Code starts a new session, immediately display the "Available Custom Commands" section to show the user what commands are available.**

## 🚀 Available Custom Commands

When Claude Code starts, these custom commands are available:

| Command | Description | Action |
|---------|-------------|--------|
| **"test raporunu oku"** | Read and fix test report | Reads `C:\test_report.md`, analyzes findings, implements fixes, tests in Docker, and requests commit approval |

Simply type any of these commands to execute the corresponding workflow.

## Project Overview

DexAgents is a Windows endpoint management platform for remote PowerShell command execution and system monitoring. It consists of:
- **Backend**: FastAPI-based server with SQLite database, WebSocket support, and comprehensive API
- **Frontend**: Next.js 15 application with shadcn/ui components and real-time features
- **Agent**: Python-based Windows client with PowerShell integration
- **Infrastructure**: Docker Compose setup with nginx reverse proxy

## Essential Development Commands

### Quick Start

#### PostgreSQL Setup (Recommended)
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your PostgreSQL credentials
# DATABASE_URL=postgresql://dexagents:your_password@postgres:5432/dexagents

# Development with Docker (PostgreSQL)
docker-compose up -d --build
docker-compose logs -f  # Monitor logs

# Check database migration status
docker exec -it dexagents-backend-dev python -c "from app.migrations.migration_manager import MigrationManager; from app.core.config import settings; mm = MigrationManager(settings.DATABASE_URL); print('Applied migrations:', mm.get_applied_migrations())"
```

#### SQLite Setup (Development Only)
```bash
# For SQLite, use:
# DATABASE_URL=data/dexagents.db

# Manual backend development
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac: venv\Scripts\activate on Windows
pip install -r requirements.txt
python run.py

# Manual frontend development
cd frontend
npm install  # or pnpm install
npm run dev  # or pnpm dev
```

### Build & Test Commands
```bash
# Frontend build and type checking
cd frontend
npm run build
npm run type-check
npm run lint
npm run lint:fix

# Backend testing (create tests first)
cd backend
python -m pytest tests/
```

### Database Operations
```bash
# PostgreSQL Database migration (Docker)
docker exec -it dexagents-backend-dev python -c "from app.migrations.migration_manager import MigrationManager; from app.core.config import settings; MigrationManager(settings.DATABASE_URL).run_migrations()"

# Connect to PostgreSQL directly
docker exec -it dexagents-postgres-dev psql -U dexagents -d dexagents

# Check PostgreSQL database schema
docker exec -it dexagents-postgres-dev psql -U dexagents -d dexagents -c "\dt"

# Reset PostgreSQL database completely
docker-compose down -v
docker-compose up -d --build

# SQLite Database operations (legacy)
# For SQLite: MigrationManager('/app/data/dexagents.db').run_migrations()

# Manual database initialization
cd backend
python -c "from app.core.database import db_manager; db_manager.init_database()"
```

### Container Management  
```bash
# View service status
docker-compose ps

# Restart specific service
docker-compose restart backend
docker-compose restart frontend

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

## High-Level Architecture

### Backend Architecture (FastAPI)
- **`app/main.py`**: Application factory and startup configuration
- **`app/api/v1/`**: REST API endpoints organized by domain
  - `agents.py`: Agent management (register, update, command execution)
  - `commands.py`: PowerShell command library management
  - `websocket.py`: Real-time WebSocket communication
  - `auth.py`: JWT authentication and user management
  - `system.py`: System health and monitoring
- **`app/core/`**: Core services and utilities
  - `database.py`: SQLite database manager with 10+ tables
  - `websocket_manager.py`: WebSocket connection management
  - `config.py`: Settings and environment configuration
- **`app/models/`**: Database models for agents, users, commands, metrics, etc.
- **`app/migrations/`**: Database schema versioning system

### Frontend Architecture (Next.js 15)
- **App Router Structure**: `/app` directory with file-based routing
- **`components/ui/`**: shadcn/ui component library
- **`lib/api.ts`**: TypeScript API client with full type definitions
- **`contexts/AuthContext.tsx`**: Authentication state management
- **Real-time Features**: WebSocket integration for live agent updates

### Agent Architecture
- **`agent/websocket_agent.py`**: Main WebSocket client for Windows
- **PowerShell Integration**: Real-time command execution via WebSocket
- **System Monitoring**: CPU, memory, disk, network metrics collection
- **Auto-reconnection**: Resilient connection handling

## Database Schema

The database (PostgreSQL/SQLite) includes these key tables:
- **agents**: Agent registration and status
- **users**: Authentication and user management  
- **command_history**: PowerShell execution logs
- **powershell_commands**: Saved command library
- **agent_metrics**: Performance monitoring data
- **alerts**: System notifications
- **audit_logs**: Security and compliance tracking
- **scheduled_tasks**: Automation and scheduling

Schema is managed via the migration system in `app/migrations/`.

## Key Development Patterns

### WebSocket Communication
Messages follow this structure:
```javascript
{
  "type": "powershell_command",
  "request_id": "ps_123456789_abc123", 
  "command": "Get-ComputerInfo | ConvertTo-Json",
  "timeout": 30
}
```

### Error Handling
- Backend uses FastAPI exception handling
- Frontend has error boundaries and toast notifications
- Database operations use context managers for transaction safety

### Configuration Management
- Backend: Environment variables via `app/core/config.py`
- Frontend: Next.js environment variables (`NEXT_PUBLIC_*`)
- Docker: `docker-compose.yml` environment sections

## Common Development Workflows

### Adding New API Endpoints
1. Create endpoint in appropriate `app/api/v1/*.py` file
2. Add TypeScript types to `frontend/lib/api.ts`
3. Update API client methods in `ApiClient` class
4. Add database methods to `database.py` if needed

### Database Schema Changes
1. Create new migration files in `app/migrations/`:
   - `v00X_*_postgresql.py` for PostgreSQL
   - `v00X_*.py` for SQLite (if supporting both)
2. Update migration manager to include new migration
3. Test migration: `MigrationManager(settings.DATABASE_URL).run_migrations()`
4. Update database models in `app/core/database.py` and `app/core/database_postgresql.py`

### Adding Frontend Components
1. Follow shadcn/ui patterns in `components/ui/`
2. Use TypeScript interfaces from `lib/api.ts`
3. Implement error handling and loading states
4. Add to appropriate page in `app/` directory

## Security Considerations

- JWT tokens for API authentication
- Input validation via Pydantic schemas
- SQL injection protection through parameterized queries
- CORS configuration for cross-origin requests
- Audit logging for compliance tracking

## Troubleshooting

### Common Issues
- **Port conflicts**: Check ports 3000 (frontend) and 8080 (backend)
- **Database locks**: Restart backend service if SQLite locks occur
- **WebSocket disconnections**: Check agent logs and network connectivity
- **Migration failures**: Review migration logs and database state

### Debug Tools
- Backend logs: `docker-compose logs backend`
- Frontend dev tools: Built-in Next.js error overlay
- Database inspection: SQLite browser or CLI tools
- API testing: `/docs` endpoint for OpenAPI documentation

## Environment Variables

Key variables for development:
- `DATABASE_URL`: Database connection string
  - PostgreSQL: `postgresql://user:password@host:port/database`
  - SQLite: `data/dexagents.db`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: PostgreSQL configuration
- `BACKEND_CORS_ORIGINS`: Frontend URL for CORS
- `SECRET_KEY`: JWT signing key (change in production)
- `NEXT_PUBLIC_API_URL`: Backend API URL for frontend

Copy `.env.example` to `.env` and update values for your environment.

## Test Report Workflow

### Test Report Command
When user says "test raporunu oku" (read test report):
1. Read test report from Windows path: `C:\test_report.md` (accessible from WSL as `/mnt/c/test_report.md`)
2. Analyze findings and issues in the report
3. Implement fixes for identified problems in the project
4. Start Docker containers: `docker-compose up -d --build`  
5. Perform own testing to verify fixes work
6. Ask user for approval before committing changes
7. After user approval, commit changes with descriptive message
8. Stop Docker containers: `docker-compose down` (ONLY after commit is complete)

### Test Report Processing Steps
```bash
# Read test report (WSL path conversion)
cat /mnt/c/test_report.md

# Start project for testing fixes
docker-compose up -d --build

# After implementing fixes and testing
# Keep containers running for user testing
# Ask user: "Değişiklikleri commit etmemi onaylıyor musunuz?" 
# Wait for user approval before:
git add .
git commit -m "fix: resolve issues from test report - [brief description]"
git push origin main

# IMPORTANT: Only stop containers AFTER commit is complete
docker-compose down
```

### Important Container Management Rules:
- **During Development**: Keep containers running for user testing
- **Before Commit**: Allow user to test the running system
- **After Commit**: Only stop containers after git push is complete
- **User Experience**: Never stop containers before user confirms changes work

## Git Configuration

### GitHub Authentication
- GitHub token is stored in `/home/ali/gitkey.md`
- Before any git operations (commit, push, pull), always read this file and configure the remote URL
- Use the format: `https://TOKEN@github.com/asedra/dex_agent.git`

### Essential Git Commands
```bash
# Configure git remote with token (run before git operations)
GITHUB_TOKEN=$(cat /home/ali/gitkey.md | head -n1 | tr -d '\n')
git remote set-url origin "https://${GITHUB_TOKEN}@github.com/asedra/dex_agent.git"

# Standard git workflow
git add .
git commit -m "your commit message"
git push origin main
```

### Git Workflow Integration
When making changes to the codebase:
1. Read the GitHub token from `/home/ali/gitkey.md`
2. Configure the remote URL with the token
3. Perform git operations (add, commit, push)
4. Always include proper commit messages with Claude Code signature

## File Structure Notes

- Database files stored in `backend/data/`
- Agent installers in `backend/agent_installers/`
- Frontend static assets in `frontend/public/`
- Docker volumes for persistent data
- Logs in `backend/logs/` directory
- GitHub token stored in `/home/ali/gitkey.md` (for git operations)