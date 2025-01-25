# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lionagi.tools.coder import CoderTool
from lionagi.tools.coder.types import AiderAction, ChatMode, CoderRequest

# Mock Constants for Testing
TEST_SESSION_ID = "test-session-123"
TEST_WORKING_DIR = "/tmp/test-project"
TEST_FILES = ["test.py", "utils.py"]
TEST_MODEL = "gpt-4o"


@pytest.fixture
async def coder_tool():
    """Fixture providing a CoderTool instance."""
    tool = CoderTool()
    yield tool
    # Cleanup any sessions
    for session_id in list(tool.registry.sessions.keys()):
        await tool.registry.cleanup(session_id, force=True)


@pytest.fixture
def mock_process():
    """Fixture providing a mock subprocess."""
    process = AsyncMock()
    process.returncode = None
    process.stdin = AsyncMock()
    process.stdout = AsyncMock()
    process.stderr = AsyncMock()
    return process


@pytest.mark.asyncio
async def test_session_creation(coder_tool):
    """Test creating a new session."""
    request = CoderRequest(
        action=AiderAction.START_SESSION,
        session_id=TEST_SESSION_ID,
        working_dir=TEST_WORKING_DIR,
        model=TEST_MODEL,
    )

    with patch(
        "asyncio.create_subprocess_exec", new_callable=AsyncMock
    ) as mock_exec:
        response = await coder_tool.handle_request(request)

        assert response.success
        assert response.session_id == TEST_SESSION_ID
        assert TEST_SESSION_ID in coder_tool.registry.sessions
        assert (
            coder_tool.registry.sessions[TEST_SESSION_ID].state.working_dir
            == TEST_WORKING_DIR
        )


@pytest.mark.asyncio
async def test_session_reuse(coder_tool):
    """Test reusing an existing session."""
    # First request creates session
    request1 = CoderRequest(
        action=AiderAction.START_SESSION,
        session_id=TEST_SESSION_ID,
        working_dir=TEST_WORKING_DIR,
    )

    # Second request reuses it
    request2 = CoderRequest(
        action=AiderAction.ADD_FILES,
        session_id=TEST_SESSION_ID,
        files=TEST_FILES,
    )

    with patch(
        "asyncio.create_subprocess_exec", new_callable=AsyncMock
    ) as mock_exec:
        response1 = await coder_tool.handle_request(request1)
        response2 = await coder_tool.handle_request(request2)

        assert response1.success and response2.success
        assert response1.session_id == response2.session_id
        assert mock_exec.call_count == 1  # Only one process created


@pytest.mark.asyncio
async def test_session_cleanup(coder_tool):
    """Test session cleanup on persist_session=False."""
    request = CoderRequest(
        action=AiderAction.START_SESSION,
        session_id=TEST_SESSION_ID,
        persist_session=False,
    )

    with patch(
        "asyncio.create_subprocess_exec", new_callable=AsyncMock
    ) as mock_exec:
        response = await coder_tool.handle_request(request)

        assert response.success
        assert TEST_SESSION_ID not in coder_tool.registry.sessions


@pytest.mark.asyncio
async def test_command_execution(coder_tool, mock_process):
    """Test executing commands in a session."""
    request = CoderRequest(
        action=AiderAction.ADD_FILES,
        session_id=TEST_SESSION_ID,
        files=TEST_FILES,
    )

    with patch(
        "asyncio.create_subprocess_exec", return_value=mock_process
    ) as mock_exec:
        # Setup mock process output
        mock_process.stdout.readline = AsyncMock(
            side_effect=[
                b"Added test.py to the chat\n",
                b"Added utils.py to the chat\n",
                b"> ",  # Prompt
            ]
        )

        response = await coder_tool.handle_request(request)

        assert response.success
        assert all(
            f in response.session_state.active_files for f in TEST_FILES
        )


@pytest.mark.asyncio
async def test_chat_mode_switch(coder_tool, mock_process):
    """Test switching chat modes."""
    request = CoderRequest(
        action=AiderAction.START_SESSION,
        session_id=TEST_SESSION_ID,
        chat_mode=ChatMode.ARCHITECT,
    )

    with patch(
        "asyncio.create_subprocess_exec", return_value=mock_process
    ) as mock_exec:
        mock_process.stdout.readline = AsyncMock(
            side_effect=[b"Switched to architect mode\n", b"> "]  # Prompt
        )

        response = await coder_tool.handle_request(request)

        assert response.success
        assert response.session_state.mode == ChatMode.ARCHITECT


@pytest.mark.asyncio
async def test_error_handling(coder_tool):
    """Test error handling for invalid requests."""
    # Test missing required parameter
    request = CoderRequest(
        action=AiderAction.ADD_FILES,
        session_id=TEST_SESSION_ID,
        files=None,  # Required parameter
    )

    response = await coder_tool.handle_request(request)
    assert not response.success
    assert "files parameter required" in response.error.lower()


@pytest.mark.asyncio
async def test_invalid_action(coder_tool):
    """Test handling of unknown actions."""
    request = CoderRequest(
        action=AiderAction.START_SESSION, session_id=TEST_SESSION_ID
    )

    # Simulate process creation failure
    with patch(
        "asyncio.create_subprocess_exec",
        side_effect=OSError("Failed to start"),
    ):
        response = await coder_tool.handle_request(request)

        assert not response.success
        assert "failed to start" in response.error.lower()


@pytest.mark.asyncio
async def test_session_timeout(coder_tool, mock_process):
    """Test session timeout handling."""
    request = CoderRequest(
        action=AiderAction.RUN_COMMAND,
        session_id=TEST_SESSION_ID,
        command="/status",
    )

    with patch(
        "asyncio.create_subprocess_exec", return_value=mock_process
    ) as mock_exec:
        # Setup mock to never return prompt
        mock_process.stdout.readline = AsyncMock(return_value=b"Working...\n")

        response = await coder_tool.handle_request(request)
        assert not response.success
        assert "timeout" in response.error.lower()


@pytest.mark.asyncio
async def test_reference_counting(coder_tool, mock_process):
    """Test session reference counting."""
    request1 = CoderRequest(
        action=AiderAction.START_SESSION, session_id=TEST_SESSION_ID
    )

    request2 = CoderRequest(
        action=AiderAction.ADD_FILES,
        session_id=TEST_SESSION_ID,
        files=TEST_FILES,
    )

    with patch("asyncio.create_subprocess_exec", return_value=mock_process):
        # First request
        response1 = await coder_tool.handle_request(request1)
        assert response1.session_state.reference_count == 1

        # Second request increases count
        response2 = await coder_tool.handle_request(request2)
        assert response2.session_state.reference_count == 2

        # Cleanup with persist=False decrements count
        request2.persist_session = False
        response3 = await coder_tool.handle_request(request2)
        assert response3.session_state.reference_count == 1


if __name__ == "__main__":
    pytest.main([__file__])
