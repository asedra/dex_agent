from typing import List
import os

class Settings:
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DexAgents - Windows PowerShell Agent"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for executing PowerShell commands on Windows devices"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # JWT Algorithm
    ALGORITHM: str = "HS256"
    
    # CORS - Allow all origins for development
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "data/dexagents.db")
    
    # PowerShell Settings
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30"))
    MAX_TIMEOUT: int = int(os.getenv("MAX_TIMEOUT", "300"))
    
    # Agent Settings
    AGENT_INSTALLER_PATH: str = os.getenv("AGENT_INSTALLER_PATH", "agent_installers")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "temp")
        


settings = Settings() 