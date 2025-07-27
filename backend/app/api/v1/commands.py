from typing import List
from fastapi import APIRouter, HTTPException, Depends
from ...schemas.command import PowerShellCommand, CommandResponse
from ...services.powershell_service import PowerShellService
from ...core.auth import verify_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/execute", response_model=CommandResponse)
async def execute_powershell_command(
    command: PowerShellCommand,
    token: str = Depends(verify_token)
):
    """Execute a PowerShell command"""
    try:
        result = await PowerShellService.execute_command(
            command=command.command,
            timeout=command.timeout or 30,
            working_directory=command.working_directory,
            run_as_admin=command.run_as_admin or False
        )
        return result
    except Exception as e:
        logger.error(f"Error executing PowerShell command: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute command")

@router.post("/execute/batch", response_model=List[CommandResponse])
async def execute_batch_commands(
    commands: List[PowerShellCommand],
    token: str = Depends(verify_token)
):
    """Execute multiple PowerShell commands"""
    try:
        results = await PowerShellService.execute_batch_commands(commands)
        return results
    except Exception as e:
        logger.error(f"Error executing batch commands: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute batch commands") 