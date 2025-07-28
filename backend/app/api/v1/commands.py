from typing import List
from fastapi import APIRouter, HTTPException
from ...schemas.command import PowerShellCommand, CommandResponse
from ...schemas.agent import AgentCommand
from ...services.powershell_service import PowerShellService
from ...core.websocket_manager import websocket_manager
from ...core.database import db_manager
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/execute", response_model=CommandResponse)
async def execute_powershell_command(
    command: PowerShellCommand
):
    """Execute a PowerShell command"""
    try:
        result = await PowerShellService.execute_command(
            command=command.command,
            timeout=command.timeout or 30,
            working_directory=command.working_directory,
            run_as_admin=command.run_as_admin or False
        )
        return result
    except Exception as e:
        logger.error(f"Error executing PowerShell command: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute command")

@router.post("/execute/batch", response_model=List[CommandResponse])
async def execute_batch_commands(
    commands: List[PowerShellCommand]
):
    """Execute multiple PowerShell commands"""
    try:
        results = await PowerShellService.execute_batch_commands(commands)
        return results
    except Exception as e:
        logger.error(f"Error executing batch commands: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute batch commands")

@router.post("/agent/{agent_id}/execute")
async def execute_command_on_agent(agent_id: str, command: AgentCommand):
    """Execute command on specific agent via WebSocket"""
    try:
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=404, detail="Agent not connected")
        
        # Send command to agent
        command_data = {
            "command": command.command,
            "timeout": command.timeout or 30,
            "working_directory": command.working_directory
        }
        
        command_id = await websocket_manager.execute_command_on_agent(agent_id, command_data)
        
        return {
            "message": "Command sent to agent successfully",
            "command_id": command_id,
            "agent_id": agent_id
        }
        
    except ValueError as e:
        logger.error(f"Error sending command to agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error sending command to agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send command to agent")

@router.get("/agent/{agent_id}/result/{command_id}")
async def get_command_result(agent_id: str, command_id: str):
    """Get command execution result from agent"""
    try:
        # Get command response
        response = websocket_manager.get_command_response(command_id)
        
        if response is None:
            # Check if command is still pending
            pending_command = websocket_manager.get_pending_command(command_id)
            if pending_command:
                return {
                    "status": "pending",
                    "command_id": command_id,
                    "agent_id": agent_id,
                    "message": "Command is still executing"
                }
            else:
                raise HTTPException(status_code=404, detail="Command not found")
        
        return {
            "status": "completed",
            "command_id": command_id,
            "agent_id": agent_id,
            "result": response
        }
        
    except Exception as e:
        logger.error(f"Error getting command result: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get command result") 