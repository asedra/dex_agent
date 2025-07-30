#!/usr/bin/env python3
"""
DexAgents Backend Server
FastAPI application for Windows PowerShell agent management
"""

import uvicorn
import logging
import os
from app.main import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    # Get port from environment variable or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    # Disable reload in production
    reload = os.getenv("ENVIRONMENT", "development") != "production"
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        log_level="info"
    ) 