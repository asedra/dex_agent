from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from ...schemas.agent import AgentInstallerConfig
from ...services.agent_installer_service import AgentInstallerService
from ...core.auth import verify_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create")
async def create_agent_installer(
    config: AgentInstallerConfig,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Create a custom agent installer"""
    try:
        zip_path = AgentInstallerService.create_agent_installer(config)
        
        # Add cleanup task
        background_tasks.add_task(AgentInstallerService.cleanup_temp_files, zip_path)
        
        return FileResponse(
            path=zip_path,
            filename=f"DexAgents_Installer_{config.agent_name or 'Custom'}.zip",
            media_type="application/zip"
        )
    except Exception as e:
        logger.error(f"Error creating agent installer: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create agent installer")

@router.get("/config")
async def get_installer_config(token: str = Depends(verify_token)):
    """Get default installer configuration"""
    try:
        return {
            "server_url": "http://localhost:8000",
            "api_token": "your-api-token-here",
            "agent_name": None,
            "tags": [],
            "auto_start": True,
            "run_as_service": True
        }
    except Exception as e:
        logger.error(f"Error getting installer config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get installer configuration") 