import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from ...core.websocket_manager import websocket_manager
from ...core.database import db_manager
from ...schemas.agent import WebSocketMessage, AgentCommand, CommandResult
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for agent communication"""
    connection_id = None
    
    try:
        # Accept the WebSocket connection
        connection_id = await websocket_manager.connect(websocket, agent_id)
        
        # Update agent connection status
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
    message_type = message.get("type")
    
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
            # Extract result data - it might be nested
            result_data = command_result.get("result", command_result)
            response_data = {
                "success": result_data.get("success", False),
                "output": result_data.get("output", ""),
                "error": result_data.get("error", ""),
                "execution_time": result_data.get("execution_time", 0.0),
                "timestamp": datetime.now().isoformat()
            }
            websocket_manager.store_command_response(command_id, response_data)
            logger.info(f"Command response stored for command_id: {command_id}")
        else:
            logger.warning(f"No command_id in command result from agent {agent_id}")
        
        # Also store in database (ignore database errors for now)
        try:
            result_data = command_result.get("result", command_result)
            db_manager.add_command_history(agent_id, {
                "command": result_data.get("command", ""),
                "success": result_data.get("success", False),
                "output": result_data.get("output", ""),
                "error": result_data.get("error", ""),
                "execution_time": result_data.get("execution_time", 0.0)
            })
        except Exception as e:
            logger.warning(f"Could not store command history in database: {e}")
        
        logger.info(f"Command result processed for agent {agent_id}: {command_result.get('success', False)}")
        
    elif message_type == "register":
        # Handle agent registration
        agent_data = message.get("data", {})
        agent_data["id"] = agent_id
        agent_data["status"] = "online"
        agent_data["last_seen"] = datetime.now().isoformat()
        
        db_manager.add_agent(agent_data)
        logger.info(f"Agent {agent_id} registered successfully")
        
    else:
        logger.warning(f"Unknown message type from agent {agent_id}: {message_type}")

@router.post("/send/{agent_id}/command")
async def send_command_to_agent(agent_id: str, command: AgentCommand):
    """Send command to specific agent via WebSocket"""
    if not websocket_manager.is_agent_connected(agent_id):
        raise HTTPException(status_code=404, detail="Agent not connected")
    
    message = {
        "type": "command",
        "data": {
            "command": command.command,
            "timeout": command.timeout,
            "working_directory": command.working_directory
        },
        "timestamp": datetime.now().isoformat()
    }
    
    success = await websocket_manager.send_to_agent(agent_id, message)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send command to agent")
    
    return {"message": "Command sent to agent", "agent_id": agent_id}

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