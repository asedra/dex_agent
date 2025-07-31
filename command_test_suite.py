#!/usr/bin/env python3
"""
Comprehensive PowerShell Command Test Suite
Tests all saved commands individually and generates detailed reports
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

class CommandTestSuite:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.token = None
        self.headers = {}
        self.test_results = []
        self.commands = []
        self.test_agent_id = None
        
    def log_test(self, test_name: str, success: bool, message: str = "", details: Any = None, command_info: Dict = None):
        """Log test result with command information"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "command_info": command_info,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"    Details: {details}")
    
    def login(self, username: str = "admin", password: str = "admin123") -> bool:
        """Login and get token"""
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
                    return True
                    
            return False
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False
    
    def get_saved_commands(self) -> bool:
        """Retrieve all saved commands"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/commands/saved",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.commands = response.json()
                print(f"📋 Retrieved {len(self.commands)} saved commands")
                return True
            else:
                print(f"❌ Failed to get commands: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting commands: {str(e)}")
            return False
    
    def create_test_agent(self) -> Optional[str]:
        """Create a test agent for command execution testing"""
        try:
            test_agent = {
                "hostname": f"command-test-agent-{int(time.time())}",
                "ip": "192.168.1.998",
                "os": "Windows 11 Command Test",
                "version": "10.0.22000",
                "tags": ["test", "command-testing"]
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
                    self.test_agent_id = agent_id
                    print(f"🤖 Created test agent: {agent_id}")
                    return agent_id
                    
        except Exception as e:
            print(f"❌ Error creating test agent: {str(e)}")
        
        return None
    
    def test_command_validation(self, command: Dict) -> Dict:
        """Test command structure and metadata validation"""
        issues = []
        warnings = []
        
        # Required fields
        required_fields = ['id', 'name', 'command', 'category']
        for field in required_fields:
            if not command.get(field):
                issues.append(f"Missing required field: {field}")
        
        # Command content validation
        cmd_text = command.get('command', '')
        if not cmd_text.strip():
            issues.append("Empty command text")
        
        # PowerShell syntax checks
        if 'ConvertTo-Json' not in cmd_text:
            warnings.append("Command doesn't output JSON (recommended for API consistency)")
        
        # Parameter validation
        parameters = command.get('parameters', [])
        if '$' in cmd_text and not parameters:
            # Check for variables in command
            import re
            variables = re.findall(r'\$(\w+)', cmd_text)
            if variables:
                ps_builtins = {'null', 'true', 'false', 'this', 'input', 'matches', 'lastexitcode', 'error'}
                custom_vars = [v for v in variables if v.lower() not in ps_builtins]
                if custom_vars:
                    warnings.append(f"Command contains variables {custom_vars} but no parameters defined")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def test_command_execution_api(self, command: Dict) -> Dict:
        """Test command execution via API (will fail gracefully if no agent connected)"""
        try:
            # Test with execute endpoint (local PowerShell)
            execution_data = {
                "command": command['command'],
                "timeout": 30
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/commands/execute",
                json=execution_data,
                headers=self.headers,
                timeout=35
            )
            
            result_data = {
                "api_accessible": True,
                "status_code": response.status_code,
                "execution_attempted": False,
                "execution_successful": False,
                "response_data": None,
                "error": None
            }
            
            if response.status_code == 200:
                result_data["execution_attempted"] = True
                try:
                    response_json = response.json()
                    result_data["response_data"] = response_json
                    result_data["execution_successful"] = response_json.get("success", False)
                except:
                    result_data["error"] = "Invalid JSON response"
            else:
                try:
                    error_data = response.json()
                    result_data["error"] = error_data.get("detail", f"HTTP {response.status_code}")
                except:
                    result_data["error"] = f"HTTP {response.status_code}"
                    
            return result_data
            
        except Exception as e:
            return {
                "api_accessible": False,
                "error": str(e),
                "execution_attempted": False,
                "execution_successful": False
            }
    
    def test_saved_command_execution_api(self, command: Dict) -> Dict:
        """Test saved command execution via API"""
        if not self.test_agent_id:
            return {
                "api_accessible": False,
                "error": "No test agent available",
                "execution_attempted": False
            }
            
        try:
            execution_data = {
                "agent_ids": [self.test_agent_id],
                "parameters": {},
                "timeout": 30
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/commands/saved/{command['id']}/execute",
                json=execution_data,
                headers=self.headers,
                timeout=35
            )
            
            result_data = {
                "api_accessible": True,
                "status_code": response.status_code,
                "execution_attempted": False,
                "response_data": None,
                "error": None
            }
            
            if response.status_code == 200:
                result_data["execution_attempted"] = True
                try:
                    response_json = response.json()
                    result_data["response_data"] = response_json
                except:
                    result_data["error"] = "Invalid JSON response"
            else:
                try:
                    error_data = response.json()
                    result_data["error"] = error_data.get("detail", f"HTTP {response.status_code}")
                except:
                    result_data["error"] = f"HTTP {response.status_code}"
                    
            return result_data
            
        except Exception as e:
            return {
                "api_accessible": False,
                "error": str(e),
                "execution_attempted": False
            }
    
    def test_individual_command(self, command: Dict) -> Dict:
        """Comprehensive test of individual command"""
        print(f"\n🔍 Testing Command: {command.get('name', 'Unknown')}")
        print(f"   ID: {command.get('id', 'N/A')}")
        print(f"   Category: {command.get('category', 'N/A')}")
        
        test_result = {
            "command_id": command.get('id'),
            "command_name": command.get('name'),
            "command_category": command.get('category'),
            "validation": {},
            "api_execution": {},
            "saved_execution": {},
            "overall_status": "unknown"
        }
        
        # 1. Validate command structure
        validation_result = self.test_command_validation(command)
        test_result["validation"] = validation_result
        
        if validation_result["valid"]:
            self.log_test(
                f"Command Validation - {command['name']}", 
                True, 
                "Command structure is valid",
                validation_result["warnings"] if validation_result["warnings"] else None,
                command
            )
        else:
            self.log_test(
                f"Command Validation - {command['name']}", 
                False, 
                "Command validation failed",
                validation_result["issues"],
                command
            )
        
        # 2. Test API execution endpoint
        api_result = self.test_command_execution_api(command)
        test_result["api_execution"] = api_result
        
        if api_result["api_accessible"]:
            if api_result["execution_attempted"]:
                self.log_test(
                    f"API Execution - {command['name']}", 
                    api_result["execution_successful"], 
                    "Command executed via API" if api_result["execution_successful"] else f"Execution failed: {api_result.get('error', 'Unknown error')}",
                    api_result.get("response_data"),
                    command
                )
            else:
                self.log_test(
                    f"API Execution - {command['name']}", 
                    False, 
                    f"API call failed: {api_result.get('error', 'Unknown error')}",
                    api_result,
                    command
                )
        else:
            self.log_test(
                f"API Execution - {command['name']}", 
                False, 
                f"API not accessible: {api_result.get('error', 'Unknown error')}",
                api_result,
                command
            )
        
        # 3. Test saved command execution endpoint
        saved_result = self.test_saved_command_execution_api(command)
        test_result["saved_execution"] = saved_result
        
        if saved_result["api_accessible"]:
            if saved_result["execution_attempted"]:
                self.log_test(
                    f"Saved Command Execution - {command['name']}", 
                    True, 
                    "Saved command API call successful",
                    saved_result.get("response_data"),
                    command
                )
            else:
                self.log_test(
                    f"Saved Command Execution - {command['name']}", 
                    False, 
                    f"Saved command API failed: {saved_result.get('error', 'Unknown error')}",
                    saved_result,
                    command
                )
        else:
            self.log_test(
                f"Saved Command Execution - {command['name']}", 
                False, 
                f"Saved command API not accessible: {saved_result.get('error', 'Unknown error')}",
                saved_result,
                command
            )
        
        # Determine overall status
        validation_ok = validation_result["valid"]
        api_ok = api_result["api_accessible"]
        saved_ok = saved_result["api_accessible"]
        
        if validation_ok and api_ok and saved_ok:
            test_result["overall_status"] = "excellent"
        elif validation_ok and (api_ok or saved_ok):
            test_result["overall_status"] = "good"
        elif validation_ok:
            test_result["overall_status"] = "acceptable"
        else:
            test_result["overall_status"] = "poor"
        
        return test_result
    
    def cleanup_test_agent(self):
        """Clean up test agent"""
        if self.test_agent_id:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/v1/agents/{self.test_agent_id}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"🧹 Cleaned up test agent: {self.test_agent_id}")
                else:
                    print(f"⚠️ Failed to cleanup test agent: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️ Error cleaning up test agent: {str(e)}")
    
    def run_comprehensive_command_tests(self) -> Dict:
        """Run comprehensive tests on all saved commands"""
        print("🚀 Starting Comprehensive Command Test Suite")
        print("=" * 60)
        
        # Login
        if not self.login():
            print("❌ Login failed - cannot continue")
            return {"success": False, "error": "Login failed"}
        
        # Get commands
        if not self.get_saved_commands():
            print("❌ Failed to retrieve commands - cannot continue")
            return {"success": False, "error": "Failed to retrieve commands"}
        
        # Create test agent
        self.create_test_agent()
        
        # Test each command
        detailed_results = []
        for command in self.commands:
            try:
                result = self.test_individual_command(command)
                detailed_results.append(result)
            except Exception as e:
                print(f"❌ Error testing command {command.get('name', 'Unknown')}: {str(e)}")
                detailed_results.append({
                    "command_id": command.get('id'),
                    "command_name": command.get('name'),
                    "error": str(e),
                    "overall_status": "error"
                })
        
        # Cleanup
        self.cleanup_test_agent()
        
        # Generate summary
        total_commands = len(detailed_results)
        excellent_commands = len([r for r in detailed_results if r.get("overall_status") == "excellent"])
        good_commands = len([r for r in detailed_results if r.get("overall_status") == "good"])
        acceptable_commands = len([r for r in detailed_results if r.get("overall_status") == "acceptable"])
        poor_commands = len([r for r in detailed_results if r.get("overall_status") == "poor"])
        error_commands = len([r for r in detailed_results if r.get("overall_status") == "error"])
        
        print("\n" + "=" * 60)
        print(f"📊 Command Test Summary:")
        print(f"   Total Commands: {total_commands}")
        print(f"   🌟 Excellent: {excellent_commands}")
        print(f"   ✅ Good: {good_commands}")
        print(f"   ⚠️ Acceptable: {acceptable_commands}")
        print(f"   ❌ Poor: {poor_commands}")
        print(f"   💥 Errors: {error_commands}")
        
        summary = {
            "success": True,
            "total_commands": total_commands,
            "excellent_commands": excellent_commands,
            "good_commands": good_commands,
            "acceptable_commands": acceptable_commands,
            "poor_commands": poor_commands,
            "error_commands": error_commands,
            "detailed_results": detailed_results,
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def save_results(self, results: Dict, filename: str = "command_test_results.json"):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"💾 Results saved to {filename}")

def main():
    """Main function to run command tests"""
    base_url = os.getenv("API_BASE_URL", "http://localhost:8080")
    
    print(f"Testing Commands at: {base_url}")
    
    tester = CommandTestSuite(base_url)
    results = tester.run_comprehensive_command_tests()
    
    # Save results
    tester.save_results(results)
    
    # Exit with appropriate code
    if results.get("success"):
        if results.get("error_commands", 0) > 0 or results.get("poor_commands", 0) > 0:
            sys.exit(1)  # Some issues found
        else:
            sys.exit(0)  # All good
    else:
        sys.exit(2)  # Major failure

if __name__ == "__main__":
    main()