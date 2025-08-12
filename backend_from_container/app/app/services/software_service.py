"""Software management service for DexAgents."""
import asyncio
import hashlib
import json
import os
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

import psycopg2
from app.core.config import settings
from app.core.websocket_manager import websocket_manager
from app.models.software import (
    SoftwarePackage, InstalledSoftware, InstallationJob,
    SoftwareRepository, PackageType, InstallationStatus
)
from app.services.powershell_service import PowerShellService
import logging

logger = logging.getLogger(__name__)


class SoftwareService:
    """Service for managing software installations."""
    
    def __init__(self):
        self.powershell_service = PowerShellService()
        self.package_storage_path = Path("/app/data/software_packages")
        self.package_storage_path.mkdir(parents=True, exist_ok=True)
    
    async def get_installed_software(self, agent_id: str, refresh: bool = False) -> List[Dict[str, Any]]:
        """Get installed software list from an agent."""
        try:
            # PowerShell script to get installed software
            script = """
            $software = @()
            
            # Get software from Registry (32-bit and 64-bit)
            $paths = @(
                'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',
                'HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*'
            )
            
            foreach ($path in $paths) {
                Get-ItemProperty $path -ErrorAction SilentlyContinue | 
                Where-Object { $_.DisplayName -and $_.DisplayName -ne '' } |
                ForEach-Object {
                    $software += @{
                        Name = $_.DisplayName
                        Version = $_.DisplayVersion
                        Vendor = $_.Publisher
                        InstallDate = $_.InstallDate
                        InstallLocation = $_.InstallLocation
                        UninstallString = $_.UninstallString
                        RegistryKey = $_.PSPath
                        EstimatedSize = $_.EstimatedSize
                    }
                }
            }
            
            # Get Windows Store apps
            Get-AppxPackage | ForEach-Object {
                $software += @{
                    Name = $_.Name
                    Version = $_.Version
                    Vendor = $_.Publisher
                    InstallLocation = $_.InstallLocation
                    PackageType = 'WindowsStore'
                }
            }
            
            $software | ConvertTo-Json -Depth 3
            """
            
            # Execute PowerShell script on agent
            # TODO: Implement agent-specific PowerShell execution via WebSocket
            # For now, return mock data
            result = {
                'success': True,
                'output': '[]'  # Empty software list for now
            }
            
            if result.get('success'):
                software_list = json.loads(result.get('output', '[]'))
                
                # Store in database if refresh requested
                if refresh:
                    await self._update_software_inventory(agent_id, software_list)
                
                return software_list
            else:
                logger.error(f"Failed to get software inventory: {result.get('error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting installed software: {str(e)}")
            return []
    
    async def install_software(
        self,
        agent_id: str,
        package_id: Optional[int] = None,
        package_name: Optional[str] = None,
        package_type: PackageType = PackageType.EXE,
        version: Optional[str] = None,
        silent: bool = True,
        custom_args: Optional[str] = None,
        install_script: Optional[str] = None
    ) -> Dict[str, Any]:
        """Install software on an agent."""
        try:
            # Create installation job
            job = await self._create_installation_job(
                agent_id=agent_id,
                package_id=package_id,
                status=InstallationStatus.PENDING
            )
            
            # Update job status
            await self._update_job_status(
                job['id'],
                InstallationStatus.DOWNLOADING,
                progress=10,
                current_step="Preparing installation"
            )
            
            # Determine installation method
            if package_type == PackageType.CHOCOLATEY:
                result = await self._install_chocolatey(
                    agent_id, package_name, version, job['id']
                )
            elif package_type == PackageType.WINGET:
                result = await self._install_winget(
                    agent_id, package_name, version, job['id']
                )
            elif package_type == PackageType.POWERSHELL and install_script:
                result = await self._install_powershell(
                    agent_id, install_script, job['id']
                )
            elif package_id:
                # Install from package repository
                package = await self._get_package(package_id)
                if package:
                    result = await self._install_package(
                        agent_id, package, silent, custom_args, job['id']
                    )
                else:
                    result = {'success': False, 'error': 'Package not found'}
            else:
                result = {'success': False, 'error': 'Invalid installation parameters'}
            
            # Update final job status
            if result.get('success'):
                await self._update_job_status(
                    job['id'],
                    InstallationStatus.COMPLETED,
                    progress=100,
                    current_step="Installation completed",
                    output_log=result.get('output')
                )
            else:
                await self._update_job_status(
                    job['id'],
                    InstallationStatus.FAILED,
                    error_message=result.get('error'),
                    output_log=result.get('output')
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error installing software: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def uninstall_software(
        self,
        agent_id: str,
        software_id: Optional[int] = None,
        software_name: Optional[str] = None,
        silent: bool = True,
        custom_args: Optional[str] = None
    ) -> Dict[str, Any]:
        """Uninstall software from an agent."""
        try:
            # Get software information
            if software_id:
                software = await self._get_installed_software_by_id(software_id)
            elif software_name:
                software = await self._get_installed_software_by_name(agent_id, software_name)
            else:
                return {'success': False, 'error': 'Software identifier required'}
            
            if not software:
                return {'success': False, 'error': 'Software not found'}
            
            # Build uninstall command
            uninstall_string = software.get('uninstall_string')
            if uninstall_string:
                # Add silent flags if requested
                if silent and '/quiet' not in uninstall_string.lower():
                    uninstall_string += ' /quiet /norestart'
                if custom_args:
                    uninstall_string += f' {custom_args}'
                
                # Execute uninstall command
                script = f"""
                Start-Process -FilePath cmd.exe -ArgumentList '/c', '{uninstall_string}' -Wait -NoNewWindow
                $LASTEXITCODE
                """
                
                # TODO: Implement agent-specific PowerShell execution
                result = {'success': True, 'output': 'Mock uninstall'}
                
                return result
            else:
                # Try alternative uninstall methods
                return await self._uninstall_alternative(agent_id, software, silent)
                
        except Exception as e:
            logger.error(f"Error uninstalling software: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def upload_package(
        self,
        file_content: bytes,
        filename: str,
        package_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upload a software package to the repository."""
        try:
            # Calculate checksum
            checksum = hashlib.sha256(file_content).hexdigest()
            
            # Save file
            file_path = self.package_storage_path / filename
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Create package record
            package = SoftwarePackage(
                id=await self._get_next_package_id(),
                name=package_info.get('name', filename),
                version=package_info.get('version', '1.0.0'),
                description=package_info.get('description'),
                package_type=PackageType(package_info.get('package_type', 'exe')),
                vendor=package_info.get('vendor'),
                size_bytes=len(file_content),
                file_path=str(file_path),
                silent_install_args=package_info.get('silent_install_args'),
                silent_uninstall_args=package_info.get('silent_uninstall_args'),
                checksum=checksum
            )
            
            # Save to database
            await self._save_package(package)
            
            return {
                'success': True,
                'package_id': package.id,
                'filename': filename,
                'size_bytes': len(file_content),
                'checksum': checksum,
                'upload_path': str(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error uploading package: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _install_chocolatey(
        self,
        agent_id: str,
        package_name: str,
        version: Optional[str],
        job_id: int
    ) -> Dict[str, Any]:
        """Install software using Chocolatey."""
        try:
            # Check if Chocolatey is installed
            check_script = "Get-Command choco -ErrorAction SilentlyContinue"
            # TODO: Implement agent-specific PowerShell execution
            check_result = {'success': False, 'output': ''}
            
            if not check_result.get('success') or not check_result.get('output'):
                # Install Chocolatey first
                await self._update_job_status(
                    job_id,
                    InstallationStatus.INSTALLING,
                    progress=20,
                    current_step="Installing Chocolatey"
                )
                
                install_choco = """
                Set-ExecutionPolicy Bypass -Scope Process -Force
                [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
                iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
                """
                
                # TODO: Implement agent-specific PowerShell execution
                pass
            
            # Install package
            await self._update_job_status(
                job_id,
                InstallationStatus.INSTALLING,
                progress=50,
                current_step=f"Installing {package_name}"
            )
            
            install_cmd = f"choco install {package_name} -y --no-progress"
            if version:
                install_cmd += f" --version={version}"
            
            # TODO: Implement agent-specific PowerShell execution
            result = {'success': True, 'output': 'Mock Chocolatey install'}
            
            return result
            
        except Exception as e:
            logger.error(f"Error with Chocolatey installation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _install_winget(
        self,
        agent_id: str,
        package_name: str,
        version: Optional[str],
        job_id: int
    ) -> Dict[str, Any]:
        """Install software using Windows Package Manager (winget)."""
        try:
            await self._update_job_status(
                job_id,
                InstallationStatus.INSTALLING,
                progress=50,
                current_step=f"Installing {package_name} via winget"
            )
            
            install_cmd = f"winget install {package_name} --silent --accept-package-agreements --accept-source-agreements"
            if version:
                install_cmd += f" --version {version}"
            
            # TODO: Implement agent-specific PowerShell execution
            result = {'success': True, 'output': 'Mock winget install'}
            
            return result
            
        except Exception as e:
            logger.error(f"Error with winget installation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _install_powershell(
        self,
        agent_id: str,
        install_script: str,
        job_id: int
    ) -> Dict[str, Any]:
        """Install software using custom PowerShell script."""
        try:
            await self._update_job_status(
                job_id,
                InstallationStatus.INSTALLING,
                progress=50,
                current_step="Executing installation script"
            )
            
            # TODO: Implement agent-specific PowerShell execution
            result = {'success': True, 'output': 'Mock PowerShell install'}
            
            return result
            
        except Exception as e:
            logger.error(f"Error with PowerShell installation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _install_package(
        self,
        agent_id: str,
        package: Dict[str, Any],
        silent: bool,
        custom_args: Optional[str],
        job_id: int
    ) -> Dict[str, Any]:
        """Install a package from repository."""
        try:
            # Transfer package file to agent
            await self._update_job_status(
                job_id,
                InstallationStatus.DOWNLOADING,
                progress=30,
                current_step="Transferring package to agent"
            )
            
            # Read package file
            file_path = package.get('file_path')
            if not file_path or not os.path.exists(file_path):
                return {'success': False, 'error': 'Package file not found'}
            
            # Create installation script based on package type
            package_type = package.get('package_type')
            filename = os.path.basename(file_path)
            temp_path = f"C:\\Temp\\{filename}"
            
            if package_type == 'msi':
                install_cmd = f"msiexec /i {temp_path}"
                if silent:
                    install_cmd += " /quiet /norestart"
                if package.get('silent_install_args'):
                    install_cmd += f" {package['silent_install_args']}"
            elif package_type == 'exe':
                install_cmd = f"{temp_path}"
                if silent and package.get('silent_install_args'):
                    install_cmd += f" {package['silent_install_args']}"
                elif silent:
                    install_cmd += " /S /quiet"
            else:
                install_cmd = package.get('install_script', '')
            
            if custom_args:
                install_cmd += f" {custom_args}"
            
            # Execute installation
            await self._update_job_status(
                job_id,
                InstallationStatus.INSTALLING,
                progress=60,
                current_step="Installing package"
            )
            
            script = f"""
            # Ensure temp directory exists
            New-Item -ItemType Directory -Force -Path C:\\Temp | Out-Null
            
            # Download package (in real implementation, use file transfer)
            # For now, assume file is transferred
            
            # Execute installation
            Start-Process -FilePath cmd.exe -ArgumentList '/c', '{install_cmd}' -Wait -NoNewWindow
            $LASTEXITCODE
            """
            
            # TODO: Implement agent-specific PowerShell execution
            result = {'success': True, 'output': 'Mock package install'}
            
            return result
            
        except Exception as e:
            logger.error(f"Error installing package: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _uninstall_alternative(
        self,
        agent_id: str,
        software: Dict[str, Any],
        silent: bool
    ) -> Dict[str, Any]:
        """Try alternative uninstall methods."""
        try:
            software_name = software.get('name')
            
            # Try using WMIC
            script = f"""
            $product = Get-WmiObject -Class Win32_Product | Where-Object {{$_.Name -eq '{software_name}'}}
            if ($product) {{
                $product.Uninstall()
                "Uninstalled successfully"
            }} else {{
                "Product not found"
            }}
            """
            
            # TODO: Implement agent-specific PowerShell execution
            result = {'success': True, 'output': 'Mock alternative uninstall'}
            
            return result
            
        except Exception as e:
            logger.error(f"Error with alternative uninstall: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _create_installation_job(
        self,
        agent_id: str,
        package_id: Optional[int],
        status: InstallationStatus
    ) -> Dict[str, Any]:
        """Create an installation job record."""
        try:
            conn = psycopg2.connect(settings.DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO installation_jobs 
                (agent_id, package_id, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                agent_id,
                package_id,
                status.value,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            job_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {'id': job_id, 'agent_id': agent_id, 'package_id': package_id}
            
        except Exception as e:
            logger.error(f"Error creating installation job: {str(e)}")
            return {}
    
    async def _update_job_status(
        self,
        job_id: int,
        status: InstallationStatus,
        progress: Optional[int] = None,
        current_step: Optional[str] = None,
        error_message: Optional[str] = None,
        output_log: Optional[str] = None
    ) -> None:
        """Update installation job status."""
        try:
            conn = psycopg2.connect(settings.DATABASE_URL)
            cursor = conn.cursor()
            
            updates = ["status = %s", "updated_at = %s"]
            values = [status.value, datetime.now().isoformat()]
            
            if progress is not None:
                updates.append("progress_percent = %s")
                values.append(progress)
            
            if current_step:
                updates.append("current_step = %s")
                values.append(current_step)
            
            if error_message:
                updates.append("error_message = %s")
                values.append(error_message)
            
            if output_log:
                updates.append("output_log = %s")
                values.append(output_log)
            
            if status == InstallationStatus.INSTALLING and not updates.count("started_at = %s"):
                updates.append("started_at = %s")
                values.append(datetime.now().isoformat())
            
            if status in [InstallationStatus.COMPLETED, InstallationStatus.FAILED]:
                updates.append("completed_at = %s")
                values.append(datetime.now().isoformat())
            
            values.append(job_id)
            
            cursor.execute(f"""
                UPDATE installation_jobs 
                SET {', '.join(updates)}
                WHERE id = %s
            """, values)
            
            conn.commit()
            conn.close()
            
            # Send WebSocket update
            await websocket_manager.broadcast({
                'type': 'installation_progress',
                'job_id': job_id,
                'status': status.value,
                'progress': progress,
                'current_step': current_step,
                'error_message': error_message
            })
            
        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
    
    async def _get_package(self, package_id: int) -> Optional[Dict[str, Any]]:
        """Get package information from database."""
        try:
            conn = psycopg2.connect(settings.DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM software_packages WHERE id = %s
            """, (package_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting package: {str(e)}")
            return None
    
    async def _save_package(self, package: SoftwarePackage) -> None:
        """Save package to database."""
        try:
            conn = psycopg2.connect(settings.DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO software_packages 
                (name, version, description, package_type, vendor, size_bytes,
                 file_path, silent_install_args, checksum, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                package.name,
                package.version,
                package.description,
                package.package_type.value,
                package.vendor,
                package.size_bytes,
                package.file_path,
                package.silent_install_args,
                package.checksum,
                package.created_at.isoformat(),
                package.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving package: {str(e)}")
    
    async def _get_next_package_id(self) -> int:
        """Get next available package ID."""
        try:
            conn = psycopg2.connect(settings.DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("SELECT MAX(id) FROM software_packages")
            max_id = cursor.fetchone()[0]
            conn.close()
            
            return (max_id or 0) + 1
            
        except Exception as e:
            logger.error(f"Error getting next package ID: {str(e)}")
            return 1
    
    async def _update_software_inventory(
        self,
        agent_id: str,
        software_list: List[Dict[str, Any]]
    ) -> None:
        """Update software inventory in database."""
        try:
            conn = psycopg2.connect(settings.DATABASE_URL)
            cursor = conn.cursor()
            
            # Clear existing inventory
            cursor.execute("DELETE FROM installed_software WHERE agent_id = %s", (agent_id,))
            
            # Insert new inventory
            for software in software_list:
                cursor.execute("""
                    INSERT INTO installed_software 
                    (agent_id, name, version, vendor, install_location, 
                     uninstall_string, registry_key, size_bytes, detected_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    agent_id,
                    software.get('Name'),
                    software.get('Version'),
                    software.get('Vendor'),
                    software.get('InstallLocation'),
                    software.get('UninstallString'),
                    software.get('RegistryKey'),
                    software.get('EstimatedSize'),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating software inventory: {str(e)}")
    
    async def _get_installed_software_by_id(self, software_id: int) -> Optional[Dict[str, Any]]:
        """Get installed software by ID."""
        try:
            conn = psycopg2.connect(settings.DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM installed_software WHERE id = %s
            """, (software_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting installed software: {str(e)}")
            return None
    
    async def _get_installed_software_by_name(
        self,
        agent_id: str,
        software_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get installed software by name."""
        try:
            conn = psycopg2.connect(settings.DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM installed_software 
                WHERE agent_id = %s AND name LIKE %s
            """, (agent_id, f"%{software_name}%"))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting installed software by name: {str(e)}")
            return None