import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import sys
import threading
import time
import requests
import psutil
from datetime import datetime
import subprocess
import logging
from pathlib import Path
import webbrowser

class DexAgentGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DexAgents Windows Agent")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Configure logging
        self.setup_logging()
        
        # Agent configuration
        self.config = self.load_config()
        self.agent_running = False
        self.agent_thread = None
        
        # Create GUI
        self.create_widgets()
        
        # Start status update
        self.update_status()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "agent.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Load configuration from file"""
        config_file = Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "server_url": "http://localhost:8000",
            "api_token": "default_token",
            "agent_name": f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "tags": ["windows", "gui-agent"],
            "auto_start": True,
            "run_as_service": False,
            "version": "2.1.4",
            "created_at": datetime.now().isoformat()
        }
        
    def save_config(self):
        """Save configuration to file"""
        try:
            with open("config.json", 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info("Configuration saved")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            
    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="DexAgents Windows Agent", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Configuration Frame
        config_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Server URL
        ttk.Label(config_frame, text="Server URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.server_url_var = tk.StringVar(value=self.config.get("server_url", ""))
        self.server_url_entry = ttk.Entry(config_frame, textvariable=self.server_url_var, width=50)
        self.server_url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # API Token
        ttk.Label(config_frame, text="API Token:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.api_token_var = tk.StringVar(value=self.config.get("api_token", ""))
        self.api_token_entry = ttk.Entry(config_frame, textvariable=self.api_token_var, width=50, show="*")
        self.api_token_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Agent Name
        ttk.Label(config_frame, text="Agent Name:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.agent_name_var = tk.StringVar(value=self.config.get("agent_name", ""))
        self.agent_name_entry = ttk.Entry(config_frame, textvariable=self.agent_name_var, width=50)
        self.agent_name_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Tags
        ttk.Label(config_frame, text="Tags:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.tags_var = tk.StringVar(value=", ".join(self.config.get("tags", [])))
        self.tags_entry = ttk.Entry(config_frame, textvariable=self.tags_var, width=50)
        self.tags_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        ttk.Label(config_frame, text="(comma separated)").grid(row=3, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Auto start checkbox
        self.auto_start_var = tk.BooleanVar(value=self.config.get("auto_start", True))
        self.auto_start_check = ttk.Checkbutton(options_frame, text="Auto-start with Windows", variable=self.auto_start_var)
        self.auto_start_check.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Run as service checkbox
        self.run_as_service_var = tk.BooleanVar(value=self.config.get("run_as_service", False))
        self.run_as_service_check = ttk.Checkbutton(options_frame, text="Run as Windows Service", variable=self.run_as_service_var)
        self.run_as_service_check.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Connection status
        ttk.Label(status_frame, text="Connection:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.connection_status = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.connection_status.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Agent status
        ttk.Label(status_frame, text="Agent:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.agent_status = ttk.Label(status_frame, text="Stopped", foreground="red")
        self.agent_status.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Last seen
        ttk.Label(status_frame, text="Last Seen:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.last_seen_label = ttk.Label(status_frame, text="Never")
        self.last_seen_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # System info
        ttk.Label(status_frame, text="CPU Usage:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.cpu_usage_label = ttk.Label(status_frame, text="0%")
        self.cpu_usage_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(status_frame, text="Memory Usage:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.memory_usage_label = ttk.Label(status_frame, text="0%")
        self.memory_usage_label.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # Start/Stop button
        self.start_stop_button = ttk.Button(buttons_frame, text="Start Agent", command=self.toggle_agent)
        self.start_stop_button.grid(row=0, column=0, padx=(0, 10))
        
        # Test connection button
        self.test_connection_button = ttk.Button(buttons_frame, text="Test Connection", command=self.test_connection)
        self.test_connection_button.grid(row=0, column=1, padx=(0, 10))
        
        # Save config button
        self.save_config_button = ttk.Button(buttons_frame, text="Save Config", command=self.save_configuration)
        self.save_config_button.grid(row=0, column=2, padx=(0, 10))
        
        # Open logs button
        self.open_logs_button = ttk.Button(buttons_frame, text="Open Logs", command=self.open_logs)
        self.open_logs_button.grid(row=0, column=3, padx=(0, 10))
        
        # Open web interface button
        self.open_web_button = ttk.Button(buttons_frame, text="Open Web Interface", command=self.open_web_interface)
        self.open_web_button.grid(row=0, column=4)
        
        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Log text area
        self.log_text = tk.Text(log_frame, height=8, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for log
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Add initial log message
        self.log_message("DexAgents Windows Agent GUI started")
        
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.logger.info(message)
        
    def get_system_info(self):
        """Get system information"""
        try:
            hostname = os.environ.get('COMPUTERNAME', 'Unknown')
            os_version = os.environ.get('OS', 'Unknown')
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = (usage.used / usage.total) * 100
                except PermissionError:
                    continue
                    
            return {
                "hostname": hostname,
                "os_version": os_version,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "disk_usage": disk_usage
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return None
            
    def test_connection(self):
        """Test connection to server"""
        try:
            server_url = self.server_url_var.get()
            api_token = self.api_token_var.get()
            
            if not server_url or not api_token:
                messagebox.showerror("Error", "Please enter server URL and API token")
                return
                
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{server_url}/", headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.connection_status.config(text="Connected", foreground="green")
                self.log_message("Connection test successful")
                messagebox.showinfo("Success", "Connection to server successful!")
            else:
                self.connection_status.config(text="Failed", foreground="red")
                self.log_message(f"Connection test failed: {response.status_code}")
                messagebox.showerror("Error", f"Connection failed: {response.status_code}")
                
        except Exception as e:
            self.connection_status.config(text="Error", foreground="red")
            self.log_message(f"Connection test error: {e}")
            messagebox.showerror("Error", f"Connection error: {e}")
            
    def register_agent(self):
        """Register agent with server"""
        try:
            system_info = self.get_system_info()
            if not system_info:
                return False
                
            agent_data = {
                "hostname": system_info["hostname"],
                "os": system_info["os_version"],
                "version": self.config["version"],
                "status": "online",
                "last_seen": datetime.now().isoformat(),
                "tags": self.config["tags"],
                "system_info": system_info
            }
            
            server_url = self.server_url_var.get()
            api_token = self.api_token_var.get()
            
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(f"{server_url}/api/agents/register", json=agent_data, headers=headers)
            if response.status_code == 200:
                self.log_message("Agent registered successfully")
                return True
            else:
                self.log_message(f"Failed to register agent: {response.status_code}")
                return False
        except Exception as e:
            self.log_message(f"Error registering agent: {e}")
            return False
            
    def update_status(self):
        """Update agent status"""
        try:
            system_info = self.get_system_info()
            if not system_info:
                return False
                
            update_data = {
                "status": "online",
                "last_seen": datetime.now().isoformat(),
                "system_info": system_info
            }
            
            server_url = self.server_url_var.get()
            api_token = self.api_token_var.get()
            
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(f"{server_url}/api/agents/register", json=update_data, headers=headers)
            return response.status_code == 200
        except Exception as e:
            self.log_message(f"Error updating status: {e}")
            return False
            
    def agent_loop(self):
        """Main agent loop"""
        self.log_message("Starting agent loop")
        
        # Initial registration
        if not self.register_agent():
            self.log_message("Failed to register agent")
            return
            
        while self.agent_running:
            try:
                # Update status every 30 seconds
                self.update_status()
                time.sleep(30)
            except Exception as e:
                self.log_message(f"Error in agent loop: {e}")
                time.sleep(60)  # Wait before retry
                
        self.log_message("Agent loop stopped")
        
    def toggle_agent(self):
        """Start or stop agent"""
        if not self.agent_running:
            # Start agent
            self.agent_running = True
            self.agent_status.config(text="Running", foreground="green")
            self.start_stop_button.config(text="Stop Agent")
            self.log_message("Starting agent...")
            
            # Start agent thread
            self.agent_thread = threading.Thread(target=self.agent_loop, daemon=True)
            self.agent_thread.start()
        else:
            # Stop agent
            self.agent_running = False
            self.agent_status.config(text="Stopped", foreground="red")
            self.start_stop_button.config(text="Start Agent")
            self.log_message("Stopping agent...")
            
    def save_configuration(self):
        """Save current configuration"""
        try:
            # Update config with current values
            self.config["server_url"] = self.server_url_var.get()
            self.config["api_token"] = self.api_token_var.get()
            self.config["agent_name"] = self.agent_name_var.get()
            self.config["tags"] = [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()]
            self.config["auto_start"] = self.auto_start_var.get()
            self.config["run_as_service"] = self.run_as_service_var.get()
            
            self.save_config()
            self.log_message("Configuration saved")
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            self.log_message(f"Error saving configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            
    def open_logs(self):
        """Open logs directory"""
        try:
            log_dir = Path("logs")
            if log_dir.exists():
                os.startfile(log_dir)
            else:
                messagebox.showinfo("Info", "Logs directory not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open logs: {e}")
            
    def open_web_interface(self):
        """Open web interface"""
        try:
            server_url = self.server_url_var.get()
            if server_url:
                # Replace port 8000 with 3000 for frontend
                web_url = server_url.replace(":8000", ":3000")
                webbrowser.open(web_url)
            else:
                messagebox.showinfo("Info", "Please enter server URL first")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open web interface: {e}")
            
    def update_status_display(self):
        """Update status display"""
        try:
            system_info = self.get_system_info()
            if system_info:
                self.cpu_usage_label.config(text=f"{system_info['cpu_usage']:.1f}%")
                self.memory_usage_label.config(text=f"{system_info['memory_usage']:.1f}%")
                
            if self.agent_running:
                self.last_seen_label.config(text=datetime.now().strftime("%H:%M:%S"))
                
        except Exception as e:
            self.logger.error(f"Error updating status display: {e}")
            
        # Schedule next update
        self.root.after(5000, self.update_status_display)  # Update every 5 seconds
        
    def run(self):
        """Run the GUI application"""
        # Start status update
        self.update_status_display()
        
        # Run the main loop
        self.root.mainloop()

if __name__ == "__main__":
    app = DexAgentGUI()
    app.run() 