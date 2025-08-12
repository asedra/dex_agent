#!/usr/bin/env python3
"""
Comprehensive Software Management Page Test
Tests all functionality of the software management page using Playwright.
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page

class SoftwarePageTester:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.backend_url = "http://localhost:8080"
        self.username = "admin"
        self.password = "admin123"
        self.results = {
            "test_start_time": datetime.now().isoformat(),
            "tests": [],
            "screenshots": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }
        }

    async def log_test(self, test_name: str, passed: bool, details: str = "", error: str = ""):
        """Log test result"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "error": error
        }
        self.results["tests"].append(result)
        self.results["summary"]["total_tests"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
            print(f"✅ {test_name}: PASSED - {details}")
        else:
            self.results["summary"]["failed"] += 1
            self.results["summary"]["errors"].append(f"{test_name}: {error}")
            print(f"❌ {test_name}: FAILED - {error}")

    async def take_screenshot(self, page: Page, name: str):
        """Take a screenshot and save it"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/home/ali/dex_agent/test-screenshots/{timestamp}_{name}.png"
        await page.screenshot(path=filename, full_page=True)
        self.results["screenshots"].append(filename)
        print(f"📸 Screenshot saved: {filename}")

    async def login(self, page: Page) -> bool:
        """Login to the application"""
        try:
            await page.goto(f"{self.base_url}/login")
            await page.wait_for_selector('input[name="username"]', timeout=10000)
            
            await self.take_screenshot(page, "01_login_page")
            
            # Fill login form
            await page.fill('input[name="username"]', self.username)
            await page.fill('input[name="password"]', self.password)
            
            await self.take_screenshot(page, "02_login_filled")
            
            # Submit login
            await page.click('button[type="submit"]')
            
            # Wait for redirect to dashboard
            await page.wait_for_url(f"{self.base_url}/**", timeout=10000)
            await page.wait_for_selector('[data-testid="dashboard"]', timeout=10000)
            
            await self.take_screenshot(page, "03_login_success")
            
            await self.log_test("User Authentication", True, f"Successfully logged in as {self.username}")
            return True
            
        except Exception as e:
            await self.log_test("User Authentication", False, error=f"Login failed: {str(e)}")
            return False

    async def navigate_to_software_page(self, page: Page) -> bool:
        """Navigate to the software management page"""
        try:
            # Navigate to software page
            await page.goto(f"{self.base_url}/software")
            await page.wait_for_selector('[data-testid="software-page"]', timeout=15000)
            
            await self.take_screenshot(page, "04_software_page_loaded")
            
            await self.log_test("Software Page Navigation", True, "Successfully navigated to software page")
            return True
            
        except Exception as e:
            await self.log_test("Software Page Navigation", False, error=f"Navigation failed: {str(e)}")
            return False

    async def verify_software_data_loading(self, page: Page) -> bool:
        """Verify that software data loads correctly (should show 10 items)"""
        try:
            # Wait for software table to load
            await page.wait_for_selector('[data-testid="software-table"]', timeout=15000)
            
            # Count software items in the table
            software_rows = await page.locator('[data-testid="software-row"]').count()
            
            await self.take_screenshot(page, "05_stats_cards_check")
            
            if software_rows >= 10:
                await self.log_test("Software Data Loading", True, f"Successfully loaded {software_rows} software items")
                return True
            else:
                await self.log_test("Software Data Loading", False, error=f"Only {software_rows} software items loaded, expected at least 10")
                return False
                
        except Exception as e:
            await self.log_test("Software Data Loading", False, error=f"Failed to verify software data: {str(e)}")
            return False

    async def verify_statistics_cards(self, page: Page) -> bool:
        """Verify that statistics cards show correct numbers"""
        try:
            # Wait for stats cards to load
            await page.wait_for_selector('[data-testid="stats-total"]', timeout=10000)
            
            # Get total count from stats card
            total_text = await page.locator('[data-testid="stats-total"]').inner_text()
            total_count = int(''.join(filter(str.isdigit, total_text)))
            
            await self.take_screenshot(page, "06_table_check")
            
            if total_count >= 10:
                await self.log_test("Statistics Cards Verification", True, f"Total software count: {total_count}")
                return True
            else:
                await self.log_test("Statistics Cards Verification", False, error=f"Total count shows {total_count}, expected at least 10")
                return False
                
        except Exception as e:
            await self.log_test("Statistics Cards Verification", False, error=f"Failed to verify statistics: {str(e)}")
            return False

    async def test_search_functionality(self, page: Page) -> bool:
        """Test search functionality - search for 'Microsoft'"""
        try:
            # Find and use search input
            await page.fill('[data-testid="software-search"]', 'Microsoft')
            await page.wait_for_timeout(1000)  # Wait for search to filter
            
            await self.take_screenshot(page, "07_agent_selector_clicked")
            
            # Check if results are filtered
            search_results = await page.locator('[data-testid="software-row"]').count()
            
            if search_results > 0:
                await self.log_test("Search Functionality", True, f"Search for 'Microsoft' returned {search_results} results")
                
                # Clear search
                await page.fill('[data-testid="software-search"]', '')
                await page.wait_for_timeout(1000)
                
                return True
            else:
                await self.log_test("Search Functionality", False, error="Search for 'Microsoft' returned no results")
                return False
                
        except Exception as e:
            await self.log_test("Search Functionality", False, error=f"Search failed: {str(e)}")
            return False

    async def test_agent_filter_dropdown(self, page: Page) -> bool:
        """Test agent filter dropdown"""
        try:
            # Find and click agent filter dropdown
            await page.click('[data-testid="agent-filter"]')
            await page.wait_for_timeout(500)
            
            await self.take_screenshot(page, "08_search_tested")
            
            # Check if dropdown options are visible
            dropdown_options = await page.locator('[data-testid="agent-option"]').count()
            
            if dropdown_options > 0:
                await self.log_test("Agent Filter Dropdown", True, f"Agent filter dropdown shows {dropdown_options} options")
                
                # Close dropdown by clicking elsewhere
                await page.click('[data-testid="software-page"]')
                
                return True
            else:
                await self.log_test("Agent Filter Dropdown", False, error="Agent filter dropdown shows no options")
                return False
                
        except Exception as e:
            await self.log_test("Agent Filter Dropdown", False, error=f"Agent filter test failed: {str(e)}")
            return False

    async def test_software_item_details(self, page: Page) -> bool:
        """Click on a software item to see details"""
        try:
            # Click on the first software item
            await page.click('[data-testid="software-row"]:first-child')
            await page.wait_for_timeout(1000)
            
            # Check if details are shown (could be modal, expanded row, or navigation)
            details_visible = (
                await page.locator('[data-testid="software-details"]').count() > 0 or
                await page.locator('[role="dialog"]').count() > 0 or
                await page.url() != f"{self.base_url}/software"
            )
            
            await self.take_screenshot(page, "10_final_state")
            
            if details_visible:
                await self.log_test("Software Item Details", True, "Successfully opened software item details")
                return True
            else:
                await self.log_test("Software Item Details", False, error="No details shown when clicking software item")
                return False
                
        except Exception as e:
            await self.log_test("Software Item Details", False, error=f"Failed to test item details: {str(e)}")
            return False

    async def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Software Management Page Test")
        print("=" * 60)
        
        async with async_playwright() as playwright:
            # Launch browser
            browser = await playwright.chromium.launch(headless=False, slow_mo=500)
            context = await browser.new_context(viewport={'width': 1280, 'height': 720})
            page = await context.new_page()
            
            try:
                # Test sequence
                await self.login(page)
                await self.navigate_to_software_page(page)
                await self.verify_software_data_loading(page)
                await self.verify_statistics_cards(page)
                await self.test_search_functionality(page)
                await self.test_agent_filter_dropdown(page)
                await self.test_software_item_details(page)
                
                # Final screenshot
                await self.take_screenshot(page, "final_overview")
                
            except Exception as e:
                print(f"💥 Critical error during testing: {str(e)}")
                await self.log_test("Critical Error", False, error=str(e))
            
            finally:
                await browser.close()

        # Generate final report
        self.results["test_end_time"] = datetime.now().isoformat()
        
        # Save results
        with open("/home/ali/dex_agent/test-screenshots/software_test_report.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['summary']['total_tests']}")
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")
        
        if self.results['summary']['failed'] > 0:
            print("\n❌ FAILED TESTS:")
            for error in self.results['summary']['errors']:
                print(f"  - {error}")
        
        print(f"\n📁 Screenshots saved in: /home/ali/dex_agent/test-screenshots/")
        print(f"📄 Full report saved: /home/ali/dex_agent/test-screenshots/software_test_report.json")
        
        # Final status
        if self.results['summary']['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED! Software management page is working correctly.")
            return True
        else:
            print(f"\n⚠️  {self.results['summary']['failed']} test(s) failed. Please check the details above.")
            return False

async def main():
    """Main function"""
    tester = SoftwarePageTester()
    success = await tester.run_comprehensive_test()
    
    if success:
        print("\n✅ FINAL STATUS: Software management page is fully functional!")
    else:
        print("\n❌ FINAL STATUS: Issues found in software management page functionality.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())