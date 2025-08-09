#!/usr/bin/env python3
"""Test Software page for 401 errors."""

from playwright.sync_api import sync_playwright
import time
import json

def test_software_page():
    with sync_playwright() as p:
        # Launch browser with visible window
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        # Enable console message capturing
        page = context.new_page()
        
        console_messages = []
        network_errors = []
        
        # Capture console messages
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text,
            "location": msg.location
        }))
        
        # Capture network failures
        page.on("requestfailed", lambda request: network_errors.append({
            "url": request.url,
            "failure": request.failure,
            "method": request.method
        }))
        
        # Monitor responses for 401s
        responses_401 = []
        page.on("response", lambda response: responses_401.append({
            "url": response.url,
            "status": response.status,
            "status_text": response.status_text
        }) if response.status == 401 else None)
        
        print("1. Navigating to login page...")
        page.goto("http://localhost:3000/login")
        page.wait_for_load_state("networkidle")
        
        print("2. Logging in with admin/admin123...")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin123")
        page.click('button[type="submit"]')
        
        # Wait for redirect to dashboard or home
        page.wait_for_url("http://localhost:3000/", timeout=10000)
        print("3. Login successful, redirected to home")
        
        # Wait a bit for everything to settle
        time.sleep(2)
        
        print("4. Navigating to Software page...")
        page.goto("http://localhost:3000/software")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle", timeout=10000)
        
        # Wait a bit more to catch any late API calls
        time.sleep(3)
        
        print("\n=== TEST RESULTS ===")
        print(f"Console messages: {len(console_messages)}")
        print(f"Network errors: {len(network_errors)}")
        print(f"401 responses: {len(responses_401)}")
        
        if console_messages:
            print("\n=== CONSOLE MESSAGES ===")
            for msg in console_messages:
                if msg["type"] in ["error", "warning"]:
                    print(f"[{msg['type'].upper()}] {msg['text']}")
                    if msg["location"]:
                        print(f"  Location: {msg['location']}")
        
        if network_errors:
            print("\n=== NETWORK ERRORS ===")
            for error in network_errors:
                print(f"[{error['method']}] {error['url']}")
                print(f"  Failure: {error['failure']}")
        
        if responses_401:
            print("\n=== 401 UNAUTHORIZED RESPONSES ===")
            for resp in responses_401:
                print(f"[401] {resp['url']}")
                print(f"  Status: {resp['status']} {resp['status_text']}")
        
        # Check if page title is visible
        try:
            page.wait_for_selector('h1:has-text("Software Management")', timeout=5000)
            print("\n✅ Software Management page title is visible")
        except:
            print("\n❌ Software Management page title NOT found")
        
        # Take screenshot
        page.screenshot(path="software_page_test.png")
        print("\n📸 Screenshot saved as software_page_test.png")
        
        # Return test results
        test_passed = len(responses_401) == 0 and len(network_errors) == 0
        
        browser.close()
        
        return {
            "passed": test_passed,
            "console_errors": len([m for m in console_messages if m["type"] == "error"]),
            "401_count": len(responses_401),
            "network_errors": len(network_errors)
        }

if __name__ == "__main__":
    result = test_software_page()
    print("\n=== FINAL RESULT ===")
    print(json.dumps(result, indent=2))
    
    if result["passed"]:
        print("\n✅ TEST PASSED - No 401 errors found")
    else:
        print("\n❌ TEST FAILED - Found 401 errors or network issues")