# DexAgents Modern Windows Agent

Modern, robust Windows agent for DexAgents with improved GUI, better error handling, and enhanced functionality.

## 🚀 Features

### Modern GUI Interface
- **Clean Design**: Intuitive, modern user interface
- **Real-time Monitoring**: Live system metrics display
- **Status Indicators**: Visual connection and agent status
- **Activity Logging**: Comprehensive logging with timestamps
- **Responsive Layout**: Adapts to different screen sizes

### Enhanced Functionality
- **Better Error Handling**: Comprehensive error catching and reporting
- **Async Operations**: Non-blocking connection tests and updates
- **Configurable Settings**: Flexible configuration options
- **System Monitoring**: CPU, memory, disk, and network monitoring
- **Log Management**: Automatic log rotation and backup

### Security & Reliability
- **Secure Token Handling**: Masked API token display with toggle
- **Connection Validation**: Robust connection testing
- **Graceful Degradation**: Continues operation despite network issues
- **Resource Management**: Efficient memory and CPU usage

## 📋 Requirements

- Windows 10/11 (64-bit)
- Python 3.8+ (for development)
- 4GB RAM minimum
- 100MB free disk space
- Internet connection for server communication

## 🔧 Installation

### Option 1: Pre-built Executable
1. Download `DexAgents_Modern_Installer.zip`
2. Extract to desired location
3. Run `DexAgentsModernAgent.exe` as administrator

### Option 2: Build from Source
```bash
# Clone repository
git clone <repository-url>
cd dexagents/agent

# Install dependencies
pip install -r modern_requirements.txt

# Build executable
python modern_build_exe.py

# Run directly (for development)
python modern_agent_gui.py
```

## ⚙️ Configuration

### Connection Settings
- **Server URL**: Your DexAgents server URL (e.g., `http://localhost:8000`)
- **API Token**: Your server API token (required for authentication)
- **Agent Name**: Custom name for this agent instance
- **Tags**: Comma-separated tags for categorization

### Options
- **Auto-start with Windows**: Automatically start agent on system boot
- **Run as Windows Service**: Run as a Windows service (advanced)

### Advanced Settings
```json
{
  "update_interval": 30,
  "connection_timeout": 10,
  "log_level": "INFO",
  "max_log_size": 10485760,
  "backup_logs": true
}
```

## 🎯 Usage

### Starting the Agent
1. Launch `DexAgentsModernAgent.exe`
2. Enter server URL and API token
3. Configure agent name and tags
4. Click "Start Agent"

### Monitoring
- **Connection Status**: Green = connected, Red = disconnected
- **Agent Status**: Shows if agent is running or stopped
- **System Metrics**: Real-time CPU, memory, and disk usage
- **Activity Log**: Scrollable log with timestamps

### Troubleshooting
- **Test Connection**: Verify server connectivity
- **Open Logs**: View detailed log files
- **Web Interface**: Open browser to server dashboard

## 📊 System Monitoring

### Metrics Tracked
- **CPU Usage**: Real-time processor utilization
- **Memory Usage**: RAM consumption and availability
- **Disk Usage**: Storage space monitoring
- **Network Status**: Connection health

### Data Collection
- System information (hostname, OS version)
- Performance metrics
- Network statistics
- Custom agent metadata

## 🔍 Troubleshooting

### Common Issues

#### Connection Problems
```
Error: Connection refused
Solution: Verify server is running and accessible
```

```
Error: Invalid API token
Solution: Check token in server configuration
```

#### Agent Won't Start
```
Error: Permission denied
Solution: Run as administrator
```

```
Error: Missing dependencies
Solution: Reinstall or rebuild executable
```

### Log Analysis
Logs are stored in `logs/agent.log`:
```
[14:30:15] INFO: Modern DexAgents Windows Agent GUI started
[14:30:20] INFO: Connection test successful
[14:30:25] INFO: Agent registered successfully
[14:30:55] INFO: Status update sent successfully
```

### Debug Mode
Enable debug logging in configuration:
```json
{
  "log_level": "DEBUG"
}
```

## 🔧 Development

### Project Structure
```
agent/
├── modern_agent_gui.py      # Main GUI application
├── modern_build_exe.py      # Build script
├── modern_requirements.txt   # Dependencies
├── config.json              # Configuration file
├── logs/                    # Log directory
└── README_MODERN.md         # This file
```

### Building
```bash
# Install dependencies
pip install -r modern_requirements.txt

# Build executable
python modern_build_exe.py

# Test locally
python modern_agent_gui.py
```

### Code Features
- **Type Hints**: Full type annotation support
- **Error Handling**: Comprehensive exception management
- **Async Operations**: Non-blocking background tasks
- **Logging**: Structured logging with multiple levels
- **Configuration**: JSON-based configuration management

## 📈 Performance

### Resource Usage
- **Memory**: ~50MB typical usage
- **CPU**: <1% when idle, ~5% during updates
- **Disk**: Minimal I/O, logs rotate automatically
- **Network**: Configurable update intervals

### Optimization
- Efficient threading model
- Minimal UI updates
- Smart connection pooling
- Automatic resource cleanup

## 🔒 Security

### Features
- **Token Masking**: API tokens hidden by default
- **Secure Storage**: Configuration file protection
- **Network Security**: HTTPS support for connections
- **Access Control**: Administrator privileges required

### Best Practices
- Use strong API tokens
- Run as administrator
- Keep executable updated
- Monitor log files regularly

## 📝 Changelog

### Version 3.0.0 (Current)
- Complete GUI rewrite with modern design
- Enhanced error handling and logging
- Improved system monitoring
- Better configuration management
- Async operations for better performance

### Version 2.x (Legacy)
- Basic tkinter GUI
- Simple configuration
- Limited error handling

## 🤝 Support

### Getting Help
1. Check the logs for error messages
2. Verify server connectivity
3. Review configuration settings
4. Test with connection button

### Reporting Issues
Include the following information:
- Agent version
- Windows version
- Error messages from logs
- Steps to reproduce

## 📄 License

This project is part of the DexAgents system. See main project for license information.

---

**Modern DexAgents Windows Agent v3.0.0**  
Built with Python, tkinter, and modern development practices. 