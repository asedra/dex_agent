"""Schemas for Windows Event Log functionality."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from enum import Enum


class EventLevel(str, Enum):
    """Windows Event Log levels."""
    CRITICAL = "Critical"
    ERROR = "Error"
    WARNING = "Warning"
    INFORMATION = "Information"
    VERBOSE = "Verbose"


class EventLogType(str, Enum):
    """Types of Windows Event Logs."""
    SYSTEM = "System"
    APPLICATION = "Application"
    SECURITY = "Security"
    SETUP = "Setup"
    FORWARDED = "Forwarded Events"
    CUSTOM = "Custom"


class EventLogFilter(BaseModel):
    """Filter criteria for event logs."""
    log_name: Optional[EventLogType] = None
    level: Optional[List[EventLevel]] = None
    source: Optional[str] = None
    event_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    keyword: Optional[str] = None
    limit: Optional[int] = 100
    offset: Optional[int] = 0


class WindowsEventLog(BaseModel):
    """Windows Event Log entry."""
    id: int
    log_name: str
    source: str
    event_id: int
    level: EventLevel
    task_category: Optional[str] = None
    keywords: Optional[List[str]] = None
    timestamp: datetime
    computer: str
    user: Optional[str] = None
    message: str
    data: Optional[Dict[str, Any]] = None


class EventLogResponse(BaseModel):
    """Response containing event logs."""
    events: List[WindowsEventLog]
    total: int
    page: int
    page_size: int
    has_more: bool


class EventLogStats(BaseModel):
    """Statistics for event logs."""
    total_events: int
    critical_count: int
    error_count: int
    warning_count: int
    info_count: int
    verbose_count: int
    sources: List[Dict[str, int]]
    recent_critical: List[WindowsEventLog]
    recent_errors: List[WindowsEventLog]


class EventAlertRule(BaseModel):
    """Alert rule for event monitoring."""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    log_name: EventLogType
    level: Optional[List[EventLevel]] = None
    source: Optional[str] = None
    event_id: Optional[List[int]] = None
    keywords: Optional[List[str]] = None
    enabled: bool = True
    notify_email: Optional[bool] = False
    notify_webhook: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EventExportRequest(BaseModel):
    """Request for exporting event logs."""
    format: str  # "csv" or "json"
    filters: EventLogFilter
    include_data: bool = False


class EventStreamRequest(BaseModel):
    """Request for streaming event logs."""
    log_names: Optional[List[EventLogType]] = None
    levels: Optional[List[EventLevel]] = None
    sources: Optional[List[str]] = None
    follow: bool = True  # Continue streaming new events