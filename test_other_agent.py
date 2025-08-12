#!/usr/bin/env python3
import requests

# Login
login_resp = requests.post('http://localhost:8080/api/v1/auth/login', 
                           json={'username': 'admin', 'password': 'admin123'})
token = login_resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test file preview on different agent
agent_id = "agent_20250811_201747_175"
preview_resp = requests.get(f'http://localhost:8080/api/v1/files/agents/{agent_id}/files/preview',
                            params={'file_path': 'C:\\Windows\\win.ini'},
                            headers=headers)
print(f'Preview response for {agent_id}: {preview_resp.status_code}')
if preview_resp.status_code != 200:
    print(f'Error: {preview_resp.text}')
else:
    print('Success!')