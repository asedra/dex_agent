"""Insert default software management PowerShell commands."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.database_postgresql import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOFTWARE_COMMANDS = [
    {
        'name': 'Get Installed Software',
        'command': '''Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*,
HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | 
Where-Object { $_.DisplayName } | 
Select-Object DisplayName, DisplayVersion, Publisher, InstallDate, InstallLocation | 
Format-Table -AutoSize''',
        'description': 'List all installed software from Windows Registry',
        'category': 'Software'
    },
    {
        'name': 'Get Windows Store Apps',
        'command': 'Get-AppxPackage | Select-Object Name, Version, Publisher, InstallLocation | Format-Table -AutoSize',
        'description': 'List all Windows Store applications',
        'category': 'Software'
    },
    {
        'name': 'Check Chocolatey Installation',
        'command': '''if (Get-Command choco -ErrorAction SilentlyContinue) {
    choco --version
    Write-Host "Chocolatey is installed"
} else {
    Write-Host "Chocolatey is not installed"
}''',
        'description': 'Check if Chocolatey package manager is installed',
        'category': 'Software'
    },
    {
        'name': 'Install Chocolatey',
        'command': '''Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))''',
        'description': 'Install Chocolatey package manager',
        'category': 'Software'
    },
    {
        'name': 'List Chocolatey Packages',
        'command': 'choco list --local-only',
        'description': 'List installed Chocolatey packages',
        'category': 'Software'
    },
    {
        'name': 'Check Winget Installation',
        'command': '''if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget --version
    Write-Host "Windows Package Manager is installed"
} else {
    Write-Host "Windows Package Manager is not installed"
}''',
        'description': 'Check if Windows Package Manager (winget) is installed',
        'category': 'Software'
    },
    {
        'name': 'List Winget Packages',
        'command': 'winget list',
        'description': 'List installed packages via Windows Package Manager',
        'category': 'Software'
    },
    {
        'name': 'Search Winget Package',
        'command': 'winget search $PackageName',
        'description': 'Search for a package in Windows Package Manager',
        'category': 'Software'
    },
    {
        'name': 'Get Software by Name',
        'command': '''param($SoftwareName)
Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like "*$SoftwareName*" } | 
Select-Object Name, Version, Vendor, InstallDate | Format-Table -AutoSize''',
        'description': 'Find installed software by name using WMI',
        'category': 'Software'
    },
    {
        'name': 'Uninstall Software via WMI',
        'command': '''param($SoftwareName)
$product = Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -eq "$SoftwareName" }
if ($product) {
    $product.Uninstall()
    Write-Host "Uninstalled $SoftwareName successfully"
} else {
    Write-Host "Software $SoftwareName not found"
}''',
        'description': 'Uninstall software using WMI',
        'category': 'Software'
    },
    {
        'name': 'Get Windows Updates',
        'command': '''Get-HotFix | Select-Object Description, HotFixID, InstalledBy, InstalledOn | 
Sort-Object InstalledOn -Descending | Format-Table -AutoSize''',
        'description': 'List installed Windows updates',
        'category': 'Software'
    },
    {
        'name': 'Check Windows Update Status',
        'command': '''$UpdateSession = New-Object -ComObject Microsoft.Update.Session
$UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
$SearchResult = $UpdateSearcher.Search("IsInstalled=0")
Write-Host "Available Updates: $($SearchResult.Updates.Count)"
$SearchResult.Updates | Select-Object Title, Description | Format-Table -AutoSize''',
        'description': 'Check for available Windows updates',
        'category': 'Software'
    },
    {
        'name': 'Install MSI Package',
        'command': '''param($MsiPath, $LogPath = "C:\\Temp\\install.log")
Start-Process msiexec.exe -ArgumentList "/i", "`"$MsiPath`"", "/quiet", "/norestart", "/log", "`"$LogPath`"" -Wait
Get-Content $LogPath -Tail 20''',
        'description': 'Install an MSI package silently',
        'category': 'Software'
    },
    {
        'name': 'Get Software Install Locations',
        'command': '''Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | 
Where-Object { $_.InstallLocation } | 
Select-Object DisplayName, InstallLocation | 
Sort-Object DisplayName | Format-Table -AutoSize''',
        'description': 'List software installation directories',
        'category': 'Software'
    },
    {
        'name': 'Export Installed Software List',
        'command': '''$software = Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*,
HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | 
Where-Object { $_.DisplayName } | 
Select-Object DisplayName, DisplayVersion, Publisher, InstallDate
$software | Export-Csv -Path "C:\\Temp\\installed_software.csv" -NoTypeInformation
Write-Host "Exported $($software.Count) software entries to C:\\Temp\\installed_software.csv"''',
        'description': 'Export installed software list to CSV',
        'category': 'Software'
    },
    {
        'name': 'Check Software Version',
        'command': '''param($SoftwareName)
$software = Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*,
HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | 
Where-Object { $_.DisplayName -like "*$SoftwareName*" } | 
Select-Object DisplayName, DisplayVersion
if ($software) {
    $software | Format-Table -AutoSize
} else {
    Write-Host "Software '$SoftwareName' not found"
}''',
        'description': 'Check version of specific software',
        'category': 'Software'
    },
    {
        'name': 'Get Recently Installed Software',
        'command': '''Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*,
HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | 
Where-Object { $_.DisplayName -and $_.InstallDate } | 
Select-Object DisplayName, DisplayVersion, InstallDate, Publisher | 
Sort-Object InstallDate -Descending | 
Select-Object -First 10 | Format-Table -AutoSize''',
        'description': 'List 10 most recently installed software',
        'category': 'Software'
    },
    {
        'name': 'Check Disk Space for Installation',
        'command': '''Get-PSDrive -PSProvider FileSystem | 
Where-Object { $_.Free -ne $null } | 
Select-Object Name, 
    @{Name="Total(GB)";Expression={[math]::Round($_.Used/1GB + $_.Free/1GB,2)}},
    @{Name="Used(GB)";Expression={[math]::Round($_.Used/1GB,2)}},
    @{Name="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}},
    @{Name="Free(%)";Expression={[math]::Round(($_.Free/($_.Used+$_.Free))*100,2)}} | 
Format-Table -AutoSize''',
        'description': 'Check available disk space for software installation',
        'category': 'Software'
    },
    {
        'name': 'Create Software Install Log',
        'command': '''param($LogMessage, $LogFile = "C:\\Temp\\software_install.log")
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$logEntry = "$timestamp - $LogMessage"
Add-Content -Path $LogFile -Value $logEntry
Write-Host "Logged: $logEntry"''',
        'description': 'Create or append to software installation log',
        'category': 'Software'
    },
    {
        'name': 'Test Software Dependencies',
        'command': '''param($RequiredSoftware)
$missing = @()
foreach ($software in $RequiredSoftware.Split(',')) {
    $installed = Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*,
    HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | 
    Where-Object { $_.DisplayName -like "*$software*" }
    
    if (-not $installed) {
        $missing += $software
    }
}
if ($missing.Count -eq 0) {
    Write-Host "All dependencies are installed" -ForegroundColor Green
} else {
    Write-Host "Missing dependencies: $($missing -join ', ')" -ForegroundColor Red
}''',
        'description': 'Check if required software dependencies are installed',
        'category': 'Software'
    }
]

def insert_software_commands():
    """Insert software management commands into the database."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        inserted = 0
        for cmd in SOFTWARE_COMMANDS:
            # Check if command already exists
            cursor.execute("""
                SELECT id FROM saved_commands 
                WHERE name = %s
            """, (cmd['name'],))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO saved_commands (name, command, description, category)
                    VALUES (%s, %s, %s, %s)
                """, (cmd['name'], cmd['command'], cmd['description'], cmd['category']))
                inserted += 1
                logger.info(f"Inserted command: {cmd['name']}")
            else:
                logger.info(f"Command already exists: {cmd['name']}")
        
        conn.commit()
        logger.info(f"Successfully inserted {inserted} new software commands")
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error inserting software commands: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    insert_software_commands()