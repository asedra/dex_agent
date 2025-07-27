#!/usr/bin/env python3
"""
Windows PowerShell Agent Test Client
API'yi test etmek için basit bir client
"""

import requests
import json
import time
from typing import Dict, Any

class PowerShellAgentClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_token: str = "test_token_123"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint'ini test et"""
        try:
            response = requests.get(f"{self.base_url}/")
            return {
                "status_code": response.status_code,
                "data": response.json()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Sistem bilgilerini al"""
        try:
            response = requests.get(f"{self.base_url}/system/info", headers=self.headers)
            return {
                "status_code": response.status_code,
                "data": response.json()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def execute_command(self, command: str, timeout: int = 30, working_directory: str = None) -> Dict[str, Any]:
        """PowerShell komutu çalıştır"""
        payload = {
            "command": command,
            "timeout": timeout
        }
        
        if working_directory:
            payload["working_directory"] = working_directory
        
        try:
            response = requests.post(
                f"{self.base_url}/execute",
                headers=self.headers,
                json=payload
            )
            return {
                "status_code": response.status_code,
                "data": response.json()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def execute_batch_commands(self, commands: list) -> Dict[str, Any]:
        """Çoklu komut çalıştır"""
        payload = []
        for cmd in commands:
            if isinstance(cmd, str):
                payload.append({"command": cmd})
            else:
                payload.append(cmd)
        
        try:
            response = requests.post(
                f"{self.base_url}/execute/batch",
                headers=self.headers,
                json=payload
            )
            return {
                "status_code": response.status_code,
                "data": response.json()
            }
        except Exception as e:
            return {"error": str(e)}

def main():
    """Test fonksiyonları"""
    client = PowerShellAgentClient()
    
    print("🔍 Windows PowerShell Agent Test Client")
    print("=" * 50)
    
    # 1. Health Check
    print("\n1. Health Check Test:")
    result = client.health_check()
    print(f"Status: {result.get('status_code', 'N/A')}")
    print(f"Response: {json.dumps(result.get('data', result), indent=2)}")
    
    # 2. System Info
    print("\n2. System Info Test:")
    result = client.get_system_info()
    print(f"Status: {result.get('status_code', 'N/A')}")
    if 'data' in result:
        data = result['data']
        print(f"Hostname: {data.get('hostname', 'N/A')}")
        print(f"OS Version: {data.get('os_version', 'N/A')}")
        print(f"CPU Usage: {data.get('cpu_usage', 'N/A')}%")
        print(f"Memory Usage: {data.get('memory_usage', 'N/A')}%")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    # 3. Single Command Test
    print("\n3. Single Command Test:")
    result = client.execute_command("Get-Process | Select-Object Name,Id,CPU -First 5")
    print(f"Status: {result.get('status_code', 'N/A')}")
    if 'data' in result:
        data = result['data']
        print(f"Success: {data.get('success', 'N/A')}")
        print(f"Execution Time: {data.get('execution_time', 'N/A')}s")
        print(f"Output: {data.get('output', 'N/A')[:200]}...")
        if data.get('error'):
            print(f"Error: {data.get('error')}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    # 4. Batch Commands Test
    print("\n4. Batch Commands Test:")
    commands = [
        "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name,Status -First 3",
        "Get-ComputerInfo | Select-Object WindowsProductName,WindowsVersion",
        "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"
    ]
    result = client.execute_batch_commands(commands)
    print(f"Status: {result.get('status_code', 'N/A')}")
    if 'data' in result and isinstance(result['data'], list):
        for i, cmd_result in enumerate(result['data']):
            print(f"\nCommand {i+1}:")
            if isinstance(cmd_result, dict):
                print(f"  Success: {cmd_result.get('success', 'N/A')}")
                print(f"  Execution Time: {cmd_result.get('execution_time', 'N/A')}s")
                print(f"  Output: {cmd_result.get('output', 'N/A')[:100]}...")
            else:
                print(f"  Error: Invalid response format")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print("\n✅ Test tamamlandı!")

if __name__ == "__main__":
    main() 