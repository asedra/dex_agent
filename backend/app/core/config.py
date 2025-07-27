from typing import List

class Settings:
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DexAgents - Windows PowerShell Agent"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for executing PowerShell commands on Windows devices"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]
    
    # Database
    DATABASE_URL: str = "dexagents.db"
    
    # PowerShell Settings
    DEFAULT_TIMEOUT: int = 30
    MAX_TIMEOUT: int = 300
    
    # Agent Settings
    AGENT_INSTALLER_PATH: str = "agent_installers"
    TEMP_DIR: str = "temp"
        


settings = Settings() 