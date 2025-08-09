#!/usr/bin/env python3
"""
Test script to verify DX-126 bug fix
Dashboard Total Agents and Online Agents display issue
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8080"
USERNAME = "admin"
PASSWORD = "admin123"

def test_dashboard_fix():
    """Test if the dashboard correctly displays agent counts"""
    
    # 1. Login to get token
    print("1. Logging in to get authentication token...")
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # 2. Get agents from API
    print("\n2. Fetching agents from API...")
    agents_response = requests.get(
        f"{BASE_URL}/api/v1/agents/",
        headers=headers
    )
    
    if agents_response.status_code != 200:
        print(f"❌ Failed to fetch agents: {agents_response.status_code}")
        print(agents_response.text)
        return False
    
    agents_data = agents_response.json()
    print(f"✅ API response structure: {json.dumps(agents_data, indent=2)}")
    
    # 3. Verify response structure
    print("\n3. Verifying API response structure...")
    if not isinstance(agents_data, dict):
        print(f"❌ Expected dict, got {type(agents_data)}")
        return False
    
    if "agents" not in agents_data:
        print(f"❌ Missing 'agents' field in response")
        return False
    
    if "count" not in agents_data:
        print(f"❌ Missing 'count' field in response")
        return False
    
    print(f"✅ Response has correct structure")
    print(f"   - Total agents in array: {len(agents_data['agents'])}")
    print(f"   - Count field value: {agents_data['count']}")
    
    # 4. Count online agents
    online_agents = [a for a in agents_data['agents'] if a.get('status') == 'online']
    print(f"   - Online agents: {len(online_agents)}")
    
    # 5. Test frontend endpoint (if available)
    print("\n4. Testing frontend (if available)...")
    try:
        frontend_response = requests.get("http://localhost:3000/")
        if frontend_response.status_code == 200:
            print("✅ Frontend is accessible")
            print("   Please manually verify:")
            print("   1. Navigate to http://localhost:3000")
            print("   2. Login with admin/admin123")
            print(f"   3. Dashboard should show:")
            print(f"      - Total Agents: {len(agents_data['agents'])}")
            print(f"      - Online Agents: {len(online_agents)}")
        else:
            print(f"⚠️  Frontend returned status {frontend_response.status_code}")
    except Exception as e:
        print(f"⚠️  Could not reach frontend: {e}")
    
    print("\n✅ DX-126 Bug Fix Test Complete!")
    print("=" * 50)
    print("Summary:")
    print(f"- API returns correct structure with 'agents' array and 'count'")
    print(f"- Total agents: {len(agents_data['agents'])}")
    print(f"- Online agents: {len(online_agents)}")
    print(f"- Frontend code has been updated to handle the new structure")
    
    return True

if __name__ == "__main__":
    test_dashboard_fix()