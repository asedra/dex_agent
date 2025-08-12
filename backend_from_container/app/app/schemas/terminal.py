from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class TerminalMessageType(str, Enum):
    TERMINAL_START = "terminal_start"
    TERMINAL_INPUT = "terminal_input"
    TERMINAL_OUTPUT = "terminal_output"
    TERMINAL_RESIZE = "terminal_resize"
    TERMINAL_CLOSE = "terminal_close"
    TERMINAL_ERROR = "terminal_error"
    TERMINAL_PING = "terminal_ping"
    TERMINAL_PONG = "terminal_pong"


class TerminalSessionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    ERROR = "error"


class TerminalStartRequest(BaseModel):
    rows: int = Field(default=24, description="Terminal rows")
    cols: int = Field(default=80, description="Terminal columns")
    working_directory: Optional[str] = Field(None, description="Initial working directory")
    environment: Optional[Dict[str, str]] = Field(default_factory=dict, description="Environment variables")


class TerminalInputMessage(BaseModel):
    session_id: str = Field(..., description="Terminal session ID")
    data: str = Field(..., description="Input data to send to terminal")


class TerminalOutputMessage(BaseModel):
    session_id: str = Field(..., description="Terminal session ID")
    data: str = Field(..., description="Output data from terminal")
    timestamp: datetime = Field(default_factory=datetime.now)


class TerminalResizeMessage(BaseModel):
    session_id: str = Field(..., description="Terminal session ID")
    rows: int = Field(..., description="New number of rows")
    cols: int = Field(..., description="New number of columns")


class TerminalSession(BaseModel):
    id: str = Field(..., description="Session ID")
    agent_id: str = Field(..., description="Agent ID")
    user_id: str = Field(..., description="User ID")
    status: TerminalSessionStatus = Field(..., description="Session status")
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    rows: int = Field(default=24)
    cols: int = Field(default=80)
    working_directory: Optional[str] = None
    process_id: Optional[int] = None


class TerminalCommand(BaseModel):
    id: Optional[str] = None
    session_id: str = Field(..., description="Terminal session ID")
    command: str = Field(..., description="Command executed")
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: str = Field(..., description="User who executed the command")
    agent_id: str = Field(..., description="Agent where command was executed")


class TerminalWebSocketMessage(BaseModel):
    type: TerminalMessageType = Field(..., description="Message type")
    session_id: Optional[str] = Field(None, description="Terminal session ID")
    data: Optional[Dict[str, Any]] = Field(None, description="Message payload")
    timestamp: datetime = Field(default_factory=datetime.now)


class TerminalSessionCreate(BaseModel):
    agent_id: str = Field(..., description="Agent ID to create session on")
    rows: int = Field(default=24, description="Terminal rows")
    cols: int = Field(default=80, description="Terminal columns")
    working_directory: Optional[str] = Field(None, description="Initial working directory")


class TerminalSessionResponse(BaseModel):
    session_id: str = Field(..., description="Created session ID")
    agent_id: str = Field(..., description="Agent ID")
    status: TerminalSessionStatus = Field(..., description="Session status")
    websocket_url: str = Field(..., description="WebSocket URL for terminal connection")
    created_at: datetime = Field(..., description="Session creation time")