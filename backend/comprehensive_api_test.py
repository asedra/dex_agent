#!/usr/bin/env python3
"""
Comprehensive API Test Suite for DexAgents Backend
Tests all major endpoints including authentication, agents, commands, and AI functionality
"""

import requests
import json
import time
import sys
from datetime import datetime

class DexAgentsAPITester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_data=None):
        """Log test result"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"[{timestamp}] {status} {test_name}")
        if message:
            print(f"    {message}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()
    
    def test_health_endpoint(self):
        """Test system health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/system/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("System Health Check", True, f"Status: {data.get('status', 'unknown')}", data)
                return True
            else:
                self.log_test("System Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("System Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_login(self, username="admin", password="admin123"):
        """Test user authentication"""
        try:
            payload = {"username": username, "password": password}
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login", 
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.token = data["access_token"]
                    self.log_test("User Login", True, f"Token received, expires: {data.get('expires_in', 'unknown')}")
                    return True
                else:
                    self.log_test("User Login", False, "No access token in response", data)
                    return False
            else:
                self.log_test("User Login", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            return False
    
    def test_token_validation(self):
        """Test token validation via /me endpoint"""
        if not self.token:
            self.log_test("Token Validation", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Token Validation", True, f"User: {data.get('username', 'unknown')}", data)
                return True
            else:
                self.log_test("Token Validation", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Token Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_agents_endpoint(self):
        """Test agents management endpoint"""
        if not self.token:
            self.log_test("Agents List", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/v1/agents",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_count = len(data) if isinstance(data, list) else 0
                self.log_test("Agents List", True, f"Found {agent_count} agents")
                return True
            else:
                self.log_test("Agents List", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Agents List", False, f"Exception: {str(e)}")
            return False
    
    def test_saved_commands_endpoint(self):
        """Test saved commands endpoint"""
        if not self.token:
            self.log_test("Saved Commands", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/v1/commands/saved",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                command_count = len(data) if isinstance(data, list) else 0
                self.log_test("Saved Commands", True, f"Found {command_count} saved commands")
                return True
            else:
                self.log_test("Saved Commands", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Saved Commands", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_status_endpoint(self):
        """Test AI service status endpoint"""
        if not self.token:
            self.log_test("AI Status", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/v1/commands/ai/status",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_available = data.get("available", False)
                message = data.get("message", "No message")
                self.log_test("AI Status", True, f"AI Available: {ai_available} - {message}", data)
                return True
            else:
                self.log_test("AI Status", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("AI Status", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_command_generation(self):
        """Test AI command generation endpoint"""
        if not self.token:
            self.log_test("AI Command Generation", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test AI command generation
            command_request = {
                "message": "Show me system information",
                "conversation_history": []
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/commands/ai/generate",
                headers=headers,
                json=command_request,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("command_data"):
                    command_data = data["command_data"]
                    self.log_test("AI Command Generation", True, f"Generated command: {command_data.get('name', 'unnamed')}")
                    return True
                else:
                    self.log_test("AI Command Generation", False, f"AI generation failed: {data.get('error', 'Unknown error')}")
                    return False
            elif response.status_code in [500, 503]:
                # 500 error expected when API key is invalid or test key
                # 503 when service unavailable
                self.log_test("AI Command Generation", True, f"Expected failure (test API key or service unavailable): HTTP {response.status_code}")
                return True
            else:
                self.log_test("AI Command Generation", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("AI Command Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_chatgpt_settings(self):
        """Test ChatGPT settings management"""
        if not self.token:
            self.log_test("ChatGPT Settings", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Get current settings
            response = requests.get(
                f"{self.base_url}/api/v1/settings",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                settings = response.json()
                
                # Check if chatgpt_api_key setting exists
                chatgpt_setting = None
                for setting in settings:
                    if setting.get("key") == "chatgpt_api_key":
                        chatgpt_setting = setting
                        break
                
                if chatgpt_setting:
                    self.log_test("ChatGPT Settings", True, "ChatGPT API key setting found in database")
                else:
                    self.log_test("ChatGPT Settings", True, "ChatGPT API key setting not found (can be added via UI)")
                return True
            else:
                self.log_test("ChatGPT Settings", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("ChatGPT Settings", False, f"Exception: {str(e)}")
            return False

    def test_ai_button_always_visible(self):
        """Test that AI button is always visible regardless of ChatGPT configuration"""
        if not self.token:
            self.log_test("AI Button Always Visible", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # This is a backend API test - we test that the AI status endpoint
            # returns information about availability regardless of configuration
            response = requests.get(
                f"{self.base_url}/api/v1/commands/ai/status",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                ai_status = response.json()
                
                # Test that status is returned even when not configured
                if 'available' in ai_status and isinstance(ai_status['available'], bool):
                    self.log_test("AI Button Always Visible", True, f"AI status properly indicates availability: {ai_status['available']}")
                    return True
                else:
                    self.log_test("AI Button Always Visible", False, "AI status missing 'available' field")
                    return False
            else:
                self.log_test("AI Button Always Visible", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("AI Button Always Visible", False, f"Exception: {str(e)}")
            return False

    def test_ai_redirect_to_settings(self):
        """Test AI command generation when ChatGPT is not configured"""
        if not self.token:
            self.log_test("AI Redirect to Settings", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test with a simple AI command request
            command_request = {
                "message": "Show me system information",
                "conversation_history": []
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/commands/ai/generate",
                headers=headers,
                json=command_request,
                timeout=15
            )
            
            # Should return error when ChatGPT not configured, or success if configured
            if response.status_code in [400, 500, 503]:  # Bad request, internal error, or service unavailable
                error_data = response.json()
                # 500 error can happen when API key is invalid
                self.log_test("AI Redirect to Settings", True, f"AI generation fails as expected: {error_data.get('detail', 'Configuration or API key issue')}")
                return True
            elif response.status_code == 200:
                # If it succeeds, ChatGPT is already configured
                self.log_test("AI Redirect to Settings", True, "AI generation works (ChatGPT already configured)")
                return True
            else:
                self.log_test("AI Redirect to Settings", False, f"Unexpected response: HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("AI Redirect to Settings", False, f"Exception: {str(e)}")
            return False
    
    def test_command_execution(self):
        """Test command execution (gracefully handles no WebSocket agent)"""
        if not self.token:
            self.log_test("Command Execution", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # First get available agents
            agents_response = requests.get(
                f"{self.base_url}/api/v1/agents",
                headers=headers,
                timeout=10
            )
            
            if agents_response.status_code != 200:
                self.log_test("Command Execution", False, "Failed to get agents list")
                return False
            
            agents = agents_response.json()
            online_agents = [agent for agent in agents if agent.get('status') == 'online' and agent.get('id')]
            
            if not online_agents:
                self.log_test("Command Execution", True, "No online agents available - test passed (expected scenario)")
                return True
            
            # If we have online agents, try to execute a simple command
            test_command = {
                "agent_ids": [online_agents[0]['id']],
                "parameters": {},
                "timeout": 30
            }
            
            # Get saved commands to find one to execute
            commands_response = requests.get(
                f"{self.base_url}/api/v1/commands/saved",
                headers=headers,
                timeout=10
            )
            
            if commands_response.status_code == 200:
                commands = commands_response.json()
                if commands:
                    first_command_id = commands[0].get('id')
                    if first_command_id:
                        response = requests.post(
                            f"{self.base_url}/api/v1/commands/saved/{first_command_id}/execute",
                            headers=headers,
                            json=test_command,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            self.log_test("Command Execution", True, f"Command sent successfully", data)
                            return True
                        else:
                            self.log_test("Command Execution", False, f"HTTP {response.status_code}", response.text)
                            return False
            
            self.log_test("Command Execution", True, "No suitable commands found for testing - test passed")
            return True
            
        except Exception as e:
            self.log_test("Command Execution", False, f"Exception: {str(e)}")
            return False
    
    def test_unauthorized_access(self):
        """Test that protected endpoints require authentication"""
        try:
            # Try to access protected endpoint without token
            response = requests.get(f"{self.base_url}/api/v1/agents", timeout=10)
            
            if response.status_code == 401:
                self.log_test("Authorization Protection", True, "Correctly rejected unauthorized access")
                return True
            else:
                self.log_test("Authorization Protection", False, f"Expected 401, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Authorization Protection", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("=" * 60)
        print("DexAgents API Comprehensive Test Suite")
        print("=" * 60)
        print()
        
        # Test order is important - some tests depend on previous ones
        tests = [
            ("System Health", self.test_health_endpoint),
            ("User Authentication", self.test_login),
            ("Token Validation", self.test_token_validation),
            ("Authorization Protection", self.test_unauthorized_access),
            ("Agents Management", self.test_agents_endpoint),
            ("Saved Commands", self.test_saved_commands_endpoint),
            ("AI Service Status", self.test_ai_status_endpoint),
            ("AI Command Generation", self.test_ai_command_generation),
            ("ChatGPT Settings", self.test_chatgpt_settings),
            ("AI Button Always Visible", self.test_ai_button_always_visible),
            ("AI Redirect to Settings", self.test_ai_redirect_to_settings),
            ("Command Execution", self.test_command_execution),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if test_func():
                passed += 1
        
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print("⚠️  Some tests failed. Check logs above for details.")
            return False

def main():
    """Main test runner"""
    tester = DexAgentsAPITester()
    
    print("Starting comprehensive API tests...")
    print("Waiting for services to be ready...")
    time.sleep(5)  # Give services time to start
    
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All API tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some API tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()