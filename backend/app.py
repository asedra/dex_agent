import os
import subprocess
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import psutil
from dotenv import load_dotenv
from database import db_manager
import tempfile
import shutil
import json
import zipfile

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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

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

class AgentInstallerConfig(BaseModel):
    server_url: str = Field(..., description="DexAgents server URL")
    api_token: str = Field(..., description="API token for authentication")
    agent_name: Optional[str] = Field(None, description="Custom agent name")
    tags: List[str] = Field(default_factory=list, description="Agent tags")
    auto_start: bool = Field(True, description="Auto-start agent after installation")
    run_as_service: bool = Field(True, description="Run agent as Windows service")

# Security middleware
async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verify API token"""
    if not credentials:
        if os.getenv("ENVIRONMENT", "development") == "development":
            return "development_token"
        raise HTTPException(status_code=401, detail="Missing API token")
    
    token = credentials.credentials
    expected_token = os.getenv("API_TOKEN", "default_token")
    
    logger.info(f"Token verification - Received: {token[:10]}..., Expected: {expected_token[:10]}...")
    
    if token != expected_token:
        logger.warning(f"Token mismatch - Received: {token}, Expected: {expected_token}")
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    return token

# Agent installer service
class AgentInstallerService:
    @staticmethod
    def create_agent_installer(config: AgentInstallerConfig) -> str:
        """Create agent installer executable"""
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            installer_dir = os.path.join(temp_dir, "dexagents_installer")
            os.makedirs(installer_dir, exist_ok=True)
            
            # Create agent configuration
            agent_config = {
                "server_url": config.server_url,
                "api_token": config.api_token,
                "agent_name": config.agent_name or f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tags": config.tags,
                "auto_start": config.auto_start,
                "run_as_service": config.run_as_service,
                "version": "2.1.4",
                "created_at": datetime.now().isoformat()
            }
            
            # Create agent script
            script_content = f'''#!/usr/bin/env python3
"""
DexAgents Windows Agent
Version: {agent_config["version"]}
"""

import os
import sys
import json
import time
import requests
import psutil
from datetime import datetime
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(r"C:\\Program Files\\DexAgents\\logs\\agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DexAgent:
    def __init__(self):
        self.config = {json.dumps(agent_config, indent=8)}
        self.server_url = self.config["server_url"]
        self.api_token = self.config["api_token"]
        self.agent_name = self.config["agent_name"]
        self.tags = self.config["tags"]
        self.session = requests.Session()
        self.session.headers.update({{
            "Authorization": f"Bearer {{self.api_token}}",
            "Content-Type": "application/json"
        }})
        
    def get_system_info(self):
        """Get system information"""
        try:
            hostname = os.environ.get('COMPUTERNAME', 'Unknown')
            os_version = os.environ.get('OS', 'Unknown')
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            disk_usage = {{}}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = (usage.used / usage.total) * 100
                except PermissionError:
                    continue
                    
            return {{
                "hostname": hostname,
                "os_version": os_version,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "disk_usage": disk_usage
            }}
        except Exception as e:
            logger.error(f"Error getting system info: {{e}}")
            return None
            
    def register_agent(self):
        """Register agent with server"""
        try:
            system_info = self.get_system_info()
            if not system_info:
                return False
                
            agent_data = {{
                "hostname": system_info["hostname"],
                "os": system_info["os_version"],
                "version": self.config["version"],
                "status": "online",
                "last_seen": datetime.now().isoformat(),
                "tags": self.tags,
                "system_info": system_info
            }}
            
            response = self.session.post(f"{{self.server_url}}/api/agents/register", json=agent_data)
            if response.status_code == 200:
                logger.info("Agent registered successfully")
                return True
            else:
                logger.error(f"Failed to register agent: {{response.status_code}}")
                return False
        except Exception as e:
            logger.error(f"Error registering agent: {{e}}")
            return False
            
    def update_status(self):
        """Update agent status"""
        try:
            system_info = self.get_system_info()
            if not system_info:
                return False
                
            update_data = {{
                "status": "online",
                "last_seen": datetime.now().isoformat(),
                "system_info": system_info
            }}
            
            response = self.session.post(f"{{self.server_url}}/api/agents/register", json=update_data)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error updating status: {{e}}")
            return False
            
    def run(self):
        """Main agent loop"""
        logger.info("Starting DexAgents Windows Agent")
        
        if not self.register_agent():
            logger.error("Failed to register agent")
            return
            
        while True:
            try:
                self.update_status()
                time.sleep(30)
            except KeyboardInterrupt:
                logger.info("Agent stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {{e}}")
                time.sleep(60)

if __name__ == "__main__":
    agent = DexAgent()
    agent.run()
'''
            
            # Write agent script
            script_path = os.path.join(installer_dir, "dexagent.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)
                
            # Create requirements.txt
            requirements_content = '''requests>=2.31.0
psutil>=5.9.6
'''
            requirements_path = os.path.join(installer_dir, "requirements.txt")
            with open(requirements_path, "w") as f:
                f.write(requirements_content)
                
            # Create installer script
            installer_script = f'''@echo off
echo DexAgents Windows Agent Installer
echo ================================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This installer requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

echo Installing DexAgents Windows Agent...

REM Create installation directory
if not exist "C:\\Program Files\\DexAgents" mkdir "C:\\Program Files\\DexAgents"
if not exist "C:\\Program Files\\DexAgents\\logs" mkdir "C:\\Program Files\\DexAgents\\logs"

REM Copy agent files
copy "dexagent.py" "C:\\Program Files\\DexAgents\\"
copy "requirements.txt" "C:\\Program Files\\DexAgents\\"

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r "C:\\Program Files\\DexAgents\\requirements.txt"

REM Create configuration file
echo {json.dumps(agent_config, indent=4)} > "C:\\Program Files\\DexAgents\\config.json"

REM Create Windows service
echo Creating Windows service...
sc create "DexAgents" binPath= "pythonw.exe C:\\Program Files\\DexAgents\\dexagent.py" start= auto
sc description "DexAgents" "DexAgents Windows Agent Service"

REM Start service
echo Starting DexAgents service...
sc start "DexAgents"

echo.
echo DexAgents Windows Agent installed successfully!
echo Service name: DexAgents
echo Installation path: C:\\Program Files\\DexAgents
echo Logs: C:\\Program Files\\DexAgents\\logs\\agent.log
echo.
echo To manage the service:
echo   Start: sc start DexAgents
echo   Stop: sc stop DexAgents
echo   Status: sc query DexAgents
echo.
pause
'''
            
            installer_path = os.path.join(installer_dir, "install.bat")
            with open(installer_path, "w") as f:
                f.write(installer_script)
                
            # Create README
            readme_content = f'''# DexAgents Windows Agent

## Installation

1. Run `install.bat` as administrator
2. The agent will be installed as a Windows service
3. Service will start automatically

## Configuration

- Server URL: {config.server_url}
- Agent Name: {agent_config["agent_name"]}
- Tags: {", ".join(config.tags) if config.tags else "None"}

## Files

- Agent Script: `C:\\Program Files\\DexAgents\\dexagent.py`
- Configuration: `C:\\Program Files\\DexAgents\\config.json`
- Logs: `C:\\Program Files\\DexAgents\\logs\\agent.log`

## Service Management

- Start: `sc start DexAgents`
- Stop: `sc stop DexAgents`
- Status: `sc query DexAgents`
- Remove: `sc delete DexAgents`

## Uninstall

1. Stop service: `sc stop DexAgents`
2. Delete service: `sc delete DexAgents`
3. Remove files: Delete `C:\\Program Files\\DexAgents` folder
'''
            
            readme_path = os.path.join(installer_dir, "README.md")
            with open(readme_path, "w") as f:
                f.write(readme_content)
                
            # Create ZIP file
            zip_path = os.path.join(temp_dir, f"dexagents_installer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(installer_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, installer_dir)
                        zipf.write(file_path, arcname)
                        
            return zip_path
            
        except Exception as e:
            logger.error(f"Error creating installer: {e}")
            raise
        
    @staticmethod
    def cleanup_temp_files(zip_path: str):
        """Clean up temporary files"""
        try:
            temp_dir = os.path.dirname(zip_path)
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")

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
            if not command.strip():
                raise ValueError("Command cannot be empty")
            
            ps_command = [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy", "Bypass",
                "-Command", command
            ]
            
            if working_directory:
                if not os.path.exists(working_directory):
                    raise ValueError(f"Working directory does not exist: {working_directory}")
                cwd = working_directory
            else:
                cwd = os.getcwd()
            
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
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
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
        hostname = os.environ.get('COMPUTERNAME', 'Unknown')
        os_version = os.environ.get('OS', 'Unknown')
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
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

# Agent installer endpoints
@app.post("/api/installer/create")
async def create_agent_installer(
    config: AgentInstallerConfig,
    token: str = Depends(verify_token)
):
    """Create agent installer package"""
    try:
        logger.info(f"Creating agent installer for {config.agent_name}")
        
        zip_path = AgentInstallerService.create_agent_installer(config)
        
        filename = os.path.basename(zip_path)
        async def cleanup_after_response():
            await asyncio.sleep(1)  # Wait for response to be sent
            AgentInstallerService.cleanup_temp_files(zip_path)
            
        return FileResponse(
            path=zip_path,
            filename=filename,
            media_type="application/zip",
            background=BackgroundTasks([cleanup_after_response])
        )
        
    except Exception as e:
        logger.error(f"Error creating installer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create installer: {str(e)}")

@app.get("/api/installer/config")
async def get_installer_config(token: str = Depends(verify_token)):
    """Get default installer configuration"""
    return {
        "server_url": f"http://{os.environ.get('COMPUTERNAME', 'localhost')}:8000",
        "api_token": os.getenv("API_TOKEN", "default_token"),
        "default_tags": ["windows", "powershell-enabled"],
        "version": "2.1.4"
    }

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
        existing_agent = db_manager.get_agent(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
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
        agent = db_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        system_info = await get_system_info_internal()
        
        update_data = {
            'ip': system_info.hostname,
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
                'processor_name': 'Unknown'
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

@app.post("/api/agents/register", response_model=Agent)
async def register_current_system(token: str = Depends(verify_token)):
    """Register the current system as an agent"""
    try:
        system_info = await get_system_info_internal()
        
        agent_data = {
            "hostname": system_info.hostname,
            "os": system_info.os_version,
            "version": "2.1.4",
            "status": "online",
            "last_seen": datetime.now().isoformat(),
            "tags": ["Auto-Registered"],
            "system_info": system_info.dict()
        }
        
        agent_id = db_manager.add_agent(agent_data)
        return db_manager.get_agent(agent_id)
    except Exception as e:
        logger.error(f"Error registering current system: {e}")
        raise HTTPException(status_code=500, detail="Failed to register current system")

async def get_system_info_internal() -> SystemInfo:
    """Get system information (internal use)"""
    try:
        hostname = os.environ.get('COMPUTERNAME', 'Unknown')
        os_version = os.environ.get('OS', 'Unknown')
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
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

@app.get("/api/health")
async def api_health():
    """Frontend health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 