#!/usr/bin/env node

/**
 * Playwright Helper for Claude Code
 * Since Claude Code doesn't support MCP, this provides a CLI interface
 */

const { chromium } = require('playwright');

async function runPlaywright(action, ...args) {
  const browser = await chromium.launch({ 
    headless: process.env.HEADLESS !== 'false' 
  });
  const page = await browser.newPage();

  try {
    switch(action) {
      case 'navigate':
        await page.goto(args[0]);
        console.log(`Navigated to ${args[0]}`);
        break;
      
      case 'screenshot':
        const path = args[0] || `screenshot-${Date.now()}.png`;
        await page.screenshot({ path });
        console.log(`Screenshot saved to ${path}`);
        break;
      
      case 'click':
        await page.click(args[0]);
        console.log(`Clicked ${args[0]}`);
        break;
      
      case 'fill':
        await page.fill(args[0], args[1]);
        console.log(`Filled ${args[0]} with ${args[1]}`);
        break;
      
      case 'text':
        const text = await page.textContent(args[0]);
        console.log(text);
        break;
      
      case 'eval':
        const result = await page.evaluate(args[0]);
        console.log(JSON.stringify(result, null, 2));
        break;
      
      default:
        console.log('Available commands:');
        console.log('  navigate <url>');
        console.log('  screenshot [path]');
        console.log('  click <selector>');
        console.log('  fill <selector> <value>');
        console.log('  text <selector>');
        console.log('  eval <javascript>');
    }
  } finally {
    await browser.close();
  }
}

// Parse command line arguments
const [,, action, ...args] = process.argv;
if (action) {
  runPlaywright(action, ...args).catch(console.error);
} else {
  console.log('Usage: node playwright-helper.js <action> [args...]');
  runPlaywright('help');
}