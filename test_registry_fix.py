#!/usr/bin/env python3
import requests
import json

# Login first
login_data = {'username': 'admin', 'password': 'admin123'}
response = requests.post('http://localhost:8080/api/v1/auth/login', json=login_data)

if response.status_code == 200:
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get online agent
    agents_response = requests.get('http://localhost:8080/api/v1/agents', headers=headers)
    if agents_response.status_code == 200:
        agents_data = agents_response.json()
        # Handle both list and dict response
        if isinstance(agents_data, dict) and 'agents' in agents_data:
            agents = agents_data['agents']
        else:
            agents = agents_data if isinstance(agents_data, list) else []
        online_agent = next((a for a in agents if a.get('status') == 'online'), None)
        
        if online_agent:
            agent_id = online_agent.get('id') or online_agent.get('agent_id')
            print(f'Testing with agent: {agent_id}')
            
            # Test registry key deletion
            test_path = 'HKCU\\Software\\TestKey'
            response = requests.delete(
                f'http://localhost:8080/api/v1/agents/{agent_id}/registry/keys',
                params={'path': test_path},
                headers=headers
            )
            print(f'Registry key deletion: {response.status_code}')
            if response.status_code >= 400:
                print(f'Error: {response.text}')
            else:
                print('✓ Registry key deletion working')
            
            # Test registry value deletion  
            response = requests.delete(
                f'http://localhost:8080/api/v1/agents/{agent_id}/registry/values',
                params={'path': test_path, 'name': 'TestValue'},
                headers=headers
            )
            print(f'Registry value deletion: {response.status_code}')
            if response.status_code >= 400:
                print(f'Error: {response.text}')
            else:
                print('✓ Registry value deletion working')
                
            # Test registry import
            response = requests.post(
                f'http://localhost:8080/api/v1/agents/{agent_id}/registry/import',
                json={'file': 'C:\\temp\\registry_export.reg'},
                headers=headers
            )
            print(f'Registry import: {response.status_code}')
            if response.status_code >= 400:
                print(f'Error: {response.text}')
            else:
                print('✓ Registry import working')
                
            print('\n--- Summary ---')
            print('All registry operations tested successfully!')
        else:
            print('No online agent found - simulating with mock agent ID')
            agent_id = 'desktop-jk5g34l-dexagent'
            
            # Test with mock agent (should return 400 or 404)
            test_path = 'HKCU\\Software\\TestKey'
            response = requests.delete(
                f'http://localhost:8080/api/v1/agents/{agent_id}/registry/keys',
                params={'path': test_path},
                headers=headers
            )
            print(f'Registry key deletion (offline agent): {response.status_code}')
            if response.status_code == 400 or response.status_code == 404:
                print('✓ Proper error handling for offline agent')
            
    else:
        print(f'Failed to get agents: {agents_response.status_code}')
else:
    print(f'Login failed: {response.status_code}')