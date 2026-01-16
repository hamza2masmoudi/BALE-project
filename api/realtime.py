"""
BALE Real-time Features
WebSocket and SSE support for live analysis progress.
"""
import json
import asyncio
from typing import Dict, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect
from starlette.responses import StreamingResponse

from src.logger import setup_logger

logger = setup_logger("bale_realtime")


# ==================== MESSAGE TYPES ====================

class MessageType(str, Enum):
    """WebSocket message types."""
    # Connection
    CONNECTED = "connected"
    PING = "ping"
    PONG = "pong"
    
    # Analysis
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_PROGRESS = "analysis_progress"
    ANALYSIS_AGENT = "analysis_agent"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANALYSIS_ERROR = "analysis_error"
    
    # System
    NOTIFICATION = "notification"
    ERROR = "error"


@dataclass
class RealtimeMessage:
    """A real-time message."""
    type: MessageType
    data: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp
        })


# ==================== CONNECTION MANAGER ====================

class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting.
    """
    
    def __init__(self):
        # Active connections by user ID
        self.connections: Dict[str, Set[WebSocket]] = {}
        # Analysis subscriptions: analysis_id -> set of websockets
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        
        if user_id not in self.connections:
            self.connections[user_id] = set()
        
        self.connections[user_id].add(websocket)
        logger.info(f"WebSocket connected: user={user_id}")
        
        # Send connected message
        await self.send_personal(websocket, RealtimeMessage(
            type=MessageType.CONNECTED,
            data={"user_id": user_id}
        ))
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Unregister a WebSocket connection."""
        if user_id in self.connections:
            self.connections[user_id].discard(websocket)
            if not self.connections[user_id]:
                del self.connections[user_id]
        
        # Remove from all subscriptions
        for subs in self.subscriptions.values():
            subs.discard(websocket)
        
        logger.info(f"WebSocket disconnected: user={user_id}")
    
    def subscribe(self, websocket: WebSocket, analysis_id: str):
        """Subscribe a connection to an analysis stream."""
        if analysis_id not in self.subscriptions:
            self.subscriptions[analysis_id] = set()
        self.subscriptions[analysis_id].add(websocket)
    
    def unsubscribe(self, websocket: WebSocket, analysis_id: str):
        """Unsubscribe from an analysis stream."""
        if analysis_id in self.subscriptions:
            self.subscriptions[analysis_id].discard(websocket)
    
    async def send_personal(self, websocket: WebSocket, message: RealtimeMessage):
        """Send a message to a specific connection."""
        try:
            await websocket.send_text(message.to_json())
        except Exception as e:
            logger.warning(f"Failed to send personal message: {e}")
    
    async def send_to_user(self, user_id: str, message: RealtimeMessage):
        """Send a message to all connections of a user."""
        if user_id not in self.connections:
            return
        
        for websocket in list(self.connections[user_id]):
            try:
                await websocket.send_text(message.to_json())
            except Exception:
                self.connections[user_id].discard(websocket)
    
    async def broadcast_to_analysis(
        self, 
        analysis_id: str, 
        message: RealtimeMessage
    ):
        """Broadcast a message to all subscribers of an analysis."""
        if analysis_id not in self.subscriptions:
            return
        
        for websocket in list(self.subscriptions[analysis_id]):
            try:
                await websocket.send_text(message.to_json())
            except Exception:
                self.subscriptions[analysis_id].discard(websocket)
    
    async def broadcast_all(self, message: RealtimeMessage):
        """Broadcast to all connected users."""
        for user_connections in self.connections.values():
            for websocket in list(user_connections):
                try:
                    await websocket.send_text(message.to_json())
                except Exception:
                    pass


# Global connection manager
manager = ConnectionManager()


# ==================== ANALYSIS PROGRESS TRACKER ====================

class AnalysisProgressTracker:
    """
    Tracks and broadcasts analysis progress.
    """
    
    STAGES = [
        ("ingestion", "Processing document", 10),
        ("civilist", "Civilist analysis", 25),
        ("commonist", "Commonist analysis", 40),
        ("synthesizer", "Synthesizing opinions", 55),
        ("simulation", "Running simulation", 70),
        ("harmonizer", "Generating recommendations", 85),
        ("gatekeeper", "Final adjudication", 95),
        ("complete", "Analysis complete", 100),
    ]
    
    def __init__(self, analysis_id: str, user_id: str):
        self.analysis_id = analysis_id
        self.user_id = user_id
        self.current_stage = 0
        self.start_time = datetime.utcnow()
    
    async def start(self):
        """Notify that analysis has started."""
        await manager.broadcast_to_analysis(
            self.analysis_id,
            RealtimeMessage(
                type=MessageType.ANALYSIS_STARTED,
                data={
                    "analysis_id": self.analysis_id,
                    "stages": [s[0] for s in self.STAGES]
                }
            )
        )
    
    async def update_stage(self, stage_name: str, message: str = None):
        """Update to a new stage."""
        for i, (name, default_msg, progress) in enumerate(self.STAGES):
            if name == stage_name:
                self.current_stage = i
                await manager.broadcast_to_analysis(
                    self.analysis_id,
                    RealtimeMessage(
                        type=MessageType.ANALYSIS_PROGRESS,
                        data={
                            "analysis_id": self.analysis_id,
                            "stage": stage_name,
                            "message": message or default_msg,
                            "progress": progress
                        }
                    )
                )
                return
    
    async def agent_output(self, agent_name: str, output: str):
        """Stream agent output."""
        await manager.broadcast_to_analysis(
            self.analysis_id,
            RealtimeMessage(
                type=MessageType.ANALYSIS_AGENT,
                data={
                    "analysis_id": self.analysis_id,
                    "agent": agent_name,
                    "output": output[:500]  # Truncate for WS
                }
            )
        )
    
    async def complete(self, result: Dict[str, Any]):
        """Notify analysis completion."""
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        
        await manager.broadcast_to_analysis(
            self.analysis_id,
            RealtimeMessage(
                type=MessageType.ANALYSIS_COMPLETED,
                data={
                    "analysis_id": self.analysis_id,
                    "result": result,
                    "elapsed_seconds": elapsed
                }
            )
        )
    
    async def error(self, error_message: str):
        """Notify analysis error."""
        await manager.broadcast_to_analysis(
            self.analysis_id,
            RealtimeMessage(
                type=MessageType.ANALYSIS_ERROR,
                data={
                    "analysis_id": self.analysis_id,
                    "error": error_message
                }
            )
        )


# ==================== SERVER-SENT EVENTS ====================

async def sse_generator(
    analysis_id: str,
    timeout: int = 300
):
    """
    Generate SSE events for an analysis.
    
    Usage:
        @app.get("/v1/analyze/{id}/stream")
        async def stream_analysis(id: str):
            return StreamingResponse(
                sse_generator(id),
                media_type="text/event-stream"
            )
    """
    queue: asyncio.Queue = asyncio.Queue()
    
    # Create a simple subscriber
    class SSESubscriber:
        def __init__(self, q: asyncio.Queue):
            self.queue = q
        
        async def receive(self, message: RealtimeMessage):
            await self.queue.put(message)
    
    subscriber = SSESubscriber(queue)
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > timeout:
                yield f"event: timeout\ndata: {{}}\n\n"
                break
            
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(queue.get(), timeout=30)
                
                yield f"event: {message.type.value}\n"
                yield f"data: {json.dumps(message.data)}\n\n"
                
                # Stop on completion or error
                if message.type in [MessageType.ANALYSIS_COMPLETED, MessageType.ANALYSIS_ERROR]:
                    break
            
            except asyncio.TimeoutError:
                # Send keepalive
                yield f"event: ping\ndata: {{}}\n\n"
    
    except asyncio.CancelledError:
        pass


# ==================== WEBSOCKET HANDLER ====================

async def websocket_handler(websocket: WebSocket, user_id: str):
    """
    Main WebSocket handler for analysis streaming.
    
    Usage:
        @app.websocket("/ws/{user_id}")
        async def ws_endpoint(websocket: WebSocket, user_id: str):
            await websocket_handler(websocket, user_id)
    """
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive and parse message
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "ping":
                    await manager.send_personal(websocket, RealtimeMessage(
                        type=MessageType.PONG,
                        data={}
                    ))
                
                elif action == "subscribe":
                    analysis_id = message.get("analysis_id")
                    if analysis_id:
                        manager.subscribe(websocket, analysis_id)
                        await manager.send_personal(websocket, RealtimeMessage(
                            type=MessageType.NOTIFICATION,
                            data={"message": f"Subscribed to {analysis_id}"}
                        ))
                
                elif action == "unsubscribe":
                    analysis_id = message.get("analysis_id")
                    if analysis_id:
                        manager.unsubscribe(websocket, analysis_id)
            
            except json.JSONDecodeError:
                await manager.send_personal(websocket, RealtimeMessage(
                    type=MessageType.ERROR,
                    data={"message": "Invalid JSON"}
                ))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)
