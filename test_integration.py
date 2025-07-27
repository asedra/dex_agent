#!/usr/bin/env python3
"""
Integration test script to verify the complete system
"""

import requests
import json
import time

def test_backend_api():
    """Test backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Backend API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✓ Health check: {response.status_code}")
        print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False
    
    # Test agents endpoint
    try:
        response = requests.get(f"{base_url}/api/agents")
        print(f"✓ Agents endpoint: {response.status_code}")
        agents = response.json()
        print(f"  Found {len(agents)} agents")
        for agent in agents:
            print(f"    - {agent['hostname']} ({agent['status']})")
    except Exception as e:
        print(f"✗ Agents endpoint failed: {e}")
        return False
    
    # Test system info endpoint
    try:
        response = requests.get(f"{base_url}/system/info")
        print(f"✓ System info: {response.status_code}")
        sys_info = response.json()
        print(f"  Hostname: {sys_info['hostname']}")
        print(f"  CPU: {sys_info['cpu_usage']}%")
        print(f"  Memory: {sys_info['memory_usage']}%")
    except Exception as e:
        print(f"✗ System info failed: {e}")
        return False
    
    return True

def test_frontend_access():
    """Test frontend accessibility"""
    print("\nTesting Frontend...")
    
    try:
        response = requests.get("http://localhost:3000")
        print(f"✓ Frontend accessible: {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ Frontend not accessible: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\nTesting Database...")
    
    try:
        from database import db_manager
        
        agents = db_manager.get_agents()
        print(f"✓ Database accessible: {len(agents)} agents found")
        
        if agents:
            agent = agents[0]
            print(f"  Sample agent: {agent['hostname']} ({agent['status']})")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== DexAgents Integration Test ===\n")
    
    # Wait for services to start
    print("Waiting for services to start...")
    time.sleep(2)
    
    backend_ok = test_backend_api()
    frontend_ok = test_frontend_access()
    database_ok = test_database()
    
    print("\n=== Test Results ===")
    print(f"Backend API: {'✓ PASS' if backend_ok else '✗ FAIL'}")
    print(f"Frontend: {'✓ PASS' if frontend_ok else '✗ FAIL'}")
    print(f"Database: {'✓ PASS' if database_ok else '✗ FAIL'}")
    
    if all([backend_ok, frontend_ok, database_ok]):
        print("\n🎉 All tests passed! The system is working correctly.")
        print("\nYou can now access:")
        print("  - Frontend: http://localhost:3000")
        print("  - Backend API: http://localhost:8000")
        print("  - API Docs: http://localhost:8000/docs")
        print("  - Agents page: http://localhost:3000/agents")
    else:
        print("\n❌ Some tests failed. Please check the services.")
    
    return all([backend_ok, frontend_ok, database_ok])

if __name__ == "__main__":
    main() 