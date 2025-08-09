#!/usr/bin/env node

/**
 * Test script for Playwright MCP Server
 * This script tests the MCP server by simulating the MCP protocol
 */

const { spawn } = require('child_process');
const path = require('path');

// Path to the built MCP server
const serverPath = path.join(__dirname, 'mcp-server-playwright', 'dist', 'index.js');

console.log('Testing Playwright MCP Server...');
console.log('Server path:', serverPath);

// Start the MCP server
const mcpServer = spawn('node', [serverPath], {
  stdio: ['pipe', 'pipe', 'pipe']
});

// Handle server output
mcpServer.stdout.on('data', (data) => {
  console.log('Server stdout:', data.toString());
});

mcpServer.stderr.on('data', (data) => {
  console.log('Server stderr:', data.toString());
});

mcpServer.on('error', (error) => {
  console.error('Failed to start MCP server:', error);
  process.exit(1);
});

mcpServer.on('close', (code) => {
  console.log(`MCP server exited with code ${code}`);
});

// Send test requests
async function testServer() {
  // Send initialize request
  const initRequest = {
    jsonrpc: '2.0',
    method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: {
        name: 'test-client',
        version: '1.0.0'
      }
    },
    id: 1
  };

  console.log('\nSending initialize request...');
  mcpServer.stdin.write(JSON.stringify(initRequest) + '\n');

  // Wait a bit then send list tools request
  setTimeout(() => {
    const listToolsRequest = {
      jsonrpc: '2.0',
      method: 'tools/list',
      params: {},
      id: 2
    };

    console.log('\nSending list tools request...');
    mcpServer.stdin.write(JSON.stringify(listToolsRequest) + '\n');

    // Close after testing
    setTimeout(() => {
      console.log('\nTest complete. Closing server...');
      mcpServer.stdin.end();
      process.exit(0);
    }, 2000);
  }, 1000);
}

// Start testing after server is ready
setTimeout(testServer, 500);

console.log('\nMCP Server is starting...');
console.log('If successful, you should see the server respond with available tools.');
console.log('\nTo use in Claude Desktop:');
console.log('1. Copy claude_mcp_config.json to ~/.config/claude/claude_desktop_config.json');
console.log('2. Restart Claude Desktop');
console.log('3. The Playwright tools will be available in Claude');