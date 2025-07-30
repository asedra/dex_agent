#!/usr/bin/env python3
"""
Render.com Startup Script for DexAgents Backend
Handles database initialization and starts the FastAPI server
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database with migrations and default data"""
    try:
        from app.core.database import DatabaseManager
        
        logger.info("Initializing database...")
        db_manager = DatabaseManager()
        db_manager.init_database()
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)

def start_server():
    """Start the FastAPI server with Render configuration"""
    try:
        import uvicorn
        from app.main import app
        
        # Get port from environment variable (Render uses PORT=10000)
        port = int(os.getenv("PORT", 10000))
        host = "0.0.0.0"
        
        logger.info(f"Starting server on {host}:{port}")
        
        # Production configuration for Render
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=1,  # Render recommends single worker for web services
            reload=False,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Server startup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Starting DexAgents Backend on Render...")
    
    # Initialize database first
    initialize_database()
    
    # Start the server
    start_server()