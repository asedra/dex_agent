#!/usr/bin/env python3
"""Simple test to check dashboard route and API calls"""

from playwright.sync_api import sync_playwright
import time

def test_dashboard_route():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser for debugging
        context = browser.new_context()
        page = context.new_page()
        
        # Track 404 errors
        errors_404 = []
        
        def handle_response(response):
            if response.status == 404:
                errors_404.append(response.url)
                print(f"❌ 404 Error: {response.url}")
        
        page.on("response", handle_response)
        
        # Login first
        print("1. Navigating to login...")
        page.goto("http://localhost:3000/login")
        page.wait_for_load_state("networkidle")
        
        print("2. Logging in...")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin123")
        page.click('button[type="submit"]')
        
        # Check where we end up after login
        time.sleep(2)
        current_url = page.url
        print(f"3. After login, URL is: {current_url}")
        
        # Try to navigate to dashboard directly
        print("4. Navigating to dashboard directly...")
        page.goto("http://localhost:3000/dashboard")
        time.sleep(2)
        
        final_url = page.url
        print(f"5. Final URL: {final_url}")
        
        # Check if we're on the dashboard
        if "/dashboard" in final_url or final_url.endswith("/"):
            print("✅ Dashboard route is accessible")
        else:
            print(f"❌ Dashboard route redirected to: {final_url}")
        
        # Check for dashboard content
        try:
            if page.locator("text=Dashboard").is_visible():
                print("✅ Dashboard title is visible")
            else:
                print("❌ Dashboard title not found")
        except:
            print("❌ Could not check dashboard title")
        
        # Wait a bit for API calls
        time.sleep(3)
        
        # Summary
        if errors_404:
            print(f"\n❌ Found {len(errors_404)} 404 errors:")
            for url in errors_404:
                if "dashboard" in url:
                    print(f"   Dashboard API: {url}")
        else:
            print("\n✅ No 404 errors!")
        
        browser.close()

if __name__ == "__main__":
    test_dashboard_route()