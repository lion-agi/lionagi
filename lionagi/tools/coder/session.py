# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import time
import uuid
import weakref
from typing import Dict, Optional, Set

from pydantic import BaseModel

from .types import ChatMode, SessionState

# Constants
DEFAULT_SESSION_TIMEOUT = 3600  # 1 hour
MAX_INACTIVE_TIME = 7200  # 2 hours


class AiderSession:
    """
    Manages a persistent aider process and its state.
    Handles process control, command execution, and state tracking.
    """

    def __init__(
        self,
        session_id: str,
        working_dir: str,
        model: str = "gpt-4",
        git_enabled: bool = True,
    ):
        self.session_id = session_id
        self.process = None
        self.state = SessionState(
            working_dir=working_dir, model=model, git_enabled=git_enabled
        )
        self._locks: Dict[str, asyncio.Lock] = {
            "process": asyncio.Lock(),
            "command": asyncio.Lock(),
        }
        self._input_queue = asyncio.Queue()
        self._output_buffer = []

    def get_lock(self, name: str) -> asyncio.Lock:
        """Get a named lock for synchronization."""
        if name not in self._locks:
            self._locks[name] = asyncio.Lock()
        return self._locks[name]

    async def start(self) -> bool:
        """
        Start the aider process.
        Returns True if successful, False if already running.
        """
        async with self.get_lock("process"):
            if self.process and self.process.returncode is None:
                return False

            try:
                # Build command with args
                cmd = ["aider"]
                if self.state.model:
                    cmd.extend(["--model", self.state.model])
                if not self.state.git_enabled:
                    cmd.append("--no-git")

                # Start process
                self.process = await asyncio.create_subprocess_exec(
                    *cmd,
                    cwd=self.state.working_dir,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                # Start background tasks
                asyncio.create_task(self._read_output())
                asyncio.create_task(self._process_input())

                return True

            except Exception as e:
                self.state.last_operation = {"success": False, "error": str(e)}
                return False

    async def stop(self) -> None:
        """Stop the aider process."""
        async with self.get_lock("process"):
            if self.process:
                try:
                    await self.execute("/exit")
                except:
                    pass

                try:
                    self.process.terminate()
                    await self.process.wait()
                except:
                    pass
                finally:
                    self.process = None

    async def _read_output(self) -> None:
        """Background task to read process output."""
        if not self.process or not self.process.stdout:
            return

        partial_line = ""
        while True:
            if self.process.returncode is not None:
                break

            try:
                line = await self.process.stdout.readline()
                if not line:
                    break

                # Handle potential partial UTF-8 encoding
                try:
                    text = partial_line + line.decode("utf-8")
                    partial_line = ""
                except UnicodeDecodeError:
                    partial_line += line
                    continue

                text = text.rstrip("\n")
                self._output_buffer.append(text)

                # Parse aider output events
                await self._parse_output_event(text)

            except Exception as e:
                self.state.last_operation = {
                    "success": False,
                    "error": f"Output read error: {str(e)}",
                }
                break

        # Clear any remaining partial line
        if partial_line:
            try:
                text = partial_line.decode("utf-8").rstrip("\n")
                self._output_buffer.append(text)
                await self._parse_output_event(text)
            except:
                pass

    async def _parse_output_event(self, text: str) -> None:
        """Parse individual lines for state updates and events."""
        # File tracking events
        if "to the chat" in text:
            if text.startswith("Added "):
                filename = text[6 : text.index(" to the chat")].strip()
                self.state.active_files.add(filename)
            elif text.startswith("Dropped "):
                filename = text[8 : text.index(" from the chat")].strip()
                self.state.active_files.discard(filename)

        # Error detection
        if text.startswith(("Error:", "Traceback")):
            self.state.last_operation = {"success": False, "error": text}

        # Git status updates
        if text.startswith("On branch "):
            # Basic git status parsing
            self.state.git_status = {"branch": text[10:].strip()}

    async def _process_input(self) -> None:
        """Background task to process input queue."""
        if not self.process or not self.process.stdin:
            return

        while True:
            try:
                command = await self._input_queue.get()
                if command is None:  # Shutdown signal
                    break

                # Handle multi-line inputs
                if isinstance(command, (list, tuple)):
                    for line in command:
                        await self._write_line(line)
                else:
                    await self._write_line(command)

            except Exception as e:
                self.state.last_operation = {
                    "success": False,
                    "error": f"Input processing error: {str(e)}",
                }

    async def _write_line(self, line: str) -> None:
        """Write a single line to the process with proper line ending."""
        if not line.endswith("\n"):
            line += "\n"
        try:
            self.process.stdin.write(line.encode("utf-8"))
            await self.process.stdin.drain()
        except Exception as e:
            raise RuntimeError(f"Failed to write to process: {str(e)}")

    async def execute(self, command: str) -> dict:
        """
        Execute a command in the aider process.
        Returns dict with output and status.
        """
        # Update last used time
        self.state.last_used_at = asyncio.get_event_loop().time()

        async with self.get_lock("command"):
            try:
                # Clear output buffer
                self._output_buffer = []

                # Send command
                await self._input_queue.put(command)

                # Wait for output with timeout
                timeout = 30.0  # 30 second timeout
                start_time = asyncio.get_event_loop().time()

                # Wait until we see the aider prompt or timeout
                while True:
                    if asyncio.get_event_loop().time() - start_time > timeout:
                        raise TimeoutError(
                            "Command timed out waiting for response"
                        )

                    # Check if we have output and see a prompt-like pattern
                    if self._output_buffer and any(
                        line.rstrip().endswith(("> ", "? "))
                        for line in self._output_buffer[-3:]
                    ):
                        break

                    await asyncio.sleep(0.1)

                result = {
                    "success": True,
                    "output": "\n".join(self._output_buffer),
                }

                # Update state based on command
                if command.startswith("/chat-mode "):
                    mode = command[11:].strip()
                    if mode in ChatMode.__members__:
                        self.state.mode = ChatMode[mode.upper()]

                elif command == "/diff":
                    # Extract diff content (everything between the command and prompt)
                    diff_lines = []
                    in_diff = False
                    for line in self._output_buffer:
                        if line == "/diff":
                            in_diff = True
                            continue
                        if line.rstrip().endswith(("> ", "? ")):
                            break
                        if in_diff:
                            diff_lines.append(line)
                    result["diff"] = (
                        "\n".join(diff_lines) if diff_lines else None
                    )

                self.state.last_operation = result
                return result

            except Exception as e:
                error_result = {
                    "success": False,
                    "error": str(e),
                    "output": "\n".join(self._output_buffer),
                }
                self.state.last_operation = error_result
                return error_result


class AiderSessionRegistry:
    """
    Manages multiple aider sessions with reference counting and cleanup.
    """

    def __init__(self):
        self.sessions: Dict[str, AiderSession] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

        # Start cleanup task
        loop = asyncio.get_event_loop()
        self._cleanup_task = loop.create_task(
            self._cleanup_inactive_sessions()
        )

    async def get_or_create(
        self, session_id: Optional[str] = None, **config
    ) -> AiderSession:
        """Get existing session or create new one."""
        if not session_id:
            session_id = str(uuid.uuid4())

        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.state.reference_count += 1
        else:
            session = AiderSession(session_id, **config)
            await session.start()
            self.sessions[session_id] = session
            self.locks[session_id] = asyncio.Lock()

        # Update last used time
        session.state.last_used_at = asyncio.get_event_loop().time()
        return session

    async def cleanup(self, session_id: str, force: bool = False) -> None:
        """
        Clean up session resources.

        Args:
            session_id: ID of session to clean up
            force: If True, cleanup regardless of reference count
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]

            if force:
                session.state.reference_count = 0
            else:
                session.state.reference_count -= 1

            if session.state.reference_count <= 0:
                await session.stop()
                self.sessions.pop(session_id)
                self.locks.pop(session_id)

    async def _cleanup_inactive_sessions(self) -> None:
        """Background task to cleanup inactive sessions."""
        while True:
            try:
                current_time = asyncio.get_event_loop().time()

                # Find inactive sessions
                inactive_sessions = []
                for session_id, session in self.sessions.items():
                    inactive_time = current_time - session.state.last_used_at

                    # Force cleanup if session is very old
                    if inactive_time > MAX_INACTIVE_TIME:
                        inactive_sessions.append((session_id, True))

                    # Clean up if no references and inactive
                    elif (
                        session.state.reference_count <= 0
                        and inactive_time > DEFAULT_SESSION_TIMEOUT
                    ):
                        inactive_sessions.append((session_id, False))

                # Cleanup inactive sessions
                for session_id, force in inactive_sessions:
                    await self.cleanup(session_id, force=force)

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                print(f"Error in session cleanup: {e}")
                await asyncio.sleep(300)  # Back off on error


__all__ = (
    "AiderSession",
    "AiderSessionRegistry",
)
