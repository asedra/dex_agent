#!/usr/bin/env python3
"""
Test Failure Analysis Script for API Tests
Analyzes test results and identifies failures for Jira ticket creation
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class TestFailureAnalyzer:
    def __init__(self, output_dir: str = "/home/ali/dex_agent/docs/backend/api/outputs"):
        self.output_dir = Path(output_dir)
        self.failures = []
        self.critical_failures = []
        self.high_priority_failures = []
        self.medium_priority_failures = []
        self.low_priority_failures = []
    
    def analyze_all_results(self):
        """Analyze all test result files"""
        result_files = list(self.output_dir.glob("*_results.json"))
        
        for result_file in result_files:
            if result_file.name == "test_summary.json":
                continue
                
            print(f"Analyzing {result_file.name}...")
            self._analyze_result_file(result_file)
        
        self._categorize_failures()
        return self._generate_failure_report()
    
    def _analyze_result_file(self, result_file: Path):
        """Analyze a single test result file"""
        try:
            with open(result_file, 'r') as f:
                data = json.load(f)
            
            test_suite = data.get("test_suite", result_file.stem.replace("_results", ""))
            tests = data.get("tests", [])
            
            for test in tests:
                if test.get("status") == "failed":
                    failure_info = {
                        "test_suite": test_suite,
                        "test_name": test.get("name"),
                        "endpoint": test.get("endpoint"),
                        "response_code": test.get("response_code"),
                        "response_time_ms": test.get("response_time_ms"),
                        "error": test.get("error"),
                        "assertions": test.get("assertions", []),
                        "request": test.get("request"),
                        "response": test.get("response"),
                        "file": result_file.name
                    }
                    
                    # Determine failure reason
                    failure_info["failure_reason"] = self._determine_failure_reason(failure_info)
                    failure_info["severity"] = self._determine_severity(failure_info)
                    
                    self.failures.append(failure_info)
                    
        except Exception as e:
            print(f"Error analyzing {result_file}: {str(e)}")
    
    def _determine_failure_reason(self, failure_info: Dict) -> str:
        """Determine the primary reason for test failure"""
        if failure_info.get("error"):
            return failure_info["error"]
        
        assertions = failure_info.get("assertions", [])
        failed_assertions = [a for a in assertions if not a.get("passed", False)]
        
        if failed_assertions:
            reasons = []
            for assertion in failed_assertions:
                if assertion.get("type") == "status_code":
                    reasons.append(f"Expected status {assertion.get('expected')} but got {assertion.get('actual')}")
                elif assertion.get("type") == "custom_validation":
                    reasons.append(f"Custom validation failed: {assertion.get('error', 'Unknown validation error')}")
                elif assertion.get("type") == "performance":
                    reasons.append(f"Performance threshold exceeded: {assertion.get('actual')} > {assertion.get('expected')}")
                else:
                    reasons.append(f"{assertion.get('type', 'Unknown')} assertion failed")
            return "; ".join(reasons)
        
        return "Unknown failure reason"
    
    def _determine_severity(self, failure_info: Dict) -> str:
        """Determine severity based on failure type and impact"""
        
        # Critical: Authentication failures, system failures, data corruption risks
        if any(keyword in failure_info["test_suite"].lower() for keyword in ["auth", "system", "database"]):
            if any(keyword in failure_info["failure_reason"].lower() for keyword in ["error", "exception", "crash"]):
                return "Critical"
        
        # Critical: Core agent functionality failures
        if failure_info["test_suite"] in ["agents", "commands"] and failure_info.get("response_code") in [500, 422]:
            return "Critical"
        
        # High: Authorization issues, unexpected status codes
        if failure_info.get("response_code") in [401, 403, 500]:
            return "High"
        
        # High: Command execution failures
        if failure_info["test_suite"] == "commands" and "execute" in failure_info.get("test_name", "").lower():
            return "High"
        
        # Medium: Validation failures, 422 errors
        if failure_info.get("response_code") == 422:
            return "Medium"
        
        # Medium: Performance issues
        if "performance" in failure_info["failure_reason"].lower():
            return "Medium"
        
        # Low: Other failures
        return "Low"
    
    def _categorize_failures(self):
        """Categorize failures by severity"""
        for failure in self.failures:
            severity = failure["severity"]
            if severity == "Critical":
                self.critical_failures.append(failure)
            elif severity == "High":
                self.high_priority_failures.append(failure)
            elif severity == "Medium":
                self.medium_priority_failures.append(failure)
            else:
                self.low_priority_failures.append(failure)
    
    def _generate_failure_report(self) -> Dict[str, Any]:
        """Generate comprehensive failure report"""
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_failures": len(self.failures),
            "severity_breakdown": {
                "Critical": len(self.critical_failures),
                "High": len(self.high_priority_failures),
                "Medium": len(self.medium_priority_failures),
                "Low": len(self.low_priority_failures)
            },
            "failures_by_suite": {},
            "critical_failures": self.critical_failures,
            "high_priority_failures": self.high_priority_failures,
            "medium_priority_failures": self.medium_priority_failures,
            "low_priority_failures": self.low_priority_failures
        }
        
        # Count failures by test suite
        for failure in self.failures:
            suite = failure["test_suite"]
            if suite not in report["failures_by_suite"]:
                report["failures_by_suite"][suite] = 0
            report["failures_by_suite"][suite] += 1
        
        return report
    
    def generate_jira_ticket_data(self, failure: Dict) -> Dict[str, Any]:
        """Generate Jira ticket data for a specific failure"""
        
        # Create summary
        summary = f"[API Test Failure] {failure['test_suite']} - {failure['test_name']}"
        if len(summary) > 100:
            summary = summary[:97] + "..."
        
        # Create description
        description = f"""## Test Information
- Test Suite: {failure['test_suite']}
- Test Name: {failure['test_name']}
- Test File: {failure['file']}
- Endpoint: {failure.get('endpoint', 'N/A')}
- Agent ID Used: DESKTOP-JK5G34L

## Failure Details
**Response Code**: {failure.get('response_code', 'N/A')}
**Response Time**: {failure.get('response_time_ms', 'N/A')}ms
**Error**: {failure.get('failure_reason', 'See assertions below')}

## Request Details
```json
{json.dumps(failure.get('request', {}), indent=2)}
```

## Response Details
```json
{json.dumps(failure.get('response', {}), indent=2) if failure.get('response') else 'No response data'}
```

## Failed Assertions
"""
        
        assertions = failure.get('assertions', [])
        failed_assertions = [a for a in assertions if not a.get('passed', False)]
        
        if failed_assertions:
            for i, assertion in enumerate(failed_assertions, 1):
                description += f"\n{i}. **{assertion.get('type', 'Unknown')}**\n"
                if assertion.get('expected') and assertion.get('actual'):
                    description += f"   - Expected: `{assertion.get('expected')}`\n"
                    description += f"   - Actual: `{assertion.get('actual')}`\n"
                if assertion.get('error'):
                    description += f"   - Error: {assertion.get('error')}\n"
        else:
            description += "\nNo specific assertion failures recorded."
        
        description += f"""

## Steps to Reproduce
1. Navigate to API test directory: `/home/ali/dex_agent/docs/backend/api/`
2. Ensure Docker services are running: `docker compose up -d`
3. Run specific test: `python3 run_all_tests.py {failure['test_suite'].replace('test_', '')}`
4. Observe failure for test: `{failure['test_name']}`

## Expected vs Actual
- **Expected**: Test should pass with proper response
- **Actual**: {failure.get('failure_reason', 'Test failed - see details above')}

## Environment
- API Base URL: http://localhost:8080
- Test Agent: DESKTOP-JK5G34L
- Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Determine priority mapping
        priority_map = {
            "Critical": "Highest",
            "High": "High", 
            "Medium": "Medium",
            "Low": "Low"
        }
        
        return {
            "summary": summary,
            "description": description,
            "priority": priority_map.get(failure["severity"], "Medium"),
            "severity": failure["severity"],
            "labels": ["api-test", "automated-test", failure["test_suite"], "DESKTOP-JK5G34L"],
            "components": ["API", "Testing"],
            "test_suite": failure["test_suite"],
            "test_name": failure["test_name"]
        }

def main():
    """Main execution"""
    analyzer = TestFailureAnalyzer()
    
    print("Analyzing API test failures...")
    report = analyzer.analyze_all_results()
    
    print(f"\n{'='*60}")
    print("TEST FAILURE ANALYSIS SUMMARY")
    print(f"{'='*60}")
    print(f"Total Failures: {report['total_failures']}")
    print(f"Critical: {report['severity_breakdown']['Critical']}")
    print(f"High: {report['severity_breakdown']['High']}")
    print(f"Medium: {report['severity_breakdown']['Medium']}")
    print(f"Low: {report['severity_breakdown']['Low']}")
    
    print(f"\nFailures by Test Suite:")
    for suite, count in sorted(report['failures_by_suite'].items()):
        print(f"  {suite}: {count}")
    
    # Save analysis report
    report_file = Path("/home/ali/dex_agent/test_failure_analysis.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed analysis saved to: {report_file}")
    
    # Generate Jira ticket data for top failures
    print(f"\n{'='*60}")
    print("JIRA TICKET DATA (Top 10 Critical/High Priority)")
    print(f"{'='*60}")
    
    top_failures = (analyzer.critical_failures[:5] + analyzer.high_priority_failures[:5])[:10]
    
    for i, failure in enumerate(top_failures, 1):
        ticket_data = analyzer.generate_jira_ticket_data(failure)
        print(f"\n{i}. {ticket_data['summary']}")
        print(f"   Priority: {ticket_data['priority']}")
        print(f"   Suite: {failure['test_suite']}")
        print(f"   Error: {failure['failure_reason'][:100]}...")

if __name__ == "__main__":
    main()