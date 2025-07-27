from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

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