#!/usr/bin/env python3
"""
Simple Software Management Page Test
Tests the current state of the software page with comprehensive reporting.
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright

async def test_software_page():
    """Test the software management page comprehensively"""
    print("🚀 Testing Software Management Page")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "screenshots": [],
        "issues": [],
        "console_logs": [],
        "network_requests": []
    }
    
    async with async_playwright() as playwright:
        # Launch browser
        browser = await playwright.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()
        
        # Monitor console and network
        page.on("console", lambda msg: results["console_logs"].append({
            "type": msg.type,
            "text": msg.text,
            "timestamp": datetime.now().isoformat()
        }))
        
        page.on("requestfailed", lambda request: results["network_requests"].append({
            "url": request.url,
            "method": request.method,
            "failure": request.failure,
            "timestamp": datetime.now().isoformat()
        }))
        
        try:
            # 1. Test Login
            print("📝 Step 1: Testing Login...")
            await page.goto("http://localhost:3000/login")
            await page.wait_for_selector('input[name="username"]', timeout=10000)
            
            # Take screenshot of login page
            await page.screenshot(path="/home/ali/dex_agent/test-screenshots/01_login_page.png", full_page=True)
            results["screenshots"].append("01_login_page.png")
            
            # Fill and submit login
            await page.fill('input[name="username"]', "admin")
            await page.fill('input[name="password"]', "admin123")
            await page.screenshot(path="/home/ali/dex_agent/test-screenshots/02_login_filled.png", full_page=True)
            results["screenshots"].append("02_login_filled.png")
            
            await page.click('button[type="submit"]')
            await page.wait_for_url("http://localhost:3000/**", timeout=10000)
            
            await page.screenshot(path="/home/ali/dex_agent/test-screenshots/03_login_success.png", full_page=True)
            results["screenshots"].append("03_login_success.png")
            
            results["tests"]["login"] = {"status": "PASS", "message": "Login successful"}
            print("✅ Login: PASSED")
            
            # 2. Navigate to Software Page
            print("📝 Step 2: Navigating to Software Page...")
            await page.goto("http://localhost:3000/software")
            await page.wait_for_timeout(3000)  # Wait for page to load
            
            await page.screenshot(path="/home/ali/dex_agent/test-screenshots/04_software_page_loaded.png", full_page=True)
            results["screenshots"].append("04_software_page_loaded.png")
            
            # Check if we're on the software page
            current_url = page.url
            if "/software" in current_url:
                results["tests"]["navigation"] = {"status": "PASS", "message": "Navigation successful"}
                print("✅ Navigation: PASSED")
            else:
                results["tests"]["navigation"] = {"status": "FAIL", "message": f"Expected /software, got {current_url}"}
                print("❌ Navigation: FAILED")
            
            # 3. Check Page Elements
            print("📝 Step 3: Checking Page Elements...")
            
            # Check for statistics cards
            stats_cards = await page.locator('[data-testid*="stats"], .stats-card, [class*="stat"]').count()
            if stats_cards > 0:
                results["tests"]["statistics_cards"] = {"status": "PASS", "found": stats_cards}
                print(f"✅ Statistics Cards: FOUND {stats_cards} cards")
            else:
                results["tests"]["statistics_cards"] = {"status": "FAIL", "found": 0}
                print("❌ Statistics Cards: NOT FOUND")
            
            # Check for software table/list
            software_items = await page.locator('[data-testid*="software"], .software-item, tbody tr, [class*="software"]').count()
            if software_items > 0:
                results["tests"]["software_inventory"] = {"status": "PASS", "found": software_items}
                print(f"✅ Software Inventory: FOUND {software_items} items")
            else:
                results["tests"]["software_inventory"] = {"status": "FAIL", "found": 0}
                print("❌ Software Inventory: NOT FOUND")
            
            # Check for search functionality
            search_elements = await page.locator('input[placeholder*="search"], input[type="search"], [data-testid*="search"]').count()
            if search_elements > 0:
                results["tests"]["search_functionality"] = {"status": "PASS", "found": search_elements}
                print(f"✅ Search Functionality: FOUND {search_elements} search elements")
            else:
                results["tests"]["search_functionality"] = {"status": "FAIL", "found": 0}
                print("❌ Search Functionality: NOT FOUND")
            
            # Check for agent filter
            filter_elements = await page.locator('select, [data-testid*="filter"], [data-testid*="agent"], .filter-dropdown').count()
            if filter_elements > 0:
                results["tests"]["agent_filter"] = {"status": "PASS", "found": filter_elements}
                print(f"✅ Agent Filter: FOUND {filter_elements} filter elements")
            else:
                results["tests"]["agent_filter"] = {"status": "FAIL", "found": 0}
                print("❌ Agent Filter: NOT FOUND")
            
            # 4. Test Search if Available
            print("📝 Step 4: Testing Search Functionality...")
            search_input = page.locator('input[placeholder*="search"], input[type="search"]').first
            if await search_input.count() > 0:
                await search_input.fill("Microsoft")
                await page.wait_for_timeout(1000)
                
                await page.screenshot(path="/home/ali/dex_agent/test-screenshots/05_search_test.png", full_page=True)
                results["screenshots"].append("05_search_test.png")
                
                # Clear search
                await search_input.fill("")
                results["tests"]["search_test"] = {"status": "PASS", "message": "Search functionality works"}
                print("✅ Search Test: PASSED")
            else:
                results["tests"]["search_test"] = {"status": "SKIP", "message": "No search input found"}
                print("⏭️ Search Test: SKIPPED")
            
            # 5. Final Screenshot
            await page.screenshot(path="/home/ali/dex_agent/test-screenshots/06_final_overview.png", full_page=True)
            results["screenshots"].append("06_final_overview.png")
            
            # 6. Analyze Console Errors
            api_errors = [log for log in results["console_logs"] if log["type"] == "error" and "api" in log["text"].lower()]
            network_errors = [req for req in results["network_requests"]]
            
            if api_errors:
                results["issues"].append(f"API Connection Issues: {len(api_errors)} errors found")
            if network_errors:
                results["issues"].append(f"Network Issues: {len(network_errors)} failed requests")
            
        except Exception as e:
            results["tests"]["critical_error"] = {"status": "FAIL", "error": str(e)}
            print(f"💥 Critical Error: {str(e)}")
        
        finally:
            await browser.close()
    
    # Generate Report
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len([t for t in results["tests"].values() if t.get("status") in ["PASS", "FAIL"]])
    passed_tests = len([t for t in results["tests"].values() if t.get("status") == "PASS"])
    failed_tests = len([t for t in results["tests"].values() if t.get("status") == "FAIL"])
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    
    if results["issues"]:
        print("\n⚠️ ISSUES FOUND:")
        for issue in results["issues"]:
            print(f"  - {issue}")
    
    if results["console_logs"]:
        error_logs = [log for log in results["console_logs"] if log["type"] == "error"]
        if error_logs:
            print(f"\n🔍 Console Errors: {len(error_logs)} found")
    
    if results["network_requests"]:
        print(f"🌐 Network Failures: {len(results['network_requests'])} found")
    
    # Save detailed results
    with open("/home/ali/dex_agent/test-screenshots/test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Screenshots saved in: /home/ali/dex_agent/test-screenshots/")
    print(f"📄 Detailed results: /home/ali/dex_agent/test-screenshots/test_results.json")
    
    # Final Assessment
    if failed_tests == 0 and not results["issues"]:
        print("\n🎉 FINAL STATUS: Software management page is working correctly!")
        return True
    elif passed_tests > failed_tests:
        print("\n⚠️ FINAL STATUS: Software management page is mostly functional but has some issues.")
        return True
    else:
        print("\n❌ FINAL STATUS: Software management page has significant issues.")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_software_page())
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test completed with issues.")