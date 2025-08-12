#!/usr/bin/env python3
"""
Execute Get System Information command on agent
"""

import requests
import json
import time

def execute_system_info():
    """Execute Get System Information command on an available agent"""
    
    # Login
    session = requests.Session()
    login_url = "http://localhost:8080/api/v1/auth/login"
    login_data = {"username": "admin", "password": "admin123"}
    login_response = session.post(login_url, json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Get agents
    agents_url = "http://localhost:8080/api/v1/agents"
    agents_response = session.get(agents_url, headers=headers)
    
    if agents_response.status_code != 200:
        print(f"❌ Failed to get agents: {agents_response.status_code}")
        return False
    
    agents_data = agents_response.json()
    
    # Handle both list and dict response formats
    if isinstance(agents_data, dict):
        agents = agents_data.get("items", []) or agents_data.get("agents", [])
    else:
        agents = agents_data
    
    if not agents:
        print("❌ No agents available")
        return False
    
    print(f"✅ Found {len(agents)} agents")
    
    # Find an online agent
    online_agent = None
    for agent in agents:
        # Handle both string and dict agent formats
        if isinstance(agent, str):
            # If agent is just an ID string, use it
            online_agent = {"id": agent}
            break
        elif isinstance(agent, dict):
            if agent.get("status") == "online" or agent.get("is_online"):
                online_agent = agent
                break
    
    if not online_agent:
        # Use first agent anyway
        first_agent = agents[0]
        if isinstance(first_agent, str):
            online_agent = {"id": first_agent}
        else:
            online_agent = first_agent
        print(f"⚠️  No online agents, using agent: {online_agent.get('hostname', online_agent.get('id', 'Unknown'))}")
    else:
        print(f"✅ Using online agent: {online_agent.get('hostname', 'Unknown')}")
    
    # Execute Get System Information command
    agent_id = online_agent.get("id")
    execute_url = f"http://localhost:8080/api/v1/commands/execute"
    
    # The command to execute
    system_info_command = {
        "agent_id": agent_id,
        "command": "Get-ComputerInfo | ConvertTo-Json",
        "command_type": "powershell"
    }
    
    print(f"\n📊 Executing 'Get System Information' on agent {agent_id}...")
    
    try:
        execute_response = session.post(execute_url, json=system_info_command, headers=headers)
        
        if execute_response.status_code in [200, 201, 202]:
            result = execute_response.json()
            print("✅ Command executed successfully!")
            
            # Check for execution ID to get results
            execution_id = result.get("id") or result.get("execution_id")
            
            if execution_id:
                # Wait a bit for execution
                time.sleep(2)
                
                # Try to get results
                results_url = f"http://localhost:8080/api/v1/commands/execution/{execution_id}"
                results_response = session.get(results_url, headers=headers)
                
                if results_response.status_code == 200:
                    execution_result = results_response.json()
                    print("\n📋 Execution Result:")
                    print(f"  Status: {execution_result.get('status', 'Unknown')}")
                    
                    output = execution_result.get('output', '')
                    if output:
                        print(f"  Output preview: {output[:200]}...")
                    
                    # Save full result
                    with open('/home/ali/dex_agent/system_info_result.json', 'w') as f:
                        json.dump(execution_result, f, indent=2)
                    
                    print("\n✅ Full result saved to: system_info_result.json")
                else:
                    print(f"⚠️  Could not get execution results: {results_response.status_code}")
            else:
                print("⚠️  No execution ID returned")
                print(f"Response: {json.dumps(result, indent=2)}")
            
            return True
            
        else:
            print(f"❌ Failed to execute command: {execute_response.status_code}")
            print(f"Response: {execute_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error executing command: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("EXECUTING GET SYSTEM INFORMATION COMMAND")
    print("="*60)
    
    success = execute_system_info()
    
    print("\n" + "="*60)
    if success:
        print("✅ Command execution completed")
    else:
        print("❌ Command execution failed")