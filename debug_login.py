#!/usr/bin/env python3
"""
Debug script to check login page and form elements
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Navigating to http://localhost:3000...")
        await page.goto("http://localhost:3000")
        await page.wait_for_load_state('networkidle', timeout=10000)
        
        print(f"Current URL: {page.url}")
        print(f"Page title: {await page.title()}")
        
        # Take screenshot
        await page.screenshot(path="debug_initial.png", full_page=True)
        print("Screenshot saved as debug_initial.png")
        
        # Check for form elements
        print("\nLooking for form elements...")
        
        # Try different selectors for username
        username_selectors = [
            'input[name="username"]',
            'input[type="text"]',
            'input[placeholder*="username" i]',
            'input[placeholder*="user" i]',
            '#username',
            '.username'
        ]
        
        username_found = None
        for selector in username_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    placeholder = await element.get_attribute('placeholder')
                    name = await element.get_attribute('name')
                    input_type = await element.get_attribute('type')
                    print(f"  Found username input: {selector}")
                    print(f"    Placeholder: {placeholder}")
                    print(f"    Name: {name}")
                    print(f"    Type: {input_type}")
                    username_found = element
                    break
            except:
                continue
                
        # Try different selectors for password
        password_selectors = [
            'input[name="password"]',
            'input[type="password"]',
            'input[placeholder*="password" i]',
            '#password',
            '.password'
        ]
        
        password_found = None
        for selector in password_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    placeholder = await element.get_attribute('placeholder')
                    name = await element.get_attribute('name')
                    input_type = await element.get_attribute('type')
                    print(f"  Found password input: {selector}")
                    print(f"    Placeholder: {placeholder}")
                    print(f"    Name: {name}")
                    print(f"    Type: {input_type}")
                    password_found = element
                    break
            except:
                continue
                
        # Look for submit button
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Login")',
            'button:has-text("Sign in")',
            '.login-button',
            '#login-button'
        ]
        
        submit_found = None
        for selector in submit_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    button_type = await element.get_attribute('type')
                    print(f"  Found submit button: {selector}")
                    print(f"    Text: {text}")
                    print(f"    Type: {button_type}")
                    submit_found = element
                    break
            except:
                continue
                
        if not username_found:
            print("❌ No username input found!")
        if not password_found:
            print("❌ No password input found!")
        if not submit_found:
            print("❌ No submit button found!")
            
        # If we found the form elements, try to login
        if username_found and password_found and submit_found:
            print("\n🔐 Attempting login...")
            await username_found.fill("admin")
            await password_found.fill("admin123")
            
            # Take screenshot before submit
            await page.screenshot(path="debug_before_submit.png", full_page=True)
            print("Screenshot before submit saved as debug_before_submit.png")
            
            await submit_found.click()
            await page.wait_for_timeout(3000)
            
            print(f"URL after submit: {page.url}")
            
            # Take screenshot after submit
            await page.screenshot(path="debug_after_submit.png", full_page=True)
            print("Screenshot after submit saved as debug_after_submit.png")
            
        # Get page HTML to check structure
        html_content = await page.content()
        with open("debug_page_content.html", "w") as f:
            f.write(html_content)
        print("Page HTML saved as debug_page_content.html")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_login())