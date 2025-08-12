"""Simple events API for testing"""
from fastapi import APIRouter, Depends, Query, Response, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import csv
import io
from collections import Counter
from ...core.auth import verify_token

router = APIRouter(prefix="/agents/{agent_id}/events")

# In-memory storage for events (in production, this would be in a database)
events_storage: Dict[str, List[Dict[str, Any]]] = {}
# In-memory storage for alert rules
alert_rules_storage: Dict[str, List[Dict[str, Any]]] = {}

@router.get("/")
async def get_events(
    agent_id: str,
    after_id: Optional[str] = Query(None, description="Get events after this event ID"),
    limit: int = Query(100, le=1000),
    severity: Optional[str] = Query(None),
    token: str = Depends(verify_token)
):
    """Get events for an agent, optionally filtering by after_id"""
    
    # Get or create events list for this agent
    if agent_id not in events_storage:
        events_storage[agent_id] = []
    
    agent_events = events_storage[agent_id]
    
    # Filter by after_id if provided
    if after_id:
        # Find the index of the after_id event
        after_index = None
        for i, event in enumerate(agent_events):
            if event['id'] == after_id:
                after_index = i
                break
        
        if after_index is not None:
            # Return only events before this index (newer events)
            agent_events = agent_events[:after_index]
    
    # Filter by severity if provided
    if severity and severity != 'all':
        agent_events = [e for e in agent_events if e.get('severity') == severity]
    
    # Limit results
    agent_events = agent_events[:limit]
    
    return {
        "events": agent_events,
        "total": len(agent_events),
        "page": 0,
        "page_size": limit,
        "has_more": False
    }

@router.post("/")
async def create_event(
    agent_id: str,
    event_data: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Create a new event for an agent"""
    
    # Get or create events list for this agent
    if agent_id not in events_storage:
        events_storage[agent_id] = []
    
    # Create event with unique ID and timestamp
    event = {
        "id": str(uuid.uuid4()),
        "agent_id": agent_id,
        "timestamp": datetime.utcnow().isoformat(),
        **event_data
    }
    
    # Add default fields if not provided
    if 'severity' not in event:
        event['severity'] = 'info'
    if 'event_type' not in event:
        event['event_type'] = 'system'
    if 'message' not in event:
        event['message'] = 'Event created'
    if 'source' not in event:
        event['source'] = 'system'
    
    # Add to storage (at the beginning for newest first)
    events_storage[agent_id].insert(0, event)
    
    # Keep only last 1000 events per agent
    if len(events_storage[agent_id]) > 1000:
        events_storage[agent_id] = events_storage[agent_id][:1000]
    
    return event

# Add some sample events for testing
def initialize_sample_events():
    """Initialize some sample events for testing"""
    sample_agent_id = "desktop-jk5g34l-dexagent"
    
    if sample_agent_id not in events_storage:
        events_storage[sample_agent_id] = []
    
    # Add sample events if none exist
    if not events_storage[sample_agent_id]:
        sample_events = [
            {
                "id": "event-1",
                "agent_id": sample_agent_id,
                "timestamp": "2025-08-09T18:00:00",
                "severity": "info",
                "event_type": "system",
                "message": "System started successfully",
                "source": "system"
            },
            {
                "id": "event-2",
                "agent_id": sample_agent_id,
                "timestamp": "2025-08-09T18:01:00",
                "severity": "warning",
                "event_type": "security",
                "message": "Failed login attempt detected",
                "source": "security"
            },
            {
                "id": "event-3",
                "agent_id": sample_agent_id,
                "timestamp": "2025-08-09T18:02:00",
                "severity": "error",
                "event_type": "application",
                "message": "Application crash detected",
                "source": "app-monitor"
            },
            {
                "id": "event-4",
                "agent_id": sample_agent_id,
                "timestamp": "2025-08-09T18:03:00",
                "severity": "info",
                "event_type": "system",
                "message": "Disk cleanup completed",
                "source": "maintenance"
            },
            {
                "id": "event-5",
                "agent_id": sample_agent_id,
                "timestamp": "2025-08-09T18:04:00",
                "severity": "critical",
                "event_type": "hardware",
                "message": "High CPU temperature detected",
                "source": "hardware-monitor"
            }
        ]
        events_storage[sample_agent_id] = sample_events

# Initialize sample events on module load
initialize_sample_events()

@router.post("/export")
async def export_events(
    agent_id: str,
    format: str = "csv",
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    token: str = Depends(verify_token)
):
    """Export events as CSV"""
    
    # Get events for this agent
    agent_events = events_storage.get(agent_id, [])
    
    # Filter by severity if provided
    if severity and severity != 'all':
        agent_events = [e for e in agent_events if e.get('severity') == severity]
    
    # Filter by event_type if provided
    if event_type and event_type != 'all':
        agent_events = [e for e in agent_events if e.get('event_type') == event_type]
    
    # Create CSV
    output = io.StringIO()
    fieldnames = ['timestamp', 'event_type', 'severity', 'message', 'source']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    for event in agent_events:
        writer.writerow({
            'timestamp': event.get('timestamp', ''),
            'event_type': event.get('event_type', ''),
            'severity': event.get('severity', ''),
            'message': event.get('message', ''),
            'source': event.get('source', '')
        })
    
    csv_content = output.getvalue()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=events_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )

@router.get("/stats")
async def get_event_stats(
    agent_id: str,
    time_range: str = Query("24h", description="Time range for stats (24h, 7d, 30d)"),
    token: str = Depends(verify_token)
):
    """Get event statistics"""
    
    # Get events for this agent
    agent_events = events_storage.get(agent_id, [])
    
    # Calculate time threshold
    now = datetime.utcnow()
    if time_range == "24h":
        threshold = now - timedelta(hours=24)
    elif time_range == "7d":
        threshold = now - timedelta(days=7)
    elif time_range == "30d":
        threshold = now - timedelta(days=30)
    else:
        threshold = now - timedelta(hours=24)
    
    # Filter events by time range
    recent_events = []
    for event in agent_events:
        try:
            event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            if event_time >= threshold:
                recent_events.append(event)
        except:
            pass
    
    # Calculate statistics
    severity_counts = Counter(e.get('severity', 'unknown') for e in recent_events)
    type_counts = Counter(e.get('event_type', 'unknown') for e in recent_events)
    
    # Calculate trend (events per day for last 7 days)
    trend = []
    for i in range(7):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        day_count = sum(1 for e in recent_events
                       if 'timestamp' in e
                       and day_start <= datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')) < day_end)
        trend.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'count': day_count
        })
    trend.reverse()
    
    # Count critical and warning events in last 24h
    last_24h = now - timedelta(hours=24)
    critical_24h = sum(1 for e in recent_events
                      if e.get('severity') == 'critical'
                      and 'timestamp' in e
                      and datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')) >= last_24h)
    warning_24h = sum(1 for e in recent_events
                     if e.get('severity') == 'warning'
                     and 'timestamp' in e
                     and datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')) >= last_24h)
    
    return {
        'total_events': len(recent_events),
        'events_by_severity': dict(severity_counts),
        'events_by_type': dict(type_counts),
        'recent_trend': trend,
        'critical_events_24h': critical_24h,
        'warning_events_24h': warning_24h
    }

@router.get("/alert-rules")
async def get_alert_rules(
    agent_id: str,
    token: str = Depends(verify_token)
):
    """Get alert rules for an agent"""
    
    # Get or create alert rules list for this agent
    if agent_id not in alert_rules_storage:
        alert_rules_storage[agent_id] = []
    
    return alert_rules_storage[agent_id]

@router.post("/alert-rules")
async def create_alert_rule(
    agent_id: str,
    rule_data: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Create a new alert rule"""
    
    # Get or create alert rules list for this agent
    if agent_id not in alert_rules_storage:
        alert_rules_storage[agent_id] = []
    
    # Create rule with unique ID
    rule = {
        "id": str(uuid.uuid4()),
        "agent_id": agent_id,
        "created_at": datetime.utcnow().isoformat(),
        **rule_data
    }
    
    # Add default fields if not provided
    if 'enabled' not in rule:
        rule['enabled'] = True
    if 'notification_channels' not in rule:
        rule['notification_channels'] = []
    
    # Add to storage
    alert_rules_storage[agent_id].append(rule)
    
    return rule

@router.put("/alert-rules/{rule_id}")
async def update_alert_rule(
    agent_id: str,
    rule_id: str,
    rule_data: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Update an existing alert rule"""
    
    # Get alert rules for this agent
    if agent_id not in alert_rules_storage:
        raise HTTPException(status_code=404, detail="No alert rules found for this agent")
    
    # Find and update the rule
    for i, rule in enumerate(alert_rules_storage[agent_id]):
        if rule['id'] == rule_id:
            # Update the rule
            updated_rule = {
                **rule,
                **rule_data,
                "id": rule_id,  # Preserve ID
                "agent_id": agent_id,  # Preserve agent ID
                "updated_at": datetime.utcnow().isoformat()
            }
            alert_rules_storage[agent_id][i] = updated_rule
            return updated_rule
    
    raise HTTPException(status_code=404, detail="Alert rule not found")

@router.delete("/alert-rules/{rule_id}")
async def delete_alert_rule(
    agent_id: str,
    rule_id: str,
    token: str = Depends(verify_token)
):
    """Delete an alert rule"""
    
    # Get alert rules for this agent
    if agent_id not in alert_rules_storage:
        raise HTTPException(status_code=404, detail="No alert rules found for this agent")
    
    # Find and delete the rule
    for i, rule in enumerate(alert_rules_storage[agent_id]):
        if rule['id'] == rule_id:
            alert_rules_storage[agent_id].pop(i)
            return {"message": "Alert rule deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Alert rule not found")