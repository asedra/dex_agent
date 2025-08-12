#!/usr/bin/env python3
"""
Comprehensive test script for the software management page.
Tests authentication, navigation, data loading, and functionality.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Test configuration
BASE_URL = "http://localhost:3000"
LOGIN_CREDENTIALS = {"username": "admin", "password": "admin123"}
SCREENSHOTS_DIR = Path("screenshots")
TEST_RESULTS = []

class SoftwarePageTester:
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        self.test_start_time = datetime.now()
        self.bugs_found = []
        
    async def setup(self):
        """Initialize browser and page"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Run in headed mode to see what's happening
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
        # Create screenshots directory
        SCREENSHOTS_DIR.mkdir(exist_ok=True)
        
        print(f"Browser initialized. Starting tests at {self.test_start_time}")
        
    async def cleanup(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def take_screenshot(self, name: str, description: str = ""):
        """Take a screenshot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.png"
        filepath = SCREENSHOTS_DIR / filename
        
        try:
            await self.page.screenshot(path=str(filepath), full_page=True)
            print(f"📸 Screenshot saved: {filename} - {description}")
            return str(filepath)
        except Exception as e:
            print(f"❌ Failed to take screenshot {name}: {str(e)}")
            return None
            
    async def log_test_result(self, test_name: str, status: str, details: str = "", error: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,  # PASS/FAIL/WARNING
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        TEST_RESULTS.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
            
    async def report_bug(self, bug_type: str, severity: str, page_url: str, description: str, 
                        steps_to_reproduce: str, expected_behavior: str, actual_behavior: str,
                        console_errors: list = None, network_errors: list = None):
        """Report a bug found during testing"""
        bug = {
            "type": bug_type,
            "severity": severity,
            "page_url": page_url,
            "description": description,
            "steps_to_reproduce": steps_to_reproduce,
            "expected_behavior": expected_behavior,
            "actual_behavior": actual_behavior,
            "console_errors": console_errors or [],
            "network_errors": network_errors or [],
            "timestamp": datetime.now().isoformat(),
            "browser": "Chromium",
            "viewport": "1920x1080"
        }
        self.bugs_found.append(bug)
        print(f"🐛 Bug reported: {severity} - {description}")
        
    async def check_console_errors(self):
        """Monitor for console errors"""
        console_errors = []
        network_errors = []
        
        def handle_console_msg(msg):
            if msg.type in ['error', 'warning']:
                console_errors.append({
                    "type": msg.type,
                    "text": msg.text,
                    "url": self.page.url
                })
                print(f"🔍 Console {msg.type}: {msg.text}")
                
        def handle_response(response):
            if response.status >= 400:
                network_errors.append({
                    "url": response.url,
                    "status": response.status,
                    "status_text": response.status_text
                })
                print(f"🔍 Network error: {response.status} - {response.url}")
                
        self.page.on("console", handle_console_msg)
        self.page.on("response", handle_response)
        
        return console_errors, network_errors
        
    async def test_login(self):
        """Test login functionality"""
        print("\n🔐 Testing login functionality...")
        
        try:
            # Navigate to login page
            await self.page.goto(BASE_URL)
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # Check if we're redirected to login
            current_url = self.page.url
            if '/login' not in current_url and current_url != BASE_URL:
                await self.log_test_result("Login Redirect", "FAIL", 
                                         f"Expected redirect to login, got: {current_url}")
                return False
                
            await self.take_screenshot("01_login_page", "Initial login page")
            
            # Fill login form
            await self.page.fill('input[name="username"]', LOGIN_CREDENTIALS["username"])
            await self.page.fill('input[name="password"]', LOGIN_CREDENTIALS["password"])
            
            # Submit login
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # Check if login was successful
            current_url = self.page.url
            if '/login' in current_url:
                await self.log_test_result("Login Authentication", "FAIL", 
                                         "Still on login page after form submission")
                await self.report_bug(
                    "Authentication", "HIGH", current_url,
                    "Login form submission does not authenticate user",
                    "1. Navigate to login page\n2. Enter admin/admin123\n3. Click submit",
                    "User should be redirected to dashboard",
                    "User remains on login page",
                    await self.get_console_errors()
                )
                return False
                
            await self.log_test_result("Login Authentication", "PASS", 
                                     f"Successfully logged in, redirected to: {current_url}")
            await self.take_screenshot("02_post_login", "After successful login")
            return True
            
        except Exception as e:
            await self.log_test_result("Login Authentication", "FAIL", 
                                     f"Login test failed with exception: {str(e)}")
            return False
            
    async def get_console_errors(self):
        """Get any console errors that occurred"""
        # This would need to be implemented with proper event listeners
        return []
        
    async def test_navigation_to_software_page(self):
        """Test navigation to software management page"""
        print("\n🧭 Testing navigation to software page...")
        
        try:
            # Try to navigate directly to software page
            await self.page.goto(f"{BASE_URL}/software")
            await self.page.wait_for_load_state('networkidle', timeout=15000)
            
            current_url = self.page.url
            if '/software' not in current_url:
                await self.log_test_result("Software Page Navigation", "FAIL", 
                                         f"Failed to navigate to software page, current URL: {current_url}")
                return False
                
            await self.take_screenshot("03_software_page_loaded", "Software page initial load")
            await self.log_test_result("Software Page Navigation", "PASS", "Successfully navigated to software page")
            return True
            
        except Exception as e:
            await self.log_test_result("Software Page Navigation", "FAIL", 
                                     f"Navigation failed with exception: {str(e)}")
            return False
            
    async def test_page_title_and_structure(self):
        """Test page title and basic structure"""
        print("\n📄 Testing page title and structure...")
        
        try:
            # Check page title
            title = await self.page.title()
            if 'software' not in title.lower():
                await self.log_test_result("Page Title", "WARNING", 
                                         f"Page title may not indicate software page: {title}")
                
            # Check for main heading
            heading = await self.page.query_selector('h1')
            if heading:
                heading_text = await heading.inner_text()
                await self.log_test_result("Main Heading", "PASS", 
                                         f"Found main heading: {heading_text}")
            else:
                await self.log_test_result("Main Heading", "FAIL", "No h1 heading found")
                await self.report_bug(
                    "UI/Layout", "MEDIUM", self.page.url,
                    "Software page missing main h1 heading",
                    "1. Navigate to /software page\n2. Check for h1 element",
                    "Page should have a clear h1 heading",
                    "No h1 heading found on page"
                )
                
            return True
            
        except Exception as e:
            await self.log_test_result("Page Structure", "FAIL", 
                                     f"Structure test failed: {str(e)}")
            return False
            
    async def test_data_loading(self):
        """Test if software data loads correctly (should show 10 items from mock data)"""
        print("\n📊 Testing software data loading...")
        
        try:
            # Wait for potential data loading
            await self.page.wait_for_timeout(3000)
            
            # Look for software items (various possible selectors)
            selectors_to_try = [
                '[data-testid="software-item"]',
                '.software-item',
                'tbody tr',  # If it's a table
                '[role="row"]',  # If using ARIA
                '.card',  # If using card layout
                '.list-item'
            ]
            
            software_items = []
            for selector in selectors_to_try:
                try:
                    items = await self.page.query_selector_all(selector)
                    if items:
                        software_items = items
                        await self.log_test_result("Software Items Detection", "PASS", 
                                                 f"Found {len(items)} items using selector: {selector}")
                        break
                except:
                    continue
                    
            if not software_items:
                await self.log_test_result("Software Data Loading", "FAIL", 
                                         "No software items found on page")
                await self.report_bug(
                    "Functional", "HIGH", self.page.url,
                    "Software items not loading or not visible",
                    "1. Navigate to /software page\n2. Wait for data to load\n3. Check for software items",
                    "Should display 10 software items from mock data",
                    "No software items visible on page"
                )
                return False
                
            # Check if we have the expected 10 items
            if len(software_items) != 10:
                await self.log_test_result("Software Data Count", "WARNING", 
                                         f"Found {len(software_items)} items, expected 10")
                await self.report_bug(
                    "Functional", "MEDIUM", self.page.url,
                    f"Incorrect number of software items displayed",
                    "1. Navigate to /software page\n2. Count displayed items",
                    "Should display exactly 10 software items from mock data",
                    f"Displays {len(software_items)} items instead of 10"
                )
            else:
                await self.log_test_result("Software Data Count", "PASS", "Correct number of items (10) displayed")
                
            await self.take_screenshot("04_data_loaded", f"Software data loaded ({len(software_items)} items)")
            return True
            
        except Exception as e:
            await self.log_test_result("Data Loading", "FAIL", 
                                     f"Data loading test failed: {str(e)}")
            return False
            
    async def test_statistics_cards(self):
        """Test if statistics cards show correct values"""
        print("\n📈 Testing statistics cards...")
        
        try:
            # Look for statistics/summary cards
            stat_selectors = [
                '[data-testid="stat-card"]',
                '.stat-card',
                '.statistics',
                '.summary-card',
                '.metric',
                '.kpi-card'
            ]
            
            stats_found = False
            for selector in stat_selectors:
                try:
                    stats = await self.page.query_selector_all(selector)
                    if stats:
                        await self.log_test_result("Statistics Cards", "PASS", 
                                                 f"Found {len(stats)} statistics cards")
                        stats_found = True
                        
                        # Try to extract values from cards
                        for i, stat in enumerate(stats):
                            text = await stat.inner_text()
                            print(f"   Stat {i+1}: {text.strip()}")
                            
                        break
                except:
                    continue
                    
            if not stats_found:
                # Look for any numeric values that might be statistics
                numbers = await self.page.query_selector_all('[data-value], .number, .count')
                if numbers:
                    await self.log_test_result("Statistics Cards", "WARNING", 
                                             f"No formal stat cards found, but found {len(numbers)} numeric elements")
                else:
                    await self.log_test_result("Statistics Cards", "FAIL", 
                                             "No statistics cards or numeric values found")
                    await self.report_bug(
                        "UI/Layout", "MEDIUM", self.page.url,
                        "Statistics cards not displayed on software page",
                        "1. Navigate to /software page\n2. Look for statistics/summary cards",
                        "Should display statistics cards with software metrics",
                        "No statistics cards visible"
                    )
                    
            await self.take_screenshot("05_statistics", "Statistics cards view")
            return stats_found
            
        except Exception as e:
            await self.log_test_result("Statistics Cards", "FAIL", 
                                     f"Statistics test failed: {str(e)}")
            return False
            
    async def test_search_filter(self):
        """Test search filter functionality"""
        print("\n🔍 Testing search filter...")
        
        try:
            # Look for search input
            search_selectors = [
                'input[type="search"]',
                'input[placeholder*="search" i]',
                'input[placeholder*="filter" i]',
                '[data-testid="search"]',
                '.search-input',
                'input[name="search"]'
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = await self.page.query_selector(selector)
                    if search_input:
                        await self.log_test_result("Search Input Detection", "PASS", 
                                                 f"Found search input with selector: {selector}")
                        break
                except:
                    continue
                    
            if not search_input:
                await self.log_test_result("Search Filter", "FAIL", "No search input found")
                await self.report_bug(
                    "Functional", "MEDIUM", self.page.url,
                    "Search filter input not found on software page",
                    "1. Navigate to /software page\n2. Look for search/filter input",
                    "Should have a search input for filtering software",
                    "No search input element found"
                )
                return False
                
            # Test search functionality
            await search_input.fill("test")
            await self.page.wait_for_timeout(1000)  # Wait for potential filtering
            
            await self.log_test_result("Search Input Functionality", "PASS", "Search input accepts text")
            await self.take_screenshot("06_search_test", "Search filter with 'test' input")
            
            # Clear search
            await search_input.fill("")
            await self.page.wait_for_timeout(1000)
            
            return True
            
        except Exception as e:
            await self.log_test_result("Search Filter", "FAIL", 
                                     f"Search test failed: {str(e)}")
            return False
            
    async def test_agent_selector(self):
        """Test agent selector dropdown"""
        print("\n🖥️ Testing agent selector dropdown...")
        
        try:
            # Look for agent selector dropdown
            dropdown_selectors = [
                'select',
                '[data-testid="agent-selector"]',
                '.agent-selector',
                '[role="combobox"]',
                'input[list]',  # datalist
                '.dropdown-trigger'
            ]
            
            dropdown_found = False
            for selector in dropdown_selectors:
                try:
                    dropdown = await self.page.query_selector(selector)
                    if dropdown:
                        await self.log_test_result("Agent Selector Detection", "PASS", 
                                                 f"Found agent selector with selector: {selector}")
                        
                        # Try to interact with dropdown
                        if selector == 'select':
                            # For select element, get options
                            options = await self.page.query_selector_all(f'{selector} option')
                            await self.log_test_result("Agent Selector Options", "PASS", 
                                                     f"Found {len(options)} options in select")
                        else:
                            # For other elements, try clicking
                            await dropdown.click()
                            await self.page.wait_for_timeout(1000)
                            
                        dropdown_found = True
                        break
                except:
                    continue
                    
            if not dropdown_found:
                await self.log_test_result("Agent Selector", "FAIL", "No agent selector dropdown found")
                await self.report_bug(
                    "Functional", "MEDIUM", self.page.url,
                    "Agent selector dropdown not found on software page",
                    "1. Navigate to /software page\n2. Look for agent selector dropdown",
                    "Should have an agent selector dropdown for filtering",
                    "No agent selector dropdown found"
                )
                
            await self.take_screenshot("07_agent_selector", "Agent selector dropdown")
            return dropdown_found
            
        except Exception as e:
            await self.log_test_result("Agent Selector", "FAIL", 
                                     f"Agent selector test failed: {str(e)}")
            return False
            
    async def test_page_responsiveness(self):
        """Test page responsiveness"""
        print("\n📱 Testing page responsiveness...")
        
        try:
            # Test different viewport sizes
            viewports = [
                {"width": 1920, "height": 1080, "name": "Desktop"},
                {"width": 768, "height": 1024, "name": "Tablet"},
                {"width": 375, "height": 667, "name": "Mobile"}
            ]
            
            for viewport in viewports:
                await self.page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
                await self.page.wait_for_timeout(1000)
                
                # Check if page content is still accessible
                body = await self.page.query_selector('body')
                if body:
                    await self.log_test_result(f"Responsiveness ({viewport['name']})", "PASS", 
                                             f"Page renders at {viewport['width']}x{viewport['height']}")
                    await self.take_screenshot(f"08_responsive_{viewport['name'].lower()}", 
                                             f"Responsive view - {viewport['name']}")
                else:
                    await self.log_test_result(f"Responsiveness ({viewport['name']})", "FAIL", 
                                             f"Page not rendering properly at {viewport['width']}x{viewport['height']}")
                    
            # Reset to original viewport
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            return True
            
        except Exception as e:
            await self.log_test_result("Responsiveness", "FAIL", 
                                     f"Responsiveness test failed: {str(e)}")
            return False
            
    async def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting comprehensive software page testing...\n")
        
        # Setup monitoring for console and network errors
        await self.check_console_errors()
        
        test_results = {}
        
        # Run all tests
        test_results['login'] = await self.test_login()
        if not test_results['login']:
            print("❌ Login failed, cannot continue with other tests")
            return
            
        test_results['navigation'] = await self.test_navigation_to_software_page()
        if not test_results['navigation']:
            print("❌ Navigation to software page failed")
            return
            
        test_results['structure'] = await self.test_page_title_and_structure()
        test_results['data_loading'] = await self.test_data_loading()
        test_results['statistics'] = await self.test_statistics_cards()
        test_results['search'] = await self.test_search_filter()
        test_results['agent_selector'] = await self.test_agent_selector()
        test_results['responsiveness'] = await self.test_page_responsiveness()
        
        # Final screenshot
        await self.take_screenshot("09_final_state", "Final page state after all tests")
        
        # Generate summary
        await self.generate_test_summary(test_results)
        
    async def generate_test_summary(self, test_results):
        """Generate comprehensive test summary"""
        print("\n" + "="*80)
        print("📊 TEST SUMMARY REPORT")
        print("="*80)
        
        total_tests = len(TEST_RESULTS)
        passed_tests = len([r for r in TEST_RESULTS if r['status'] == 'PASS'])
        failed_tests = len([r for r in TEST_RESULTS if r['status'] == 'FAIL'])
        warning_tests = len([r for r in TEST_RESULTS if r['status'] == 'WARNING'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n🐛 Bugs Found: {len(self.bugs_found)}")
        
        if self.bugs_found:
            print("\nBug Summary:")
            for i, bug in enumerate(self.bugs_found, 1):
                print(f"{i}. [{bug['severity']}] {bug['description']}")
                
        print(f"\nTest Duration: {datetime.now() - self.test_start_time}")
        print(f"Screenshots saved in: {SCREENSHOTS_DIR}")
        
        # Save results to JSON file
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "test_results": TEST_RESULTS,
                "bugs_found": self.bugs_found,
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "warnings": warning_tests,
                    "success_rate": (passed_tests/total_tests)*100,
                    "duration": str(datetime.now() - self.test_start_time)
                }
            }, indent=2)
            
        print(f"Results saved to: {results_file}")
        

async def main():
    """Main test execution function"""
    tester = SoftwarePageTester()
    
    try:
        await tester.setup()
        await tester.run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with unexpected error: {str(e)}")
    finally:
        await tester.cleanup()
        

if __name__ == "__main__":
    asyncio.run(main())