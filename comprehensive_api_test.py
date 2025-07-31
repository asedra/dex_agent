#!/usr/bin/env python3
"""
Comprehensive API Test Suite for DexAgents Platform
Tests all major API endpoints with proper error handling
"""

import json
import time
import requests
from datetime import datetime
import sys

class ComprehensiveAPITest:
    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        
    def log_test(self, test_name, status, message="", details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if details:
            result["details"] = details
            
        self.test_results["tests"].append(result)
        self.test_results["summary"]["total"] += 1
        self.test_results["summary"][status.lower()] += 1
        
        status_emoji = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⏭️"}
        print(f"{status_emoji.get(status, '❓')} {test_name}: {message}")
        
        if details and status == "FAILED":
            print(f"  Details: {json.dumps(details, indent=2)}")
    
    def test_health_endpoint(self):
        """Test system health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/system/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", "PASSED", "System is healthy")
                    return True
                else:
                    self.log_test("Health Check", "FAILED", f"Unhealthy status: {data}")
                    return False
            else:
                self.log_test("Health Check", "FAILED", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check", "FAILED", f"Exception: {str(e)}")
            return False
    
    def test_login_endpoint(self):
        """Test user authentication"""
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Login", "PASSED", f"Login successful for user: {data['user'].get('username', 'unknown')}")
                    return True
                else:
                    self.log_test("User Login", "FAILED", f"Missing token or user data: {data}")
                    return False
            else:
                self.log_test("User Login", "FAILED", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Login", "FAILED", f"Exception: {str(e)}")
            return False

    def test_me_endpoint(self):
        """Test token validation via /me endpoint"""
        if not self.auth_token:
            self.log_test("Token Validation", "SKIPPED", "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auth/me", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "username" in data:
                    self.log_test("Token Validation", "PASSED", f"Token valid for user: {data['username']}")
                    return True
                else:
                    self.log_test("Token Validation", "FAILED", f"Invalid user data: {data}")
                    return False
            else:
                self.log_test("Token Validation", "FAILED", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Token Validation", "FAILED", f"Exception: {str(e)}")
            return False

    def test_agents_endpoint(self):
        """Test agents listing"""
        if not self.auth_token:
            self.log_test("Agents Listing", "SKIPPED", "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/api/v1/agents", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    agent_count = len(data)
                    self.log_test("Agents Listing", "PASSED", f"Retrieved {agent_count} agents")
                    
                    # Test agent details if agents exist
                    if agent_count > 0:
                        first_agent = data[0]
                        required_fields = ["id", "hostname", "status"]
                        missing_fields = [field for field in required_fields if field not in first_agent]
                        
                        if not missing_fields:
                            self.log_test("Agent Data Structure", "PASSED", "Agent data structure is valid")
                        else:
                            self.log_test("Agent Data Structure", "FAILED", f"Missing fields: {missing_fields}")
                    
                    return True
                else:
                    self.log_test("Agents Listing", "FAILED", f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Agents Listing", "FAILED", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Agents Listing", "FAILED", f"Exception: {str(e)}")
            return False

    def test_commands_endpoint(self):
        """Test commands listing"""
        if not self.auth_token:
            self.log_test("Commands Listing", "SKIPPED", "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/api/v1/commands/saved", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    command_count = len(data)
                    self.log_test("Commands Listing", "PASSED", f"Retrieved {command_count} commands")
                    
                    # Test command structure if commands exist
                    if command_count > 0:
                        first_command = data[0]
                        required_fields = ["id", "name", "command"]
                        missing_fields = [field for field in required_fields if field not in first_command]
                        
                        if not missing_fields:
                            self.log_test("Command Data Structure", "PASSED", "Command data structure is valid")
                        else:
                            self.log_test("Command Data Structure", "FAILED", f"Missing fields: {missing_fields}")
                    
                    return True
                else:
                    self.log_test("Commands Listing", "FAILED", f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Commands Listing", "FAILED", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Commands Listing", "FAILED", f"Exception: {str(e)}")
            return False

    def test_command_execution(self):
        """Test command execution API"""
        if not self.auth_token:
            self.log_test("Command Execution", "SKIPPED", "No auth token available")
            return False
            
        try:
            # First get available agents
            agents_response = self.session.get(f"{self.base_url}/api/v1/agents", timeout=10)
            
            if agents_response.status_code != 200:
                self.log_test("Command Execution", "SKIPPED", "Cannot retrieve agents for testing")
                return False
                
            agents = agents_response.json()
            connected_agents = [agent for agent in agents if agent.get('is_connected', False)]
            
            if not connected_agents:
                self.log_test("Command Execution", "SKIPPED", "No connected agents available for testing")
                return True  # This is not a failure, just no agents to test with
            
            # Test with first connected agent
            test_agent = connected_agents[0]
            agent_id = test_agent["id"]
            
            # Simple PowerShell command that should work
            test_command = {
                "command": "Get-Date | ConvertTo-Json",
                "timeout": 30
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/commands/agent/{agent_id}/execute",
                json=test_command,
                timeout=35
            )
            
            if response.status_code == 200:
                self.log_test("Command Execution", "PASSED", f"Command sent to agent {agent_id}")
                return True
            else:
                # Command execution via WebSocket might not return immediate results
                # This is expected behavior, so we'll consider it a pass if we get a proper HTTP response
                if response.status_code in [202, 204]:  # Accepted or No Content
                    self.log_test("Command Execution", "PASSED", f"Command accepted by agent {agent_id}")
                    return True
                else:
                    self.log_test("Command Execution", "FAILED", f"HTTP {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log_test("Command Execution", "FAILED", f"Exception: {str(e)}")
            return False

    def test_settings_endpoint(self):
        """Test settings API"""
        if not self.auth_token:
            self.log_test("Settings API", "SKIPPED", "No auth token available")
            return False
            
        try:
            # Test GET settings
            response = self.session.get(f"{self.base_url}/api/v1/settings", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Settings Retrieval", "PASSED", f"Retrieved {len(data)} settings")
                    return True
                else:
                    self.log_test("Settings API", "FAILED", f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Settings API", "FAILED", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Settings API", "FAILED", f"Exception: {str(e)}")
            return False

    def test_unauthorized_access(self):
        """Test authorization controls"""
        try:
            # Create session without auth token
            unauth_session = requests.Session()
            
            # Test accessing protected endpoint without token
            response = unauth_session.get(f"{self.base_url}/api/v1/agents", timeout=10)
            
            if response.status_code == 401:
                self.log_test("Authorization Control", "PASSED", "Unauthorized access properly denied")
                return True
            else:
                self.log_test("Authorization Control", "FAILED", f"Expected 401, got HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Authorization Control", "FAILED", f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print(f"\n🚀 Starting Comprehensive API Tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Test order matters - login must come early
        tests = [
            self.test_health_endpoint,
            self.test_unauthorized_access,
            self.test_login_endpoint,
            self.test_me_endpoint,
            self.test_agents_endpoint,
            self.test_commands_endpoint,
            self.test_command_execution,
            self.test_settings_endpoint,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "FAILED", f"Test crashed: {str(e)}")
            time.sleep(0.5)  # Small delay between tests
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        summary = self.test_results["summary"]
        print(f"Total Tests: {summary['total']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        
        success_rate = (summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Save detailed results
        with open('api_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: api_test_results.json")
        
        # Return overall success
        return summary['failed'] == 0

def main():
    """Main test execution"""
    tester = ComprehensiveAPITest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All API tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some API tests failed. Check the results above.")
        sys.exit(1)

if __name__ == "__main__":
    main()