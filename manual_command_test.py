#!/usr/bin/env python3
"""
Manual test for Command Library page - checking for errors
"""

import requests
import json
from datetime import datetime

def test_command_library():
    """Test Command Library page functionality"""
    
    errors_found = []
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "page": "Command Library",
        "url": "http://localhost:3000/commands",
        "errors": []
    }
    
    # Login first
    session = requests.Session()
    login_url = "http://localhost:8080/api/v1/auth/login"
    
    try:
        # Login
        login_data = {"username": "admin", "password": "admin123"}
        login_response = session.post(login_url, json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful")
        else:
            error = f"Login failed: {login_response.status_code}"
            errors_found.append(error)
            print(f"❌ {error}")
            return errors_found
        
        # Test 1: Get saved commands
        print("\n📋 Testing Command Library API endpoints...")
        
        commands_url = "http://localhost:8080/api/v1/commands/saved"
        response = session.get(commands_url, headers=headers)
        
        if response.status_code == 200:
            commands = response.json()
            print(f"✅ Retrieved {len(commands)} saved commands")
            
            # Look for "Get System Information" command
            system_info_cmd = None
            for cmd in commands:
                if "system" in cmd.get("name", "").lower() and "info" in cmd.get("name", "").lower():
                    system_info_cmd = cmd
                    print(f"✅ Found 'Get System Information' command: {cmd.get('name')}")
                    break
            
            if not system_info_cmd:
                error = "Get System Information command not found in saved commands"
                errors_found.append(error)
                print(f"⚠️  {error}")
                
                # Try to create it
                create_url = "http://localhost:8080/api/v1/commands"
                new_command = {
                    "name": "Get System Information",
                    "description": "Retrieve comprehensive system information",
                    "command": "Get-ComputerInfo | ConvertTo-Json",
                    "category": "System Info"
                }
                create_response = session.post(create_url, json=new_command, headers=headers)
                
                if create_response.status_code in [200, 201]:
                    print("✅ Created 'Get System Information' command")
                    system_info_cmd = create_response.json()
                else:
                    error = f"Failed to create Get System Information command: {create_response.status_code}"
                    errors_found.append(error)
                    print(f"❌ {error}")
        else:
            error = f"Failed to get saved commands: {response.status_code}"
            errors_found.append(error)
            print(f"❌ {error}")
        
        # Test 2: Check AI endpoint
        print("\n🤖 Testing AI features...")
        
        ai_status_url = "http://localhost:8080/api/v1/commands/ai/status"
        ai_response = session.get(ai_status_url, headers=headers)
        
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            if ai_data.get("available"):
                print("✅ AI features are available")
            else:
                error = "AI features not configured (missing API key)"
                errors_found.append(error)
                print(f"⚠️  {error}")
        else:
            error = f"AI status endpoint error: {ai_response.status_code}"
            errors_found.append(error)
            print(f"❌ {error}")
        
        # Test 3: Get agents for command execution
        print("\n🖥️  Testing agent availability...")
        
        agents_url = "http://localhost:8080/api/v1/agents"
        agents_response = session.get(agents_url, headers=headers)
        
        if agents_response.status_code == 200:
            agents = agents_response.json()
            if len(agents) > 0:
                print(f"✅ Found {len(agents)} agents")
                
                # Try to execute system info command on first agent
                if system_info_cmd:
                    agent_id = agents[0].get("id")
                    execute_url = f"http://localhost:8080/api/v1/commands/agent/{agent_id}/execute"
                    execute_data = {
                        "command": system_info_cmd.get("command"),
                        "name": system_info_cmd.get("name")
                    }
                    
                    execute_response = session.post(execute_url, json=execute_data, headers=headers)
                    
                    if execute_response.status_code in [200, 201, 202]:
                        print(f"✅ Executed 'Get System Information' on agent {agent_id}")
                    else:
                        error = f"Failed to execute command on agent: {execute_response.status_code}"
                        errors_found.append(error)
                        print(f"❌ {error}")
            else:
                error = "No agents available for command execution"
                errors_found.append(error)
                print(f"⚠️  {error}")
        else:
            error = f"Failed to get agents: {agents_response.status_code}"
            errors_found.append(error)
            print(f"❌ {error}")
        
        # Test 4: Frontend specific issues
        print("\n🌐 Checking frontend accessibility...")
        
        # Check if frontend loads
        frontend_response = requests.get("http://localhost:3000/")
        if frontend_response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            error = f"Frontend not accessible: {frontend_response.status_code}"
            errors_found.append(error)
            print(f"❌ {error}")
        
    except requests.exceptions.ConnectionError as e:
        error = f"Connection error: {str(e)}"
        errors_found.append(error)
        print(f"❌ {error}")
    except Exception as e:
        error = f"Unexpected error: {str(e)}"
        errors_found.append(error)
        print(f"❌ {error}")
    
    # Additional known issues from frontend
    known_issues = [
        "AI button always visible but redirects to settings when not configured",
        "Command execution requires agent to be online",
        "Search functionality may not filter commands in real-time",
        "Category filter might not work properly"
    ]
    
    print("\n⚠️  Known potential issues:")
    for issue in known_issues:
        print(f"  - {issue}")
    
    # Compile all errors
    test_results["errors"] = errors_found + known_issues
    
    # Save results
    with open('/home/ali/dex_agent/command_library_errors.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    return test_results

if __name__ == "__main__":
    print("="*60)
    print("COMMAND LIBRARY PAGE - ERROR CHECK")
    print("="*60)
    
    results = test_command_library()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if results.get("errors"):
        print(f"❌ Total issues found: {len(results['errors'])}")
        print("\nIssues to report in Jira:")
        for i, error in enumerate(results['errors'], 1):
            print(f"{i}. {error}")
    else:
        print("✅ No errors found")
    
    print("\nResults saved to: command_library_errors.json")