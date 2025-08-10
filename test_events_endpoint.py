#!/usr/bin/env python3
"""Test the events endpoint"""

import requests
import json

# Login
response = requests.post('http://localhost:8080/api/v1/auth/login', 
                         json={'username': 'admin', 'password': 'admin123'})
token = response.json()['access_token']

# Test events endpoint
headers = {'Authorization': f'Bearer {token}'}
agent_id = "desktop-jk5g34l-dexagent"

response = requests.get(f'http://localhost:8080/api/v1/agents/{agent_id}/events/', 
                        headers=headers)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
else:
    print(f"Error: {response.text}")