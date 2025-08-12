#!/usr/bin/env python3
"""
Corrected comprehensive test script for the software management page.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Test configuration
BASE_URL = "http://localhost:3000"
LOGIN_CREDENTIALS = {"username": "admin", "password": "admin123"}
SCREENSHOTS_DIR = Path("test-screenshots")
TEST_RESULTS = []

class SoftwarePageTester:
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        self.test_start_time = datetime.now()
        self.bugs_found = []
        self.console_errors = []
        self.network_errors = []
        
    async def setup(self):
        """Initialize browser and page"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
        # Setup error monitoring
        self.page.on("console", self.handle_console_msg)
        self.page.on("response", self.handle_response)
        
        # Create screenshots directory
        SCREENSHOTS_DIR.mkdir(exist_ok=True)
        
        print(f"🚀 Browser initialized. Starting tests at {self.test_start_time}")
        
    async def cleanup(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    def handle_console_msg(self, msg):
        """Handle console messages"""
        if msg.type in ['error', 'warning']:
            error = {
                "type": msg.type,
                "text": msg.text,
                "url": self.page.url,
                "timestamp": datetime.now().isoformat()
            }
            self.console_errors.append(error)
            print(f"🔍 Console {msg.type}: {msg.text}")
            
    def handle_response(self, response):
        """Handle network responses"""
        if response.status >= 400:
            error = {
                "url": response.url,
                "status": response.status,
                "status_text": response.status_text,
                "timestamp": datetime.now().isoformat()
            }
            self.network_errors.append(error)
            print(f"🔍 Network error: {response.status} - {response.url}")
            
    async def take_screenshot(self, name: str, description: str = ""):
        """Take a screenshot with timestamp"""
        filename = f"{name}.png"
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
        
    async def test_login_and_navigate(self):
        """Test login and navigation to software page"""
        print("\n🔐 Testing login and navigation...")
        
        try:
            # Navigate to the application
            await self.page.goto(BASE_URL)
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            await self.take_screenshot("01_login_page", "Initial login page")
            
            # Fill login form
            await self.page.fill('input[name="username"]', LOGIN_CREDENTIALS["username"])
            await self.page.fill('input[name="password"]', LOGIN_CREDENTIALS["password"])
            await self.take_screenshot("02_login_filled", "Login form filled")
            
            # Submit login
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # Check if we're redirected (login successful)
            current_url = self.page.url
            if current_url == f"{BASE_URL}/" or '/login' not in current_url:
                await self.log_test_result("Login Authentication", "PASS", 
                                         f"Successfully logged in, URL: {current_url}")
                await self.take_screenshot("03_login_success", "Successful login")
            else:
                await self.log_test_result("Login Authentication", "FAIL", 
                                         f"Login failed, still at: {current_url}")
                return False
                
            # Navigate to software page
            await self.page.goto(f"{BASE_URL}/software")
            await self.page.wait_for_load_state('networkidle', timeout=15000)
            
            current_url = self.page.url
            if '/software' in current_url:
                await self.log_test_result("Software Page Navigation", "PASS", 
                                         f"Successfully navigated to software page")
                await self.take_screenshot("04_software_page_loaded", "Software page loaded")
                return True
            else:
                await self.log_test_result("Software Page Navigation", "FAIL", 
                                         f"Failed to navigate to software page, URL: {current_url}")
                return False
                
        except Exception as e:
            await self.log_test_result("Login and Navigation", "FAIL", 
                                     f"Exception during login/navigation: {str(e)}")
            return False
            
    async def test_page_structure(self):
        """Test page structure and title"""
        print("\n📄 Testing page structure...")
        
        try:
            # Check page title
            title = await self.page.title()
            await self.log_test_result("Page Title", "PASS", f"Page title: {title}")
            
            # Look for main heading
            headings = await self.page.query_selector_all('h1, h2, .title, .heading')
            if headings:
                heading_texts = []
                for heading in headings:
                    text = await heading.inner_text()
                    heading_texts.append(text.strip())
                    
                await self.log_test_result("Page Headings", "PASS", 
                                         f"Found headings: {', '.join(heading_texts)}")
            else:
                await self.log_test_result("Page Headings", "WARNING", "No clear headings found")
                
            return True
            
        except Exception as e:
            await self.log_test_result("Page Structure", "FAIL", f"Exception: {str(e)}")
            return False
            
    async def test_statistics_cards(self):
        """Test statistics cards"""
        print("\n📊 Testing statistics cards...")
        
        try:
            # Wait a bit for potential data loading
            await self.page.wait_for_timeout(2000)
            
            # Look for various types of statistics cards
            card_selectors = [
                '[data-testid="stat-card"]',
                '.stat-card',
                '.statistics',
                '.summary-card',
                '.metric-card',
                '.kpi',
                '.card:has-text("Total")',
                '.card:has-text("Active")',
                '.card:has-text("Installed")',
                'div:has(> h3):has(> p)'  # Generic card pattern
            ]
            
            stats_found = []
            for selector in card_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        for element in elements:
                            text = await element.inner_text()
                            stats_found.append(text.strip().replace('\n', ' '))
                except:
                    continue
                    
            if stats_found:
                await self.log_test_result("Statistics Cards", "PASS", 
                                         f"Found {len(stats_found)} statistics cards")
                for i, stat in enumerate(stats_found[:5]):  # Show first 5
                    print(f"   Stat {i+1}: {stat[:100]}")
                    
                await self.take_screenshot("05_stats_cards_check", "Statistics cards view")
            else:
                await self.log_test_result("Statistics Cards", "FAIL", 
                                         "No statistics cards found")
                await self.report_bug(
                    "UI/Layout", "MEDIUM", self.page.url,
                    "No statistics cards found on software page",
                    "1. Navigate to /software\n2. Look for statistics/summary cards",
                    "Should display statistics cards with software metrics",
                    "No statistics cards visible",
                    self.console_errors[-5:], self.network_errors[-5:]
                )
                
            return len(stats_found) > 0
            
        except Exception as e:
            await self.log_test_result("Statistics Cards", "FAIL", f"Exception: {str(e)}")
            return False
            
    async def test_data_loading(self):
        """Test software data loading (should show items)"""
        print("\n📊 Testing software data loading...")
        
        try:
            # Wait for data loading
            await self.page.wait_for_timeout(3000)
            
            # Look for data table or list items
            data_selectors = [
                'tbody tr',  # Table rows
                '[data-testid="software-item"]',
                '.software-item',
                '.data-row',
                '.list-item',
                'tr',  # Any table row
                '.table-row',
                '[role="row"]'
            ]
            
            software_items = []
            used_selector = None
            
            for selector in data_selectors:
                try:
                    items = await self.page.query_selector_all(selector)
                    if items and len(items) > 1:  # More than just header
                        software_items = items
                        used_selector = selector
                        break
                except:
                    continue
                    
            if software_items:
                await self.log_test_result("Software Data Loading", "PASS", 
                                         f"Found {len(software_items)} items using {used_selector}")
                
                # Check for expected count (10 items from mock data)
                if len(software_items) == 10:
                    await self.log_test_result("Software Data Count", "PASS", 
                                             "Exactly 10 items as expected from mock data")
                elif len(software_items) > 0:
                    await self.log_test_result("Software Data Count", "WARNING", 
                                             f"Found {len(software_items)} items, expected 10")
                    
                # Try to extract some sample data
                sample_data = []
                for i, item in enumerate(software_items[:3]):  # First 3 items
                    try:
                        text = await item.inner_text()
                        sample_data.append(text.strip().replace('\n', ' ')[:100])
                    except:
                        continue
                        
                if sample_data:
                    print("   Sample software items:")
                    for i, data in enumerate(sample_data):
                        print(f"   {i+1}. {data}")
                        
                await self.take_screenshot("06_table_check", f"Data table with {len(software_items)} items")
                
            else:
                await self.log_test_result("Software Data Loading", "FAIL", 
                                         "No software items found")
                await self.report_bug(
                    "Functional", "HIGH", self.page.url,
                    "No software data loading on software page",
                    "1. Navigate to /software\n2. Wait for data to load\n3. Check for software items",
                    "Should display software items (10 from mock data)",
                    "No software items visible",
                    self.console_errors[-5:], self.network_errors[-5:]
                )
                
            return len(software_items) > 0
            
        except Exception as e:
            await self.log_test_result("Data Loading", "FAIL", f"Exception: {str(e)}")
            return False
            
    async def test_agent_selector(self):
        """Test agent selector dropdown"""
        print("\n🖥️ Testing agent selector dropdown...")
        
        try:
            # Look for agent selector
            selector_options = [
                'select',
                '[data-testid="agent-selector"]',
                '.agent-selector',
                'select:has(option)',
                '[role="combobox"]',
                'button:has-text("Agent")',
                'button:has-text("Select")',
                '.dropdown-trigger'
            ]
            
            agent_selector = None
            used_selector = None
            
            for selector in selector_options:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        agent_selector = element
                        used_selector = selector
                        break
                except:
                    continue
                    
            if agent_selector:
                await self.log_test_result("Agent Selector Detection", "PASS", 
                                         f"Found agent selector using: {used_selector}")
                
                # Try to interact with it
                if used_selector == 'select':
                    # For select element, check options
                    options = await self.page.query_selector_all(f'{used_selector} option')
                    await self.log_test_result("Agent Selector Options", "PASS", 
                                             f"Found {len(options)} options")
                    
                    # Try to get option texts
                    option_texts = []
                    for option in options[:5]:  # First 5 options
                        try:
                            text = await option.inner_text()
                            option_texts.append(text.strip())
                        except:
                            continue
                            
                    if option_texts:
                        print(f"   Options: {', '.join(option_texts)}")
                        
                else:
                    # For other elements, try clicking
                    try:
                        await agent_selector.click()
                        await self.page.wait_for_timeout(1000)
                        await self.log_test_result("Agent Selector Interaction", "PASS", 
                                                 "Successfully clicked agent selector")
                    except Exception as e:
                        await self.log_test_result("Agent Selector Interaction", "WARNING", 
                                                 f"Could not click selector: {str(e)}")
                        
                await self.take_screenshot("07_agent_selector_clicked", "Agent selector interaction")
                
            else:
                await self.log_test_result("Agent Selector", "FAIL", "No agent selector found")
                await self.report_bug(
                    "Functional", "MEDIUM", self.page.url,
                    "Agent selector dropdown not found",
                    "1. Navigate to /software\n2. Look for agent selector dropdown",
                    "Should have an agent selector for filtering software by agent",
                    "No agent selector found",
                    self.console_errors[-5:], self.network_errors[-5:]
                )
                
            return agent_selector is not None
            
        except Exception as e:
            await self.log_test_result("Agent Selector", "FAIL", f"Exception: {str(e)}")
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
                'input[name="search"]',
                'input[name="filter"]',
                '.search-field'
            ]
            
            search_input = None
            used_selector = None
            
            for selector in search_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        search_input = element
                        used_selector = selector
                        break
                except:
                    continue
                    
            if search_input:
                await self.log_test_result("Search Input Detection", "PASS", 
                                         f"Found search input using: {used_selector}")
                
                # Get placeholder text
                try:
                    placeholder = await search_input.get_attribute('placeholder')
                    if placeholder:
                        print(f"   Placeholder: {placeholder}")
                except:
                    pass
                    
                # Test search functionality
                test_search_term = "microsoft"
                await search_input.fill(test_search_term)
                await self.page.wait_for_timeout(1500)  # Wait for filtering
                
                await self.log_test_result("Search Input Functionality", "PASS", 
                                         f"Successfully entered search term: {test_search_term}")
                await self.take_screenshot("08_search_tested", f"Search with '{test_search_term}'")
                
                # Clear search
                await search_input.fill("")
                await self.page.wait_for_timeout(1000)
                
            else:
                await self.log_test_result("Search Filter", "FAIL", "No search input found")
                await self.report_bug(
                    "Functional", "MEDIUM", self.page.url,
                    "Search filter input not found",
                    "1. Navigate to /software\n2. Look for search/filter input",
                    "Should have a search input for filtering software",
                    "No search input found",
                    self.console_errors[-5:], self.network_errors[-5:]
                )
                
            return search_input is not None
            
        except Exception as e:
            await self.log_test_result("Search Filter", "FAIL", f"Exception: {str(e)}")
            return False
            
    async def check_console_and_network_errors(self):
        """Check for console and network errors during testing"""
        print("\n🔍 Checking for errors...")
        
        if self.console_errors:
            await self.log_test_result("Console Errors", "WARNING", 
                                     f"Found {len(self.console_errors)} console errors/warnings")
            for error in self.console_errors[-3:]:  # Show last 3
                print(f"   Console {error['type']}: {error['text'][:100]}")
                
        if self.network_errors:
            await self.log_test_result("Network Errors", "WARNING", 
                                     f"Found {len(self.network_errors)} network errors")
            for error in self.network_errors[-3:]:  # Show last 3
                print(f"   Network {error['status']}: {error['url']}")
                
        if not self.console_errors and not self.network_errors:
            await self.log_test_result("Error Check", "PASS", "No console or network errors detected")
            
    async def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting comprehensive software page testing...\n")
        
        test_results = {}
        
        # Test login and navigation
        test_results['login_navigation'] = await self.test_login_and_navigate()
        if not test_results['login_navigation']:
            print("❌ Cannot continue without successful login and navigation")
            return
            
        # Test page structure
        test_results['structure'] = await self.test_page_structure()
        
        # Test statistics cards
        test_results['statistics'] = await self.test_statistics_cards()
        
        # Test data loading
        test_results['data_loading'] = await self.test_data_loading()
        
        # Test agent selector
        test_results['agent_selector'] = await self.test_agent_selector()
        
        # Test search filter
        test_results['search'] = await self.test_search_filter()
        
        # Check for errors
        await self.check_console_and_network_errors()
        
        # Final screenshot
        await self.take_screenshot("10_final_state", "Final state after all tests")
        
        # Generate summary
        await self.generate_test_summary(test_results)
        
    async def generate_test_summary(self, test_results):
        """Generate comprehensive test summary"""
        print("\n" + "="*80)
        print("📊 SOFTWARE PAGE TEST SUMMARY REPORT")
        print("="*80)
        
        total_tests = len(TEST_RESULTS)
        passed_tests = len([r for r in TEST_RESULTS if r['status'] == 'PASS'])
        failed_tests = len([r for r in TEST_RESULTS if r['status'] == 'FAIL'])
        warning_tests = len([r for r in TEST_RESULTS if r['status'] == 'WARNING'])
        
        print(f"📋 Test Overview:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️  Warnings: {warning_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n🔍 Error Summary:")
        print(f"   Console Errors: {len(self.console_errors)}")
        print(f"   Network Errors: {len(self.network_errors)}")
        print(f"   🐛 Bugs Reported: {len(self.bugs_found)}")
        
        if self.bugs_found:
            print(f"\n🐛 Bug Details:")
            for i, bug in enumerate(self.bugs_found, 1):
                print(f"   {i}. [{bug['severity']}] {bug['description']}")
                
        print(f"\n⏱️  Test Duration: {datetime.now() - self.test_start_time}")
        print(f"📸 Screenshots: {SCREENSHOTS_DIR}")
        
        # Save comprehensive results
        results_file = SCREENSHOTS_DIR / "software_test_report.json"
        with open(results_file, 'w') as f:
            json.dump({
                "test_results": TEST_RESULTS,
                "bugs_found": self.bugs_found,
                "console_errors": self.console_errors,
                "network_errors": self.network_errors,
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "warnings": warning_tests,
                    "success_rate": (passed_tests/total_tests)*100,
                    "duration": str(datetime.now() - self.test_start_time),
                    "bugs_count": len(self.bugs_found),
                    "console_errors_count": len(self.console_errors),
                    "network_errors_count": len(self.network_errors)
                }
            }, indent=2)
            
        print(f"📄 Detailed report saved to: {results_file}")
        

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
        import traceback
        traceback.print_exc()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())