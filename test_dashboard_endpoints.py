#!/usr/bin/env python3
"""Test script to verify dashboard endpoints are working correctly"""

import requests
import json
import sys

# Base URL
BASE_URL = "http://localhost:8080/api/v1"

# Login credentials
credentials = {
    "username": "admin",
    "password": "admin123"
}

def get_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/auth/login", json=credentials)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Failed to login: {response.status_code}")
        return None

def test_dashboard_endpoints():
    """Test all dashboard endpoints"""
    token = get_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test endpoints
    endpoints = [
        "/dashboard/stats",
        "/dashboard/alerts",
        "/dashboard/recent-activity?limit=10",
        "/dashboard/metrics/trend?hours=24",
        "/dashboard/top-commands?limit=5&days=7"
    ]
    
    all_passed = True
    print("\n=== Testing Dashboard Endpoints ===\n")
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Status: {response.status_code} - PASSED")
                # Print first 100 chars of response
                data = json.dumps(response.json(), indent=2)[:100] + "..."
                print(f"   Response preview: {data}\n")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code} - FAILED")
                print(f"   Error: {response.text[:200]}\n")
                all_passed = False
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)} - FAILED\n")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    success = test_dashboard_endpoints()
    
    if success:
        print("\n✅ All dashboard endpoints are working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some dashboard endpoints failed!")
        sys.exit(1)