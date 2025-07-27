from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

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