#!/usr/bin/env python3
"""
DexAgent - Windows PowerShell Agent
===================================

Standalone Windows agent for DexAgents system.
Connects to DexAgents server via WebSocket and executes PowerShell commands.

Requirements:
- Python 3.8+
- websockets: pip install websockets
- psutil: pip install psutil  
- requests: pip install requests

Usage:
1. Configure the settings below
2. Run: python dexagent_windows.py
3. Agent will show GUI and connect to server

Author: DexAgents System
"""

import asyncio
import websockets
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import time
import requests
import psutil
import platform
import socket
import subprocess
import logging
import sys
import os
from datetime import datetime
import uuid

# ================================
# CONFIGURATION - EDIT THESE VALUES
# ================================

CONFIG = {
    # Server connection settings
    "server_url": "ws://localhost:8080",  # Change to your server URL
    "api_token": "your-api-token-here",   # Change to your API token
    
    # Agent identification
    "agent_name": "Windows-Agent",        # Custom agent name
    "tags": ["windows", "desktop"],       # Agent tags
    
    # Behavior settings
    "auto_start": True,                   # Auto-connect on startup
    "reconnect_interval": 30,             # Reconnection interval (seconds)
    "heartbeat_interval": 60,             # Heartbeat interval (seconds)
    
    # Logging
    "log_level": "INFO",                  # DEBUG, INFO, WARNING, ERROR
    "log_file": "dexagent.log",          # Log file path
}

# ================================
# LOGGING SETUP
# ================================

# Create logger
logger = logging.getLogger('DexAgent')
logger.setLevel(getattr(logging, CONFIG['log_level']))

# Create formatters
console_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File handler
try:
    file_handler = logging.FileHandler(CONFIG['log_file'])
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
except Exception as e:
    logger.warning(f"Could not create log file: {e}")

# ================================
# MAIN AGENT CLASS
# ================================

class DexAgentWindows:
    def __init__(self):
        self.config = CONFIG
        self.running = False
        self.websocket = None
        self.agent_id = str(uuid.uuid4())
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        
        # GUI components
        self.root = None
        self.status_label = None
        self.connect_button = None
        self.log_text = None
        
        # Background tasks
        self.heartbeat_task = None
        self.reconnect_task = None
        
    def setup_gui(self):
        """Setup the GUI interface"""
        self.root = tk.Tk()
        self.root.title(f"DexAgent - {self.config['agent_name']}")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text=f"DexAgent - {self.config['agent_name']}", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Connection Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(
            status_frame, 
            text="Disconnected", 
            foreground="red",
            font=('Arial', 10, 'bold')
        )
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Server info
        ttk.Label(status_frame, text="Server:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Label(
            status_frame, 
            text=self.config['server_url']
        ).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Agent info
        ttk.Label(status_frame, text="Agent ID:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Label(
            status_frame, 
            text=self.agent_id[:8] + "..."
        ).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Control buttons frame
        button_frame = ttk.Frame(status_frame)
        button_frame.grid(row=0, column=2, rowspan=3, padx=(20, 0))
        
        self.connect_button = ttk.Button(
            button_frame, 
            text="Connect", 
            command=self.toggle_connection,
            width=12
        )
        self.connect_button.pack(pady=2)
        
        ttk.Button(
            button_frame, 
            text="Config", 
            command=self.show_config,
            width=12
        ).pack(pady=2)
        
        ttk.Button(
            button_frame, 
            text="Test", 
            command=self.test_connection,
            width=12
        ).pack(pady=2)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text with scrollbar
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=15, 
            width=80,
            font=('Consolas', 9),
            state=tk.DISABLED
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log control buttons
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        ttk.Button(
            log_button_frame, 
            text="Clear Log", 
            command=self.clear_log
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            log_button_frame, 
            text="Save Log", 
            command=self.save_log
        ).pack(side=tk.LEFT, padx=5)
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initial log message
        self.log("DexAgent Windows initialized")
        self.log(f"Agent ID: {self.agent_id}")
        self.log(f"Server: {self.config['server_url']}")
        
    def log(self, message, level="INFO"):
        """Add message to GUI log and logger"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}"
        
        # Log to file/console
        getattr(logger, level.lower(), logger.info)(message)
        
        # Log to GUI
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, log_message + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        
    def clear_log(self):
        """Clear the GUI log"""
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
            
    def save_log(self):
        """Save log to file"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    content = self.log_text.get(1.0, tk.END)
                    f.write(content)
                self.log(f"Log saved to {filename}")
        except Exception as e:
            self.log(f"Failed to save log: {e}", "ERROR")
            
    def show_config(self):
        """Show configuration dialog"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Agent Configuration")
        config_window.geometry("500x400")
        config_window.resizable(False, False)
        
        # Center the window
        config_window.transient(self.root)
        config_window.grab_set()
        
        frame = ttk.Frame(config_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Configuration entries
        entries = {}
        
        # Server URL
        ttk.Label(frame, text="Server URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entries['server_url'] = ttk.Entry(frame, width=40)
        entries['server_url'].grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        entries['server_url'].insert(0, self.config['server_url'])
        
        # API Token
        ttk.Label(frame, text="API Token:").grid(row=1, column=0, sticky=tk.W, pady=5)
        entries['api_token'] = ttk.Entry(frame, width=40, show="*")
        entries['api_token'].grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        entries['api_token'].insert(0, self.config['api_token'])
        
        # Agent Name
        ttk.Label(frame, text="Agent Name:").grid(row=2, column=0, sticky=tk.W, pady=5)
        entries['agent_name'] = ttk.Entry(frame, width=40)
        entries['agent_name'].grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        entries['agent_name'].insert(0, self.config['agent_name'])
        
        # Tags
        ttk.Label(frame, text="Tags (comma-separated):").grid(row=3, column=0, sticky=tk.W, pady=5)
        entries['tags'] = ttk.Entry(frame, width=40)
        entries['tags'].grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        entries['tags'].insert(0, ", ".join(self.config['tags']))
        
        # Auto-start checkbox
        auto_start_var = tk.BooleanVar(value=self.config['auto_start'])
        ttk.Checkbutton(
            frame, 
            text="Auto-connect on startup", 
            variable=auto_start_var
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_config():
            try:
                # Update configuration
                self.config['server_url'] = entries['server_url'].get().strip()
                self.config['api_token'] = entries['api_token'].get().strip()
                self.config['agent_name'] = entries['agent_name'].get().strip()
                self.config['tags'] = [tag.strip() for tag in entries['tags'].get().split(',') if tag.strip()]
                self.config['auto_start'] = auto_start_var.get()
                
                # Update GUI
                self.root.title(f"DexAgent - {self.config['agent_name']}")
                
                self.log("Configuration updated")
                config_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")
                
        ttk.Button(button_frame, text="Save", command=save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=config_window.destroy).pack(side=tk.LEFT, padx=5)
        
    def test_connection(self):
        """Test connection to server"""
        self.log("Testing connection...")
        
        def test_thread():
            try:
                # Test HTTP endpoint first
                http_url = self.config['server_url'].replace('ws://', 'http://').replace('wss://', 'https://')
                if not http_url.endswith('/api/v1/system/health'):
                    http_url = http_url.rstrip('/') + '/api/v1/system/health'
                
                response = requests.get(http_url, timeout=10)
                if response.status_code == 200:
                    self.log(f"✓ HTTP connection successful: {response.status_code}")
                else:
                    self.log(f"⚠ HTTP response: {response.status_code}", "WARNING")
                    
            except requests.exceptions.RequestException as e:
                self.log(f"✗ HTTP connection failed: {e}", "ERROR")
                
            # Test WebSocket connection
            try:
                import asyncio
                
                async def test_ws():
                    ws_url = self.config['server_url']
                    if not ws_url.endswith('/ws'):
                        ws_url = ws_url.rstrip('/') + '/api/v1/ws'
                    
                    async with websockets.connect(ws_url, timeout=10) as websocket:
                        # Send test registration
                        test_msg = {
                            "type": "register",
                            "agent_id": f"test-{self.agent_id[:8]}",
                            "agent_name": f"test-{self.config['agent_name']}",
                            "tags": ["test"],
                            "system_info": self.get_system_info()
                        }
                        await websocket.send(json.dumps(test_msg))
                        self.log("✓ WebSocket connection successful")
                        
                asyncio.run(test_ws())
                
            except Exception as e:
                self.log(f"✗ WebSocket connection failed: {e}", "ERROR")
                
        threading.Thread(target=test_thread, daemon=True).start()
        
    def toggle_connection(self):
        """Toggle connection to server"""
        if self.running:
            self.disconnect()
        else:
            self.connect()
            
    def connect(self):
        """Connect to server"""
        if not self.running:
            self.running = True
            self.reconnect_attempts = 0
            self.status_label.config(text="Connecting...", foreground="orange")
            self.connect_button.config(text="Disconnect")
            self.log("Connecting to server...")
            
            # Start WebSocket connection in background thread
            thread = threading.Thread(target=self.websocket_worker, daemon=True)
            thread.start()
            
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        
        # Cancel background tasks
        if self.heartbeat_task and not self.heartbeat_task.done():
            self.heartbeat_task.cancel()
        if self.reconnect_task and not self.reconnect_task.done():
            self.reconnect_task.cancel()
            
        # Close WebSocket
        if self.websocket:
            try:
                asyncio.create_task(self.websocket.close())
            except:
                pass
            self.websocket = None
            
        # Update GUI
        self.status_label.config(text="Disconnected", foreground="red")
        self.connect_button.config(text="Connect")
        self.log("Disconnected from server")
        
    def websocket_worker(self):
        """WebSocket connection worker (runs in background thread)"""
        try:
            # Run the async WebSocket handler
            asyncio.run(self.websocket_handler())
        except Exception as e:
            self.log(f"WebSocket worker error: {e}", "ERROR")
            if self.running:
                self.schedule_reconnect()
                
    async def websocket_handler(self):
        """Handle WebSocket connection and messages"""
        ws_url = self.config['server_url']
        if not ws_url.endswith('/ws'):
            ws_url = ws_url.rstrip('/') + '/api/v1/ws'
            
        try:
            async with websockets.connect(ws_url) as websocket:
                self.websocket = websocket
                self.reconnect_attempts = 0
                
                # Update GUI status
                self.root.after(0, lambda: self.status_label.config(text="Connected", foreground="green"))
                self.root.after(0, lambda: self.log("Connected to server"))
                
                # Send registration
                registration = {
                    "type": "register",
                    "agent_id": self.agent_id,
                    "agent_name": self.config['agent_name'],
                    "tags": self.config['tags'],
                    "system_info": self.get_system_info()
                }
                await websocket.send(json.dumps(registration))
                self.root.after(0, lambda: self.log("Agent registered with server"))
                
                # Start heartbeat task
                self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())
                
                # Listen for messages
                async for message in websocket:
                    if not self.running:
                        break
                        
                    try:
                        data = json.loads(message)
                        await self.handle_message(data)
                    except json.JSONDecodeError as e:
                        self.root.after(0, lambda: self.log(f"Invalid JSON received: {e}", "ERROR"))
                    except Exception as e:
                        self.root.after(0, lambda: self.log(f"Message handling error: {e}", "ERROR"))
                        
        except websockets.exceptions.ConnectionClosed:
            self.root.after(0, lambda: self.log("WebSocket connection closed"))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"WebSocket connection error: {e}", "ERROR"))
        finally:
            self.websocket = None
            if self.running:
                self.schedule_reconnect()
                
    async def handle_message(self, data):
        """Handle incoming WebSocket messages"""
        message_type = data.get('type', 'unknown')
        
        if message_type == 'command':
            self.root.after(0, lambda: self.log(f"Executing command: {data.get('command', '')[:50]}..."))
            result = await self.execute_command(data.get('command', ''))
            
            # Send response
            response = {
                "type": "command_result",
                "command_id": data.get('command_id'),
                "result": result
            }
            
            if self.websocket:
                await self.websocket.send(json.dumps(response))
                
        elif message_type == 'ping':
            # Respond to ping
            pong = {"type": "pong", "timestamp": time.time()}
            if self.websocket:
                await self.websocket.send(json.dumps(pong))
                
        elif message_type == 'system_info_request':
            # Send system information
            sys_info = {
                "type": "system_info",
                "data": self.get_system_info()
            }
            if self.websocket:
                await self.websocket.send(json.dumps(sys_info))
                
        else:
            self.root.after(0, lambda: self.log(f"Unknown message type: {message_type}", "WARNING"))
            
    async def execute_command(self, command):
        """Execute PowerShell command"""
        try:
            # Log command execution
            self.root.after(0, lambda: self.log(f"Executing: {command}"))
            
            # Execute PowerShell command
            process = await asyncio.create_subprocess_shell(
                f'powershell.exe -Command "{command}"',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            
            stdout, stderr = await process.communicate()
            
            result = {
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "return_code": process.returncode,
                "execution_time": time.time()
            }
            
            # Log result
            status = "completed" if process.returncode == 0 else "failed"
            self.root.after(0, lambda: self.log(f"Command {status} (exit code: {process.returncode})"))
            
            return result
            
        except Exception as e:
            error_result = {
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": time.time()
            }
            self.root.after(0, lambda: self.log(f"Command execution error: {e}", "ERROR"))
            return error_result
            
    async def heartbeat_loop(self):
        """Send periodic heartbeat to server"""
        while self.running and self.websocket:
            try:
                heartbeat = {
                    "type": "heartbeat",
                    "timestamp": time.time(),
                    "system_info": self.get_system_info()
                }
                await self.websocket.send(json.dumps(heartbeat))
                await asyncio.sleep(self.config['heartbeat_interval'])
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Heartbeat error: {e}", "ERROR"))
                break
                
    def schedule_reconnect(self):
        """Schedule reconnection attempt"""
        if not self.running:
            return
            
        self.reconnect_attempts += 1
        if self.reconnect_attempts > self.max_reconnect_attempts:
            self.root.after(0, lambda: self.log("Max reconnection attempts reached", "ERROR"))
            self.root.after(0, self.disconnect)
            return
            
        delay = min(self.config['reconnect_interval'] * self.reconnect_attempts, 300)  # Max 5 minutes
        self.root.after(0, lambda: self.log(f"Reconnecting in {delay} seconds... (attempt {self.reconnect_attempts})"))
        self.root.after(0, lambda: self.status_label.config(text=f"Reconnecting ({self.reconnect_attempts})...", foreground="orange"))
        
        def reconnect():
            if self.running:
                thread = threading.Thread(target=self.websocket_worker, daemon=True)
                thread.start()
                
        # Schedule reconnection
        self.root.after(delay * 1000, reconnect)
        
    def get_system_info(self):
        """Get system information"""
        try:
            # Get CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Get memory info
            memory = psutil.virtual_memory()
            
            # Get disk usage for C: drive
            try:
                disk = psutil.disk_usage('C:\\')
                disk_usage = (disk.used / disk.total) * 100
            except:
                disk_usage = 0
                
            # Get network interfaces
            network_interfaces = []
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        network_interfaces.append({
                            "interface": interface,
                            "ip": addr.address,
                            "netmask": addr.netmask
                        })
                        
            return {
                "hostname": socket.gethostname(),
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "python_version": sys.version,
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "disk_usage": disk_usage,
                "network_interfaces": network_interfaces,
                "uptime": time.time() - psutil.boot_time(),
                "agent_version": "1.0.0",
                "last_updated": time.time()
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {
                "hostname": socket.gethostname(),
                "platform": platform.system(),
                "error": str(e)
            }
            
    def on_closing(self):
        """Handle window close event"""
        if messagebox.askokcancel("Quit", "Do you want to quit DexAgent?"):
            self.disconnect()
            self.root.destroy()
            
    def run(self):
        """Run the agent"""
        try:
            # Setup GUI
            self.setup_gui()
            
            # Auto-connect if enabled
            if self.config['auto_start']:
                self.root.after(1000, self.connect)  # Connect after 1 second
                
            # Start GUI main loop
            self.root.mainloop()
            
        except KeyboardInterrupt:
            self.log("Received interrupt signal")
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            if self.root:
                messagebox.showerror("Error", f"Agent error: {e}")
        finally:
            self.disconnect()
            logger.info("DexAgent shutdown complete")

# ================================
# MAIN EXECUTION
# ================================

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    try:
        import websockets
    except ImportError:
        missing.append("websockets")
        
    try:
        import psutil
    except ImportError:
        missing.append("psutil")
        
    try:
        import requests
    except ImportError:
        missing.append("requests")
        
    if missing:
        print("ERROR: Missing required dependencies!")
        print("Please install them using:")
        print(f"pip install {' '.join(missing)}")
        print("\nRequired packages:")
        print("- websockets: For WebSocket communication")
        print("- psutil: For system information")
        print("- requests: For HTTP requests")
        return False
        
    return True

def main():
    """Main entry point"""
    print("DexAgent - Windows PowerShell Agent")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return
        
    # Check Python version
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        input("Press Enter to exit...")
        return
        
    try:
        # Create and run agent
        agent = DexAgentWindows()
        agent.run()
        
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        print(f"ERROR: Failed to start agent: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()