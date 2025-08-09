# Playwright MCP Server

This is a Model Context Protocol (MCP) server that enables Claude to control web browsers using Playwright.

## Setup

1. **Install dependencies:**
   ```bash
   cd mcp-server-playwright
   npm install
   ```

2. **Build the server:**
   ```bash
   npm run build
   ```

3. **Configure Claude Desktop:**
   
   Copy the MCP configuration to Claude's config directory:
   
   **On Linux/Mac:**
   ```bash
   mkdir -p ~/.config/claude
   cp ../claude_mcp_config.json ~/.config/claude/claude_desktop_config.json
   ```
   
   **On Windows:**
   ```powershell
   mkdir -Force $env:APPDATA\Claude
   copy ..\claude_mcp_config.json $env:APPDATA\Claude\claude_desktop_config.json
   ```

4. **Restart Claude Desktop** to load the MCP server.

## Available Tools

Once configured, Claude will have access to the following Playwright tools:

- `playwright_navigate` - Navigate to a URL
- `playwright_click` - Click an element
- `playwright_fill` - Fill an input field
- `playwright_select` - Select dropdown option
- `playwright_wait` - Wait for element or timeout
- `playwright_screenshot` - Take a screenshot
- `playwright_evaluate` - Execute JavaScript
- `playwright_get_text` - Get element text
- `playwright_get_attribute` - Get element attribute
- `playwright_wait_for_navigation` - Wait for page navigation
- `playwright_close` - Close the browser

## Usage Example

You can ask Claude to:
- "Open google.com and search for something"
- "Test the login page at localhost:3000"
- "Take a screenshot of the current page"
- "Fill out a form on the website"

## Environment Variables

- `PLAYWRIGHT_HEADLESS` - Set to `false` to see the browser (default: `true`)

## Development

To run in development mode:
```bash
npm run dev
```

## Troubleshooting

If the MCP server doesn't appear in Claude:
1. Check that the config file is in the right location
2. Restart Claude Desktop completely
3. Check Claude's developer console for errors
4. Verify the server builds without errors: `npm run build`