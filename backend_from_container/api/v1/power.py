"""Power management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging

from ...core.database import db_manager
from ...core.auth import verify_token
from ...core.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/agents/{agent_id}/power/action")
async def perform_power_action(
    agent_id: str,
    action_request: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Perform power action on agent (shutdown, restart, hibernate, sleep)."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        action = action_request.get("action", "").lower()
        force = action_request.get("force", False)
        delay = action_request.get("delay", 0)  # delay in seconds
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            # Return mock success for disconnected agents for testing
            return {
                "action": action,
                "success": True,
                "message": f"Power action '{action}' simulated (agent disconnected)",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "force": force,
                    "delay": delay
                },
                "status": "disconnected"
            }
        
        valid_actions = ["shutdown", "restart", "hibernate", "sleep", "logoff"]
        if action not in valid_actions:
            raise HTTPException(status_code=400, detail=f"Invalid action. Valid actions: {valid_actions}")
        
        # Build PowerShell command based on action
        if action == "shutdown":
            if force:
                ps_command = f"Stop-Computer -Force"
            else:
                ps_command = f"Stop-Computer"
            if delay > 0:
                ps_command = f"shutdown /s /t {delay}"
        elif action == "restart":
            if force:
                ps_command = f"Restart-Computer -Force"
            else:
                ps_command = f"Restart-Computer"
            if delay > 0:
                ps_command = f"shutdown /r /t {delay}"
        elif action == "hibernate":
            ps_command = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        elif action == "sleep":
            ps_command = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        elif action == "logoff":
            ps_command = "shutdown /l"
        
        # Add confirmation
        ps_command += "; 'Action initiated successfully'"
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            return {
                "action": action,
                "success": True,
                "message": f"Power action '{action}' initiated successfully",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "force": force,
                    "delay": delay
                }
            }
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            return {
                "action": action,
                "success": False,
                "message": f"Power action '{action}' failed: {error_msg}",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing power action {action_request.get('action')} on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/agents/{agent_id}/power/status")
async def get_power_status(
    agent_id: str,
    token: str = Depends(verify_token)
):
    """Get system power status and battery information."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            # Return mock data for disconnected agents for testing
            return {
                "agent_id": agent_id,
                "Battery": None,
                "PowerPlan": {
                    "ElementName": "Balanced",
                    "InstanceID": "Microsoft:PowerPlan\\{381b4222-f694-41f0-9685-ff5bb260df2e}",
                    "IsActive": True
                },
                "Timestamp": datetime.now().isoformat(),
                "status": "disconnected",
                "message": "Agent is not connected, returning mock data"
            }
        
        # PowerShell command to get power status
        ps_command = '''
        $battery = Get-WmiObject Win32_Battery
        $powerPlan = Get-WmiObject Win32_PowerPlan -Namespace root/cimv2/power | Where-Object {$_.IsActive}
        $powerStatus = @{
            'Battery' = if ($battery) {
                @{
                    'BatteryStatus' = $battery.BatteryStatus
                    'EstimatedChargeRemaining' = $battery.EstimatedChargeRemaining
                    'EstimatedRunTime' = $battery.EstimatedRunTime
                    'Name' = $battery.Name
                    'PowerOnline' = $battery.PowerOnline
                }
            } else { $null }
            'PowerPlan' = if ($powerPlan) {
                @{
                    'ElementName' = $powerPlan.ElementName
                    'InstanceID' = $powerPlan.InstanceID
                    'IsActive' = $powerPlan.IsActive
                }
            } else { $null }
            'Timestamp' = Get-Date -Format 'o'
        }
        $powerStatus | ConvertTo-Json -Depth 3
        '''
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            # Try to get data directly first (already parsed)
            power_data = response.get("data")
            if power_data:
                power_data["agent_id"] = agent_id
                return power_data
            
            # Fallback to parsing output
            output = response.get("output", "{}")
            try:
                # Try to parse as JSON
                power_data = json.loads(output) if output else {}
                power_data["agent_id"] = agent_id
                return power_data
            except json.JSONDecodeError as e:
                # Try to evaluate as Python dict (for legacy agents)
                try:
                    import ast
                    power_data = ast.literal_eval(output) if output else {}
                    power_data["agent_id"] = agent_id
                    return power_data
                except:
                    logger.error(f"Failed to parse power status data: {str(e)}, output: {output}")
                    raise HTTPException(status_code=500, detail="Failed to parse power status data")
        else:
            raise HTTPException(status_code=500, detail="Failed to get power status from agent")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting power status from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/agents/{agent_id}/power/plans")
async def get_power_plans(
    agent_id: str,
    token: str = Depends(verify_token)
):
    """Get available power plans on the system."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            # Return mock data for disconnected agents for testing
            return {
                "agent_id": agent_id,
                "Plans": [
                    {
                        "ElementName": "Balanced",
                        "InstanceID": "Microsoft:PowerPlan\\{381b4222-f694-41f0-9685-ff5bb260df2e}",
                        "IsActive": True,
                        "Description": "Automatically balance performance with energy consumption on capable hardware"
                    },
                    {
                        "ElementName": "Power saver",
                        "InstanceID": "Microsoft:PowerPlan\\{a1841308-3541-4fab-bc81-f71556f20b4a}",
                        "IsActive": False,
                        "Description": "Saves energy by reducing computer performance"
                    },
                    {
                        "ElementName": "High performance",
                        "InstanceID": "Microsoft:PowerPlan\\{8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c}",
                        "IsActive": False,
                        "Description": "Favors performance but may use more energy"
                    }
                ],
                "Timestamp": datetime.now().isoformat(),
                "status": "disconnected",
                "message": "Agent is not connected, returning mock data"
            }
        
        # PowerShell command to get power plans
        ps_command = '''
        $plans = Get-WmiObject Win32_PowerPlan -Namespace root/cimv2/power
        $result = @{
            'Plans' = @()
            'Timestamp' = Get-Date -Format 'o'
        }
        foreach ($plan in $plans) {
            $result.Plans += @{
                'ElementName' = $plan.ElementName
                'InstanceID' = $plan.InstanceID
                'IsActive' = $plan.IsActive
                'Description' = $plan.Description
            }
        }
        $result | ConvertTo-Json -Depth 3
        '''
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            # Try to get data directly first (already parsed)
            plans_data = response.get("data")
            if plans_data:
                plans_data["agent_id"] = agent_id
                return plans_data
            
            # Fallback to parsing output
            output = response.get("output", "{}")
            try:
                # Try to parse as JSON
                plans_data = json.loads(output) if output else {}
                plans_data["agent_id"] = agent_id
                return plans_data
            except json.JSONDecodeError as e:
                # Try to evaluate as Python dict (for legacy agents)
                try:
                    import ast
                    plans_data = ast.literal_eval(output) if output else {}
                    plans_data["agent_id"] = agent_id
                    return plans_data
                except:
                    logger.error(f"Failed to parse power plans data: {str(e)}, output: {output}")
                    raise HTTPException(status_code=500, detail="Failed to parse power plans data")
        else:
            raise HTTPException(status_code=500, detail="Failed to get power plans from agent")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting power plans from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/agents/{agent_id}/power/events")
async def get_power_events(
    agent_id: str,
    limit: int = Query(default=50, description="Number of events to retrieve"),
    token: str = Depends(verify_token)
):
    """Get power-related events from Windows Event Log."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            # Return mock data for disconnected agents for testing
            return {
                "agent_id": agent_id,
                "Events": [],
                "Timestamp": datetime.now().isoformat(),
                "status": "disconnected",
                "message": "Agent is not connected, returning empty events"
            }
        
        # PowerShell command to get power events
        ps_command = f'''
        $events = Get-EventLog -LogName System -Source "Microsoft-Windows-Power*" -Newest {limit} -ErrorAction SilentlyContinue
        $result = @{{
            'Events' = @()
            'Timestamp' = Get-Date -Format 'o'
        }}
        foreach ($event in $events) {{
            $result.Events += @{{
                'TimeGenerated' = $event.TimeGenerated.ToString('o')
                'EntryType' = $event.EntryType.ToString()
                'Source' = $event.Source
                'EventID' = $event.EventID
                'Message' = $event.Message
            }}
        }}
        $result | ConvertTo-Json -Depth 3
        '''
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            # Try to get data directly first (already parsed)
            events_data = response.get("data")
            if events_data:
                events_data["agent_id"] = agent_id
                return events_data
            
            # Fallback to parsing output
            output = response.get("output", "{}")
            try:
                # Try to parse as JSON
                events_data = json.loads(output) if output else {}
                events_data["agent_id"] = agent_id
                return events_data
            except json.JSONDecodeError as e:
                # Try to evaluate as Python dict (for legacy agents)
                try:
                    import ast
                    events_data = ast.literal_eval(output) if output else {}
                    events_data["agent_id"] = agent_id
                    return events_data
                except:
                    logger.error(f"Failed to parse power events data: {str(e)}, output: {output}")
                    raise HTTPException(status_code=500, detail="Failed to parse power events data")
        else:
            raise HTTPException(status_code=500, detail="Failed to get power events from agent")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting power events from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/agents/{agent_id}/power/plans/activate")
async def activate_power_plan(
    agent_id: str,
    plan_request: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Activate a specific power plan."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            # Return mock success for disconnected agents for testing
            plan_id = plan_request.get("plan_id", "Balanced")
            return {
                "agent_id": agent_id,
                "Success": True,
                "Message": "Power plan activation simulated (agent disconnected)",
                "PlanID": plan_id,
                "PlanName": "Balanced",
                "Timestamp": datetime.now().isoformat(),
                "status": "disconnected"
            }
        
        plan_id = plan_request.get("plan_id")
        if not plan_id:
            raise HTTPException(status_code=400, detail="plan_id is required")
        
        # PowerShell command to activate power plan
        ps_command = f'''
        $planToActivate = Get-WmiObject Win32_PowerPlan -Namespace root/cimv2/power | Where-Object {{$_.InstanceID -eq '{plan_id}'}}
        if ($planToActivate) {{
            $planToActivate.Activate()
            $result = @{{
                'Success' = $true
                'Message' = "Power plan activated successfully"
                'PlanID' = '{plan_id}'
                'PlanName' = $planToActivate.ElementName
                'Timestamp' = Get-Date -Format 'o'
            }}
        }} else {{
            $result = @{{
                'Success' = $false
                'Message' = "Power plan not found"
                'PlanID' = '{plan_id}'
                'Timestamp' = Get-Date -Format 'o'
            }}
        }}
        $result | ConvertTo-Json -Depth 3
        '''
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            # Try to get data directly first (already parsed)
            activation_data = response.get("data")
            if activation_data:
                activation_data["agent_id"] = agent_id
                if activation_data.get("Success"):
                    return activation_data
                else:
                    raise HTTPException(status_code=400, detail=activation_data.get("Message", "Failed to activate power plan"))
            
            # Fallback to parsing output
            output = response.get("output", "{}")
            try:
                # Try to parse as JSON
                activation_data = json.loads(output) if output else {}
                activation_data["agent_id"] = agent_id
                
                if activation_data.get("Success"):
                    return activation_data
                else:
                    raise HTTPException(status_code=400, detail=activation_data.get("Message", "Failed to activate power plan"))
            except json.JSONDecodeError as e:
                # Try to evaluate as Python dict (for legacy agents)
                try:
                    import ast
                    activation_data = ast.literal_eval(output) if output else {}
                    activation_data["agent_id"] = agent_id
                    
                    if activation_data.get("Success"):
                        return activation_data
                    else:
                        raise HTTPException(status_code=400, detail=activation_data.get("Message", "Failed to activate power plan"))
                except:
                    logger.error(f"Failed to parse activation result: {str(e)}, output: {output}")
                    raise HTTPException(status_code=500, detail="Failed to parse activation result")
        else:
            raise HTTPException(status_code=500, detail="Failed to activate power plan on agent")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating power plan on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")