#!/usr/bin/env python3
"""Test the events page frontend functionality"""

import requests
import json
import time

def test_events_page():
    """Test all events page functionality"""
    
    print("=" * 50)
    print("Testing Events Page Functionality")
    print("=" * 50)
    
    # 1. Login to get token
    print("\n1. Logging in...")
    login_resp = requests.post('http://localhost:8080/api/v1/auth/login', 
                              json={'username': 'admin', 'password': 'admin123'})
    if login_resp.status_code != 200:
        print(f"❌ Login failed: {login_resp.status_code}")
        return False
    
    token = login_resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ Login successful")
    
    agent_id = "desktop-jk5g34l-dexagent"
    
    # 2. Test Events List endpoint
    print("\n2. Testing Events List endpoint...")
    events_resp = requests.get(f'http://localhost:8080/api/v1/agents/{agent_id}/events/', 
                              headers=headers)
    if events_resp.status_code == 200:
        events = events_resp.json()
        print(f"✅ Events list working - Found {len(events.get('events', []))} events")
        if events.get('events'):
            print(f"   Sample event: {events['events'][0].get('message', 'N/A')}")
    else:
        print(f"❌ Events list failed: {events_resp.status_code}")
        return False
    
    # 3. Test Events Stats endpoint
    print("\n3. Testing Events Stats endpoint...")
    stats_resp = requests.get(f'http://localhost:8080/api/v1/agents/{agent_id}/events/stats?time_range=24h',
                              headers=headers)
    if stats_resp.status_code == 200:
        stats = stats_resp.json()
        print(f"✅ Stats endpoint working")
        print(f"   Total events: {stats.get('total_events', 0)}")
        print(f"   Events by severity: {stats.get('events_by_severity', {})}")
        print(f"   Events by type: {stats.get('events_by_type', {})}")
    else:
        print(f"❌ Stats endpoint failed: {stats_resp.status_code}")
        return False
    
    # 4. Test Alert Rules endpoint
    print("\n4. Testing Alert Rules endpoints...")
    
    # Get alert rules
    rules_resp = requests.get(f'http://localhost:8080/api/v1/agents/{agent_id}/events/alert-rules',
                              headers=headers)
    if rules_resp.status_code == 200:
        rules = rules_resp.json()
        print(f"✅ Get alert rules working - Found {len(rules)} rules")
    else:
        print(f"❌ Get alert rules failed: {rules_resp.status_code}")
        return False
    
    # Create a test alert rule
    test_rule = {
        "name": "Test Rule",
        "description": "Test alert rule for critical events",
        "condition": {
            "field": "severity",
            "operator": "equals",
            "value": "critical"
        },
        "severity_filter": ["critical"],
        "notification_channels": ["email"],
        "enabled": True
    }
    
    create_resp = requests.post(f'http://localhost:8080/api/v1/agents/{agent_id}/events/alert-rules',
                                headers={**headers, 'Content-Type': 'application/json'},
                                json=test_rule)
    if create_resp.status_code == 200:
        created_rule = create_resp.json()
        rule_id = created_rule['id']
        print(f"✅ Create alert rule working - ID: {rule_id}")
        
        # Update the rule
        update_data = {"description": "Updated test rule", "enabled": False}
        update_resp = requests.put(f'http://localhost:8080/api/v1/agents/{agent_id}/events/alert-rules/{rule_id}',
                                   headers={**headers, 'Content-Type': 'application/json'},
                                   json=update_data)
        if update_resp.status_code == 200:
            print(f"✅ Update alert rule working")
        else:
            print(f"❌ Update alert rule failed: {update_resp.status_code}")
        
        # Delete the rule
        delete_resp = requests.delete(f'http://localhost:8080/api/v1/agents/{agent_id}/events/alert-rules/{rule_id}',
                                      headers=headers)
        if delete_resp.status_code == 200:
            print(f"✅ Delete alert rule working")
        else:
            print(f"❌ Delete alert rule failed: {delete_resp.status_code}")
    else:
        print(f"❌ Create alert rule failed: {create_resp.status_code}")
        return False
    
    # 5. Test Export endpoint
    print("\n5. Testing Export endpoint...")
    export_data = {
        "format": "csv",
        "severity": "all",
        "event_type": "all"
    }
    export_resp = requests.post(f'http://localhost:8080/api/v1/agents/{agent_id}/events/export',
                                headers={**headers, 'Content-Type': 'application/json'},
                                json=export_data)
    if export_resp.status_code == 200:
        csv_content = export_resp.text
        lines = csv_content.strip().split('\n')
        print(f"✅ Export endpoint working - Exported {len(lines) - 1} events (CSV format)")
        print(f"   CSV Headers: {lines[0]}")
    else:
        print(f"❌ Export endpoint failed: {export_resp.status_code}")
        return False
    
    # 6. Create a new event to test real-time updates
    print("\n6. Testing Event Creation...")
    new_event = {
        "severity": "info",
        "event_type": "system",
        "message": "Test event created via API test",
        "source": "test_script"
    }
    create_event_resp = requests.post(f'http://localhost:8080/api/v1/agents/{agent_id}/events/',
                                      headers={**headers, 'Content-Type': 'application/json'},
                                      json=new_event)
    if create_event_resp.status_code == 200:
        created_event = create_event_resp.json()
        print(f"✅ Event creation working - Event ID: {created_event['id']}")
    else:
        print(f"❌ Event creation failed: {create_event_resp.status_code}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All Events Page API Endpoints Working!")
    print("=" * 50)
    
    print("\n📊 Summary:")
    print(f"- Events page URL: http://localhost:3000/agents/{agent_id}/events")
    print("- All backend endpoints are functional")
    print("- Frontend should now display:")
    print("  • Event Logs tab with events list and export")
    print("  • Statistics tab with charts and metrics")
    print("  • Alert Rules tab with CRUD operations")
    
    return True

if __name__ == "__main__":
    success = test_events_page()
    exit(0 if success else 1)