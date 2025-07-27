import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_exe():
    """Build agent as executable"""
    print("🔨 Building DexAgents Windows Agent as executable...")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Build with PyInstaller
    print("🔧 Building executable with PyInstaller...")
    
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name=DexAgentsAgent",        # Executable name
        "--icon=icon.ico",             # Icon (if exists)
        "--add-data=config.json;.",    # Include config file
        "--hidden-import=tkinter",     # Include tkinter
        "--hidden-import=requests",    # Include requests
        "--hidden-import=psutil",      # Include psutil
        "agent_gui.py"                 # Main script
    ]
    
    # Remove icon if not exists
    if not Path("icon.ico").exists():
        pyinstaller_cmd.remove("--icon=icon.ico")
    
    # Remove config if not exists
    if not Path("config.json").exists():
        pyinstaller_cmd.remove("--add-data=config.json;.")
    
    subprocess.run(pyinstaller_cmd, check=True)
    
    # Copy executable to current directory
    exe_path = Path("dist/DexAgentsAgent.exe")
    if exe_path.exists():
        shutil.copy(exe_path, "DexAgentsAgent.exe")
        print(f"✅ Executable created: DexAgentsAgent.exe")
        
        # Create installer package
        create_installer_package()
    else:
        print("❌ Executable not found in dist directory")
        
def create_installer_package():
    """Create installer package with executable and config"""
    print("📦 Creating installer package...")
    
    # Create installer directory
    installer_dir = Path("DexAgents_Installer")
    installer_dir.mkdir(exist_ok=True)
    
    # Copy executable
    if Path("DexAgentsAgent.exe").exists():
        shutil.copy("DexAgentsAgent.exe", installer_dir / "DexAgentsAgent.exe")
    
    # Create default config
    default_config = {
        "server_url": "http://localhost:8000",
        "api_token": "default_token",
        "agent_name": "agent_gui",
        "tags": ["windows", "gui-agent"],
        "auto_start": True,
        "run_as_service": False,
        "version": "2.1.4"
    }
    
    import json
    with open(installer_dir / "config.json", 'w') as f:
        json.dump(default_config, f, indent=4)
    
    # Create README
    readme_content = """# DexAgents Windows Agent

## Installation

1. Extract all files to a folder
2. Run `DexAgentsAgent.exe` as administrator
3. Configure connection settings in the GUI
4. Click "Start Agent" to begin

## Configuration

- Server URL: Your DexAgents server URL (e.g., http://localhost:8000)
- API Token: Your server API token
- Agent Name: Custom name for this agent
- Tags: Comma-separated tags (e.g., windows, gui-agent)

## Features

- GUI interface for easy configuration
- Real-time system monitoring
- Automatic connection management
- Log viewing and management
- Web interface integration

## Files

- `DexAgentsAgent.exe` - Main agent executable
- `config.json` - Configuration file
- `logs/` - Log files directory

## Troubleshooting

- Ensure server is running and accessible
- Check firewall settings
- Verify API token is correct
- Check logs for detailed error messages
"""
    
    with open(installer_dir / "README.txt", 'w') as f:
        f.write(readme_content)
    
    # Create ZIP file
    import zipfile
    zip_path = "DexAgents_Installer.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in installer_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(installer_dir)
                zipf.write(file, arcname)
    
    print(f"✅ Installer package created: {zip_path}")
    print(f"📁 Installer directory: {installer_dir}")
    
    # Cleanup
    if Path("DexAgentsAgent.exe").exists():
        os.remove("DexAgentsAgent.exe")
    
    print("🎉 Build completed successfully!")

if __name__ == "__main__":
    try:
        build_exe()
    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1) 