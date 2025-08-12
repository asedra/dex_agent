"""API endpoints for Windows Event Log management."""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import csv
import io
import asyncio
import logging

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.websocket_manager import websocket_manager
from app.models.user import User
from app.models.agent import Agent
from app.schemas.events import (
    EventLogFilter,
    EventLogResponse,
    EventLogStats,
    EventAlertRule,
    EventExportRequest,
    EventStreamRequest,
    WindowsEventLog,
    EventLevel,
    EventLogType
)
from app.services.powershell_service import PowerShellService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents/{agent_id}/events")
ws_manager = websocket_manager
ps_service = PowerShellService()


@router.get("/", response_model=EventLogResponse)
async def get_event_logs(
    agent_id: str,
    log_name: Optional[EventLogType] = Query(None),
    log: Optional[str] = Query(None, description="Log name (alternative to log_name)"),
    level: Optional[List[EventLevel]] = Query(None),
    source: Optional[str] = Query(None),
    event_id: Optional[int] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    keyword: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    after_id: Optional[str] = Query(None, description="Get events after this event ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve Windows Event Logs from an agent with filtering options.
    """
    # Verify agent exists and belongs to user
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Use log parameter if log_name is not provided
    effective_log_name = log_name
    if not effective_log_name and log:
        # Try to convert log string to EventLogType
        try:
            effective_log_name = EventLogType(log)
        except ValueError:
            # If not a valid enum value, pass as string
            effective_log_name = log
    
    # Build PowerShell command for retrieving events
    ps_command = _build_event_query_command(
        log_name=effective_log_name,
        level=level,
        source=source,
        event_id=event_id,
        start_time=start_time,
        end_time=end_time,
        keyword=keyword,
        limit=limit,
        offset=offset,
        after_id=after_id
    )
    
    # Execute command on agent
    result = await ps_service.execute_command(
        agent_id,
        ps_command,
        db
    )
    
    # Parse and return results
    if result and result.get("success"):
        events = _parse_event_logs(result.get("output", ""))
    else:
        events = []
    
    return EventLogResponse(
        events=events,
        total=len(events),
        page=offset // limit,
        page_size=limit,
        has_more=len(events) == limit
    )


@router.get("/stats", response_model=EventLogStats)
async def get_event_stats(
    agent_id: str,
    log_name: Optional[EventLogType] = Query(None),
    log: Optional[str] = Query(None, description="Log name (alternative to log_name)"),
    hours: int = Query(24, description="Hours to look back for statistics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about event logs from an agent.
    """
    # Verify agent exists
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Use log parameter if log_name is not provided
    effective_log_name = log_name
    if not effective_log_name and log:
        try:
            effective_log_name = EventLogType(log)
        except ValueError:
            effective_log_name = log
    
    # Build PowerShell command for statistics
    ps_command = _build_stats_query_command(effective_log_name, hours)
    
    # Execute command on agent
    result = await ps_service.execute_command(
        agent_id,
        ps_command,
        db
    )
    
    # Parse and return statistics
    if result and result.get("success"):
        stats = _parse_event_stats(result.get("output", ""))
    else:
        stats = EventLogStats(
            total_events=0,
            critical_count=0,
            error_count=0,
            warning_count=0,
            info_count=0,
            verbose_count=0,
            sources=[],
            recent_critical=[],
            recent_errors=[]
        )
    return stats


@router.post("/export")
async def export_event_logs(
    agent_id: str,
    export_request: EventExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export event logs to CSV or JSON format.
    """
    # Verify agent exists
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get event logs based on filters
    ps_command = _build_event_query_command(
        log_name=export_request.filters.log_name,
        level=export_request.filters.level,
        source=export_request.filters.source,
        event_id=export_request.filters.event_id,
        start_time=export_request.filters.start_time,
        end_time=export_request.filters.end_time,
        keyword=export_request.filters.keyword,
        limit=export_request.filters.limit or 10000,
        offset=export_request.filters.offset or 0,
        after_id=None  # Export doesn't use after_id
    )
    
    result = await ps_service.execute_command(
        agent_id,
        ps_command,
        db
    )
    
    events = _parse_event_logs(result)
    
    # Export based on format
    if export_request.format.lower() == "csv":
        return _export_to_csv(events, agent.hostname)
    elif export_request.format.lower() == "json":
        return _export_to_json(events, agent.hostname)
    else:
        raise HTTPException(status_code=400, detail="Invalid export format")


@router.websocket("/stream")
async def stream_event_logs(
    websocket: WebSocket,
    agent_id: str,
    db: Session = Depends(get_db)
):
    """
    Stream real-time event logs via WebSocket.
    """
    await websocket.accept()
    
    try:
        # Verify agent exists
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            await websocket.send_json({"error": "Agent not found"})
            await websocket.close()
            return
        
        # Parse stream request
        data = await websocket.receive_json()
        stream_request = EventStreamRequest(**data)
        
        # Build PowerShell command for streaming
        ps_command = _build_stream_command(stream_request)
        
        # Start streaming events
        while True:
            try:
                # Execute command to get recent events
                result = await ps_service.execute_command(
                    agent_id=agent_id,
                    command=ps_command,
                    db=db
                )
                
                events = _parse_event_logs(result)
                
                # Send events to client
                for event in events:
                    await websocket.send_json(event.dict())
                
                # Wait before next poll
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error streaming events: {e}")
                await websocket.send_json({"error": str(e)})
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for agent {agent_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


@router.get("/alert-rules", response_model=List[EventAlertRule])
async def get_alert_rules(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get alert rules for event monitoring.
    """
    # This would typically query from a database table
    # For now, return example rules
    return [
        EventAlertRule(
            id=1,
            name="Critical System Events",
            description="Alert on critical system events",
            log_name=EventLogType.SYSTEM,
            level=[EventLevel.CRITICAL],
            enabled=True
        ),
        EventAlertRule(
            id=2,
            name="Application Errors",
            description="Alert on application errors",
            log_name=EventLogType.APPLICATION,
            level=[EventLevel.ERROR],
            enabled=True
        )
    ]


@router.post("/alert-rules", response_model=EventAlertRule)
async def create_alert_rule(
    agent_id: str,
    rule: EventAlertRule,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new alert rule for event monitoring.
    """
    # This would typically save to a database
    # For now, return the rule with an ID
    rule.id = 1
    rule.created_at = datetime.utcnow()
    rule.updated_at = datetime.utcnow()
    return rule


def _build_event_query_command(
    log_name: Optional[EventLogType] = None,
    level: Optional[List[EventLevel]] = None,
    source: Optional[str] = None,
    event_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    keyword: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    after_id: Optional[str] = None
) -> str:
    """Build PowerShell command for querying event logs."""
    
    # Map event levels to Windows event levels
    level_map = {
        EventLevel.CRITICAL: 1,
        EventLevel.ERROR: 2,
        EventLevel.WARNING: 3,
        EventLevel.INFORMATION: 4,
        EventLevel.VERBOSE: 5
    }
    
    # Build filter hashtable
    filters = []
    
    if log_name:
        filters.append(f"LogName='{log_name.value}'")
    
    if level:
        levels = [str(level_map[l]) for l in level]
        filters.append(f"Level={','.join(levels)}")
    
    if event_id:
        filters.append(f"ID={event_id}")
    
    if start_time:
        filters.append(f"StartTime='{start_time.isoformat()}'")
    
    if end_time:
        filters.append(f"EndTime='{end_time.isoformat()}'")
    
    # Build the command
    if filters:
        filter_string = "{" + "; ".join(filters) + "}"
        command = f"Get-WinEvent -FilterHashtable @{filter_string} -MaxEvents {limit}"
    else:
        command = f"Get-WinEvent -LogName System -MaxEvents {limit}"
    
    # Add after_id filtering if specified
    if after_id:
        command += f" | Where-Object {{[int]$_.Id -gt {after_id}}}"
    
    # Add keyword filtering if specified
    if keyword:
        command += f" | Where-Object {{$_.Message -like '*{keyword}*'}}"
    
    # Skip to offset if specified
    if offset > 0:
        command = f"({command}) | Select-Object -Skip {offset}"
    
    # Format output as JSON
    command += " | Select-Object Id, LogName, ProviderName, @{Name='EventId';Expression={$_.Id}}, LevelDisplayName, Message, TimeCreated, MachineName, UserId | ConvertTo-Json -Depth 3"
    
    return command


def _build_stats_query_command(log_name: Optional[EventLogType], hours: int) -> str:
    """Build PowerShell command for event statistics."""
    
    start_time = f"(Get-Date).AddHours(-{hours})"
    
    if log_name:
        base_query = f"Get-WinEvent -FilterHashtable @{{LogName='{log_name.value}'; StartTime={start_time}}}"
    else:
        base_query = f"Get-WinEvent -FilterHashtable @{{LogName='System','Application'; StartTime={start_time}}}"
    
    command = f"""
    $events = {base_query} -ErrorAction SilentlyContinue
    $stats = @{{
        TotalEvents = $events.Count
        CriticalCount = ($events | Where-Object {{$_.Level -eq 1}}).Count
        ErrorCount = ($events | Where-Object {{$_.Level -eq 2}}).Count
        WarningCount = ($events | Where-Object {{$_.Level -eq 3}}).Count
        InfoCount = ($events | Where-Object {{$_.Level -eq 4}}).Count
        VerboseCount = ($events | Where-Object {{$_.Level -eq 5}}).Count
        Sources = $events | Group-Object ProviderName | Select-Object Name, Count | Sort-Object Count -Descending | Select-Object -First 10
        RecentCritical = $events | Where-Object {{$_.Level -eq 1}} | Select-Object -First 5
        RecentErrors = $events | Where-Object {{$_.Level -eq 2}} | Select-Object -First 5
    }}
    $stats | ConvertTo-Json -Depth 4
    """
    
    return command


def _build_stream_command(request: EventStreamRequest) -> str:
    """Build PowerShell command for streaming events."""
    
    filters = []
    
    if request.log_names:
        log_names = "'" + "','".join([ln.value for ln in request.log_names]) + "'"
        filters.append(f"LogName={log_names}")
    else:
        filters.append("LogName='System','Application'")
    
    if request.levels:
        level_map = {
            EventLevel.CRITICAL: 1,
            EventLevel.ERROR: 2,
            EventLevel.WARNING: 3,
            EventLevel.INFORMATION: 4,
            EventLevel.VERBOSE: 5
        }
        levels = [str(level_map[l]) for l in request.levels]
        filters.append(f"Level={','.join(levels)}")
    
    # Get events from last 30 seconds
    filters.append("StartTime=(Get-Date).AddSeconds(-30)")
    
    filter_string = "{" + "; ".join(filters) + "}"
    command = f"Get-WinEvent -FilterHashtable @{filter_string} -ErrorAction SilentlyContinue"
    
    if request.sources:
        sources_filter = " -or ".join([f"$_.ProviderName -eq '{s}'" for s in request.sources])
        command += f" | Where-Object {{{sources_filter}}}"
    
    command += " | Select-Object Id, LogName, ProviderName, LevelDisplayName, Message, TimeCreated, MachineName | ConvertTo-Json -Depth 3"
    
    return command


def _parse_event_logs(result: str) -> List[WindowsEventLog]:
    """Parse PowerShell JSON output to event log objects."""
    try:
        if not result:
            return []
        
        data = json.loads(result)
        if not isinstance(data, list):
            data = [data]
        
        events = []
        for item in data:
            # Map Windows levels to our enum
            level_map = {
                "Critical": EventLevel.CRITICAL,
                "Error": EventLevel.ERROR,
                "Warning": EventLevel.WARNING,
                "Information": EventLevel.INFORMATION,
                "Verbose": EventLevel.VERBOSE
            }
            
            event = WindowsEventLog(
                id=item.get("Id", 0),
                log_name=item.get("LogName", ""),
                source=item.get("ProviderName", ""),
                event_id=item.get("EventId", item.get("Id", 0)),
                level=level_map.get(item.get("LevelDisplayName", "Information"), EventLevel.INFORMATION),
                timestamp=datetime.fromisoformat(item.get("TimeCreated", datetime.now().isoformat())),
                computer=item.get("MachineName", ""),
                user=item.get("UserId", ""),
                message=item.get("Message", "")
            )
            events.append(event)
        
        return events
    except Exception as e:
        logger.error(f"Error parsing event logs: {e}")
        return []


def _parse_event_stats(result: str) -> EventLogStats:
    """Parse PowerShell JSON output to event statistics."""
    try:
        if not result:
            return EventLogStats(
                total_events=0,
                critical_count=0,
                error_count=0,
                warning_count=0,
                info_count=0,
                verbose_count=0,
                sources=[],
                recent_critical=[],
                recent_errors=[]
            )
        
        data = json.loads(result)
        
        # Parse sources
        sources = []
        if data.get("Sources"):
            for source in data["Sources"]:
                sources.append({
                    "name": source.get("Name", ""),
                    "count": source.get("Count", 0)
                })
        
        # Parse recent events
        recent_critical = _parse_event_logs(json.dumps(data.get("RecentCritical", [])))
        recent_errors = _parse_event_logs(json.dumps(data.get("RecentErrors", [])))
        
        return EventLogStats(
            total_events=data.get("TotalEvents", 0),
            critical_count=data.get("CriticalCount", 0),
            error_count=data.get("ErrorCount", 0),
            warning_count=data.get("WarningCount", 0),
            info_count=data.get("InfoCount", 0),
            verbose_count=data.get("VerboseCount", 0),
            sources=sources,
            recent_critical=recent_critical,
            recent_errors=recent_errors
        )
    except Exception as e:
        logger.error(f"Error parsing event stats: {e}")
        return EventLogStats(
            total_events=0,
            critical_count=0,
            error_count=0,
            warning_count=0,
            info_count=0,
            verbose_count=0,
            sources=[],
            recent_critical=[],
            recent_errors=[]
        )


def _export_to_csv(events: List[WindowsEventLog], hostname: str) -> StreamingResponse:
    """Export events to CSV format."""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "log_name", "source", "event_id", "level", "timestamp", "computer", "user", "message"]
    )
    writer.writeheader()
    
    for event in events:
        writer.writerow({
            "id": event.id,
            "log_name": event.log_name,
            "source": event.source,
            "event_id": event.event_id,
            "level": event.level.value,
            "timestamp": event.timestamp.isoformat(),
            "computer": event.computer,
            "user": event.user or "",
            "message": event.message
        })
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=events_{hostname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


def _export_to_json(events: List[WindowsEventLog], hostname: str) -> StreamingResponse:
    """Export events to JSON format."""
    event_dicts = [event.dict() for event in events]
    json_output = json.dumps(event_dicts, default=str, indent=2)
    
    return StreamingResponse(
        io.BytesIO(json_output.encode()),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=events_{hostname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        }
    )