#!/usr/bin/env python3
"""
Real Agent Data Population Script
Uses PowerShell to get real system information and populate the database
"""

import asyncio
import subprocess
import json
import sqlite3
from datetime import datetime, timedelta
from database import db_manager

def get_system_info_powershell():
    """Get real system information using PowerShell"""
    try:
        # Simple PowerShell command to get basic system information
        ps_command = """
        $computerInfo = Get-ComputerInfo
        $ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.*"} | Select-Object -First 1
        
        $result = @{
            hostname = $computerInfo.CsName
            os_version = $computerInfo.WindowsProductName + " " + $computerInfo.WindowsVersion
            ip_address = $ipAddresses.IPAddress
            processor_name = $computerInfo.CsProcessors[0].Name
        }
        
        ConvertTo-Json -Compress $result
        """
        
        # Execute PowerShell command
        result = subprocess.run(
            ["powershell.exe", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
        else:
            print(f"PowerShell error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error getting system info: {e}")
        return None

def get_performance_info_powershell():
    """Get performance information using PowerShell"""
    try:
        ps_command = """
        $cpu = Get-Counter -Counter "\\Processor(_Total)\\% Processor Time" -SampleInterval 1 -MaxSamples 1
        $memory = Get-Counter -Counter "\\Memory\\% Committed Bytes In Use" -SampleInterval 1 -MaxSamples 1
        $disk = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "C:"}
        
        $diskUsage = 0
        if ($disk) {
            $diskUsage = (($disk.Size - $disk.FreeSpace) / $disk.Size) * 100
        }
        
        $result = @{
            cpu_usage = [math]::Round($cpu.CounterSamples[0].CookedValue, 1)
            memory_usage = [math]::Round($memory.CounterSamples[0].CookedValue, 1)
            disk_usage = @{"C:" = [math]::Round($diskUsage, 1)}
        }
        
        ConvertTo-Json -Compress $result
        """
        
        result = subprocess.run(
            ["powershell.exe", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
        else:
            return {'cpu_usage': 0, 'memory_usage': 0, 'disk_usage': {'C:': 0}}
            
    except Exception as e:
        print(f"Error getting performance info: {e}")
        return {'cpu_usage': 0, 'memory_usage': 0, 'disk_usage': {'C:': 0}}

def populate_real_agents():
    """Populate database with real agent data"""
    print("🔍 Getting real system information...")
    
    # Get current system info
    system_info = get_system_info_powershell()
    if not system_info:
        print("❌ Failed to get system information")
        return
    
    # Get performance info
    performance_info = get_performance_info_powershell()
    
    print(f"✅ System info retrieved:")
    print(f"   Hostname: {system_info.get('hostname', 'Unknown')}")
    print(f"   OS: {system_info.get('os_version', 'Unknown')}")
    print(f"   IP: {system_info.get('ip_address', 'Unknown')}")
    print(f"   CPU: {performance_info.get('cpu_usage', 0)}%")
    print(f"   Memory: {performance_info.get('memory_usage', 0)}%")
    
    # Clear existing agents
    print("🗑️ Clearing existing agents...")
    with db_manager.get_connection() as conn:
        conn.execute("DELETE FROM agents")
        conn.execute("DELETE FROM command_history")
        conn.commit()
    
    # Create main agent (current system)
    main_agent_data = {
        'hostname': system_info.get('hostname', 'Unknown'),
        'ip': system_info.get('ip_address', 'Unknown'),
        'os': system_info.get('os_version', 'Unknown'),
        'version': system_info.get('os_version', 'Unknown').split()[-1] if system_info.get('os_version') else 'Unknown',
        'status': 'online',
        'last_seen': datetime.now().isoformat(),
        'tags': ['primary', 'windows', 'powershell-enabled', 'real-system'],
        'system_info': {
            'hostname': system_info.get('hostname'),
            'os_version': system_info.get('os_version'),
            'cpu_usage': performance_info.get('cpu_usage', 0),
            'memory_usage': performance_info.get('memory_usage', 0),
            'disk_usage': performance_info.get('disk_usage', {}),
            'processor_name': system_info.get('processor_name', 'Unknown')
        }
    }
    
    agent_id = db_manager.add_agent(main_agent_data)
    print(f"✅ Main agent created: {agent_id}")
    
    # Add some sample command history
    print("📝 Adding sample command history...")
    sample_commands = [
        {
            'command': 'Get-Process | Sort-Object CPU -Descending | Select-Object -First 10',
            'success': True,
            'output': 'Process list retrieved successfully',
            'execution_time': 0.5
        },
        {
            'command': 'Get-Service | Where-Object {$_.Status -eq "Running"} | Measure-Object | Select-Object Count',
            'success': True,
            'output': 'Count: 45',
            'execution_time': 0.3
        },
        {
            'command': 'Get-Disk | Format-Table -AutoSize',
            'success': True,
            'output': 'Disk information displayed',
            'execution_time': 0.2
        }
    ]
    
    # Get the main agent ID for command history
    agents = db_manager.get_agents()
    if agents:
        main_agent_id = agents[0]['id']
        for cmd in sample_commands:
            db_manager.add_command_history(main_agent_id, cmd)
    
    print("✅ Real agent data population completed!")
    print(f"📊 Total agents: {len(db_manager.get_agents())}")
    
    # Print all agents
    print("\n📋 Agent List:")
    for agent in db_manager.get_agents():
        print(f"  - {agent['hostname']} ({agent['ip']}) - {agent['status']}")

if __name__ == "__main__":
    populate_real_agents() 