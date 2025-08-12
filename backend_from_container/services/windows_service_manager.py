import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .powershell_service import PowerShellService
from ..schemas.services import (
    ServiceInfo,
    ServiceStatus,
    ServiceStartType,
    ServiceActionResponse,
    ServiceConfigResponse,
    ServiceDependencyGraph
)

logger = logging.getLogger(__name__)


class WindowsServiceManager:
    def __init__(self):
        self.powershell_service = PowerShellService()

    async def get_services(self, agent_id: str, filter_query: Optional[str] = None) -> List[ServiceInfo]:
        """Get list of Windows services from agent"""
        try:
            command = """
            $services = Get-Service | Select-Object Name, DisplayName, Status, StartType, @{Name='CanStop';Expression={$_.CanStop}}, @{Name='CanPauseAndContinue';Expression={$_.CanPauseAndContinue}}
            $serviceDetails = @()
            foreach ($service in $services) {
                $wmiService = Get-WmiObject -Class Win32_Service -Filter "Name='$($service.Name)'" -ErrorAction SilentlyContinue
                $dependencies = (Get-Service -Name $service.Name).DependentServices.Name
                $requiredServices = (Get-Service -Name $service.Name).RequiredServices.Name
                
                $serviceInfo = @{
                    Name = $service.Name
                    DisplayName = $service.DisplayName
                    Status = $service.Status.ToString()
                    StartType = $service.StartType.ToString()
                    CanStop = $service.CanStop
                    CanPauseAndContinue = $service.CanPauseAndContinue
                    Description = if ($wmiService) { $wmiService.Description } else { $null }
                    Path = if ($wmiService) { $wmiService.PathName } else { $null }
                    AccountName = if ($wmiService) { $wmiService.StartName } else { $null }
                    ProcessId = if ($wmiService) { $wmiService.ProcessId } else { 0 }
                    Dependencies = @($requiredServices)
                    DependentServices = @($dependencies)
                }
                $serviceDetails += $serviceInfo
            }
            ConvertTo-Json $serviceDetails -Depth 3
            """

            if filter_query:
                command = f"""
                $filter = "{filter_query}"
                """ + command.replace("Get-Service |", f"Get-Service | Where-Object {{$_.Name -like '*$filter*' -or $_.DisplayName -like '*$filter*'}} |")

            result = await self.powershell_service.execute_command(agent_id, command, None)

            if result and result.get("success") == True:
                services_data = json.loads(result.get("output", "[]"))
                services = []
                for svc in services_data:
                    service = ServiceInfo(
                        name=svc["Name"],
                        display_name=svc["DisplayName"],
                        status=ServiceStatus(svc["Status"]),
                        start_type=self._map_start_type(svc["StartType"]),
                        description=svc.get("Description"),
                        can_stop=svc.get("CanStop", False),
                        can_pause_and_continue=svc.get("CanPauseAndContinue", False),
                        dependencies=svc.get("Dependencies", []),
                        dependent_services=svc.get("DependentServices", []),
                        path=svc.get("Path"),
                        account_name=svc.get("AccountName"),
                        process_id=svc.get("ProcessId", 0) if svc.get("ProcessId") else None
                    )
                    services.append(service)
                return services
            return []

        except Exception as e:
            logger.error(f"Error getting services: {str(e)}")
            return []

    async def start_service(self, agent_id: str, service_name: str, force: bool = False) -> ServiceActionResponse:
        """Start a Windows service"""
        try:
            command = f"Start-Service -Name '{service_name}'"
            if force:
                command += " -Force"
            
            result = await self.powershell_service.execute_command(agent_id, command, None)

            success = result and result.get("success") == True
            
            # Get new status
            new_status = None
            if success:
                status_cmd = f"(Get-Service -Name '{service_name}').Status.ToString()"
                status_result = await self.powershell_service.execute_command(agent_id, status_cmd, None)
                if status_result and status_result.get("success") == True:
                    new_status = ServiceStatus(status_result.get("output", "").strip())
                    
                    # Note: Status update broadcast removed for simplicity

            return ServiceActionResponse(
                success=success,
                message=result.get("output", "") if result else "Failed to start service",
                service_name=service_name,
                new_status=new_status,
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Error starting service {service_name}: {str(e)}")
            return ServiceActionResponse(
                success=False,
                message=str(e),
                service_name=service_name,
                timestamp=datetime.utcnow()
            )

    async def stop_service(self, agent_id: str, service_name: str, force: bool = False) -> ServiceActionResponse:
        """Stop a Windows service"""
        try:
            command = f"Stop-Service -Name '{service_name}'"
            if force:
                command += " -Force"
            
            result = await self.powershell_service.execute_command(agent_id, command, None)

            success = result and result.get("success") == True
            
            # Get new status
            new_status = None
            if success:
                status_cmd = f"(Get-Service -Name '{service_name}').Status.ToString()"
                status_result = await self.powershell_service.execute_command(agent_id, status_cmd, None)
                if status_result and status_result.get("success") == True:
                    new_status = ServiceStatus(status_result.get("output", "").strip())
                    
                    # Broadcast status update
                    # await self.websocket_manager.broadcast_service_update(
                    #     agent_id, service_name, new_status.value
                    # )

            return ServiceActionResponse(
                success=success,
                message=result.get("output", "") if result else "Failed to stop service",
                service_name=service_name,
                new_status=new_status,
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Error stopping service {service_name}: {str(e)}")
            return ServiceActionResponse(
                success=False,
                message=str(e),
                service_name=service_name,
                timestamp=datetime.utcnow()
            )

    async def restart_service(self, agent_id: str, service_name: str, force: bool = False) -> ServiceActionResponse:
        """Restart a Windows service"""
        try:
            command = f"Restart-Service -Name '{service_name}'"
            if force:
                command += " -Force"
            
            result = await self.powershell_service.execute_command(agent_id, command, None)

            success = result and result.get("success") == True
            
            # Get new status
            new_status = None
            if success:
                status_cmd = f"(Get-Service -Name '{service_name}').Status.ToString()"
                status_result = await self.powershell_service.execute_command(agent_id, status_cmd, None)
                if status_result and status_result.get("success") == True:
                    new_status = ServiceStatus(status_result.get("output", "").strip())
                    
                    # Broadcast status update
                    # await self.websocket_manager.broadcast_service_update(
                    #     agent_id, service_name, new_status.value
                    # )

            return ServiceActionResponse(
                success=success,
                message=result.get("output", "") if result else "Failed to restart service",
                service_name=service_name,
                new_status=new_status,
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Error restarting service {service_name}: {str(e)}")
            return ServiceActionResponse(
                success=False,
                message=str(e),
                service_name=service_name,
                timestamp=datetime.utcnow()
            )

    async def configure_service(self, agent_id: str, service_name: str, config: Dict[str, Any]) -> ServiceConfigResponse:
        """Configure a Windows service"""
        try:
            commands = []
            
            if "start_type" in config:
                start_type_map = {
                    "Automatic": "Automatic",
                    "AutomaticDelayedStart": "AutomaticDelayedStart",
                    "Manual": "Manual",
                    "Disabled": "Disabled"
                }
                ps_start_type = start_type_map.get(config["start_type"])
                if ps_start_type:
                    commands.append(f"Set-Service -Name '{service_name}' -StartupType {ps_start_type}")
            
            if "display_name" in config:
                commands.append(f"Set-Service -Name '{service_name}' -DisplayName '{config['display_name']}'")
            
            if "description" in config:
                commands.append(f"Set-Service -Name '{service_name}' -Description '{config['description']}'")

            success = True
            messages = []
            
            for cmd in commands:
                result = await self.websocket_manager.execute_command_on_agent(
                    agent_id,
                    cmd,
                    command_type="powershell"
                )
                if not result or result.get("status") != "success":
                    success = False
                    messages.append(f"Failed: {cmd}")
                else:
                    messages.append(f"Success: {cmd}")

            # Get updated configuration
            get_config_cmd = f"""
            $service = Get-WmiObject -Class Win32_Service -Filter "Name='{service_name}'"
            @{{
                Name = $service.Name
                DisplayName = $service.DisplayName
                StartType = $service.StartMode
                Description = $service.Description
                PathName = $service.PathName
                StartName = $service.StartName
            }} | ConvertTo-Json
            """
            
            config_result = await self.websocket_manager.execute_command_on_agent(
                agent_id,
                get_config_cmd,
                command_type="powershell"
            )
            
            updated_config = {}
            if config_result and config_result.get("success") == True:
                updated_config = json.loads(config_result.get("output", "{}"))

            return ServiceConfigResponse(
                success=success,
                message="; ".join(messages),
                service_name=service_name,
                config=updated_config,
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Error configuring service {service_name}: {str(e)}")
            return ServiceConfigResponse(
                success=False,
                message=str(e),
                service_name=service_name,
                config={},
                timestamp=datetime.utcnow()
            )

    async def get_service_dependencies(self, agent_id: str, service_name: str) -> ServiceDependencyGraph:
        """Get service dependency graph"""
        try:
            command = f"""
            $service = Get-Service -Name '{service_name}'
            $dependencies = @{{
                ServiceName = $service.Name
                DisplayName = $service.DisplayName
                Status = $service.Status.ToString()
                RequiredServices = @()
                DependentServices = @()
            }}
            
            foreach ($req in $service.RequiredServices) {{
                $dependencies.RequiredServices += @{{
                    Name = $req.Name
                    DisplayName = $req.DisplayName
                    Status = $req.Status.ToString()
                }}
            }}
            
            foreach ($dep in $service.DependentServices) {{
                $dependencies.DependentServices += @{{
                    Name = $dep.Name
                    DisplayName = $dep.DisplayName
                    Status = $dep.Status.ToString()
                }}
            }}
            
            ConvertTo-Json $dependencies -Depth 3
            """

            result = await self.powershell_service.execute_command(agent_id, command, None)

            if result and result.get("success") == True:
                dep_data = json.loads(result.get("output", "{}"))
                
                # Build graph data for visualization
                graph_data = {
                    "nodes": [
                        {
                            "id": service_name,
                            "label": dep_data.get("DisplayName", service_name),
                            "status": dep_data.get("Status"),
                            "type": "main"
                        }
                    ],
                    "edges": []
                }
                
                # Add required services as dependencies
                for req in dep_data.get("RequiredServices", []):
                    graph_data["nodes"].append({
                        "id": req["Name"],
                        "label": req["DisplayName"],
                        "status": req["Status"],
                        "type": "dependency"
                    })
                    graph_data["edges"].append({
                        "from": req["Name"],
                        "to": service_name,
                        "type": "requires"
                    })
                
                # Add dependent services
                for dep in dep_data.get("DependentServices", []):
                    graph_data["nodes"].append({
                        "id": dep["Name"],
                        "label": dep["DisplayName"],
                        "status": dep["Status"],
                        "type": "dependent"
                    })
                    graph_data["edges"].append({
                        "from": service_name,
                        "to": dep["Name"],
                        "type": "required_by"
                    })
                
                return ServiceDependencyGraph(
                    service_name=service_name,
                    dependencies=dep_data.get("RequiredServices", []),
                    dependent_services=dep_data.get("DependentServices", []),
                    graph_data=graph_data
                )
            
            return ServiceDependencyGraph(
                service_name=service_name,
                dependencies=[],
                dependent_services=[],
                graph_data={"nodes": [], "edges": []}
            )

        except Exception as e:
            logger.error(f"Error getting service dependencies for {service_name}: {str(e)}")
            return ServiceDependencyGraph(
                service_name=service_name,
                dependencies=[],
                dependent_services=[],
                graph_data={"nodes": [], "edges": []}
            )

    def _map_start_type(self, start_type: str) -> ServiceStartType:
        """Map Windows service start type to enum"""
        mapping = {
            "Automatic": ServiceStartType.AUTOMATIC,
            "AutomaticDelayedStart": ServiceStartType.AUTOMATIC_DELAYED,
            "Manual": ServiceStartType.MANUAL,
            "Disabled": ServiceStartType.DISABLED,
            "Boot": ServiceStartType.BOOT,
            "System": ServiceStartType.SYSTEM
        }
        return mapping.get(start_type, ServiceStartType.MANUAL)