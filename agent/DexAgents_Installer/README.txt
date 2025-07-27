# DexAgents Installer

## Installation Guide

### Prerequisites
- Windows 10/11
- Python 3.11+ (will be installed automatically if needed)
- Internet connection for dependency download

### Installation Steps

1. **Run Installer**
   - Double-click `DexAgentsInstaller.exe`
   - The installer will open with a modern GUI

2. **Configure Server Settings**
   - Enter your DexAgents server URL (e.g., http://localhost:8000)
   - Enter your API token
   - Click "Test Connection" to verify settings

3. **Configure Agent Settings**
   - Enter a custom agent name
   - Add tags (comma-separated)
   - Choose installation options

4. **Install**
   - Click "Install DexAgents" when connection test is successful
   - The installer will:
     - Copy files to %USERPROFILE%\DexAgents
     - Install Python dependencies
     - Create desktop shortcut
     - Configure auto-start (if enabled)

### Features

✅ **Connection Testing**
- Tests server health endpoint
- Validates API token
- Real-time status feedback

✅ **Smart Installation**
- Automatic dependency installation
- Desktop shortcut creation
- Auto-start configuration
- Windows service support

✅ **User-Friendly Interface**
- Modern GUI design
- Progress indicators
- Error handling
- Success notifications

### Installation Directory

The agent will be installed to: `%USERPROFILE%\DexAgents`

Files installed:
- `agent_gui.py` - Main agent application
- `config.json` - Agent configuration
- `requirements.txt` - Python dependencies
- `start_agent.bat` - Startup script
- `logs/` - Log directory

### Configuration

The installer creates a `config.json` file with your settings:
```json
{
    "server_url": "http://your-server:8000",
    "api_token": "your-token",
    "agent_name": "your-agent-name",
    "tags": ["windows", "installed"],
    "auto_start": true,
    "run_as_service": false
}
```

### Troubleshooting

**Connection Test Fails:**
- Verify server URL is correct
- Check if server is running
- Verify API token is valid
- Check firewall settings

**Installation Fails:**
- Run as administrator
- Check disk space
- Verify Python installation
- Check antivirus software

**Agent Won't Start:**
- Check logs in %USERPROFILE%\DexAgents\logs
- Verify configuration file
- Check Python dependencies

### Support

For issues or questions:
1. Check the logs in the installation directory
2. Verify server connectivity
3. Review configuration settings
4. Contact system administrator

### Files

- `DexAgentsInstaller.exe` - Main installer executable
- `config_template.json` - Configuration template
- `README.txt` - This documentation

---
DexAgents Windows Endpoint Management Platform v2.1.4
