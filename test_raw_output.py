#!/usr/bin/env python3
import requests
import json

# Login
login_response = requests.post('http://localhost:8080/api/v1/auth/login', 
    json={'username': 'admin', 'password': 'admin123'})
token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Get connected agents
agents_response = requests.get('http://localhost:8080/api/v1/agents', headers=headers)
agents = agents_response.json()

print(f'Connected agents: {len(agents)}')

agents_list = agents.get('agents', [])
if agents_list and len(agents_list) > 0:
    agent = agents_list[0]
    agent_id = agent.get('id') or agent.get('agent_id')
    print(f'Using agent: {agent_id}')
    
    # Execute the Get-ComputerInfo command directly on agent
    command = 'Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory, CsProcessors | ConvertTo-Json'
    
    # Execute command on agent
    exec_response = requests.post(
        f'http://localhost:8080/api/v1/commands/agent/{agent_id}/execute',
        headers=headers,
        json={
            'command': command,
            'timeout': 30
        }
    )
    
    print(f'Execution response: {exec_response.status_code}')
    
    if exec_response.status_code == 200:
        result = exec_response.json()
        print(f'Success: {result.get("success")}')
        
        # Get the raw output
        output = result.get('output', '')
        print(f'Output length: {len(output)}')
        print(f'Output first 200 chars: {repr(output[:200])}')
        
        # Check for BOM
        if output.startswith('\ufeff'):
            print('WARNING: Output starts with BOM character!')
            output = output[1:]  # Remove BOM
        
        # Try to parse as JSON
        try:
            parsed = json.loads(output)
            print('SUCCESS: Valid JSON parsed!')
            print(f'JSON keys: {list(parsed.keys())}')
        except json.JSONDecodeError as e:
            print(f'ERROR: JSON parsing failed: {e}')
            print(f'Error at position: {e.pos}')
            
            # Show the problematic part
            if e.pos and e.pos < len(output):
                start = max(0, e.pos - 20)
                end = min(len(output), e.pos + 20)
                print(f'Around error position: {repr(output[start:end])}')
                
            # Show raw bytes
            print(f'\nRaw bytes at start: {output[:50].encode("utf-8")}')