#!/usr/bin/env python3
"""Test dashboard functionality in frontend using Playwright"""

from playwright.sync_api import sync_playwright
import time

def test_dashboard():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Enable console message logging
        page.on("console", lambda msg: print(f"Console {msg.type}: {msg.text}"))
        
        # Go to login page
        print("1. Navigating to login page...")
        page.goto("http://localhost:3000/login")
        page.wait_for_load_state("networkidle")
        
        # Login
        print("2. Logging in...")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin123")
        page.click('button[type="submit"]')
        
        # Wait for navigation to dashboard
        print("3. Waiting for dashboard...")
        page.wait_for_url("**/dashboard", timeout=10000)
        
        # Wait a bit for API calls
        print("4. Waiting for API calls to complete...")
        time.sleep(3)
        
        # Check for network errors
        print("\n5. Checking for 404 errors in Network tab...")
        
        # Listen for response events
        failed_requests = []
        
        def handle_response(response):
            if response.status == 404:
                failed_requests.append({
                    "url": response.url,
                    "status": response.status
                })
                print(f"   ❌ 404 Error: {response.url}")
        
        page.on("response", handle_response)
        
        # Reload page to capture all requests
        print("6. Reloading page to capture all requests...")
        page.reload()
        page.wait_for_load_state("networkidle", timeout=10000)
        
        # Take screenshot
        page.screenshot(path="dashboard_test.png")
        print("7. Screenshot saved as dashboard_test.png")
        
        # Check page content
        print("\n8. Checking page content...")
        
        # Check if dashboard elements are present
        try:
            # Check for main dashboard elements
            if page.locator("text=Dashboard").is_visible():
                print("   ✅ Dashboard title is visible")
            else:
                print("   ❌ Dashboard title not found")
                
            if page.locator("text=System Overview").is_visible():
                print("   ✅ System Overview section found")
            else:
                print("   ❌ System Overview section not found")
                
            if page.locator("text=Agent Status").is_visible():
                print("   ✅ Agent Status section found")
            else:
                print("   ❌ Agent Status section not found")
        except Exception as e:
            print(f"   ❌ Error checking elements: {e}")
        
        # Get page HTML for debugging
        html = page.content()
        with open("dashboard_content.html", "w") as f:
            f.write(html)
        print("\n9. Page HTML saved to dashboard_content.html")
        
        browser.close()
        
        # Summary
        if failed_requests:
            print(f"\n❌ Found {len(failed_requests)} 404 errors:")
            for req in failed_requests:
                print(f"   - {req['url']}")
            return False
        else:
            print("\n✅ No 404 errors found!")
            return True

if __name__ == "__main__":
    success = test_dashboard()
    exit(0 if success else 1)