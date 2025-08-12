"""File manager API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Response
from fastapi.responses import StreamingResponse
import io

from app.core.database import db_manager
from app.core.auth import verify_token
from app.schemas.files import (
    FileItem,
    DirectoryContent,
    FileOperation,
    FileOperationResult,
    FileUploadRequest,
    FileUploadResponse,
    FileDownloadRequest,
    FilePreviewRequest,
    FilePreviewResponse,
    FileSearchRequest,
    FileSearchResult,
    FilePermissions,
    FileTree
)
from app.services.file_manager_service import FileManagerService
from app.core.websocket_manager import websocket_manager

router = APIRouter()

# Initialize services
file_service = FileManagerService(websocket_manager)


@router.get("/agents/{agent_id}/files", response_model=DirectoryContent)
async def list_directory(
    agent_id: str,
    path: str = Query("C:\\", description="Directory path to list"),
    token: str = Depends(verify_token)
):
    """List contents of a directory on the agent."""
    # Check if agent exists and is online
    agent = db_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if agent.get("status") != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} is not online"
        )
    
    return await file_service.list_directory(agent_id, path)


@router.post("/agents/{agent_id}/files/operation", response_model=FileOperationResult)
async def perform_file_operation(
    agent_id: str,
    operation: FileOperation,
    token: str = Depends(verify_token)
):
    """Perform file operation (copy, move, delete, rename, create) on agent."""
    # Check if agent exists and is online
    agent = db_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if agent.get("status") != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} is not online"
        )
    
    return await file_service.perform_file_operation(agent_id, operation)


@router.post("/agents/{agent_id}/files/upload", response_model=FileUploadResponse)
async def upload_file(
    agent_id: str,
    file: UploadFile = File(...),
    target_path: str = Query(..., description="Target directory path on agent"),
    overwrite: bool = Query(False, description="Overwrite existing file"),
    token: str = Depends(verify_token)
):
    """Upload file to agent."""
    # Check if agent exists and is online
    agent = db_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if agent.get("status") != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} is not online"
        )
    
    return await file_service.upload_file(agent_id, file, target_path, overwrite)


@router.get("/agents/{agent_id}/files/download")
async def download_file(
    agent_id: str,
    file_path: str = Query(..., description="File path on agent"),
    compress: bool = Query(False, description="Compress file before download"),
    token: str = Depends(verify_token)
):
    """Download file from agent."""
    # Check if agent exists and is online
    agent = db_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if agent.get("status") != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} is not online"
        )
    
    # Get file stream from service
    try:
        file_stream = file_service.download_file(agent_id, file_path, compress)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}"
        )
    
    # Determine filename and content type
    from pathlib import Path
    filename = Path(file_path).name
    if compress:
        filename = f"{filename}.zip"
        content_type = "application/zip"
    else:
        import mimetypes
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    
    return StreamingResponse(
        file_stream,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/agents/{agent_id}/files/preview", response_model=FilePreviewResponse)
async def preview_file(
    agent_id: str,
    file_path: str = Query(..., description="File path on agent"),
    token: str = Depends(verify_token)
):
    """Preview file content from agent."""
    # Check if agent exists and is online
    agent = db_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if agent.get("status") != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} is not online"
        )
    
    return await file_service.preview_file(agent_id, file_path)


@router.post("/agents/{agent_id}/files/search", response_model=FileSearchResult)
async def search_files(
    agent_id: str,
    search_request: FileSearchRequest,
    token: str = Depends(verify_token)
):
    """Search for files on agent."""
    # Check if agent exists and is online
    agent = db_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if agent.get("status") != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} is not online"
        )
    
    return await file_service.search_files(agent_id, search_request)


@router.get("/agents/{agent_id}/files/tree", response_model=FileTree)
async def get_file_tree(
    agent_id: str,
    root_path: str = Query("C:\\", description="Root path for tree"),
    max_depth: int = Query(3, description="Maximum tree depth", ge=1, le=10),
    token: str = Depends(verify_token)
):
    """Get file tree structure from agent."""
    # Check if agent exists and is online
    agent = db_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if agent.get("status") != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} is not online"
        )
    
    return await file_service.get_file_tree(agent_id, root_path, max_depth)


@router.post("/agents/{agent_id}/files/folder", response_model=FileOperationResult)
async def create_folder(
    agent_id: str,
    path: str = Query(..., description="Folder path to create"),
    token: str = Depends(verify_token)
):
    """Create a new folder on agent."""
    # Check if agent exists and is online
    agent = db_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if agent.get("status") != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} is not online"
        )
    
    return await file_service.create_folder(agent_id, path)


@router.delete("/agents/{agent_id}/files", response_model=FileOperationResult)
async def delete_files(
    agent_id: str,
    paths: List[str] = Query(..., description="List of file/folder paths to delete"),
    token: str = Depends(verify_token)
):
    """Delete multiple files/folders on agent."""
    # Check if agent exists and is online
    agent = db_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if agent.get("status") != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} is not online"
        )
    
    return await file_service.delete_items(agent_id, paths)


@router.post("/agents/{agent_id}/files/compress", response_model=FileOperationResult)
async def compress_files(
    agent_id: str,
    paths: List[str] = Query(..., description="List of file/folder paths to compress"),
    output_path: str = Query(..., description="Output archive path"),
    token: str = Depends(verify_token)
):
    """Compress files/folders into archive."""
    # Check if agent exists and is online
    agent = db_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if agent.get("status") != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} is not online"
        )
    
    return await file_service.compress_files(agent_id, paths, output_path)


@router.post("/agents/{agent_id}/files/extract", response_model=FileOperationResult)
async def extract_archive(
    agent_id: str,
    archive_path: str = Query(..., description="Archive file path"),
    output_path: str = Query(..., description="Output directory path"),
    token: str = Depends(verify_token)
):
    """Extract archive contents."""
    # Check if agent exists and is online
    agent = db_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if agent.get("status") != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} is not online"
        )
    
    return await file_service.extract_archive(agent_id, archive_path, output_path)


@router.post("/agents/{agent_id}/files/batch-upload")
async def batch_upload_files(
    agent_id: str,
    files: List[UploadFile] = File(...),
    target_path: str = Query(..., description="Target directory path on agent"),
    overwrite: bool = Query(False, description="Overwrite existing files"),
    token: str = Depends(verify_token)
):
    """Upload multiple files to agent."""
    # Check if agent exists and is online
    agent = db_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    if agent.get("status") != "online":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} is not online"
        )
    
    results = []
    for file in files:
        try:
            result = await file_service.upload_file(agent_id, file, target_path, overwrite)
            results.append({
                "filename": file.filename,
                "success": result.success,
                "message": result.message,
                "file_path": result.file_path
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "message": str(e),
                "file_path": None
            })
    
    return {"results": results, "total": len(files), "successful": sum(1 for r in results if r["success"])}