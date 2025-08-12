#!/usr/bin/env python3
import requests
import json

# Login
login_resp = requests.post('http://localhost:8080/api/v1/auth/login', 
                           json={'username': 'admin', 'password': 'admin123'})
token = login_resp.json()['access_token']
print(f'Token obtained: {token[:20]}...')

# Test file preview
headers = {'Authorization': f'Bearer {token}'}
preview_resp = requests.get('http://localhost:8080/api/v1/files/agents/desktop-jk5g34l-dexagent/files/preview',
                            params={'file_path': 'C:\\Windows\\win.ini'},
                            headers=headers)
print(f'Preview response: {preview_resp.status_code}')
if preview_resp.status_code != 200:
    print(f'Error: {preview_resp.text}')
else:
    print('Success! Preview data received')
    print(json.dumps(preview_resp.json(), indent=2))

# Test file upload
print('\nTesting file upload...')
files = {'file': ('test.txt', b'Test content for upload', 'text/plain')}
params = {'target_path': 'C:\\temp\\dexagents_test'}
upload_resp = requests.post('http://localhost:8080/api/v1/files/agents/desktop-jk5g34l-dexagent/files/upload',
                            files=files,
                            params=params,
                            headers=headers)
print(f'Upload response: {upload_resp.status_code}')
if upload_resp.status_code != 200:
    print(f'Error: {upload_resp.text}')
else:
    print('Success! File uploaded')
    print(json.dumps(upload_resp.json(), indent=2))