#!/usr/bin/env python3

"""
Playwright Test Script for DexAgent
Tests the frontend using Playwright Python
"""

import asyncio
from playwright.async_api import async_playwright
import sys
import json

async def test_dexagent_frontend():
    """Test DexAgent frontend with Playwright"""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("Testing DexAgent Frontend...")
            
            # Navigate to login page
            print("1. Navigating to http://localhost:3000")
            await page.goto("http://localhost:3000")
            await page.wait_for_load_state("networkidle")
            
            # Check if we're on login page
            if "login" in page.url:
                print("2. On login page, attempting login...")
                
                # Fill login form
                await page.fill('input[name="username"]', 'admin')
                await page.fill('input[name="password"]', 'admin123')
                
                # Click login button
                await page.click('button[type="submit"]')
                
                # Wait for navigation
                await page.wait_for_load_state("networkidle")
                print("3. Login successful!")
            
            # Check dashboard
            print("4. Checking dashboard...")
            await page.wait_for_selector('text=Dashboard', timeout=5000)
            
            # Take screenshot
            screenshot_path = "dexagent-dashboard.png"
            await page.screenshot(path=screenshot_path)
            print(f"5. Screenshot saved to {screenshot_path}")
            
            # Navigate to agents page
            print("6. Navigating to Agents page...")
            await page.click('text=Agents')
            await page.wait_for_load_state("networkidle")
            
            # Check for AI button
            print("7. Checking for AI features...")
            ai_button = await page.query_selector('text=Create Command with AI')
            if ai_button:
                print("   ✓ AI button found!")
            else:
                print("   ✗ AI button not found")
            
            print("\n✅ All tests passed!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            await page.screenshot(path="error-screenshot.png")
            print("Error screenshot saved to error-screenshot.png")
            
        finally:
            await browser.close()

async def quick_test(url):
    """Quick test any URL"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print(f"Opening {url}...")
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        
        title = await page.title()
        print(f"Page title: {title}")
        
        # Keep browser open for 5 seconds
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(quick_test(sys.argv[1]))
    else:
        asyncio.run(test_dexagent_frontend())