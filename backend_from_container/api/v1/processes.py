"""Process management API endpoints."""
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


@router.get("/agents/{agent_id}/processes/")
async def get_processes(
    agent_id: str,
    sort_by: str = Query("cpu_percent", description="Sort by field"),
    sort_desc: bool = Query(True, description="Sort descending"),
    filter_name: Optional[str] = Query(None, description="Filter by process name"),
    filter_user: Optional[str] = Query(None, description="Filter by user"),
    include_system: bool = Query(True, description="Include system processes"),
    limit: Optional[int] = Query(None, description="Limit results"),
    token: str = Depends(verify_token)
):
    """Get list of processes from agent."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Build PowerShell command to get processes
        ps_command = "Get-Process | Select-Object Id, Name, CPU, WorkingSet, VirtualMemorySize, Handles, StartTime, UserName"
        
        # Add filtering
        if filter_name:
            ps_command += f" | Where-Object {{$_.Name -like '*{filter_name}*'}}"
        
        if filter_user:
            ps_command += f" | Where-Object {{$_.UserName -like '*{filter_user}*'}}"
        
        # Add sorting
        valid_sort_fields = ["Id", "Name", "CPU", "WorkingSet", "VirtualMemorySize", "Handles"]
        if sort_by in valid_sort_fields:
            ps_command += f" | Sort-Object {sort_by}"
            if sort_desc:
                ps_command += " -Descending"
        
        # Add limit
        if limit:
            ps_command += f" | Select-Object -First {limit}"
        
        ps_command += " | ConvertTo-Json"
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            output = response.get("output", "[]")
            try:
                processes_data = json.loads(output) if output else []
                if not isinstance(processes_data, list):
                    processes_data = [processes_data]  # Single process result
                
                return {
                    "processes": processes_data,
                    "total": len(processes_data),
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "filters": {
                        "name": filter_name,
                        "user": filter_user,
                        "include_system": include_system
                    }
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse process data: {str(e)}, output: {output}")
                raise HTTPException(status_code=500, detail="Failed to parse process data")
        else:
            raise HTTPException(status_code=500, detail="Failed to get processes from agent")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processes from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/agents/{agent_id}/processes/tree")
async def get_process_tree(
    agent_id: str,
    token: str = Depends(verify_token)
):
    """Get process tree from agent."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # PowerShell command to get process tree with parent-child relationships
        ps_command = '''
        $processes = Get-CimInstance Win32_Process | Select-Object ProcessId, Name, ParentProcessId, CommandLine, CreationDate, WorkingSetSize
        $processTree = @{}
        
        foreach ($proc in $processes) {
            $processTree[[string]$proc.ProcessId] = @{
                'Id' = $proc.ProcessId
                'Name' = $proc.Name
                'ParentId' = $proc.ParentProcessId
                'CommandLine' = $proc.CommandLine
                'CreationDate' = $proc.CreationDate
                'WorkingSetSize' = $proc.WorkingSetSize
                'Children' = @()
            }
        }
        
        # Build parent-child relationships
        foreach ($proc in $processTree.Values) {
            if ($proc.ParentId -and $processTree.ContainsKey([string]$proc.ParentId)) {
                $processTree[[string]$proc.ParentId].Children += $proc.Id
            }
        }
        
        $processTree | ConvertTo-Json -Depth 5
        '''
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            output = response.get("output", "{}")
            try:
                tree_data = json.loads(output) if output else {}
                
                return {
                    "process_tree": tree_data,
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat()
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse process tree data: {str(e)}, output: {output}")
                raise HTTPException(status_code=500, detail="Failed to parse process tree data")
        else:
            raise HTTPException(status_code=500, detail="Failed to get process tree from agent")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting process tree from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/agents/{agent_id}/processes/kill")
async def kill_process(
    agent_id: str,
    request: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Kill a process on the agent."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        process_id = request.get("process_id") or request.get("pid")
        force = request.get("force", False)
        
        if not process_id:
            raise HTTPException(status_code=400, detail="process_id or pid is required")
        
        # Build PowerShell command to kill process
        if force:
            ps_command = f"Stop-Process -Id {process_id} -Force; $?"
        else:
            ps_command = f"Stop-Process -Id {process_id}; $?"
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            output = response.get("output", "False")
            success = output.strip().lower() in ["true", "$true"]
            
            return {
                "process_id": process_id,
                "success": success,
                "message": "Process killed successfully" if success else "Failed to kill process",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            return {
                "process_id": process_id,
                "success": False,
                "message": f"Failed to kill process: {error_msg}",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error killing process {request.get('process_id')} on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/agents/{agent_id}/processes/priority")
async def set_process_priority(
    agent_id: str,
    request: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Set process priority on the agent."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        process_id = request.get("process_id") or request.get("pid")
        priority = request.get("priority")
        
        if not process_id:
            raise HTTPException(status_code=400, detail="process_id or pid is required")
        if not priority:
            raise HTTPException(status_code=400, detail="priority is required")
        
        # Normalize priority case and validate
        priority_map = {
            "idle": "Idle",
            "belownormal": "BelowNormal", 
            "below_normal": "BelowNormal",
            "normal": "Normal",
            "abovenormal": "AboveNormal",
            "above_normal": "AboveNormal", 
            "high": "High",
            "realtime": "RealTime",
            "real_time": "RealTime"
        }
        normalized_priority = priority_map.get(priority.lower(), priority)
        valid_priorities = ["Idle", "BelowNormal", "Normal", "AboveNormal", "High", "RealTime"]
        if normalized_priority not in valid_priorities:
            raise HTTPException(status_code=400, detail=f"Invalid priority. Valid values: {valid_priorities}")
        
        priority = normalized_priority
        
        # Build PowerShell command to set process priority
        ps_command = f"""
        $process = Get-Process -Id {process_id} -ErrorAction SilentlyContinue
        if ($process) {{
            $process.PriorityClass = '{priority}'
            $?
        }} else {{
            $false
        }}
        """
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            output = response.get("output", "False")
            success = output.strip().lower() in ["true", "$true"]
            
            return {
                "process_id": process_id,
                "priority": priority,
                "success": success,
                "message": "Process priority set successfully" if success else "Failed to set process priority",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            return {
                "process_id": process_id,
                "priority": priority,
                "success": False,
                "message": f"Failed to set process priority: {error_msg}",
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting priority for process {request.get('process_id')} on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/agents/{agent_id}/processes/suspend-resume")
async def suspend_resume_process(
    agent_id: str,
    request: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Suspend or resume a process on the agent."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        process_id = request.get("process_id") or request.get("pid")
        action = request.get("action", "").lower()
        
        if not process_id:
            raise HTTPException(status_code=400, detail="process_id or pid is required")
        
        valid_actions = ["suspend", "resume"]
        if action not in valid_actions:
            raise HTTPException(status_code=400, detail=f"Invalid action. Valid actions: {valid_actions}")
        
        # Note: Windows doesn't have built-in suspend/resume for processes like Linux
        # This would require using Windows API calls or third-party tools
        # For now, we'll return a message indicating this limitation
        
        return {
            "process_id": process_id,
            "action": action,
            "success": False,
            "message": "Process suspend/resume functionality requires additional Windows API integration",
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suspending/resuming process {request.get('process_id')} on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")