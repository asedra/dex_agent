#!/bin/bash
set -e

echo "Starting DexAgents Backend..."

# Create necessary directories
mkdir -p /app/data /app/logs /app/temp /app/agent_installers

# Run database migrations
echo "Running database migrations..."
python -c "
from app.migrations.migration_manager import MigrationManager
from app.core.config import settings
import os

db_path = os.path.join('/app', settings.DATABASE_URL)
mm = MigrationManager(db_path)
mm.run_migrations()
print('Migrations completed successfully')
"

# Insert default PowerShell commands
echo "Inserting default PowerShell commands..."
python /app/app/scripts/insert_default_commands.py

# Start the application
echo "Starting the application..."
exec python run.py