from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from ...schemas.agent import Agent, AgentUpdate, AgentRegister, BulkAgentOperation, BulkOperationResult
from ...core.database import db_manager
from ...core.auth import verify_token
from ...core.websocket_manager import websocket_manager
import logging
import socket
import platform
import psutil
from datetime import datetime
import json
import asyncio
from ...schemas.command import PowerShellCommand, CommandResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_agents(
    status: Optional[str] = Query(None, description="Filter agents by status (online, offline, etc.)"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit the number of results (1-1000)"),
    offset: Optional[int] = Query(0, ge=0, description="Number of results to skip for pagination"),
    order_by: str = Query("updated_at", description="Field to order by"),
    order_desc: bool = Query(True, description="Order in descending order"),
    include_total: bool = Query(False, description="Include total count in response"),
    token: str = Depends(verify_token)
):
    """Get agents with filtering and pagination support"""
    try:
        # Validate order_by field to prevent SQL injection
        valid_order_fields = ['id', 'hostname', 'ip', 'os', 'version', 'status', 'last_seen', 'created_at', 'updated_at']
        if order_by not in valid_order_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid order_by field. Valid fields: {', '.join(valid_order_fields)}"
            )
        
        # Validate status filter
        if status:
            valid_statuses = ['online', 'offline', 'warning', 'error']
            if status not in valid_statuses:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid status filter. Valid statuses: {', '.join(valid_statuses)}"
                )
        
        # Get agents with filtering and pagination
        agents_data = db_manager.get_agents(
            status=status,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_desc=order_desc
        )
        
        # Deduplicate agents by hostname, keeping the most recent one
        unique_agents = {}
        for agent_data in agents_data:
            hostname = agent_data.get('hostname')
            if hostname:
                # If we already have an agent with this hostname, keep the one with newer last_seen
                if hostname in unique_agents:
                    existing = unique_agents[hostname]
                    current_last_seen = agent_data.get('last_seen', '')
                    existing_last_seen = existing.get('last_seen', '')
                    
                    # Keep the agent with more recent last_seen timestamp
                    if current_last_seen > existing_last_seen:
                        unique_agents[hostname] = agent_data
                else:
                    unique_agents[hostname] = agent_data
        
        # Convert back to list and create Agent objects
        agents = []
        for agent_data in unique_agents.values():
            # Check if agent is currently connected
            agent_data['is_connected'] = websocket_manager.is_agent_connected(agent_data['id'])
            agents.append(Agent(**agent_data))
        
        response = {
            "agents": agents,
            "count": len(agents),
            "filters": {
                "status": status,
                "limit": limit,
                "offset": offset,
                "order_by": order_by,
                "order_desc": order_desc
            }
        }
        
        # Include total count if requested (useful for pagination UI)
        if include_total:
            total_count = db_manager.get_agents_count(status=status)
            response["total_count"] = total_count
            response["has_more"] = offset + len(agents) < total_count if offset is not None else False
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/list", response_model=List[Agent])
async def get_agents_list(
    status: Optional[str] = Query(None, description="Filter agents by status"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit the number of results"),
    offset: Optional[int] = Query(0, ge=0, description="Number of results to skip"),
    token: str = Depends(verify_token)
):
    """Get agents list (backward compatible endpoint) - returns only the agents array"""
    try:
        # Validate status filter
        if status:
            valid_statuses = ['online', 'offline', 'warning', 'error']
            if status not in valid_statuses:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid status filter. Valid statuses: {', '.join(valid_statuses)}"
                )
        
        # Get agents with filtering and pagination
        agents_data = db_manager.get_agents(
            status=status,
            limit=limit,
            offset=offset
        )
        
        # Deduplicate agents by hostname, keeping the most recent one
        unique_agents = {}
        for agent_data in agents_data:
            hostname = agent_data.get('hostname')
            if hostname:
                # If we already have an agent with this hostname, keep the one with newer last_seen
                if hostname in unique_agents:
                    existing = unique_agents[hostname]
                    current_last_seen = agent_data.get('last_seen', '')
                    existing_last_seen = existing.get('last_seen', '')
                    
                    # Keep the agent with more recent last_seen timestamp
                    if current_last_seen > existing_last_seen:
                        unique_agents[hostname] = agent_data
                else:
                    unique_agents[hostname] = agent_data
        
        # Convert back to list and create Agent objects
        agents = []
        for agent_data in unique_agents.values():
            # Check if agent is currently connected
            agent_data['is_connected'] = websocket_manager.is_agent_connected(agent_data['id'])
            agents.append(Agent(**agent_data))
        
        return agents
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agents list: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/connected")
async def get_connected_agents(token: str = Depends(verify_token)):
    """Get list of currently connected agents"""
    try:
        connected_agents = websocket_manager.get_connected_agents()
        agents_info = []
        
        for agent_id in connected_agents:
            agent_data = db_manager.get_agent(agent_id)
            if agent_data:
                agent_data['is_connected'] = True
                try:
                    connection_info = websocket_manager.get_connection_info(
                        websocket_manager.agent_connections[agent_id]
                    )
                    agent_data['connection_info'] = connection_info
                except:
                    agent_data['connection_info'] = None
                agents_info.append(agent_data)
        
        return {
            "connected_agents": agents_info,
            "total": len(agents_info),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting connected agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/offline")
async def get_offline_agents(token: str = Depends(verify_token)):
    """Get list of agents that haven't sent heartbeat in the last 60 seconds"""
    try:
        from datetime import timedelta
        
        # Get all agents
        all_agents = db_manager.get_agents()
        offline_agents = []
        
        # Check which agents haven't sent heartbeat recently
        cutoff_time = datetime.now() - timedelta(seconds=60)
        
        for agent_data in all_agents:
            last_seen_str = agent_data.get('last_seen')
            is_offline = False
            
            if last_seen_str:
                try:
                    last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                    if last_seen < cutoff_time:
                        is_offline = True
                except ValueError:
                    # If last_seen is invalid, consider agent offline
                    is_offline = True
            else:
                # No last_seen, consider offline
                is_offline = True
            
            # Also check if not connected via WebSocket
            if not websocket_manager.is_agent_connected(agent_data.get('id', '')):
                is_offline = True
            
            if is_offline:
                agent_data['is_connected'] = False
                offline_agents.append(agent_data)
        
        return {
            "offline_agents": offline_agents,
            "total": len(offline_agents),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting offline agents: {str(e)}")
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
            
            # Map new field names to old ones for database compatibility
            if 'ip_address' in update_data and update_data['ip_address']:
                update_data['ip'] = update_data['ip_address']
            if 'os_version' in update_data and update_data['os_version']:
                update_data['version'] = update_data['os_version']
                
            # Remove the duplicate/deprecated fields
            for field in ['ip_address', 'os_version', 'mac_address', 'agent_version', 'powershell_version']:
                if field in update_data:
                    del update_data[field]
            
            # Ensure IP address is properly set with fallback methods
            if not update_data.get("ip") or update_data.get("ip") in ["127.0.0.1", "localhost", None, ""]:
                # Try to get IP from system_info network_adapters
                system_info = update_data.get("system_info") or {}
                network_adapters = system_info.get("network_adapters", []) if isinstance(system_info, dict) else []
                
                if network_adapters and isinstance(network_adapters, list):
                    for adapter in network_adapters:
                        if isinstance(adapter, dict) and adapter.get("ip"):
                            ip = adapter.get("ip")
                            if ip and ip not in ["127.0.0.1", "localhost", "::1"]:
                                update_data["ip"] = ip
                                logger.info(f"Updated agent IP from network adapter: {ip}")
                                break
                
                # If still no valid IP, try system_info primary_ip
                if (not update_data.get("ip") or update_data.get("ip") in ["127.0.0.1", "localhost", None, ""]) and isinstance(system_info, dict) and system_info.get("primary_ip"):
                    primary_ip = system_info.get("primary_ip")
                    if primary_ip and primary_ip not in ["127.0.0.1", "localhost", "::1"]:
                        update_data["ip"] = primary_ip
                        logger.info(f"Updated agent IP from system_info primary_ip: {primary_ip}")
            
            update_data['status'] = 'online'
            update_data['last_seen'] = datetime.now().isoformat()
            
            db_manager.update_agent(existing_agent['id'], update_data)
            existing_agent.update(update_data)
            existing_agent['is_connected'] = websocket_manager.is_agent_connected(existing_agent['id'])
            
            logger.info(f"Agent {existing_agent['id']} updated during registration")
            return Agent(**existing_agent)
        
        # Create new agent - normalize field names
        agent_dict = agent_data.dict()
        
        # Map new field names to old ones for database compatibility
        if 'ip_address' in agent_dict and agent_dict['ip_address']:
            agent_dict['ip'] = agent_dict['ip_address']
        if 'os_version' in agent_dict and agent_dict['os_version']:
            agent_dict['version'] = agent_dict['os_version']
            
        # Remove the duplicate/deprecated fields
        for field in ['ip_address', 'os_version', 'mac_address', 'agent_version', 'powershell_version']:
            if field in agent_dict:
                del agent_dict[field]
        
        # Ensure IP address is properly set with fallback methods
        if not agent_dict.get("ip") or agent_dict.get("ip") in ["127.0.0.1", "localhost", None, ""]:
            # Try to get IP from system_info network_adapters
            system_info = agent_dict.get("system_info") or {}
            network_adapters = system_info.get("network_adapters", []) if isinstance(system_info, dict) else []
            
            if network_adapters and isinstance(network_adapters, list):
                for adapter in network_adapters:
                    if isinstance(adapter, dict) and adapter.get("ip"):
                        ip = adapter.get("ip")
                        if ip and ip not in ["127.0.0.1", "localhost", "::1"]:
                            agent_dict["ip"] = ip
                            logger.info(f"Set agent IP from network adapter: {ip}")
                            break
            
            # If still no valid IP, try system_info primary_ip
            if (not agent_dict.get("ip") or agent_dict.get("ip") in ["127.0.0.1", "localhost", None, ""]) and isinstance(system_info, dict) and system_info.get("primary_ip"):
                primary_ip = system_info.get("primary_ip")
                if primary_ip and primary_ip not in ["127.0.0.1", "localhost", "::1"]:
                    agent_dict["ip"] = primary_ip
                    logger.info(f"Set agent IP from system_info primary_ip: {primary_ip}")
        
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

@router.post("/{agent_id}/command", response_model=CommandResponse)
async def execute_agent_command(
    agent_id: str,
    command: PowerShellCommand,
    token: str = Depends(verify_token)
):
    """Execute a PowerShell command on a specific agent"""
    try:
        # Check if agent exists and is online
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected via WebSocket
        if agent_id not in websocket_manager.agent_connections:
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Execute command on agent via WebSocket
        # The websocket manager expects just the command string and handles the timeout internally
        try:
            response = await websocket_manager.execute_command_on_agent(agent_id, command.command)
            
            # Check if we got a valid response
            if response and response.get("status") != "error":
                success = response.get("success", False)
                output = response.get("output", "")
                error = response.get("error", None)
                execution_time = response.get("execution_time", 0.0)
                
                # Save command to history
                try:
                    db_manager.add_command_history(agent_id, {
                        'command': command.command,
                        'success': success,
                        'output': output,
                        'error': error,
                        'execution_time': execution_time
                    })
                except Exception as e:
                    logger.error(f"Failed to save command history: {str(e)}")
                
                # Convert agent response to CommandResponse
                return CommandResponse(
                    success=success,
                    output=output,
                    error=error,
                    execution_time=execution_time,
                    timestamp=response.get("timestamp", datetime.now().isoformat()),
                    command=command.command
                )
            else:
                # Command failed or timed out
                error_msg = response.get("message", "Command execution failed") if response else "No response from agent"
                
                # Save failure to history
                try:
                    db_manager.add_command_history(agent_id, {
                        'command': command.command,
                        'success': False,
                        'output': "",
                        'error': error_msg,
                        'execution_time': command.timeout or 30
                    })
                except Exception as e:
                    logger.error(f"Failed to save command history: {str(e)}")
                
                return CommandResponse(
                    success=False,
                    output="",
                    error=error_msg,
                    execution_time=command.timeout or 30,
                    timestamp=datetime.now().isoformat(),
                    command=command.command
                )
        except ValueError as e:
            # Agent not connected or other error
            logger.error(f"Command execution error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing command on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute command on agent")

@router.get("/{agent_id}/commands", response_model=List[CommandResponse])
async def get_agent_command_history(
    agent_id: str,
    limit: int = 50,
    token: str = Depends(verify_token)
):
    """Get command execution history for a specific agent"""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get command history from database
        commands = db_manager.get_command_history(agent_id, limit)
        
        # Transform the command history data to CommandResponse format
        command_responses = []
        for cmd in commands:
            # Handle timestamp - it might already be a string from the database
            timestamp = cmd.get('timestamp')
            if timestamp:
                # If it's a datetime object, convert to ISO format
                if hasattr(timestamp, 'isoformat'):
                    timestamp = timestamp.isoformat()
                # Otherwise it's already a string
            else:
                timestamp = datetime.now().isoformat()
            
            command_responses.append(CommandResponse(
                success=cmd.get('success', False),
                output=cmd.get('output', ''),
                error=cmd.get('error'),
                execution_time=cmd.get('execution_time', 0.0),
                timestamp=timestamp,
                command=cmd.get('command', '')
            ))
        
        return command_responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting command history for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get command history")

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
        
        # If agent is connected, request system info via WebSocket
        if is_connected:
            try:
                # Request system info from agent
                request_id = await websocket_manager.request_system_info(agent_id)
                logger.info(f"System info request {request_id} sent to agent {agent_id}")
                
                # Wait briefly for agent to respond (we'll handle the actual update via WebSocket)
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error requesting system info from agent {agent_id}: {str(e)}")
        
        # Update agent status based on connection
        status = 'online' if is_connected else 'offline'
        update_data = {
            'status': status,
            'last_seen': datetime.now().isoformat()
        }
        
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


@router.get("/status/{agent_id}")
async def get_agent_status(agent_id: str, token: str = Depends(verify_token)):
    """Get detailed status of an agent including heartbeat timing"""
    try:
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected via WebSocket
        is_websocket_connected = websocket_manager.is_agent_connected(agent_id)
        
        # Check heartbeat timing
        last_seen_str = agent_data.get('last_seen')
        heartbeat_status = "unknown"
        seconds_since_heartbeat = None
        
        if last_seen_str:
            try:
                last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                seconds_since_heartbeat = (datetime.now() - last_seen).total_seconds()
                
                if seconds_since_heartbeat < 30:
                    heartbeat_status = "recent"
                elif seconds_since_heartbeat < 60:
                    heartbeat_status = "stale"
                else:
                    heartbeat_status = "offline"
            except ValueError:
                heartbeat_status = "invalid_timestamp"
        
        # Determine overall status
        if is_websocket_connected:
            overall_status = "online"
        elif heartbeat_status == "recent":
            overall_status = "online"
        elif heartbeat_status == "stale":
            overall_status = "warning"
        else:
            overall_status = "offline"
        
        status_info = {
            "agent_id": agent_id,
            "overall_status": overall_status,
            "websocket_connected": is_websocket_connected,
            "heartbeat_status": heartbeat_status,
            "seconds_since_heartbeat": seconds_since_heartbeat,
            "last_seen": last_seen_str,
            "agent_data": Agent(**agent_data)
        }
        
        return status_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status {agent_id}: {str(e)}")
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

@router.post("/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str, token: str = Depends(verify_token)):
    """Agent heartbeat endpoint - called every 30 seconds to indicate agent is online"""
    try:
        logger.info(f"Heartbeat received from agent {agent_id}")
        
        # Verify agent exists
        agent = db_manager.get_agent(agent_id)
        if not agent:
            logger.error(f"Agent {agent_id} not found for heartbeat")
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get system information
        system_info = {}
        try:
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
        
        # Update agent status
        update_data = {
            'status': 'online',
            'last_seen': datetime.now().isoformat()
        }
        
        # Add system info if available
        if system_info:
            update_data['system_info'] = system_info
        
        logger.info(f"Updating agent {agent_id} heartbeat with data: {update_data}")
        success = db_manager.update_agent(agent_id, update_data)
        
        if not success:
            logger.error(f"Failed to update agent {agent_id} heartbeat")
            raise HTTPException(status_code=500, detail="Failed to update agent heartbeat")
        
        # Get updated agent data
        updated_agent = db_manager.get_agent(agent_id)
        updated_agent['is_connected'] = websocket_manager.is_agent_connected(agent_id)
        
        logger.info(f"Agent {agent_id} heartbeat updated successfully")
        
        return {
            "message": "Heartbeat received",
            "agent": Agent(**updated_agent),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing heartbeat for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/bulk", response_model=BulkOperationResult)
async def bulk_agent_operation(
    bulk_operation: BulkAgentOperation,
    token: str = Depends(verify_token)
):
    """Perform bulk operations on multiple agents"""
    try:
        logger.info(f"Bulk operation requested: {bulk_operation.operation} on {len(bulk_operation.agent_ids)} agents")
        
        successful = []
        failed = []
        results = {}
        
        # Validate operation type
        valid_operations = ['refresh', 'restart', 'shutdown', 'status', 'update_tags']
        if bulk_operation.operation not in valid_operations:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid operation '{bulk_operation.operation}'. Valid operations: {valid_operations}"
            )
        
        # Validate agent IDs are not empty
        if not bulk_operation.agent_ids:
            raise HTTPException(status_code=400, detail="Agent IDs list cannot be empty")
        
        # Process each agent
        for agent_id in bulk_operation.agent_ids:
            try:
                # Verify agent exists
                agent_data = db_manager.get_agent(agent_id)
                if not agent_data:
                    failed.append({
                        "agent_id": agent_id,
                        "error": "Agent not found"
                    })
                    continue
                
                # Perform the requested operation
                if bulk_operation.operation == "refresh":
                    # Check if agent is connected and update status
                    is_connected = websocket_manager.is_agent_connected(agent_id)
                    
                    if is_connected:
                        try:
                            # Request system info from agent
                            request_id = await websocket_manager.request_system_info(agent_id)
                            logger.info(f"System info request {request_id} sent to agent {agent_id}")
                            await asyncio.sleep(0.1)  # Brief wait for response
                        except Exception as e:
                            logger.warning(f"Could not request system info from agent {agent_id}: {str(e)}")
                    
                    # Update agent status
                    status = 'online' if is_connected else 'offline'
                    update_data = {
                        'status': status,
                        'last_seen': datetime.now().isoformat()
                    }
                    
                    success = db_manager.update_agent(agent_id, update_data)
                    if success:
                        successful.append(agent_id)
                        updated_agent = db_manager.get_agent(agent_id)
                        updated_agent['is_connected'] = is_connected
                        results[agent_id] = {
                            "agent": Agent(**updated_agent),
                            "message": "Agent refreshed successfully"
                        }
                    else:
                        failed.append({
                            "agent_id": agent_id,
                            "error": "Failed to refresh agent data"
                        })
                
                elif bulk_operation.operation == "restart":
                    # Check if agent is connected via WebSocket
                    if not websocket_manager.is_agent_connected(agent_id):
                        failed.append({
                            "agent_id": agent_id,
                            "error": "Agent is not connected"
                        })
                        continue
                    
                    try:
                        # Send restart command to agent
                        command_data = {
                            "command": "Restart-Computer -Force",
                            "timeout": 30,
                            "run_as_admin": True
                        }
                        command_id = await websocket_manager.execute_command_on_agent(agent_id, command_data)
                        successful.append(agent_id)
                        results[agent_id] = {
                            "message": "Restart command sent successfully",
                            "command_id": command_id
                        }
                    except Exception as e:
                        failed.append({
                            "agent_id": agent_id,
                            "error": f"Failed to send restart command: {str(e)}"
                        })
                
                elif bulk_operation.operation == "shutdown":
                    # Check if agent is connected via WebSocket
                    if not websocket_manager.is_agent_connected(agent_id):
                        failed.append({
                            "agent_id": agent_id,
                            "error": "Agent is not connected"
                        })
                        continue
                    
                    try:
                        # Send shutdown command to agent
                        command_data = {
                            "command": "Stop-Computer -Force",
                            "timeout": 30,
                            "run_as_admin": True
                        }
                        command_id = await websocket_manager.execute_command_on_agent(agent_id, command_data)
                        successful.append(agent_id)
                        results[agent_id] = {
                            "message": "Shutdown command sent successfully",
                            "command_id": command_id
                        }
                    except Exception as e:
                        failed.append({
                            "agent_id": agent_id,
                            "error": f"Failed to send shutdown command: {str(e)}"
                        })
                
                elif bulk_operation.operation == "status":
                    # Get detailed status for agent
                    is_connected = websocket_manager.is_agent_connected(agent_id)
                    
                    # Check heartbeat timing
                    last_seen_str = agent_data.get('last_seen')
                    heartbeat_status = "unknown"
                    seconds_since_heartbeat = None
                    
                    if last_seen_str:
                        try:
                            last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                            seconds_since_heartbeat = (datetime.now() - last_seen).total_seconds()
                            
                            if seconds_since_heartbeat < 30:
                                heartbeat_status = "recent"
                            elif seconds_since_heartbeat < 60:
                                heartbeat_status = "stale"
                            else:
                                heartbeat_status = "offline"
                        except ValueError:
                            heartbeat_status = "invalid_timestamp"
                    
                    # Determine overall status
                    if is_connected:
                        overall_status = "online"
                    elif heartbeat_status == "recent":
                        overall_status = "online"
                    elif heartbeat_status == "stale":
                        overall_status = "warning"
                    else:
                        overall_status = "offline"
                    
                    successful.append(agent_id)
                    agent_data['is_connected'] = is_connected
                    results[agent_id] = {
                        "agent": Agent(**agent_data),
                        "overall_status": overall_status,
                        "websocket_connected": is_connected,
                        "heartbeat_status": heartbeat_status,
                        "seconds_since_heartbeat": seconds_since_heartbeat,
                        "last_seen": last_seen_str
                    }
                
                elif bulk_operation.operation == "update_tags":
                    # Update agent tags
                    tags = getattr(bulk_operation, 'tags', []) or []
                    
                    # Update the agent's tags in the database
                    update_data = {'tags': tags}
                    db_manager.update_agent(agent_id, update_data)
                    
                    # Get updated agent data
                    updated_agent = db_manager.get_agent(agent_id)
                    if updated_agent:
                        successful.append(agent_id)
                        updated_agent['is_connected'] = websocket_manager.is_agent_connected(agent_id)
                        results[agent_id] = {
                            "agent": Agent(**updated_agent),
                            "previous_tags": agent_data.get('tags', []),
                            "new_tags": tags
                        }
                    else:
                        failed.append({
                            "agent_id": agent_id,
                            "error": "Failed to update agent tags"
                        })
                
            except Exception as e:
                logger.error(f"Error processing bulk operation for agent {agent_id}: {str(e)}")
                failed.append({
                    "agent_id": agent_id,
                    "error": f"Internal error: {str(e)}"
                })
        
        logger.info(f"Bulk operation {bulk_operation.operation} completed: {len(successful)} successful, {len(failed)} failed")
        
        return BulkOperationResult(
            operation=bulk_operation.operation,
            total_agents=len(bulk_operation.agent_ids),
            successful=successful,
            failed=failed,
            results=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing bulk agent operation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 