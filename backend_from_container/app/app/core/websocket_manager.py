import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import uuid
from .config import settings

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.agent_connections: Dict[str, str] = {}  # agent_id -> connection_id
        self.connection_agents: Dict[str, str] = {}  # connection_id -> agent_id
        self.connection_info: Dict[str, Dict[str, Any]] = {}
        self.pending_commands: Dict[str, Dict[str, Any]] = {}  # command_id -> command_info
        self.command_responses: Dict[str, Dict[str, Any]] = {}  # command_id -> response
        self.response_events: Dict[str, asyncio.Event] = {}  # command_id -> event for waiting responses
        
        # Mock agent support for testing
        self.mock_agents: Dict[str, Dict[str, Any]] = {}  # agent_id -> mock agent info
        self._initialize_mock_agents_if_enabled()
    
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
            # For mock agents, just return True (message is "sent")
            if self.is_mock_agent(agent_id):
                logger.debug(f"Mock message sent to agent {agent_id}: {message.get('type', 'unknown')}")
                return True
            return await self.send_message(connection_id, message)
        return False
    
    async def broadcast_service_update(self, agent_id: str, service_name: str, status: str):
        """Broadcast service status update to all connected clients"""
        message = {
            "type": "service_status_update",
            "agent_id": agent_id,
            "service_name": service_name,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to all client connections (excluding agent connections)
        await self.broadcast_to_clients(message)
    
    async def broadcast_to_clients(self, message: Dict[str, Any]):
        """Broadcast message to all client connections (not agents)"""
        disconnected = []
        
        for conn_id, websocket in self.active_connections.items():
            # Skip agent connections - only send to client connections
            if conn_id not in self.connection_agents:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to client {conn_id}: {str(e)}")
                    disconnected.append(conn_id)
        
        # Clean up disconnected connections
        for conn_id in disconnected:
            self.disconnect(conn_id)
    
    async def execute_command_on_agent(self, agent_id: str, command: str, command_type: str = "powershell") -> Dict[str, Any]:
        """Execute PowerShell command on agent and return command ID"""
        logger.info(f"Attempting to execute PowerShell command on agent {agent_id}")
        logger.info(f"Connected agents: {list(self.agent_connections.keys())}")
        
        if agent_id not in self.agent_connections:
            logger.error(f"Agent {agent_id} is not connected. Available agents: {list(self.agent_connections.keys())}")
            raise ValueError(f"Agent {agent_id} is not connected")
        
        # Use PowerShell-specific request ID format to match agent expectations
        request_id = f"ps_{datetime.now().timestamp()}_{uuid.uuid4().hex[:8]}"
        
        # Store command info
        self.pending_commands[request_id] = {
            "agent_id": agent_id,
            "command": command,
            "timestamp": datetime.now(),
            "status": "pending"
        }
        
        # Check if this is a mock agent
        if self.is_mock_agent(agent_id):
            logger.info(f"Simulating command execution on mock agent {agent_id}")
            # Simulate async command execution for mock agents
            response = await self._simulate_mock_command_response(request_id, command, agent_id)
            self.store_command_response(request_id, response)
            return response
        
        # Create event for waiting for response (real agents only)
        self.response_events[request_id] = asyncio.Event()
        
        # Send PowerShell command to agent in the format it expects
        powershell_message = {
            "type": "powershell_command" if command_type == "powershell" else "command",
            "request_id": request_id,
            "command": command,
            "timeout": 15,  # Reduced timeout for faster testing (DX-170 performance fix)
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Sending PowerShell command {request_id} to agent {agent_id}: {powershell_message}")
        success = await self.send_to_agent(agent_id, powershell_message)
        if not success:
            del self.pending_commands[request_id]
            logger.error(f"Failed to send PowerShell command to agent {agent_id}")
            raise ValueError(f"Failed to send PowerShell command to agent {agent_id}")
        
        logger.info(f"PowerShell command {request_id} sent to agent {agent_id}, waiting for response...")
        
        # Wait for response - reduced timeout for faster testing (DX-170 performance fix)
        response = await self.wait_for_command_response(request_id, timeout=15)
        
        if response:
            logger.info(f"Got response for command {request_id}: {response}")
            return response
        else:
            logger.error(f"No response received for command {request_id}")
            return {"status": "error", "message": "Command timeout or no response"}
    
    def store_command_response(self, command_id: str, response: Dict[str, Any]):
        """Store command response from agent"""
        self.command_responses[command_id] = response
        if command_id in self.pending_commands:
            self.pending_commands[command_id]["status"] = "completed"
            self.pending_commands[command_id]["response"] = response
        
        # Signal waiting threads that response is ready
        if command_id in self.response_events:
            self.response_events[command_id].set()
        
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
    
    async def wait_for_command_response(self, command_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Wait for command response with timeout"""
        try:
            # Check if response already exists
            if command_id in self.command_responses:
                return self.command_responses[command_id]
            
            # Create event if not exists
            if command_id not in self.response_events:
                self.response_events[command_id] = asyncio.Event()
            
            # Wait for response with timeout
            await asyncio.wait_for(self.response_events[command_id].wait(), timeout=timeout)
            
            # Cleanup event
            if command_id in self.response_events:
                del self.response_events[command_id]
            
            return self.command_responses.get(command_id)
        
        except asyncio.TimeoutError:
            logger.warning(f"Command {command_id} timed out after {timeout} seconds")
            # Cleanup
            if command_id in self.response_events:
                del self.response_events[command_id]
            if command_id in self.pending_commands:
                self.pending_commands[command_id]["status"] = "timeout"
            return None
        except Exception as e:
            logger.error(f"Error waiting for command response {command_id}: {str(e)}")
            # Cleanup
            if command_id in self.response_events:
                del self.response_events[command_id]
            return None
    
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
        
# PowerShell script to get complete system information
        powershell_script = """
$systemInfo = @{
    hostname = $env:COMPUTERNAME
    platform = [System.Environment]::OSVersion.VersionString
    architecture = [System.Environment]::Is64BitOperatingSystem
    cpu_count = (Get-CimInstance Win32_Processor).NumberOfLogicalProcessors
    cpu_name = (Get-CimInstance Win32_Processor).Name
    cpu_usage = (Get-Counter '\\\\Processor(_Total)\\\\% Processor Time' -SampleInterval 1).CounterSamples[0].CookedValue
    memory = @{
        total = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
        available = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory * 1024
        usage = 100 - ((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / ((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1024)) * 100
    }
    disk_usage = @{}
    uptime_seconds = (New-TimeSpan -Start (Get-CimInstance Win32_OperatingSystem).LastBootUpTime -End (Get-Date)).TotalSeconds
    network_adapters = @()
    processes = (Get-Process).Count
    top_processes = @()
    services = @{
        total = (Get-Service).Count
        running = (Get-Service | Where-Object {$_.Status -eq 'Running'}).Count
        stopped = (Get-Service | Where-Object {$_.Status -eq 'Stopped'}).Count
    }
}

# Get disk usage for all drives
Get-WmiObject Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    $systemInfo.disk_usage[$_.DeviceID] = @{
        total = $_.Size
        free = $_.FreeSpace
        used = $_.Size - $_.FreeSpace
        percent = [math]::Round((($_.Size - $_.FreeSpace) / $_.Size) * 100, 1)
    }
}

# Get network adapter info
Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object {
    $ipConfig = Get-NetIPAddress -InterfaceIndex $_.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
    $adapter = @{
        name = $_.Name
        description = $_.InterfaceDescription
        mac = $_.MacAddress
        speed = $_.LinkSpeed
        ip = if($ipConfig) { $ipConfig.IPAddress } else { "N/A" }
    }
    $systemInfo.network_adapters += $adapter
}

# Get top 5 processes by CPU
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 | ForEach-Object {
    $process = @{
        name = $_.ProcessName
        id = $_.Id
        cpu = [math]::Round($_.CPU, 2)
        memory_mb = [math]::Round($_.WorkingSet / 1MB, 2)
    }
    $systemInfo.top_processes += $process
}

# Convert to JSON
$systemInfo | ConvertTo-Json -Depth 10 -Compress
"""
        
        # Send PowerShell command request to agent
        request_message = {
            "type": "powershell_command",
            "request_id": request_id,
            "command": powershell_script,
            "response_type": "system_info_update",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Sending PowerShell system info request {request_id} to agent {agent_id}")
        success = await self.send_to_agent(agent_id, request_message)
        
        if not success:
            logger.error(f"Failed to send system info request to agent {agent_id}")
            raise ValueError(f"Failed to send system info request to agent {agent_id}")
        
        return request_id
    
    def _initialize_mock_agents_if_enabled(self):
        """Initialize mock agents if enabled in configuration"""
        if settings.MOCK_AGENTS or settings.ENABLE_TEST_MODE:
            logger.info("Initializing mock agents for testing")
            # Create some default mock agents for testing
            mock_agent_configs = [
                {
                    "id": "mock-agent-001",
                    "hostname": "TEST-PC-001",
                    "platform": "Windows 10 Pro",
                    "architecture": "x64",
                    "status": "online"
                },
                {
                    "id": "mock-agent-002", 
                    "hostname": "TEST-SERVER-001",
                    "platform": "Windows Server 2019",
                    "architecture": "x64", 
                    "status": "online"
                },
                {
                    "id": "mock-agent-003",
                    "hostname": "TEST-PC-002", 
                    "platform": "Windows 11 Pro",
                    "architecture": "x64",
                    "status": "offline"
                }
            ]
            
            for agent_config in mock_agent_configs:
                agent_id = agent_config["id"]
                self.mock_agents[agent_id] = {
                    **agent_config,
                    "connected_at": datetime.now().isoformat(),
                    "last_heartbeat": datetime.now().isoformat(),
                    "is_mock": True
                }
                # Only add online mock agents to connections
                if agent_config["status"] == "online":
                    mock_connection_id = f"mock-conn-{agent_id}"
                    self.agent_connections[agent_id] = mock_connection_id
                    self.connection_agents[mock_connection_id] = agent_id
                    self.connection_info[mock_connection_id] = self.mock_agents[agent_id]
            
            logger.info(f"Initialized {len(self.mock_agents)} mock agents")
    
    def add_mock_agent(self, agent_id: str, hostname: str = None, platform: str = None, status: str = "online"):
        """Add a mock agent for testing purposes"""
        if not settings.MOCK_AGENTS and not settings.ENABLE_TEST_MODE:
            logger.warning("Attempted to add mock agent but mock agents are disabled")
            return False
            
        mock_agent = {
            "id": agent_id,
            "hostname": hostname or f"MOCK-{agent_id.upper()}",
            "platform": platform or "Windows 10 Pro (Mock)",
            "architecture": "x64",
            "status": status,
            "connected_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "is_mock": True
        }
        
        self.mock_agents[agent_id] = mock_agent
        
        if status == "online":
            mock_connection_id = f"mock-conn-{agent_id}"
            self.agent_connections[agent_id] = mock_connection_id
            self.connection_agents[mock_connection_id] = agent_id
            self.connection_info[mock_connection_id] = mock_agent
        
        logger.info(f"Added mock agent: {agent_id} ({status})")
        return True
    
    def remove_mock_agent(self, agent_id: str):
        """Remove a mock agent"""
        if agent_id in self.mock_agents:
            # Remove from connections if present
            if agent_id in self.agent_connections:
                connection_id = self.agent_connections[agent_id]
                del self.agent_connections[agent_id]
                if connection_id in self.connection_agents:
                    del self.connection_agents[connection_id]
                if connection_id in self.connection_info:
                    del self.connection_info[connection_id]
            
            del self.mock_agents[agent_id]
            logger.info(f"Removed mock agent: {agent_id}")
            return True
        return False
    
    def is_mock_agent(self, agent_id: str) -> bool:
        """Check if agent is a mock agent"""
        return agent_id in self.mock_agents
    
    async def _simulate_mock_command_response(self, command_id: str, command: str, agent_id: str) -> Dict[str, Any]:
        """Simulate a realistic command response from a mock agent"""
        # Add realistic delay
        await asyncio.sleep(0.5 + (len(command) * 0.01))  # Simulate processing time
        
        # Generate realistic responses based on common commands
        command_lower = command.lower().strip()
        
        if "get-process" in command_lower:
            output = """ProcessName      Id  CPU     WorkingSet
-----------      --  ---     ----------
chrome         1234  45.67   234567890
explorer       5678  12.34   123456789
powershell     9012  5.89    67890123"""
        elif any(service_cmd in command_lower for service_cmd in ["get-service", "start-service", "stop-service", "restart-service", "suspend-service", "resume-service", "set-service"]):
            if "dependentservices" in command_lower or "servicesdependedon" in command_lower:
                # Service dependency query
                output = '''{"ServiceName":"W32Time","DependentServices":[{"Name":"TimeBroker","Status":"Running"}],"ServicesDependedOn":[{"Name":"RpcSs","Status":"Running"}]}'''
            elif "start-service" in command_lower or "stop-service" in command_lower or "restart-service" in command_lower:
                # Service action followed by status check
                service_name = "W32Time"  # Default service for testing
                status = "Running" if "start-service" in command_lower or "restart-service" in command_lower else "Stopped"
                output = f'{{"Name":"{service_name}","Status":"{status}"}}'
            elif "set-service" in command_lower:
                # Service configuration change
                output = '{"Name":"W32Time","Status":"Running","StartType":"Manual"}'
            elif "w32time" in command_lower:
                # Single service query
                output = '{"Name":"W32Time","DisplayName":"Windows Time","Status":"Running","StartType":"Manual","ServiceType":"Win32ShareProcess","Description":"Maintains date and time synchronization on all clients and servers in the network."}'
            elif "convertto-json" in command_lower:
                # List of services in JSON format
                output = '''[
  {"Name":"Spooler","DisplayName":"Print Spooler","Status":"Running","StartType":"Automatic"},
  {"Name":"Themes","DisplayName":"Themes","Status":"Running","StartType":"Automatic"},
  {"Name":"W32Time","DisplayName":"Windows Time","Status":"Running","StartType":"Manual"},
  {"Name":"Fax","DisplayName":"Fax","Status":"Stopped","StartType":"Manual"}
]'''
            else:
                # Fallback to text format for other service commands
                output = """Status  Name           DisplayName
------  ----           -----------
Running Spooler        Print Spooler
Running Themes         Themes
Stopped Fax            Fax"""
        elif "get-eventlog" in command_lower or "get-winevent" in command_lower:
            output = """Index Time          EntryType   Source                 InstanceID Message
----- ----          ---------   ------                 ---------- -------
12345 Jan 01 12:00  Information Microsoft-Windows-Kernel-General 1 System started successfully
12344 Jan 01 11:59  Warning     Microsoft-Windows-Kernel-Power    42 System battery is low"""
        elif "test-connection" in command_lower or "ping" in command_lower:
            output = """
Source        Destination     IPV4Address      IPV6Address                              Bytes    Time(ms)
------        -----------     -----------      -----------                              -----    --------
TEST-PC-001   google.com      8.8.8.8                                                   32       45
TEST-PC-001   google.com      8.8.8.8                                                   32       42
TEST-PC-001   google.com      8.8.8.8                                                   32       38
TEST-PC-001   google.com      8.8.8.8                                                   32       41"""
        elif "get-disk" in command_lower or "get-volume" in command_lower:
            output = """DriveLetter FriendlyName FileSystemType DriveType HealthStatus SizeRemaining      Size
----------- ------------ -------------- --------- ------------ -------------      ----
C           Local Disk   NTFS           Fixed     Healthy         45.67 GB    232.88 GB
D           Data Drive   NTFS           Fixed     Healthy        123.45 GB    465.76 GB"""
        elif "get-computerinfo" in command_lower or "hostname" in command_lower:
            mock_agent = self.mock_agents.get(agent_id, {})
            hostname = mock_agent.get("hostname", "MOCK-AGENT")
            platform = mock_agent.get("platform", "Windows 10 Pro")
            output = f"""ComputerName: {hostname}
WindowsProductName: {platform}
WindowsVersion: 10.0.19042
TotalPhysicalMemory: 17179869184
CsProcessors: Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz"""
        elif "error" in command_lower or "fail" in command_lower:
            # Simulate an error for testing error handling
            return {
                "success": False,
                "output": "",
                "error": "The term 'nonexistentcommand' is not recognized as the name of a cmdlet, function, script file, or operable program.",
                "exit_code": 1,
                "execution_time": 0.123,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Generic successful response
            output = f"Command executed successfully on {agent_id}\nMock output for: {command[:100]}..."
        
        return {
            "success": True,
            "output": output,
            "error": "",
            "exit_code": 0,
            "execution_time": 0.5 + (len(command) * 0.01),
            "timestamp": datetime.now().isoformat()
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager() 