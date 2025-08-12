#!/usr/bin/env python3
import requests
import json
import time

# Login with JSON format
login_response = requests.post('http://localhost:8080/api/v1/auth/login', 
    json={'username': 'admin', 'password': 'admin123'},
    headers={'Content-Type': 'application/json'})

if login_response.status_code != 200:
    print(f'Login failed: {login_response.status_code} - {login_response.text}')
    exit(1)

token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Get saved commands and find 'Get System Information'
commands_response = requests.get('http://localhost:8080/api/v1/commands/saved', headers=headers)
commands = commands_response.json()

# Find the 'Get System Information' command
sys_info_command = None
for cmd in commands:
    if cmd['name'] == 'Get System Information':
        sys_info_command = cmd
        break

if sys_info_command:
    print(f'Found command: {sys_info_command["name"]}')
    print(f'Command ID: {sys_info_command["id"]}')
    print(f'Command: {sys_info_command["command"]}')
    
    # Create a mock agent for testing
    mock_agent_data = {
        'agent_id': 'test-agent-dx227',
        'hostname': 'TEST-PC',
        'platform': 'Windows 11 Pro',
        'status': 'online'
    }
    
    # Add the mock agent
    try:
        mock_response = requests.post('http://localhost:8080/api/v1/commands/test/mock-agent', 
            headers=headers, json=mock_agent_data)
        print(f'Mock agent added: {mock_response.status_code}')
    except:
        pass
    
    # Execute the command on the mock agent
    execution_data = {
        'agent_ids': ['test-agent-dx227'],
        'parameters': {},
        'timeout': 30
    }
    
    exec_response = requests.post(
        f'http://localhost:8080/api/v1/commands/saved/{sys_info_command["id"]}/execute',
        headers=headers,
        json=execution_data
    )
    
    print(f'\nExecution response status: {exec_response.status_code}')
    exec_result = exec_response.json()
    print(f'Execution result: {json.dumps(exec_result, indent=2)}')
    
    # Check if command was sent
    if exec_result.get('results'):
        result = exec_result['results'][0]
        if result.get('command_id'):
            # Wait a bit for the command to complete
            time.sleep(2)
            
            # Get the command result
            result_response = requests.get(
                f'http://localhost:8080/api/v1/commands/agent/test-agent-dx227/result/{result["command_id"]}',
                headers=headers
            )
            
            print(f'\nResult response status: {result_response.status_code}')
            if result_response.status_code == 200:
                cmd_result = result_response.json()
                print(f'Command result: {json.dumps(cmd_result, indent=2)}')
                
                # Check if the output is valid JSON
                if cmd_result.get('result', {}).get('output'):
                    try:
                        parsed_json = json.loads(cmd_result['result']['output'])
                        print('\n✅ SUCCESS: Output is valid JSON!')
                        print(f'Parsed JSON: {json.dumps(parsed_json, indent=2)}')
                    except json.JSONDecodeError as e:
                        print(f'\n❌ ERROR: Failed to parse output as JSON: {e}')
                        print(f'Raw output: {cmd_result["result"]["output"][:500]}')
else:
    print('Command not found!')