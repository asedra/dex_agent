from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from ...schemas.agent import Agent, AgentUpdate, AgentRegister
from ...core.database import db_manager
from ...core.auth import verify_token
from ...core.websocket_manager import websocket_manager
import logging
import socket
import platform
import psutil
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[Agent])
async def get_agents(token: str = Depends(verify_token)):
    """Get all agents"""
    try:
        agents_data = db_manager.get_agents()
        agents = []
        
        for agent_data in agents_data:
            # Check if agent is currently connected
            agent_data['is_connected'] = websocket_manager.is_agent_connected(agent_data['id'])
            agents.append(Agent(**agent_data))
        
        return agents
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, token: str = Depends(verify_token)):
    """Get a specific agent by ID"""
    try:
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is currently connected
        agent_data['is_connected'] = websocket_manager.is_agent_connected(agent_id)
        return Agent(**agent_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/register", response_model=Agent)
async def register_agent(agent_data: AgentRegister, token: str = Depends(verify_token)):
    """Register a new agent"""
    try:
        # Check if agent with same hostname already exists
        existing_agent = db_manager.get_agent_by_hostname(agent_data.hostname)
        if existing_agent:
            # Update existing agent instead of creating new one
            update_data = agent_data.dict(exclude_unset=True)
            update_data['status'] = 'online'
            update_data['last_seen'] = datetime.now().isoformat()
            
            db_manager.update_agent(existing_agent['id'], update_data)
            existing_agent.update(update_data)
            existing_agent['is_connected'] = websocket_manager.is_agent_connected(existing_agent['id'])
            
            logger.info(f"Agent {existing_agent['id']} updated during registration")
            return Agent(**existing_agent)
        
        # Create new agent
        agent_dict = agent_data.dict()
        agent_dict['status'] = 'online'
        agent_dict['last_seen'] = datetime.now().isoformat()
        
        agent_id = db_manager.add_agent(agent_dict)
        agent_dict['id'] = agent_id
        agent_dict['is_connected'] = False  # Will be updated when WebSocket connects
        
        logger.info(f"New agent {agent_id} registered")
        return Agent(**agent_dict)
        
    except Exception as e:
        logger.error(f"Error registering agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, agent_update: AgentUpdate, token: str = Depends(verify_token)):
    """Update an existing agent"""
    try:
        # Get current agent data
        current_agent = db_manager.get_agent(agent_id)
        if not current_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update only provided fields
        update_data = agent_update.dict(exclude_unset=True)
        success = db_manager.update_agent(agent_id, update_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update agent")
        
        # Return updated agent
        updated_agent = db_manager.get_agent(agent_id)
        updated_agent['is_connected'] = websocket_manager.is_agent_connected(agent_id)
        return Agent(**updated_agent)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, token: str = Depends(verify_token)):
    """Delete an agent"""
    try:
        success = db_manager.delete_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"message": "Agent deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{agent_id}/commands", response_model=List[Dict[str, Any]])
async def get_agent_commands(agent_id: str, limit: int = 50, token: str = Depends(verify_token)):
    """Get command history for an agent"""
    try:
        # Verify agent exists
        agent = db_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        commands = db_manager.get_command_history(agent_id, limit)
        return commands
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting commands for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{agent_id}/refresh")
async def refresh_agent(agent_id: str, token: str = Depends(verify_token)):
    """Refresh agent status and return updated agent data"""
    try:
        logger.info(f"Refresh request received for agent {agent_id}")
        
        # Verify agent exists
        agent = db_manager.get_agent(agent_id)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is currently connected via WebSocket
        is_connected = websocket_manager.is_agent_connected(agent_id)
        logger.info(f"Agent {agent_id} connection status: {is_connected}")
        
        # Get current system info if agent is connected
        system_info = None
        if is_connected:
            try:
                # Get basic system information
                
                cpu_usage = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk_usage = {}
                
                # Get disk usage for all mounted drives
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_usage[partition.mountpoint] = round((usage.used / usage.total) * 100, 1)
                    except PermissionError:
                        continue
                
                system_info = {
                    "hostname": platform.node(),
                    "os_version": platform.platform(),
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory.percent,
                    "disk_usage": disk_usage
                }
                
                logger.info(f"Retrieved system info for agent {agent_id}: {system_info}")
            except Exception as e:
                logger.error(f"Error getting system info for agent {agent_id}: {str(e)}")
                system_info = {}
        
        # Update agent status based on connection
        status = 'online' if is_connected else 'offline'
        update_data = {
            'status': status,
            'last_seen': datetime.now().isoformat()
        }
        
        # Add system info if available
        if system_info:
            update_data['system_info'] = system_info
        
        logger.info(f"Updating agent {agent_id} with data: {update_data}")
        success = db_manager.update_agent(agent_id, update_data)
        
        if not success:
            logger.error(f"Failed to update agent {agent_id}")
            raise HTTPException(status_code=500, detail="Failed to refresh agent")
        
        # Get updated agent data
        updated_agent = db_manager.get_agent(agent_id)
        updated_agent['is_connected'] = is_connected
        
        logger.info(f"Agent {agent_id} updated successfully")
        logger.info(f"Returning agent data: {updated_agent}")
        
        return {
            "message": "Agent refreshed successfully",
            "agent": Agent(**updated_agent)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/connected", response_model=List[Agent])
async def get_connected_agents(token: str = Depends(verify_token)):
    """Get list of currently connected agents"""
    try:
        connected_agents = websocket_manager.get_connected_agents()
        agents_info = []
        
        for agent_id in connected_agents:
            agent_data = db_manager.get_agent(agent_id)
            if agent_data:
                agent_data['is_connected'] = True
                connection_info = websocket_manager.get_connection_info(
                    websocket_manager.agent_connections[agent_id]
                )
                agent_data['connection_info'] = connection_info
                agents_info.append(Agent(**agent_data))
        
        return agents_info
    except Exception as e:
        logger.error(f"Error getting connected agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/seed", response_model=List[Agent])
async def seed_test_data(token: str = Depends(verify_token)):
    """Seed test data for development"""
    try:
        test_agents = [
            {
                "hostname": "DESKTOP-ABC123",
                "ip": "192.168.1.100",
                "os": "Windows 11",
                "version": "10.0.22000",
                "status": "online",
                "tags": ["development", "test"]
            },
            {
                "hostname": "LAPTOP-XYZ789",
                "ip": "192.168.1.101",
                "os": "Windows 10",
                "version": "10.0.19045",
                "status": "offline",
                "tags": ["production", "critical"]
            },
            {
                "hostname": "SERVER-MAIN",
                "ip": "192.168.1.102",
                "os": "Windows Server 2022",
                "version": "10.0.20348",
                "status": "online",
                "tags": ["server", "production", "database"]
            }
        ]
        
        created_agents = []
        for agent_data in test_agents:
            agent_id = db_manager.add_agent(agent_data)
            agent_data["id"] = agent_id
            agent_data["is_connected"] = websocket_manager.is_agent_connected(agent_id)
            created_agents.append(Agent(**agent_data))
        
        return created_agents
    except Exception as e:
        logger.error(f"Error seeding test data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 