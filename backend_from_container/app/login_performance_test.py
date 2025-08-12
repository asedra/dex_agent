#!/usr/bin/env python3
"""
Performance test for login endpoint optimization.
Tests the login endpoint response times to ensure sub-100ms target is met.
"""

import asyncio
import aiohttp
import time
import statistics
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8080"
LOGIN_ENDPOINT = f"{BASE_URL}/api/v1/auth/login"
TEST_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

async def test_login_performance(session, credentials):
    """Test single login request and return response time"""
    start_time = time.time()
    
    try:
        async with session.post(LOGIN_ENDPOINT, json=credentials) as response:
            await response.json()  # Consume response
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            return response_time, response.status
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        return response_time, f"Error: {str(e)}"

async def run_performance_tests():
    """Run comprehensive performance tests for login endpoint"""
    print("🚀 DexAgents Login Performance Test")
    print("=" * 50)
    print(f"Target: < 100ms response time")
    print(f"Endpoint: {LOGIN_ENDPOINT}")
    print(f"Credentials: {TEST_CREDENTIALS['username']}")
    print()
    
    # Test parameters
    test_scenarios = [
        {"name": "Cold Start (First Request)", "requests": 1, "concurrent": 1},
        {"name": "Warm Cache (Sequential)", "requests": 10, "concurrent": 1},
        {"name": "Concurrent Load (5 requests)", "requests": 5, "concurrent": 5},
        {"name": "Heavy Load (20 requests)", "requests": 20, "concurrent": 10},
    ]
    
    results = {}
    
    async with aiohttp.ClientSession() as session:
        for scenario in test_scenarios:
            print(f"🧪 Running: {scenario['name']}")
            
            # Run concurrent requests
            tasks = []
            semaphore = asyncio.Semaphore(scenario['concurrent'])
            
            async def limited_request():
                async with semaphore:
                    return await test_login_performance(session, TEST_CREDENTIALS)
            
            # Create all tasks
            for _ in range(scenario['requests']):
                tasks.append(limited_request())
            
            # Execute and collect results
            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = (time.time() - start_time) * 1000
            
            # Process results
            response_times = []
            errors = []
            status_codes = []
            
            for resp in responses:
                if isinstance(resp, Exception):
                    errors.append(str(resp))
                else:
                    response_time, status = resp
                    response_times.append(response_time)
                    status_codes.append(status)
            
            # Calculate statistics
            if response_times:
                stats = {
                    'min': min(response_times),
                    'max': max(response_times),
                    'avg': statistics.mean(response_times),
                    'median': statistics.median(response_times),
                    'p95': sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 1 else response_times[0],
                    'total_time': total_time,
                    'requests': len(response_times),
                    'errors': len(errors),
                    'success_rate': len(response_times) / (len(response_times) + len(errors)) * 100
                }
                
                results[scenario['name']] = stats
                
                # Print results
                print(f"  ✅ Completed: {stats['requests']} requests in {stats['total_time']:.1f}ms")
                print(f"  📊 Response Times: min={stats['min']:.1f}ms, avg={stats['avg']:.1f}ms, max={stats['max']:.1f}ms, p95={stats['p95']:.1f}ms")
                print(f"  🎯 Target Met: {'✅ YES' if stats['p95'] < 100 else '❌ NO'} (P95: {stats['p95']:.1f}ms)")
                print(f"  📈 Success Rate: {stats['success_rate']:.1f}%")
                
                if errors:
                    print(f"  ❌ Errors: {len(errors)} - {errors[:3]}")  # Show first 3 errors
            else:
                print(f"  ❌ All requests failed: {errors}")
                
            print()
    
    # Summary
    print("📋 PERFORMANCE SUMMARY")
    print("=" * 50)
    
    for scenario_name, stats in results.items():
        target_met = "✅" if stats['p95'] < 100 else "❌"
        print(f"{target_met} {scenario_name}: P95={stats['p95']:.1f}ms (avg={stats['avg']:.1f}ms)")
    
    # Overall assessment
    all_targets_met = all(stats['p95'] < 100 for stats in results.values())
    print()
    print("🏆 OVERALL RESULT")
    print("=" * 20)
    if all_targets_met:
        print("✅ SUCCESS: All scenarios meet the <100ms target!")
    else:
        print("❌ NEEDS IMPROVEMENT: Some scenarios exceed 100ms target")
        slow_scenarios = [name for name, stats in results.items() if stats['p95'] >= 100]
        print(f"   Slow scenarios: {', '.join(slow_scenarios)}")
    
    # Generate detailed report
    report = {
        'timestamp': datetime.now().isoformat(),
        'target_ms': 100,
        'overall_success': all_targets_met,
        'scenarios': results
    }
    
    with open('/home/ali/dex_agent/login_performance_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📁 Detailed report saved to: login_performance_report.json")

if __name__ == "__main__":
    print("Starting login performance tests...")
    print("Make sure the backend is running on http://localhost:8080")
    print()
    
    try:
        asyncio.run(run_performance_tests())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")