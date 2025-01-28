"""
Enhanced file system manager with state persistence and concurrency control.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union

import aiofiles
from pydantic import BaseModel, Field

from ..base import LionTool
from .base_ import FileOperation, FileState, FileStats, FileSystemError
from .constraints import PathConstraints


class ManagerConfig(BaseModel):
    """
    Configuration for FileManager.

    Attributes:
        state_ttl: Time-to-live for file states
        cleanup_interval: Interval for cleanup tasks
        max_concurrent: Maximum concurrent operations
        persist_path: Path for state persistence
        shard_size: Maximum states per shard
    """

    state_ttl: int = Field(3600, description="State TTL in seconds")  # 1 hour
    cleanup_interval: int = Field(
        300, description="Cleanup interval in seconds"  # 5 minutes
    )
    max_concurrent: int = Field(100, description="Max concurrent operations")
    persist_path: Optional[str] = Field(
        None, description="Path for state persistence"
    )
    shard_size: int = Field(1000, description="Max states per shard")
    connection_pool_size: int = Field(
        10, description="Size of connection pool"
    )


class FileManager:
    """
    Enhanced file system manager with state persistence and concurrency control.

    Features:
    - State persistence and recovery
    - Connection pooling
    - State sharding
    - Concurrent operation limits
    - Periodic cleanup
    """

    def __init__(
        self,
        config: Union[ManagerConfig, dict] = None,
        constraints: Optional[PathConstraints] = None,
    ):
        """
        Initialize manager with config and constraints.

        Args:
            config: Manager configuration
            constraints: Path constraints
        """
        self.config = (
            config
            if isinstance(config, ManagerConfig)
            else ManagerConfig(**(config or {}))
        )
        self.constraints = constraints or PathConstraints()

        # State management
        self.states: Dict[str, Dict[Path, FileState]] = {"0": {}}
        self.active_shard = "0"

        # Concurrency control
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
        self._cleanup_task: Optional[asyncio.Task] = None
        self._connection_pool = asyncio.Queue(self.config.connection_pool_size)

        # Tool registry
        self._tools: Dict[str, LionTool] = {}

    async def start(self) -> None:
        """Start manager and initialize resources."""
        # Initialize connection pool
        for _ in range(self.config.connection_pool_size):
            await self._connection_pool.put(None)

        # Restore state if persist path exists
        if self.config.persist_path:
            await self.restore_states()

        # Start cleanup task
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def stop(self) -> None:
        """Stop manager and cleanup resources."""
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Persist states if configured
        if self.config.persist_path:
            await self.persist_states()

        # Final cleanup
        await self.cleanup()

    async def validate_operation(
        self, path: Union[str, Path], operation: FileOperation
    ) -> Path:
        """
        Validate operation against constraints.

        Args:
            path: Target path
            operation: Requested operation

        Returns:
            Validated Path object
        """
        return self.constraints.validate_path(path, operation)

    def register_tool(
        self, name: str, tool: LionTool, replace: bool = False
    ) -> None:
        """Register a file operation tool."""
        if name in self._tools and not replace:
            raise ValueError(f"Tool {name} already registered")
        self._tools[name] = tool

    def get_tool(self, name: str) -> LionTool:
        """Get registered tool by name."""
        if name not in self._tools:
            raise KeyError(f"Tool {name} not registered")
        return self._tools[name]

    async def get_state(self, path: Path) -> FileState:
        """
        Get or create file state.
        Creates new shard if current is full.
        """
        # Find state in shards
        for shard_id, shard in self.states.items():
            if path in shard:
                return shard[path]

        # Create new state
        state = FileState()

        # Check if current shard is full
        current_shard = self.states[self.active_shard]
        if len(current_shard) >= self.config.shard_size:
            # Create new shard
            new_shard_id = str(int(self.active_shard) + 1)
            self.states[new_shard_id] = {}
            self.active_shard = new_shard_id
            current_shard = self.states[self.active_shard]

        current_shard[path] = state
        return state

    async def persist_states(self) -> None:
        """Save states to configured persist path."""
        if not self.config.persist_path:
            return

        persist_path = Path(self.config.persist_path)
        persist_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert states to serializable format
        state_data = {
            shard_id: {
                str(path): {
                    "mode": state.mode,
                    "ref_count": state.ref_count,
                    "in_use": state.in_use,
                    "last_accessed": (
                        state.last_accessed.isoformat()
                        if state.last_accessed
                        else None
                    ),
                    "metadata": state.metadata,
                }
                for path, state in shard.items()
            }
            for shard_id, shard in self.states.items()
        }

        async with aiofiles.open(persist_path, "w") as f:
            await f.write(json.dumps(state_data, indent=2))

    async def restore_states(self) -> None:
        """Restore states from persist path."""
        if not self.config.persist_path:
            return

        persist_path = Path(self.config.persist_path)
        if not persist_path.exists():
            return

        async with aiofiles.open(persist_path) as f:
            state_data = json.loads(await f.read())

        # Restore states by shard
        for shard_id, shard_data in state_data.items():
            shard = {}
            for path_str, state_info in shard_data.items():
                state = FileState()
                state.mode = state_info["mode"]
                state.ref_count = state_info["ref_count"]
                state.in_use = state_info["in_use"]
                if state_info["last_accessed"]:
                    state.last_accessed = datetime.fromisoformat(
                        state_info["last_accessed"]
                    )
                state.metadata = state_info["metadata"]
                shard[Path(path_str)] = state
            self.states[shard_id] = shard

        # Set active shard to last one
        self.active_shard = max(self.states.keys())

    async def _periodic_cleanup(self) -> None:
        """Run periodic state cleanup."""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                await self.cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue cleanup loop
                print(f"Cleanup error: {e}")

    async def cleanup(self) -> None:
        """
        Clean up expired states and resources.
        Removes states older than TTL and empty shards.
        """
        now = datetime.now()
        ttl = timedelta(seconds=self.config.state_ttl)

        # Track empty shards
        empty_shards = set()

        # Check each shard
        for shard_id, shard in self.states.items():
            expired_paths = set()

            # Find expired states
            for path, state in shard.items():
                if state.last_accessed:
                    age = now - state.last_accessed
                    if age > ttl and not state.in_use:
                        expired_paths.add(path)
                        # Cleanup temp file if exists
                        if state._temp_path and state._temp_path.exists():
                            try:
                                state._temp_path.unlink()
                            except Exception:
                                pass

            # Remove expired states
            for path in expired_paths:
                del shard[path]

            # Track empty shard
            if not shard and shard_id != self.active_shard:
                empty_shards.add(shard_id)

        # Remove empty shards
        for shard_id in empty_shards:
            del self.states[shard_id]

    async def get_connection(self):
        """Get connection from pool."""
        return await self._connection_pool.get()

    async def release_connection(self, conn: Any):
        """Release connection back to pool."""
        await self._connection_pool.put(conn)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Async context manager exit."""
        await self.stop()
