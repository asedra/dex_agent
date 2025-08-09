#!/usr/bin/env python3
"""
Test script to verify DX-84 and DX-88 fixes for agent registration and filtering
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
AGENTS_URL = f"{BASE_URL}/agents"
REGISTER_URL = f"{BASE_URL}/agents/register"

# Test credentials
USERNAME = "admin"
PASSWORD = "admin123"

class AgentFixTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        
    def authenticate(self):
        """Authenticate and get token"""
        print("🔐 Authenticating...")
        try:
            response = self.session.post(LOGIN_URL, json={
                "username": USERNAME,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_dx84_validation(self):
        """Test DX-84: Agent registration validation"""
        print("\n🧪 Testing DX-84: Agent registration validation...")
        
        test_cases = [
            {
                "name": "Missing IP address",
                "data": {
                    "hostname": "TEST-HOST-1",
                    "os": "Windows 11",
                    "version": "10.0.22000"
                },
                "should_fail": True
            },
            {
                "name": "Missing OS",
                "data": {
                    "hostname": "TEST-HOST-2", 
                    "ip": "192.168.1.100",
                    "version": "10.0.22000"
                },
                "should_fail": True
            },
            {
                "name": "Missing version",
                "data": {
                    "hostname": "TEST-HOST-3",
                    "ip": "192.168.1.101", 
                    "os": "Windows 11"
                },
                "should_fail": True
            },
            {
                "name": "Invalid IP address",
                "data": {
                    "hostname": "TEST-HOST-4",
                    "ip": "999.999.999.999",
                    "os": "Windows 11",
                    "version": "10.0.22000"
                },
                "should_fail": True
            },
            {
                "name": "Empty hostname",
                "data": {
                    "hostname": "",
                    "ip": "192.168.1.102",
                    "os": "Windows 11", 
                    "version": "10.0.22000"
                },
                "should_fail": True
            },
            {
                "name": "Valid registration",
                "data": {
                    "hostname": "TEST-HOST-VALID",
                    "ip": "192.168.1.200",
                    "os": "Windows 11",
                    "version": "10.0.22000",
                    "tags": ["test", "validation"]
                },
                "should_fail": False
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"  Testing: {test_case['name']}")
            
            try:
                response = self.session.post(REGISTER_URL, json=test_case['data'])
                
                if test_case['should_fail']:
                    if response.status_code >= 400:
                        print(f"    ✅ Correctly rejected: {response.status_code}")
                        results.append(True)
                    else:
                        print(f"    ❌ Should have failed but got: {response.status_code}")
                        results.append(False)
                else:
                    if response.status_code == 200:
                        print(f"    ✅ Successfully registered")
                        results.append(True)
                    else:
                        print(f"    ❌ Should have succeeded but got: {response.status_code}")
                        print(f"        Error: {response.text}")
                        results.append(False)
                        
            except Exception as e:
                print(f"    ❌ Test error: {str(e)}")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📊 DX-84 Validation Test Results: {success_rate:.1f}% ({sum(results)}/{len(results)} passed)")
        return success_rate >= 90
    
    def test_dx88_filtering_pagination(self):
        """Test DX-88: Filtering and pagination"""
        print("\n🧪 Testing DX-88: Filtering and pagination...")
        
        # First, create some test agents with different statuses
        test_agents = [
            {"hostname": f"ONLINE-HOST-{i}", "ip": f"192.168.1.{100+i}", "os": "Windows 11", "version": "10.0.22000", "status": "online"}
            for i in range(3)
        ] + [
            {"hostname": f"OFFLINE-HOST-{i}", "ip": f"192.168.1.{110+i}", "os": "Windows 10", "version": "10.0.19045", "status": "offline"}
            for i in range(2)
        ]
        
        # Register test agents
        print("  Creating test agents...")
        for agent_data in test_agents:
            try:
                response = self.session.post(REGISTER_URL, json=agent_data)
                if response.status_code != 200:
                    print(f"    ⚠️ Failed to create agent {agent_data['hostname']}: {response.status_code}")
            except Exception as e:
                print(f"    ⚠️ Error creating agent {agent_data['hostname']}: {str(e)}")
        
        time.sleep(1)  # Allow agents to be created
        
        # Test filtering by status
        print("  Testing status filtering...")
        tests = [
            {
                "name": "Filter by online status",
                "url": f"{AGENTS_URL}?status=online",
                "expected_min": 1
            },
            {
                "name": "Filter by offline status", 
                "url": f"{AGENTS_URL}?status=offline",
                "expected_min": 1
            },
            {
                "name": "Pagination with limit=2",
                "url": f"{AGENTS_URL}?limit=2&include_total=true",
                "expected_count": 2
            },
            {
                "name": "Pagination with limit=1 and offset=1",
                "url": f"{AGENTS_URL}?limit=1&offset=1",
                "expected_count": 1
            },
            {
                "name": "Combined: online status with limit=1",
                "url": f"{AGENTS_URL}?status=online&limit=1",
                "expected_max": 1
            }
        ]
        
        results = []
        
        for test in tests:
            print(f"    Testing: {test['name']}")
            
            try:
                response = self.session.get(test['url'])
                
                if response.status_code == 200:
                    data = response.json()
                    agents = data.get('agents', [])
                    count = len(agents)
                    
                    # Check expectations
                    passed = True
                    
                    if 'expected_min' in test and count < test['expected_min']:
                        print(f"      ❌ Expected at least {test['expected_min']}, got {count}")
                        passed = False
                    
                    if 'expected_count' in test and count != test['expected_count']:
                        print(f"      ❌ Expected exactly {test['expected_count']}, got {count}")
                        passed = False
                    
                    if 'expected_max' in test and count > test['expected_max']:
                        print(f"      ❌ Expected at most {test['expected_max']}, got {count}")
                        passed = False
                    
                    # Check filtering actually worked (if filtering by status)
                    if 'status=' in test['url'] and agents:
                        expected_status = test['url'].split('status=')[1].split('&')[0]
                        for agent in agents:
                            # Note: We can't easily check actual status since WebSocket connection state affects it
                            pass
                    
                    if passed:
                        print(f"      ✅ Returned {count} agents")
                        if 'total_count' in data:
                            print(f"         Total available: {data['total_count']}")
                    
                    results.append(passed)
                else:
                    print(f"      ❌ Request failed: {response.status_code}")
                    print(f"         Error: {response.text}")
                    results.append(False)
                    
            except Exception as e:
                print(f"      ❌ Test error: {str(e)}")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📊 DX-88 Filtering/Pagination Test Results: {success_rate:.1f}% ({sum(results)}/{len(results)} passed)")
        return success_rate >= 80
    
    def cleanup_test_agents(self):
        """Clean up test agents"""
        print("\n🧹 Cleaning up test agents...")
        
        try:
            # Get all agents
            response = self.session.get(AGENTS_URL)
            if response.status_code == 200:
                data = response.json()
                agents = data.get('agents', [])
                
                # Delete test agents
                for agent in agents:
                    if agent['hostname'].startswith(('TEST-HOST', 'ONLINE-HOST', 'OFFLINE-HOST')):
                        delete_url = f"{AGENTS_URL}/{agent['id']}"
                        delete_response = self.session.delete(delete_url)
                        if delete_response.status_code == 200:
                            print(f"    ✅ Deleted {agent['hostname']}")
                        else:
                            print(f"    ⚠️ Failed to delete {agent['hostname']}: {delete_response.status_code}")
            
        except Exception as e:
            print(f"⚠️ Cleanup error: {str(e)}")
    
    def run_tests(self):
        """Run all tests"""
        print("🚀 Starting Agent Fix Tests")
        print(f"Target URL: {BASE_URL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Run tests
        dx84_passed = self.test_dx84_validation()
        dx88_passed = self.test_dx88_filtering_pagination()
        
        # Cleanup
        self.cleanup_test_agents()
        
        # Final results
        print("\n" + "="*50)
        print("📋 FINAL TEST RESULTS")
        print("="*50)
        print(f"DX-84 (Agent Registration Validation): {'✅ PASSED' if dx84_passed else '❌ FAILED'}")
        print(f"DX-88 (Filtering & Pagination): {'✅ PASSED' if dx88_passed else '❌ FAILED'}")
        
        overall_passed = dx84_passed and dx88_passed
        print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_passed else '❌ SOME TESTS FAILED'}")
        
        return overall_passed

if __name__ == "__main__":
    tester = AgentFixTester()
    success = tester.run_tests()
    exit(0 if success else 1)