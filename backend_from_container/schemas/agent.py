from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import re

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
    connection_id: Optional[str] = None
    is_connected: bool = False

class AgentUpdate(BaseModel):
    hostname: Optional[str] = None
    ip: Optional[str] = None
    os: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    system_info: Optional[Dict[str, Any]] = None
    connection_id: Optional[str] = None
    is_connected: Optional[bool] = None

class AgentRegister(BaseModel):
    hostname: str = Field(..., min_length=1, max_length=255, description="Agent hostname is required")
    ip: Optional[str] = Field(None, description="IP address (deprecated, use ip_address)")
    ip_address: Optional[str] = Field(None, description="IP address for agent registration")
    os: str = Field(..., min_length=1, max_length=100, description="Operating system is required")
    version: Optional[str] = Field(None, description="OS version (deprecated, use os_version)")
    os_version: Optional[str] = Field(None, description="OS version")
    mac_address: Optional[str] = Field(None, description="MAC address")
    agent_version: Optional[str] = Field(None, description="Agent software version")
    powershell_version: Optional[str] = Field(None, description="PowerShell version")
    tags: List[str] = []
    system_info: Optional[Dict[str, Any]] = None
    
    @validator('ip_address', 'ip', pre=True)
    def validate_ip_address(cls, v, values):
        """Validate IP address format - supports both ip and ip_address fields"""
        if not v:
            # Check if the other field has a value
            if 'ip' in values and values['ip']:
                return values['ip']
            elif 'ip_address' in values and values['ip_address']:
                return values['ip_address']
            return None
        
        if not v.strip():
            return None
        
        # Basic IPv4 validation using regex
        ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        # Basic IPv6 validation (simplified)
        ipv6_pattern = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$'
        
        if not (re.match(ipv4_pattern, v.strip()) or re.match(ipv6_pattern, v.strip())):
            raise ValueError("Invalid IP address format")
        
        return v.strip()
    
    @validator('hostname')
    def validate_hostname(cls, v):
        """Validate hostname format"""
        if not v or not v.strip():
            raise ValueError("Hostname cannot be empty")
        
        # Basic hostname validation - alphanumeric, hyphens, dots
        hostname_pattern = r'^[a-zA-Z0-9.-]+$'
        if not re.match(hostname_pattern, v.strip()):
            raise ValueError("Invalid hostname format")
        
        return v.strip()
    
    @validator('os')
    def validate_os(cls, v):
        """Validate OS field"""
        if not v or not v.strip():
            raise ValueError("Operating system cannot be empty")
        return v.strip()
    
    @validator('version')
    def validate_version(cls, v):
        """Validate version field"""
        if not v or not v.strip():
            raise ValueError("Version cannot be empty")
        return v.strip()

class AgentInstallerConfig(BaseModel):
    server_url: str = Field(..., description="DexAgents server URL")
    api_token: str = Field(..., description="API token for authentication")
    agent_name: Optional[str] = Field(None, description="Custom agent name")
    tags: List[str] = Field(default_factory=list, description="Agent tags")
    auto_start: bool = Field(True, description="Auto-start agent after installation")
    run_as_service: bool = Field(True, description="Run agent as Windows service")

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None

class AgentCommand(BaseModel):
    command: str
    timeout: Optional[int] = 30
    working_directory: Optional[str] = None

class CommandResult(BaseModel):
    command: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    exit_code: Optional[int] = None

class BulkAgentOperation(BaseModel):
    agent_ids: List[str] = Field(..., description="List of agent IDs to perform operation on")
    operation: str = Field(..., description="Operation to perform: 'refresh', 'restart', 'shutdown', 'status', 'update_tags'")
    tags: Optional[List[str]] = Field(None, description="Tags to set when using update_tags operation")
    
class BulkOperationResult(BaseModel):
    operation: str
    total_agents: int
    successful: List[str]
    failed: List[Dict[str, Any]]  # Each dict contains agent_id and error
    results: Dict[str, Any] = {} 