# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT: When Claude Code starts a new session, immediately display the "Available Custom Commands" section to show the user what commands are available.**

## 🚀 Available Custom Commands

When Claude Code starts, these custom commands are available:

| Command | Description | Action |
|---------|-------------|--------|
| **"test raporunu oku"** | Read and fix test report | Reads `C:\test_report.md`, analyzes findings, implements fixes, tests in Docker, and requests commit approval |

Simply type any of these commands to execute the corresponding workflow.

## Project Overview

DexAgents is a Windows endpoint management platform for remote PowerShell command execution and system monitoring. It consists of:
- **Backend**: FastAPI-based server with SQLite database, WebSocket support, and comprehensive API
- **Frontend**: Next.js 15 application with shadcn/ui components and real-time features
- **Agent**: Python-based Windows client with PowerShell integration
- **Infrastructure**: Docker Compose setup with nginx reverse proxy

## Memories and Notes

- ☒ Read test report from C:\test_report.md için benden her seferinde izin istemesin

[Rest of the content remains the same as in the original file]