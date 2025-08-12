import asyncio
import json
import logging
import uuid
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from fastapi import WebSocket

from ..schemas.terminal import (
    TerminalSession,
    TerminalSessionStatus,
    TerminalCommand,
    TerminalMessageType,
    TerminalWebSocketMessage
)
from ..core.database import db_manager

logger = logging.getLogger(__name__)


class TerminalSessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, TerminalSession] = {}
        self.session_websockets: Dict[str, WebSocket] = {}
        self.session_buffers: Dict[str, List[str]] = {}
        self.session_commands: Dict[str, List[TerminalCommand]] = {}
        self.session_locks: Dict[str, asyncio.Lock] = {}
        self.cleanup_task = None
        self.session_timeout = 1800  # 30 minutes
        
    async def create_session(
        self,
        agent_id: str,
        user_id: str,
        websocket: WebSocket,
        rows: int = 24,
        cols: int = 80,
        working_directory: Optional[str] = None
    ) -> TerminalSession:
        """Create a new terminal session"""
        session_id = str(uuid.uuid4())
        
        session = TerminalSession(
            id=session_id,
            agent_id=agent_id,
            user_id=user_id,
            status=TerminalSessionStatus.ACTIVE,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            rows=rows,
            cols=cols,
            working_directory=working_directory
        )
        
        self.active_sessions[session_id] = session
        self.session_websockets[session_id] = websocket
        self.session_buffers[session_id] = []
        self.session_commands[session_id] = []
        self.session_locks[session_id] = asyncio.Lock()
        
        # Store session in database
        await self._store_session(session)
        
        logger.info(f"Created terminal session {session_id} for agent {agent_id}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get a terminal session by ID"""
        return self.active_sessions.get(session_id)
    
    async def update_session_activity(self, session_id: str):
        """Update last activity time for a session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].last_activity = datetime.now()
    
    async def close_session(self, session_id: str):
        """Close a terminal session"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        session.status = TerminalSessionStatus.CLOSED
        
        # Clean up resources
        if session_id in self.session_websockets:
            del self.session_websockets[session_id]
        if session_id in self.session_buffers:
            del self.session_buffers[session_id]
        if session_id in self.session_locks:
            del self.session_locks[session_id]
        
        # Update database
        await self._update_session_status(session_id, TerminalSessionStatus.CLOSED)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.info(f"Closed terminal session {session_id}")
    
    async def add_command_to_history(
        self,
        session_id: str,
        command: str,
        user_id: str,
        agent_id: str
    ):
        """Add a command to session history"""
        if session_id not in self.session_commands:
            self.session_commands[session_id] = []
        
        cmd = TerminalCommand(
            id=str(uuid.uuid4()),
            session_id=session_id,
            command=command,
            timestamp=datetime.now(),
            user_id=user_id,
            agent_id=agent_id
        )
        
        self.session_commands[session_id].append(cmd)
        
        # Store in database for audit trail
        await self._store_command(cmd)
        
        # Update session activity
        await self.update_session_activity(session_id)
    
    async def buffer_output(self, session_id: str, data: str):
        """Buffer terminal output"""
        if session_id not in self.session_buffers:
            self.session_buffers[session_id] = []
        
        async with self.session_locks.get(session_id, asyncio.Lock()):
            self.session_buffers[session_id].append(data)
            
            # Limit buffer size to prevent memory issues
            if len(self.session_buffers[session_id]) > 1000:
                self.session_buffers[session_id] = self.session_buffers[session_id][-500:]
    
    async def get_buffered_output(self, session_id: str) -> List[str]:
        """Get and clear buffered output"""
        if session_id not in self.session_buffers:
            return []
        
        async with self.session_locks.get(session_id, asyncio.Lock()):
            output = self.session_buffers[session_id].copy()
            self.session_buffers[session_id].clear()
            return output
    
    async def resize_session(self, session_id: str, rows: int, cols: int):
        """Resize terminal session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.rows = rows
            session.cols = cols
            await self.update_session_activity(session_id)
            logger.info(f"Resized session {session_id} to {rows}x{cols}")
    
    async def get_active_sessions_for_agent(self, agent_id: str) -> List[TerminalSession]:
        """Get all active sessions for an agent"""
        return [
            session for session in self.active_sessions.values()
            if session.agent_id == agent_id and session.status == TerminalSessionStatus.ACTIVE
        ]
    
    async def get_active_sessions_for_user(self, user_id: str) -> List[TerminalSession]:
        """Get all active sessions for a user"""
        return [
            session for session in self.active_sessions.values()
            if session.user_id == user_id and session.status == TerminalSessionStatus.ACTIVE
        ]
    
    async def cleanup_inactive_sessions(self):
        """Clean up inactive sessions"""
        now = datetime.now()
        sessions_to_close = []
        
        for session_id, session in self.active_sessions.items():
            if session.status == TerminalSessionStatus.ACTIVE:
                time_since_activity = (now - session.last_activity).total_seconds()
                if time_since_activity > self.session_timeout:
                    sessions_to_close.append(session_id)
                    logger.info(f"Session {session_id} timed out after {time_since_activity} seconds")
        
        for session_id in sessions_to_close:
            await self.close_session(session_id)
    
    async def start_cleanup_task(self):
        """Start the cleanup task"""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_cleanup_task(self):
        """Stop the cleanup task"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            self.cleanup_task = None
    
    async def _cleanup_loop(self):
        """Background task to clean up inactive sessions"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self.cleanup_inactive_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}")
    
    async def _store_session(self, session: TerminalSession):
        """Store session in database"""
        try:
            # Store session data in database
            session_data = {
                "id": session.id,
                "agent_id": session.agent_id,
                "user_id": session.user_id,
                "status": session.status,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "rows": session.rows,
                "cols": session.cols,
                "working_directory": session.working_directory
            }
            # You would implement actual database storage here
            logger.debug(f"Stored session {session.id} in database")
        except Exception as e:
            logger.error(f"Failed to store session: {str(e)}")
    
    async def _update_session_status(self, session_id: str, status: TerminalSessionStatus):
        """Update session status in database"""
        try:
            # Update session status in database
            logger.debug(f"Updated session {session_id} status to {status}")
        except Exception as e:
            logger.error(f"Failed to update session status: {str(e)}")
    
    async def _store_command(self, command: TerminalCommand):
        """Store command in database for audit trail"""
        try:
            # Store command in database
            command_data = {
                "id": command.id,
                "session_id": command.session_id,
                "command": command.command,
                "timestamp": command.timestamp.isoformat(),
                "user_id": command.user_id,
                "agent_id": command.agent_id
            }
            # You would implement actual database storage here
            logger.debug(f"Stored command for session {command.session_id}")
        except Exception as e:
            logger.error(f"Failed to store command: {str(e)}")
    
    async def send_to_agent(
        self,
        session_id: str,
        agent_id: str,
        message_type: TerminalMessageType,
        data: Dict[str, Any]
    ) -> bool:
        """Send terminal message to agent through WebSocket manager"""
        from ..core.websocket_manager import websocket_manager
        
        message = {
            "type": message_type,
            "session_id": session_id,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        success = await websocket_manager.send_to_agent(agent_id, message)
        if success:
            await self.update_session_activity(session_id)
        
        return success
    
    async def broadcast_to_session_clients(
        self,
        session_id: str,
        message_type: str,
        data: Any
    ):
        """Broadcast message to all clients connected to a session"""
        if session_id in self.session_websockets:
            websocket = self.session_websockets[session_id]
            try:
                message = {
                    "type": message_type,
                    "session_id": session_id,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to broadcast to session {session_id}: {str(e)}")


# Global instance
terminal_manager = TerminalSessionManager()