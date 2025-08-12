from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class ServiceStatus(str, Enum):
    RUNNING = "Running"
    STOPPED = "Stopped"
    PAUSED = "Paused"
    START_PENDING = "StartPending"
    STOP_PENDING = "StopPending"
    PAUSE_PENDING = "PausePending"
    CONTINUE_PENDING = "ContinuePending"


class ServiceStartType(str, Enum):
    AUTOMATIC = "Automatic"
    AUTOMATIC_DELAYED = "AutomaticDelayedStart"
    MANUAL = "Manual"
    DISABLED = "Disabled"
    BOOT = "Boot"
    SYSTEM = "System"


class ServiceInfo(BaseModel):
    name: str
    display_name: str
    status: ServiceStatus
    start_type: ServiceStartType
    description: Optional[str] = None
    can_stop: bool = False
    can_pause_and_continue: bool = False
    dependencies: List[str] = []
    dependent_services: List[str] = []
    path: Optional[str] = None
    account_name: Optional[str] = None
    process_id: Optional[int] = None


class ServiceListResponse(BaseModel):
    services: List[ServiceInfo]
    total: int
    agent_id: str
    timestamp: datetime


class ServiceActionRequest(BaseModel):
    action: str  # start, stop, restart, pause, continue
    force: bool = False


class ServiceActionResponse(BaseModel):
    success: bool
    message: str
    service_name: str
    new_status: Optional[ServiceStatus] = None
    timestamp: datetime


class ServiceConfigRequest(BaseModel):
    start_type: Optional[ServiceStartType] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    recovery_actions: Optional[Dict[str, Any]] = None


class ServiceConfigResponse(BaseModel):
    success: bool
    message: str
    service_name: str
    config: Dict[str, Any]
    timestamp: datetime


class ServiceBatchActionRequest(BaseModel):
    services: List[str]
    action: str
    force: bool = False


class ServiceBatchActionResponse(BaseModel):
    success: bool
    results: List[ServiceActionResponse]
    failed_services: List[str]
    timestamp: datetime


class ServiceDependencyGraph(BaseModel):
    service_name: str
    dependencies: List[Dict[str, Any]]
    dependent_services: List[Dict[str, Any]]
    graph_data: Dict[str, Any]