from pydantic import BaseModel, Field
from typing import Optional, Any, List, Literal
from datetime import datetime

class RegistryKey(BaseModel):
    name: str
    path: str
    sub_key_count: int = Field(alias="SubKeyCount")
    value_count: int = Field(alias="ValueCount")
    
    class Config:
        populate_by_name = True

class RegistryValue(BaseModel):
    name: str
    value: Any
    type: str
    data: Optional[str] = None

class RegistryValueCreateRequest(BaseModel):
    path: str = Field(description="Registry path")
    name: str = Field(description="Value name")
    value: Any = Field(description="Value data")
    type: str = Field(description="Value type (String, DWord, etc.)")

class RegistryBackupRequest(BaseModel):
    path: str = Field(description="Registry path to backup")
    backup_file: Optional[str] = Field(default=None, description="Backup file path")

class RegistrySearchRequest(BaseModel):
    search_path: str = Field(default="HKLM:\\SOFTWARE", description="Registry path to start search from")
    pattern: str = Field(description="Search pattern (supports wildcards)")
    search_keys: Optional[bool] = True
    search_values: Optional[bool] = True
    search_type: Optional[Literal["key", "value", "both"]] = None
    max_results: Optional[int] = 100

class RegistryBackupResponse(BaseModel):
    backup_file: str
    timestamp: datetime
    path: str

class RegistryImportRequest(BaseModel):
    file: Optional[str] = Field(default=None, description="Path to .reg file to import")
    content: Optional[str] = Field(default=None, description="Content of .reg file to import")
    create_backup: bool = Field(default=True, description="Create backup before import")

class RegistryExportRequest(BaseModel):
    path: str = Field(description="Registry path to export")
    file: Optional[str] = Field(default=None, description="Export file path")
    filename: Optional[str] = Field(default=None, description="Export filename")

class RegistryTreeNode(BaseModel):
    name: str
    path: str
    type: Literal["key", "value"]
    children: Optional[List['RegistryTreeNode']] = []
    value: Optional[Any] = None
    value_type: Optional[str] = None
    expanded: bool = False

RegistryTreeNode.model_rebuild()