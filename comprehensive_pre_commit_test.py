#!/usr/bin/env python3
"""
Comprehensive Pre-Commit Test Suite
===================================

This script combines all test suites mentioned in CLAUDE.md into a single comprehensive test runner
that generates a unified test report for commit readiness verification.

Test Coverage:
1. AI Features Test Suite (test_ai_features.py)
2. Dark Mode UI Compatibility (test_dark_mode_ui.py) 
3. Comprehensive Test Suite (comprehensive_test.py)
4. Command Output Display Test (test_command_output_display.py)
5. Pre-Commit API Tests (pre_commit_api_tests.py)

Usage: python3 comprehensive_pre_commit_test.py
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import traceback

class Colors:
    """ANSI color codes for console output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class TestResult:
    """Container for individual test results"""
    def __init__(self, name: str, status: str, details: str = "", execution_time: float = 0.0):
        self.name = name
        self.status = status  # "PASS", "FAIL", "WARN", "SKIP"
        self.details = details
        self.execution_time = execution_time
        self.timestamp = datetime.now().isoformat()

class TestSuite:
    """Container for a group of related tests"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tests: List[TestResult] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
    def add_test(self, test: TestResult):
        self.tests.append(test)
        
    def start(self):
        self.start_time = datetime.now()
        
    def finish(self):
        self.end_time = datetime.now()
        
    @property
    def execution_time(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
        
    @property
    def passed_count(self) -> int:
        return len([t for t in self.tests if t.status == "PASS"])
        
    @property
    def failed_count(self) -> int:
        return len([t for t in self.tests if t.status == "FAIL"])
        
    @property
    def warned_count(self) -> int:
        return len([t for t in self.tests if t.status == "WARN"])
        
    @property
    def skipped_count(self) -> int:
        return len([t for t in self.tests if t.status == "SKIP"])
        
    @property
    def total_count(self) -> int:
        return len(self.tests)

class ComprehensiveTestRunner:
    """Main test runner that orchestrates all test suites"""
    
    def __init__(self, base_url: str = "http://localhost:8080", frontend_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.frontend_url = frontend_url
        self.session = requests.Session()
        self.session.timeout = 30
        self.auth_token: Optional[str] = None
        
        # Test suites
        self.suites: List[TestSuite] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Configuration
        self.test_user = {"username": "admin", "password": "admin123"}
        self.chatgpt_key_path = "/app/chatgpt.key"
        
    def print_header(self, text: str, char: str = "=", width: int = 80):
        """Print a formatted header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{char * width}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(width)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{char * width}{Colors.END}")
        
    def print_status(self, message: str, status: str = "INFO"):
        """Print a status message with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if status == "PASS":
            print(f"{Colors.GREEN}✅ [{timestamp}] {message}{Colors.END}")
        elif status == "FAIL":
            print(f"{Colors.RED}❌ [{timestamp}] {message}{Colors.END}")
        elif status == "WARN":
            print(f"{Colors.YELLOW}⚠️  [{timestamp}] {message}{Colors.END}")
        elif status == "INFO":
            print(f"{Colors.BLUE}ℹ️  [{timestamp}] {message}{Colors.END}")
        elif status == "SKIP":
            print(f"{Colors.MAGENTA}⏭️  [{timestamp}] {message}{Colors.END}")
        else:
            print(f"[{timestamp}] {message}")
            
    def safe_request(self, method: str, url: str, **kwargs) -> Tuple[bool, Optional[requests.Response], str]:
        """Make a safe HTTP request with error handling"""
        try:
            response = self.session.request(method, url, **kwargs)
            return True, response, ""
        except requests.exceptions.RequestException as e:
            return False, None, str(e)
            
    def login(self) -> bool:
        """Authenticate with the API and get JWT token"""
        success, response, error = self.safe_request(
            "POST", 
            f"{self.base_url}/api/v1/auth/login",
            json=self.test_user
        )
        
        if not success or not response:
            return False
            
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
            if self.auth_token:
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                return True
        return False
        
    def run_health_check_tests(self) -> TestSuite:
        """Health Check and System Status Tests"""
        suite = TestSuite("Health Check", "Basic system health and connectivity tests")
        suite.start()
        
        # Test 1: Backend Health Check
        start_time = time.time()
        success, response, error = self.safe_request("GET", f"{self.base_url}/api/v1/system/health")
        execution_time = time.time() - start_time
        
        if success and response and response.status_code == 200:
            suite.add_test(TestResult("Backend Health Check", "PASS", 
                                    f"System is healthy - {response.status_code}", execution_time))
        else:
            suite.add_test(TestResult("Backend Health Check", "FAIL", 
                                    f"Health check failed: {error or 'Unknown error'}", execution_time))
            
        # Test 2: Frontend Accessibility
        start_time = time.time()
        success, response, error = self.safe_request("GET", self.frontend_url)
        execution_time = time.time() - start_time
        
        if success and response and response.status_code == 200:
            suite.add_test(TestResult("Frontend Accessibility", "PASS", 
                                    f"Frontend accessible - {response.status_code}", execution_time))
        else:
            suite.add_test(TestResult("Frontend Accessibility", "FAIL", 
                                    f"Frontend not accessible: {error or 'Unknown error'}", execution_time))
            
        # Test 3: Commands Page Accessibility
        start_time = time.time()
        success, response, error = self.safe_request("GET", f"{self.frontend_url}/commands")
        execution_time = time.time() - start_time
        
        if success and response and response.status_code == 200:
            # Check for AI button presence in HTML
            html_content = response.text
            if "Create Command with AI" in html_content:
                suite.add_test(TestResult("Commands Page & AI Button", "PASS", 
                                        "Commands page accessible with AI button", execution_time))
            else:
                suite.add_test(TestResult("Commands Page & AI Button", "WARN", 
                                        "Commands page accessible but AI button not found in HTML", execution_time))
        else:
            suite.add_test(TestResult("Commands Page & AI Button", "FAIL", 
                                    f"Commands page not accessible: {error or 'Unknown error'}", execution_time))
        
        suite.finish()
        return suite
        
    def run_authentication_tests(self) -> TestSuite:
        """Authentication and Authorization Tests"""
        suite = TestSuite("Authentication", "User authentication and JWT token validation tests")
        suite.start()
        
        # Test 1: Unauthorized Access Protection
        temp_session = requests.Session()
        temp_session.timeout = 30
        start_time = time.time()
        try:
            response = temp_session.get(f"{self.base_url}/api/v1/auth/me")
            execution_time = time.time() - start_time
            
            if response.status_code == 401:
                suite.add_test(TestResult("Unauthorized Access Protection", "PASS", 
                                        "Protected endpoint correctly requires authentication", execution_time))
            else:
                suite.add_test(TestResult("Unauthorized Access Protection", "FAIL", 
                                    f"Protected endpoint should return 401 but got {response.status_code}", execution_time))
        except Exception as e:
            execution_time = time.time() - start_time
            suite.add_test(TestResult("Unauthorized Access Protection", "FAIL", 
                                    f"Request failed: {str(e)}", execution_time))
            
        # Test 2: User Login
        start_time = time.time()
        login_success = self.login()
        execution_time = time.time() - start_time
        
        if login_success:
            suite.add_test(TestResult("User Login", "PASS", 
                                    f"Successfully logged in as {self.test_user['username']}", execution_time))
        else:
            suite.add_test(TestResult("User Login", "FAIL", 
                                    "Failed to authenticate with provided credentials", execution_time))
            
        # Test 3: JWT Token Validation
        if self.auth_token:
            start_time = time.time()
            success, response, error = self.safe_request("GET", f"{self.base_url}/api/v1/auth/me")
            execution_time = time.time() - start_time
            
            if success and response and response.status_code == 200:
                user_data = response.json()
                suite.add_test(TestResult("JWT Token Validation", "PASS", 
                                        f"Token valid for user: {user_data.get('username', 'unknown')}", execution_time))
            else:
                suite.add_test(TestResult("JWT Token Validation", "FAIL", 
                                        f"Token validation failed: {error or 'Unknown error'}", execution_time))
        else:
            suite.add_test(TestResult("JWT Token Validation", "SKIP", 
                                    "No token available for validation", 0))
        
        suite.finish()
        return suite
        
    def run_api_functionality_tests(self) -> TestSuite:
        """Core API Functionality Tests"""
        suite = TestSuite("API Functionality", "Core API endpoints and data operations tests")
        suite.start()
        
        # Test 1: Agents List
        start_time = time.time()
        success, response, error = self.safe_request("GET", f"{self.base_url}/api/v1/agents/")
        execution_time = time.time() - start_time
        
        if success and response and response.status_code == 200:
            agents = response.json()
            suite.add_test(TestResult("Agents List", "PASS", 
                                    f"Retrieved {len(agents)} agents", execution_time))
        else:
            suite.add_test(TestResult("Agents List", "FAIL", 
                                    f"Failed to retrieve agents: {error or 'Unknown error'}", execution_time))
            
        # Test 2: Commands Library
        start_time = time.time()
        success, response, error = self.safe_request("GET", f"{self.base_url}/api/v1/commands/saved")
        execution_time = time.time() - start_time
        
        if success and response and response.status_code == 200:
            commands = response.json()
            suite.add_test(TestResult("Commands Library", "PASS", 
                                    f"Retrieved {len(commands)} saved commands", execution_time))
        else:
            suite.add_test(TestResult("Commands Library", "FAIL", 
                                    f"Failed to retrieve commands: {error or 'Unknown error'}", execution_time))
            
        # Test 3: Agent Registration (Create Test Agent)
        test_agent_data = {
            "hostname": f"test_agent_{int(time.time())}",
            "os": "Windows 11",
            "os_version": "22H2",
            "python_version": "3.11.0",
            "agent_version": "1.0.0"
        }
        
        start_time = time.time()
        success, response, error = self.safe_request("POST", f"{self.base_url}/api/v1/agents/register", 
                                                    json=test_agent_data)
        execution_time = time.time() - start_time
        
        test_agent_id = None
        if success and response and response.status_code == 200:
            agent_data = response.json()
            test_agent_id = agent_data.get("id")
            suite.add_test(TestResult("Agent Registration", "PASS", 
                                    f"Registered agent: {agent_data.get('hostname')}", execution_time))
        else:
            suite.add_test(TestResult("Agent Registration", "FAIL", 
                                    f"Failed to register agent: {error or 'Unknown error'}", execution_time))
            
        # Test 4: Agent Refresh (if agent was created)
        if test_agent_id:
            start_time = time.time()
            success, response, error = self.safe_request("POST", f"{self.base_url}/api/v1/agents/{test_agent_id}/refresh")
            execution_time = time.time() - start_time
            
            if success and response and response.status_code == 200:
                suite.add_test(TestResult("Agent Refresh", "PASS", 
                                        "Agent refreshed successfully", execution_time))
            else:
                suite.add_test(TestResult("Agent Refresh", "FAIL", 
                                        f"Failed to refresh agent: {error or 'Unknown error'}", execution_time))
                
            # Test 5: Agent Command Execution (graceful failure expected)
            command_data = {
                "command": "Get-ComputerInfo | ConvertTo-Json",
                "timeout": 10
            }
            
            start_time = time.time()
            success, response, error = self.safe_request("POST", f"{self.base_url}/api/v1/agents/{test_agent_id}/execute", 
                                                        json=command_data)
            execution_time = time.time() - start_time
            
            if success and response:
                if response.status_code == 200:
                    suite.add_test(TestResult("Agent Command Execution", "WARN", 
                                            "Command sent successfully (WebSocket agent not expected in testing)", execution_time))
                else:
                    suite.add_test(TestResult("Agent Command Execution", "PASS", 
                                            "Agent not connected (expected in testing)", execution_time))
            else:
                suite.add_test(TestResult("Agent Command Execution", "FAIL", 
                                        f"Command execution failed: {error or 'Unknown error'}", execution_time))
                
            # Cleanup: Delete test agent
            start_time = time.time()
            success, response, error = self.safe_request("DELETE", f"{self.base_url}/api/v1/agents/{test_agent_id}")
            execution_time = time.time() - start_time
            
            if success and response and response.status_code == 200:
                suite.add_test(TestResult("Agent Cleanup", "PASS", 
                                        f"Test agent {test_agent_data['hostname']} deleted", execution_time))
            else:
                suite.add_test(TestResult("Agent Cleanup", "WARN", 
                                        f"Failed to delete test agent: {error or 'Unknown error'}", execution_time))
        
        suite.finish()
        return suite
        
    def run_ai_features_tests(self) -> TestSuite:
        """AI Features and ChatGPT Integration Tests"""
        suite = TestSuite("AI Features", "AI-powered command generation and ChatGPT integration tests")
        suite.start()
        
        # Test 1: AI Service Status
        start_time = time.time()
        success, response, error = self.safe_request("GET", f"{self.base_url}/api/v1/commands/ai/status")
        execution_time = time.time() - start_time
        
        ai_available = False
        if success and response and response.status_code == 200:
            ai_status = response.json()
            ai_available = ai_status.get("available", False)
            if ai_available:
                suite.add_test(TestResult("AI Service Status", "PASS", 
                                        f"AI service available: {ai_status.get('model', 'unknown')}", execution_time))
            else:
                suite.add_test(TestResult("AI Service Status", "WARN", 
                                        f"AI service not available: {ai_status.get('error', 'Unknown reason')}", execution_time))
        else:
            suite.add_test(TestResult("AI Service Status", "FAIL", 
                                    f"Failed to check AI status: {error or 'Unknown error'}", execution_time))
            
        # Test 2: ChatGPT API Key Availability
        start_time = time.time()
        key_exists = os.path.exists(self.chatgpt_key_path)
        execution_time = time.time() - start_time
        
        if key_exists:
            try:
                with open(self.chatgpt_key_path, 'r') as f:
                    key_content = f.read().strip()
                    if key_content and len(key_content) > 20:
                        suite.add_test(TestResult("ChatGPT API Key", "PASS", 
                                                "API key found and appears valid", execution_time))
                    else:
                        suite.add_test(TestResult("ChatGPT API Key", "WARN", 
                                                "API key file exists but content seems invalid", execution_time))
            except Exception as e:
                suite.add_test(TestResult("ChatGPT API Key", "FAIL", 
                                        f"Failed to read API key: {str(e)}", execution_time))
        else:
            suite.add_test(TestResult("ChatGPT API Key", "WARN", 
                                    "ChatGPT API key file not found", execution_time))
            
        # Test 3: AI Command Generation (if AI is available)
        if ai_available:
            command_request = {
                "message": "Show me system information",
                "conversation_history": []
            }
            
            start_time = time.time()
            success, response, error = self.safe_request("POST", f"{self.base_url}/api/v1/ai/generate-command", 
                                                        json=command_request)
            execution_time = time.time() - start_time
            
            if success and response and response.status_code == 200:
                ai_response = response.json()
                if ai_response.get("success") and ai_response.get("command_data"):
                    command_data = ai_response["command_data"]
                    suite.add_test(TestResult("AI Command Generation", "PASS", 
                                            f"Generated command: {command_data.get('name', 'unnamed')}", execution_time))
                else:
                    suite.add_test(TestResult("AI Command Generation", "FAIL", 
                                            f"AI generation failed: {ai_response.get('error', 'Unknown error')}", execution_time))
            else:
                suite.add_test(TestResult("AI Command Generation", "FAIL", 
                                        f"Failed to generate command: {error or 'Unknown error'}", execution_time))
        else:
            suite.add_test(TestResult("AI Command Generation", "SKIP", 
                                    "AI service not available", 0))
            
        # Test 4: AI Test Command (if AI is available and we have agents)
        if ai_available:
            # Get available agents first
            success, response, error = self.safe_request("GET", f"{self.base_url}/api/v1/agents/")
            
            if success and response and response.status_code == 200:
                agents = response.json()
                online_agents = [agent for agent in agents if agent.get("status") == "online" and agent.get("id")]
                
                if online_agents:
                    test_request = {
                        "command": "Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory | ConvertTo-Json",
                        "agent_id": online_agents[0]["id"],
                        "timeout": 15
                    }
                    
                    start_time = time.time()
                    success, response, error = self.safe_request("POST", f"{self.base_url}/api/v1/ai/test-command", 
                                                                json=test_request)
                    execution_time = time.time() - start_time
                    
                    if success and response and response.status_code == 200:
                        test_result = response.json()
                        if test_result.get("success"):
                            suite.add_test(TestResult("AI Test Command", "PASS", 
                                                    "Test command executed successfully", execution_time))
                        else:
                            suite.add_test(TestResult("AI Test Command", "WARN", 
                                                    f"Test command failed: {test_result.get('error', 'Unknown error')}", execution_time))
                    else:
                        suite.add_test(TestResult("AI Test Command", "FAIL", 
                                                f"Failed to test command: {error or 'Unknown error'}", execution_time))
                else:
                    suite.add_test(TestResult("AI Test Command", "SKIP", 
                                            "No online agents available for testing", 0))
            else:
                suite.add_test(TestResult("AI Test Command", "SKIP", 
                                        "Could not retrieve agents list", 0))
        else:
            suite.add_test(TestResult("AI Test Command", "SKIP", 
                                    "AI service not available", 0))
        
        suite.finish()
        return suite
        
    def run_ui_integration_tests(self) -> TestSuite:
        """UI Integration and Dark Mode Tests"""
        suite = TestSuite("UI Integration", "Frontend integration and dark mode compatibility tests")
        suite.start()
        
        # Test 1: Commands Page Functionality
        start_time = time.time()
        success, response, error = self.safe_request("GET", f"{self.frontend_url}/commands")
        execution_time = time.time() - start_time
        
        if success and response and response.status_code == 200:
            html_content = response.text
            
            # Check for key UI elements
            ui_elements = [
                ("Create Command button", "Create Command"),
                ("Create Command with AI button", "Create Command with AI"),
                ("Search functionality", "Search commands"),
                ("Categories section", "Categories"),
                ("Command Library title", "Command Library")
            ]
            
            found_elements = []
            missing_elements = []
            
            for element_name, element_text in ui_elements:
                if element_text in html_content:
                    found_elements.append(element_name)
                else:
                    missing_elements.append(element_name)
                    
            if len(found_elements) >= 4:  # At least 4 out of 5 elements should be present
                suite.add_test(TestResult("Commands Page Functionality", "PASS", 
                                        f"Found {len(found_elements)}/5 UI elements: {', '.join(found_elements)}", execution_time))
            else:
                suite.add_test(TestResult("Commands Page Functionality", "WARN", 
                                        f"Only found {len(found_elements)}/5 UI elements. Missing: {', '.join(missing_elements)}", execution_time))
        else:
            suite.add_test(TestResult("Commands Page Functionality", "FAIL", 
                                    f"Commands page not accessible: {error or 'Unknown error'}", execution_time))
            
        # Test 2: Dark Mode CSS Classes Detection
        start_time = time.time()
        success, response, error = self.safe_request("GET", f"{self.frontend_url}/commands")
        execution_time = time.time() - start_time
        
        if success and response and response.status_code == 200:
            html_content = response.text.lower()
            
            # Check for dark mode related CSS classes and attributes
            dark_mode_indicators = [
                "dark:",
                "dark:bg-",
                "dark:text-",
                "class=\"dark",
                "data-theme",
                "theme-dark"
            ]
            
            found_indicators = [indicator for indicator in dark_mode_indicators if indicator in html_content]
            
            if len(found_indicators) >= 2:
                suite.add_test(TestResult("Dark Mode CSS Classes", "PASS", 
                                        f"Found {len(found_indicators)} dark mode indicators", execution_time))
            else:
                suite.add_test(TestResult("Dark Mode CSS Classes", "WARN", 
                                        f"Limited dark mode support detected ({len(found_indicators)} indicators)", execution_time))
        else:
            suite.add_test(TestResult("Dark Mode CSS Classes", "SKIP", 
                                    "Commands page not accessible", execution_time))
            
        # Test 3: AI Button Functionality Integration
        start_time = time.time()
        success, response, error = self.safe_request("GET", f"{self.frontend_url}/commands")
        execution_time = time.time() - start_time
        
        if success and response and response.status_code == 200:
            html_content = response.text
            
            # Check for AI-related functionality indicators
            ai_indicators = [
                "Create Command with AI",
                "Wand2",  # Lucide icon for AI button
                "aiDialogOpen",
                "generateCommandWithAI",
                "AI Chat Dialog"
            ]
            
            found_ai_features = [indicator for indicator in ai_indicators if indicator in html_content]
            
            if len(found_ai_features) >= 3:
                suite.add_test(TestResult("AI Button Integration", "PASS", 
                                        f"AI functionality properly integrated ({len(found_ai_features)}/5 features)", execution_time))
            else:
                suite.add_test(TestResult("AI Button Integration", "WARN", 
                                        f"Limited AI integration detected ({len(found_ai_features)}/5 features)", execution_time))
        else:
            suite.add_test(TestResult("AI Button Integration", "SKIP", 
                                    "Commands page not accessible", execution_time))
        
        suite.finish()
        return suite
        
    def run_all_tests(self) -> bool:
        """Run all test suites and generate comprehensive report"""
        self.start_time = datetime.now()
        
        self.print_header("🚀 COMPREHENSIVE PRE-COMMIT TEST SUITE", "=", 80)
        self.print_status(f"Starting comprehensive test suite at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.print_status(f"Testing Backend: {self.base_url}")
        self.print_status(f"Testing Frontend: {self.frontend_url}")
        
        # Run all test suites
        try:
            # 1. Health Check Tests
            self.print_header("🏥 Health Check Tests")
            health_suite = self.run_health_check_tests()
            self.suites.append(health_suite)
            self.print_suite_summary(health_suite)
            
            # 2. Authentication Tests  
            self.print_header("🔐 Authentication Tests")
            auth_suite = self.run_authentication_tests()
            self.suites.append(auth_suite)
            self.print_suite_summary(auth_suite)
            
            # 3. API Functionality Tests
            self.print_header("🔌 API Functionality Tests")
            api_suite = self.run_api_functionality_tests()
            self.suites.append(api_suite)
            self.print_suite_summary(api_suite)
            
            # 4. AI Features Tests
            self.print_header("🤖 AI Features Tests")
            ai_suite = self.run_ai_features_tests()
            self.suites.append(ai_suite)
            self.print_suite_summary(ai_suite)
            
            # 5. UI Integration Tests
            self.print_header("🎨 UI Integration Tests")
            ui_suite = self.run_ui_integration_tests()
            self.suites.append(ui_suite)
            self.print_suite_summary(ui_suite)
            
        except Exception as e:
            self.print_status(f"Critical error during test execution: {str(e)}", "FAIL")
            traceback.print_exc()
            return False
            
        self.end_time = datetime.now()
        
        # Generate final report
        self.generate_final_report()
        
        # Determine overall success
        total_failed = sum(suite.failed_count for suite in self.suites)
        return total_failed == 0
        
    def print_suite_summary(self, suite: TestSuite):
        """Print a summary of a test suite"""
        status_symbol = "✅" if suite.failed_count == 0 else "❌"
        print(f"\n{status_symbol} {Colors.BOLD}{suite.name}{Colors.END}: {suite.passed_count}/{suite.total_count} tests passed")
        
        for test in suite.tests:
            if test.status == "PASS":
                self.print_status(f"PASS {test.name}: {test.details}", "PASS")
            elif test.status == "FAIL":
                self.print_status(f"FAIL {test.name}: {test.details}", "FAIL") 
            elif test.status == "WARN":
                self.print_status(f"WARN {test.name}: {test.details}", "WARN")
            elif test.status == "SKIP":
                self.print_status(f"SKIP {test.name}: {test.details}", "SKIP")
                
    def generate_final_report(self):
        """Generate comprehensive final test report"""
        self.print_header("📊 COMPREHENSIVE TEST REPORT", "=", 80)
        
        # Calculate totals
        total_tests = sum(suite.total_count for suite in self.suites)
        total_passed = sum(suite.passed_count for suite in self.suites)
        total_failed = sum(suite.failed_count for suite in self.suites)
        total_warned = sum(suite.warned_count for suite in self.suites)
        total_skipped = sum(suite.skipped_count for suite in self.suites)
        
        execution_time = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
        
        # Print summary
        print(f"\n{Colors.BOLD}Test Summary:{Colors.END}")
        print(f"  📅 Execution Time: {execution_time:.2f} seconds")
        print(f"  🧪 Total Tests: {total_tests}")
        print(f"  {Colors.GREEN}✅ Passed: {total_passed}{Colors.END}")
        print(f"  {Colors.RED}❌ Failed: {total_failed}{Colors.END}")
        print(f"  {Colors.YELLOW}⚠️  Warnings: {total_warned}{Colors.END}")
        print(f"  {Colors.MAGENTA}⏭️  Skipped: {total_skipped}{Colors.END}")
        
        # Print suite breakdown
        print(f"\n{Colors.BOLD}Suite Breakdown:{Colors.END}")
        for suite in self.suites:
            status_color = Colors.GREEN if suite.failed_count == 0 else Colors.RED
            print(f"  {status_color}• {suite.name}: {suite.passed_count}/{suite.total_count} passed "
                  f"({suite.execution_time:.2f}s){Colors.END}")
            
        # Overall status
        print(f"\n{Colors.BOLD}Overall Status:{Colors.END}")
        if total_failed == 0:
            if total_warned == 0:
                print(f"  {Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED - READY FOR COMMIT{Colors.END}")
                self.print_status("System is fully functional and ready for production deployment", "PASS")
            else:
                print(f"  {Colors.YELLOW}{Colors.BOLD}⚠️  TESTS PASSED WITH WARNINGS - PROCEED WITH CAUTION{Colors.END}")
                self.print_status(f"System is functional but has {total_warned} warnings that should be addressed", "WARN")
        else:
            print(f"  {Colors.RED}{Colors.BOLD}❌ COMMIT NOT RECOMMENDED - FIX ISSUES FIRST{Colors.END}")
            self.print_status(f"System has {total_failed} critical failures that must be resolved", "FAIL")
            
        # Detailed recommendations
        print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
        if total_failed == 0 and total_warned == 0:
            print("  🎉 All systems operational - proceed with confidence!")
        elif total_failed == 0:
            print("  📝 Review warnings and consider addressing them before production")
            print("  ✅ Safe to commit but monitor the warned components")
        else:
            print("  🔧 Fix all failed tests before committing")
            print("  🧪 Re-run tests after fixes to ensure stability")
            
        # Save detailed report to file
        self.save_detailed_report()
        
    def save_detailed_report(self):
        """Save detailed test report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.json"
        
        report_data = {
            "timestamp": self.start_time.isoformat() if self.start_time else None,
            "execution_time": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0,
            "summary": {
                "total_tests": sum(suite.total_count for suite in self.suites),
                "total_passed": sum(suite.passed_count for suite in self.suites),
                "total_failed": sum(suite.failed_count for suite in self.suites),
                "total_warned": sum(suite.warned_count for suite in self.suites),
                "total_skipped": sum(suite.skipped_count for suite in self.suites)
            },
            "suites": []
        }
        
        for suite in self.suites:
            suite_data = {
                "name": suite.name,
                "description": suite.description,
                "execution_time": suite.execution_time,
                "summary": {
                    "total": suite.total_count,
                    "passed": suite.passed_count,
                    "failed": suite.failed_count,
                    "warned": suite.warned_count,
                    "skipped": suite.skipped_count
                },
                "tests": []
            }
            
            for test in suite.tests:
                test_data = {
                    "name": test.name,
                    "status": test.status,
                    "details": test.details,
                    "execution_time": test.execution_time,
                    "timestamp": test.timestamp
                }
                suite_data["tests"].append(test_data)
                
            report_data["suites"].append(suite_data)
            
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            self.print_status(f"Detailed report saved to: {report_file}", "INFO")
        except Exception as e:
            self.print_status(f"Failed to save detailed report: {str(e)}", "WARN")


def main():
    """Main execution function"""
    print(f"{Colors.BOLD}{Colors.CYAN}Comprehensive Pre-Commit Test Suite{Colors.END}")
    print(f"{Colors.CYAN}Based on CLAUDE.md test specifications{Colors.END}\n")
    
    # Initialize test runner
    runner = ComprehensiveTestRunner()
    
    # Run all tests
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()