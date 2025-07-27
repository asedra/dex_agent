import os
import tempfile
import shutil
import json
import zipfile
import logging
from ..schemas.agent import AgentInstallerConfig
from ..core.config import settings

logger = logging.getLogger(__name__)

class AgentInstallerService:
    @staticmethod
    def create_agent_installer(config: AgentInstallerConfig) -> str:
        """
        Create a custom agent installer with the provided configuration
        """
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Create config file
            config_data = {
                "server_url": config.server_url,
                "api_token": config.api_token,
                "agent_name": config.agent_name,
                "tags": config.tags,
                "auto_start": config.auto_start,
                "run_as_service": config.run_as_service
            }
            
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Copy agent executable (assuming it exists in agent directory)
            agent_source = os.path.join("..", "agent", "DexAgentsAgent.exe")
            if os.path.exists(agent_source):
                agent_dest = os.path.join(temp_dir, "DexAgentsAgent.exe")
                shutil.copy2(agent_source, agent_dest)
            else:
                logger.warning("Agent executable not found, creating placeholder")
                # Create a placeholder file
                with open(os.path.join(temp_dir, "DexAgentsAgent.exe"), 'w') as f:
                    f.write("# Placeholder for agent executable")
            
            # Create README
            readme_content = f"""
DexAgents Agent Installer

This installer contains a pre-configured DexAgents agent.

Configuration:
- Server URL: {config.server_url}
- Agent Name: {config.agent_name or 'Auto-generated'}
- Tags: {', '.join(config.tags) if config.tags else 'None'}
- Auto Start: {'Yes' if config.auto_start else 'No'}
- Run as Service: {'Yes' if config.run_as_service else 'No'}

Installation:
1. Extract all files to a directory
2. Run DexAgentsAgent.exe as administrator
3. The agent will automatically connect to the server

For support, contact your system administrator.
"""
            
            with open(os.path.join(temp_dir, "README.txt"), 'w') as f:
                f.write(readme_content)
            
            # Create ZIP file
            zip_filename = f"DexAgents_Installer_{config.agent_name or 'Custom'}.zip"
            zip_path = os.path.join(settings.TEMP_DIR, zip_filename)
            
            # Ensure temp directory exists
            os.makedirs(settings.TEMP_DIR, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            
            logger.info(f"Agent installer created: {zip_path}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Error creating agent installer: {str(e)}")
            raise
    
    @staticmethod
    def cleanup_temp_files(zip_path: str):
        """
        Clean up temporary installer files
        """
        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
                logger.info(f"Cleaned up temporary file: {zip_path}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary file: {str(e)}") 