#!/usr/bin/env python3
"""
Debug script to understand agent creation issues
"""

from database import db_manager
from datetime import datetime
import json

def debug_agent_creation():
    """Debug agent creation process"""
    print("🔍 Debugging agent creation...")
    
    # Clear existing agents
    print("🗑️ Clearing existing agents...")
    with db_manager.get_connection() as conn:
        conn.execute("DELETE FROM agents")
        conn.execute("DELETE FROM command_history")
        conn.commit()
    
    print(f"📊 Agents after clearing: {len(db_manager.get_agents())}")
    
    # Create first agent
    agent1_data = {
        'hostname': 'DESKTOP-JK5G34L',
        'ip': '172.27.48.1',
        'os': 'Windows 10 Pro 2009',
        'version': '2009',
        'status': 'online',
        'last_seen': datetime.now().isoformat(),
        'tags': ['primary', 'windows', 'powershell-enabled', 'real-system'],
        'system_info': {
            'hostname': 'DESKTOP-JK5G34L',
            'os_version': 'Windows 10 Pro 2009',
            'cpu_usage': 15.2,
            'memory_usage': 65.8,
            'disk_usage': {'C:': 85.3},
            'processor_name': '13th Gen Intel(R) Core(TM) i7-13700K'
        }
    }
    
    print("➕ Creating agent 1...")
    agent1_id = db_manager.add_agent(agent1_data)
    print(f"✅ Agent 1 created with ID: {agent1_id}")
    print(f"📊 Total agents: {len(db_manager.get_agents())}")
    
    # Create second agent
    agent2_data = {
        'hostname': 'WS-001.domain.com',
        'ip': '192.168.1.101',
        'os': 'Windows 11 Pro',
        'version': '10.0.22621',
        'status': 'online',
        'last_seen': datetime.now().isoformat(),
        'tags': ['workstation', 'development'],
        'system_info': {
            'hostname': 'WS-001.domain.com',
            'os_version': 'Windows 11 Pro',
            'cpu_usage': 25.3,
            'memory_usage': 68.7,
            'disk_usage': {'C:': 45.2, 'D:': 12.8},
            'processor_name': 'Intel(R) Core(TM) i7-10700K CPU @ 3.80GHz'
        }
    }
    
    print("➕ Creating agent 2...")
    agent2_id = db_manager.add_agent(agent2_data)
    print(f"✅ Agent 2 created with ID: {agent2_id}")
    print(f"📊 Total agents: {len(db_manager.get_agents())}")
    
    # List all agents
    print("\n📋 All Agents:")
    agents = db_manager.get_agents()
    for i, agent in enumerate(agents, 1):
        print(f"  {i}. {agent['hostname']} ({agent['ip']}) - {agent['status']} - ID: {agent['id']}")
    
    # Check database directly
    print("\n🔍 Direct database check:")
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, hostname, ip, status FROM agents")
        rows = cursor.fetchall()
        print(f"Raw database rows: {len(rows)}")
        for row in rows:
            print(f"  - {row}")

if __name__ == "__main__":
    debug_agent_creation() 