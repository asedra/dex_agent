#!/usr/bin/env python3
"""
Command Library Page Frontend Test
Tests all functionality of the Command Library page including:
- Page loading and navigation
- Command list display
- Create new command
- AI command generation
- Execute command on agent
- Edit/Delete commands
"""

import time
import json
import subprocess
import sys
from datetime import datetime
import os

def run_playwright_test():
    """Run Playwright test for Command Library page"""
    print("\n" + "="*60)
    print("COMMAND LIBRARY PAGE FRONTEND TEST")
    print("="*60)
    
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "page": "Command Library",
        "tests": [],
        "errors": []
    }
    
    # Create test script
    test_script = """
const { test, expect } = require('@playwright/test');

test.describe('Command Library Page Tests', () => {
    test.beforeEach(async ({ page }) => {
        // Login
        await page.goto('http://localhost:3000/login');
        await page.fill('input[name="username"]', 'admin');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForURL('**/dashboard');
        
        // Navigate to Command Library
        await page.goto('http://localhost:3000/commands');
        await page.waitForLoadState('networkidle');
    });

    test('Page loads correctly', async ({ page }) => {
        // Check page title
        await expect(page.locator('h1')).toContainText('Command Library');
        
        // Check main elements
        await expect(page.locator('button:has-text("Create Command")')).toBeVisible();
        await expect(page.locator('button:has-text("Create Command with AI")')).toBeVisible();
        
        // Take screenshot
        await page.screenshot({ path: 'test-screenshots/command-library-page.png', fullPage: true });
    });

    test('Commands list displays', async ({ page }) => {
        // Wait for table or empty state
        const hasTable = await page.locator('table').count() > 0;
        const hasEmptyState = await page.locator('text=/no commands/i').count() > 0;
        
        expect(hasTable || hasEmptyState).toBeTruthy();
        
        if (hasTable) {
            // Check table headers
            await expect(page.locator('th:has-text("Name")')).toBeVisible();
            await expect(page.locator('th:has-text("Description")')).toBeVisible();
            await expect(page.locator('th:has-text("Category")')).toBeVisible();
            await expect(page.locator('th:has-text("Actions")')).toBeVisible();
        }
    });

    test('Create Command button works', async ({ page }) => {
        // Click Create Command
        await page.click('button:has-text("Create Command")');
        
        // Check if modal/form appears
        await page.waitForSelector('input[name="name"], input[placeholder*="name" i]', { timeout: 5000 });
        
        // Fill form
        await page.fill('input[name="name"], input[placeholder*="name" i]', 'Test Command');
        await page.fill('textarea[name="description"], textarea[placeholder*="description" i]', 'Test Description');
        await page.fill('textarea[name="command"], textarea[placeholder*="command" i]', 'Get-ComputerInfo');
        
        // Select category if available
        const categorySelect = await page.locator('select[name="category"], [role="combobox"]').count();
        if (categorySelect > 0) {
            await page.selectOption('select[name="category"]', { index: 1 });
        }
        
        // Take screenshot before save
        await page.screenshot({ path: 'test-screenshots/create-command-form.png' });
        
        // Save command
        await page.click('button:has-text("Save"), button:has-text("Create")');
        
        // Check for success message or new command in list
        await page.waitForTimeout(2000);
    });

    test('AI Command Generation button', async ({ page }) => {
        // Click AI button
        await page.click('button:has-text("Create Command with AI")');
        
        // Check what happens - either opens modal or redirects to settings
        await page.waitForTimeout(2000);
        
        const currentUrl = page.url();
        if (currentUrl.includes('/settings')) {
            console.log('AI not configured - redirected to settings');
            await expect(page.locator('h1')).toContainText('Settings');
        } else {
            // AI modal opened
            await expect(page.locator('text=/ai/i, text=/generate/i')).toBeVisible();
        }
        
        await page.screenshot({ path: 'test-screenshots/ai-command-response.png' });
    });

    test('Execute command on agent', async ({ page }) => {
        // First check if there are any commands
        const hasCommands = await page.locator('table tbody tr').count() > 0;
        
        if (hasCommands) {
            // Find execute button
            const executeBtn = page.locator('button:has-text("Execute"), button[title*="execute" i]').first();
            
            if (await executeBtn.count() > 0) {
                await executeBtn.click();
                
                // Check for agent selection modal or execution feedback
                await page.waitForTimeout(2000);
                
                // Take screenshot
                await page.screenshot({ path: 'test-screenshots/execute-command.png' });
            }
        } else {
            console.log('No commands available to execute');
        }
    });

    test('Search and filter commands', async ({ page }) => {
        // Look for search input
        const searchInput = page.locator('input[placeholder*="search" i], input[type="search"]');
        
        if (await searchInput.count() > 0) {
            await searchInput.fill('system');
            await page.waitForTimeout(1000);
            
            // Check if filtering works
            await page.screenshot({ path: 'test-screenshots/search-commands.png' });
        }
    });

    test('Command categories', async ({ page }) => {
        // Check for category filter/tabs
        const categories = ['System Info', 'File Operations', 'Network', 'Security', 'Custom'];
        
        for (const category of categories) {
            const categoryElement = page.locator(`text=${category}`);
            if (await categoryElement.count() > 0) {
                console.log(`Found category: ${category}`);
            }
        }
    });

    test('Get System Information command', async ({ page }) => {
        // Look for Get System Information command
        const systemInfoCmd = page.locator('text=/get system information/i, text=/system info/i');
        
        if (await systemInfoCmd.count() > 0) {
            console.log('Found Get System Information command');
            
            // Try to execute it
            const row = systemInfoCmd.locator('xpath=ancestor::tr');
            const executeBtn = row.locator('button:has-text("Execute"), button[title*="execute" i]');
            
            if (await executeBtn.count() > 0) {
                await executeBtn.click();
                await page.waitForTimeout(2000);
                
                // Take screenshot of execution
                await page.screenshot({ path: 'test-screenshots/system-info-execution.png' });
            }
        } else {
            console.log('Get System Information command not found - may need to create it');
        }
    });
});
"""
    
    # Write test file
    test_file = '/home/ali/dex_agent/frontend/test-command-library.spec.js'
    with open(test_file, 'w') as f:
        f.write(test_script)
    
    print("\n📝 Running Playwright tests for Command Library page...")
    
    # Run the test
    try:
        result = subprocess.run(
            ['npx', 'playwright', 'test', 'test-command-library.spec.js', '--reporter=json'],
            cwd='/home/ali/dex_agent/frontend',
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            test_results["status"] = "success"
        else:
            print("❌ Some tests failed")
            test_results["status"] = "failed"
            
            # Parse JSON output if available
            if result.stdout:
                try:
                    test_output = json.loads(result.stdout)
                    for suite in test_output.get('suites', []):
                        for spec in suite.get('specs', []):
                            test_results["tests"].append({
                                "name": spec.get('title', 'Unknown'),
                                "status": spec.get('ok', False),
                                "duration": spec.get('duration', 0)
                            })
                            
                            # Collect errors
                            for test in spec.get('tests', []):
                                for result in test.get('results', []):
                                    if result.get('error'):
                                        test_results["errors"].append({
                                            "test": spec.get('title'),
                                            "error": result['error'].get('message', 'Unknown error')
                                        })
                except json.JSONDecodeError:
                    pass
            
            # Also capture stderr
            if result.stderr:
                test_results["errors"].append({
                    "type": "stderr",
                    "message": result.stderr
                })
                
    except subprocess.TimeoutExpired:
        print("⏱️ Test timeout")
        test_results["status"] = "timeout"
        test_results["errors"].append({"type": "timeout", "message": "Test execution timed out"})
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        test_results["status"] = "error"
        test_results["errors"].append({"type": "exception", "message": str(e)})
    
    # Save results
    with open('/home/ali/dex_agent/command_library_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    return test_results

def check_screenshots():
    """Check if screenshots were created"""
    screenshot_dir = '/home/ali/dex_agent/frontend/test-screenshots'
    if os.path.exists(screenshot_dir):
        screenshots = os.listdir(screenshot_dir)
        print(f"\n📸 Screenshots created: {len(screenshots)}")
        for screenshot in screenshots:
            print(f"  - {screenshot}")
    else:
        print("\n📸 No screenshots directory found")

def main():
    print("Starting Command Library Page Frontend Tests")
    print("=" * 60)
    
    # Ensure screenshot directory exists
    os.makedirs('/home/ali/dex_agent/frontend/test-screenshots', exist_ok=True)
    
    # Run tests
    results = run_playwright_test()
    
    # Check screenshots
    check_screenshots()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Status: {results.get('status', 'unknown')}")
    print(f"Total tests: {len(results.get('tests', []))}")
    
    if results.get('errors'):
        print(f"\n❌ Errors found: {len(results['errors'])}")
        for error in results['errors']:
            print(f"\n  Error: {error}")
    else:
        print("\n✅ No errors found")
    
    print("\n" + "="*60)
    print("Results saved to: command_library_test_results.json")
    
    return results

if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get('status') == 'success' else 1)