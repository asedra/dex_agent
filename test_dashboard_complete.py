#!/usr/bin/env python3
"""Complete test of dashboard functionality"""

from playwright.sync_api import sync_playwright
import time
import json

def test_dashboard_complete():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Enable console logging
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        
        # Track network responses
        api_responses = {}
        
        def handle_response(response):
            if "dashboard" in response.url:
                api_responses[response.url] = {
                    "status": response.status,
                    "ok": response.ok
                }
                print(f"API Call: {response.url} - Status: {response.status}")
        
        page.on("response", handle_response)
        
        print("1. Navigating to login page...")
        page.goto("http://localhost:3000/login")
        page.wait_for_load_state("networkidle")
        
        print("2. Logging in...")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin123")
        page.click('button[type="submit"]')
        
        print("3. Waiting for navigation...")
        time.sleep(3)
        
        # Check localStorage for token
        print("4. Checking authentication token...")
        token = page.evaluate("() => localStorage.getItem('token')")
        if token:
            print(f"   ✅ Token found: {token[:20]}...")
        else:
            print("   ❌ No token in localStorage!")
        
        print("5. Current URL:", page.url)
        
        # Navigate to root (where dashboard is)
        print("6. Navigating to dashboard (root)...")
        page.goto("http://localhost:3000/")
        time.sleep(5)  # Wait for API calls
        
        # Check page content
        print("\n7. Checking page content...")
        try:
            # Take screenshot
            page.screenshot(path="dashboard_complete_test.png")
            print("   Screenshot saved as dashboard_complete_test.png")
            
            # Check for dashboard title
            dashboard_title = page.locator("h2:has-text('Dashboard')").is_visible()
            if dashboard_title:
                print("   ✅ Dashboard title is visible")
            else:
                print("   ❌ Dashboard title not found")
            
            # Check for error messages
            error_elements = page.locator("text=/Failed to/i").all()
            if error_elements:
                print(f"   ❌ Found {len(error_elements)} error messages on page")
                for elem in error_elements[:3]:
                    print(f"      - {elem.text_content()}")
            else:
                print("   ✅ No error messages on page")
            
            # Check for dashboard cards
            cards = page.locator(".card").count()
            print(f"   Found {cards} cards on dashboard")
            
        except Exception as e:
            print(f"   ❌ Error checking content: {e}")
        
        # Print console messages
        print("\n8. Console messages:")
        for msg in console_messages[-10:]:  # Last 10 messages
            if "error" in msg.lower():
                print(f"   ❌ {msg}")
            else:
                print(f"   {msg}")
        
        # Print API responses summary
        print("\n9. Dashboard API responses:")
        for url, response in api_responses.items():
            if response["ok"]:
                print(f"   ✅ {url.split('/')[-1]} - Status: {response['status']}")
            else:
                print(f"   ❌ {url.split('/')[-1]} - Status: {response['status']}")
        
        browser.close()

if __name__ == "__main__":
    test_dashboard_complete()