from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
import json
import datetime
import os
import logging

from ...core.database import db_manager
from ...core.auth import verify_token
from ...core.websocket_manager import websocket_manager
from app.schemas.registry import (
    RegistryKey,
    RegistryValue,
    RegistryValueCreateRequest,
    RegistrySearchRequest,
    RegistryBackupRequest,
    RegistryBackupResponse,
    RegistryImportRequest,
    RegistryExportRequest
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Registry hive mappings
REGISTRY_HIVES = {
    "HKLM": "HKEY_LOCAL_MACHINE",
    "HKCU": "HKEY_CURRENT_USER",
    "HKCR": "HKEY_CLASSES_ROOT",
    "HKU": "HKEY_USERS",
    "HKCC": "HKEY_CURRENT_CONFIG"
}

# Critical registry keys that should be protected
PROTECTED_KEYS = [
    "HKLM\\SYSTEM\\CurrentControlSet\\Control\\SecureBoot",
    "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies",
    "HKLM\\SYSTEM\\CurrentControlSet\\Services\\WinDefend",
    "HKLM\\SOFTWARE\\Microsoft\\Windows Defender"
]

def validate_registry_path(path: str) -> bool:
    """Validate registry path and check if it's not protected"""
    # Normalize path
    normalized_path = path.upper().replace("/", "\\")
    
    # Check if path is in protected list
    for protected in PROTECTED_KEYS:
        if normalized_path.startswith(protected.upper()):
            return False
    
    # Check if path starts with valid hive
    valid_start = any(normalized_path.startswith(hive) for hive in REGISTRY_HIVES.keys())
    valid_start = valid_start or any(normalized_path.startswith(hive) for hive in REGISTRY_HIVES.values())
    
    return valid_start

@router.get("/agents/{agent_id}/registry/keys")
async def get_registry_keys(
    agent_id: str,
    path: str,
    token: str = Depends(verify_token)
):
    """Get registry keys at specified path"""
    try:
        # Check if agent exists and is connected
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        if not validate_registry_path(path):
            raise HTTPException(status_code=403, detail="Access to this registry path is restricted")
        
        # PowerShell command to get registry keys
        ps_command = f"""
        $path = '{path}'
        $keys = @()
        
        try {{
            $items = Get-ChildItem -Path "Registry::$path" -ErrorAction Stop
            foreach ($item in $items) {{
                $keys += @{{
                    Name = $item.PSChildName
                    Path = $item.Name
                    SubKeyCount = (Get-ChildItem -Path $item.PSPath -ErrorAction SilentlyContinue).Count
                    ValueCount = (Get-ItemProperty -Path $item.PSPath -ErrorAction SilentlyContinue).PSObject.Properties.Where({{$_.Name -notlike 'PS*'}}).Count
                }}
            }}
        }} catch {{
            Write-Error $_.Exception.Message
        }}
        
        ConvertTo-Json $keys -Compress
        """
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            output = response.get("output", "[]")
            try:
                keys_data = json.loads(output) if output else []
                if not isinstance(keys_data, list):
                    keys_data = [keys_data]  # Single key result
                
                return keys_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse registry keys data: {str(e)}, output: {output}")
                raise HTTPException(status_code=500, detail="Failed to parse registry keys data")
        else:
            raise HTTPException(status_code=500, detail="Failed to get registry keys from agent")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting registry keys from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/agents/{agent_id}/registry/values")
async def get_registry_values(
    agent_id: str,
    path: str,
    token: str = Depends(verify_token)
):
    """Get registry values at specified path"""
    try:
        # Check if agent exists and is connected
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        if not validate_registry_path(path):
            raise HTTPException(status_code=403, detail="Access to this registry path is restricted")
        
        # PowerShell command to get registry values
        ps_command = f"""
        $path = '{path}'
        $values = @()
        
        try {{
            $properties = Get-ItemProperty -Path "Registry::$path" -ErrorAction Stop
            $properties.PSObject.Properties | Where-Object {{ $_.Name -notlike 'PS*' }} | ForEach-Object {{
                $values += @{{
                    Name = $_.Name
                    Value = $_.Value
                    Type = $_.Value.GetType().Name
                    Data = if ($_.Value -is [byte[]]) {{ [System.Convert]::ToBase64String($_.Value) }} else {{ $_.Value }}
                }}
            }}
        }} catch {{
            Write-Error $_.Exception.Message
        }}
        
        ConvertTo-Json $values -Compress
        """
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            output = response.get("output", "[]")
            try:
                values_data = json.loads(output) if output else []
                if not isinstance(values_data, list):
                    values_data = [values_data]  # Single value result
                
                return values_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse registry values data: {str(e)}, output: {output}")
                raise HTTPException(status_code=500, detail="Failed to parse registry values data")
        else:
            raise HTTPException(status_code=500, detail="Failed to get registry values from agent")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting registry values from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/agents/{agent_id}/registry/values")
async def create_registry_value(
    agent_id: str,
    request: RegistryValueCreateRequest,
    token: str = Depends(verify_token)
):
    """Create or update a registry value"""
    try:
        # Check if agent exists and is connected
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        if not validate_registry_path(request.path):
            raise HTTPException(status_code=403, detail="Access to this registry path is restricted")
    
        # PowerShell command to set registry value
        ps_command = f"""
    $path = '{request.path}'
    $name = '{request.name}'
    $value = '{request.value}'
    $type = '{request.type}'
    
    try {{
        # Create key if it doesn't exist
        if (!(Test-Path "Registry::$path")) {{
            New-Item -Path "Registry::$path" -Force | Out-Null
        }}
        
        # Set the value based on type
        switch ($type) {{
            'String' {{ Set-ItemProperty -Path "Registry::$path" -Name $name -Value $value -Type String }}
            'ExpandString' {{ Set-ItemProperty -Path "Registry::$path" -Name $name -Value $value -Type ExpandString }}
            'Binary' {{ 
                $bytes = [System.Convert]::FromBase64String($value)
                Set-ItemProperty -Path "Registry::$path" -Name $name -Value $bytes -Type Binary 
            }}
            'DWord' {{ Set-ItemProperty -Path "Registry::$path" -Name $name -Value ([int]$value) -Type DWord }}
            'QWord' {{ Set-ItemProperty -Path "Registry::$path" -Name $name -Value ([long]$value) -Type QWord }}
            'MultiString' {{ 
                $values = $value -split ','
                Set-ItemProperty -Path "Registry::$path" -Name $name -Value $values -Type MultiString 
            }}
            default {{ throw "Unsupported value type: $type" }}
        }}
        
        Write-Output "Successfully set registry value"
    }} catch {{
        Write-Error $_.Exception.Message
    }}
        """
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            return {"message": "Registry value created successfully"}
        else:
            error_msg = response.get("error", "Failed to create registry value") if response else "Agent did not respond"
            raise HTTPException(status_code=500, detail=error_msg)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating registry value on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/agents/{agent_id}/registry/values")
async def delete_registry_value(
    agent_id: str,
    path: str,
    name: str,
    token: str = Depends(verify_token)
):
    """Delete a registry value"""
    try:
        # Check if agent exists and is connected
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        if not validate_registry_path(path):
            raise HTTPException(status_code=403, detail="Access to this registry path is restricted")
    
        # PowerShell command to delete registry value
        ps_command = f"""
    $path = '{path}'
    $name = '{name}'
    
    try {{
        Remove-ItemProperty -Path "Registry::$path" -Name $name -Force -ErrorAction Stop
        Write-Output "Successfully deleted registry value"
    }} catch {{
        Write-Error $_.Exception.Message
    }}
        """
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            return {"message": "Registry value deleted successfully"}
        else:
            error_msg = response.get("error", "Failed to delete registry value") if response else "Agent did not respond"
            raise HTTPException(status_code=500, detail=error_msg)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting registry value on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/agents/{agent_id}/registry/keys")
async def delete_registry_key(
    agent_id: str,
    path: str,
    token: str = Depends(verify_token)
):
    """Delete a registry key and all its subkeys"""
    try:
        # Check if agent exists and is connected
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        if not validate_registry_path(path):
            raise HTTPException(status_code=403, detail="Access to this registry path is restricted")
    
        # PowerShell command to delete registry key
        ps_command = f"""
    $path = '{path}'
    
    try {{
        Remove-Item -Path "Registry::$path" -Recurse -Force -ErrorAction Stop
        Write-Output "Successfully deleted registry key"
    }} catch {{
        Write-Error $_.Exception.Message
    }}
        """
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            return {"message": "Registry key deleted successfully"}
        else:
            error_msg = response.get("error", "Failed to delete registry key") if response else "Agent did not respond"
            raise HTTPException(status_code=500, detail=error_msg)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting registry key on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/agents/{agent_id}/registry/search")
async def search_registry(
    agent_id: str,
    request: RegistrySearchRequest,
    token: str = Depends(verify_token)
):
    """Search registry for keys or values"""
    # Validate agent_id format
    if not agent_id:
        raise HTTPException(status_code=400, detail="Agent ID is required")
    
    # Determine search type from boolean flags or direct type
    if request.search_type:
        search_type = request.search_type
    elif request.search_keys and request.search_values:
        search_type = "both"
    elif request.search_keys:
        search_type = "key"
    elif request.search_values:
        search_type = "value"
    else:
        search_type = "both"
    
    # PowerShell command to search registry
    ps_command = f"""
    $searchPath = '{request.search_path}'
    $searchPattern = '{request.pattern}'
    $searchType = '{search_type}'
    $maxResults = {request.max_results or 100}
    $results = @()
    $count = 0
    
    function Search-Registry {{
        param($Path, $Pattern, $Type)
        
        try {{
            if ($Type -eq 'key' -or $Type -eq 'both') {{
                Get-ChildItem -Path "Registry::$Path" -Recurse -ErrorAction SilentlyContinue | 
                Where-Object {{ $_.PSChildName -like "*$Pattern*" -and $count -lt $maxResults }} | 
                ForEach-Object {{
                    $results += @{{
                        Type = 'Key'
                        Path = $_.Name
                        Name = $_.PSChildName
                    }}
                    $count++
                }}
            }}
            
            if ($Type -eq 'value' -or $Type -eq 'both') {{
                Get-ChildItem -Path "Registry::$Path" -Recurse -ErrorAction SilentlyContinue | 
                ForEach-Object {{
                    if ($count -ge $maxResults) {{ return }}
                    $key = $_
                    Get-ItemProperty -Path $key.PSPath -ErrorAction SilentlyContinue | 
                    ForEach-Object {{
                        $_.PSObject.Properties | 
                        Where-Object {{ $_.Name -notlike 'PS*' -and ($_.Name -like "*$Pattern*" -or $_.Value -like "*$Pattern*") }} |
                        ForEach-Object {{
                            if ($count -lt $maxResults) {{
                                $results += @{{
                                    Type = 'Value'
                                    Path = $key.Name
                                    Name = $_.Name
                                    Value = $_.Value
                                }}
                                $count++
                            }}
                        }}
                    }}
                }}
            }}
        }} catch {{
            Write-Warning "Error searching $Path : $_"
        }}
    }}
    
    Search-Registry -Path $searchPath -Pattern $searchPattern -Type $searchType
    ConvertTo-Json $results -Compress
    """
    
    try:
        # Check if agent exists and is connected
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            output = response.get("output", "[]")
            try:
                return json.loads(output) if output else []
            except json.JSONDecodeError:
                logger.error(f"Failed to parse search results: {output}")
                return []
        else:
            error_msg = response.get("error", "Failed to search registry") if response else "Agent did not respond"
            raise HTTPException(status_code=500, detail=error_msg)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching registry on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/agents/{agent_id}/registry/backup")
async def backup_registry(
    agent_id: str,
    request: RegistryBackupRequest,
    token: str = Depends(verify_token)
) -> RegistryBackupResponse:
    """Create a backup of registry path"""
    try:
        # Check if agent exists and is connected
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # PowerShell command to backup registry
        ps_command = f"""
        $path = '{request.path}'
        $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
        $backupFile = "$env:TEMP\\registry_backup_$timestamp.reg"
        
        try {{
            reg export "$path" "$backupFile" /y
            Write-Output $backupFile
        }} catch {{
            Write-Error $_.Exception.Message
        }}
        """
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            backup_filename = response.get("output", "").strip()
            return RegistryBackupResponse(
                backup_file=backup_filename,
                timestamp=datetime.datetime.now(),
                path=request.path
            )
        else:
            error_msg = response.get("error", "Failed to backup registry") if response else "Agent did not respond"
            raise HTTPException(status_code=500, detail=error_msg)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error backing up registry on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/agents/{agent_id}/registry/export")
async def export_registry(
    agent_id: str,
    request: RegistryExportRequest,
    token: str = Depends(verify_token)
):
    """Export registry path to .reg file"""
    # Validate agent_id format
    if not agent_id:
        raise HTTPException(status_code=400, detail="Agent ID is required")
    
    if not validate_registry_path(request.path):
        raise HTTPException(status_code=403, detail="Access to this registry path is restricted")
    
    # PowerShell command to export registry  
    export_file = request.file or request.filename or f"export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.reg"
    ps_command = f"""
    $path = '{request.path}'
    $exportFile = 'C:\\Windows\\Temp\\{export_file}'
    
    try {{
        reg export "$path" "$exportFile" /y
        if (Test-Path $exportFile) {{
            $content = Get-Content $exportFile -Raw
            Remove-Item $exportFile -Force
            Write-Output $content
        }} else {{
            throw "Export failed"
        }}
    }} catch {{
        Write-Error $_.Exception.Message
    }}
    """
    
    try:
        # Check if agent exists and is connected
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            return {
                "content": response.get("output", ""),
                "filename": export_file
            }
        else:
            error_msg = response.get("error", "Failed to export registry") if response else "Agent did not respond"
            raise HTTPException(status_code=500, detail=error_msg)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting registry on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/agents/{agent_id}/registry/import")
async def import_registry(
    agent_id: str,
    request: RegistryImportRequest,
    token: str = Depends(verify_token)
):
    """Import .reg file to registry"""
    try:
        # Check if agent exists and is connected
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Handle both file path and content import
        import_file = f"import_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.reg"
        
        if request.file:
            # Import from file path
            ps_command = f"""
            $importFile = '{request.file}'
            
            try {{
                if (Test-Path $importFile) {{
                    reg import "$importFile" 2>&1
                    Write-Output "Registry import completed successfully"
                }} else {{
                    throw "File not found: $importFile"
                }}
            }} catch {{
                Write-Error $_.Exception.Message
            }}
            """
        elif request.content:
            # Import from content
            ps_command = f"""
            $content = @'
{request.content}
'@
            
            $importFile = 'C:\\Windows\\Temp\\{import_file}'
            
            try {{
                Set-Content -Path $importFile -Value $content -Encoding Unicode
                reg import "$importFile" 2>&1
                Remove-Item $importFile -Force
                Write-Output "Registry import completed successfully"
            }} catch {{
                Write-Error $_.Exception.Message
            }}
            """
        else:
            raise HTTPException(status_code=400, detail="Either file path or content must be provided")
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            return {"message": "Registry import completed successfully"}
        else:
            error_msg = response.get("error", "Failed to import registry") if response else "Agent did not respond"
            raise HTTPException(status_code=500, detail=error_msg)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing registry on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def create_registry_backup(agent_id: str, path: str) -> str:
    """Helper function to create registry backup"""
    backup_filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.reg"
    
    ps_command = f"""
    $path = '{path}'
    $backupFile = 'C:\\Windows\\Temp\\Registry_Backups\\{backup_filename}'
    
    # Create backup directory if it doesn't exist
    $backupDir = Split-Path $backupFile -Parent
    if (!(Test-Path $backupDir)) {{
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    }}
    
    try {{
        reg export "$path" "$backupFile" /y
        Write-Output "Backup created: $backupFile"
    }} catch {{
        Write-Error "Backup failed: $_"
    }}
    """
    
    # Mock backup creation - in real implementation this would execute on agent
    # await ps_service.execute_command(agent_id, ps_command, db)
    
    return backup_filename