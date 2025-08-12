#!/usr/bin/env python3
"""Final test to verify dashboard is working completely"""

from playwright.sync_api import sync_playwright
import time

def test_dashboard_final():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Track errors
        errors = []
        
        def handle_response(response):
            if response.status >= 400:
                errors.append(f"{response.url} - {response.status}")
        
        page.on("response", handle_response)
        
        print("=== Dashboard Final Test ===\n")
        
        # Login
        print("1. Logging in...")
        page.goto("http://localhost:3000/login")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin123")
        page.click('button[type="submit"]')
        
        # Wait for navigation
        time.sleep(3)
        
        # Check dashboard
        print("2. Checking dashboard page...")
        page.goto("http://localhost:3000/")
        time.sleep(5)  # Wait for all API calls
        
        # Take screenshot
        page.screenshot(path="dashboard_final.png")
        
        # Check for dashboard elements
        checks = {
            "Dashboard title": page.locator("h2:has-text('Dashboard')").is_visible(),
            "Total Agents card": page.locator("text=Total Agents").is_visible(),
            "Commands Today card": page.locator("text=Commands Today").is_visible(),
            "System Health card": page.locator("text=System Health").is_visible(),
            "Quick Actions section": page.locator("text=Quick Actions").is_visible(),
            "Agent Metrics section": page.locator("text=Agent Metrics").is_visible()
        }
        
        print("\n3. Dashboard Elements:")
        all_passed = True
        for element, visible in checks.items():
            if visible:
                print(f"   ✅ {element}")
            else:
                print(f"   ❌ {element}")
                all_passed = False
        
        # Check for errors
        print("\n4. API Errors:")
        if errors:
            print(f"   ❌ Found {len(errors)} errors:")
            for error in errors[:5]:
                print(f"      - {error}")
            all_passed = False
        else:
            print("   ✅ No API errors")
        
        browser.close()
        
        # Summary
        print("\n" + "="*40)
        if all_passed:
            print("✅ DASHBOARD IS FULLY FUNCTIONAL!")
        else:
            print("❌ Some issues remain")
        print("="*40)
        
        return all_passed

if __name__ == "__main__":
    success = test_dashboard_final()
    exit(0 if success else 1)