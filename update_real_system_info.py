#!/usr/bin/env python3
"""
Update Real System Information Script
Updates the current system's agent with real-time PowerShell data
"""

import asyncio
import subprocess
import json
from datetime import datetime
from database import db_manager

def get_real_system_info():
    """Get real-time system information using PowerShell"""
    try:
        ps_command = """
        $computerInfo = Get-ComputerInfo
        $ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.*"} | Select-Object -First 1
        
        $cpu = Get-Counter -Counter "\\Processor(_Total)\\% Processor Time" -SampleInterval 1 -MaxSamples 1
        $memory = Get-Counter -Counter "\\Memory\\% Committed Bytes In Use" -SampleInterval 1 -MaxSamples 1
        $disk = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "C:"}
        
        $diskUsage = 0
        if ($disk) {
            $diskUsage = (($disk.Size - $disk.FreeSpace) / $disk.Size) * 100
        }
        
        $result = @{
            hostname = $computerInfo.CsName
            os_version = $computerInfo.WindowsProductName + " " + $computerInfo.WindowsVersion
            ip_address = $ipAddresses.IPAddress
            processor_name = $computerInfo.CsProcessors[0].Name
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

def update_current_system_agent():
    """Update the current system's agent with real-time data"""
    print("🔍 Getting real-time system information...")
    
    system_info = get_real_system_info()
    if not system_info:
        print("❌ Failed to get system information")
        return
    
    print(f"✅ Real-time system info:")
    print(f"   Hostname: {system_info.get('hostname', 'Unknown')}")
    print(f"   OS: {system_info.get('os_version', 'Unknown')}")
    print(f"   IP: {system_info.get('ip_address', 'Unknown')}")
    print(f"   CPU: {system_info.get('cpu_usage', 0)}%")
    print(f"   Memory: {system_info.get('memory_usage', 0)}%")
    print(f"   Disk C: {system_info.get('disk_usage', {}).get('C:', 0)}%")
    
    # Find the current system's agent
    agents = db_manager.get_agents()
    current_agent = None
    
    for agent in agents:
        if agent['hostname'] == system_info.get('hostname'):
            current_agent = agent
            break
    
    if not current_agent:
        print("❌ Current system agent not found in database")
        return
    
    # Update the agent with real-time data
    update_data = {
        'ip': system_info.get('ip_address'),
        'os': system_info.get('os_version'),
        'version': system_info.get('os_version', '').split()[-1] if system_info.get('os_version') else 'Unknown',
        'status': 'online',
        'last_seen': datetime.now().isoformat(),
        'system_info': {
            'hostname': system_info.get('hostname'),
            'os_version': system_info.get('os_version'),
            'cpu_usage': system_info.get('cpu_usage', 0),
            'memory_usage': system_info.get('memory_usage', 0),
            'disk_usage': system_info.get('disk_usage', {}),
            'processor_name': system_info.get('processor_name', 'Unknown')
        }
    }
    
    success = db_manager.update_agent(current_agent['id'], update_data)
    
    if success:
        print(f"✅ Agent {current_agent['hostname']} updated successfully!")
        print(f"   ID: {current_agent['id']}")
        print(f"   Status: online")
        print(f"   Last seen: {datetime.now().isoformat()}")
    else:
        print("❌ Failed to update agent")

def main():
    """Main function"""
    print("🔄 Updating current system agent with real-time data...")
    update_current_system_agent()
    print("✅ Update completed!")

if __name__ == "__main__":
    main() 