#!/usr/bin/env python3
"""
Unified Test Runner
Runs both backend and frontend tests with combined reporting
"""

import sys
import os
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
import concurrent.futures

class UnifiedTestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.backend_script = self.scripts_dir / "run_backend_tests.py"
        self.frontend_script = self.scripts_dir / "run_frontend_tests.js"
        
    def check_docker_services(self):
        """Check if Docker services are running"""
        print("🐳 Checking Docker services...")
        
        try:
            # Check if docker-compose is running
            result = subprocess.run(
                ["docker-compose", "ps", "--services", "--filter", "status=running"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                running_services = result.stdout.strip().split('\n')
                running_services = [s for s in running_services if s.strip()]
                
                if len(running_services) >= 2:  # At least backend and frontend
                    print(f"✅ Docker services running: {', '.join(running_services)}")
                    return True
                else:
                    print(f"⚠️  Only {len(running_services)} services running")
                    return False
            else:
                print("❌ Docker Compose not running")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Docker service check timed out")
            return False
        except Exception as e:
            print(f"❌ Error checking Docker services: {e}")
            return False
    
    def wait_for_services(self, max_wait=90):
        """Wait for services to be ready"""
        print("⏳ Waiting for services to be ready...")
        
        start_time = time.time()
        backend_ready = False
        frontend_ready = False
        
        while time.time() - start_time < max_wait:
            try:
                # Check backend health with shorter timeout
                if not backend_ready:
                    backend_result = subprocess.run(
                        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                         "http://localhost:8080/api/v1/system/health"],
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    backend_ready = backend_result.returncode == 0 and backend_result.stdout.strip() == "200"
                
                # Check frontend with shorter timeout
                if not frontend_ready:
                    frontend_result = subprocess.run(
                        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                         "http://localhost:3000"],
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    frontend_ready = frontend_result.returncode == 0 and frontend_result.stdout.strip() in ["200", "404", "401"]
                
                # Show progress
                status_msg = f"Backend: {'✅' if backend_ready else '⏳'}, Frontend: {'✅' if frontend_ready else '⏳'}"
                print(f"   {status_msg}")
                
                if backend_ready and frontend_ready:
                    print("✅ All services are ready")
                    return True
                
                time.sleep(3)
                
            except subprocess.TimeoutExpired:
                print("⏳ Service check timeout, retrying...")
                time.sleep(3)
            except Exception as e:
                print(f"⏳ Service check error: {str(e)[:50]}...")
                time.sleep(3)
        
        print("❌ Services did not become ready in time")
        print(f"   Backend ready: {backend_ready}")
        print(f"   Frontend ready: {frontend_ready}")
        return False
    
    def run_backend_tests(self):
        """Run backend tests"""
        print("\n🔧 Running Backend Tests")
        print("=" * 50)
        
        try:
            result = subprocess.run(
                ["python3", str(self.backend_script)],
                cwd=self.project_root,
                timeout=300  # 5 minutes timeout
            )
            
            success = result.returncode == 0
            print(f"\n🔧 Backend Tests: {'✅ PASSED' if success else '❌ FAILED'}")
            return success
            
        except subprocess.TimeoutExpired:
            print("\n❌ Backend tests timed out")
            return False
        except Exception as e:
            print(f"\n❌ Backend test execution failed: {e}")
            return False
    
    def run_frontend_tests(self):
        """Run frontend tests"""
        print("\n🌐 Running Frontend Tests")
        print("=" * 50)
        
        try:
            result = subprocess.run(
                ["node", str(self.frontend_script)],
                cwd=self.project_root,
                timeout=600  # 10 minutes timeout
            )
            
            success = result.returncode == 0
            print(f"\n🌐 Frontend Tests: {'✅ PASSED' if success else '❌ FAILED'}")
            return success
            
        except subprocess.TimeoutExpired:
            print("\n❌ Frontend tests timed out")
            return False
        except Exception as e:
            print(f"\n❌ Frontend test execution failed: {e}")
            return False
    
    def run_tests_parallel(self):
        """Run backend and frontend tests in parallel"""
        print("\n🚀 Running Tests in Parallel")
        print("=" * 50)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both test suites
            backend_future = executor.submit(self.run_backend_tests)
            frontend_future = executor.submit(self.run_frontend_tests)
            
            # Wait for both to complete
            backend_success = backend_future.result()
            frontend_success = frontend_future.result()
            
            return backend_success, frontend_success
    
    def run_tests_sequential(self):
        """Run backend and frontend tests sequentially"""
        print("\n🔄 Running Tests Sequentially")
        print("=" * 50)
        
        backend_success = self.run_backend_tests()
        frontend_success = self.run_frontend_tests()
        
        return backend_success, frontend_success
    
    def generate_combined_summary(self, backend_success, frontend_success):
        """Generate a combined test summary"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        print("\n" + "=" * 60)
        print("UNIFIED TEST SUMMARY")
        print("=" * 60)
        print(f"Execution Time: {timestamp}")
        print(f"Backend Tests: {'✅ PASSED' if backend_success else '❌ FAILED'}")
        print(f"Frontend Tests: {'✅ PASSED' if frontend_success else '❌ FAILED'}")
        print()
        
        overall_success = backend_success and frontend_success
        
        if overall_success:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Your code is ready for review and commit")
        else:
            print("⚠️  SOME TESTS FAILED")
            failed_suites = []
            if not backend_success:
                failed_suites.append("Backend")
            if not frontend_success:
                failed_suites.append("Frontend")
            print(f"❌ Failed test suites: {', '.join(failed_suites)}")
            print("📋 Check individual test reports for details:")
            print("   - backend_test_results.md")
            print("   - frontend_test_results.md")
        
        print("\n📋 Test Reports:")
        print("   📄 Backend Results: backend_test_results.md")
        print("   📄 Frontend Results: frontend_test_results.md")
        print("   🌐 Frontend Visual Report: http://localhost:9323")
        print("   🎥 Test Videos & Screenshots: frontend/test-results/")
        
        print("\n💡 Next Steps:")
        if overall_success:
            print("   1. Review test reports")
            print("   2. Request commit approval from user")
            print("   3. Commit and push changes")
        else:
            print("   1. Review failed test reports")
            print("   2. View detailed failures at: http://localhost:9323")
            print("   3. Fix failing tests")
            print("   4. Re-run tests")
        
        return overall_success
    
    def run(self, parallel=True):
        """Main execution method"""
        print("🚀 Unified Test Runner Started")
        print("=" * 60)
        print(f"Mode: {'Parallel' if parallel else 'Sequential'}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check Docker services
        if not self.check_docker_services():
            print("\n❌ Docker services are not running!")
            print("💡 Please run: docker-compose up -d --build")
            return False
        
        # Wait for services to be ready
        if not self.wait_for_services():
            print("\n❌ Services are not ready!")
            print("💡 Try: docker-compose restart")
            return False
        
        # Run tests
        start_time = time.time()
        
        if parallel:
            backend_success, frontend_success = self.run_tests_parallel()
        else:
            backend_success, frontend_success = self.run_tests_sequential()
        
        duration = time.time() - start_time
        print(f"\n⏱️  Total execution time: {duration:.1f} seconds")
        
        # Generate combined summary
        overall_success = self.generate_combined_summary(backend_success, frontend_success)
        
        return overall_success

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Unified Test Runner for DexAgents')
    parser.add_argument('--sequential', action='store_true', 
                       help='Run tests sequentially instead of parallel')
    parser.add_argument('--backend-only', action='store_true',
                       help='Run only backend tests')
    parser.add_argument('--frontend-only', action='store_true',
                       help='Run only frontend tests')
    
    args = parser.parse_args()
    
    runner = UnifiedTestRunner()
    
    if args.backend_only:
        success = runner.run_backend_tests()
    elif args.frontend_only:
        success = runner.run_frontend_tests()
    else:
        success = runner.run(parallel=not args.sequential)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()