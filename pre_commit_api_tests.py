#!/usr/bin/env python3
"""
Comprehensive API test suite for pre-commit validation
Tests login, token validation, agent functionality, and command execution
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

class PreCommitAPITester:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.token = None
        self.headers = {}
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", details: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"    Details: {details}")
    
    def test_health_endpoint(self) -> bool:
        """Test system health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/system/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, "System is healthy")
                    return True
                else:
                    self.log_test("Health Check", False, f"System not healthy: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_login(self, username: str = "admin", password: str = "admin123") -> bool:
        """Test user login and token generation"""
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                
                if self.token:
                    self.headers = {"Authorization": f"Bearer {self.token}"}
                    self.log_test("Login", True, f"Successfully logged in as {username}")
                    
                    # Validate token structure
                    if "." in self.token:  # JWT should have dots
                        self.log_test("Token Format", True, "JWT token format is valid")
                        return True
                    else:
                        self.log_test("Token Format", False, "Invalid token format")
                        return False
                else:
                    self.log_test("Login", False, "No access token in response")
                    return False
            else:
                error_msg = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                self.log_test("Login", False, error_msg)
                return False
                
        except Exception as e:
            self.log_test("Login", False, f"Login error: {str(e)}")
            return False
    
    def test_token_validation(self) -> bool:
        """Test token validation with /me endpoint"""
        if not self.token:
            self.log_test("Token Validation", False, "No token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                if user_data.get("username"):
                    self.log_test("Token Validation", True, f"Token valid for user: {user_data['username']}")
                    return True
                else:
                    self.log_test("Token Validation", False, "Invalid user data in response")
                    return False
            else:
                self.log_test("Token Validation", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Token Validation", False, f"Token validation error: {str(e)}")
            return False
    
    def test_agents_endpoint(self) -> bool:
        """Test agents list endpoint"""
        if not self.token:
            self.log_test("Agents List", False, "No token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/agents/",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                agents = response.json()
                if isinstance(agents, list):
                    self.log_test("Agents List", True, f"Retrieved {len(agents)} agents")
                    return True
                else:
                    self.log_test("Agents List", False, "Response is not a list")
                    return False
            else:
                self.log_test("Agents List", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Agents List", False, f"Agents endpoint error: {str(e)}")
            return False
    
    def test_agent_registration(self) -> Optional[str]:
        """Test agent registration and return agent ID"""
        if not self.token:
            self.log_test("Agent Registration", False, "No token available")
            return None
            
        try:
            test_agent = {
                "hostname": f"test-agent-{int(time.time())}",
                "ip": "192.168.1.999",
                "os": "Windows 11 Test",
                "version": "10.0.22000",
                "tags": ["test", "pre-commit"]
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/agents/register",
                json=test_agent,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                agent_data = response.json()
                agent_id = agent_data.get("id")
                if agent_id:
                    self.log_test("Agent Registration", True, f"Registered agent: {agent_id}")
                    return agent_id
                else:
                    self.log_test("Agent Registration", False, "No agent ID in response")
                    return None
            else:
                error_msg = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                self.log_test("Agent Registration", False, error_msg)
                return None
                
        except Exception as e:
            self.log_test("Agent Registration", False, f"Registration error: {str(e)}")
            return None
    
    def test_agent_command_execution(self, agent_id: str) -> bool:
        """Test command execution on agent (will fail if no WebSocket agent connected)"""
        if not self.token or not agent_id:
            self.log_test("Agent Command", False, "No token or agent ID available")
            return False
            
        try:
            test_command = {
                "command": "echo 'Hello from DexAgents API Test'",
                "timeout": 30
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/agents/{agent_id}/command",
                json=test_command,
                headers=self.headers,
                timeout=35
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_test("Agent Command", True, f"Command executed successfully: {result.get('output', '')[:50]}...")
                    return True
                else:
                    self.log_test("Agent Command", False, f"Command failed: {result.get('error', 'Unknown error')}")
                    return False
            elif response.status_code == 400:
                # Agent not connected - this is expected in pre-commit tests
                self.log_test("Agent Command", True, "Agent not connected (expected in testing)", "No WebSocket agent running")
                return True
            else:
                error_msg = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                self.log_test("Agent Command", False, error_msg)
                return False
                
        except Exception as e:
            self.log_test("Agent Command", False, f"Command execution error: {str(e)}")
            return False
    
    def test_commands_endpoint(self) -> bool:
        """Test PowerShell commands library endpoint"""
        if not self.token:
            self.log_test("Commands Library", False, "No token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/commands/saved",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                commands = response.json()
                if isinstance(commands, list):
                    self.log_test("Commands Library", True, f"Retrieved {len(commands)} saved commands")
                    return True
                else:
                    self.log_test("Commands Library", False, "Response is not a list")
                    return False
            else:
                self.log_test("Commands Library", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Commands Library", False, f"Commands endpoint error: {str(e)}")
            return False
    
    def test_unauthorized_access(self) -> bool:
        """Test that protected endpoints require authentication"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/agents/", timeout=10)
            
            if response.status_code == 401:
                self.log_test("Unauthorized Access", True, "Protected endpoint correctly requires authentication")
                return True
            else:
                self.log_test("Unauthorized Access", False, f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Unauthorized Access", False, f"Unauthorized test error: {str(e)}")
            return False
    
    def cleanup_test_agent(self, agent_id: str) -> bool:
        """Clean up test agent"""
        if not self.token or not agent_id:
            return False
            
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/agents/{agent_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Agent Cleanup", True, f"Test agent {agent_id} deleted")
                return True
            else:
                self.log_test("Agent Cleanup", False, f"Failed to delete test agent: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Agent Cleanup", False, f"Cleanup error: {str(e)}")
            return False
    
    def run_full_test_suite(self) -> bool:
        """Run complete API test suite"""
        print("🚀 Starting Pre-Commit API Test Suite")
        print("=" * 50)
        
        # Test sequence
        tests_passed = 0
        total_tests = 0
        
        # Basic connectivity and health
        total_tests += 1
        if self.test_health_endpoint():
            tests_passed += 1
        
        # Authentication tests
        total_tests += 1
        if self.test_unauthorized_access():
            tests_passed += 1
            
        total_tests += 1
        if self.test_login():
            tests_passed += 1
        else:
            print("❌ Login failed - stopping tests")
            return False
            
        total_tests += 1
        if self.test_token_validation():
            tests_passed += 1
        
        # API endpoint tests
        total_tests += 1
        if self.test_agents_endpoint():
            tests_passed += 1
            
        total_tests += 1
        if self.test_commands_endpoint():
            tests_passed += 1
        
        # Agent functionality tests
        total_tests += 1
        agent_id = self.test_agent_registration()
        if agent_id:
            tests_passed += 1
            
            # Test command execution (expected to fail gracefully)
            total_tests += 1
            if self.test_agent_command_execution(agent_id):
                tests_passed += 1
                
            # Cleanup
            self.cleanup_test_agent(agent_id)
        
        # Results summary
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("✅ All API tests passed! Ready for commit.")
            return True
        else:
            print(f"❌ {total_tests - tests_passed} tests failed. Fix issues before commit.")
            return False
    
    def save_results(self, filename: str = "api_test_results.json"):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.test_results),
                "passed_tests": len([r for r in self.test_results if r["success"]]),
                "failed_tests": len([r for r in self.test_results if not r["success"]]),
                "results": self.test_results
            }, f, indent=2)

def main():
    """Main function to run API tests"""
    # Get base URL from environment or use default
    base_url = os.getenv("API_BASE_URL", "http://localhost:8080")
    
    print(f"Testing API at: {base_url}")
    
    tester = PreCommitAPITester(base_url)
    
    success = tester.run_full_test_suite()
    
    # Save results
    tester.save_results()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()