"""Pydantic schemas for software management."""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PackageType(str, Enum):
    """Software package types."""
    MSI = "msi"
    EXE = "exe"
    CHOCOLATEY = "chocolatey"
    WINGET = "winget"
    POWERSHELL = "powershell"
    ZIP = "zip"
    WINDOWS_UPDATE = "windows_update"


class InstallationStatus(str, Enum):
    """Installation status types."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    INSTALLING = "installing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLBACK = "rollback"


class SoftwareCategory(str, Enum):
    """Software categories."""
    PRODUCTIVITY = "productivity"
    DEVELOPMENT = "development"
    SECURITY = "security"
    UTILITIES = "utilities"
    MULTIMEDIA = "multimedia"
    COMMUNICATION = "communication"
    SYSTEM = "system"
    OTHER = "other"


class SoftwarePackageBase(BaseModel):
    """Base software package schema."""
    name: str = Field(..., description="Software package name")
    version: str = Field(..., description="Software version")
    description: Optional[str] = Field(None, description="Package description")
    package_type: PackageType = Field(PackageType.EXE, description="Package type")
    installer: Optional[str] = Field(None, description="Package type (alternative to package_type)")
    category: SoftwareCategory = Field(SoftwareCategory.OTHER, description="Software category")
    vendor: Optional[str] = Field(None, description="Software vendor")
    size_bytes: Optional[int] = Field(None, description="Package size in bytes")
    download_url: Optional[str] = Field(None, description="Download URL")
    url: Optional[str] = Field(None, description="Download URL (alternative to download_url)")
    silent_install_args: Optional[str] = Field(None, description="Silent installation arguments")
    silent_uninstall_args: Optional[str] = Field(None, description="Silent uninstallation arguments")
    install_script: Optional[str] = Field(None, description="PowerShell installation script")
    uninstall_script: Optional[str] = Field(None, description="PowerShell uninstallation script")
    dependencies: List[str] = Field(default_factory=list, description="Package dependencies")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    requires_reboot: bool = Field(False, description="Requires system reboot")
    requires_admin: bool = Field(True, description="Requires administrator privileges")
    
    @validator('package_type', pre=True)
    def validate_package_type(cls, v, values):
        """Handle alternative installer field name"""
        if 'installer' in values and values['installer'] and not v:
            # Map installer to package_type
            installer_map = {
                'msi': PackageType.MSI,
                'exe': PackageType.EXE,
                'chocolatey': PackageType.CHOCOLATEY,
                'winget': PackageType.WINGET,
                'powershell': PackageType.POWERSHELL,
                'zip': PackageType.ZIP
            }
            return installer_map.get(values['installer'].lower(), PackageType.EXE)
        return v if v is not None else PackageType.EXE
    
    @validator('download_url', pre=True)
    def validate_download_url(cls, v, values):
        """Handle alternative url field name"""
        if 'url' in values and values['url'] and not v:
            return values['url']
        return v


class SoftwarePackageCreate(SoftwarePackageBase):
    """Create software package schema."""
    pass


class SoftwarePackageUpdate(BaseModel):
    """Update software package schema."""
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    package_type: Optional[PackageType] = None
    category: Optional[SoftwareCategory] = None
    vendor: Optional[str] = None
    size_bytes: Optional[int] = None
    download_url: Optional[str] = None
    silent_install_args: Optional[str] = None
    silent_uninstall_args: Optional[str] = None
    install_script: Optional[str] = None
    uninstall_script: Optional[str] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    requires_reboot: Optional[bool] = None
    requires_admin: Optional[bool] = None


class SoftwarePackageResponse(SoftwarePackageBase):
    """Software package response schema."""
    id: int
    file_path: Optional[str] = None
    signature_verified: bool = False
    checksum: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InstalledSoftwareBase(BaseModel):
    """Base installed software schema."""
    name: str
    version: str
    vendor: Optional[str] = None
    install_location: Optional[str] = None
    size_bytes: Optional[int] = None


class InstalledSoftwareResponse(InstalledSoftwareBase):
    """Installed software response schema."""
    id: int
    agent_id: str
    install_date: Optional[datetime] = None
    uninstall_string: Optional[str] = None
    registry_key: Optional[str] = None
    last_used: Optional[datetime] = None
    detected_at: datetime
    
    class Config:
        from_attributes = True


class InstallationJobBase(BaseModel):
    """Base installation job schema."""
    agent_id: str = Field(..., description="Target agent ID")
    package_id: int = Field(..., description="Software package ID")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled installation time")
    install_params: Dict[str, Any] = Field(default_factory=dict, description="Installation parameters")


class InstallationJobCreate(InstallationJobBase):
    """Create installation job schema."""
    pass


class InstallationJobUpdate(BaseModel):
    """Update installation job schema."""
    status: Optional[InstallationStatus] = None
    progress_percent: Optional[int] = Field(None, ge=0, le=100)
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    output_log: Optional[str] = None


class InstallationJobResponse(InstallationJobBase):
    """Installation job response schema."""
    id: int
    status: InstallationStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percent: int = 0
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    output_log: Optional[str] = None
    rollback_performed: bool = False
    retry_count: int = 0
    max_retries: int = 3
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SoftwareInventoryRequest(BaseModel):
    """Software inventory request schema."""
    agent_id: str = Field(..., description="Agent ID to get inventory from")
    refresh: bool = Field(False, description="Force refresh inventory")


class SoftwareInstallRequest(BaseModel):
    """Software installation request schema."""
    package_id: Optional[int] = Field(None, description="Package ID from repository")
    package_name: Optional[str] = Field(None, description="Package name for Chocolatey/Winget")
    package: Optional[str] = Field(None, description="Package name (alternative to package_name)")
    package_type: PackageType = Field(..., description="Installation method")
    source: Optional[str] = Field(None, description="Installation source (alternative to package_type)")
    version: Optional[str] = Field(None, description="Specific version to install")
    silent: bool = Field(True, description="Use silent installation")
    force: bool = Field(False, description="Force installation even if already installed")
    custom_args: Optional[str] = Field(None, description="Custom installation arguments")
    install_script: Optional[str] = Field(None, description="Custom PowerShell installation script")
    
    @validator('package_name', pre=True)
    def validate_package_name(cls, v, values):
        """Handle alternative package field name"""
        if 'package' in values and values['package'] and not v:
            return values['package']
        return v
    
    @validator('package_type', pre=True)
    def validate_package_type(cls, v, values):
        """Handle alternative source field name"""
        if 'source' in values and values['source'] and not v:
            # Map source to package_type
            source_map = {
                'chocolatey': PackageType.CHOCOLATEY,
                'winget': PackageType.WINGET,
                'msi': PackageType.MSI,
                'exe': PackageType.EXE,
                'powershell': PackageType.POWERSHELL
            }
            return source_map.get(values['source'].lower(), PackageType.EXE)
        return v if v is not None else PackageType.EXE


class SoftwareUninstallRequest(BaseModel):
    """Software uninstallation request schema."""
    software_id: Optional[int] = Field(None, description="Installed software ID")
    software_name: Optional[str] = Field(None, description="Software name to uninstall")
    package: Optional[str] = Field(None, description="Software name (alternative to software_name)")
    silent: bool = Field(True, description="Use silent uninstallation")
    force: bool = Field(False, description="Force uninstallation")
    custom_args: Optional[str] = Field(None, description="Custom uninstallation arguments")
    
    @validator('software_name', pre=True)
    def validate_software_name(cls, v, values):
        """Handle alternative package field name"""
        if 'package' in values and values['package'] and not v:
            return values['package']
        return v


class PackageUploadResponse(BaseModel):
    """Package upload response schema."""
    package_id: int
    filename: str
    size_bytes: int
    checksum: str
    upload_path: str
    message: str = "Package uploaded successfully"


class SoftwareRepositoryBase(BaseModel):
    """Base software repository schema."""
    name: str = Field(..., description="Repository name")
    type: str = Field(..., description="Repository type (chocolatey, winget, custom)")
    url: Optional[str] = Field(None, description="Repository URL")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    enabled: bool = Field(True, description="Repository enabled status")
    priority: int = Field(0, description="Repository priority (lower is higher priority)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SoftwareRepositoryCreate(SoftwareRepositoryBase):
    """Create software repository schema."""
    pass


class SoftwareRepositoryResponse(SoftwareRepositoryBase):
    """Software repository response schema."""
    id: int
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BulkInstallRequest(BaseModel):
    """Bulk installation request schema."""
    agent_ids: List[str] = Field(..., description="List of agent IDs")
    package_ids: Optional[List[int]] = Field(None, description="List of package IDs to install")
    packages: Optional[List[str]] = Field(None, description="List of package names (alternative to package_ids)")
    schedule: Optional[datetime] = Field(None, description="Scheduled installation time")
    sequential: bool = Field(False, description="Install sequentially instead of parallel")
    
    @validator('package_ids', pre=True)
    def validate_package_ids(cls, v, values):
        """Handle alternative packages field name"""
        if 'packages' in values and values['packages'] and not v:
            # For now, convert package names to dummy IDs
            # In a real implementation, you would look up the package IDs from names
            return [hash(pkg) % 1000000 for pkg in values['packages']]
        return v or []


class InstallationProgressUpdate(BaseModel):
    """Installation progress update schema."""
    job_id: int
    status: InstallationStatus
    progress_percent: int
    current_step: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)