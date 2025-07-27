import os
import subprocess
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import psutil
from dotenv import load_dotenv

# Environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Windows PowerShell Agent",
    description="API for executing PowerShell commands on Windows devices",
    version="1.0.0"
)

# Security
security = HTTPBearer()

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

# Security middleware
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token"""
    token = credentials.credentials
    expected_token = os.getenv("API_TOKEN", "default_token")
    
    if token != expected_token:
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
    return {"message": "Windows PowerShell Agent is running", "status": "healthy"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 