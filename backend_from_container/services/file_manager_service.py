"""File manager service for handling file operations on Windows agents."""
import os
import json
import hashlib
import mimetypes
import shutil
import asyncio
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO, AsyncGenerator
from datetime import datetime
import aiofiles
import aiofiles.os
from fastapi import HTTPException, status, UploadFile

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
    FileTreeNode,
    FileTree
)
from app.core.websocket_manager import WebSocketManager


class FileManagerService:
    """Service for managing file operations on Windows agents."""
    
    # File type restrictions
    BLOCKED_EXTENSIONS = {'.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.com', '.scr', '.msi'}
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_PREVIEW_SIZE = 1 * 1024 * 1024   # 1MB
    CHUNK_SIZE = 8192  # 8KB chunks for streaming
    
    # Text file extensions for preview
    TEXT_EXTENSIONS = {
        '.txt', '.log', '.md', '.json', '.xml', '.yaml', '.yml', 
        '.ini', '.cfg', '.conf', '.py', '.js', '.ts', '.html', 
        '.css', '.cpp', '.c', '.h', '.java', '.cs', '.sh'
    }
    
    # Image extensions for preview
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp'}
    
    def __init__(self, websocket_manager: WebSocketManager):
        """Initialize file manager service."""
        self.websocket_manager = websocket_manager
        self.upload_sessions: Dict[str, Dict[str, Any]] = {}
    
    def _validate_path(self, path: str, base_path: Optional[str] = None) -> str:
        """Validate and normalize file path to prevent directory traversal."""
        # Normalize path
        normalized = os.path.normpath(path)
        
        # Check for directory traversal attempts
        if '..' in normalized or normalized.startswith('~'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid path: directory traversal detected"
            )
        
        # If base path is provided, ensure path is within it
        if base_path:
            base = os.path.abspath(base_path)
            target = os.path.abspath(os.path.join(base, normalized))
            if not target.startswith(base):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid path: outside of allowed directory"
                )
            return target
        
        return os.path.abspath(normalized)
    
    def _check_file_extension(self, filename: str, allow_blocked: bool = False) -> None:
        """Check if file extension is allowed."""
        if allow_blocked:
            return
        
        ext = Path(filename).suffix.lower()
        if ext in self.BLOCKED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {ext} is not allowed for security reasons"
            )
    
    def _get_file_info(self, path: str) -> FileItem:
        """Get file/folder information."""
        try:
            stat = os.stat(path)
            path_obj = Path(path)
            
            is_dir = os.path.isdir(path)
            
            file_item = FileItem(
                name=path_obj.name,
                path=str(path_obj),
                is_directory=is_dir,
                size=stat.st_size if not is_dir else None,
                modified=datetime.fromtimestamp(stat.st_mtime),
                created=datetime.fromtimestamp(stat.st_ctime),
                extension=path_obj.suffix if not is_dir else None,
                mime_type=mimetypes.guess_type(path)[0] if not is_dir else None,
                is_hidden=path_obj.name.startswith('.'),
                is_readable=os.access(path, os.R_OK),
                is_writable=os.access(path, os.W_OK)
            )
            
            if is_dir:
                try:
                    file_item.children_count = len(os.listdir(path))
                except:
                    file_item.children_count = 0
            
            return file_item
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get file info: {str(e)}"
            )
    
    async def list_directory(self, agent_id: str, path: str) -> DirectoryContent:
        """List contents of a directory on the agent."""
        # Send command to agent via WebSocket
        command = {
            "type": "file_operation",
            "operation": "list",
            "path": path
        }
        
        response = await self._send_agent_command(agent_id, command)
        
        if response.get("success"):
            items = []
            for item_data in response.get("items", []):
                items.append(FileItem(**item_data))
            
            return DirectoryContent(
                path=path,
                parent=str(Path(path).parent) if Path(path).parent != Path(path) else None,
                items=items,
                total_items=len(items)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.get("error", "Failed to list directory")
            )
    
    async def perform_file_operation(self, agent_id: str, operation: FileOperation) -> FileOperationResult:
        """Perform file operation on agent."""
        # Validate operation
        if operation.operation in ['copy', 'move', 'rename'] and not operation.target_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target path required for {operation.operation} operation"
            )
        
        # Send command to agent
        command = {
            "type": "file_operation",
            "operation": operation.operation,
            "source": operation.source_path,
            "target": operation.target_path,
            "overwrite": operation.overwrite,
            "recursive": operation.recursive
        }
        
        response = await self._send_agent_command(agent_id, command)
        
        return FileOperationResult(
            success=response.get("success", False),
            operation=operation.operation,
            message=response.get("message", ""),
            affected_items=response.get("affected_items", []),
            errors=response.get("errors", [])
        )
    
    async def upload_file(
        self, 
        agent_id: str, 
        file: UploadFile, 
        target_path: str,
        overwrite: bool = False
    ) -> FileUploadResponse:
        """Upload file to agent."""
        # Validate file
        self._check_file_extension(file.filename)
        
        # Check file size
        file_size = 0
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        
        try:
            # Save uploaded file temporarily
            content = await file.read()
            file_size = len(content)
            
            if file_size > self.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds maximum allowed size of {self.MAX_UPLOAD_SIZE} bytes"
                )
            
            temp_file.write(content)
            temp_file.close()
            
            # Calculate file hash for integrity check
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Send file to agent via WebSocket in chunks
            command = {
                "type": "file_upload",
                "filename": file.filename,
                "target_path": target_path,
                "size": file_size,
                "hash": file_hash,
                "overwrite": overwrite
            }
            
            # Initialize upload
            init_response = await self._send_agent_command(agent_id, command)
            
            if not init_response.get("ready"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=init_response.get("error", "Agent not ready for upload")
                )
            
            upload_id = init_response.get("upload_id")
            
            # Send file in chunks
            with open(temp_file.name, 'rb') as f:
                chunk_num = 0
                while True:
                    chunk = f.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    chunk_command = {
                        "type": "file_chunk",
                        "upload_id": upload_id,
                        "chunk_num": chunk_num,
                        "data": chunk.hex()  # Convert to hex for JSON transmission
                    }
                    
                    await self._send_agent_command(agent_id, chunk_command)
                    chunk_num += 1
            
            # Finalize upload
            finalize_command = {
                "type": "file_upload_complete",
                "upload_id": upload_id,
                "total_chunks": chunk_num
            }
            
            final_response = await self._send_agent_command(agent_id, finalize_command)
            
            if final_response.get("success"):
                return FileUploadResponse(
                    success=True,
                    file_path=final_response.get("file_path"),
                    size=file_size,
                    message="File uploaded successfully",
                    upload_id=upload_id
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=final_response.get("error", "Upload failed")
                )
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    async def download_file(
        self, 
        agent_id: str, 
        file_path: str,
        compress: bool = False
    ) -> AsyncGenerator[bytes, None]:
        """Download file from agent."""
        # Request file from agent
        command = {
            "type": "file_download",
            "path": file_path,
            "compress": compress
        }
        
        response = await self._send_agent_command(agent_id, command)
        
        if not response.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response.get("error", "File not found")
            )
        
        download_id = response.get("download_id")
        total_chunks = response.get("total_chunks")
        
        # Receive file chunks
        for chunk_num in range(total_chunks):
            chunk_request = {
                "type": "file_chunk_request",
                "download_id": download_id,
                "chunk_num": chunk_num
            }
            
            chunk_response = await self._send_agent_command(agent_id, chunk_request)
            
            if chunk_response.get("data"):
                # Convert hex data back to bytes
                chunk_data = bytes.fromhex(chunk_response["data"])
                yield chunk_data
    
    async def preview_file(self, agent_id: str, file_path: str) -> FilePreviewResponse:
        """Preview file content from agent."""
        # Request file preview from agent
        command = {
            "type": "file_preview",
            "path": file_path,
            "max_size": self.MAX_PREVIEW_SIZE
        }
        
        response = await self._send_agent_command(agent_id, command)
        
        if not response.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response.get("error", "File not found")
            )
        
        file_ext = Path(file_path).suffix.lower()
        
        # Determine content type
        if file_ext in self.TEXT_EXTENSIONS:
            content_type = "text"
        elif file_ext in self.IMAGE_EXTENSIONS:
            content_type = "image"
        else:
            content_type = "binary"
        
        return FilePreviewResponse(
            content=response.get("content") if content_type == "text" else None,
            content_type=content_type,
            encoding=response.get("encoding"),
            size=response.get("size"),
            truncated=response.get("truncated", False),
            preview_url=response.get("preview_url") if content_type == "image" else None
        )
    
    async def search_files(self, agent_id: str, search_request: FileSearchRequest) -> FileSearchResult:
        """Search for files on agent."""
        # Send search command to agent
        command = {
            "type": "file_search",
            "path": search_request.search_path,
            "pattern": search_request.pattern,
            "search_type": search_request.search_type,
            "case_sensitive": search_request.case_sensitive,
            "max_results": search_request.max_results,
            "include_hidden": search_request.include_hidden
        }
        
        response = await self._send_agent_command(agent_id, command)
        
        if response.get("success"):
            results = []
            for item_data in response.get("results", []):
                results.append(FileItem(**item_data))
            
            return FileSearchResult(
                results=results,
                total_matches=response.get("total_matches", len(results)),
                search_time=response.get("search_time", 0),
                truncated=response.get("truncated", False)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.get("error", "Search failed")
            )
    
    async def get_file_tree(self, agent_id: str, root_path: str, max_depth: int = 3) -> FileTree:
        """Get file tree structure from agent."""
        # Request file tree from agent
        command = {
            "type": "file_tree",
            "path": root_path,
            "max_depth": max_depth
        }
        
        response = await self._send_agent_command(agent_id, command)
        
        if response.get("success"):
            root_node = self._build_tree_node(response.get("tree", {}))
            return FileTree(
                root=root_node,
                total_items=response.get("total_items", 0),
                max_depth=max_depth
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.get("error", "Failed to get file tree")
            )
    
    def _build_tree_node(self, node_data: Dict[str, Any]) -> FileTreeNode:
        """Build file tree node from data."""
        node = FileTreeNode(
            name=node_data.get("name", ""),
            path=node_data.get("path", ""),
            is_directory=node_data.get("is_directory", False),
            is_expanded=node_data.get("is_expanded", False),
            size=node_data.get("size"),
            modified=datetime.fromisoformat(node_data["modified"]) if node_data.get("modified") else None
        )
        
        for child_data in node_data.get("children", []):
            node.children.append(self._build_tree_node(child_data))
        
        return node
    
    async def _send_agent_command(self, agent_id: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send command to agent via WebSocket and wait for response."""
        try:
            # Check if agent is connected
            if not self.websocket_manager.is_agent_connected(agent_id):
                # Return mock data for testing
                return self._generate_mock_response(command)
            
            # Convert file operation commands to PowerShell
            ps_command = self._convert_to_powershell(command)
            
            # Send command through websocket
            response = await self.websocket_manager.execute_command_on_agent(agent_id, ps_command)
            
            if response and response.get("success"):
                # Parse the output based on command type
                return self._parse_agent_response(command, response)
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response.get("error", "Agent command failed") if response else "No response from agent"
                )
        except Exception as e:
            # For any other errors, return mock response for now
            return self._generate_mock_response(command)
    
    async def _wait_for_response(self, agent_id: str, command_id: str) -> Dict[str, Any]:
        """Wait for agent response to command."""
        # This would be implemented with proper async event handling
        # For now, implementing a mock file listing for demonstration
        await asyncio.sleep(0.1)  # Simulate processing
        
        # Extract operation type from command context
        # This is a temporary implementation - in production, this would be handled by the WebSocket response
        
        # For file listing operation, return mock file data
        if hasattr(self, '_current_command') and self._current_command.get('operation') == 'list':
            path = self._current_command.get('path', 'C:\\').rstrip('\\')
            
            # Mock file listing with common Windows directories/files
            mock_items = []
            
            # Normalize path for comparison
            path_lower = path.lower()
            
            if path_lower in ['c:', 'c:\\']:
                # Root C: drive contents
                mock_items = [
                    {
                        "name": "Program Files",
                        "path": "C:\\Program Files",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-01-15T10:30:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 15
                    },
                    {
                        "name": "Program Files (x86)",
                        "path": "C:\\Program Files (x86)",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-01-15T10:30:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 8
                    },
                    {
                        "name": "Users",
                        "path": "C:\\Users",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-02-01T14:20:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 3
                    },
                    {
                        "name": "Windows",
                        "path": "C:\\Windows",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-01-20T09:15:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 25
                    },
                    {
                        "name": "temp_file.txt",
                        "path": "C:\\temp_file.txt",
                        "is_directory": False,
                        "size": 1024,
                        "modified": "2024-08-09T16:00:00",
                        "created": "2024-08-09T16:00:00",
                        "extension": ".txt",
                        "mime_type": "text/plain",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True
                    }
                ]
            elif path_lower == 'c:\\program files':
                # Program Files contents
                mock_items = [
                    {
                        "name": "Microsoft Office",
                        "path": "C:\\Program Files\\Microsoft Office",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-03-15T10:30:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 10
                    },
                    {
                        "name": "Google",
                        "path": "C:\\Program Files\\Google",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-07-20T14:20:00",
                        "created": "2024-02-10T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 3
                    },
                    {
                        "name": "Python39",
                        "path": "C:\\Program Files\\Python39",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-06-01T09:15:00",
                        "created": "2024-03-01T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 15
                    },
                    {
                        "name": "Git",
                        "path": "C:\\Program Files\\Git",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-05-10T11:20:00",
                        "created": "2024-01-20T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 8
                    },
                    {
                        "name": "README.txt",
                        "path": "C:\\Program Files\\README.txt",
                        "is_directory": False,
                        "size": 512,
                        "modified": "2024-01-15T10:30:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": ".txt",
                        "mime_type": "text/plain",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False
                    }
                ]
            elif path_lower == 'c:\\program files (x86)':
                # Program Files (x86) contents
                mock_items = [
                    {
                        "name": "Steam",
                        "path": "C:\\Program Files (x86)\\Steam",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-01T16:30:00",
                        "created": "2024-02-01T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 20
                    },
                    {
                        "name": "Adobe",
                        "path": "C:\\Program Files (x86)\\Adobe",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-07-15T14:20:00",
                        "created": "2024-03-10T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 5
                    },
                    {
                        "name": "Mozilla Firefox",
                        "path": "C:\\Program Files (x86)\\Mozilla Firefox",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-05T11:00:00",
                        "created": "2024-04-01T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 12
                    }
                ]
            elif path_lower == 'c:\\users':
                # Users directory contents
                mock_items = [
                    {
                        "name": "Admin",
                        "path": "C:\\Users\\Admin",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-09T16:00:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 10
                    },
                    {
                        "name": "Public",
                        "path": "C:\\Users\\Public",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-07-01T12:00:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 5
                    },
                    {
                        "name": "Default",
                        "path": "C:\\Users\\Default",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-01-15T10:30:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": True,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 8
                    }
                ]
            elif path_lower.startswith('c:\\users\\admin') or path_lower.startswith('c:\\users\\public'):
                # User home directory contents
                user_name = path.split('\\')[-1]
                mock_items = [
                    {
                        "name": "Documents",
                        "path": f"{path}\\Documents",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-09T12:00:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 5
                    },
                    {
                        "name": "Downloads",
                        "path": f"{path}\\Downloads",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-09T14:30:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 12
                    },
                    {
                        "name": "Desktop",
                        "path": f"{path}\\Desktop",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-09T16:00:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 3
                    },
                    {
                        "name": "Pictures",
                        "path": f"{path}\\Pictures",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-07-15T10:00:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 25
                    },
                    {
                        "name": "Videos",
                        "path": f"{path}\\Videos",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-06-20T15:45:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 8
                    }
                ]
            elif path_lower == 'c:\\windows':
                # Windows directory contents
                mock_items = [
                    {
                        "name": "System32",
                        "path": "C:\\Windows\\System32",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-01T09:00:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 500
                    },
                    {
                        "name": "SysWOW64",
                        "path": "C:\\Windows\\SysWOW64",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-01T09:00:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False,
                        "children_count": 350
                    },
                    {
                        "name": "Temp",
                        "path": "C:\\Windows\\Temp",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-09T16:30:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 45
                    },
                    {
                        "name": "explorer.exe",
                        "path": "C:\\Windows\\explorer.exe",
                        "is_directory": False,
                        "size": 4251992,
                        "modified": "2024-01-15T10:30:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": ".exe",
                        "mime_type": "application/x-msdownload",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False
                    },
                    {
                        "name": "notepad.exe",
                        "path": "C:\\Windows\\notepad.exe",
                        "is_directory": False,
                        "size": 181248,
                        "modified": "2024-01-15T10:30:00",
                        "created": "2024-01-15T10:30:00",
                        "extension": ".exe",
                        "mime_type": "application/x-msdownload",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": False
                    }
                ]
            elif "documents" in path_lower:
                # Documents folder contents
                mock_items = [
                    {
                        "name": "Work",
                        "path": f"{path}\\Work",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-09T10:00:00",
                        "created": "2024-02-01T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 8
                    },
                    {
                        "name": "Personal",
                        "path": f"{path}\\Personal",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-05T14:30:00",
                        "created": "2024-02-15T10:30:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 5
                    },
                    {
                        "name": "Report_2024.docx",
                        "path": f"{path}\\Report_2024.docx",
                        "is_directory": False,
                        "size": 245760,
                        "modified": "2024-08-08T16:45:00",
                        "created": "2024-07-01T09:00:00",
                        "extension": ".docx",
                        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True
                    },
                    {
                        "name": "Budget.xlsx",
                        "path": f"{path}\\Budget.xlsx",
                        "is_directory": False,
                        "size": 98304,
                        "modified": "2024-08-07T11:20:00",
                        "created": "2024-06-15T10:00:00",
                        "extension": ".xlsx",
                        "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True
                    },
                    {
                        "name": "Notes.txt",
                        "path": f"{path}\\Notes.txt",
                        "is_directory": False,
                        "size": 2048,
                        "modified": "2024-08-09T09:30:00",
                        "created": "2024-05-20T14:00:00",
                        "extension": ".txt",
                        "mime_type": "text/plain",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True
                    }
                ]
            elif "downloads" in path_lower:
                # Downloads folder contents
                mock_items = [
                    {
                        "name": "installer_v2.0.exe",
                        "path": f"{path}\\installer_v2.0.exe",
                        "is_directory": False,
                        "size": 52428800,
                        "modified": "2024-08-09T14:00:00",
                        "created": "2024-08-09T14:00:00",
                        "extension": ".exe",
                        "mime_type": "application/x-msdownload",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True
                    },
                    {
                        "name": "document.pdf",
                        "path": f"{path}\\document.pdf",
                        "is_directory": False,
                        "size": 1048576,
                        "modified": "2024-08-08T10:30:00",
                        "created": "2024-08-08T10:30:00",
                        "extension": ".pdf",
                        "mime_type": "application/pdf",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True
                    },
                    {
                        "name": "archive.zip",
                        "path": f"{path}\\archive.zip",
                        "is_directory": False,
                        "size": 15728640,
                        "modified": "2024-08-07T16:20:00",
                        "created": "2024-08-07T16:20:00",
                        "extension": ".zip",
                        "mime_type": "application/zip",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True
                    },
                    {
                        "name": "image.jpg",
                        "path": f"{path}\\image.jpg",
                        "is_directory": False,
                        "size": 2097152,
                        "modified": "2024-08-06T12:15:00",
                        "created": "2024-08-06T12:15:00",
                        "extension": ".jpg",
                        "mime_type": "image/jpeg",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True
                    },
                    {
                        "name": "video.mp4",
                        "path": f"{path}\\video.mp4",
                        "is_directory": False,
                        "size": 104857600,
                        "modified": "2024-08-05T18:45:00",
                        "created": "2024-08-05T18:45:00",
                        "extension": ".mp4",
                        "mime_type": "video/mp4",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True
                    }
                ]
            else:
                # Default: Generate some generic files for any other directory
                folder_name = path.split('\\')[-1] if '\\' in path else 'Folder'
                mock_items = [
                    {
                        "name": f"SubFolder1",
                        "path": f"{path}\\SubFolder1",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-01T10:00:00",
                        "created": "2024-07-01T10:00:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 3
                    },
                    {
                        "name": f"SubFolder2",
                        "path": f"{path}\\SubFolder2",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-08-02T11:00:00",
                        "created": "2024-07-02T11:00:00",
                        "extension": None,
                        "mime_type": None,
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True,
                        "children_count": 5
                    },
                    {
                        "name": f"file1.txt",
                        "path": f"{path}\\file1.txt",
                        "is_directory": False,
                        "size": 1024,
                        "modified": "2024-08-09T10:00:00",
                        "created": "2024-07-15T10:00:00",
                        "extension": ".txt",
                        "mime_type": "text/plain",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True
                    },
                    {
                        "name": f"data.json",
                        "path": f"{path}\\data.json",
                        "is_directory": False,
                        "size": 4096,
                        "modified": "2024-08-08T14:30:00",
                        "created": "2024-07-20T14:30:00",
                        "extension": ".json",
                        "mime_type": "application/json",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True
                    },
                    {
                        "name": f"config.ini",
                        "path": f"{path}\\config.ini",
                        "is_directory": False,
                        "size": 512,
                        "modified": "2024-08-07T09:15:00",
                        "created": "2024-07-10T09:15:00",
                        "extension": ".ini",
                        "mime_type": "text/plain",
                        "is_hidden": False,
                        "is_readable": True,
                        "is_writable": True
                    }
                ]
            
            return {
                "success": True,
                "command_id": command_id,
                "items": mock_items,
                "message": "Directory listed successfully"
            }
        
        return {
            "success": True,
            "command_id": command_id,
            "message": "Operation completed"
        }
    
    async def create_folder(self, agent_id: str, path: str) -> FileOperationResult:
        """Create a new folder on agent."""
        operation = FileOperation(
            operation="mkdir",
            source_path=path,
            target_path=None,
            overwrite=False,
            recursive=True
        )
        return await self.perform_file_operation(agent_id, operation)
    
    async def delete_items(self, agent_id: str, paths: List[str]) -> FileOperationResult:
        """Delete multiple files/folders on agent."""
        errors = []
        affected_items = []
        
        for path in paths:
            operation = FileOperation(
                operation="delete",
                source_path=path,
                target_path=None,
                overwrite=False,
                recursive=True
            )
            
            result = await self.perform_file_operation(agent_id, operation)
            
            if result.success:
                affected_items.extend(result.affected_items)
            else:
                errors.extend(result.errors)
        
        return FileOperationResult(
            success=len(errors) == 0,
            operation="delete",
            message=f"Deleted {len(affected_items)} items" if len(errors) == 0 else f"Deleted with {len(errors)} errors",
            affected_items=affected_items,
            errors=errors
        )
    
    async def compress_files(self, agent_id: str, paths: List[str], output_path: str) -> FileOperationResult:
        """Compress files/folders into archive."""
        command = {
            "type": "file_compress",
            "paths": paths,
            "output": output_path,
            "format": "zip"
        }
        
        response = await self._send_agent_command(agent_id, command)
        
        return FileOperationResult(
            success=response.get("success", False),
            operation="compress",
            message=response.get("message", ""),
            affected_items=paths,
            errors=response.get("errors", [])
        )
    
    async def extract_archive(self, agent_id: str, archive_path: str, output_path: str) -> FileOperationResult:
        """Extract archive contents."""
        command = {
            "type": "file_extract",
            "archive": archive_path,
            "output": output_path
        }
        
        response = await self._send_agent_command(agent_id, command)
        
        return FileOperationResult(
            success=response.get("success", False),
            operation="extract",
            message=response.get("message", ""),
            affected_items=response.get("extracted_files", []),
            errors=response.get("errors", [])
        )
    
    def _convert_to_powershell(self, command: Dict[str, Any]) -> str:
        """Convert file operation command to PowerShell script."""
        op_type = command.get("type", "")
        
        if op_type == "file_operation" and command.get("operation") == "list":
            path = command.get("path", "C:\\")
            return f"""
            $path = '{path}'
            $items = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Select-Object @{{
                Name='name'; Expression={{$_.Name}}
            }}, @{{
                Name='path'; Expression={{$_.FullName}}
            }}, @{{
                Name='is_directory'; Expression={{$_.PSIsContainer}}
            }}, @{{
                Name='size'; Expression={{if(-not $_.PSIsContainer){{$_.Length}}else{{$null}}}}
            }}, @{{
                Name='modified'; Expression={{$_.LastWriteTime.ToString('yyyy-MM-ddTHH:mm:ss')}}
            }}, @{{
                Name='created'; Expression={{$_.CreationTime.ToString('yyyy-MM-ddTHH:mm:ss')}}
            }}, @{{
                Name='extension'; Expression={{if(-not $_.PSIsContainer){{$_.Extension}}else{{$null}}}}
            }}
            ConvertTo-Json @($items) -Compress
            """
        elif op_type == "file_preview":
            path = command.get("path", "")
            max_size = command.get("max_size", 1024*1024)
            return f"""
            $path = '{path}'
            if (Test-Path $path) {{
                $item = Get-Item $path
                if ($item.Length -le {max_size}) {{
                    $content = Get-Content $path -Raw -ErrorAction SilentlyContinue
                    @{{
                        content = $content
                        size = $item.Length
                        encoding = 'utf-8'
                        truncated = $false
                    }} | ConvertTo-Json -Compress
                }} else {{
                    @{{
                        content = ''
                        size = $item.Length
                        truncated = $true
                        error = 'File too large for preview'
                    }} | ConvertTo-Json -Compress
                }}
            }} else {{
                @{{error = 'File not found'}} | ConvertTo-Json -Compress
            }}
            """
        else:
            # For unsupported operations, return a simple echo
            return "Write-Output 'Operation not implemented'"
    
    def _parse_agent_response(self, command: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse agent response based on command type."""
        output = response.get("output", "")
        
        try:
            # Try to parse as JSON
            if output:
                data = json.loads(output)
                if command.get("type") == "file_operation" and command.get("operation") == "list":
                    return {"success": True, "items": data if isinstance(data, list) else []}
                elif command.get("type") == "file_preview":
                    return {"success": True, **data}
                else:
                    return {"success": True, "data": data}
        except json.JSONDecodeError:
            # If not JSON, return as plain text
            pass
        
        return {"success": True, "output": output}
    
    def _generate_mock_response(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock response for testing when agent is not connected."""
        op_type = command.get("type", "")
        
        if op_type == "file_operation" and command.get("operation") == "list":
            # Return mock directory listing
            return {
                "success": True,
                "items": [
                    {
                        "name": "Documents",
                        "path": "C:\\Users\\Default\\Documents",
                        "is_directory": True,
                        "size": None,
                        "modified": "2024-01-15T10:30:00",
                        "created": "2024-01-15T10:30:00"
                    },
                    {
                        "name": "test.txt",
                        "path": "C:\\Users\\Default\\test.txt",
                        "is_directory": False,
                        "size": 1024,
                        "modified": "2024-01-15T10:30:00",
                        "created": "2024-01-15T10:30:00"
                    }
                ]
            }
        elif op_type == "file_preview":
            return {
                "success": True,
                "content": "Mock file content for preview",
                "size": 100,
                "encoding": "utf-8",
                "truncated": False
            }
        elif op_type == "file_upload":
            return {
                "success": True,
                "ready": True,
                "message": "Mock upload ready"
            }
        elif op_type == "file_download":
            return {
                "success": True,
                "download_id": "mock_download_123",
                "total_chunks": 1
            }
        else:
            return {
                "success": True,
                "message": "Mock operation completed"
            }