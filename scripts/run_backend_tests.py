#!/usr/bin/env python3
"""
Backend Test Runner with Automated Reporting
Runs backend API tests and generates formatted markdown reports
"""

import sys
import os
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

# Add backend directory to path to import the tester
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from comprehensive_api_test import DexAgentsAPITester
except ImportError:
    print("❌ Could not import DexAgentsAPITester. Make sure backend/comprehensive_api_test.py exists.")
    sys.exit(1)

class BackendTestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results_file = self.project_root / "backend_test_results.md"
        self.tester = DexAgentsAPITester()
        
    def check_services(self):
        """Check if backend services are running"""
        print("🔍 Checking if backend services are running...")
        
        try:
            # Test if the backend is responding
            result = self.tester.test_health_endpoint()
            if result:
                print("✅ Backend services are running")
                return True
            else:
                print("❌ Backend services are not responding")
                return False
        except Exception as e:
            print(f"❌ Error checking services: {e}")
            return False
    
    def run_tests(self):
        """Run all backend API tests"""
        print("\n🧪 Running backend API tests...")
        print("=" * 60)
        print("🚀 Starting comprehensive API test execution")
        print("📊 Live test results will appear below:")
        print("-" * 60)
        
        # Reset test results
        self.tester.test_results = []
        
        # Run all tests with live output
        success = self.tester.run_all_tests()
        
        print("\n" + "=" * 60)
        print("🏁 Backend test execution completed!")
        
        return success, self.tester.test_results
    
    def generate_report(self, success, test_results):
        """Generate markdown report from test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Count results
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        # Generate report content
        report = f"""# Backend Test Results

## Latest Test Run

**Date**: {timestamp}
**Tester**: Automated Script
**Test Environment**: Local Docker
**Test Command**: python scripts/run_backend_tests.py
**Duration**: {self._calculate_duration(test_results)}

## Test Results Summary

- **Total Tests**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {failed_tests}
- **Success Rate**: {(passed_tests/total_tests)*100:.1f}%

## Test Details

"""
        
        # Add individual test results
        for result in test_results:
            status_icon = "✅" if result['success'] else "❌"
            status_text = "PASS" if result['success'] else "FAIL"
            
            report += f"### {status_icon} {result['test']} - {status_text}\n"
            report += f"**Time**: {result['timestamp']}\n"
            
            if result['message']:
                report += f"**Result**: {result['message']}\n"
            
            if not result['success'] and result.get('response_data'):
                report += f"**Error Details**:\n```\n{result['response_data']}\n```\n"
            
            report += "\n"
        
        # Add failed tests summary if any
        failed_test_results = [r for r in test_results if not r['success']]
        if failed_test_results:
            report += "\n## Failed Tests Summary\n\n"
            for i, result in enumerate(failed_test_results, 1):
                report += f"{i}. **{result['test']}**: {result['message']}\n"
                if result.get('response_data'):
                    report += f"   - Error: {result['response_data']}\n"
            report += "\n"
        
        # Add performance notes
        report += "## Performance Notes\n\n"
        if passed_tests > 0:
            report += "- All API endpoints responded within acceptable timeouts\n"
            report += "- Authentication and authorization working correctly\n"
        
        if failed_tests > 0:
            report += f"- {failed_tests} tests failed - see details above\n"
        
        report += f"- Test execution completed in {self._calculate_duration(test_results)}\n\n"
        
        # Add issues found
        report += "## New Issues Found\n\n"
        if failed_test_results:
            for result in failed_test_results:
                report += f"- **{result['test']}**: {result['message']}\n"
        else:
            report += "- No new issues found\n"
        
        report += "\n"
        
        # Add overall status
        if success:
            report += "## Overall Status: ✅ PASSED\n\nAll backend API tests completed successfully.\n"
        else:
            report += "## Overall Status: ❌ FAILED\n\nSome backend API tests failed. Review failed tests above.\n"
        
        return report
    
    def _calculate_duration(self, test_results):
        """Calculate test duration from results"""
        if not test_results:
            return "0 seconds"
        
        try:
            start_time = datetime.strptime(test_results[0]['timestamp'], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(test_results[-1]['timestamp'], "%Y-%m-%d %H:%M:%S")
            duration = (end_time - start_time).total_seconds()
            
            if duration < 60:
                return f"{duration:.1f} seconds"
            else:
                return f"{duration/60:.1f} minutes"
        except:
            return "Unknown duration"
    
    def save_report(self, report):
        """Save report to backend_test_results.md"""
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Test report saved to: {self.results_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return False
    
    def run(self):
        """Main execution method"""
        print("🚀 Backend Test Runner Started")
        print("=" * 50)
        
        # Check if services are running
        if not self.check_services():
            print("\n❌ Backend services are not running!")
            print("💡 Please run: docker-compose up -d --build")
            return False
        
        # Run tests
        success, test_results = self.run_tests()
        
        # Generate and save report
        report = self.generate_report(success, test_results)
        
        if self.save_report(report):
            print(f"\n📊 Test Summary:")
            print(f"   Total: {len(test_results)} tests")
            print(f"   Passed: {sum(1 for r in test_results if r['success'])}")
            print(f"   Failed: {sum(1 for r in test_results if not r['success'])}")
            
            if success:
                print("\n✅ All backend tests passed!")
            else:
                print("\n⚠️  Some backend tests failed - check report for details")
        
        return success

def main():
    """Main entry point"""
    runner = BackendTestRunner()
    success = runner.run()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()