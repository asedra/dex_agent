#!/usr/bin/env python3
"""
Comprehensive API Test Suite for DexAgents
Tests all 118 API endpoints with validation and reporting
"""

import requests
import json
import time
import uuid
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import traceback

# API Configuration
BASE_URL = "http://localhost:8080"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"

# Test result tracking
@dataclass
class TestResult:
    endpoint: str
    method: str
    status: str  # PASS, FAIL, SKIP
    response_code: Optional[int] = None
    response_time: Optional[float] = None
    error: Optional[str] = None
    details: Optional[Dict] = None

class APITester:
    def __init__(self):
        self.token = None
        self.results: List[TestResult] = []
        self.online_agent_id = None
        self.offline_agent_id = None
        self.test_command_id = None
        self.test_package_id = None
        self.test_job_id = None
        self.start_time = datetime.now()
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️ ",
            "TEST": "🧪"
        }.get(level, "  ")
        print(f"[{timestamp}] {prefix} {message}")
        
    def test_endpoint(self, method: str, path: str, **kwargs) -> TestResult:
        """Test a single endpoint"""
        url = f"{BASE_URL}{path}"
        headers = kwargs.get('headers', {})
        
        # Add auth token if available and not explicitly excluded
        if self.token and 'no_auth' not in kwargs:
            headers['Authorization'] = f"Bearer {self.token}"
            kwargs['headers'] = headers
            
        # Remove custom flags
        kwargs.pop('no_auth', None)
        test_name = kwargs.pop('test_name', f"{method} {path}")
        
        self.log(f"Testing: {test_name}", "TEST")
        
        start_time = time.time()
        result = TestResult(
            endpoint=path,
            method=method,
            status="FAIL"
        )
        
        try:
            response = requests.request(method, url, **kwargs)
            response_time = (time.time() - start_time) * 1000  # ms
            
            result.response_code = response.status_code
            result.response_time = response_time
            
            # Determine if test passed based on status code
            if response.status_code < 400:
                result.status = "PASS"
                self.log(f"  Response: {response.status_code} ({response_time:.1f}ms)", "SUCCESS")
            else:
                result.status = "FAIL"
                result.error = f"HTTP {response.status_code}"
                self.log(f"  Response: {response.status_code} - {response.text[:200]}", "ERROR")
                
            return result
            
        except Exception as e:
            result.status = "FAIL"
            result.error = str(e)
            self.log(f"  Exception: {str(e)}", "ERROR")
            return result
        finally:
            self.results.append(result)
            
    def run_tests(self):
        """Run all API tests"""
        self.log("=" * 60)
        self.log("DexAgents Comprehensive API Test Suite")
        self.log("=" * 60)
        
        # Test modules in order
        self.test_auth_endpoints()
        self.test_system_endpoints()
        self.test_agent_endpoints()
        self.test_command_endpoints()
        self.test_service_endpoints()
        self.test_registry_endpoints()
        self.test_file_endpoints()
        self.test_network_endpoints()
        self.test_process_endpoints()
        self.test_event_endpoints()
        self.test_software_endpoints()
        self.test_settings_endpoints()
        self.test_websocket_endpoints()
        self.test_installer_endpoints()
        
        # Generate report
        self.generate_report()
        
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        self.log("\n🔐 Testing Authentication Endpoints", "INFO")
        self.log("-" * 40)
        
        # Login
        result = self.test_endpoint(
            "POST", "/api/v1/auth/login",
            json={"username": DEFAULT_USERNAME, "password": DEFAULT_PASSWORD},
            no_auth=True,
            test_name="Login with valid credentials"
        )
        
        if result.status == "PASS":
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"username": DEFAULT_USERNAME, "password": DEFAULT_PASSWORD}
            )
            data = response.json()
            self.token = data.get('access_token')
            self.log(f"  Token obtained: {self.token[:20]}...", "INFO")
        
        # Get current user
        self.test_endpoint("GET", "/api/v1/auth/me", test_name="Get current user info")
        
        # Logout
        self.test_endpoint("POST", "/api/v1/auth/logout", test_name="Logout user")
        
    def test_system_endpoints(self):
        """Test system endpoints"""
        self.log("\n⚙️ Testing System Endpoints", "INFO")
        self.log("-" * 40)
        
        # Health check (no auth required)
        self.test_endpoint("GET", "/api/v1/system/health", no_auth=True, test_name="Health check")
        self.test_endpoint("GET", "/api/v1/health", no_auth=True, test_name="Alternative health check")
        
        # System info
        self.test_endpoint("GET", "/api/v1/system/info", test_name="Get system info")
        
        # Stats and metrics
        self.test_endpoint("GET", "/api/v1/stats", no_auth=True, test_name="Get system stats")
        self.test_endpoint("GET", "/api/v1/metrics", no_auth=True, test_name="Get metrics")
        
        # Root endpoint
        self.test_endpoint("GET", "/", no_auth=True, test_name="Root endpoint")
        
    def test_agent_endpoints(self):
        """Test agent management endpoints"""
        self.log("\n🖥️ Testing Agent Endpoints", "INFO")
        self.log("-" * 40)
        
        # Get all agents
        result = self.test_endpoint("GET", "/api/v1/agents/", test_name="Get all agents")
        if result.status == "PASS":
            response = requests.get(
                f"{BASE_URL}/api/v1/agents/",
                headers={'Authorization': f"Bearer {self.token}"}
            )
            data = response.json()
            agents = data.get('agents', [])
            
            # Find online and offline agents
            for agent in agents:
                if agent.get('is_connected') or agent.get('status') == 'online':
                    self.online_agent_id = agent['id']
                    self.log(f"  Found online agent: {self.online_agent_id}", "INFO")
                elif not self.offline_agent_id:
                    self.offline_agent_id = agent['id']
                    self.log(f"  Found offline agent: {self.offline_agent_id}", "INFO")
                    
                if self.online_agent_id and self.offline_agent_id:
                    break
        
        # Test other agent endpoints
        self.test_endpoint("GET", "/api/v1/agents/list", test_name="Get agents list (legacy)")
        self.test_endpoint("GET", "/api/v1/agents/connected", test_name="Get connected agents")
        self.test_endpoint("GET", "/api/v1/agents/offline", test_name="Get offline agents")
        
        # Test with specific agent ID 
        test_agent_id = "desktop-jk5g34l-dexagent"
        
        # Test agent-specific endpoints with provided agent ID
        self.test_endpoint("GET", f"/api/v1/agents/{test_agent_id}", test_name="Get specific agent (desktop-jk5g34l-dexagent)")
        self.test_endpoint("PUT", f"/api/v1/agents/{test_agent_id}", 
                         json={"tags": ["test", "api"]}, test_name="Update agent (desktop-jk5g34l-dexagent)")
        self.test_endpoint("POST", f"/api/v1/agents/{test_agent_id}/heartbeat", 
                         test_name="Send heartbeat (desktop-jk5g34l-dexagent)")
        self.test_endpoint("POST", f"/api/v1/agents/{test_agent_id}/refresh",
                         test_name="Refresh agent (desktop-jk5g34l-dexagent)")
        self.test_endpoint("GET", f"/api/v1/agents/status/{test_agent_id}",
                         test_name="Get agent status (desktop-jk5g34l-dexagent)")
        self.test_endpoint("GET", f"/api/v1/agents/{test_agent_id}/commands",
                         test_name="Get command history (desktop-jk5g34l-dexagent)")
        
        # Test command execution on specific agent
        self.test_endpoint("POST", f"/api/v1/agents/{test_agent_id}/command",
                         json={"command": "Get-Date", "timeout": 5000},
                         test_name="Execute command on agent (desktop-jk5g34l-dexagent)")

        if self.online_agent_id:
            # Test agent-specific endpoints with dynamically found agent
            self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}", test_name="Get specific agent")
            self.test_endpoint("PUT", f"/api/v1/agents/{self.online_agent_id}", 
                             json={"tags": ["test", "api"]}, test_name="Update agent")
            self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/heartbeat", 
                             test_name="Send heartbeat")
            self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/refresh",
                             test_name="Refresh agent")
            self.test_endpoint("GET", f"/api/v1/agents/status/{self.online_agent_id}",
                             test_name="Get agent status")
            self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/commands",
                             test_name="Get command history")
            
            # Test command execution on agent
            self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/command",
                             json={"command": "Get-Date", "timeout": 5000},
                             test_name="Execute command on agent")
        
        # Test bulk operations
        self.test_endpoint("POST", "/api/v1/agents/bulk",
                         json={
                             "operation": "update_tags",
                             "agent_ids": [self.online_agent_id] if self.online_agent_id else [],
                             "tags": ["bulk-test"]
                         },
                         test_name="Bulk agent operation")
        
        # Register new agent
        self.test_endpoint("POST", "/api/v1/agents/register",
                         json={
                             "hostname": f"TEST-API-{uuid.uuid4().hex[:8]}",
                             "ip": "192.168.1.200",
                             "os": "Windows 10",
                             "version": "10.0.19045"
                         },
                         test_name="Register new agent")
        
        # Seed test data
        self.test_endpoint("POST", "/api/v1/agents/seed", test_name="Seed test agents")
        
    def test_command_endpoints(self):
        """Test command execution endpoints"""
        self.log("\n📟 Testing Command Endpoints", "INFO")
        self.log("-" * 40)
        
        # Get saved commands
        result = self.test_endpoint("GET", "/api/v1/commands/saved", test_name="Get saved commands")
        if result.status == "PASS":
            response = requests.get(
                f"{BASE_URL}/api/v1/commands/saved",
                headers={'Authorization': f"Bearer {self.token}"}
            )
            commands = response.json()
            if commands:
                self.test_command_id = commands[0]['id']
                self.log(f"  Found saved command: {self.test_command_id}", "INFO")
        
        # Create new command with proper test marking
        new_command = {
            "name": f"Test Command {uuid.uuid4().hex[:8]}",
            "description": "API test command - automatically generated for testing",
            "category": "Testing",
            "command": "Get-Process | Select-Object -First 5",
            "tags": ["test", "api", "auto-generated"]
        }
        result = self.test_endpoint("POST", "/api/v1/commands/saved",
                                  json=new_command,
                                  test_name="Create saved command")
        
        if result.status == "PASS":
            response = requests.post(
                f"{BASE_URL}/api/v1/commands/saved",
                json=new_command,
                headers={'Authorization': f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                created_command = response.json()
                test_cmd_id = created_command.get('id')
                if test_cmd_id:
                    # Test command CRUD operations
                    self.test_endpoint("GET", f"/api/v1/commands/saved/{test_cmd_id}",
                                     test_name="Get specific command")
                    self.test_endpoint("PUT", f"/api/v1/commands/saved/{test_cmd_id}",
                                     json={"description": "Updated description"},
                                     test_name="Update command")
                    
                    if self.online_agent_id:
                        self.test_endpoint("POST", f"/api/v1/commands/saved/{test_cmd_id}/execute",
                                         json={"agent_ids": [self.online_agent_id]},
                                         test_name="Execute saved command")
                    
                    self.test_endpoint("DELETE", f"/api/v1/commands/saved/{test_cmd_id}",
                                     test_name="Delete command")
        
        # Test direct command execution
        self.test_endpoint("POST", "/api/v1/commands/execute",
                         json={"command": "Write-Output 'Test'"},
                         test_name="Execute PowerShell command")
        
        self.test_endpoint("POST", "/api/v1/commands/execute/batch",
                         json=[
                             {"command": "Write-Output 'Test1'"},
                             {"command": "Write-Output 'Test2'"}
                         ],
                         test_name="Execute batch commands")
        
        # Test agent command execution
        if self.online_agent_id:
            self.test_endpoint("POST", f"/api/v1/commands/agent/{self.online_agent_id}/execute",
                             json={"command": "Get-Date"},
                             no_auth=True,
                             test_name="Execute on agent (sync)")
            
            # Execute async command and capture the command ID
            async_result = self.test_endpoint("POST", f"/api/v1/commands/agent/{self.online_agent_id}/execute/async",
                             json={"command": "Get-Date"},
                             no_auth=True,
                             test_name="Execute on agent (async)")
            
            # Try to get command result using actual command ID from async execution
            if async_result.status == "PASS":
                # Make the actual async request to get the command ID
                response = requests.post(
                    f"{BASE_URL}/api/v1/commands/agent/{self.online_agent_id}/execute/async",
                    json={"command": "Get-Date"}
                )
                if response.status_code == 200:
                    async_data = response.json()
                    command_id = async_data.get('command_id')
                    if command_id:
                        # Wait a moment for command to execute
                        time.sleep(0.5)
                        # Now test result retrieval with real command ID
                        self.test_endpoint("GET", f"/api/v1/commands/agent/{self.online_agent_id}/result/{command_id}",
                                         no_auth=True,
                                         test_name="Get command result")
                    else:
                        self.log("  No command_id returned from async execution", "WARNING")
                else:
                    self.log(f"  Async execution failed with status {response.status_code}", "WARNING")
        
        # Test AI endpoints
        self.test_endpoint("GET", "/api/v1/commands/ai/status", test_name="Get AI status")
        self.test_endpoint("POST", "/api/v1/commands/ai/generate",
                         json={"message": "Get system information"},
                         test_name="Generate AI command")
        
        if self.online_agent_id:
            self.test_endpoint("POST", "/api/v1/commands/ai/test",
                             json={
                                 "agent_id": self.online_agent_id,
                                 "command": "Get-ComputerInfo"
                             },
                             test_name="Test AI command")
        
        # Test mock agent endpoints
        self.test_endpoint("GET", "/api/v1/commands/test/status", test_name="Get test status")
        self.test_endpoint("POST", "/api/v1/commands/test/mock-agent",
                         json={
                             "hostname": "MOCK-TEST",
                             "ip": "10.0.0.1",
                             "os": "Windows 10"
                         },
                         test_name="Add mock agent")
        self.test_endpoint("DELETE", "/api/v1/commands/test/mock-agent/mock-test-id",
                         test_name="Remove mock agent")
        
    def test_service_endpoints(self):
        """Test Windows service management endpoints"""
        self.log("\n🔧 Testing Service Endpoints", "INFO")
        self.log("-" * 40)
        
        if not self.online_agent_id:
            self.log("  No online agent available, skipping service tests", "WARNING")
            return
            
        # Get services
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/services",
                         test_name="Get agent services")
        
        # Test specific service (Windows Time service usually exists)
        service_name = "W32Time"
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/services/{service_name}",
                         test_name=f"Get service details ({service_name})")
        
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/services/{service_name}/dependencies",
                         test_name=f"Get service dependencies")
        
        # Service actions (non-destructive - just test with stop on a non-critical service)
        # Note: We'll use "stop" action but on a service that's likely already stopped or safe to stop
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/services/action",
                         json={"action": "stop", "service_name": service_name, "force": "false"},
                         test_name="Stop service action")
        
        # Service configuration
        self.test_endpoint("PUT", f"/api/v1/agents/{self.online_agent_id}/services/{service_name}/config",
                         json={"startup_type": "Manual"},  # Capital M for valid startup type
                         test_name="Configure service")
        
        # Batch service operations
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/services/batch",
                         json={
                             "services": [service_name],
                             "action": "stop"  # Changed from "status" to valid action
                         },
                         test_name="Batch service action")
        
    def test_registry_endpoints(self):
        """Test Windows registry endpoints"""
        self.log("\n📋 Testing Registry Endpoints", "INFO")
        self.log("-" * 40)
        
        if not self.online_agent_id:
            self.log("  No online agent available, skipping registry tests", "WARNING")
            return
            
        # Get registry keys
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/registry/keys",
                         params={"path": "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion"},
                         test_name="Get registry keys")
        
        # Get registry values
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/registry/values",
                         params={"path": "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion"},
                         test_name="Get registry values")
        
        # Search registry
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/registry/search",
                         json={
                             "pattern": "Windows",
                             "search_keys": True,
                             "search_values": True
                         },
                         test_name="Search registry")
        
        # Create test registry value (in safe location)
        test_path = "HKCU:\\Software\\DexAgents\\Test"
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/registry/values",
                         json={
                             "path": test_path,
                             "name": "TestValue",
                             "value": "TestData",
                             "type": "String"
                         },
                         test_name="Create registry value")
        
        # Delete test registry value
        self.test_endpoint("DELETE", f"/api/v1/agents/{self.online_agent_id}/registry/values",
                         params={
                             "path": test_path,
                             "name": "TestValue"
                         },
                         test_name="Delete registry value")
        
        # Delete test registry key
        self.test_endpoint("DELETE", f"/api/v1/agents/{self.online_agent_id}/registry/keys",
                         params={"path": test_path},
                         test_name="Delete registry key")
        
        # Export/Import registry
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/registry/export",
                         json={
                             "path": "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion",
                             "file": "C:\\temp\\registry_export.reg"
                         },
                         test_name="Export registry")
        
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/registry/import",
                         json={"file": "C:\\temp\\registry_export.reg"},
                         test_name="Import registry")
        
        # Backup registry
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/registry/backup",
                         json={
                             "path": "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion",
                             "backup_file": "C:\\temp\\registry_backup.reg"
                         },
                         test_name="Backup registry")
        
    def test_file_endpoints(self):
        """Test file management endpoints"""
        self.log("\n📁 Testing File Endpoints", "INFO")
        self.log("-" * 40)
        
        if not self.online_agent_id:
            self.log("  No online agent available, skipping file tests", "WARNING")
            return
            
        # List directory
        self.test_endpoint("GET", f"/api/v1/files/agents/{self.online_agent_id}/files",
                         params={"path": "C:\\Windows"},
                         test_name="List directory")
        
        # Get file tree
        self.test_endpoint("GET", f"/api/v1/files/agents/{self.online_agent_id}/files/tree",
                         params={"path": "C:\\Windows\\System32", "max_depth": 2},
                         test_name="Get file tree")
        
        # Search files
        self.test_endpoint("POST", f"/api/v1/files/agents/{self.online_agent_id}/files/search",
                         json={
                             "search_path": "C:\\Windows",
                             "pattern": "*.ini"
                         },
                         test_name="Search files")
        
        # Preview file
        self.test_endpoint("GET", f"/api/v1/files/agents/{self.online_agent_id}/files/preview",
                         params={"file_path": "C:\\Windows\\win.ini"},
                         test_name="Preview file")
        
        # Create test folder
        test_folder = "C:\\temp\\dexagents_test"
        self.test_endpoint("POST", f"/api/v1/files/agents/{self.online_agent_id}/files/folder",
                         params={"path": test_folder},
                         test_name="Create folder")
        
        # Upload file (simulate)
        self.test_endpoint("POST", f"/api/v1/files/agents/{self.online_agent_id}/files/upload",
                         files={"file": ("test.txt", b"Test content", "text/plain")},
                         params={"target_path": test_folder},
                         test_name="Upload file")
        
        # Download file
        self.test_endpoint("GET", f"/api/v1/files/agents/{self.online_agent_id}/files/download",
                         params={"file_path": f"{test_folder}\\test.txt"},
                         test_name="Download file")
        
        # File operations
        self.test_endpoint("POST", f"/api/v1/files/agents/{self.online_agent_id}/files/operation",
                         json={
                             "operation": "copy",
                             "source_path": f"{test_folder}\\test.txt",
                             "target_path": f"{test_folder}\\test_copy.txt"
                         },
                         test_name="Copy file")
        
        # Compress files
        self.test_endpoint("POST", f"/api/v1/files/agents/{self.online_agent_id}/files/compress",
                         params={
                             "paths": [test_folder],
                             "output_path": f"{test_folder}.zip"
                         },
                         test_name="Compress files")
        
        # Extract archive
        self.test_endpoint("POST", f"/api/v1/files/agents/{self.online_agent_id}/files/extract",
                         params={
                             "archive_path": f"{test_folder}.zip",
                             "output_path": "C:\\temp\\extracted"
                         },
                         test_name="Extract archive")
        
        # Batch upload
        self.test_endpoint("POST", f"/api/v1/files/agents/{self.online_agent_id}/files/batch-upload",
                         files=[
                             ("files", ("file1.txt", b"Content 1", "text/plain")),
                             ("files", ("file2.txt", b"Content 2", "text/plain"))
                         ],
                         params={"target_path": test_folder},
                         test_name="Batch upload files")
        
        # Delete files
        self.test_endpoint("DELETE", f"/api/v1/files/agents/{self.online_agent_id}/files",
                         params={"paths": [test_folder]},
                         test_name="Delete files")
        
    def test_network_endpoints(self):
        """Test network management endpoints"""
        self.log("\n🌐 Testing Network Endpoints", "INFO")
        self.log("-" * 40)
        
        if not self.online_agent_id:
            self.log("  No online agent available, skipping network tests", "WARNING")
            return
            
        # Get network adapters
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/network/adapters",
                         test_name="Get network adapters")
        
        # Get firewall rules
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/network/firewall/rules",
                         test_name="Get firewall rules")
        
        # Get routing table
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/network/routing/table",
                         test_name="Get routing table")
        
        # Test network connectivity
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/network/test",
                         json={
                             "target": "8.8.8.8",
                             "type": "ping",
                             "count": 2
                         },
                         test_name="Test network connectivity")
        
        # Configure network adapter (non-destructive test)
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/network/configure",
                         json={
                             "adapter_id": "Ethernet",
                             "dhcp_enabled": True
                         },
                         test_name="Configure network adapter")
        
    def test_process_endpoints(self):
        """Test process management endpoints"""
        self.log("\n⚙️ Testing Process Endpoints", "INFO")
        self.log("-" * 40)
        
        if not self.online_agent_id:
            self.log("  No online agent available, skipping process tests", "WARNING")
            return
            
        # Get processes
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/processes/",
                         test_name="Get processes")
        
        # Get process tree
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/processes/tree",
                         test_name="Get process tree")
        
        # Kill process (using non-existent PID)
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/processes/kill",
                         json={"pid": 99999},
                         test_name="Kill process")
        
        # Set process priority
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/processes/priority",
                         json={
                             "pid": 1234,
                             "priority": "normal"
                         },
                         test_name="Set process priority")
        
        # Suspend/Resume process
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/processes/suspend-resume",
                         json={
                             "pid": 1234,
                             "action": "suspend"
                         },
                         test_name="Suspend/Resume process")
        
    def test_event_endpoints(self):
        """Test event log endpoints"""
        self.log("\n📊 Testing Event Endpoints", "INFO")
        self.log("-" * 40)
        
        if not self.online_agent_id:
            self.log("  No online agent available, skipping event tests", "WARNING")
            return
            
        # Get event logs
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/events/",
                         params={"log": "System", "limit": 10},
                         test_name="Get event logs")
        
        # Get event stats
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/events/stats",
                         params={"log": "Application"},
                         test_name="Get event statistics")
        
        # Get alert rules
        self.test_endpoint("GET", f"/api/v1/agents/{self.online_agent_id}/events/alert-rules",
                         test_name="Get alert rules")
        
        # Create alert rule
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/events/alert-rules",
                         json={
                             "name": "Test Alert",
                             "log": "System",
                             "event_id": 1001,
                             "level": "Error",
                             "action": "email"
                         },
                         test_name="Create alert rule")
        
        # Export event logs
        self.test_endpoint("POST", f"/api/v1/agents/{self.online_agent_id}/events/export",
                         json={
                             "log": "Application",
                             "format": "csv",
                             "start_time": "2025-01-01T00:00:00",
                             "end_time": "2025-12-31T23:59:59"
                         },
                         test_name="Export event logs")
        
    def test_software_endpoints(self):
        """Test software management endpoints"""
        self.log("\n💿 Testing Software Endpoints", "INFO")
        self.log("-" * 40)
        
        # Get packages
        self.test_endpoint("GET", "/api/v1/software/packages",
                         test_name="List packages")
        
        # Create package
        result = self.test_endpoint("POST", "/api/v1/software/packages",
                                   json={
                                       "name": "Test Package",
                                       "version": "1.0.0",
                                       "description": "Test package",
                                       "installer": "msi",
                                       "url": "https://example.com/test.msi"
                                   },
                                   test_name="Create package")
        
        if result.status == "PASS":
            response = requests.post(
                f"{BASE_URL}/api/v1/software/packages",
                json={
                    "name": f"Test Package {uuid.uuid4().hex[:8]}",
                    "version": "1.0.0",
                    "description": "Test package",
                    "installer": "msi"
                },
                headers={'Authorization': f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                package = response.json()
                self.test_package_id = package.get('id')
                
                if self.test_package_id:
                    # Test package operations
                    self.test_endpoint("GET", f"/api/v1/software/packages/{self.test_package_id}",
                                     test_name="Get package")
                    self.test_endpoint("PUT", f"/api/v1/software/packages/{self.test_package_id}",
                                     json={"description": "Updated description"},
                                     test_name="Update package")
                    self.test_endpoint("DELETE", f"/api/v1/software/packages/{self.test_package_id}",
                                     test_name="Delete package")
        
        # Upload package
        self.test_endpoint("POST", "/api/v1/software/packages/upload",
                         files={"file": ("test.msi", b"fake msi content", "application/octet-stream")},
                         test_name="Upload package")
        
        # Search Chocolatey
        self.test_endpoint("GET", "/api/v1/software/chocolatey/search",
                         params={"query": "notepad"},
                         test_name="Search Chocolatey packages")
        
        # Search Winget
        self.test_endpoint("GET", "/api/v1/software/winget/search",
                         params={"query": "notepad"},
                         test_name="Search Winget packages")
        
        # Get repositories
        self.test_endpoint("GET", "/api/v1/software/repositories",
                         test_name="List repositories")
        
        # Create repository
        self.test_endpoint("POST", "/api/v1/software/repositories",
                         json={
                             "name": "Test Repo",
                             "url": "https://example.com/repo",
                             "type": "nuget"
                         },
                         test_name="Create repository")
        
        if self.online_agent_id:
            # Get installed software
            self.test_endpoint("GET", f"/api/v1/software/agents/{self.online_agent_id}/installed",
                             test_name="Get installed software")
            
            # Install software (safe package)
            self.test_endpoint("POST", f"/api/v1/software/agents/{self.online_agent_id}/install",
                             json={
                                 "package": "7zip",
                                 "source": "chocolatey"
                             },
                             test_name="Install software")
            
            # Uninstall software
            self.test_endpoint("POST", f"/api/v1/software/agents/{self.online_agent_id}/uninstall",
                             json={"package": "7zip"},
                             test_name="Uninstall software")
        
        # Bulk install
        self.test_endpoint("POST", "/api/v1/software/bulk-install",
                         json={
                             "agent_ids": [self.online_agent_id] if self.online_agent_id else [],
                             "packages": ["notepadplusplus", "7zip"]
                         },
                         test_name="Bulk install")
        
        # Installation jobs
        self.test_endpoint("GET", "/api/v1/software/jobs",
                         test_name="List installation jobs")
        
        # Create a test job and track it
        if self.online_agent_id:
            response = requests.post(
                f"{BASE_URL}/api/v1/software/agents/{self.online_agent_id}/install",
                json={"package": "test-package", "source": "test"},
                headers={'Authorization': f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                job_data = response.json()
                job_id = job_data.get('job_id')
                if job_id:
                    self.test_job_id = job_id
                    self.test_endpoint("GET", f"/api/v1/software/jobs/{job_id}",
                                     test_name="Get installation job")
                    self.test_endpoint("PUT", f"/api/v1/software/jobs/{job_id}/cancel",
                                     test_name="Cancel installation job")
        
    def test_settings_endpoints(self):
        """Test settings management endpoints"""
        self.log("\n⚙️ Testing Settings Endpoints", "INFO")
        self.log("-" * 40)
        
        # Get all settings
        self.test_endpoint("GET", "/api/v1/settings/", test_name="Get all settings")
        
        # Create/Update setting
        test_setting = {
            "key": "test_setting",
            "value": "test_value",
            "description": "Test setting for API"
        }
        self.test_endpoint("POST", "/api/v1/settings/",
                         json=test_setting,
                         test_name="Create setting")
        
        # Get specific setting
        self.test_endpoint("GET", "/api/v1/settings/test_setting",
                         test_name="Get specific setting")
        
        # Delete setting
        self.test_endpoint("DELETE", "/api/v1/settings/test_setting",
                         test_name="Delete setting")
        
        # ChatGPT configuration
        self.test_endpoint("GET", "/api/v1/settings/chatgpt/config",
                         test_name="Get ChatGPT config")
        
        self.test_endpoint("POST", "/api/v1/settings/chatgpt/config",
                         json={
                             "api_key": "sk-test-key",
                             "model": "gpt-4",
                             "temperature": 0.7
                         },
                         test_name="Save ChatGPT config")
        
        # Test ChatGPT API
        self.test_endpoint("POST", "/api/v1/settings/chatgpt/test",
                         test_name="Test ChatGPT API")
        
        # Reload AI service
        self.test_endpoint("POST", "/api/v1/settings/reload-ai-service",
                         test_name="Reload AI service")
        
    def test_websocket_endpoints(self):
        """Test WebSocket-related endpoints"""
        self.log("\n🔌 Testing WebSocket Endpoints", "INFO")
        self.log("-" * 40)
        
        # Get connected agents (via WebSocket endpoint)
        self.test_endpoint("GET", "/api/v1/connected",
                         no_auth=True,
                         test_name="Get connected agents (WebSocket)")
        
        # Send command via WebSocket
        if self.online_agent_id:
            self.test_endpoint("POST", f"/api/v1/send/{self.online_agent_id}/command",
                             json={"command": "Get-Date"},
                             no_auth=True,
                             test_name="Send command via WebSocket")
        
    def test_installer_endpoints(self):
        """Test installer creation endpoints"""
        self.log("\n📦 Testing Installer Endpoints", "INFO")
        self.log("-" * 40)
        
        # Get installer config
        self.test_endpoint("GET", "/api/v1/installer/config",
                         no_auth=True,
                         test_name="Get installer config")
        
        # Create agent installer
        self.test_endpoint("POST", "/api/v1/installer/create",
                         json={
                             "server_url": "http://localhost:8080",
                             "agent_name": "TestAgent",
                             "auto_start": True
                         },
                         no_auth=True,
                         test_name="Create agent installer")
        
        # Create Python agent
        self.test_endpoint("POST", "/api/v1/installer/create-python",
                         json={
                             "server_url": "http://localhost:8080",
                             "agent_name": "TestPythonAgent"
                         },
                         no_auth=True,
                         test_name="Create Python agent")
        
    def generate_report(self):
        """Generate test report and analysis"""
        self.log("\n" + "=" * 60)
        self.log("📊 Test Results Summary")
        self.log("=" * 60)
        
        # Calculate statistics
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        skipped = sum(1 for r in self.results if r.status == "SKIP")
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        avg_response_time = sum(r.response_time or 0 for r in self.results if r.response_time) / max(1, sum(1 for r in self.results if r.response_time))
        
        # Print summary
        self.log(f"Total Tests: {total}")
        self.log(f"✅ Passed: {passed} ({pass_rate:.1f}%)")
        self.log(f"❌ Failed: {failed}")
        self.log(f"⏭️ Skipped: {skipped}")
        self.log(f"⏱️ Average Response Time: {avg_response_time:.1f}ms")
        self.log(f"⏰ Total Test Duration: {(datetime.now() - self.start_time).total_seconds():.1f}s")
        
        # Group results by endpoint category
        categories = {}
        for result in self.results:
            # Extract category from path
            parts = result.endpoint.split('/')
            if len(parts) > 3:
                category = parts[3]  # e.g., 'agents', 'commands', etc.
            else:
                category = 'other'
                
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0, 'total': 0}
                
            categories[category]['total'] += 1
            if result.status == "PASS":
                categories[category]['passed'] += 1
            elif result.status == "FAIL":
                categories[category]['failed'] += 1
        
        # Print category breakdown
        self.log("\n📈 Results by Category:")
        self.log("-" * 40)
        for category, stats in sorted(categories.items()):
            cat_pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status_icon = "✅" if cat_pass_rate == 100 else "⚠️" if cat_pass_rate >= 50 else "❌"
            self.log(f"{status_icon} {category:15} {stats['passed']:3}/{stats['total']:3} ({cat_pass_rate:.0f}%)")
        
        # List failed tests
        if failed > 0:
            self.log("\n❌ Failed Tests:")
            self.log("-" * 40)
            for result in self.results:
                if result.status == "FAIL":
                    self.log(f"  {result.method:6} {result.endpoint}")
                    if result.error:
                        self.log(f"         Error: {result.error}")
        
        # Save JSON report
        report_data = {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "pass_rate": pass_rate,
                "avg_response_time": avg_response_time,
                "duration": (datetime.now() - self.start_time).total_seconds(),
                "timestamp": datetime.now().isoformat()
            },
            "categories": categories,
            "results": [asdict(r) for r in self.results]
        }
        
        with open("api_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        self.log("\n📄 Detailed report saved to: api_test_report.json")
        
        # Create markdown summary
        self.create_markdown_summary(report_data)
        
    def create_markdown_summary(self, report_data):
        """Create a markdown summary of test results"""
        summary = f"""# DexAgents API Test Report

## 📊 Summary
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Tests**: {report_data['summary']['total']}
- **Passed**: {report_data['summary']['passed']} ({report_data['summary']['pass_rate']:.1f}%)
- **Failed**: {report_data['summary']['failed']}
- **Average Response Time**: {report_data['summary']['avg_response_time']:.1f}ms
- **Test Duration**: {report_data['summary']['duration']:.1f}s

## 📈 Results by Category

| Category | Passed | Total | Pass Rate |
|----------|--------|-------|-----------|
"""
        
        for category, stats in sorted(report_data['categories'].items()):
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            summary += f"| {category} | {stats['passed']} | {stats['total']} | {pass_rate:.0f}% |\n"
        
        # Add failed tests if any
        failed_tests = [r for r in report_data['results'] if r['status'] == 'FAIL']
        if failed_tests:
            summary += "\n## ❌ Failed Tests\n\n"
            for test in failed_tests:
                summary += f"- **{test['method']} {test['endpoint']}**\n"
                if test['error']:
                    summary += f"  - Error: {test['error']}\n"
        
        with open("api_test_summary.md", "w") as f:
            f.write(summary)
        self.log("📄 Markdown summary saved to: api_test_summary.md")

def main():
    """Main entry point"""
    tester = APITester()
    
    try:
        tester.run_tests()
        
        # Exit with appropriate code
        failed = sum(1 for r in tester.results if r.status == "FAIL")
        sys.exit(0 if failed == 0 else 1)
        
    except KeyboardInterrupt:
        tester.log("\n⚠️ Test interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        tester.log(f"\n❌ Fatal error: {str(e)}", "ERROR")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()