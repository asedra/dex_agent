from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from ...schemas.command import (
    PowerShellCommand, 
    CommandResponse, 
    SavedPowerShellCommand,
    SavedPowerShellCommandUpdate,
    PowerShellCommandExecution,
    BatchCommandExecution,
    AICommandRequest,
    AITestRequest
)
from ...schemas.agent import AgentCommand
from ...services.powershell_service import PowerShellService
from ...core.websocket_manager import websocket_manager
from ...core.database import db_manager
from ...core.auth import verify_token
from ...core.config import settings
from ...services.ai_service import ai_service
import logging
import asyncio
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/execute", response_model=CommandResponse)
async def execute_powershell_command(
    command: PowerShellCommand,
    token: str = Depends(verify_token)
):
    """Execute a PowerShell command locally on the server"""
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
    commands: List[PowerShellCommand],
    token: str = Depends(verify_token)
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
    """Execute command on specific agent via WebSocket and wait for response"""
    try:
        logger.info(f"Received command execution request for agent {agent_id}: {command.command[:100]}...")
        
        # Get list of connected agents for better error reporting
        connected_agents = websocket_manager.get_connected_agents()
        mock_agents = list(websocket_manager.mock_agents.keys()) if hasattr(websocket_manager, 'mock_agents') else []
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            # Provide detailed error information
            error_detail = {
                "error": "Agent is not connected",
                "agent_id": agent_id,
                "message": f"Agent '{agent_id}' is not currently connected to the server",
                "available_agents": list(connected_agents),
                "suggestions": []
            }
            
            # Add helpful suggestions
            if mock_agents:
                error_detail["mock_agents_available"] = mock_agents
                error_detail["suggestions"].append("Use mock agents for testing by setting MOCK_AGENTS=true or ENABLE_TEST_MODE=true")
                
            if not connected_agents and not mock_agents:
                error_detail["suggestions"].extend([
                    "Ensure the agent is running and properly configured",
                    "Check the agent's WebSocket connection to the server", 
                    "For CI/CD testing, enable mock agents with MOCK_AGENTS=true",
                    "Verify the agent ID is correct and matches the registered agent"
                ])
            elif connected_agents:
                error_detail["suggestions"].append(f"Try using one of the available agents: {', '.join(list(connected_agents)[:3])}")
            
            logger.warning(f"Agent {agent_id} not connected. Available: {connected_agents}")
            raise HTTPException(status_code=404, detail=error_detail)
        
        # Log whether this is a mock or real agent
        if websocket_manager.is_mock_agent(agent_id):
            logger.info(f"Executing command on mock agent {agent_id} (test mode)")
        else:
            logger.info(f"Executing command on real agent {agent_id}")
        
        # Send command to agent
        command_data = {
            "command": command.command,
            "timeout": command.timeout or 30,
            "working_directory": command.working_directory
        }
        
        # Execute command and get response
        response = await websocket_manager.execute_command_on_agent(
            agent_id, command.command, "powershell"
        )
        
        # Handle response based on type
        if isinstance(response, dict):
            if not response.get("success", True):
                logger.error(f"Command execution failed: {response}")
                return {
                    "success": False,
                    "command_id": None,
                    "agent_id": agent_id,
                    "message": response.get("error", "Command execution failed"),
                    "error": response.get("error", "Unknown error"),
                    "status": "error",
                    "is_mock": websocket_manager.is_mock_agent(agent_id)
                }
            else:
                # Successful response
                return {
                    "success": response.get("success", True),
                    "command_id": response.get("command_id"),
                    "agent_id": agent_id,
                    "output": response.get("output", ""),
                    "error": response.get("error", ""),
                    "exit_code": response.get("exit_code", 0),
                    "execution_time": response.get("execution_time", None),
                    "timestamp": response.get("timestamp"),
                    "status": "completed",
                    "is_mock": websocket_manager.is_mock_agent(agent_id)
                }
        
        # Fallback for unexpected response format
        logger.warning(f"Unexpected response format from agent {agent_id}: {response}")
        return {
            "success": False,
            "command_id": None,
            "agent_id": agent_id,
            "message": "Received unexpected response format from agent",
            "error": f"Response: {str(response)[:200]}...",
            "status": "error",
            "is_mock": websocket_manager.is_mock_agent(agent_id)
        }
        
    except ValueError as e:
        logger.error(f"ValueError executing command on agent {agent_id}: {str(e)}")
        error_msg = str(e)
        if "not connected" in error_msg.lower():
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": "Agent connection error",
                    "message": error_msg,
                    "agent_id": agent_id,
                    "troubleshooting": [
                        "Verify the agent is running and connected",
                        "Check WebSocket connection status",
                        "Enable mock agents for testing: MOCK_AGENTS=true"
                    ]
                }
            )
        else:
            raise HTTPException(status_code=400, detail={"error": "Invalid request", "message": error_msg})
            
    except asyncio.TimeoutError:
        logger.error(f"Command execution timed out for agent {agent_id}")
        raise HTTPException(
            status_code=408, 
            detail={
                "error": "Command execution timeout", 
                "message": f"Command execution timed out after {command.timeout or 30} seconds",
                "agent_id": agent_id,
                "troubleshooting": [
                    "Try increasing the timeout value",
                    "Check if the command is resource-intensive",
                    "Verify agent is responsive"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error executing command on agent {agent_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Internal server error",
                "message": "Failed to execute command on agent",
                "agent_id": agent_id,
                "details": str(e) if settings.TESTING else "Contact system administrator"
            }
        )

@router.post("/agent/{agent_id}/execute/async")
async def execute_command_on_agent_async(agent_id: str, command: AgentCommand):
    """Execute command on specific agent via WebSocket (async - don't wait for response)"""
    try:
        logger.info(f"Received async command execution request for agent {agent_id}: {command.command[:100]}...")
        
        # Get list of connected agents for better error reporting
        connected_agents = websocket_manager.get_connected_agents()
        mock_agents = list(websocket_manager.mock_agents.keys()) if hasattr(websocket_manager, 'mock_agents') else []
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            # Provide detailed error information
            error_detail = {
                "error": "Agent is not connected",
                "agent_id": agent_id,
                "message": f"Agent '{agent_id}' is not currently connected to the server",
                "available_agents": list(connected_agents),
                "suggestions": []
            }
            
            # Add helpful suggestions
            if mock_agents:
                error_detail["mock_agents_available"] = mock_agents
                error_detail["suggestions"].append("Use mock agents for testing by setting MOCK_AGENTS=true or ENABLE_TEST_MODE=true")
                
            if not connected_agents and not mock_agents:
                error_detail["suggestions"].extend([
                    "Ensure the agent is running and properly configured",
                    "Check the agent's WebSocket connection to the server", 
                    "For CI/CD testing, enable mock agents with MOCK_AGENTS=true",
                    "Verify the agent ID is correct and matches the registered agent"
                ])
            elif connected_agents:
                error_detail["suggestions"].append(f"Try using one of the available agents: {', '.join(list(connected_agents)[:3])}")
            
            logger.warning(f"Agent {agent_id} not connected for async command. Available: {connected_agents}")
            raise HTTPException(status_code=404, detail=error_detail)
        
        # Log whether this is a mock or real agent
        if websocket_manager.is_mock_agent(agent_id):
            logger.info(f"Sending async command to mock agent {agent_id} (test mode)")
            # For mock agents, generate a fake command ID since they don't use real command tracking
            command_id = f"mock_async_{datetime.now().timestamp()}_{uuid.uuid4().hex[:8]}"
        else:
            logger.info(f"Sending async command to real agent {agent_id}")
            command_id = f"async_{datetime.now().timestamp()}_{uuid.uuid4().hex[:8]}"
        
        # Send command to agent
        command_data = {
            "command": command.command,
            "timeout": command.timeout or 30,
            "working_directory": command.working_directory
        }
        
        # Send message to agent (for real agents) or simulate for mock agents
        success = await websocket_manager.send_to_agent(agent_id, {
            "type": "powershell_command",
            "request_id": command_id,
            "command": command.command,
            "timeout": command.timeout or 30,
            "timestamp": datetime.now().isoformat(),
            "async": True  # Mark as async execution
        })
        
        if not success and not websocket_manager.is_mock_agent(agent_id):
            raise HTTPException(
                status_code=500, 
                detail={
                    "error": "Failed to send command",
                    "message": "Could not deliver command to agent",
                    "agent_id": agent_id
                }
            )
        
        return {
            "message": "Command sent to agent successfully",
            "command_id": command_id,
            "agent_id": agent_id,
            "status": "sent",
            "is_mock": websocket_manager.is_mock_agent(agent_id),
            "note": "This is an async execution - use GET /api/v1/commands/agent/{agent_id}/result/{command_id} to check status"
        }
        
    except ValueError as e:
        logger.error(f"ValueError sending async command to agent {agent_id}: {str(e)}")
        error_msg = str(e)
        if "not connected" in error_msg.lower():
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": "Agent connection error",
                    "message": error_msg,
                    "agent_id": agent_id,
                    "troubleshooting": [
                        "Verify the agent is running and connected",
                        "Check WebSocket connection status",
                        "Enable mock agents for testing: MOCK_AGENTS=true"
                    ]
                }
            )
        else:
            raise HTTPException(status_code=400, detail={"error": "Invalid request", "message": error_msg})
            
    except Exception as e:
        logger.error(f"Unexpected error sending async command to agent {agent_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Internal server error",
                "message": "Failed to send command to agent",
                "agent_id": agent_id,
                "details": str(e) if settings.TESTING else "Contact system administrator"
            }
        )

@router.get("/agent/{agent_id}/result/{command_id}")
async def get_command_result(agent_id: str, command_id: str):
    """Get command execution result from agent"""
    try:
        logger.info(f"Retrieving command result for {command_id} on agent {agent_id}")
        
        # Check if agent exists (for better error reporting)
        if not websocket_manager.is_agent_connected(agent_id) and not websocket_manager.is_mock_agent(agent_id):
            logger.warning(f"Requesting result for command {command_id} but agent {agent_id} is not connected")
        
        # Get command response
        response = websocket_manager.get_command_response(command_id)
        
        if response is None:
            # Check if command is still pending
            pending_command = websocket_manager.get_pending_command(command_id)
            if pending_command:
                logger.info(f"Command {command_id} is still pending execution")
                return {
                    "status": "pending",
                    "command_id": command_id,
                    "agent_id": agent_id,
                    "message": "Command is still executing",
                    "submitted_at": pending_command.get("timestamp"),
                    "command": pending_command.get("command", "")[:100] + "..." if len(pending_command.get("command", "")) > 100 else pending_command.get("command", "")
                }
            else:
                # Command not found - provide helpful information
                available_commands = list(websocket_manager.command_responses.keys())
                pending_commands = list(websocket_manager.pending_commands.keys())
                
                logger.warning(f"Command {command_id} not found. Available: {len(available_commands)}, Pending: {len(pending_commands)}")
                
                error_detail = {
                    "error": "Command not found",
                    "command_id": command_id,
                    "agent_id": agent_id,
                    "message": f"No command result found for ID '{command_id}'",
                    "troubleshooting": [
                        "Verify the command ID is correct",
                        "Check if the command has expired or was cleaned up",
                        "Ensure the command was submitted successfully"
                    ]
                }
                
                if available_commands:
                    error_detail["available_commands"] = available_commands[-5:]  # Show last 5 commands
                    error_detail["troubleshooting"].append("Try using one of the available command IDs")
                
                if pending_commands:
                    error_detail["pending_commands"] = pending_commands[-5:]  # Show last 5 pending
                    error_detail["troubleshooting"].append("Command might still be in the pending queue")
                
                raise HTTPException(status_code=404, detail=error_detail)
        
        # Command completed - return result
        logger.info(f"Found completed command result for {command_id}: success={response.get('success', False)}")
        
        return {
            "status": "completed",
            "command_id": command_id,
            "agent_id": agent_id,
            "result": response,
            "is_mock": websocket_manager.is_mock_agent(agent_id),
            "retrieved_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
        
    except Exception as e:
        logger.error(f"Error getting command result for {command_id}: {str(e)}", exc_info=True)
        
        # Provide debug info in testing mode
        debug_info = {}
        if settings.TESTING:
            debug_info = {
                "available_responses": len(websocket_manager.command_responses),
                "pending_commands": len(websocket_manager.pending_commands),
                "response_keys": list(websocket_manager.command_responses.keys())[-3:],  # Last 3
                "pending_keys": list(websocket_manager.pending_commands.keys())[-3:]   # Last 3
            }
        
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Internal server error",
                "message": "Failed to retrieve command result", 
                "command_id": command_id,
                "agent_id": agent_id,
                "details": str(e) if settings.TESTING else "Contact system administrator",
                **debug_info
            }
        )

# Saved Commands Management

@router.get("/saved", response_model=List[SavedPowerShellCommand])
async def get_saved_commands(
    include_test_commands: bool = True,
    token: str = Depends(verify_token)
):
    """Get all saved PowerShell commands
    
    Args:
        include_test_commands: Include test commands (default: True). 
                              Set to False to exclude Testing category and 'Test Command' names.
    """
    try:
        # Get saved commands from database
        commands = db_manager.get_all_saved_commands(include_test_commands=include_test_commands)
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
async def update_saved_command(command_id: str, command_update: SavedPowerShellCommandUpdate, token: str = Depends(verify_token)):
    """Update a saved PowerShell command (partial update supported)"""
    try:
        # Check if command exists
        existing = db_manager.get_saved_command(command_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Command not found")
        
        # Merge updates with existing data
        update_data = command_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                existing[key] = value
        
        # Update metadata
        existing['id'] = command_id
        existing['updated_at'] = datetime.now()
        
        # Update in database
        success = db_manager.update_saved_command(command_id, existing)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update command")
        
        return SavedPowerShellCommand(**existing)
    except HTTPException:
        raise
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
        
        # Get command parameters definition from saved command
        command_parameters = saved_command.get('parameters', [])
        
        # Auto-detect parameters from command text if definitions are missing
        import re
        
        # Find all $variables but exclude PowerShell built-in variables
        all_dollar_vars = re.findall(r'\$(\w+)', command_text)
        
        # PowerShell built-in and system variables to exclude
        builtin_vars = {
            '_', 'null', 'true', 'false', 'this', 'input', 'matches', 
            'lastexitcode', 'error', 'executioncontext', 'foreach', 'switch',
            'profile', 'pshome', 'psversion', 'pwd', 'args', 'home', 'host',
            'myinvocation', 'ofs', 'shellid', 'stacktrace',
            # Common script variables to exclude (lowercase for comparison)
            'result', 'results', 'output', 'data', 'item', 'items',
            'remoteservices', 'secprocs', 'services', 'users', 'processes',
            'securityprocesses', 'temp', 'tmp', 'obj', 'object'
        }
        
        # Only include custom parameters (not built-in PowerShell variables)
        detected_params = [param for param in all_dollar_vars if param.lower() not in builtin_vars]
        
        # Create a comprehensive parameters dict with intelligent defaults
        complete_parameters = {}
        
        # Default values for common PowerShell parameters
        default_param_values = {
            'LogName': 'System',
            'Level': 'Error',
            'Count': '10',
            'ComputerName': 'localhost',
            'Path': 'C:\\',
            'Service': 'Spooler',
            'ProcessName': 'explorer',
            'Drive': 'C:',
            'Directory': 'C:\\',
            'EventID': '1000',
            'Source': 'Application',
            'Days': '7',
            'Hours': '24',
            'Minutes': '60',
            'Size': '100MB',
            'Top': '10',
            'Limit': '100'
        }
        
        # If we have parameter definitions, use them
        if command_parameters:
            for param in command_parameters:
                param_name = param.get('name', '')
                if param_name in execution.parameters and execution.parameters[param_name]:
                    # Use provided value
                    complete_parameters[param_name] = execution.parameters[param_name]
                elif param.get('default'):
                    # Use parameter's default value
                    complete_parameters[param_name] = param.get('default')
                elif param_name in default_param_values:
                    # Use intelligent default
                    complete_parameters[param_name] = default_param_values[param_name]
                else:
                    # Use empty string as fallback
                    complete_parameters[param_name] = ''
        else:
            # No parameter definitions - use auto-detected parameters with intelligent defaults
            for param_name in detected_params:
                if param_name in execution.parameters and execution.parameters[param_name]:
                    # Use provided value
                    complete_parameters[param_name] = execution.parameters[param_name]
                elif param_name in default_param_values:
                    # Use intelligent default
                    complete_parameters[param_name] = default_param_values[param_name]
                else:
                    # Use empty string as fallback
                    complete_parameters[param_name] = ''
        
        # Replace all parameters in command text
        for param_name, param_value in complete_parameters.items():
            command_text = command_text.replace(f"${param_name}", str(param_value))
        
        # Log the parameter substitution for debugging
        logger.info(f"Command: {saved_command['name']}")
        logger.info(f"Original: {saved_command['command']}")
        logger.info(f"Detected params: {detected_params}")
        logger.info(f"Complete params: {complete_parameters}")
        logger.info(f"Final command: {command_text}")
        
        # Execute on each agent
        results = []
        for agent_id in execution.agent_ids:
            if not websocket_manager.is_agent_connected(agent_id):
                # Provide detailed error information for disconnected agents
                error_info = {
                    "agent_id": agent_id,
                    "success": False,
                    "error": "Agent not connected",
                    "message": f"Agent '{agent_id}' is not currently connected to the server",
                    "is_mock": websocket_manager.is_mock_agent(agent_id)
                }
                
                # Add suggestions for agent connection issues
                connected_agents = websocket_manager.get_connected_agents()
                if connected_agents:
                    error_info["suggestions"] = [f"Try using connected agents: {', '.join(list(connected_agents)[:3])}"]
                elif hasattr(websocket_manager, 'mock_agents') and websocket_manager.mock_agents:
                    error_info["suggestions"] = ["Use mock agents for testing by setting MOCK_AGENTS=true"]
                else:
                    error_info["suggestions"] = [
                        "Ensure the agent is running and connected",
                        "Enable mock agents for testing: MOCK_AGENTS=true"
                    ]
                
                results.append(error_info)
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

# AI-Powered Command Generation

class AICommandRequest(BaseModel):
    message: str = Field(..., description="User request for command generation")
    conversation_history: Optional[List[dict]] = Field(default=None, description="Previous conversation messages")

class AITestRequest(BaseModel):
    command: str = Field(..., description="Command to test")
    agent_id: str = Field(..., description="Target agent ID for testing")
    timeout: Optional[int] = Field(30, description="Test timeout in seconds")

@router.post("/ai/generate")
async def generate_command_with_ai(
    request: AICommandRequest,
    token: str = Depends(verify_token)
):
    """Generate PowerShell command using AI based on user request"""
    try:
        if not ai_service.is_available():
            raise HTTPException(
                status_code=503, 
                detail="AI service not available - ChatGPT API key not configured"
            )
        
        result = await ai_service.generate_powershell_command(
            user_request=request.message,
            conversation_history=request.conversation_history
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating command with AI: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate command")

@router.post("/ai/test")
async def test_ai_command(
    request: AITestRequest,
    token: str = Depends(verify_token)
):
    """Test AI-generated command on specified agent"""
    try:
        result = await ai_service.test_command_on_agent(
            command=request.command,
            agent_id=request.agent_id,
            websocket_manager=websocket_manager,
            timeout=request.timeout or 30
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing AI command: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to test command")

@router.get("/ai/status")
async def get_ai_status(token: str = Depends(verify_token)):
    """Get AI service status"""
    return {
        "available": ai_service.is_available(),
        "message": "AI service is available" if ai_service.is_available() else "ChatGPT API key not configured"
    }

# Testing and Mock Agent Management

@router.get("/test/status")
async def get_test_status(token: str = Depends(verify_token)):
    """Get testing configuration and mock agent status"""
    connected_agents = websocket_manager.get_connected_agents()
    mock_agents = getattr(websocket_manager, 'mock_agents', {})
    
    return {
        "testing_enabled": settings.TESTING,
        "mock_agents_enabled": settings.MOCK_AGENTS or settings.ENABLE_TEST_MODE,
        "connected_agents": list(connected_agents),
        "mock_agents": list(mock_agents.keys()),
        "mock_agent_details": mock_agents if settings.TESTING else {},
        "total_agents": len(connected_agents) + len(mock_agents),
        "recommendations": _get_testing_recommendations(connected_agents, mock_agents)
    }

def _get_testing_recommendations(connected_agents: set, mock_agents: dict) -> List[str]:
    """Get recommendations for testing setup"""
    recommendations = []
    
    if not connected_agents and not mock_agents:
        recommendations.extend([
            "No agents available for testing",
            "Enable mock agents with MOCK_AGENTS=true for CI/CD testing",
            "Connect real agents for production testing"
        ])
    elif not connected_agents and mock_agents:
        recommendations.extend([
            "Currently using mock agents only",
            "Good for CI/CD and automated testing", 
            "Consider testing with real agents before deployment"
        ])
    elif connected_agents and not mock_agents:
        recommendations.extend([
            "Real agents connected - good for integration testing",
            "Enable mock agents for consistent CI/CD testing",
            "Mock agents provide faster, predictable responses"
        ])
    else:
        recommendations.extend([
            "Both real and mock agents available",
            "Ideal setup for comprehensive testing",
            "Use mock agents for CI/CD, real agents for integration"
        ])
        
    return recommendations

@router.post("/test/mock-agent")
async def add_mock_agent(
    agent_data: dict, 
    token: str = Depends(verify_token)
):
    """Add a mock agent for testing (only available in test mode)"""
    if not (settings.MOCK_AGENTS or settings.ENABLE_TEST_MODE):
        raise HTTPException(
            status_code=403, 
            detail={
                "error": "Mock agents disabled",
                "message": "Mock agents are not enabled",
                "solution": "Set MOCK_AGENTS=true or ENABLE_TEST_MODE=true to use this feature"
            }
        )
    
    agent_id = agent_data.get("agent_id")
    hostname = agent_data.get("hostname")
    platform = agent_data.get("platform")
    status = agent_data.get("status", "online")
    
    if not agent_id:
        raise HTTPException(
            status_code=400,
            detail={"error": "Missing agent_id", "message": "agent_id is required"}
        )
    
    success = websocket_manager.add_mock_agent(agent_id, hostname, platform, status)
    
    if success:
        return {
            "message": f"Mock agent {agent_id} added successfully",
            "agent_id": agent_id,
            "status": status,
            "is_mock": True
        }
    else:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to add mock agent", "message": "Could not create mock agent"}
        )

@router.delete("/test/mock-agent/{agent_id}")
async def remove_mock_agent(
    agent_id: str, 
    token: str = Depends(verify_token)
):
    """Remove a mock agent (only available in test mode)"""
    if not (settings.MOCK_AGENTS or settings.ENABLE_TEST_MODE):
        raise HTTPException(
            status_code=403, 
            detail={
                "error": "Mock agents disabled",
                "message": "Mock agents are not enabled",
                "solution": "Set MOCK_AGENTS=true or ENABLE_TEST_MODE=true to use this feature"
            }
        )
    
    if not websocket_manager.is_mock_agent(agent_id):
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Mock agent not found",
                "message": f"No mock agent found with ID '{agent_id}'",
                "available_mock_agents": list(getattr(websocket_manager, 'mock_agents', {}).keys())
            }
        )
    
    success = websocket_manager.remove_mock_agent(agent_id)
    
    if success:
        return {
            "message": f"Mock agent {agent_id} removed successfully",
            "agent_id": agent_id
        }
    else:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to remove mock agent", "message": "Could not remove mock agent"}
        )