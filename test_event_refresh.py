#!/usr/bin/env python3
"""Test script for event refresh functionality"""

import requests
import json
import time

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

def get_agents(token):
    """Get list of agents"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/agents", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def test_event_refresh(token):
    """Test the event refresh functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get agents
    agents = get_agents(token)
    if isinstance(agents, dict) and 'agents' in agents:
        agents = agents['agents']
    
    print(f"Found {len(agents)} agents")
    
    if not agents:
        print("No agents found. Creating mock agent for testing...")
        # You would need to create an agent here if needed
        return
    
    agent_id = agents[0]["id"]
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
            
            # Second request - get events after the latest ID
            print("\n2. Fetching events after ID {latest_event_id}...")
            time.sleep(2)  # Wait a bit
            
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
                    for event in new_events['events'][:3]:  # Show first 3
                        print(f"     - ID: {event['id']}, Type: {event.get('event_type', 'N/A')}")
                else:
                    print("   No new events (this is expected if no new events occurred)")
            else:
                print(f"   Error fetching new events: {response.status_code}")
                print(f"   Response: {response.text}")
        else:
            print("   No events found for this agent")
    else:
        print(f"   Error fetching initial events: {response.status_code}")
        print(f"   Response: {response.text}")

if __name__ == "__main__":
    print("Testing Event Refresh Functionality")
    print("=" * 40)
    
    # Login
    print("Logging in...")
    token = login()
    
    if token:
        print("Login successful!")
        test_event_refresh(token)
    else:
        print("Failed to login")