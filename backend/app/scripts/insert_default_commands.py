import json
import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, '/app')

from app.core.database import db_manager

def insert_default_commands():
    """Insert default PowerShell commands into the database"""
    
    default_commands = [
        {
            'id': 'sys-get-computer-info',
            'name': 'Get System Information',
            'description': 'Retrieves comprehensive system information including OS, hardware, and network details',
            'category': 'system',
            'command': 'Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory, CsProcessors | ConvertTo-Json',
            'parameters': [],
            'tags': ["system", "hardware", "info"],
            'version': '1.0',
            'author': 'System',
            'is_system': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'id': 'sys-check-disk-space',
            'name': 'Check Disk Space',
            'description': 'Monitors disk space usage across all drives with JSON output',
            'category': 'disk',
            'command': 'Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name="Size_GB";Expression={[math]::Round($_.Size/1GB,2)}}, @{Name="FreeSpace_GB";Expression={[math]::Round($_.FreeSpace/1GB,2)}}, @{Name="UsedPercent";Expression={[math]::Round((($_.Size-$_.FreeSpace)/$_.Size)*100,1)}} | ConvertTo-Json',
            'parameters': '[]',
            'tags': json.dumps(["disk", "storage", "monitoring"]),
            'version': '1.0',
            'author': 'System',
            'is_system': 1
        },
        {
            'id': 'sys-network-config',
            'name': 'Get Network Configuration',
            'description': 'Retrieves network adapter configuration and IP settings',
            'category': 'network',
            'command': 'Get-NetIPConfiguration | Select-Object InterfaceAlias, IPv4Address, IPv4DefaultGateway | ConvertTo-Json',
            'parameters': '[]',
            'tags': json.dumps(["network", "ip", "configuration"]),
            'version': '1.0',
            'author': 'System',
            'is_system': 1
        },
        {
            'id': 'sys-security-audit',
            'name': 'Security Audit',
            'description': 'Performs basic security audit checks with JSON output',
            'category': 'security',
            'command': '$users = Get-LocalUser | Select-Object Name, Enabled, LastLogon; $services = Get-Service | Where-Object {$_.Status -eq "Running" -and $_.Name -like "*Remote*"} | Select-Object Name, Status; @{Users=$users; RemoteServices=$services} | ConvertTo-Json -Depth 3',
            'parameters': '[]',
            'tags': json.dumps(["security", "audit", "users", "services"]),
            'version': '1.0',
            'author': 'System',
            'is_system': 1
        },
        {
            'id': 'sys-process-list',
            'name': 'Get Running Processes',
            'description': 'Lists all running processes with resource usage',
            'category': 'system',
            'command': 'Get-Process | Select-Object Name, Id, CPU, WorkingSet, @{Name="Memory_MB";Expression={[math]::Round($_.WorkingSet/1MB,2)}} | Sort-Object CPU -Descending | Select-Object -First $Count | ConvertTo-Json',
            'parameters': json.dumps([
                {"name":"Count","type":"number","default":"20","description":"Number of top processes to show","required":False}
            ]),
            'tags': json.dumps(["processes", "performance", "monitoring"]),
            'version': '1.0',
            'author': 'System',
            'is_system': 1
        },
        {
            'id': 'sys-service-status',
            'name': 'Get Service Status',
            'description': 'Check status of Windows services',
            'category': 'system',
            'command': 'Get-Service | Group-Object Status | Select-Object Name, Count | ConvertTo-Json',
            'parameters': '[]',
            'tags': json.dumps(["services", "status", "monitoring"]),
            'version': '1.0',
            'author': 'System',
            'is_system': 1
        }
    ]
    
    # Insert commands using database manager
    for cmd in default_commands:
        try:
            # Convert legacy format to new format if needed
            command_data = {
                'id': cmd['id'],
                'name': cmd['name'],
                'description': cmd['description'],
                'category': cmd['category'],
                'command': cmd['command'],
                'parameters': cmd.get('parameters', []) if isinstance(cmd.get('parameters'), list) else [],
                'tags': cmd.get('tags', []) if isinstance(cmd.get('tags'), list) else json.loads(cmd.get('tags', '[]')),
                'version': cmd['version'],
                'author': cmd['author'],
                'is_system': cmd['is_system'] if isinstance(cmd['is_system'], bool) else bool(cmd['is_system']),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            success = db_manager.save_powershell_command(command_data)
            if success:
                print(f"Inserted command: {cmd['name']}")
            else:
                print(f"Failed to insert command: {cmd['name']}")
        except Exception as e:
            print(f"Error inserting {cmd['name']}: {e}")
    
    print("Default commands insertion completed!")

if __name__ == "__main__":
    insert_default_commands()