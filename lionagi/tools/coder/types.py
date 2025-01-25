# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AiderAction(str, Enum):
    """
    Core actions that can be performed with the coder tool.
    Maps to specific aider functionality.
    """

    # Session Management
    START_SESSION = "start_session"
    END_SESSION = "end_session"

    # File Management
    ADD_FILES = "add_files"
    DROP_FILES = "drop_files"

    # Operation Modes
    ARCHITECT = "architect"
    CODE = "code"
    ASK = "ask"

    # Utility Actions
    RUN_COMMAND = "run_command"
    RUN_TEST = "run_test"
    RUN_LINT = "run_lint"

    # Git Operations
    COMMIT = "commit"
    SHOW_DIFF = "show_diff"


class ChatMode(str, Enum):
    """Available chat modes in aider."""

    CODE = "code"
    ARCHITECT = "architect"
    ASK = "ask"
    HELP = "help"


class SessionState(BaseModel):
    """Tracks the current state of an aider session."""

    active_files: set[str] = Field(
        default_factory=set, description="Files currently added to the session"
    )
    mode: ChatMode = Field(
        default=ChatMode.CODE, description="Current chat mode"
    )
    git_status: Dict[str, Any] | None = Field(
        default=None, description="Current git status if git is enabled"
    )
    last_operation: Dict[str, Any] | None = Field(
        default=None, description="Details about the last operation performed"
    )
    working_dir: str = Field(
        ..., description="Working directory for this session"
    )
    model: str = Field(
        default="gpt-4", description="Model being used for this session"
    )
    git_enabled: bool = Field(
        default=True, description="Whether git operations are enabled"
    )
    reference_count: int = Field(
        default=1, description="Number of active references to this session"
    )
    created_at: float = Field(
        default_factory=lambda: asyncio.get_event_loop().time(),
        description="Timestamp when session was created",
    )
    last_used_at: float = Field(
        default_factory=lambda: asyncio.get_event_loop().time(),
        description="Timestamp of last session activity",
    )

    def to_dict(self) -> dict:
        """Convert session state to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "SessionState":
        """Create session state from dictionary."""
        return cls(**data)


class CoderRequest(BaseModel):
    """Request model for coder tool operations."""

    # Session Management
    session_id: Optional[str] = Field(
        None,
        description="Session identifier for persistent operations. If None, creates new session",
    )
    persist_session: bool = Field(
        True, description="Whether to keep session alive after operation"
    )

    # Core Operation
    action: AiderAction = Field(..., description="The action to perform")

    # File Management
    files: Optional[List[str]] = Field(
        None,
        description="Files to operate on. Required for ADD_FILES and DROP_FILES actions",
    )

    # Command & Instruction
    command: Optional[str] = Field(
        None, description="Slash command or instruction to execute"
    )
    instruction: Optional[str] = Field(
        None, description="Free-form instruction for code changes or questions"
    )

    # Mode Settings
    chat_mode: Optional[ChatMode] = Field(
        None, description="Chat mode to use: code, architect, or ask"
    )

    # Git Integration
    commit_message: Optional[str] = Field(
        None, description="Commit message when using git operations"
    )
    git_enabled: bool = Field(
        True, description="Whether to enable git operations"
    )

    # Advanced Configuration
    working_dir: Optional[str] = Field(
        None, description="Working directory for the session"
    )
    model: str = Field(
        default="gpt-4", description="Model to use for the session"
    )
    extra_args: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional arguments for advanced usage",
    )


class CoderResponse(BaseModel):
    """Response model for coder tool operations."""

    success: bool = Field(..., description="Whether the operation succeeded")
    session_id: Optional[str] = Field(
        None, description="ID of the session used for the operation"
    )
    error: Optional[str] = Field(
        None, description="Error message if operation failed"
    )
    output: Optional[str] = Field(
        None, description="Console or chat output from aider"
    )
    final_diff: Optional[str] = Field(
        None, description="Git diff of changes if applicable"
    )
    git_status: Optional[Dict[str, Any]] = Field(
        None, description="Current git status if git enabled"
    )
    session_state: Optional[SessionState] = Field(
        None, description="Current state of the session"
    )


__all__ = (
    "AiderAction",
    "ChatMode",
    "SessionState",
    "CoderRequest",
    "CoderResponse",
)
