#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { chromium, Page, Browser, BrowserContext } from 'playwright';
import { z } from 'zod';

// Tool schemas
const NavigateSchema = z.object({
  url: z.string().describe('URL to navigate to'),
});

const ClickSchema = z.object({
  selector: z.string().describe('CSS selector or text to click'),
});

const FillSchema = z.object({
  selector: z.string().describe('CSS selector for input field'),
  value: z.string().describe('Value to fill'),
});

const SelectSchema = z.object({
  selector: z.string().describe('CSS selector for select element'),
  value: z.string().describe('Value to select'),
});

const WaitSchema = z.object({
  selector: z.string().optional().describe('CSS selector to wait for'),
  timeout: z.number().optional().default(30000).describe('Timeout in milliseconds'),
});

const ScreenshotSchema = z.object({
  path: z.string().optional().describe('Path to save screenshot'),
  fullPage: z.boolean().optional().default(false).describe('Capture full page'),
});

const EvaluateSchema = z.object({
  script: z.string().describe('JavaScript code to evaluate in browser context'),
});

const GetTextSchema = z.object({
  selector: z.string().describe('CSS selector to get text from'),
});

const GetAttributeSchema = z.object({
  selector: z.string().describe('CSS selector of element'),
  attribute: z.string().describe('Attribute name to get'),
});

const WaitForNavigationSchema = z.object({
  timeout: z.number().optional().default(30000).describe('Timeout in milliseconds'),
});

const CloseSchema = z.object({});

class PlaywrightServer {
  private server: Server;
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private page: Page | null = null;

  constructor() {
    this.server = new Server(
      {
        name: 'playwright-server',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  private async ensureBrowser() {
    if (!this.browser) {
      this.browser = await chromium.launch({
        headless: process.env.PLAYWRIGHT_HEADLESS !== 'false',
      });
      this.context = await this.browser.newContext();
      this.page = await this.context.newPage();
    }
    return this.page!;
  }

  private setupHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      const tools: Tool[] = [
        {
          name: 'playwright_navigate',
          description: 'Navigate to a URL',
          inputSchema: {
            type: 'object',
            properties: {
              url: { type: 'string', description: 'URL to navigate to' },
            },
            required: ['url'],
          },
        },
        {
          name: 'playwright_click',
          description: 'Click an element',
          inputSchema: {
            type: 'object',
            properties: {
              selector: { type: 'string', description: 'CSS selector or text to click' },
            },
            required: ['selector'],
          },
        },
        {
          name: 'playwright_fill',
          description: 'Fill an input field',
          inputSchema: {
            type: 'object',
            properties: {
              selector: { type: 'string', description: 'CSS selector for input field' },
              value: { type: 'string', description: 'Value to fill' },
            },
            required: ['selector', 'value'],
          },
        },
        {
          name: 'playwright_select',
          description: 'Select an option from a dropdown',
          inputSchema: {
            type: 'object',
            properties: {
              selector: { type: 'string', description: 'CSS selector for select element' },
              value: { type: 'string', description: 'Value to select' },
            },
            required: ['selector', 'value'],
          },
        },
        {
          name: 'playwright_wait',
          description: 'Wait for an element or timeout',
          inputSchema: {
            type: 'object',
            properties: {
              selector: { type: 'string', description: 'CSS selector to wait for' },
              timeout: { type: 'number', description: 'Timeout in milliseconds' },
            },
          },
        },
        {
          name: 'playwright_screenshot',
          description: 'Take a screenshot',
          inputSchema: {
            type: 'object',
            properties: {
              path: { type: 'string', description: 'Path to save screenshot' },
              fullPage: { type: 'boolean', description: 'Capture full page' },
            },
          },
        },
        {
          name: 'playwright_evaluate',
          description: 'Execute JavaScript in the browser',
          inputSchema: {
            type: 'object',
            properties: {
              script: { type: 'string', description: 'JavaScript code to evaluate' },
            },
            required: ['script'],
          },
        },
        {
          name: 'playwright_get_text',
          description: 'Get text content of an element',
          inputSchema: {
            type: 'object',
            properties: {
              selector: { type: 'string', description: 'CSS selector to get text from' },
            },
            required: ['selector'],
          },
        },
        {
          name: 'playwright_get_attribute',
          description: 'Get attribute value of an element',
          inputSchema: {
            type: 'object',
            properties: {
              selector: { type: 'string', description: 'CSS selector of element' },
              attribute: { type: 'string', description: 'Attribute name to get' },
            },
            required: ['selector', 'attribute'],
          },
        },
        {
          name: 'playwright_wait_for_navigation',
          description: 'Wait for navigation to complete',
          inputSchema: {
            type: 'object',
            properties: {
              timeout: { type: 'number', description: 'Timeout in milliseconds' },
            },
          },
        },
        {
          name: 'playwright_close',
          description: 'Close the browser',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
      ];

      return { tools };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'playwright_navigate': {
            const { url } = NavigateSchema.parse(args);
            const page = await this.ensureBrowser();
            await page.goto(url);
            return {
              content: [{ type: 'text', text: `Navigated to ${url}` }],
            };
          }

          case 'playwright_click': {
            const { selector } = ClickSchema.parse(args);
            const page = await this.ensureBrowser();
            
            // Try to click by text first, then by selector
            try {
              await page.getByText(selector).click();
            } catch {
              await page.click(selector);
            }
            
            return {
              content: [{ type: 'text', text: `Clicked on ${selector}` }],
            };
          }

          case 'playwright_fill': {
            const { selector, value } = FillSchema.parse(args);
            const page = await this.ensureBrowser();
            await page.fill(selector, value);
            return {
              content: [{ type: 'text', text: `Filled ${selector} with ${value}` }],
            };
          }

          case 'playwright_select': {
            const { selector, value } = SelectSchema.parse(args);
            const page = await this.ensureBrowser();
            await page.selectOption(selector, value);
            return {
              content: [{ type: 'text', text: `Selected ${value} in ${selector}` }],
            };
          }

          case 'playwright_wait': {
            const { selector, timeout } = WaitSchema.parse(args);
            const page = await this.ensureBrowser();
            
            if (selector) {
              await page.waitForSelector(selector, { timeout });
              return {
                content: [{ type: 'text', text: `Waited for ${selector}` }],
              };
            } else {
              await page.waitForTimeout(timeout);
              return {
                content: [{ type: 'text', text: `Waited for ${timeout}ms` }],
              };
            }
          }

          case 'playwright_screenshot': {
            const { path, fullPage } = ScreenshotSchema.parse(args);
            const page = await this.ensureBrowser();
            const screenshotPath = path || `screenshot-${Date.now()}.png`;
            await page.screenshot({ path: screenshotPath, fullPage });
            return {
              content: [{ type: 'text', text: `Screenshot saved to ${screenshotPath}` }],
            };
          }

          case 'playwright_evaluate': {
            const { script } = EvaluateSchema.parse(args);
            const page = await this.ensureBrowser();
            const result = await page.evaluate(script);
            return {
              content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
            };
          }

          case 'playwright_get_text': {
            const { selector } = GetTextSchema.parse(args);
            const page = await this.ensureBrowser();
            const text = await page.textContent(selector);
            return {
              content: [{ type: 'text', text: text || '' }],
            };
          }

          case 'playwright_get_attribute': {
            const { selector, attribute } = GetAttributeSchema.parse(args);
            const page = await this.ensureBrowser();
            const value = await page.getAttribute(selector, attribute);
            return {
              content: [{ type: 'text', text: value || '' }],
            };
          }

          case 'playwright_wait_for_navigation': {
            const { timeout } = WaitForNavigationSchema.parse(args);
            const page = await this.ensureBrowser();
            await page.waitForLoadState('networkidle', { timeout });
            return {
              content: [{ type: 'text', text: 'Navigation completed' }],
            };
          }

          case 'playwright_close': {
            if (this.browser) {
              await this.browser.close();
              this.browser = null;
              this.context = null;
              this.page = null;
            }
            return {
              content: [{ type: 'text', text: 'Browser closed' }],
            };
          }

          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error instanceof Error ? error.message : String(error)}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Playwright MCP server running on stdio');
  }
}

const server = new PlaywrightServer();
server.run().catch(console.error);