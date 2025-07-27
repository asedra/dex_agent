#!/usr/bin/env python3
"""
Script to populate the database with initial agent data for testing
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from database import db_manager

def populate_agents():
    """Populate the database with sample agent data"""
    
    # Sample agent data
    sample_agents = [
        {
            "hostname": "WS-001.domain.com",
            "ip": "192.168.1.101",
            "os": "Windows 11 Pro",
            "version": "2.1.4",
            "status": "online",
            "last_seen": datetime.now().isoformat(),
            "tags": ["Production", "Finance"],
            "system_info": {
                "hostname": "WS-001.domain.com",
                "os_version": "Windows 11 Pro",
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": {"C:": 78.5, "D:": 23.1}
            }
        },
        {
            "hostname": "WS-002.domain.com",
            "ip": "192.168.1.102",
            "os": "Windows 10 Enterprise",
            "version": "2.1.4",
            "status": "online",
            "last_seen": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "tags": ["Development"],
            "system_info": {
                "hostname": "WS-002.domain.com",
                "os_version": "Windows 10 Enterprise",
                "cpu_usage": 32.1,
                "memory_usage": 54.3,
                "disk_usage": {"C:": 65.2, "E:": 45.7}
            }
        },
        {
            "hostname": "SRV-001.domain.com",
            "ip": "192.168.1.201",
            "os": "Windows Server 2022",
            "version": "2.1.3",
            "status": "offline",
            "last_seen": (datetime.now() - timedelta(hours=2)).isoformat(),
            "tags": ["Server", "Critical"],
            "system_info": {
                "hostname": "SRV-001.domain.com",
                "os_version": "Windows Server 2022",
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": {"C:": 0.0, "D:": 0.0}
            }
        },
        {
            "hostname": "WS-045.domain.com",
            "ip": "192.168.1.145",
            "os": "Windows 11 Pro",
            "version": "2.1.4",
            "status": "pending",
            "last_seen": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "tags": ["HR"],
            "system_info": {
                "hostname": "WS-045.domain.com",
                "os_version": "Windows 11 Pro",
                "cpu_usage": 28.9,
                "memory_usage": 42.1,
                "disk_usage": {"C:": 71.3}
            }
        }
    ]
    
    print("Populating database with sample agents...")
    
    for agent_data in sample_agents:
        try:
            agent_id = db_manager.add_agent(agent_data)
            print(f"✓ Added agent: {agent_data['hostname']} (ID: {agent_id})")
        except Exception as e:
            print(f"✗ Failed to add agent {agent_data['hostname']}: {e}")
    
    # Add some command history
    print("\nAdding sample command history...")
    
    sample_commands = [
        {
            "agent_id": "agent_20241201_120000",  # This will be the first agent's ID
            "command": "Get-Process | Select-Object Name, CPU, WorkingSet | Sort-Object CPU -Descending | Select-Object -First 10",
            "success": True,
            "output": "Name                    CPU(s) WorkingSet(MB)\n----                    ------ --------------\nchrome.exe              45.2    1,234.5\npowershell.exe           12.3      567.8\nsvchost.exe              8.9      234.1",
            "error": "",
            "execution_time": 2.34,
            "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat()
        },
        {
            "agent_id": "agent_20241201_120000",
            "command": "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name, Status",
            "success": True,
            "output": "Name                    Status\n----                    ------\nAudioSrv                Running\nBITS                    Running\nCryptSvc                Running",
            "error": "",
            "execution_time": 1.87,
            "timestamp": (datetime.now() - timedelta(minutes=25)).isoformat()
        }
    ]
    
    for cmd_data in sample_commands:
        try:
            cmd_id = db_manager.add_command_history(cmd_data["agent_id"], cmd_data)
            print(f"✓ Added command history entry (ID: {cmd_id})")
        except Exception as e:
            print(f"✗ Failed to add command history: {e}")
    
    print("\nDatabase population completed!")
    print(f"Total agents in database: {len(db_manager.get_agents())}")

if __name__ == "__main__":
    try:
        populate_agents()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 