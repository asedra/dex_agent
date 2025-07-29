"""
Migration v003: Add PowerShell Commands table
"""

MIGRATION = {
    'version': 'v003',
    'description': 'Add PowerShell Commands table for saved command templates',
    'up': '''
        -- Create powershell_commands table
        CREATE TABLE IF NOT EXISTS powershell_commands (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL DEFAULT 'general',
            command TEXT NOT NULL,
            parameters TEXT, -- JSON array of parameters
            tags TEXT, -- JSON array of tags
            version TEXT DEFAULT '1.0',
            author TEXT DEFAULT 'Unknown',
            is_system BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create index for faster queries
        CREATE INDEX IF NOT EXISTS idx_powershell_commands_category ON powershell_commands(category);
        CREATE INDEX IF NOT EXISTS idx_powershell_commands_author ON powershell_commands(author);
        CREATE INDEX IF NOT EXISTS idx_powershell_commands_created_at ON powershell_commands(created_at);
        
        -- Insert default system commands
        INSERT OR IGNORE INTO powershell_commands (id, name, description, category, command, parameters, tags, version, author, is_system, created_at, updated_at) VALUES
        ('sys-get-computer-info', 'Get System Information', 'Retrieves comprehensive system information including OS, hardware, and network details', 'system', 'Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory, CsProcessors | ConvertTo-Json', '[]', '[\'system\', \'hardware\', \'info\']', '1.0', 'System', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        
        ('sys-check-disk-space', 'Check Disk Space', 'Monitors disk space usage across all drives with JSON output', 'disk', 'Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name=''Size_GB'';Expression={[math]::Round($_.Size/1GB,2)}}, @{Name=''FreeSpace_GB'';Expression={[math]::Round($_.FreeSpace/1GB,2)}}, @{Name=''UsedPercent'';Expression={[math]::Round((($_.Size-$_.FreeSpace)/$_.Size)*100,1)}} | ConvertTo-Json', '[]', '[''disk'', ''storage'', ''monitoring'']', '1.0', 'System', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        
        ('sys-network-config', 'Get Network Configuration', 'Retrieves network adapter configuration and IP settings', 'network', 'Get-NetIPConfiguration | Select-Object InterfaceAlias, IPv4Address, IPv4DefaultGateway | ConvertTo-Json', '[]', '[\'network\', \'ip\', \'configuration\']', '1.0', 'System', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        
        ('sys-event-logs', 'Get Event Logs', 'Retrieves system event logs with customizable parameters', 'monitoring', 'Get-EventLog -LogName $LogName -Newest $Count | Where-Object {$_.EntryType -eq \"$Level\"} | Select-Object TimeGenerated, EntryType, Source, Message | ConvertTo-Json', '[{\"name\":\"LogName\",\"type\":\"string\",\"default\":\"System\",\"description\":\"Log name to query\",\"required\":true},{\"name\":\"Count\",\"type\":\"number\",\"default\":\"10\",\"description\":\"Number of entries to retrieve\",\"required\":false},{\"name\":\"Level\",\"type\":\"string\",\"default\":\"Error\",\"description\":\"Event level filter (Error, Warning, Information)\",\"required\":false}]', '[\'logs\', \'events\', \'monitoring\', \'troubleshooting\']', '1.0', 'System', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        
        ('sys-security-audit', 'Security Audit', 'Performs basic security audit checks with JSON output', 'security', '$users = Get-LocalUser | Select-Object Name, Enabled, LastLogon; $services = Get-Service | Where-Object {$_.Status -eq \"Running\" -and $_.Name -like \"*Remote*\"} | Select-Object Name, Status; @{Users=$users; RemoteServices=$services} | ConvertTo-Json -Depth 3', '[]', '[\'security\', \'audit\', \'users\', \'services\']', '1.0', 'System', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        
        ('sys-process-list', 'Get Running Processes', 'Lists all running processes with resource usage', 'system', 'Get-Process | Select-Object Name, Id, CPU, WorkingSet, @{Name=\"Memory_MB\";Expression={[math]::Round($_.WorkingSet/1MB,2)}} | Sort-Object CPU -Descending | Select-Object -First $Count | ConvertTo-Json', '[{\"name\":\"Count\",\"type\":\"number\",\"default\":\"20\",\"description\":\"Number of top processes to show\",\"required\":false}]', '[\'processes\', \'performance\', \'monitoring\']', '1.0', 'System', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        
        ('sys-service-status', 'Get Service Status', 'Check status of Windows services', 'system', 'Get-Service | Group-Object Status | Select-Object Name, Count | ConvertTo-Json', '[]', '[\'services\', \'status\', \'monitoring\']', '1.0', 'System', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
    ''',
    'down': '''
        DROP TABLE IF EXISTS powershell_commands;
    '''
}