"""
Progress tracking for batch evaluations.
Manages WebSocket connections and progress state for running evaluations.
"""

import asyncio
import uuid
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import Lock as ThreadLock
from fastapi import WebSocket


@dataclass
class ProgressUpdate:
    """Represents a progress update for an evaluation run."""
    run_id: str
    completed_tasks: int
    total_tasks: int
    percentage: float
    status: str  # "running", "done", "error"
    message: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class ProgressTracker:
    """
    Manages progress tracking for evaluation runs.

    Supports both WebSocket connections and polling-based status queries.
    """

    def __init__(self):
        # Map run_id -> list of WebSocket connections
        self._websockets: Dict[str, list[WebSocket]] = {}
        # Map run_id -> latest ProgressUpdate
        self._progress_state: Dict[str, ProgressUpdate] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
        # Synchronous lock for create/cleanup to avoid races across threads
        self._sync_lock = ThreadLock()

    def create_run(self, total_tasks: int, run_id: Optional[str] = None) -> str:
        """
        Create a new evaluation run and return its run_id.

        Args:
            total_tasks: Total number of tasks to evaluate
            run_id: Optional client-supplied run ID

        Returns:
            Unique run_id for this evaluation
        """
        with self._sync_lock:
            run_id = run_id or str(uuid.uuid4())
            # Avoid collision by regenerating if already present
            if run_id in self._progress_state:
                run_id = str(uuid.uuid4())
            initial_update = ProgressUpdate(
                run_id=run_id,
                completed_tasks=0,
                total_tasks=total_tasks,
                percentage=0.0,
                status="running"
            )
            self._progress_state[run_id] = initial_update
            self._websockets[run_id] = []
            return run_id

    async def register_websocket(self, run_id: str, websocket: WebSocket):
        """
        Register a WebSocket connection for receiving progress updates.

        Args:
            run_id: The evaluation run ID
            websocket: WebSocket connection to register
        """
        async with self._lock:
            if run_id not in self._websockets:
                self._websockets[run_id] = []
            self._websockets[run_id].append(websocket)

            # Send current state immediately upon connection
            if run_id in self._progress_state:
                await websocket.send_json(self._progress_state[run_id].to_dict())

    async def unregister_websocket(self, run_id: str, websocket: WebSocket):
        """
        Unregister a WebSocket connection.

        Args:
            run_id: The evaluation run ID
            websocket: WebSocket connection to unregister
        """
        async with self._lock:
            if run_id in self._websockets:
                try:
                    self._websockets[run_id].remove(websocket)
                except ValueError:
                    pass  # Already removed

    async def update_progress(
        self,
        run_id: str,
        completed_tasks: int,
        total_tasks: Optional[int] = None
    ):
        """
        Update progress for a run and notify all connected WebSockets.

        Args:
            run_id: The evaluation run ID
            completed_tasks: Number of tasks completed so far
            total_tasks: Total tasks (optional, uses existing if not provided)
        """
        async with self._lock:
            if run_id not in self._progress_state:
                return

            current = self._progress_state[run_id]
            if total_tasks is None:
                total_tasks = current.total_tasks

            percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            update = ProgressUpdate(
                run_id=run_id,
                completed_tasks=completed_tasks,
                total_tasks=total_tasks,
                percentage=round(percentage, 1),
                status="running"
            )
            self._progress_state[run_id] = update

            # Broadcast to all connected WebSockets
            await self._broadcast(run_id, update)

    async def complete_run(self, run_id: str, message: Optional[str] = None):
        """
        Mark a run as completed and notify all WebSockets.

        Args:
            run_id: The evaluation run ID
            message: Optional completion message
        """
        async with self._lock:
            if run_id not in self._progress_state:
                return

            current = self._progress_state[run_id]
            update = ProgressUpdate(
                run_id=run_id,
                completed_tasks=current.total_tasks,
                total_tasks=current.total_tasks,
                percentage=100.0,
                status="done",
                message=message
            )
            self._progress_state[run_id] = update

            # Broadcast completion
            await self._broadcast(run_id, update)

    async def error_run(self, run_id: str, error_message: str):
        """
        Mark a run as failed and notify all WebSockets.

        Args:
            run_id: The evaluation run ID
            error_message: Error description
        """
        async with self._lock:
            if run_id not in self._progress_state:
                return

            current = self._progress_state[run_id]
            update = ProgressUpdate(
                run_id=run_id,
                completed_tasks=current.completed_tasks,
                total_tasks=current.total_tasks,
                percentage=current.percentage,
                status="error",
                message=error_message
            )
            self._progress_state[run_id] = update

            # Broadcast error
            await self._broadcast(run_id, update)

    async def _broadcast(self, run_id: str, update: ProgressUpdate):
        """
        Broadcast progress update to all connected WebSockets.

        Args:
            run_id: The evaluation run ID
            update: Progress update to broadcast
        """
        if run_id not in self._websockets:
            return

        # Send to all connected clients
        disconnected = []
        for ws in self._websockets[run_id]:
            try:
                await ws.send_json(update.to_dict())
            except Exception:
                # Mark for removal if send fails
                disconnected.append(ws)

        # Clean up disconnected WebSockets
        for ws in disconnected:
            try:
                self._websockets[run_id].remove(ws)
            except ValueError:
                pass

    def get_progress(self, run_id: str) -> Optional[ProgressUpdate]:
        """
        Get current progress state for polling-based clients.

        Args:
            run_id: The evaluation run ID

        Returns:
            Current ProgressUpdate or None if run doesn't exist
        """
        return self._progress_state.get(run_id)

    def cleanup_run(self, run_id: str):
        """
        Clean up resources for a completed run.
        Should be called after a reasonable delay to allow clients to retrieve final state.

        Args:
            run_id: The evaluation run ID
        """
        with self._sync_lock:
            if run_id in self._websockets:
                del self._websockets[run_id]
            if run_id in self._progress_state:
                del self._progress_state[run_id]

    def get_progress_callback(self, run_id: str) -> Callable[[int, int], None]:
        """
        Get a synchronous callback function for updating progress.
        Used by evaluation pipeline to report progress.

        Args:
            run_id: The evaluation run ID

        Returns:
            Callback function that takes (completed_tasks, total_tasks)
        """
        def callback(completed_tasks: int, total_tasks: int):
            """Synchronous progress callback."""
            # Schedule async update in event loop
            try:
                loop = asyncio.get_event_loop()
                asyncio.create_task(
                    self.update_progress(run_id, completed_tasks, total_tasks)
                )
            except RuntimeError:
                # No event loop available (shouldn't happen in FastAPI)
                pass

        return callback


# Global progress tracker instance
progress_tracker = ProgressTracker()
