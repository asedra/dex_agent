import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
import time
import socket
import platform
import psutil
import requests
import websockets
import asyncio
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DexAgentsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DexAgents Agent")
        self.root.geometry("800x600")
        
        # Agent configuration
        self.config = self.load_config()
        self.agent_id = None
        self.websocket = None
        self.websocket_task = None
        self.is_connected = False
        self.heartbeat_thread = None
        self.stop_heartbeat = False
        
        # Create GUI
        self.create_widgets()
        self.load_config_to_gui()
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
        
        return {
            "server_url": "http://localhost:8000",
            "api_token": "your-secret-key-here",
            "agent_name": socket.gethostname(),
            "tags": ["windows", "gui-agent"],
            "auto_start": False,
            "run_as_service": False
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                "server_url": self.server_url_var.get(),
                "api_token": self.api_token_var.get(),
                "agent_name": self.agent_name_var.get(),
                "tags": self.tags_var.get().split(',') if self.tags_var.get() else [],
                "auto_start": self.auto_start_var.get(),
                "run_as_service": self.run_as_service_var.get()
            }
            
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("Configuration saved")
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Connection Settings Frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="5")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        conn_frame.columnconfigure(1, weight=1)
        
        # Server URL
        ttk.Label(conn_frame, text="Server URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.server_url_var = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self.server_url_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # API Token
        ttk.Label(conn_frame, text="API Token:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.api_token_var = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self.api_token_var, width=50, show="*").grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Agent Name
        ttk.Label(conn_frame, text="Agent Name:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5))
        self.agent_name_var = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self.agent_name_var, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Tags
        ttk.Label(conn_frame, text="Tags:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5))
        self.tags_var = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self.tags_var, width=50).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Auto Start
        self.auto_start_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Auto-start agent", variable=self.auto_start_var).grid(row=0, column=0, sticky=tk.W)
        
        # Run as Service
        self.run_as_service_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Run as Windows service", variable=self.run_as_service_var).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Connection Status
        ttk.Label(status_frame, text="Connection:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.connection_status_var = tk.StringVar(value="Disconnected")
        self.connection_status_label = ttk.Label(status_frame, textvariable=self.connection_status_var, foreground="red")
        self.connection_status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Agent Status
        ttk.Label(status_frame, text="Agent:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.agent_status_var = tk.StringVar(value="Not registered")
        self.agent_status_label = ttk.Label(status_frame, textvariable=self.agent_status_var)
        self.agent_status_label.grid(row=1, column=1, sticky=tk.W)
        
        # System Info
        ttk.Label(status_frame, text="CPU:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5))
        self.cpu_var = tk.StringVar(value="0%")
        ttk.Label(status_frame, textvariable=self.cpu_var).grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(status_frame, text="Memory:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5))
        self.memory_var = tk.StringVar(value="0%")
        ttk.Label(status_frame, textvariable=self.memory_var).grid(row=3, column=1, sticky=tk.W)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        # Test Connection Button
        ttk.Button(buttons_frame, text="Test Connection", command=self.test_connection).pack(side=tk.LEFT, padx=(0, 5))
        
        # Save Config Button
        ttk.Button(buttons_frame, text="Save Config", command=self.save_config).pack(side=tk.LEFT, padx=(0, 5))
        
        # Start/Stop Button
        self.start_stop_button = ttk.Button(buttons_frame, text="Start Agent", command=self.toggle_agent)
        self.start_stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Log Text
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear Log Button
        ttk.Button(log_frame, text="Clear Log", command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
    
    def load_config_to_gui(self):
        """Load configuration into GUI fields"""
        self.server_url_var.set(self.config.get("server_url", ""))
        self.api_token_var.set(self.config.get("api_token", ""))
        self.agent_name_var.set(self.config.get("agent_name", ""))
        self.tags_var.set(",".join(self.config.get("tags", [])))
        self.auto_start_var.set(self.config.get("auto_start", False))
        self.run_as_service_var.set(self.config.get("run_as_service", False))
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        logger.info(message)
    
    def clear_log(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)
    
    def test_connection(self):
        """Test connection to server"""
        try:
            server_url = self.server_url_var.get()
            api_token = self.api_token_var.get()
            
            if not server_url or not api_token:
                messagebox.showerror("Error", "Please enter server URL and API token")
                return
            
            # Test HTTP connection
            headers = {"Authorization": f"Bearer {api_token}"}
            response = requests.get(f"{server_url}/", headers=headers, timeout=5)
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Connection test successful!")
                self.log_message("Connection test successful")
            else:
                messagebox.showerror("Error", f"Connection test failed: {response.status_code}")
                self.log_message(f"Connection test failed: {response.status_code}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed: {str(e)}")
            self.log_message(f"Connection test failed: {str(e)}")
    
    def register_agent(self):
        """Register agent with server"""
        try:
            server_url = self.server_url_var.get()
            api_token = self.api_token_var.get()
            agent_name = self.agent_name_var.get()
            tags = [tag.strip() for tag in self.tags_var.get().split(',') if tag.strip()]
            
            # Get system information
            system_info = {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": {partition.device: psutil.disk_usage(partition.mountpoint).percent 
                              for partition in psutil.disk_partitions() if partition.device}
            }
            
            # Register agent
            headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
            agent_data = {
                "hostname": agent_name,
                "os": platform.system(),
                "version": platform.version(),
                "tags": tags,
                "system_info": system_info
            }
            
            response = requests.post(
                f"{server_url}/api/v1/agents/register",
                headers=headers,
                json=agent_data,
                timeout=10
            )
            
            if response.status_code == 200:
                agent_info = response.json()
                self.agent_id = agent_info["id"]
                self.log_message(f"Agent registered successfully: {self.agent_id}")
                self.agent_status_var.set(f"Registered: {self.agent_id}")
                return True
            else:
                self.log_message(f"Agent registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_message(f"Agent registration error: {str(e)}")
            return False
    
    def start_websocket_connection(self):
        """Start WebSocket connection to server"""
        try:
            server_url = self.server_url_var.get().replace("http://", "ws://").replace("https://", "wss://")
            websocket_url = f"{server_url}/api/v1/ws/{self.agent_id}"
            
            self.log_message(f"Connecting to WebSocket: {websocket_url}")
            
            # Start WebSocket connection in separate thread
            self.websocket_thread = threading.Thread(target=self.websocket_worker, args=(websocket_url,))
            self.websocket_thread.daemon = True
            self.websocket_thread.start()
            
        except Exception as e:
            self.log_message(f"WebSocket connection error: {str(e)}")
    
    def websocket_worker(self, websocket_url):
        """WebSocket worker thread"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.websocket_handler(websocket_url))
        except Exception as e:
            self.log_message(f"WebSocket worker error: {str(e)}")
    
    async def websocket_handler(self, websocket_url):
        """Handle WebSocket connection"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                self.websocket = websocket
                self.is_connected = True
                
                # Update GUI
                self.root.after(0, lambda: self.connection_status_var.set("Connected"))
                self.root.after(0, lambda: self.connection_status_label.config(foreground="green"))
                
                self.log_message("WebSocket connected")
                
                # Send registration message
                await self.send_registration_message(websocket)
                
                # Start heartbeat
                self.start_heartbeat()
                
                # Listen for messages
                async for message in websocket:
                    await self.handle_server_message(message)
                    
        except Exception as e:
            self.log_message(f"WebSocket error: {str(e)}")
        finally:
            self.is_connected = False
            self.websocket = None
            self.stop_heartbeat = True
            
            # Update GUI
            self.root.after(0, lambda: self.connection_status_var.set("Disconnected"))
            self.root.after(0, lambda: self.connection_status_label.config(foreground="red"))
    
    async def send_registration_message(self, websocket):
        """Send registration message to server"""
        try:
            system_info = {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": {partition.device: psutil.disk_usage(partition.mountpoint).percent 
                              for partition in psutil.disk_partitions() if partition.device}
            }
            
            message = {
                "type": "register",
                "data": {
                    "hostname": self.agent_name_var.get(),
                    "os": platform.system(),
                    "version": platform.version(),
                    "tags": [tag.strip() for tag in self.tags_var.get().split(',') if tag.strip()],
                    "system_info": system_info
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(message))
            self.log_message("Registration message sent")
            
        except Exception as e:
            self.log_message(f"Error sending registration: {str(e)}")
    
    def start_heartbeat(self):
        """Start heartbeat thread"""
        self.stop_heartbeat = False
        self.heartbeat_thread = threading.Thread(target=self.heartbeat_worker)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
    
    def heartbeat_worker(self):
        """Heartbeat worker thread"""
        while not self.stop_heartbeat:
            try:
                if self.websocket and self.is_connected:
                    # Send heartbeat message
                    system_info = {
                        "cpu_usage": psutil.cpu_percent(),
                        "memory_usage": psutil.virtual_memory().percent,
                        "disk_usage": {partition.device: psutil.disk_usage(partition.mountpoint).percent 
                                      for partition in psutil.disk_partitions() if partition.device}
                    }
                    
                    message = {
                        "type": "heartbeat",
                        "data": {
                            "system_info": system_info
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Update GUI with system info
                    self.root.after(0, lambda: self.cpu_var.set(f"{system_info['cpu_usage']:.1f}%"))
                    self.root.after(0, lambda: self.memory_var.set(f"{system_info['memory_usage']:.1f}%"))
                    
                    # Send heartbeat asynchronously
                    asyncio.run_coroutine_threadsafe(
                        self.websocket.send(json.dumps(message)),
                        asyncio.get_event_loop()
                    )
                
                time.sleep(30)  # Send heartbeat every 30 seconds
                
            except Exception as e:
                self.log_message(f"Heartbeat error: {str(e)}")
                time.sleep(30)
    
    async def handle_server_message(self, message):
        """Handle messages from server"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "welcome":
                self.log_message(f"Welcome message: {data.get('data', {}).get('message', '')}")
                
            elif message_type == "command":
                await self.handle_command(data.get("data", {}))
                
            else:
                self.log_message(f"Unknown message type: {message_type}")
                
        except Exception as e:
            self.log_message(f"Error handling server message: {str(e)}")
    
    async def handle_command(self, command_data):
        """Handle command from server"""
        try:
            command = command_data.get("command", "")
            timeout = command_data.get("timeout", 30)
            working_directory = command_data.get("working_directory")
            
            self.log_message(f"Executing command: {command}")
            
            # Execute command
            import subprocess
            import time
            
            start_time = time.time()
            
            try:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=working_directory,
                    timeout=timeout
                )
                
                stdout, stderr = process.communicate()
                execution_time = time.time() - start_time
                
                success = process.returncode == 0
                output = stdout.decode('utf-8', errors='ignore')
                error = stderr.decode('utf-8', errors='ignore')
                
                self.log_message(f"Command completed: {success}")
                
            except subprocess.TimeoutExpired:
                success = False
                output = ""
                error = "Command timed out"
                execution_time = timeout
                self.log_message("Command timed out")
                
            except Exception as e:
                success = False
                output = ""
                error = str(e)
                execution_time = time.time() - start_time
                self.log_message(f"Command error: {str(e)}")
            
            # Send result back to server
            result_message = {
                "type": "command_result",
                "data": {
                    "command": command,
                    "success": success,
                    "output": output,
                    "error": error,
                    "execution_time": execution_time,
                    "exit_code": process.returncode if 'process' in locals() else -1
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(result_message))
            self.log_message("Command result sent to server")
            
        except Exception as e:
            self.log_message(f"Error handling command: {str(e)}")
    
    def toggle_agent(self):
        """Start or stop agent"""
        if not self.is_connected:
            # Start agent
            if not self.agent_id:
                if not self.register_agent():
                    messagebox.showerror("Error", "Failed to register agent")
                    return
            
            self.start_websocket_connection()
            self.start_stop_button.config(text="Stop Agent")
            self.log_message("Agent started")
        else:
            # Stop agent
            self.stop_heartbeat = True
            if self.websocket:
                asyncio.run_coroutine_threadsafe(self.websocket.close(), asyncio.get_event_loop())
            
            self.is_connected = False
            self.start_stop_button.config(text="Start Agent")
            self.log_message("Agent stopped")

def main():
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create and run GUI
    root = tk.Tk()
    app = DexAgentsGUI(root)
    
    # Auto-start if configured
    if app.config.get("auto_start", False):
        root.after(1000, app.toggle_agent)  # Start after 1 second
    
    root.mainloop()

if __name__ == "__main__":
    main() 