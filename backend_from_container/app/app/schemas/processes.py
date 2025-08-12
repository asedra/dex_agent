"""Process management schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProcessStatus(str, Enum):
    """Process status enumeration."""
    RUNNING = "running"
    SUSPENDED = "suspended"
    STOPPED = "stopped"
    ZOMBIE = "zombie"
    UNKNOWN = "unknown"


class ProcessPriority(str, Enum):
    """Process priority levels."""
    REALTIME = "realtime"
    HIGH = "high"
    ABOVE_NORMAL = "above_normal"
    NORMAL = "normal"
    BELOW_NORMAL = "below_normal"
    IDLE = "idle"


class ProcessInfo(BaseModel):
    """Process information schema."""
    pid: int = Field(..., description="Process ID")
    name: str = Field(..., description="Process name")
    path: Optional[str] = Field(None, description="Executable path")
    status: ProcessStatus = Field(..., description="Process status")
    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_mb: float = Field(..., description="Memory usage in MB")
    memory_percent: float = Field(..., description="Memory usage percentage")
    threads: int = Field(..., description="Number of threads")
    handles: Optional[int] = Field(None, description="Number of handles (Windows)")
    user: Optional[str] = Field(None, description="Process owner")
    create_time: datetime = Field(..., description="Process creation time")
    command_line: Optional[str] = Field(None, description="Command line arguments")
    parent_pid: Optional[int] = Field(None, description="Parent process ID")
    priority: Optional[ProcessPriority] = Field(None, description="Process priority")
    is_system: bool = Field(False, description="Is system process")


class ProcessListRequest(BaseModel):
    """Request for listing processes."""
    sort_by: Optional[str] = Field("cpu_percent", description="Sort field")
    sort_desc: bool = Field(True, description="Sort descending")
    filter_name: Optional[str] = Field(None, description="Filter by name")
    filter_user: Optional[str] = Field(None, description="Filter by user")
    include_system: bool = Field(True, description="Include system processes")
    limit: Optional[int] = Field(None, description="Limit results")


class ProcessListResponse(BaseModel):
    """Response for process list."""
    processes: List[ProcessInfo]
    total: int
    timestamp: datetime
    system_stats: Dict[str, Any]


class ProcessKillRequest(BaseModel):
    """Request to kill a process."""
    pid: int = Field(..., description="Process ID to kill")
    force: bool = Field(False, description="Force kill")
    kill_tree: bool = Field(False, description="Kill process tree")


class ProcessKillResponse(BaseModel):
    """Response for process kill operation."""
    success: bool
    message: str
    killed_pids: List[int]
    errors: Optional[List[str]] = None


class ProcessSuspendResumeRequest(BaseModel):
    """Request to suspend or resume a process."""
    pid: int = Field(..., description="Process ID")
    action: str = Field(..., description="Action: suspend or resume")


class ProcessPriorityRequest(BaseModel):
    """Request to change process priority."""
    pid: int = Field(..., description="Process ID")
    priority: ProcessPriority = Field(..., description="New priority level")


class ProcessTreeNode(BaseModel):
    """Process tree node for hierarchy display."""
    process: ProcessInfo
    children: List["ProcessTreeNode"] = []


class ProcessTreeResponse(BaseModel):
    """Response containing process tree."""
    tree: List[ProcessTreeNode]
    total_processes: int
    timestamp: datetime


class ProcessResourceUsage(BaseModel):
    """Process resource usage over time."""
    pid: int
    name: str
    timestamps: List[datetime]
    cpu_history: List[float]
    memory_history: List[float]
    io_read_bytes: Optional[int] = None
    io_write_bytes: Optional[int] = None
    network_sent: Optional[int] = None
    network_recv: Optional[int] = None


class ProcessMonitorRequest(BaseModel):
    """Request to monitor specific processes."""
    pids: List[int] = Field(..., description="PIDs to monitor")
    duration_seconds: int = Field(60, description="Monitoring duration")
    interval_seconds: int = Field(5, description="Sampling interval")


class ProcessMonitorResponse(BaseModel):
    """Response for process monitoring."""
    usage: List[ProcessResourceUsage]
    summary: Dict[str, Any]


# Update forward references
ProcessTreeNode.model_rebuild()