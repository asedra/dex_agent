import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations_dir = os.path.dirname(__file__)
        self.init_migrations_table()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()
    
    def init_migrations_table(self):
        """Create migrations tracking table"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT version FROM migrations ORDER BY id')
            return [row['version'] for row in cursor.fetchall()]
    
    def mark_migration_applied(self, version: str, description: str):
        """Mark a migration as applied"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO migrations (version, description)
                VALUES (?, ?)
            ''', (version, description))
            conn.commit()
    
    def apply_migration(self, version: str, description: str, up_sql: str):
        """Apply a single migration"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Execute migration
                for statement in up_sql.split(';'):
                    if statement.strip():
                        cursor.execute(statement)
                
                # Mark as applied
                cursor.execute('''
                    INSERT INTO migrations (version, description)
                    VALUES (?, ?)
                ''', (version, description))
                
                conn.commit()
                logger.info(f"Applied migration {version}: {description}")
                return True
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to apply migration {version}: {e}")
                return False
    
    def rollback_migration(self, version: str, down_sql: str):
        """Rollback a migration"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Execute rollback
                for statement in down_sql.split(';'):
                    if statement.strip():
                        cursor.execute(statement)
                
                # Remove from migrations table
                cursor.execute('DELETE FROM migrations WHERE version = ?', (version,))
                
                conn.commit()
                logger.info(f"Rolled back migration {version}")
                return True
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to rollback migration {version}: {e}")
                return False
    
    def run_migrations(self):
        """Run all pending migrations"""
        applied = self.get_applied_migrations()
        migrations = self.get_available_migrations()
        
        for migration in migrations:
            if migration['version'] not in applied:
                success = self.apply_migration(
                    migration['version'],
                    migration['description'],
                    migration['up']
                )
                if not success:
                    logger.error(f"Migration {migration['version']} failed, stopping.")
                    break
    
    def get_available_migrations(self) -> List[dict]:
        """Get list of available migrations"""
        # Import migrations from files
        migrations = []
        
        # Add initial migration
        from .v001_initial_schema import migration as v001
        migrations.append(v001)
        
        # Add indexes migration
        from .v002_add_indexes import migration as v002
        migrations.append(v002)
        
        # Sort by version
        migrations.sort(key=lambda x: x['version'])
        
        return migrations