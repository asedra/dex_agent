"""Software package models for the DexAgents system."""
from dataclasses import dataclass, field
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


@dataclass
class SoftwarePackage:
    """Software package definition."""
    id: int
    name: str
    version: str
    description: Optional[str] = None
    package_type: PackageType = PackageType.EXE
    category: SoftwareCategory = SoftwareCategory.OTHER
    vendor: Optional[str] = None
    size_bytes: Optional[int] = None
    download_url: Optional[str] = None
    file_path: Optional[str] = None
    silent_install_args: Optional[str] = None
    silent_uninstall_args: Optional[str] = None
    install_script: Optional[str] = None
    uninstall_script: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    requires_reboot: bool = False
    requires_admin: bool = True
    signature_verified: bool = False
    checksum: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert package to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'package_type': self.package_type.value if isinstance(self.package_type, PackageType) else self.package_type,
            'category': self.category.value if isinstance(self.category, SoftwareCategory) else self.category,
            'vendor': self.vendor,
            'size_bytes': self.size_bytes,
            'download_url': self.download_url,
            'file_path': self.file_path,
            'silent_install_args': self.silent_install_args,
            'silent_uninstall_args': self.silent_uninstall_args,
            'install_script': self.install_script,
            'uninstall_script': self.uninstall_script,
            'dependencies': self.dependencies,
            'metadata': self.metadata,
            'requires_reboot': self.requires_reboot,
            'requires_admin': self.requires_admin,
            'signature_verified': self.signature_verified,
            'checksum': self.checksum,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class InstalledSoftware:
    """Installed software on an agent."""
    id: int
    agent_id: str
    name: str
    version: str
    vendor: Optional[str] = None
    install_date: Optional[datetime] = None
    install_location: Optional[str] = None
    uninstall_string: Optional[str] = None
    registry_key: Optional[str] = None
    size_bytes: Optional[int] = None
    last_used: Optional[datetime] = None
    detected_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'name': self.name,
            'version': self.version,
            'vendor': self.vendor,
            'install_date': self.install_date.isoformat() if self.install_date else None,
            'install_location': self.install_location,
            'uninstall_string': self.uninstall_string,
            'registry_key': self.registry_key,
            'size_bytes': self.size_bytes,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None
        }


@dataclass
class InstallationJob:
    """Software installation job."""
    id: int
    agent_id: str
    package_id: int
    status: InstallationStatus = InstallationStatus.PENDING
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percent: int = 0
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    output_log: Optional[str] = None
    rollback_performed: bool = False
    retry_count: int = 0
    max_retries: int = 3
    install_params: Dict[str, Any] = field(default_factory=dict)
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'package_id': self.package_id,
            'status': self.status.value if isinstance(self.status, InstallationStatus) else self.status,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress_percent': self.progress_percent,
            'current_step': self.current_step,
            'error_message': self.error_message,
            'output_log': self.output_log,
            'rollback_performed': self.rollback_performed,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'install_params': self.install_params,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class SoftwareRepository:
    """Software repository configuration."""
    id: int
    name: str
    type: str  # chocolatey, winget, custom
    url: Optional[str] = None
    api_key: Optional[str] = None
    enabled: bool = True
    priority: int = 0
    last_sync: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'url': self.url,
            'api_key': self.api_key,
            'enabled': self.enabled,
            'priority': self.priority,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }