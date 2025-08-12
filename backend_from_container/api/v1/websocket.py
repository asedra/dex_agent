import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from ...core.websocket_manager import websocket_manager
from ...core.database import db_manager
from ...schemas.agent import WebSocketMessage, AgentCommand, CommandResult
from ...schemas.terminal import (
    TerminalMessageType,
    TerminalWebSocketMessage,
    TerminalStartRequest,
    TerminalInputMessage,
    TerminalOutputMessage,
    TerminalResizeMessage
)
from ...services.terminal_service import terminal_manager
from ...core.auth import get_current_user
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/agent")
async def agent_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for Python agent communication"""
    connection_id = None
    agent_id = None
    
    try:
        # Accept WebSocket connection first
        await websocket.accept()
        logger.info("New agent WebSocket connection accepted")
        
        # Wait for registration message
        data = await websocket.receive_text()
        message = json.loads(data)
        
        if message.get("type") != "register":
            await websocket.send_text(json.dumps({
                "type": "error",
                "data": {"message": "First message must be registration"}
            }))
            return
        
        # Extract agent info from registration
        agent_data = message.get("data", {})
        agent_id = agent_data.get("id")
        
        if not agent_id:
            await websocket.send_text(json.dumps({
                "type": "error", 
                "data": {"message": "Agent ID required in registration"}
            }))
            return
        
        # Register connection (don't accept again)
        connection_id = await websocket_manager.connect(websocket, agent_id, accept=False)
        
        # Update agent in database
        agent_data["status"] = "online"
        agent_data["last_seen"] = datetime.now().isoformat()
        
        # Ensure IP address is properly set with multiple fallback methods
        if not agent_data.get("ip") or agent_data.get("ip") in ["127.0.0.1", "localhost", None, ""]:
            # Try to get IP from system_info network_adapters first
            system_info = agent_data.get("system_info", {})
            network_adapters = system_info.get("network_adapters", [])
            
            if network_adapters and isinstance(network_adapters, list):
                for adapter in network_adapters:
                    if isinstance(adapter, dict) and adapter.get("ip"):
                        ip = adapter.get("ip")
                        if ip and ip not in ["127.0.0.1", "localhost", "::1"]:
                            agent_data["ip"] = ip
                            logger.info(f"Set agent IP from network adapter: {ip}")
                            break
            
            # If still no valid IP, try system_info primary_ip
            if (not agent_data.get("ip") or agent_data.get("ip") in ["127.0.0.1", "localhost", None, ""]) and system_info.get("primary_ip"):
                primary_ip = system_info.get("primary_ip")
                if primary_ip and primary_ip not in ["127.0.0.1", "localhost", "::1"]:
                    agent_data["ip"] = primary_ip
                    logger.info(f"Set agent IP from system_info primary_ip: {primary_ip}")
            
            # Final fallback: WebSocket client IP
            if not agent_data.get("ip") or agent_data.get("ip") in ["127.0.0.1", "localhost", None, ""]:
                try:
                    # Get client IP from WebSocket connection
                    client_host, client_port = websocket.client.host, websocket.client.port
                    if client_host and client_host not in ["127.0.0.1", "localhost", "::1"]:
                        agent_data["ip"] = client_host
                        logger.info(f"Set agent IP to WebSocket client IP: {client_host}")
                except Exception as e:
                    logger.warning(f"Could not determine client IP from WebSocket: {e}")
        
        db_manager.add_agent(agent_data)
        
        logger.info(f"Agent {agent_id} registered and connected via WebSocket")
        
        # Send welcome message
        welcome_message = {
            "type": "welcome",
            "data": {
                "agent_id": agent_id,
                "connection_id": connection_id,
                "message": "Connected to DexAgents server"
            },
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_message))
        
        # Listen for messages from agent
        while True:
            try:
                # Receive message from agent
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Update heartbeat
                websocket_manager.update_heartbeat(connection_id)
                
                # Handle different message types
                await handle_agent_message(agent_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"Agent {agent_id} disconnected")
                break
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from agent {agent_id}")
                continue
            except Exception as e:
                logger.error(f"Error handling message from agent {agent_id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"WebSocket error for agent {agent_id}: {str(e)}")
    finally:
        # Clean up connection
        if connection_id and agent_id:
            websocket_manager.disconnect(connection_id)
            db_manager.update_agent_status(agent_id, "offline")
            logger.info(f"Agent {agent_id} connection cleaned up")

@router.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for agent communication"""
    connection_id = None
    
    try:
        # Accept the WebSocket connection
        connection_id = await websocket_manager.connect(websocket, agent_id)
        
        # Update agent connection status and ensure IP is set if missing
        agent_data = db_manager.get_agent(agent_id)
        if agent_data and (not agent_data.get("ip") or agent_data.get("ip") in ["127.0.0.1", "localhost", None, ""]):
            # Try to get IP from agent's system_info first
            system_info = agent_data.get("system_info", {})
            network_adapters = system_info.get("network_adapters", [])
            ip_updated = False
            
            if network_adapters and isinstance(network_adapters, list):
                for adapter in network_adapters:
                    if isinstance(adapter, dict) and adapter.get("ip"):
                        ip = adapter.get("ip")
                        if ip and ip not in ["127.0.0.1", "localhost", "::1"]:
                            db_manager.update_agent(agent_id, {"ip": ip})
                            logger.info(f"Updated agent {agent_id} IP from network adapter: {ip}")
                            ip_updated = True
                            break
            
            # Try system_info primary_ip if no network adapter IP found
            if not ip_updated and system_info.get("primary_ip"):
                primary_ip = system_info.get("primary_ip")
                if primary_ip and primary_ip not in ["127.0.0.1", "localhost", "::1"]:
                    db_manager.update_agent(agent_id, {"ip": primary_ip})
                    logger.info(f"Updated agent {agent_id} IP from system_info primary_ip: {primary_ip}")
                    ip_updated = True
            
            # Final fallback: WebSocket client IP
            if not ip_updated:
                try:
                    # Get client IP from WebSocket connection
                    client_host, client_port = websocket.client.host, websocket.client.port
                    if client_host and client_host not in ["127.0.0.1", "localhost", "::1"]:
                        db_manager.update_agent(agent_id, {"ip": client_host})
                        logger.info(f"Updated agent {agent_id} IP to WebSocket client IP: {client_host}")
                except Exception as e:
                    logger.warning(f"Could not determine client IP from WebSocket for agent {agent_id}: {e}")
        
        db_manager.update_agent_connection(agent_id, connection_id, True)
        
        logger.info(f"Agent {agent_id} connected via WebSocket")
        
        # Send welcome message
        welcome_message = {
            "type": "welcome",
            "data": {
                "agent_id": agent_id,
                "connection_id": connection_id,
                "message": "Connected to DexAgents server"
            },
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_message))
        
        # Listen for messages from agent
        while True:
            try:
                # Receive message from agent
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Update heartbeat
                websocket_manager.update_heartbeat(connection_id)
                
                # Handle different message types
                await handle_agent_message(agent_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"Agent {agent_id} disconnected")
                break
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from agent {agent_id}")
                continue
            except Exception as e:
                logger.error(f"Error handling message from agent {agent_id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"WebSocket error for agent {agent_id}: {str(e)}")
    finally:
        # Clean up connection
        if connection_id:
            websocket_manager.disconnect(connection_id)
            db_manager.update_agent_connection(agent_id, None, False)
            logger.info(f"Agent {agent_id} connection cleaned up")

async def handle_agent_message(agent_id: str, message: Dict[str, Any]):
    """Handle messages from agent"""
    try:
        # Debug log the raw message
        logger.info(f"Raw message from agent {agent_id}: {type(message)} - {message}")
        
        # If message is string, try to parse as JSON
        if isinstance(message, str):
            try:
                message = json.loads(message)
                logger.info(f"Parsed JSON message: {message}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON message from agent {agent_id}: {e}")
                return
        
        message_type = message.get("type")
    except Exception as e:
        logger.error(f"Error handling message from agent {agent_id}: {e}")
        logger.error(f"Message type: {type(message)}, content: {message}")
        return
    
    if message_type == "heartbeat":
        # Update agent status with system info
        system_info = message.get("data", {}).get("system_info", {})
        db_manager.update_agent_status(agent_id, "online", system_info)
        
    elif message_type == "command_result":
        # Handle command execution result
        command_result = message.get("data", {})
        command_id = command_result.get("command_id", "") or message.get("command_id", "")
        
        logger.info(f"Command result received from agent {agent_id}, command_id: {command_id}")
        logger.info(f"Command result data: {command_result}")
        
        # Store command response in WebSocket manager
        if command_id:
            # Extract result data - support new Python agent format
            # Handle nested output format - fix for DX-170
            result_data = command_result.get("result", {})
            output_value = result_data.get("output", "") if isinstance(result_data, dict) else str(result_data)
            
            response_data = {
                "success": command_result.get("success", False),
                "output": output_value,
                "error": command_result.get("error", ""),
                "return_code": command_result.get("return_code", 0),
                "execution_time": command_result.get("execution_time", 0.0),
                "timestamp": command_result.get("timestamp", datetime.now().isoformat())
            }
            websocket_manager.store_command_response(command_id, response_data)
            logger.info(f"Command response stored for command_id: {command_id}")
        else:
            logger.warning(f"No command_id in command result from agent {agent_id}")
            
    elif message_type == "powershell_result":
        # Handle PowerShell command result
        request_id = message.get("request_id")
        data = message.get("data", {})
        success = message.get("success", False)
        
        logger.info(f"PowerShell result received from agent {agent_id}, request_id: {request_id}")
        logger.info(f"PowerShell result data: {data}")
        
        if request_id:
            # Format response data for PowerShell results
            # Handle both dict and list data types
            error_msg = ""
            execution_time = 0.0
            output_data = ""
            
            # Default success to True if not explicitly set to False (DX-172 fix)
            if success is None and not message.get("error"):
                success = True
            
            if isinstance(data, dict):
                error_msg = data.get("error", "") if not success else ""
                execution_time = data.get("execution_time", 0.0)
                # Extract output string from nested dict - fix for DX-170
                output_data = data.get("output", "") if "output" in data else str(data)
            elif isinstance(data, str):
                output_data = data
            elif isinstance(data, list):
                # Handle array data directly - DX-172 services fix
                output_data = json.dumps(data)
                success = True  # Array data indicates successful execution
            else:
                # For other types, convert to string
                output_data = str(data)
            
            response_data = {
                "status": "completed",
                "success": success,
                "output": output_data,
                "data": data,  # Also include original data field for newer endpoints - DX-172
                "error": error_msg,
                "execution_time": execution_time,
                "timestamp": message.get("timestamp", datetime.now().isoformat())
            }
            websocket_manager.store_command_response(request_id, response_data)
            logger.info(f"PowerShell response stored for request_id: {request_id}")
        else:
            logger.warning(f"No request_id in PowerShell result from agent {agent_id}")
        
        # Also store in database (ignore database errors for now)
        try:
            db_manager.add_command_history(agent_id, {
                "command": data.get("command", "") if isinstance(data, dict) else "",
                "success": success,
                "output": data,
                "error": error_msg,
                "execution_time": execution_time
            })
        except Exception as e:
            logger.warning(f"Could not store command history in database: {e}")
        
        logger.info(f"PowerShell result processed for agent {agent_id}: {success}")
    
    elif message_type == "system_info_update":
        # Handle system info update from agent
        system_info = message.get("data", {})
        logger.info(f"System info update received from agent {agent_id}: {system_info}")
        
        # Update agent in database with new system info
        try:
            update_data = {
                "system_info": system_info,
                "last_seen": datetime.now().isoformat()
            }
            db_manager.update_agent(agent_id, update_data)
            logger.info(f"Agent {agent_id} system info updated in database")
        except Exception as e:
            logger.error(f"Error updating agent {agent_id} system info: {str(e)}")
    
    elif message_type == "pong":
        # Handle pong response
        logger.debug(f"Pong received from agent {agent_id}")
        
    elif message_type == "register":
        # Handle agent registration - this is redundant for new endpoint but keep for compatibility  
        logger.info(f"Received redundant registration from agent {agent_id}")
        
    elif message_type == "terminal_output":
        # Handle terminal output from agent
        session_id = message.get("session_id")
        output_data = message.get("data", {})
        
        if session_id:
            # Forward output to terminal client
            await terminal_manager.broadcast_to_session_clients(
                session_id=session_id,
                message_type=TerminalMessageType.TERMINAL_OUTPUT,
                data=output_data
            )
            
            # Buffer output for later retrieval if needed
            if "data" in output_data:
                await terminal_manager.buffer_output(session_id, output_data["data"])
        
        logger.debug(f"Terminal output received from agent {agent_id} for session {session_id}")
        
    elif message_type == "terminal_error":
        # Handle terminal error from agent
        session_id = message.get("session_id")
        error_data = message.get("data", {})
        
        if session_id:
            # Forward error to terminal client
            await terminal_manager.broadcast_to_session_clients(
                session_id=session_id,
                message_type=TerminalMessageType.TERMINAL_ERROR,
                data=error_data
            )
        
        logger.error(f"Terminal error from agent {agent_id}: {error_data}")
        
    elif message_type == "terminal_closed":
        # Handle terminal closed notification from agent
        session_id = message.get("session_id")
        
        if session_id:
            # Close the session
            await terminal_manager.close_session(session_id)
        
        logger.info(f"Terminal session {session_id} closed by agent {agent_id}")
        
    else:
        logger.warning(f"Unknown message type from agent {agent_id}: {message_type}")

@router.post("/send/{agent_id}/command")
async def send_command_to_agent(agent_id: str, command: AgentCommand):
    """Send command to specific agent via WebSocket"""
    if not websocket_manager.is_agent_connected(agent_id):
        raise HTTPException(status_code=404, detail="Agent not connected")
    
    # Generate command ID for tracking
    import uuid
    command_id = str(uuid.uuid4())
    
    message = {
        "type": "command",
        "data": {
            "id": command_id,
            "type": getattr(command, 'command_type', 'powershell'),
            "command": command.command,
            "timeout": command.timeout,
            "working_directory": command.working_directory
        },
        "timestamp": datetime.now().isoformat()
    }
    
    success = await websocket_manager.send_to_agent(agent_id, message)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send command to agent")
    
    return {"message": "Command sent to agent", "agent_id": agent_id, "command_id": command_id}

@router.get("/connected")  
async def get_connected_agents():
    """Get list of connected agents"""
    try:
        connected_agents = websocket_manager.get_connected_agents()
        agents_info = []
        
        for agent_id in connected_agents:
            agent_data = db_manager.get_agent(agent_id)
            if agent_data:
                try:
                    connection_info = websocket_manager.get_connection_info(
                        websocket_manager.agent_connections[agent_id]
                    )
                    agent_data["connection_info"] = connection_info
                except Exception as e:
                    logger.warning(f"Could not get connection info for agent {agent_id}: {e}")
                agents_info.append(agent_data)
        
        return {"connected_agents": agents_info, "count": len(agents_info)}
    except Exception as e:
        logger.error(f"Error getting connected agents: {e}")
        return {"connected_agents": [], "count": 0, "error": str(e)}


@router.websocket("/ws/agents/{agent_id}/terminal")
async def terminal_websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for terminal session"""
    session_id = None
    user_id = "admin"  # TODO: Get from authentication token
    
    try:
        # Accept WebSocket connection
        await websocket.accept()
        logger.info(f"New terminal WebSocket connection for agent {agent_id}")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            await websocket.send_text(json.dumps({
                "type": "error",
                "data": {"message": f"Agent {agent_id} is not connected"}
            }))
            await websocket.close()
            return
        
        # Wait for terminal start message
        data = await websocket.receive_text()
        message = json.loads(data)
        
        if message.get("type") != TerminalMessageType.TERMINAL_START:
            await websocket.send_text(json.dumps({
                "type": "error",
                "data": {"message": "First message must be terminal_start"}
            }))
            await websocket.close()
            return
        
        # Extract terminal configuration
        config = message.get("data", {})
        rows = config.get("rows", 24)
        cols = config.get("cols", 80)
        working_directory = config.get("working_directory")
        
        # Create terminal session
        session = await terminal_manager.create_session(
            agent_id=agent_id,
            user_id=user_id,
            websocket=websocket,
            rows=rows,
            cols=cols,
            working_directory=working_directory
        )
        session_id = session.id
        
        # Notify agent to start terminal session
        await terminal_manager.send_to_agent(
            session_id=session_id,
            agent_id=agent_id,
            message_type=TerminalMessageType.TERMINAL_START,
            data={
                "session_id": session_id,
                "rows": rows,
                "cols": cols,
                "working_directory": working_directory
            }
        )
        
        # Send success response to client
        await websocket.send_text(json.dumps({
            "type": "session_created",
            "data": {
                "session_id": session_id,
                "agent_id": agent_id,
                "status": "active"
            }
        }))
        
        # Start cleanup task if not already running
        await terminal_manager.start_cleanup_task()
        
        # Listen for messages from client
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                message_type = message.get("type")
                message_data = message.get("data", {})
                
                if message_type == TerminalMessageType.TERMINAL_INPUT:
                    # Forward input to agent
                    input_data = message_data.get("data", "")
                    
                    # Add command to history if it's a complete command (ends with newline)
                    if input_data.endswith("\r") or input_data.endswith("\n"):
                        command = input_data.strip()
                        if command:
                            await terminal_manager.add_command_to_history(
                                session_id=session_id,
                                command=command,
                                user_id=user_id,
                                agent_id=agent_id
                            )
                    
                    # Send input to agent
                    await terminal_manager.send_to_agent(
                        session_id=session_id,
                        agent_id=agent_id,
                        message_type=TerminalMessageType.TERMINAL_INPUT,
                        data={"data": input_data}
                    )
                    
                elif message_type == TerminalMessageType.TERMINAL_RESIZE:
                    # Handle terminal resize
                    new_rows = message_data.get("rows", rows)
                    new_cols = message_data.get("cols", cols)
                    
                    await terminal_manager.resize_session(session_id, new_rows, new_cols)
                    
                    # Notify agent about resize
                    await terminal_manager.send_to_agent(
                        session_id=session_id,
                        agent_id=agent_id,
                        message_type=TerminalMessageType.TERMINAL_RESIZE,
                        data={"rows": new_rows, "cols": new_cols}
                    )
                    
                elif message_type == TerminalMessageType.TERMINAL_PING:
                    # Respond to ping
                    await websocket.send_text(json.dumps({
                        "type": TerminalMessageType.TERMINAL_PONG,
                        "data": {}
                    }))
                    await terminal_manager.update_session_activity(session_id)
                    
                elif message_type == TerminalMessageType.TERMINAL_CLOSE:
                    # Close terminal session
                    logger.info(f"Closing terminal session {session_id}")
                    break
                    
            except WebSocketDisconnect:
                logger.info(f"Terminal client disconnected for session {session_id}")
                break
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from terminal client")
                continue
            except Exception as e:
                logger.error(f"Error handling terminal message: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Terminal WebSocket error: {str(e)}")
    finally:
        # Clean up session
        if session_id:
            # Notify agent to close terminal
            await terminal_manager.send_to_agent(
                session_id=session_id,
                agent_id=agent_id,
                message_type=TerminalMessageType.TERMINAL_CLOSE,
                data={}
            )
            
            # Close session
            await terminal_manager.close_session(session_id)
            logger.info(f"Terminal session {session_id} cleaned up") 