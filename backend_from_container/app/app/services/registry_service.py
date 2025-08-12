"""Registry Service for Windows Registry operations via PowerShell"""
import json
import logging
from typing import Dict, List, Any, Optional
from app.services.powershell_service import PowerShellService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class RegistryService:
    """Service for Windows Registry operations"""
    
    def __init__(self):
        self.ps_service = PowerShellService()
        
    async def get_registry_tree(self, agent_id: int, root_path: str, db: Session, depth: int = 2) -> Dict:
        """Get registry tree structure up to specified depth"""
        ps_command = f"""
        function Get-RegistryTree {{
            param(
                [string]$Path,
                [int]$CurrentDepth,
                [int]$MaxDepth
            )
            
            $node = @{{
                Name = Split-Path $Path -Leaf
                Path = $Path
                Type = 'key'
                Children = @()
            }}
            
            if ($CurrentDepth -lt $MaxDepth) {{
                try {{
                    $subKeys = Get-ChildItem -Path "Registry::$Path" -ErrorAction SilentlyContinue
                    foreach ($subKey in $subKeys) {{
                        $childNode = Get-RegistryTree -Path $subKey.Name -CurrentDepth ($CurrentDepth + 1) -MaxDepth $MaxDepth
                        $node.Children += $childNode
                    }}
                }} catch {{
                    # Ignore access denied errors
                }}
            }}
            
            return $node
        }}
        
        $tree = Get-RegistryTree -Path '{root_path}' -CurrentDepth 0 -MaxDepth {depth}
        ConvertTo-Json $tree -Depth 10 -Compress
        """
        
        result = await self.ps_service.execute_command(agent_id, ps_command, db)
        if result.get("error"):
            logger.error(f"Error getting registry tree: {result['error']}")
            return {}
            
        try:
            return json.loads(result.get("output", "{}"))
        except json.JSONDecodeError:
            logger.error("Failed to parse registry tree JSON")
            return {}
    
    async def get_registry_value_types(self, agent_id: int, db: Session) -> List[str]:
        """Get supported registry value types"""
        return [
            "String",
            "ExpandString", 
            "Binary",
            "DWord",
            "QWord",
            "MultiString"
        ]
    
    async def validate_registry_value(self, value_type: str, value: Any) -> bool:
        """Validate registry value based on type"""
        try:
            if value_type == "DWord":
                # DWord must be 32-bit integer
                int_val = int(value)
                return 0 <= int_val <= 4294967295
            elif value_type == "QWord":
                # QWord must be 64-bit integer
                int_val = int(value)
                return 0 <= int_val <= 18446744073709551615
            elif value_type == "Binary":
                # Binary must be base64 encoded
                import base64
                base64.b64decode(value)
                return True
            elif value_type in ["String", "ExpandString"]:
                # String types accept any string
                return isinstance(value, str)
            elif value_type == "MultiString":
                # MultiString accepts comma-separated values
                return isinstance(value, str)
            else:
                return False
        except Exception:
            return False
    
    async def get_common_registry_paths(self) -> Dict[str, List[Dict]]:
        """Get common registry paths for quick navigation"""
        return {
            "System": [
                {
                    "name": "Run (Current User)",
                    "path": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    "description": "Programs that run at user login"
                },
                {
                    "name": "Run (Local Machine)",
                    "path": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    "description": "Programs that run at system startup"
                },
                {
                    "name": "Uninstall",
                    "path": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
                    "description": "Installed programs information"
                },
                {
                    "name": "Environment Variables",
                    "path": "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
                    "description": "System environment variables"
                }
            ],
            "Network": [
                {
                    "name": "Network Profiles",
                    "path": "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\Profiles",
                    "description": "Network connection profiles"
                },
                {
                    "name": "TCP/IP Parameters",
                    "path": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters",
                    "description": "TCP/IP configuration"
                }
            ],
            "Security": [
                {
                    "name": "Windows Defender",
                    "path": "HKLM\\SOFTWARE\\Microsoft\\Windows Defender",
                    "description": "Windows Defender settings"
                },
                {
                    "name": "Firewall Rules",
                    "path": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\SharedAccess\\Parameters\\FirewallPolicy",
                    "description": "Windows Firewall configuration"
                }
            ],
            "User": [
                {
                    "name": "Desktop",
                    "path": "HKCU\\Control Panel\\Desktop",
                    "description": "Desktop settings"
                },
                {
                    "name": "Explorer",
                    "path": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer",
                    "description": "Windows Explorer settings"
                }
            ]
        }
    
    async def create_registry_snapshot(self, agent_id: int, paths: List[str], db: Session) -> Dict:
        """Create a snapshot of registry paths for comparison"""
        ps_command = """
        param($Paths)
        
        $snapshot = @{}
        
        foreach ($path in $Paths) {
            try {
                $snapshot[$path] = @{
                    Keys = @()
                    Values = @{}
                }
                
                # Get subkeys
                $keys = Get-ChildItem -Path "Registry::$path" -ErrorAction SilentlyContinue
                foreach ($key in $keys) {
                    $snapshot[$path].Keys += $key.PSChildName
                }
                
                # Get values
                $props = Get-ItemProperty -Path "Registry::$path" -ErrorAction SilentlyContinue
                $props.PSObject.Properties | Where-Object { $_.Name -notlike 'PS*' } | ForEach-Object {
                    $snapshot[$path].Values[$_.Name] = @{
                        Value = $_.Value
                        Type = $_.Value.GetType().Name
                    }
                }
            } catch {
                # Ignore errors for inaccessible paths
            }
        }
        
        ConvertTo-Json $snapshot -Depth 5 -Compress
        """
        
        ps_command_full = f"""
        $paths = @({','.join([f"'{p}'" for p in paths])})
        {ps_command}
        """
        
        result = await self.ps_service.execute_command(agent_id, ps_command_full, db)
        if result.get("error"):
            logger.error(f"Error creating registry snapshot: {result['error']}")
            return {}
            
        try:
            return json.loads(result.get("output", "{}"))
        except json.JSONDecodeError:
            logger.error("Failed to parse registry snapshot JSON")
            return {}
    
    async def compare_registry_snapshots(self, snapshot1: Dict, snapshot2: Dict) -> Dict:
        """Compare two registry snapshots and return differences"""
        differences = {
            "added_keys": {},
            "removed_keys": {},
            "added_values": {},
            "removed_values": {},
            "modified_values": {}
        }
        
        all_paths = set(snapshot1.keys()) | set(snapshot2.keys())
        
        for path in all_paths:
            if path in snapshot1 and path not in snapshot2:
                # Path was removed
                differences["removed_keys"][path] = snapshot1[path]["Keys"]
            elif path not in snapshot1 and path in snapshot2:
                # Path was added
                differences["added_keys"][path] = snapshot2[path]["Keys"]
            else:
                # Path exists in both, check for differences
                old_keys = set(snapshot1[path]["Keys"])
                new_keys = set(snapshot2[path]["Keys"])
                
                # Check for key changes
                added = new_keys - old_keys
                removed = old_keys - new_keys
                
                if added:
                    differences["added_keys"][path] = list(added)
                if removed:
                    differences["removed_keys"][path] = list(removed)
                
                # Check for value changes
                old_values = snapshot1[path]["Values"]
                new_values = snapshot2[path]["Values"]
                
                all_value_names = set(old_values.keys()) | set(new_values.keys())
                
                for value_name in all_value_names:
                    if value_name in old_values and value_name not in new_values:
                        if path not in differences["removed_values"]:
                            differences["removed_values"][path] = []
                        differences["removed_values"][path].append(value_name)
                    elif value_name not in old_values and value_name in new_values:
                        if path not in differences["added_values"]:
                            differences["added_values"][path] = []
                        differences["added_values"][path].append({
                            "name": value_name,
                            "value": new_values[value_name]
                        })
                    elif old_values[value_name]["Value"] != new_values[value_name]["Value"]:
                        if path not in differences["modified_values"]:
                            differences["modified_values"][path] = []
                        differences["modified_values"][path].append({
                            "name": value_name,
                            "old_value": old_values[value_name],
                            "new_value": new_values[value_name]
                        })
        
        return differences
    
    async def restore_registry_from_backup(self, agent_id: int, backup_file: str, db: Session) -> Dict:
        """Restore registry from a backup file"""
        ps_command = f"""
        $backupFile = '{backup_file}'
        
        try {{
            if (Test-Path $backupFile) {{
                reg import "$backupFile" 2>&1
                Write-Output "Registry restored from backup successfully"
            }} else {{
                throw "Backup file not found: $backupFile"
            }}
        }} catch {{
            Write-Error $_.Exception.Message
        }}
        """
        
        result = await self.ps_service.execute_command(agent_id, ps_command, db)
        return result