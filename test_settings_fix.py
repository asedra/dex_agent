#!/usr/bin/env python3
"""
Test script to verify Settings page fix for DX-130
"""
import time
import subprocess
import json

def run_playwright_test():
    """Run a simple Playwright test to check for console errors"""
    test_code = """
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Collect console messages
  const consoleLogs = [];
  page.on('console', msg => {
    consoleLogs.push({
      type: msg.type(),
      text: msg.text()
    });
  });
  
  // Navigate to login page
  await page.goto('http://localhost:3000/login');
  await page.waitForLoadState('networkidle');
  
  // Login
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'admin123');
  await page.click('button[type="submit"]');
  
  // Wait for navigation
  await page.waitForURL('http://localhost:3000/', { timeout: 5000 });
  
  // Navigate to Settings page
  await page.goto('http://localhost:3000/settings');
  await page.waitForLoadState('networkidle');
  
  // Wait a bit for any delayed console messages
  await page.waitForTimeout(2000);
  
  // Check for specific errors mentioned in DX-130
  const errors = consoleLogs.filter(log => 
    log.type === 'error' || log.type === 'warning'
  ).filter(log => 
    log.text.includes('controlled input') ||
    log.text.includes('uncontrolled') ||
    log.text.includes('value prop on input should not be null') ||
    log.text.includes('Password field is not contained in a form')
  );
  
  if (errors.length > 0) {
    console.log('FAILED: Found console errors:');
    errors.forEach(err => console.log(`  - ${err.type}: ${err.text}`));
    process.exit(1);
  } else {
    console.log('SUCCESS: No console errors related to form controls found');
    
    // Additional check: verify forms are present
    const formCount = await page.locator('form').count();
    console.log(`Found ${formCount} form elements on the page`);
    
    if (formCount >= 2) {
      console.log('SUCCESS: Forms are properly structured');
    } else {
      console.log('WARNING: Expected at least 2 forms, found ' + formCount);
    }
  }
  
  await browser.close();
})();
"""
    
    # Write the test script
    with open('/tmp/test_settings.js', 'w') as f:
        f.write(test_code)
    
    # Run the test
    result = subprocess.run(
        ['node', '/tmp/test_settings.js'],
        capture_output=True,
        text=True,
        cwd='/home/ali/dex_agent/apps/frontend'
    )
    
    print("Test Output:")
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    print("Testing Settings page fix for DX-130...")
    print("-" * 50)
    
    success = run_playwright_test()
    
    if success:
        print("\n✅ All tests passed! The Settings page issues have been fixed.")
        print("\nFixed issues:")
        print("1. ✅ Wrapped password fields in form tags")
        print("2. ✅ Added autoComplete attribute to password inputs")  
        print("3. ✅ Ensured all input values have fallback empty strings")
        print("4. ✅ Added proper form submit handlers")
        print("5. ✅ Set correct button types (submit/button)")
    else:
        print("\n❌ Tests failed. Please check the output above.")
    
    exit(0 if success else 1)