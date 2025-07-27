import asyncio
import logging
from typing import Optional
from datetime import datetime
from ..schemas.command import PowerShellCommand, CommandResponse
from ..core.config import settings

logger = logging.getLogger(__name__)

class PowerShellService:
    @staticmethod
    async def execute_command(
        command: str,
        timeout: int = 30,
        working_directory: Optional[str] = None,
        run_as_admin: bool = False
    ) -> CommandResponse:
        """
        Execute a PowerShell command asynchronously
        """
        start_time = datetime.now()
        
        try:
            # Prepare PowerShell command
            if run_as_admin:
                # Run as administrator using Start-Process
                ps_command = f'Start-Process powershell -ArgumentList "-Command", "{command}" -Verb RunAs -Wait'
            else:
                ps_command = command
            
            # Create process
            process = await asyncio.create_subprocess_exec(
                'powershell.exe',
                '-Command',
                ps_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_directory
            )
            
            # Execute with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Decode output
                output = stdout.decode('utf-8', errors='ignore').strip()
                error = stderr.decode('utf-8', errors='ignore').strip()
                
                success = process.returncode == 0
                
                logger.info(f"Command executed successfully: {command[:50]}...")
                
                return CommandResponse(
                    success=success,
                    output=output,
                    error=error if not success else None,
                    execution_time=execution_time,
                    timestamp=start_time,
                    command=command
                )
                
            except asyncio.TimeoutError:
                # Kill process if timeout
                process.kill()
                await process.wait()
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                logger.warning(f"Command timed out after {timeout}s: {command[:50]}...")
                
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
            
            logger.error(f"Error executing command: {str(e)}")
            
            return CommandResponse(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time,
                timestamp=start_time,
                command=command
            )
    
    @staticmethod
    async def execute_batch_commands(
        commands: list[PowerShellCommand]
    ) -> list[CommandResponse]:
        """
        Execute multiple PowerShell commands
        """
        results = []
        
        for cmd in commands:
            result = await PowerShellService.execute_command(
                command=cmd.command,
                timeout=cmd.timeout or settings.DEFAULT_TIMEOUT,
                working_directory=cmd.working_directory,
                run_as_admin=cmd.run_as_admin or False
            )
            results.append(result)
        
        return results 