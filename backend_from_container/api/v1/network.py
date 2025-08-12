"""Network configuration API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging

from ...core.database import db_manager
from ...core.auth import verify_token
from ...core.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/agents/{agent_id}/network/adapters")
async def get_network_adapters(
    agent_id: str,
    include_hidden: bool = Query(False, description="Include hidden adapters"),
    token: str = Depends(verify_token)
):
    """Get list of network adapters from agent."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Build PowerShell command to get network adapters
        ps_command = """
        Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, LinkSpeed, 
        MacAddress, InterfaceIndex, DriverVersion, AdminStatus, MediaType, 
        ConnectorPresent, HardwareInterface | ConvertTo-Json
        """
        
        if not include_hidden:
            ps_command = """
            Get-NetAdapter | Where-Object {$_.Status -ne 'Not Present' -and $_.Name -notlike '*Loopback*'} | 
            Select-Object Name, InterfaceDescription, Status, LinkSpeed, MacAddress, InterfaceIndex, 
            DriverVersion, AdminStatus, MediaType, ConnectorPresent, HardwareInterface | ConvertTo-Json
            """
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            output = response.get("output", "[]")
            try:
                adapters_data = json.loads(output) if output else []
                if not isinstance(adapters_data, list):
                    adapters_data = [adapters_data]  # Single adapter result
                
                return {
                    "adapters": adapters_data,
                    "total": len(adapters_data),
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "include_hidden": include_hidden
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse network adapter data: {str(e)}, output: {output}")
                raise HTTPException(status_code=500, detail="Failed to parse network adapter data")
        else:
            raise HTTPException(status_code=500, detail="Failed to get network adapters from agent")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting network adapters from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/agents/{agent_id}/network/firewall/rules")
async def get_firewall_rules(
    agent_id: str,
    direction: Optional[str] = Query(None, description="Filter by direction (Inbound/Outbound)"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    limit: Optional[int] = Query(100, description="Limit results"),
    token: str = Depends(verify_token)
):
    """Get Windows Firewall rules from agent."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Build PowerShell command to get firewall rules
        ps_command = "Get-NetFirewallRule | Select-Object DisplayName, Name, Enabled, Direction, Action, Profile, Description"
        
        # Add filtering
        if direction:
            ps_command += f" | Where-Object {{$_.Direction -eq '{direction}'}}"
        
        if enabled is not None:
            enabled_str = "True" if enabled else "False"
            ps_command += f" | Where-Object {{$_.Enabled -eq ${enabled_str}}}"
        
        # Add limit
        if limit:
            ps_command += f" | Select-Object -First {limit}"
        
        ps_command += " | ConvertTo-Json"
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            output = response.get("output", "[]")
            try:
                rules_data = json.loads(output) if output else []
                if not isinstance(rules_data, list):
                    rules_data = [rules_data]  # Single rule result
                
                return {
                    "rules": rules_data,
                    "total": len(rules_data),
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "filters": {
                        "direction": direction,
                        "enabled": enabled,
                        "limit": limit
                    }
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse firewall rules data: {str(e)}, output: {output}")
                raise HTTPException(status_code=500, detail="Failed to parse firewall rules data")
        else:
            raise HTTPException(status_code=500, detail="Failed to get firewall rules from agent")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting firewall rules from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/agents/{agent_id}/network/routing/table")
async def get_routing_table(
    agent_id: str,
    interface_index: Optional[int] = Query(None, description="Filter by interface index"),
    destination: Optional[str] = Query(None, description="Filter by destination"),
    token: str = Depends(verify_token)
):
    """Get routing table from agent."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Build PowerShell command to get routing table
        ps_command = "Get-NetRoute | Select-Object DestinationPrefix, NextHop, InterfaceIndex, InterfaceAlias, RouteMetric, Protocol, AddressFamily"
        
        # Add filtering
        if interface_index:
            ps_command += f" | Where-Object {{$_.InterfaceIndex -eq {interface_index}}}"
        
        if destination:
            ps_command += f" | Where-Object {{$_.DestinationPrefix -like '*{destination}*'}}"
        
        ps_command += " | ConvertTo-Json"
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            output = response.get("output", "[]")
            try:
                routes_data = json.loads(output) if output else []
                if not isinstance(routes_data, list):
                    routes_data = [routes_data]  # Single route result
                
                return {
                    "routes": routes_data,
                    "total": len(routes_data),
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "filters": {
                        "interface_index": interface_index,
                        "destination": destination
                    }
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse routing table data: {str(e)}, output: {output}")
                raise HTTPException(status_code=500, detail="Failed to parse routing table data")
        else:
            raise HTTPException(status_code=500, detail="Failed to get routing table from agent")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting routing table from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/agents/{agent_id}/network/test")
async def test_network_connectivity(
    agent_id: str,
    test_request: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Test network connectivity from agent."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        target = test_request.get("target")
        test_type = test_request.get("type", "ping").lower()
        
        if not target:
            raise HTTPException(status_code=400, detail="target is required")
        
        # Build PowerShell command based on test type
        if test_type == "ping":
            count = test_request.get("count", 4)
            ps_command = f"Test-Connection -ComputerName '{target}' -Count {count} | Select-Object Source, Destination, Status, ResponseTime | ConvertTo-Json"
        elif test_type == "port":
            port = test_request.get("port")
            if not port:
                raise HTTPException(status_code=400, detail="port is required for port test")
            ps_command = f"Test-NetConnection -ComputerName '{target}' -Port {port} | Select-Object ComputerName, RemoteAddress, RemotePort, TcpTestSucceeded | ConvertTo-Json"
        elif test_type == "traceroute":
            ps_command = f"Test-NetConnection -ComputerName '{target}' -TraceRoute | Select-Object ComputerName, RemoteAddress, TraceRoute | ConvertTo-Json"
        else:
            raise HTTPException(status_code=400, detail="Invalid test type. Valid types: ping, port, traceroute")
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            output = response.get("output", "{}")
            try:
                test_result = json.loads(output) if output else {}
                
                return {
                    "test_type": test_type,
                    "target": target,
                    "result": test_result,
                    "success": True,
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat()
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse network test data: {str(e)}, output: {output}")
                return {
                    "test_type": test_type,
                    "target": target,
                    "result": {"raw_output": output},
                    "success": True,
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat()
                }
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            return {
                "test_type": test_type,
                "target": target,
                "result": {"error": error_msg},
                "success": False,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing network connectivity from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/agents/{agent_id}/network/configure")
async def configure_network_adapter(
    agent_id: str,
    config_request: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Configure network adapter settings on agent."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        adapter_id = config_request.get("adapter_id")
        if not adapter_id:
            raise HTTPException(status_code=400, detail="adapter_id is required")
        
        # Check if we're configuring DHCP or static IP
        dhcp_enabled = config_request.get("dhcp_enabled")
        ip_address = config_request.get("ip_address")
        subnet_mask = config_request.get("subnet_mask")
        gateway = config_request.get("gateway")
        dns_servers = config_request.get("dns_servers", [])
        
        # Build PowerShell commands for network configuration
        ps_commands = []
        
        if dhcp_enabled:
            # Enable DHCP
            ps_commands.append(f"Set-NetIPInterface -InterfaceAlias '{adapter_id}' -Dhcp Enabled")
            # Remove static DNS if enabling DHCP
            ps_commands.append(f"Set-DnsClientServerAddress -InterfaceAlias '{adapter_id}' -ResetServerAddresses")
        else:
            # Configure static IP
            if ip_address and subnet_mask:
                # Remove existing IP configuration
                ps_commands.append(f"Remove-NetIPAddress -InterfaceAlias '{adapter_id}' -Confirm:$false -ErrorAction SilentlyContinue")
                ps_commands.append(f"Remove-NetRoute -InterfaceAlias '{adapter_id}' -Confirm:$false -ErrorAction SilentlyContinue")
                
                # Set static IP
                ps_commands.append(f"New-NetIPAddress -InterfaceAlias '{adapter_id}' -IPAddress '{ip_address}' -PrefixLength {subnet_mask}")
                
                # Set gateway if provided
                if gateway:
                    ps_commands.append(f"New-NetRoute -InterfaceAlias '{adapter_id}' -DestinationPrefix '0.0.0.0/0' -NextHop '{gateway}'")
            
            # Set DNS servers if provided
            if dns_servers:
                dns_list = ','.join([f"'{dns}'" for dns in dns_servers])
                ps_commands.append(f"Set-DnsClientServerAddress -InterfaceAlias '{adapter_id}' -ServerAddresses {dns_list}")
        
        if not ps_commands:
            raise HTTPException(status_code=400, detail="No valid configuration parameters provided")
        
        # Execute configuration commands
        results = []
        for ps_command in ps_commands:
            response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
            results.append({
                "command": ps_command,
                "success": response.get("success", False) if response else False,
                "output": response.get("output", "") if response else "",
                "error": response.get("error", "") if response else "No response"
            })
        
        # Check if all commands succeeded
        all_success = all(result["success"] for result in results)
        
        # Get updated adapter information
        get_adapter_cmd = f"Get-NetAdapter -Name '{adapter_id}' | Select-Object Name, InterfaceDescription, Status, LinkSpeed, MacAddress | ConvertTo-Json"
        adapter_response = await websocket_manager.execute_command_on_agent(agent_id, get_adapter_cmd)
        
        adapter_info = None
        if adapter_response and adapter_response.get("success"):
            try:
                adapter_info = json.loads(adapter_response.get("output", "{}"))
            except json.JSONDecodeError:
                pass
        
        return {
            "success": all_success,
            "message": "Network configuration completed" if all_success else "Network configuration completed with some errors",
            "adapter": adapter_info,
            "configuration_results": results,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring network adapter on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")