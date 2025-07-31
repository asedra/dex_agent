from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from ...schemas.command import (
    PowerShellCommand, 
    CommandResponse, 
    SavedPowerShellCommand,
    PowerShellCommandExecution,
    BatchCommandExecution
)
from ...schemas.agent import AgentCommand
from ...services.powershell_service import PowerShellService
from ...core.websocket_manager import websocket_manager
from ...core.database import db_manager
from ...core.auth import verify_token
import logging
import asyncio
import uuid
from datetime import datetime

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
        logger.error(f"Error getting command result for {command_id}: {str(e)}")
        logger.error(f"Command response exists: {response is not None if 'response' in locals() else 'response not set'}")
        logger.error(f"Available command responses: {list(websocket_manager.command_responses.keys())}")
        raise HTTPException(status_code=500, detail=f"Failed to get command result: {str(e)}")

# Saved Commands Management

@router.get("/saved", response_model=List[SavedPowerShellCommand])
async def get_saved_commands(token: str = Depends(verify_token)):
    """Get all saved PowerShell commands"""
    try:
        # Get saved commands from database
        commands = db_manager.get_all_saved_commands()
        return commands
    except Exception as e:
        logger.error(f"Error getting saved commands: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get saved commands")

@router.post("/saved", response_model=SavedPowerShellCommand)
async def create_saved_command(command: SavedPowerShellCommand, token: str = Depends(verify_token)):
    """Create a new saved PowerShell command"""
    try:
        # Generate ID and timestamps
        command.id = str(uuid.uuid4())
        command.created_at = datetime.now()
        command.updated_at = datetime.now()
        
        # Save to database
        success = db_manager.save_powershell_command(command.dict())
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save command")
        
        return command
    except Exception as e:
        logger.error(f"Error creating saved command: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create saved command")

@router.get("/saved/{command_id}", response_model=SavedPowerShellCommand)
async def get_saved_command(command_id: str, token: str = Depends(verify_token)):
    """Get a specific saved PowerShell command"""
    try:
        command = db_manager.get_saved_command(command_id)
        if not command:
            raise HTTPException(status_code=404, detail="Command not found")
        return SavedPowerShellCommand(**command)
    except Exception as e:
        logger.error(f"Error getting saved command {command_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get saved command")

@router.put("/saved/{command_id}", response_model=SavedPowerShellCommand)
async def update_saved_command(command_id: str, command: SavedPowerShellCommand, token: str = Depends(verify_token)):
    """Update a saved PowerShell command"""
    try:
        # Check if command exists
        existing = db_manager.get_saved_command(command_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Command not found")
        
        # Update fields
        command.id = command_id
        command.updated_at = datetime.now()
        command.created_at = existing.get('created_at', datetime.now())
        
        # Update in database
        success = db_manager.update_saved_command(command_id, command.dict())
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update command")
        
        return command
    except Exception as e:
        logger.error(f"Error updating saved command {command_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update saved command")

@router.delete("/saved/{command_id}")
async def delete_saved_command(command_id: str, token: str = Depends(verify_token)):
    """Delete a saved PowerShell command"""
    try:
        # Check if command exists
        existing = db_manager.get_saved_command(command_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Command not found")
        
        # Don't allow deletion of system commands
        if existing.get('is_system', False):
            raise HTTPException(status_code=403, detail="Cannot delete system commands")
        
        # Delete from database
        success = db_manager.delete_saved_command(command_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete command")
        
        return {"message": "Command deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting saved command {command_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete saved command")

class CommandExecutionRequest(BaseModel):
    agent_ids: List[str] = Field(..., description="Target agent IDs")  
    parameters: dict = Field(default_factory=dict, description="Parameter values")
    timeout: Optional[int] = Field(30, description="Execution timeout")

@router.post("/saved/{command_id}/execute")
async def execute_saved_command(
    command_id: str, 
    execution: CommandExecutionRequest, 
    token: str = Depends(verify_token)
):
    """Execute a saved PowerShell command on specified agents"""
    try:
        # Get the saved command
        saved_command = db_manager.get_saved_command(command_id)
        if not saved_command:
            raise HTTPException(status_code=404, detail="Command not found")
        
        # Replace parameters in command template
        command_text = saved_command['command']
        for param_name, param_value in execution.parameters.items():
            command_text = command_text.replace(f"${param_name}", str(param_value))
        
        # Execute on each agent
        results = []
        for agent_id in execution.agent_ids:
            if not websocket_manager.is_agent_connected(agent_id):
                results.append({
                    "agent_id": agent_id,
                    "success": False,
                    "error": "Agent not connected"
                })
                continue
            
            try:
                # Send PowerShell command to agent using PowerShell-specific method
                from uuid import uuid4
                from datetime import datetime
                
                request_id = f"ps_{datetime.now().timestamp()}_{uuid4().hex[:8]}"
                
                # Send PowerShell command message directly
                powershell_message = {
                    "type": "powershell_command",
                    "request_id": request_id,
                    "command": command_text,
                    "timeout": execution.timeout or 30,
                    "timestamp": datetime.now().isoformat()
                }
                
                success = await websocket_manager.send_to_agent(agent_id, powershell_message)
                if not success:
                    raise ValueError("Failed to send PowerShell command to agent")
                
                command_execution_id = request_id
                
                results.append({
                    "agent_id": agent_id,
                    "command_id": command_execution_id,
                    "status": "sent",
                    "message": "Command sent to agent successfully"
                })
                
            except Exception as e:
                results.append({
                    "agent_id": agent_id,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "command_id": command_id,
            "command_name": saved_command['name'],
            "executed_command": command_text,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error executing saved command {command_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute saved command") 