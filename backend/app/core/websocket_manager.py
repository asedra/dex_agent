import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.agent_connections: Dict[str, str] = {}  # agent_id -> connection_id
        self.connection_agents: Dict[str, str] = {}  # connection_id -> agent_id
        self.connection_info: Dict[str, Dict[str, Any]] = {}
        self.pending_commands: Dict[str, Dict[str, Any]] = {}  # command_id -> command_info
        self.command_responses: Dict[str, Dict[str, Any]] = {}  # command_id -> response
    
    async def connect(self, websocket: WebSocket, agent_id: Optional[str] = None, accept: bool = True) -> str:
        """Accept WebSocket connection and return connection ID"""
        if accept:
            await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        
        if agent_id:
            self.agent_connections[agent_id] = connection_id
            self.connection_agents[connection_id] = agent_id
            logger.info(f"Agent {agent_id} mapped to connection {connection_id}")
            logger.info(f"Current agent connections: {list(self.agent_connections.keys())}")
        
        self.connection_info[connection_id] = {
            "connected_at": datetime.now().isoformat(),
            "agent_id": agent_id,
            "last_heartbeat": datetime.now().isoformat()
        }
        
        logger.info(f"WebSocket connected: {connection_id} (Agent: {agent_id})")
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if connection_id in self.connection_agents:
            agent_id = self.connection_agents[connection_id]
            if agent_id in self.agent_connections:
                del self.agent_connections[agent_id]
            del self.connection_agents[connection_id]
        
        if connection_id in self.connection_info:
            del self.connection_info[connection_id]
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {str(e)}")
                self.disconnect(connection_id)
                return False
        return False
    
    async def send_to_agent(self, agent_id: str, message: Dict[str, Any]):
        """Send message to specific agent"""
        if agent_id in self.agent_connections:
            connection_id = self.agent_connections[agent_id]
            return await self.send_message(connection_id, message)
        return False
    
    async def execute_command_on_agent(self, agent_id: str, command: Dict[str, Any]) -> str:
        """Execute command on agent and return command ID"""
        logger.info(f"Attempting to execute command on agent {agent_id}")
        logger.info(f"Connected agents: {list(self.agent_connections.keys())}")
        
        if agent_id not in self.agent_connections:
            logger.error(f"Agent {agent_id} is not connected. Available agents: {list(self.agent_connections.keys())}")
            raise ValueError(f"Agent {agent_id} is not connected")
        
        command_id = f"cmd_{datetime.now().timestamp()}_{uuid.uuid4().hex[:8]}"
        
        # Store command info
        self.pending_commands[command_id] = {
            "agent_id": agent_id,
            "command": command.get("command", ""),
            "timestamp": datetime.now(),
            "status": "pending"
        }
        
        # Send command to agent
        command_message = {
            "type": "command",
            "command_id": command_id,
            "data": {
                **command,
                "command_id": command_id  # Also include command_id in data for agent
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Sending command {command_id} to agent {agent_id}: {command_message}")
        success = await self.send_to_agent(agent_id, command_message)
        if not success:
            del self.pending_commands[command_id]
            logger.error(f"Failed to send command to agent {agent_id}")
            raise ValueError(f"Failed to send command to agent {agent_id}")
        
        logger.info(f"Command {command_id} sent to agent {agent_id}")
        return command_id
    
    def store_command_response(self, command_id: str, response: Dict[str, Any]):
        """Store command response from agent"""
        self.command_responses[command_id] = response
        if command_id in self.pending_commands:
            self.pending_commands[command_id]["status"] = "completed"
            self.pending_commands[command_id]["response"] = response
        
        logger.info(f"Command response stored for {command_id}")
    
    def get_command_response(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get command response"""
        response = self.command_responses.get(command_id)
        if response:
            logger.info(f"Found command response for {command_id}: {response.get('success', False)}")
        else:
            logger.debug(f"No command response found for {command_id}")
        return response
    
    def get_pending_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get pending command info"""
        return self.pending_commands.get(command_id)
    
    async def broadcast(self, message: Dict[str, Any], exclude_connection: Optional[str] = None):
        """Broadcast message to all connections"""
        disconnected = []
        
        for connection_id, websocket in self.active_connections.items():
            if connection_id != exclude_connection:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {str(e)}")
                    disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    def get_connected_agents(self) -> Set[str]:
        """Get set of connected agent IDs"""
        return set(self.agent_connections.keys())
    
    def is_agent_connected(self, agent_id: str) -> bool:
        """Check if agent is connected"""
        return agent_id in self.agent_connections
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection information"""
        return self.connection_info.get(connection_id)
    
    def update_heartbeat(self, connection_id: str):
        """Update last heartbeat time"""
        if connection_id in self.connection_info:
            self.connection_info[connection_id]["last_heartbeat"] = datetime.now().isoformat()
    
    async def request_system_info(self, agent_id: str) -> str:
        """Request system information update from agent"""
        logger.info(f"Requesting system info from agent {agent_id}")
        
        if agent_id not in self.agent_connections:
            logger.error(f"Agent {agent_id} is not connected")
            raise ValueError(f"Agent {agent_id} is not connected")
        
        request_id = f"sysinfo_{datetime.now().timestamp()}_{uuid.uuid4().hex[:8]}"
        
        # Send system info request to agent
        request_message = {
            "type": "system_info_request",
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Sending system info request {request_id} to agent {agent_id}")
        success = await self.send_to_agent(agent_id, request_message)
        
        if not success:
            logger.error(f"Failed to send system info request to agent {agent_id}")
            raise ValueError(f"Failed to send system info request to agent {agent_id}")
        
        return request_id

# Global WebSocket manager instance
websocket_manager = WebSocketManager() 