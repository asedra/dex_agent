#!/usr/bin/env python3
"""
Comprehensive Test Runner for DexAgents Backend
Executes all test suites with proper reporting and coverage analysis
"""
import os
import sys
import subprocess
import argparse
import time
from datetime import datetime
import json


class TestRunner:
    """Comprehensive test runner with reporting and analysis"""
    
    def __init__(self):
        self.test_results = {}
        self.coverage_results = {}
        self.start_time = None
        self.end_time = None
        
    def setup_environment(self):
        """Setup test environment and dependencies"""
        print("🔧 Setting up test environment...")
        
        # Ensure we're in the correct directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(backend_dir)
        
        # Load .env file settings
        from dotenv import load_dotenv
        load_dotenv()
        
        # Set up environment variables for Docker PostgreSQL (override .env)
        os.environ["DATABASE_URL"] = "postgresql://dexagents:dexagents_dev_password@localhost:5433/dexagents"
        os.environ["SECRET_KEY"] = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only")
        os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
        os.environ["PYTHONPATH"] = os.getcwd()
        
        # Set test admin credentials
        os.environ["TEST_ADMIN_USERNAME"] = "admin"
        os.environ["TEST_ADMIN_PASSWORD"] = "admin123"
        
        # Install test dependencies if needed
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          check=True, capture_output=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
        
        return True
    
    def run_test_suite(self, suite_name, test_file, markers=None, parallel=False):
        """Run a specific test suite"""
        print(f"\n🧪 Running {suite_name}...")
        
        cmd = [
            sys.executable, "-m", "pytest", 
            test_file,
            "-v",
            "--tb=short"
        ]
        
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
        
        if parallel:
            cmd.extend(["-n", "auto"])  # Use pytest-xdist for parallel execution
        
        # Add coverage for this specific test
        cmd.extend([
            f"--cov=app",
            f"--cov-report=term-missing",
            f"--cov-report=html:htmlcov/{suite_name}",
            f"--cov-report=xml:coverage_{suite_name}.xml"
        ])
        
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 min timeout
            end_time = time.time()
            
            self.test_results[suite_name] = {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "duration": end_time - start_time,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ {suite_name} completed successfully")
            else:
                print(f"❌ {suite_name} failed with return code {result.returncode}")
                print(f"Error output: {result.stderr}")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {suite_name} timed out after 10 minutes")
            self.test_results[suite_name] = {
                "status": "TIMEOUT",
                "duration": 600,
                "returncode": -1,
                "error": "Test suite timed out"
            }
            return False
        
        except Exception as e:
            print(f"💥 {suite_name} crashed: {e}")
            self.test_results[suite_name] = {
                "status": "CRASHED",
                "duration": 0,
                "returncode": -1,
                "error": str(e)
            }
            return False
    
    def run_all_tests(self, include_slow=False, parallel=False):
        """Run all test suites in order"""
        self.start_time = datetime.now()
        
        # Define test suites in order of execution - using existing test files
        test_suites = [
            {
                "name": "Basic Functionality Tests",
                "file": "tests/test_basic_functionality.py",
                "markers": None,  # Run all tests without filtering
                "parallel": parallel
            }
        ]
        
        # Add performance tests if requested
        if include_slow:
            test_suites.append({
                "name": "Performance Tests",
                "file": "tests/test_performance.py",
                "markers": ["performance", "slow"],
                "parallel": False  # Performance tests should run sequentially
            })
        
        # Add live agent tests if environment is configured
        if os.getenv("LIVE_BACKEND_URL") and os.getenv("ENABLE_LIVE_TESTS", "false").lower() == "true":
            test_suites.extend([
                {
                    "name": "Live Agent Tests",
                    "file": "tests/test_live_agent.py", 
                    "markers": ["live_agent"],
                    "parallel": False  # Live tests should not run in parallel
                },
                {
                    "name": "Advanced Live Agent Tests",
                    "file": "tests/test_live_agent_advanced.py",
                    "markers": ["live_agent", "advanced"],
                    "parallel": False
                }
            ])
        
        print("🚀 Starting comprehensive test execution...")
        print(f"📊 Running {len(test_suites)} test suites")
        if include_slow:
            print("⚡ Including slow/performance tests")
        if parallel:
            print("🔄 Using parallel execution where appropriate")
        
        # Execute all test suites
        passed_suites = 0
        failed_suites = 0
        
        for suite in test_suites:
            success = self.run_test_suite(
                suite["name"],
                suite["file"], 
                suite.get("markers"),
                suite.get("parallel", False)
            )
            
            if success:
                passed_suites += 1
            else:
                failed_suites += 1
        
        self.end_time = datetime.now()
        
        # Generate final report
        self.generate_final_report(passed_suites, failed_suites)
        
        return failed_suites == 0
    
    def run_coverage_analysis(self):
        """Run comprehensive coverage analysis"""
        print("\n📊 Running comprehensive coverage analysis...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "--cov=app",
            "--cov-report=html:htmlcov/comprehensive", 
            "--cov-report=xml:coverage_comprehensive.xml",
            "--cov-report=term-missing",
            "--cov-fail-under=80",
            "-q"  # Quiet mode for coverage run
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)  # 20 min timeout
            
            if result.returncode == 0:
                print("✅ Coverage analysis completed successfully")
                print("📄 Coverage reports generated in htmlcov/ directory")
                
                # Extract coverage percentage from output
                coverage_line = [line for line in result.stdout.split('\n') if 'TOTAL' in line]
                if coverage_line:
                    coverage_percent = coverage_line[0].split()[-1]
                    print(f"📈 Total coverage: {coverage_percent}")
                    
                return True
            else:
                print(f"❌ Coverage analysis failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Coverage analysis timed out")
            return False
        except Exception as e:
            print(f"💥 Coverage analysis crashed: {e}")
            return False
    
    def generate_final_report(self, passed_suites, failed_suites):
        """Generate comprehensive final report"""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE TEST EXECUTION REPORT")
        print("="*80)
        
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        print(f"⏱️  Execution Time: {self.format_duration(total_duration)}")
        print(f"📅 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏁 End Time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"✅ Passed Suites: {passed_suites}")
        print(f"❌ Failed Suites: {failed_suites}")
        print(f"📊 Success Rate: {(passed_suites/(passed_suites+failed_suites)*100):.1f}%")
        
        print("\n📋 Suite Details:")
        print("-" * 80)
        
        for suite_name, results in self.test_results.items():
            status_emoji = "✅" if results["status"] == "PASSED" else "❌"
            duration_str = self.format_duration(results["duration"])
            
            print(f"{status_emoji} {suite_name:<30} {results['status']:<10} {duration_str}")
            
            if results["status"] == "FAILED" and results.get("stderr"):
                # Show brief error summary
                error_lines = results["stderr"].split('\n')[:3]  # First 3 lines
                for line in error_lines:
                    if line.strip():
                        print(f"    ⚠️  {line.strip()}")
        
        print("\n📁 Generated Files:")
        print("-" * 80)
        
        # List generated files
        generated_files = [
            "htmlcov/ - HTML coverage reports",
            "coverage_*.xml - XML coverage reports", 
            "reports/ - Test execution reports (if enabled)",
            "pytest cache and logs"
        ]
        
        for file_desc in generated_files:
            print(f"📄 {file_desc}")
        
        # Save report to JSON for CI/CD integration
        report_data = {
            "execution_time": total_duration,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "passed_suites": passed_suites,
            "failed_suites": failed_suites,
            "success_rate": (passed_suites/(passed_suites+failed_suites)*100),
            "suite_results": self.test_results
        }
        
        with open("test_execution_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: test_execution_report.json")
        
        # Final status
        if failed_suites == 0:
            print("\n🎉 ALL TESTS PASSED! 🎉")
            print("🚀 Backend is ready for production deployment!")
        else:
            print(f"\n⚠️  {failed_suites} test suite(s) failed")
            print("🔧 Please review the errors and fix issues before deployment")
        
        print("="*80)
    
    def format_duration(self, seconds):
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.1f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours}h {minutes}m {secs:.1f}s"
    
    def run_specific_tests(self, test_patterns):
        """Run specific tests based on patterns or markers"""
        print(f"🎯 Running specific tests: {', '.join(test_patterns)}")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-v",
            "--tb=short"
        ]
        
        for pattern in test_patterns:
            if pattern.startswith("-m"):
                cmd.extend(["-m", pattern[2:]])  # Remove -m prefix
            else:
                cmd.append(pattern)  # File or test pattern
        
        result = subprocess.run(cmd, text=True)
        return result.returncode == 0


def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(description="DexAgents Backend Comprehensive Test Runner")
    
    parser.add_argument("--all", action="store_true", 
                       help="Run all test suites")
    parser.add_argument("--slow", action="store_true",
                       help="Include slow/performance tests")
    parser.add_argument("--parallel", action="store_true",
                       help="Use parallel test execution where safe")
    parser.add_argument("--coverage", action="store_true",
                       help="Run comprehensive coverage analysis only")
    parser.add_argument("--specific", nargs="+",
                       help="Run specific tests (files, patterns, or -m markers)")
    parser.add_argument("--setup-only", action="store_true",
                       help="Only setup environment, don't run tests")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Setup environment
    if not runner.setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    if args.setup_only:
        print("✅ Environment setup completed")
        sys.exit(0)
    
    success = True
    
    if args.coverage:
        # Run coverage analysis only
        success = runner.run_coverage_analysis()
    elif args.specific:
        # Run specific tests
        success = runner.run_specific_tests(args.specific)
    elif args.all:
        # Run all tests
        success = runner.run_all_tests(include_slow=args.slow, parallel=args.parallel)
        
        # Also run coverage analysis
        if success:
            runner.run_coverage_analysis()
    else:
        # Default: run core test suites (no slow tests)
        print("🏃 Running core test suites (use --all for complete testing)")
        success = runner.run_all_tests(include_slow=False, parallel=args.parallel)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()