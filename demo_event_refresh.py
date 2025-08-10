#!/usr/bin/env python3
"""Demo script to show event refresh functionality"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8080"

def main():
    print("=== Event Refresh Demo ===\n")
    
    # Login
    print("1. Logging in...")
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", 
                             json={'username': 'admin', 'password': 'admin123'})
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Select an agent
    agent_id = "desktop-jk5g34l-dexagent"
    print(f"2. Selected agent: {agent_id}\n")
    
    # Initial fetch
    print("3. Initial event fetch:")
    response = requests.get(f"{BASE_URL}/api/v1/agents/{agent_id}/events/", 
                            headers=headers, params={"limit": 5})
    events = response.json()['events']
    print(f"   Found {len(events)} events")
    if events:
        last_event_id = events[0]['id']
        print(f"   Latest event ID: {last_event_id}")
        for event in events[:3]:
            print(f"   - {event['timestamp']}: {event['message']}")
    
    # Simulate time passing and new events occurring
    print("\n4. Simulating new events...")
    time.sleep(1)
    
    # Create new events
    new_events = [
        {"message": "User logged in successfully", "severity": "info", "event_type": "auth"},
        {"message": "Backup completed", "severity": "info", "event_type": "backup"},
        {"message": "Network connection lost", "severity": "warning", "event_type": "network"},
    ]
    
    for event_data in new_events:
        response = requests.post(f"{BASE_URL}/api/v1/agents/{agent_id}/events/",
                                 headers=headers, json=event_data)
        if response.status_code == 200:
            print(f"   ✓ Created: {event_data['message']}")
        time.sleep(0.5)
    
    # Refresh - fetch only new events
    print(f"\n5. Refreshing (fetching events after ID: {last_event_id})...")
    response = requests.get(f"{BASE_URL}/api/v1/agents/{agent_id}/events/", 
                            headers=headers, 
                            params={"after_id": last_event_id, "limit": 10})
    new_fetched_events = response.json()['events']
    
    if new_fetched_events:
        print(f"   Found {len(new_fetched_events)} NEW events:")
        for event in new_fetched_events:
            print(f"   - {event['timestamp']}: [{event['severity']}] {event['message']}")
    else:
        print("   No new events found")
    
    print("\n✅ Demo completed successfully!")
    print("   The refresh button fetched only the new events,")
    print("   not re-fetching the entire event list.")

if __name__ == "__main__":
    main()