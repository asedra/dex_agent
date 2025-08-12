from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import datetime
import logging
import json

from ...core.database import db_manager
from ...core.auth import verify_token
from ...core.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/agents/{agent_id}/services")
async def get_agent_services(
    agent_id: str,
    filter: Optional[str] = Query(None, description="Filter services by name or display name"),
    token: str = Depends(verify_token)
):
    """Get list of Windows services from agent"""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Execute PowerShell command to get services - simplified version
        ps_command = """
        Get-Service"""
        if filter:
            ps_command += f" | Where-Object {{$_.Name -like '*{filter}*' -or $_.DisplayName -like '*{filter}*'}}"
        ps_command += """ | ForEach-Object {
            [PSCustomObject]@{
                name = $_.Name
                display_name = $_.DisplayName
                status = $_.Status.ToString()
                start_type = $_.StartType.ToString()
                can_stop = $_.CanStop
                can_pause_and_continue = $_.CanPauseAndContinue
                dependencies = @($_.ServicesDependedOn | Select-Object -ExpandProperty Name)
                dependent_services = @($_.DependentServices | Select-Object -ExpandProperty Name)
            }
        } | ConvertTo-Json -Depth 3"""
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            try:
                # Handle both old format (output) and new format (data)
                if "data" in response:
                    services_data = response.get("data", [])
                else:
                    output = response.get("output", "[]")
                    services_data = json.loads(output) if output else []
                
                if not isinstance(services_data, list):
                    services_data = [services_data]  # Single service result
                    
                return {
                    "services": services_data,
                    "total": len(services_data),
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat()
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse service data: {str(e)}, output: {output}")
                raise HTTPException(status_code=500, detail="Failed to parse service data")
        else:
            raise HTTPException(status_code=500, detail="Failed to get services from agent")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting services from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/agents/{agent_id}/services/{service_name}")
async def get_service_details(
    agent_id: str,
    service_name: str,
    token: str = Depends(verify_token)
):
    """Get details of a specific Windows service"""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Execute PowerShell command to get specific service details - with WMI for extra details
        ps_command = f"""
        $service = Get-Service -Name '{service_name}'
        $wmiService = Get-CimInstance -ClassName Win32_Service -Filter "Name='{service_name}'"
        [PSCustomObject]@{{
            name = $service.Name
            display_name = $service.DisplayName
            status = $service.Status.ToString()
            start_type = $service.StartType.ToString()
            service_type = $service.ServiceType.ToString()
            can_stop = $service.CanStop
            can_pause_and_continue = $service.CanPauseAndContinue
            description = $wmiService.Description
            path = $wmiService.PathName
            account_name = $wmiService.StartName
            process_id = $wmiService.ProcessId
            dependencies = @($service.ServicesDependedOn | Select-Object -ExpandProperty Name)
            dependent_services = @($service.DependentServices | Select-Object -ExpandProperty Name)
        }} | ConvertTo-Json -Depth 3
        """
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            try:
                # Handle both old format (output) and new format (data)
                if "data" in response:
                    service_data = response.get("data", {})
                else:
                    output = response.get("output", "{}")
                    service_data = json.loads(output)
                
                if not service_data:
                    raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
                    
                return service_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse service data: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to parse service data")
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            if "Cannot find any service with service name" in error_msg:
                raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
            raise HTTPException(status_code=500, detail=f"Failed to get service details: {error_msg}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service details for {service_name} from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/agents/{agent_id}/services/{service_name}/dependencies")
async def get_service_dependencies(
    agent_id: str,
    service_name: str,
    token: str = Depends(verify_token)
):
    """Get service dependencies"""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Execute PowerShell command to get service dependencies
        ps_command = f"""
        $service = Get-Service -Name '{service_name}'
        $dependencies = @{{
            'ServiceName' = $service.Name
            'DependentServices' = @($service.DependentServices | Select-Object Name, Status)
            'ServicesDependedOn' = @($service.ServicesDependedOn | Select-Object Name, Status)
        }}
        $dependencies | ConvertTo-Json -Depth 3
        """
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            try:
                # Handle both old format (output) and new format (data)
                if "data" in response:
                    dependency_data = response.get("data", {})
                else:
                    output = response.get("output", "{}")
                    dependency_data = json.loads(output)
                
                return dependency_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse dependency data: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to parse dependency data")
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            if "Cannot find any service with service name" in error_msg:
                raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
            raise HTTPException(status_code=500, detail=f"Failed to get service dependencies: {error_msg}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dependencies for service {service_name} from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/agents/{agent_id}/services/action")
async def perform_service_action(
    agent_id: str,
    action: Dict[str, str],
    token: str = Depends(verify_token)
):
    """Perform action on Windows service (start, stop, restart, pause, continue)"""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Get service name from request body (required)
        target_service_name = action.get("service_name")
        if not target_service_name:
            raise HTTPException(status_code=400, detail="Service name is required in request body")
        
        action_type = action.get("action", "").lower()
        valid_actions = ["start", "stop", "restart", "pause", "continue"]
        
        if action_type not in valid_actions:
            raise HTTPException(status_code=400, detail=f"Invalid action. Valid actions: {valid_actions}")
        
        # Build PowerShell command based on action with error handling
        if action_type == "start":
            ps_command = f"""
            try {{
                # Check if running as admin
                $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
                if (-not $isAdmin) {{
                    throw "Administrator privileges required to manage services"
                }}
                
                Start-Service -Name '{target_service_name}' -ErrorAction Stop
                Start-Sleep -Seconds 2
                $service = Get-Service -Name '{target_service_name}'
                if ($service.Status -ne 'Running') {{
                    throw "Service failed to start. Current status: $($service.Status)"
                }}
                $service | Select-Object Name, Status | ConvertTo-Json
            }} catch {{
                throw $_
            }}
            """
        elif action_type == "stop":
            ps_command = f"""
            try {{
                # Check if running as admin
                $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
                if (-not $isAdmin) {{
                    throw "Administrator privileges required to stop services"
                }}
                
                $service = Get-Service -Name '{target_service_name}'
                if ($service.Status -eq 'Stopped') {{
                    $service | Select-Object Name, Status | ConvertTo-Json
                    exit 0
                }}
                
                # Check if service can be stopped
                if (-not $service.CanStop) {{
                    throw "Service '{target_service_name}' cannot be stopped"
                }}
                
                Stop-Service -Name '{target_service_name}' -Force -ErrorAction Stop
                Start-Sleep -Seconds 3
                $service = Get-Service -Name '{target_service_name}'
                if ($service.Status -ne 'Stopped') {{
                    throw "Service failed to stop. Current status: $($service.Status)"
                }}
                $service | Select-Object Name, Status | ConvertTo-Json
            }} catch {{
                throw $_
            }}
            """
        elif action_type == "restart":
            ps_command = f"""
            try {{
                # Check if running as admin
                $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
                if (-not $isAdmin) {{
                    throw "Administrator privileges required to restart services"
                }}
                
                Restart-Service -Name '{target_service_name}' -Force -ErrorAction Stop
                Start-Sleep -Seconds 3
                $service = Get-Service -Name '{target_service_name}'
                if ($service.Status -ne 'Running') {{
                    throw "Service failed to restart. Current status: $($service.Status)"
                }}
                $service | Select-Object Name, Status | ConvertTo-Json
            }} catch {{
                throw $_
            }}
            """
        elif action_type == "pause":
            ps_command = f"""
            try {{
                Suspend-Service -Name '{target_service_name}' -ErrorAction Stop
                Start-Sleep -Seconds 2
                $service = Get-Service -Name '{target_service_name}'
                if ($service.Status -ne 'Paused') {{
                    throw "Service failed to pause. Current status: $($service.Status)"
                }}
                $service | Select-Object Name, Status | ConvertTo-Json
            }} catch {{
                throw $_
            }}
            """
        elif action_type == "continue":
            ps_command = f"""
            try {{
                Resume-Service -Name '{target_service_name}' -ErrorAction Stop
                Start-Sleep -Seconds 2
                $service = Get-Service -Name '{target_service_name}'
                if ($service.Status -ne 'Running') {{
                    throw "Service failed to resume. Current status: $($service.Status)"
                }}
                $service | Select-Object Name, Status | ConvertTo-Json
            }} catch {{
                throw $_
            }}
            """
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            try:
                # Handle both old format (output) and new format (data)
                if "data" in response:
                    service_status = response.get("data", {})
                else:
                    output = response.get("output", "{}")
                    service_status = json.loads(output) if output else {}
                
                return {
                    "action": action_type,
                    "service_name": target_service_name,
                    "success": True,
                    "message": f"Service {action_type} action completed successfully",
                    "current_status": service_status.get("Status", "Unknown"),
                    "timestamp": datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                # Action might have succeeded even if status parsing failed
                return {
                    "action": action_type,
                    "service_name": target_service_name,
                    "success": True,
                    "message": f"Service {action_type} action completed",
                    "timestamp": datetime.now().isoformat()
                }
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            if "Cannot find any service with service name" in error_msg:
                raise HTTPException(status_code=404, detail=f"Service '{target_service_name}' not found")
            
            return {
                "action": action_type,
                "service_name": target_service_name,
                "success": False,
                "message": f"Service {action_type} action failed: {error_msg}",
                "timestamp": datetime.now().isoformat()
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing {action.get('action')} on service {target_service_name} from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/agents/{agent_id}/services/{service_name}/config")
async def update_service_config(
    agent_id: str,
    service_name: str,
    config: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Update Windows service configuration"""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Build PowerShell command to update service configuration
        ps_commands = []
        
        # Handle startup type change
        if "startup_type" in config:
            startup_type = config["startup_type"]
            valid_types = ["Automatic", "Manual", "Disabled"]
            if startup_type not in valid_types:
                raise HTTPException(status_code=400, detail=f"Invalid startup type. Valid types: {valid_types}")
            
            ps_commands.append(f"Set-Service -Name '{service_name}' -StartupType {startup_type}")
        
        # Handle description change
        if "description" in config:
            description = config["description"].replace("'", "''")  # Escape single quotes
            ps_commands.append(f"Set-Service -Name '{service_name}' -Description '{description}'")
        
        if not ps_commands:
            raise HTTPException(status_code=400, detail="No valid configuration parameters provided")
        
        # Combine all commands and add status check
        full_command = "; ".join(ps_commands)
        full_command += f"; Get-Service -Name '{service_name}' | Select-Object Name, Status, StartType | ConvertTo-Json"
        
        response = await websocket_manager.execute_command_on_agent(agent_id, full_command)
        
        if response and response.get("success"):
            try:
                # Handle both old format (output) and new format (data)
                if "data" in response:
                    service_status = response.get("data", {})
                else:
                    output = response.get("output", "{}")
                    service_status = json.loads(output) if output else {}
                
                return {
                    "service_name": service_name,
                    "success": True,
                    "message": "Service configuration updated successfully",
                    "current_config": service_status,
                    "timestamp": datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                return {
                    "service_name": service_name,
                    "success": True,
                    "message": "Service configuration updated",
                    "timestamp": datetime.now().isoformat()
                }
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            if "Cannot find any service with service name" in error_msg:
                raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
            
            return {
                "service_name": service_name,
                "success": False,
                "message": f"Service configuration update failed: {error_msg}",
                "timestamp": datetime.now().isoformat()
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating config for service {service_name} from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/agents/{agent_id}/services/batch")
async def perform_batch_service_actions(
    agent_id: str,
    batch_request: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Perform batch actions on multiple services"""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        service_names = batch_request.get("services", [])
        action = batch_request.get("action", "").lower()
        
        if not service_names:
            raise HTTPException(status_code=400, detail="No services specified")
        
        valid_actions = ["start", "stop", "restart", "pause", "continue"]
        if action not in valid_actions:
            raise HTTPException(status_code=400, detail=f"Invalid action. Valid actions: {valid_actions}")
        
        results = []
        
        for service_name in service_names:
            try:
                # Build PowerShell command for this service
                if action == "start":
                    ps_command = f"Start-Service -Name '{service_name}'"
                elif action == "stop":
                    ps_command = f"Stop-Service -Name '{service_name}' -Force"
                elif action == "restart":
                    ps_command = f"Restart-Service -Name '{service_name}' -Force"
                elif action == "pause":
                    ps_command = f"Suspend-Service -Name '{service_name}'"
                elif action == "continue":
                    ps_command = f"Resume-Service -Name '{service_name}'"
                
                response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
                
                if response and response.get("success"):
                    results.append({
                        "service_name": service_name,
                        "action": action,
                        "success": True,
                        "message": f"Service {action} action completed successfully"
                    })
                else:
                    error_msg = response.get("error", "Unknown error") if response else "No response"
                    results.append({
                        "service_name": service_name,
                        "action": action,
                        "success": False,
                        "message": f"Service {action} action failed: {error_msg}"
                    })
            except Exception as e:
                results.append({
                    "service_name": service_name,
                    "action": action,
                    "success": False,
                    "message": f"Error performing action: {str(e)}"
                })
        
        # Calculate summary
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        return {
            "action": action,
            "total_services": len(service_names),
            "successful": successful,
            "failed": failed,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing batch service actions on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")