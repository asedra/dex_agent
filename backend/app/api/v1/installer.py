from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from ...schemas.agent import AgentInstallerConfig
from ...services.agent_installer_service import AgentInstallerService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create")
async def create_agent_installer(
    config: AgentInstallerConfig,
    background_tasks: BackgroundTasks
):
    """Create a pre-built Windows .exe agent"""
    try:
        exe_path = AgentInstallerService.create_prebuilt_exe(config)
        
        # Add cleanup task
        background_tasks.add_task(AgentInstallerService.cleanup_temp_files, exe_path)
        
        return FileResponse(
            path=exe_path,
            filename=f"DexAgent_{config.agent_name or 'Windows'}.exe",
            media_type="application/zip"
        )
    except Exception as e:
        logger.error(f"Error creating pre-built .exe: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create .exe agent")

@router.get("/config")
async def get_installer_config():
    """Get default installer configuration"""
    try:
        return {
            "server_url": "http://localhost:8080",
            "api_token": "your-api-token-here",
            "agent_name": None,
            "tags": [],
            "auto_start": True,
            "run_as_service": True
        }
    except Exception as e:
        logger.error(f"Error getting installer config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get installer configuration") 