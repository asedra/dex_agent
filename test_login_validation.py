#!/usr/bin/env python3
"""
Simple test script to check login form validation
"""

import time
from playwright.sync_api import sync_playwright

def test_login_validation():
    """Test the login form validation messages"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to login page
            print("🔍 Navigating to login page...")
            page.goto("http://localhost:3000/login", wait_until="load")
            page.wait_for_selector('input[name="username"]', timeout=10000)
            
            print("✅ Login page loaded successfully")
            
            # Test 1: Check if button is disabled when fields are empty
            print("\n📝 Test 1: Button disabled when fields are empty")
            button = page.locator('button[type="submit"]')
            is_disabled = button.get_attribute("disabled")
            print(f"   Button disabled: {is_disabled is not None}")
            
            # Test 2: Try to click empty username field and check for validation
            print("\n📝 Test 2: Username field validation")
            username_input = page.locator('input[name="username"]')
            username_input.click()
            username_input.blur()
            
            # Wait a bit for validation to show
            time.sleep(1)
            
            # Check for username validation message
            username_error = page.locator('p:has-text("Username is required")')
            if username_error.is_visible():
                print("   ✅ Username validation message visible")
            else:
                print("   ❌ Username validation message NOT visible")
                # Try to find any error message
                all_errors = page.locator('p.text-red-600')
                error_count = all_errors.count()
                print(f"   Found {error_count} error messages")
                for i in range(error_count):
                    error_text = all_errors.nth(i).text_content()
                    print(f"   Error {i}: {error_text}")
            
            # Test 3: Try to click empty password field and check for validation
            print("\n📝 Test 3: Password field validation")
            password_input = page.locator('input[name="password"]')
            password_input.click()
            password_input.blur()
            
            # Wait a bit for validation to show
            time.sleep(1)
            
            # Check for password validation message
            password_error = page.locator('p:has-text("Password is required")')
            if password_error.is_visible():
                print("   ✅ Password validation message visible")
            else:
                print("   ❌ Password validation message NOT visible")
            
            # Test 4: Check if helper message shows when one field is filled
            print("\n📝 Test 4: Check helper message with partial input")
            username_input.fill("test")
            time.sleep(1)
            
            # Check for the helper message
            helper_message = page.locator('p:has-text("Please fill in all required fields to continue")')
            if helper_message.is_visible():
                print("   ✅ Helper message visible with partial input")
            else:
                print("   ❌ Helper message NOT visible with partial input")
            
            # Test 5: Clear fields and fill both correctly
            print("\n📝 Test 5: Fill both fields correctly")
            username_input.clear()
            password_input.clear()
            time.sleep(1)
            
            username_input.fill("admin")
            password_input.fill("admin123")
            time.sleep(1)
            
            # Check if button is now enabled
            is_now_enabled = button.get_attribute("disabled") is None
            print(f"   Button now enabled: {is_now_enabled}")
            
            # Check that validation messages are gone
            username_error_gone = not page.locator('p:has-text("Username is required")').is_visible()
            password_error_gone = not page.locator('p:has-text("Password is required")').is_visible()
            print(f"   Username error cleared: {username_error_gone}")
            print(f"   Password error cleared: {password_error_gone}")
            
            print("\n🏁 Test completed!")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    test_login_validation()