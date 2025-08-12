#!/usr/bin/env python3
import requests
import json

# Login
login_resp = requests.post('http://localhost:8080/api/v1/auth/login', 
                          json={'username': 'admin', 'password': 'admin123'})
token = login_resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("Testing Software API Endpoints")
print("=" * 40)

# Test inventory endpoint  
print("\n1. Testing /software/inventory...")
inv_resp = requests.get('http://localhost:8080/api/v1/software/inventory', headers=headers)
print(f"Status: {inv_resp.status_code}")
if inv_resp.status_code == 200:
    data = inv_resp.json()
    print(f"Success! Found {len(data)} software items")
    if data and len(data) > 0:
        print(f"Sample: {data[0]['name']} v{data[0].get('version', 'N/A')}")
else:
    print(f"Error: {inv_resp.text}")

# Test stats endpoint
print("\n2. Testing /software/stats...")
stats_resp = requests.get('http://localhost:8080/api/v1/software/stats', headers=headers)
print(f"Status: {stats_resp.status_code}")
if stats_resp.status_code == 200:
    stats = stats_resp.json()
    print(f"Success! Stats: {json.dumps(stats, indent=2)}")
else:
    print(f"Error: {stats_resp.text}")

# Test mock data creation
print("\n3. Testing /software/mock-data...")
agent_id = 'desktop-jk5g34l-dexagent'
mock_resp = requests.post(f'http://localhost:8080/api/v1/software/mock-data?agent_id={agent_id}', 
                          headers=headers)
print(f"Status: {mock_resp.status_code}")
if mock_resp.status_code == 200:
    print(f"Success! {mock_resp.json()}")
else:
    print(f"Error: {mock_resp.text}")

print("\n" + "=" * 40)
print("Testing complete!")