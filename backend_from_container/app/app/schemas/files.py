"""File management schemas for API validation."""
from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re


class FileItemBase(BaseModel):
    """Base schema for file/folder items."""
    name: str = Field(..., description="File or folder name")
    path: str = Field(..., description="Full path to the item")
    is_directory: bool = Field(default=False, description="Whether item is a directory")
    size: Optional[int] = Field(None, description="File size in bytes")
    modified: Optional[datetime] = Field(None, description="Last modification time")
    created: Optional[datetime] = Field(None, description="Creation time")
    permissions: Optional[str] = Field(None, description="File permissions")
    
    @field_validator('path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate path to prevent directory traversal."""
        if '..' in v or v.startswith('~'):
            raise ValueError("Invalid path: directory traversal not allowed")
        return v


class FileItem(FileItemBase):
    """Schema for file/folder item response."""
    model_config = ConfigDict(from_attributes=True)
    
    extension: Optional[str] = Field(None, description="File extension")
    mime_type: Optional[str] = Field(None, description="MIME type for file")
    is_hidden: bool = Field(default=False, description="Whether item is hidden")
    is_readable: bool = Field(default=True, description="Whether item is readable")
    is_writable: bool = Field(default=True, description="Whether item is writable")
    children_count: Optional[int] = Field(None, description="Number of children for directories")


class DirectoryContent(BaseModel):
    """Schema for directory listing response."""
    path: str = Field(..., description="Current directory path")
    parent: Optional[str] = Field(None, description="Parent directory path")
    items: List[FileItem] = Field(default_factory=list, description="List of items in directory")
    total_items: int = Field(0, description="Total number of items")
    
    model_config = ConfigDict(from_attributes=True)


class FileOperation(BaseModel):
    """Schema for file operation requests."""
    operation: str = Field(..., description="Operation type: copy, move, delete, rename, create")
    source_path: str = Field(..., description="Source file/folder path")
    target_path: Optional[str] = Field(None, description="Target path for copy/move/rename")
    overwrite: bool = Field(default=False, description="Whether to overwrite existing files")
    recursive: bool = Field(default=False, description="Whether to apply operation recursively")
    
    @field_validator('operation')
    @classmethod
    def validate_operation(cls, v: str) -> str:
        """Validate operation type."""
        allowed_operations = ['copy', 'move', 'delete', 'rename', 'create', 'mkdir', 'list']
        if v not in allowed_operations:
            raise ValueError(f"Invalid operation. Must be one of: {', '.join(allowed_operations)}")
        return v
    
    @field_validator('source_path', 'target_path')
    @classmethod
    def validate_paths(cls, v: Optional[str]) -> Optional[str]:
        """Validate paths to prevent directory traversal."""
        if v and ('..' in v or v.startswith('~')):
            raise ValueError("Invalid path: directory traversal not allowed")
        return v


class FileOperationResult(BaseModel):
    """Schema for file operation response."""
    success: bool = Field(..., description="Whether operation was successful")
    operation: str = Field(..., description="Operation type performed")
    message: str = Field(..., description="Result message")
    affected_items: List[str] = Field(default_factory=list, description="List of affected file paths")
    errors: List[str] = Field(default_factory=list, description="List of errors if any")
    
    model_config = ConfigDict(from_attributes=True)


class FileUploadRequest(BaseModel):
    """Schema for file upload metadata."""
    filename: str = Field(..., description="Original filename")
    target_path: str = Field(..., description="Target directory path")
    overwrite: bool = Field(default=False, description="Whether to overwrite existing file")
    chunk_size: Optional[int] = Field(None, description="Chunk size for large file uploads")
    total_size: Optional[int] = Field(None, description="Total file size in bytes")
    
    @field_validator('target_path')
    @classmethod
    def validate_target_path(cls, v: str) -> str:
        """Validate target path."""
        if '..' in v or v.startswith('~'):
            raise ValueError("Invalid path: directory traversal not allowed")
        return v
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate filename for security."""
        invalid_chars = ['/', '\\', '..', '~', '|', '>', '<', ':', '*', '?', '"']
        for char in invalid_chars:
            if char in v:
                raise ValueError(f"Invalid filename: contains forbidden character '{char}'")
        return v


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    success: bool = Field(..., description="Whether upload was successful")
    file_path: str = Field(..., description="Full path of uploaded file")
    size: int = Field(..., description="File size in bytes")
    message: str = Field(..., description="Response message")
    upload_id: Optional[str] = Field(None, description="Upload ID for chunked uploads")
    
    model_config = ConfigDict(from_attributes=True)


class FileDownloadRequest(BaseModel):
    """Schema for file download request."""
    file_path: str = Field(..., description="Path to file to download")
    compress: bool = Field(default=False, description="Whether to compress file before download")
    chunk_size: Optional[int] = Field(None, description="Chunk size for streaming")
    
    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate file path."""
        if '..' in v or v.startswith('~'):
            raise ValueError("Invalid path: directory traversal not allowed")
        return v


class FilePreviewRequest(BaseModel):
    """Schema for file preview request."""
    file_path: str = Field(..., description="Path to file to preview")
    max_size: int = Field(default=1048576, description="Maximum file size to preview (1MB default)")
    encoding: str = Field(default='utf-8', description="Text file encoding")
    
    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate file path."""
        if '..' in v or v.startswith('~'):
            raise ValueError("Invalid path: directory traversal not allowed")
        return v


class FilePreviewResponse(BaseModel):
    """Schema for file preview response."""
    content: Optional[str] = Field(None, description="File content for text files")
    content_type: str = Field(..., description="Content type (text, image, binary)")
    encoding: Optional[str] = Field(None, description="Text encoding if applicable")
    size: int = Field(..., description="File size in bytes")
    truncated: bool = Field(default=False, description="Whether content was truncated")
    preview_url: Optional[str] = Field(None, description="URL for image preview")
    
    model_config = ConfigDict(from_attributes=True)


class FileSearchRequest(BaseModel):
    """Schema for file search request."""
    search_path: str = Field(..., description="Root path to search in")
    pattern: str = Field(..., description="Search pattern (supports wildcards)")
    search_type: str = Field(default='name', description="Search type: name, content, both")
    case_sensitive: bool = Field(default=False, description="Whether search is case sensitive")
    max_results: int = Field(default=100, description="Maximum number of results")
    include_hidden: bool = Field(default=False, description="Whether to include hidden files")
    
    @field_validator('search_path')
    @classmethod
    def validate_search_path(cls, v: str) -> str:
        """Validate search path."""
        if '..' in v or v.startswith('~'):
            raise ValueError("Invalid path: directory traversal not allowed")
        return v
    
    @field_validator('search_type')
    @classmethod
    def validate_search_type(cls, v: str) -> str:
        """Validate search type."""
        allowed_types = ['name', 'content', 'both']
        if v not in allowed_types:
            raise ValueError(f"Invalid search type. Must be one of: {', '.join(allowed_types)}")
        return v


class FileSearchResult(BaseModel):
    """Schema for file search result."""
    results: List[FileItem] = Field(default_factory=list, description="List of matching files")
    total_matches: int = Field(0, description="Total number of matches found")
    search_time: float = Field(..., description="Search duration in seconds")
    truncated: bool = Field(default=False, description="Whether results were truncated")
    
    model_config = ConfigDict(from_attributes=True)


class FilePermissions(BaseModel):
    """Schema for file permissions."""
    path: str = Field(..., description="File/folder path")
    owner: Optional[str] = Field(None, description="File owner")
    group: Optional[str] = Field(None, description="File group")
    permissions: str = Field(..., description="Permission string (e.g., 'rwxr-xr-x')")
    recursive: bool = Field(default=False, description="Apply permissions recursively")
    
    @field_validator('path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate path."""
        if '..' in v or v.startswith('~'):
            raise ValueError("Invalid path: directory traversal not allowed")
        return v


class FileTreeNode(BaseModel):
    """Schema for file tree node."""
    name: str
    path: str
    is_directory: bool
    is_expanded: bool = False
    children: List['FileTreeNode'] = Field(default_factory=list)
    size: Optional[int] = None
    modified: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Update forward references
FileTreeNode.model_rebuild()


class FileTree(BaseModel):
    """Schema for file tree structure."""
    root: FileTreeNode
    total_items: int = 0
    max_depth: int = 3
    
    model_config = ConfigDict(from_attributes=True)