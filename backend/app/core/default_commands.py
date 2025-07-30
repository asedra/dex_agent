"""Default PowerShell commands to be inserted on application startup"""

DEFAULT_COMMANDS = [
    {
        'id': 'sys-get-computer-info',
        'name': 'Get System Information',
        'description': 'Retrieves comprehensive system information including OS, hardware, and network details',
        'category': 'system',
        'command': 'Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory, CsProcessors | ConvertTo-Json',
        'parameters': [],
        'tags': ['system', 'hardware', 'info'],
        'version': '1.0',
        'author': 'System',
        'is_system': True
    },
    {
        'id': 'sys-check-disk-space',
        'name': 'Check Disk Space',
        'description': 'Monitors disk space usage across all drives with JSON output',
        'category': 'disk',
        'command': 'Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name="Size_GB";Expression={[math]::Round($_.Size/1GB,2)}}, @{Name="FreeSpace_GB";Expression={[math]::Round($_.FreeSpace/1GB,2)}}, @{Name="UsedPercent";Expression={[math]::Round((($_.Size-$_.FreeSpace)/$_.Size)*100,1)}} | ConvertTo-Json',
        'parameters': [],
        'tags': ['disk', 'storage', 'monitoring'],
        'version': '1.0',
        'author': 'System',
        'is_system': True
    },
    {
        'id': 'sys-network-config',
        'name': 'Get Network Configuration',
        'description': 'Retrieves network adapter configuration and IP settings',
        'category': 'network',
        'command': 'Get-NetIPConfiguration | Select-Object InterfaceAlias, IPv4Address, IPv4DefaultGateway | ConvertTo-Json',
        'parameters': [],
        'tags': ['network', 'ip', 'configuration'],
        'version': '1.0',
        'author': 'System',
        'is_system': True
    },
    {
        'id': 'sys-event-logs',
        'name': 'Get Event Logs',
        'description': 'Retrieves system event logs with customizable parameters',
        'category': 'monitoring',
        'command': 'Get-EventLog -LogName $LogName -Newest $Count | Where-Object {$_.EntryType -eq "$Level"} | Select-Object TimeGenerated, EntryType, Source, Message | ConvertTo-Json',
        'parameters': [
            {
                "name": "LogName",
                "type": "string",
                "default": "System",
                "description": "Log name to query",
                "required": True
            },
            {
                "name": "Count",
                "type": "number",
                "default": "10",
                "description": "Number of entries to retrieve",
                "required": False
            },
            {
                "name": "Level",
                "type": "string",
                "default": "Error",
                "description": "Event level filter (Error, Warning, Information)",
                "required": False
            }
        ],
        'tags': ['logs', 'events', 'monitoring', 'troubleshooting'],
        'version': '1.0',
        'author': 'System',
        'is_system': True
    },
    {
        'id': 'sys-security-audit',
        'name': 'Security Audit',
        'description': 'Performs basic security audit checks with JSON output',
        'category': 'security',
        'command': '$users = Get-LocalUser | Select-Object Name, Enabled, LastLogon; $services = Get-Service | Where-Object {$_.Status -eq "Running" -and $_.Name -like "*Remote*"} | Select-Object Name, Status; @{Users=$users; RemoteServices=$services} | ConvertTo-Json -Depth 3',
        'parameters': [],
        'tags': ['security', 'audit', 'users', 'services'],
        'version': '1.0',
        'author': 'System',
        'is_system': True
    },
    {
        'id': 'sys-process-list',
        'name': 'Get Running Processes',
        'description': 'Lists all running processes with resource usage',
        'category': 'system',
        'command': 'Get-Process | Select-Object Name, Id, CPU, WorkingSet, @{Name="Memory_MB";Expression={[math]::Round($_.WorkingSet/1MB,2)}} | Sort-Object CPU -Descending | Select-Object -First $Count | ConvertTo-Json',
        'parameters': [
            {
                "name": "Count",
                "type": "number", 
                "default": "20",
                "description": "Number of top processes to show",
                "required": False
            }
        ],
        'tags': ['processes', 'performance', 'monitoring'],
        'version': '1.0',
        'author': 'System',
        'is_system': True
    },
    {
        'id': 'sys-service-status',
        'name': 'Get Service Status',
        'description': 'Check status of Windows services',
        'category': 'system',
        'command': 'Get-Service | Group-Object Status | Select-Object Name, Count | ConvertTo-Json',
        'parameters': [],
        'tags': ['services', 'status', 'monitoring'],
        'version': '1.0',
        'author': 'System',
        'is_system': True
    }
]