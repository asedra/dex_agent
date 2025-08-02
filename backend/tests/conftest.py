"""
Simplified test configuration without PostgreSQL dependencies
For basic testing and CI environments without full database setup
"""
import asyncio
import pytest
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

import httpx
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Try to import app components with error handling
try:
    from app.main import create_application
    APP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import app.main: {e}")
    APP_AVAILABLE = False

try:
    from app.core.jwt_utils import create_access_token
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def app():
    """Create FastAPI application instance for testing."""
    if not APP_AVAILABLE:
        pytest.skip("Application not available - check backend setup")
    
    # Create a simple test app without complex dependencies
    from fastapi import FastAPI
    
    test_app = FastAPI(title="Test App", version="1.0.0")
    
    @test_app.get("/")
    def root():
        return {"message": "DexAgents API", "version": "1.0.0"}
    
    @test_app.get("/api/v1/system/health")
    def health():
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    yield test_app


@pytest.fixture(scope="session")
def client(app) -> Generator[TestClient, None, None]:
    """Create test client for synchronous tests."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client for asynchronous tests."""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture(scope="function")
def test_user_data():
    """Test user data for authentication tests - admin user."""
    return {
        "id": "admin-user-id",
        "username": "admin",
        "email": "admin@dexagents.com",
        "password": "admin123",
        "password_hash": "$2b$12$eUufJwxHDyUn7.3pAz1wCeI9RGD9pJB5ykhj2u3EQs.9cRZrGQs7O",  # hashed 'admin123'
        "is_active": True,
        "is_admin": True,
        "created_at": datetime.utcnow(),
        "last_login": None
    }


@pytest.fixture(scope="function")
def test_token(test_user_data):
    """Generate test JWT token."""
    if not JWT_AVAILABLE:
        return "mock-jwt-token"
    
    token_data = {"sub": test_user_data["username"], "user_id": test_user_data["id"]}
    return create_access_token(token_data, expires_delta=timedelta(minutes=30))


@pytest.fixture(scope="function")
def auth_headers(test_token):
    """Authentication headers with valid token."""
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture(scope="function")
def test_agent_data():
    """Test agent data."""
    return {
        "id": "test-agent-id",
        "hostname": "test-hostname",
        "ip_address": "192.168.1.100",
        "platform": "Windows",
        "platform_version": "10.0.19042",
        "python_version": "3.9.7",
        "status": "online",
        "last_seen": datetime.utcnow(),
        "system_info": {
            "cpu_count": 8,
            "memory_total": 16777216,
            "disk_total": 1000000000
        },
        "created_at": datetime.utcnow(),
        "is_connected": True
    }


@pytest.fixture(scope="function")
def mock_db_manager():
    """Mock database manager for isolated testing."""
    mock_db = MagicMock()
    
    # Setup common mock responses
    mock_db.get_user_by_username.return_value = None
    mock_db.get_agents.return_value = []
    mock_db.get_saved_commands.return_value = []
    mock_db.get_settings.return_value = []
    mock_db.is_connected.return_value = True
    
    return mock_db


@pytest.fixture(scope="function")
def invalid_tokens():
    """Various invalid tokens for security testing."""
    return [
        "invalid-token",
        "Bearer invalid-token",
        "expired-token",
        "",
        "malformed.jwt.token",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
    ]


@pytest.fixture(scope="function")
def test_login_data():
    """Test login credentials."""
    return {
        "username": "admin",
        "password": "admin123"
    }


@pytest.fixture(scope="function")
def invalid_login_data():
    """Invalid login credentials for security testing."""
    return [
        {"username": "admin", "password": "wrongpassword"},
        {"username": "wronguser", "password": "admin123"},
        {"username": "", "password": ""},
        {"username": "admin", "password": ""},
        {"username": "", "password": "admin123"}
    ]


@pytest.fixture(scope="function")
def mock_websocket_manager():
    """Mock WebSocket manager for testing."""
    from unittest.mock import AsyncMock, MagicMock
    mock_ws = MagicMock()
    mock_ws.is_agent_connected.return_value = False
    mock_ws.send_command_to_agent = AsyncMock()
    mock_ws.broadcast_to_agents = AsyncMock()
    mock_ws.active_connections = []
    return mock_ws


@pytest.fixture(scope="function")
def mock_ai_service():
    """Mock AI service for testing AI endpoints."""
    import json
    from unittest.mock import AsyncMock, MagicMock
    
    mock_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "name": "Test AI Command",
                    "description": "AI generated test command",
                    "command": "Get-Process | Select-Object -First 10",
                    "category": "system",
                    "parameters": {}
                })
            }
        }]
    }
    
    mock_openai = MagicMock()
    mock_openai.ChatCompletion.acreate = AsyncMock(return_value=mock_response)
    return mock_openai