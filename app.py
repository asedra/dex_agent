import os
import subprocess
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import psutil
from dotenv import load_dotenv
from database import db_manager

# Environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DexAgents - Windows PowerShell Agent",
    description="API for executing PowerShell commands on Windows devices",
    version="1.0.0"
)

# CORS middleware - Frontend entegrasyonu için güncellendi
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js default
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"  # Development için tüm origin'lere izin ver
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)  # Frontend için auto_error=False

# Models
class PowerShellCommand(BaseModel):
    command: str = Field(..., description="PowerShell command to execute")
    timeout: Optional[int] = Field(30, description="Command timeout in seconds")
    working_directory: Optional[str] = Field(None, description="Working directory for command")
    run_as_admin: Optional[bool] = Field(False, description="Run command as administrator")

class CommandResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float
    timestamp: datetime
    command: str

class SystemInfo(BaseModel):
    hostname: str
    os_version: str
    cpu_usage: float
    memory_usage: float
    disk_usage: Dict[str, float]

class Agent(BaseModel):
    id: Optional[str] = None
    hostname: str
    ip: Optional[str] = None
    os: Optional[str] = None
    version: Optional[str] = None
    status: str = "offline"
    last_seen: Optional[str] = None
    tags: List[str] = []
    system_info: Optional[Dict[str, Any]] = None

class AgentUpdate(BaseModel):
    hostname: Optional[str] = None
    ip: Optional[str] = None
    os: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    system_info: Optional[Dict[str, Any]] = None

# Security middleware - Frontend için daha esnek
async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verify API token - Frontend için daha esnek"""
    if not credentials:
        # Development için token kontrolünü atla
        if os.getenv("ENVIRONMENT", "development") == "development":
            return "development_token"
        raise HTTPException(status_code=401, detail="Missing API token")
    
    token = credentials.credentials
    expected_token = os.getenv("API_TOKEN", "default_token")
    
    # Debug logging
    logger.info(f"Token verification - Received: {token[:10]}..., Expected: {expected_token[:10]}...")
    
    if token != expected_token:
        logger.warning(f"Token mismatch - Received: {token}, Expected: {expected_token}")
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    return token

# PowerShell execution service
class PowerShellService:
    @staticmethod
    async def execute_command(
        command: str,
        timeout: int = 30,
        working_directory: Optional[str] = None,
        run_as_admin: bool = False
    ) -> CommandResponse:
        """Execute PowerShell command safely"""
        start_time = datetime.now()
        
        try:
            # Validate command
            if not command.strip():
                raise ValueError("Command cannot be empty")
            
            # Prepare PowerShell command
            ps_command = [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy", "Bypass",
                "-Command", command
            ]
            
            # Set working directory
            if working_directory:
                if not os.path.exists(working_directory):
                    raise ValueError(f"Working directory does not exist: {working_directory}")
                cwd = working_directory
            else:
                cwd = os.getcwd()
            
            # Execute command
            process = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    *ps_command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd
                ),
                timeout=timeout
            )
            
            stdout, stderr = await process.communicate()
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare response
            output = stdout.decode('utf-8', errors='ignore').strip()
            error = stderr.decode('utf-8', errors='ignore').strip()
            
            success = process.returncode == 0
            
            return CommandResponse(
                success=success,
                output=output,
                error=error if error else None,
                execution_time=execution_time,
                timestamp=start_time,
                command=command
            )
            
        except asyncio.TimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds()
            return CommandResponse(
                success=False,
                output="",
                error=f"Command timed out after {timeout} seconds",
                execution_time=execution_time,
                timestamp=start_time,
                command=command
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return CommandResponse(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time,
                timestamp=start_time,
                command=command
            )

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "DexAgents - Windows PowerShell Agent is running", 
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/system/info", response_model=SystemInfo)
async def get_system_info(token: str = Depends(verify_token)):
    """Get system information"""
    try:
        # Get hostname
        hostname = os.environ.get('COMPUTERNAME', 'Unknown')
        
        # Get OS version
        os_version = os.environ.get('OS', 'Unknown')
        
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Get disk usage
        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.device] = (usage.used / usage.total) * 100
            except PermissionError:
                continue
        
        return SystemInfo(
            hostname=hostname,
            os_version=os_version,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage
        )
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system information")

@app.post("/execute", response_model=CommandResponse)
async def execute_powershell_command(
    command: PowerShellCommand,
    token: str = Depends(verify_token)
):
    """Execute a PowerShell command"""
    logger.info(f"Executing command: {command.command}")
    
    try:
        result = await PowerShellService.execute_command(
            command=command.command,
            timeout=command.timeout,
            working_directory=command.working_directory,
            run_as_admin=command.run_as_admin
        )
        
        logger.info(f"Command executed successfully: {result.success}")
        return result
        
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")

@app.post("/execute/batch", response_model=list[CommandResponse])
async def execute_batch_commands(
    commands: list[PowerShellCommand],
    token: str = Depends(verify_token)
):
    """Execute multiple PowerShell commands in sequence"""
    logger.info(f"Executing batch of {len(commands)} commands")
    
    results = []
    for cmd in commands:
        try:
            result = await PowerShellService.execute_command(
                command=cmd.command,
                timeout=cmd.timeout,
                working_directory=cmd.working_directory,
                run_as_admin=cmd.run_as_admin
            )
            results.append(result)
        except Exception as e:
            logger.error(f"Error in batch command: {e}")
            results.append(CommandResponse(
                success=False,
                output="",
                error=str(e),
                execution_time=0,
                timestamp=datetime.now(),
                command=cmd.command
            ))
    
    return results

# Agent Management Endpoints
@app.get("/api/agents", response_model=List[Agent])
async def get_agents(token: str = Depends(verify_token)):
    """Get all agents"""
    try:
        agents = db_manager.get_agents()
        return agents
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agents")

@app.get("/api/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, token: str = Depends(verify_token)):
    """Get a specific agent by ID"""
    try:
        agent = db_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent")

@app.post("/api/agents", response_model=Agent)
async def create_agent(agent: Agent, token: str = Depends(verify_token)):
    """Create a new agent"""
    try:
        agent_data = agent.dict()
        agent_id = db_manager.add_agent(agent_data)
        return db_manager.get_agent(agent_id)
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to create agent")

@app.put("/api/agents/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, agent_update: AgentUpdate, token: str = Depends(verify_token)):
    """Update an existing agent"""
    try:
        # Check if agent exists
        existing_agent = db_manager.get_agent(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update agent
        update_data = {k: v for k, v in agent_update.dict().items() if v is not None}
        if update_data:
            success = db_manager.update_agent(agent_id, update_data)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update agent")
        
        return db_manager.get_agent(agent_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update agent")

@app.delete("/api/agents/{agent_id}")
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
        logger.error(f"Error deleting agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete agent")

@app.get("/api/agents/{agent_id}/commands", response_model=List[Dict[str, Any]])
async def get_agent_commands(agent_id: str, limit: int = 50, token: str = Depends(verify_token)):
    """Get command history for an agent"""
    try:
        # Check if agent exists
        agent = db_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        commands = db_manager.get_command_history(agent_id, limit)
        return commands
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting commands for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get command history")

@app.post("/api/agents/{agent_id}/refresh")
async def refresh_agent(agent_id: str, token: str = Depends(verify_token)):
    """Refresh agent with real-time system information"""
    try:
        # Get the agent first
        agent = db_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get real-time system information
        system_info = await get_system_info_internal()
        
        # Update agent with real-time data
        update_data = {
            'ip': system_info.hostname,  # We'll get IP from system info
            'os': system_info.os_version,
            'version': system_info.os_version.split()[-1] if system_info.os_version else 'Unknown',
            'status': 'online',
            'last_seen': datetime.now().isoformat(),
            'system_info': {
                'hostname': system_info.hostname,
                'os_version': system_info.os_version,
                'cpu_usage': system_info.cpu_usage,
                'memory_usage': system_info.memory_usage,
                'disk_usage': system_info.disk_usage,
                'processor_name': 'Unknown'  # We'll get this from PowerShell later
            }
        }
        
        success = db_manager.update_agent(agent_id, update_data)
        if success:
            updated_agent = db_manager.get_agent(agent_id)
            return {"message": "Agent refreshed successfully", "agent": updated_agent}
        else:
            raise HTTPException(status_code=500, detail="Failed to refresh agent")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh agent")

# Auto-register current system as an agent
@app.post("/api/agents/register", response_model=Agent)
async def register_current_system(token: str = Depends(verify_token)):
    """Register the current system as an agent"""
    try:
        # Get system info
        system_info = await get_system_info_internal()
        
        # Create agent data
        agent_data = {
            "hostname": system_info.hostname,
            "os": system_info.os_version,
            "version": "2.1.4",  # Default version
            "status": "online",
            "last_seen": datetime.now().isoformat(),
            "tags": ["Auto-Registered"],
            "system_info": system_info.dict()
        }
        
        # Add to database
        agent_id = db_manager.add_agent(agent_data)
        return db_manager.get_agent(agent_id)
    except Exception as e:
        logger.error(f"Error registering current system: {e}")
        raise HTTPException(status_code=500, detail="Failed to register current system")

# Helper function to get system info without authentication
async def get_system_info_internal() -> SystemInfo:
    """Get system information (internal use)"""
    try:
        # Get hostname
        hostname = os.environ.get('COMPUTERNAME', 'Unknown')
        
        # Get OS version
        os_version = os.environ.get('OS', 'Unknown')
        
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Get disk usage
        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.device] = (usage.used / usage.total) * 100
            except PermissionError:
                continue
        
        return SystemInfo(
            hostname=hostname,
            os_version=os_version,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage
        )
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system information")

# Frontend için ek endpoint'ler
@app.get("/api/health")
async def api_health():
    """Frontend için health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 