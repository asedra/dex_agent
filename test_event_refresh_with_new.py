#!/usr/bin/env python3
"""Test event refresh with new events being created"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8080"
USERNAME = "admin"
PASSWORD = "admin123"

def login():
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        headers={"Content-Type": "application/json"},
        json={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    else:
        print(f"Login failed: {response.status_code}")
        return None

def create_event(token, agent_id, message, severity="info"):
    """Create a new event for an agent"""
    headers = {"Authorization": f"Bearer {token}"}
    event_data = {
        "message": message,
        "severity": severity,
        "event_type": "test",
        "source": "test-script"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/agents/{agent_id}/events/",
        headers=headers,
        json=event_data
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to create event: {response.status_code}")
        return None

def test_event_refresh_with_new(token):
    """Test the event refresh functionality with new events"""
    headers = {"Authorization": f"Bearer {token}"}
    agent_id = "desktop-jk5g34l-dexagent"
    
    print(f"Testing with agent ID: {agent_id}")
    
    # First request - get initial events
    print("\n1. Fetching initial events...")
    response = requests.get(
        f"{BASE_URL}/api/v1/agents/{agent_id}/events/",
        headers=headers,
        params={"limit": 10}
    )
    
    if response.status_code == 200:
        initial_events = response.json()
        print(f"   Got {len(initial_events.get('events', []))} initial events")
        
        if initial_events.get('events'):
            # Get the latest event ID
            latest_event_id = initial_events['events'][0]['id']
            print(f"   Latest event ID: {latest_event_id}")
            
            # Create some new events
            print("\n2. Creating new events...")
            for i in range(3):
                event = create_event(
                    token, 
                    agent_id, 
                    f"New test event {i+1} at {datetime.now().isoformat()}",
                    severity=["info", "warning", "error"][i % 3]
                )
                if event:
                    print(f"   Created event: {event['id']} - {event['message'][:50]}...")
                time.sleep(0.5)
            
            # Third request - get events after the latest ID
            print(f"\n3. Fetching events after ID {latest_event_id}...")
            response = requests.get(
                f"{BASE_URL}/api/v1/agents/{agent_id}/events/",
                headers=headers,
                params={
                    "limit": 10,
                    "after_id": latest_event_id
                }
            )
            
            if response.status_code == 200:
                new_events = response.json()
                print(f"   Got {len(new_events.get('events', []))} new events")
                
                if new_events.get('events'):
                    print("   New events found:")
                    for event in new_events['events']:
                        print(f"     - ID: {event['id']}, Severity: {event['severity']}, Message: {event['message'][:40]}...")
                else:
                    print("   No new events found (unexpected)")
            else:
                print(f"   Error fetching new events: {response.status_code}")
        else:
            print("   No events found for this agent")
    else:
        print(f"   Error fetching initial events: {response.status_code}")

if __name__ == "__main__":
    print("Testing Event Refresh with New Events")
    print("=" * 40)
    
    # Login
    print("Logging in...")
    token = login()
    
    if token:
        print("Login successful!")
        test_event_refresh_with_new(token)
    else:
        print("Failed to login")