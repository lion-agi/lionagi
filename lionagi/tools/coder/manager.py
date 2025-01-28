"""
Central manager for code operations and tools.
Coordinates file management, tools, and sandboxes.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Type, Union

from ...libs.validate import string_similarity
from ..file import FileManager
from .base import (
    CodeError,
    CodeSession,
    Sandbox,
    SandboxConfig,
    SandboxError,
    SessionError,
)


class CoderManager:
    """
    Central manager for code operations.

    Features:
    - File state tracking via FileManager
    - Tool registration and coordination
    - Sandbox management
    - Session persistence
    - Fuzzy matching
    """

    def __init__(
        self,
        file_manager: FileManager,
        max_sessions: int = 100,
        session_ttl: int = 3600,  # 1 hour
        cleanup_interval: int = 300,  # 5 minutes
    ):
        self.file_manager = file_manager
        self.max_sessions = max_sessions
        self.session_ttl = session_ttl

        self._tools: Dict[str, Any] = {}
        self._sandbox_providers: Dict[str, Type[Sandbox]] = {}
        self._active_sandboxes: Dict[str, Sandbox] = {}
        self._sessions: Dict[str, CodeSession] = {}

        self._cleanup_task: Optional[asyncio.Task] = None
        self.cleanup_interval = cleanup_interval

    async def start(self) -> None:
        """Start manager and periodic cleanup"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def stop(self) -> None:
        """Stop manager and cleanup resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

        # Final cleanup
        await self.cleanup()

    def register_tool(
        self, name: str, tool: Any, replace: bool = False
    ) -> None:
        """
        Register a coding tool.

        Args:
            name: Tool name
            tool: Tool instance
            replace: Whether to replace existing tool
        """
        if name in self._tools and not replace:
            raise ValueError(f"Tool {name} already registered")
        self._tools[name] = tool

    def get_tool(self, name: str) -> Any:
        """
        Get registered tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance
        """
        if name not in self._tools:
            raise KeyError(f"Tool {name} not registered")
        return self._tools[name]

    def register_sandbox_provider(
        self, name: str, provider: Type[Sandbox]
    ) -> None:
        """
        Register a sandbox provider.

        Args:
            name: Provider name
            provider: Provider class
        """
        self._sandbox_providers[name] = provider

    async def create_sandbox(
        self, provider: str, config: SandboxConfig
    ) -> str:
        """
        Create new sandbox instance.

        Args:
            provider: Provider name
            config: Sandbox configuration

        Returns:
            Sandbox ID

        Raises:
            SandboxError: If creation fails
        """
        if provider not in self._sandbox_providers:
            raise SandboxError(f"Unknown provider: {provider}")

        try:
            # Create sandbox instance
            provider_class = self._sandbox_providers[provider]
            sandbox = provider_class(config)
            await sandbox.setup()

            # Generate ID and store
            sandbox_id = f"SANDBOX_{abs(hash(str(datetime.now())))}"
            self._active_sandboxes[sandbox_id] = sandbox

            return sandbox_id

        except Exception as e:
            raise SandboxError(f"Failed to create sandbox: {e}")

    async def get_sandbox(self, sandbox_id: str) -> Sandbox:
        """
        Get active sandbox by ID.

        Args:
            sandbox_id: Sandbox ID

        Returns:
            Sandbox instance
        """
        if sandbox_id not in self._active_sandboxes:
            raise SandboxError(f"Unknown sandbox: {sandbox_id}")
        return self._active_sandboxes[sandbox_id]

    async def create_session(
        self, files: List[str], sandbox_id: Optional[str] = None
    ) -> str:
        """
        Create new coding session.

        Args:
            files: Files to include
            sandbox_id: Optional sandbox to use

        Returns:
            Session ID
        """
        if len(self._sessions) >= self.max_sessions:
            raise SessionError("Maximum sessions reached")

        # Validate all files
        resolved_paths = []
        for file in files:
            path = Path(file).resolve()
            if not path.exists():
                raise SessionError(f"File not found: {path}")
            resolved_paths.append(str(path))

        # Create session
        session_id = f"SESS_{abs(hash(str(datetime.now())))}"
        session = CodeSession(
            session_id=session_id,
            files=resolved_paths,
            sandbox_id=sandbox_id,
            created_at=datetime.now().isoformat(),
        )

        self._sessions[session_id] = session
        return session_id

    def get_session(self, session_id: str) -> CodeSession:
        """Get session by ID"""
        if session_id not in self._sessions:
            raise SessionError(f"Unknown session: {session_id}")
        return self._sessions[session_id]

    async def _periodic_cleanup(self) -> None:
        """Run periodic cleanup of expired sessions and sandboxes"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self.cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue cleanup loop
                print(f"Cleanup error: {e}")

    async def cleanup(self) -> None:
        """
        Clean up expired sessions and sandboxes.
        Removes sessions older than session_ttl.
        """
        now = datetime.now()
        expired_sessions = []

        # Find expired sessions
        for session_id, session in self._sessions.items():
            created = datetime.fromisoformat(session.created_at)
            age = (now - created).total_seconds()

            if age > self.session_ttl:
                expired_sessions.append(session_id)

                # Cleanup associated sandbox
                if session.sandbox_id:
                    try:
                        sandbox = self._active_sandboxes.get(
                            session.sandbox_id
                        )
                        if sandbox:
                            await sandbox.cleanup()
                            self._active_sandboxes.pop(session.sandbox_id)
                    except Exception as e:
                        print(f"Failed to cleanup sandbox: {e}")

        # Remove expired sessions
        for session_id in expired_sessions:
            self._sessions.pop(session_id)

    def fuzzy_find(
        self,
        query: str,
        choices: List[str],
        threshold: float = 0.8,
        algorithm: str = "jaro_winkler",
    ) -> List[str]:
        """
        Find matches using fuzzy string matching.

        Args:
            query: Search string
            choices: Strings to search
            threshold: Minimum similarity score
            algorithm: Similarity algorithm to use

        Returns:
            List of matches above threshold
        """
        matches = []
        for choice in choices:
            score = string_similarity(
                query, choice, algorithm=algorithm, threshold=threshold
            )
            if score:
                matches.append(choice)
        return matches
