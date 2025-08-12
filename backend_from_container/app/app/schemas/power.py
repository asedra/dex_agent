"""Power management schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PowerAction(str, Enum):
    """Power management actions."""
    SHUTDOWN = "shutdown"
    RESTART = "restart"
    SLEEP = "sleep"
    HIBERNATE = "hibernate"
    LOGOFF = "logoff"
    LOCK = "lock"
    ABORT = "abort"  # Abort pending shutdown/restart


class PowerPlan(str, Enum):
    """Power plan profiles."""
    BALANCED = "balanced"
    HIGH_PERFORMANCE = "high_performance"
    POWER_SAVER = "power_saver"
    CUSTOM = "custom"


class PowerActionRequest(BaseModel):
    """Request for power action."""
    action: PowerAction = Field(..., description="Power action to perform")
    delay_seconds: int = Field(0, description="Delay before action (0 for immediate)")
    message: Optional[str] = Field(None, description="Message to display to users")
    force: bool = Field(False, description="Force action without saving work")
    planned: bool = Field(False, description="Mark as planned maintenance")


class PowerActionResponse(BaseModel):
    """Response for power action."""
    success: bool
    action: PowerAction
    message: str
    scheduled_time: Optional[datetime] = None
    abort_command: Optional[str] = None


class BatteryInfo(BaseModel):
    """Battery information."""
    present: bool = Field(..., description="Battery present")
    charging: bool = Field(..., description="Is charging")
    charge_percent: int = Field(..., description="Charge percentage")
    time_remaining_minutes: Optional[int] = Field(None, description="Time remaining in minutes")
    design_capacity: Optional[int] = Field(None, description="Design capacity in mWh")
    full_charge_capacity: Optional[int] = Field(None, description="Full charge capacity in mWh")
    voltage: Optional[float] = Field(None, description="Voltage in volts")
    wear_level: Optional[int] = Field(None, description="Battery wear level percentage")


class PowerStatus(BaseModel):
    """System power status."""
    ac_power: bool = Field(..., description="AC power connected")
    battery_info: Optional[BatteryInfo] = None
    active_power_plan: str = Field(..., description="Active power plan")
    available_power_plans: List[str] = Field(..., description="Available power plans")
    last_sleep_time: Optional[datetime] = None
    last_wake_time: Optional[datetime] = None
    uptime_seconds: int = Field(..., description="System uptime in seconds")
    can_hibernate: bool = Field(..., description="Hibernate support")
    can_sleep: bool = Field(..., description="Sleep support")
    fast_startup_enabled: bool = Field(..., description="Fast startup enabled")


class PowerPlanSettings(BaseModel):
    """Power plan configuration settings."""
    plan_name: str = Field(..., description="Power plan name")
    plan_guid: str = Field(..., description="Power plan GUID")
    is_active: bool = Field(..., description="Is currently active")
    display_off_minutes_ac: int = Field(..., description="Display off timeout on AC")
    display_off_minutes_dc: int = Field(..., description="Display off timeout on battery")
    sleep_after_minutes_ac: int = Field(..., description="Sleep timeout on AC")
    sleep_after_minutes_dc: int = Field(..., description="Sleep timeout on battery")
    hibernate_after_minutes_ac: int = Field(..., description="Hibernate timeout on AC")
    hibernate_after_minutes_dc: int = Field(..., description="Hibernate timeout on battery")
    processor_max_ac: int = Field(..., description="Max processor state on AC (%)")
    processor_max_dc: int = Field(..., description="Max processor state on battery (%)")
    processor_min_ac: int = Field(..., description="Min processor state on AC (%)")
    processor_min_dc: int = Field(..., description="Min processor state on battery (%)")


class PowerPlanListResponse(BaseModel):
    """Response for power plan list."""
    plans: List[PowerPlanSettings]
    active_plan: str
    total: int


class SetPowerPlanRequest(BaseModel):
    """Request to set active power plan."""
    plan_guid: Optional[str] = Field(None, description="Power plan GUID to activate")
    plan: Optional[str] = Field(None, description="Power plan name to activate")


class UpdatePowerPlanRequest(BaseModel):
    """Request to update power plan settings."""
    plan_guid: str = Field(..., description="Power plan GUID")
    display_off_minutes_ac: Optional[int] = None
    display_off_minutes_dc: Optional[int] = None
    sleep_after_minutes_ac: Optional[int] = None
    sleep_after_minutes_dc: Optional[int] = None
    hibernate_after_minutes_ac: Optional[int] = None
    hibernate_after_minutes_dc: Optional[int] = None
    processor_max_ac: Optional[int] = None
    processor_max_dc: Optional[int] = None


class WakeTimer(BaseModel):
    """Wake timer information."""
    id: str = Field(..., description="Timer ID")
    owner: str = Field(..., description="Process or service that set the timer")
    wake_time: datetime = Field(..., description="Scheduled wake time")
    enabled: bool = Field(..., description="Timer enabled")
    reason: Optional[str] = Field(None, description="Wake reason")


class WakeTimersResponse(BaseModel):
    """Response for wake timers list."""
    timers: List[WakeTimer]
    total: int


class PowerEventLog(BaseModel):
    """Power event log entry."""
    timestamp: datetime
    event_type: str  # sleep, wake, shutdown, restart, etc.
    source: str
    details: Optional[str] = None
    wake_source: Optional[str] = None  # For wake events


class PowerEventLogResponse(BaseModel):
    """Response for power event log."""
    events: List[PowerEventLog]
    total: int
    period_days: int


class ScheduledTaskInfo(BaseModel):
    """Scheduled shutdown/restart task information."""
    task_id: str
    action: PowerAction
    scheduled_time: datetime
    message: Optional[str] = None
    created_by: str
    created_at: datetime
    can_abort: bool


class ScheduledTasksResponse(BaseModel):
    """Response for scheduled power tasks."""
    tasks: List[ScheduledTaskInfo]
    total: int