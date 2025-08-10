"""Simplified process tree endpoint for debugging."""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import json
import logging

from backend_from_container.core.database import db_manager
from backend_from_container.core.auth import verify_token
from backend_from_container.core.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/agents/{agent_id}/processes/tree")
async def get_process_tree(
    agent_id: str,
    token: str = Depends(verify_token)
):
    """Get process tree from agent."""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected
        if not websocket_manager.is_agent_connected(agent_id):
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Simple PowerShell command first - just get basic process info
        ps_command = '''
        try {
            $processes = Get-Process | Select-Object Id, Name, WorkingSet | Sort-Object Id | Select-Object -First 10
            @{
                'status' = 'success'
                'count' = $processes.Count
                'processes' = $processes
            } | ConvertTo-Json -Depth 2 -Compress
        } catch {
            @{
                'status' = 'error'
                'message' = $_.Exception.Message
            } | ConvertTo-Json
        }
        '''
        
        response = await websocket_manager.execute_command_on_agent(agent_id, ps_command)
        
        if response and response.get("success"):
            output = response.get("output", "{}")
            logger.info(f"Raw PowerShell output: {output[:500]}...")
            
            try:
                tree_data = json.loads(output) if output else {}
                
                return {
                    "process_tree": tree_data,
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "raw_output_length": len(output)
                }
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}, output: {output[:1000]}")
                return {
                    "error": "JSON decode failed",
                    "raw_output": output[:1000],
                    "parse_error": str(e),
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat()
                }
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response from agent"
            logger.error(f"PowerShell execution failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"PowerShell execution failed: {error_msg}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting process tree from agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")