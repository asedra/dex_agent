import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "dexagents.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create agents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    hostname TEXT NOT NULL,
                    ip TEXT,
                    os TEXT,
                    version TEXT,
                    status TEXT DEFAULT 'offline',
                    last_seen TIMESTAMP,
                    tags TEXT,  -- JSON array as string
                    system_info TEXT,  -- JSON object as string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create command_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    command TEXT NOT NULL,
                    success BOOLEAN,
                    output TEXT,
                    error TEXT,
                    execution_time REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def add_agent(self, agent_data: Dict[str, Any]) -> str:
        """Add a new agent to the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Generate ID if not provided
            if 'id' not in agent_data:
                import time
                agent_data['id'] = f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000) % 1000}"
            
            # Convert tags to JSON string
            tags_json = json.dumps(agent_data.get('tags', []))
            
            # Convert system_info to JSON string
            system_info_json = json.dumps(agent_data.get('system_info', {}))
            
            cursor.execute('''
                INSERT OR REPLACE INTO agents 
                (id, hostname, ip, os, version, status, last_seen, tags, system_info, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_data['id'],
                agent_data['hostname'],
                agent_data.get('ip'),
                agent_data.get('os'),
                agent_data.get('version'),
                agent_data.get('status', 'offline'),
                agent_data.get('last_seen', datetime.now().isoformat()),
                tags_json,
                system_info_json,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            logger.info(f"Agent {agent_data['id']} added/updated successfully")
            return agent_data['id']
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get all agents from the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agents ORDER BY updated_at DESC')
            
            agents = []
            for row in cursor.fetchall():
                agent = dict(row)
                # Parse JSON fields
                agent['tags'] = json.loads(agent['tags'] or '[]')
                agent['system_info'] = json.loads(agent['system_info'] or '{}')
                agents.append(agent)
            
            return agents
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific agent by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agents WHERE id = ?', (agent_id,))
            row = cursor.fetchone()
            
            if row:
                agent = dict(row)
                # Parse JSON fields
                agent['tags'] = json.loads(agent['tags'] or '[]')
                agent['system_info'] = json.loads(agent['system_info'] or '{}')
                return agent
            
            return None
    
    def update_agent(self, agent_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing agent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically
            fields = []
            values = []
            
            for key, value in update_data.items():
                if key in ['hostname', 'ip', 'os', 'version', 'status', 'last_seen']:
                    fields.append(f"{key} = ?")
                    values.append(value)
                elif key == 'tags':
                    fields.append("tags = ?")
                    values.append(json.dumps(value))
                elif key == 'system_info':
                    fields.append("system_info = ?")
                    values.append(json.dumps(value))
            
            if not fields:
                return False
            
            fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(agent_id)
            
            query = f"UPDATE agents SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            logger.info(f"Agent {agent_id} updated successfully")
            return cursor.rowcount > 0
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent from the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM agents WHERE id = ?', (agent_id,))
            conn.commit()
            
            logger.info(f"Agent {agent_id} deleted successfully")
            return cursor.rowcount > 0
    
    def add_command_history(self, agent_id: str, command_data: Dict[str, Any]) -> int:
        """Add command execution history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO command_history 
                (agent_id, command, success, output, error, execution_time, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_id,
                command_data['command'],
                command_data['success'],
                command_data.get('output', ''),
                command_data.get('error', ''),
                command_data.get('execution_time', 0),
                command_data.get('timestamp', datetime.now().isoformat())
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_command_history(self, agent_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get command history for an agent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM command_history 
                WHERE agent_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (agent_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_agent_status(self, agent_id: str, status: str, system_info: Optional[Dict] = None) -> bool:
        """Update agent status and optionally system info"""
        update_data = {
            'status': status,
            'last_seen': datetime.now().isoformat()
        }
        
        if system_info:
            update_data['system_info'] = system_info
        
        return self.update_agent(agent_id, update_data)

# Global database instance
db_manager = DatabaseManager() 