from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from ...schemas.agent import Agent, AgentUpdate
from ...core.database import db_manager
from ...core.auth import verify_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[Agent])
async def get_agents(token: str = Depends(verify_token)):
    """Get all agents"""
    try:
        agents_data = db_manager.get_agents()
        return [Agent(**agent) for agent in agents_data]
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
        return Agent(**agent_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=Agent)
async def create_agent(agent: Agent, token: str = Depends(verify_token)):
    """Create a new agent"""
    try:
        agent_id = db_manager.add_agent(agent.dict())
        agent.id = agent_id
        return agent
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
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
    """Refresh agent status"""
    try:
        # Verify agent exists
        agent = db_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update agent status to online
        success = db_manager.update_agent_status(agent_id, "online")
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to refresh agent")
        
        return {"message": "Agent refreshed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/register", response_model=Agent)
async def register_current_system(token: str = Depends(verify_token)):
    """Register the current system as an agent"""
    try:
        import socket
        import platform
        
        hostname = socket.gethostname()
        
        # Create agent data
        agent_data = {
            "hostname": hostname,
            "os": platform.system(),
            "version": platform.version(),
            "status": "online",
            "tags": ["auto-registered"]
        }
        
        agent_id = db_manager.add_agent(agent_data)
        agent_data["id"] = agent_id
        
        return Agent(**agent_data)
    except Exception as e:
        logger.error(f"Error registering current system: {str(e)}")
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
            created_agents.append(Agent(**agent_data))
        
        return created_agents
    except Exception as e:
        logger.error(f"Error seeding test data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 