"""Test configuration and fixtures for action module tests."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest

from lionagi.action.tool import Tool
from lionagi.protocols.types import EventStatus


# Common async functions for testing
async def mock_api_call(
    endpoint: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Mock API call for testing.

    Args:
        endpoint: API endpoint to call
        params: Optional parameters
    """
    await asyncio.sleep(0.1)
    return {
        "status": "success",
        "endpoint": endpoint,
        "params": params or {},
        "timestamp": "2024-01-01T00:00:00Z",
    }


async def mock_data_processing(items: list[str]) -> dict[str, Any]:
    """Mock data processing for testing.

    Args:
        items: List of items to process
    """
    await asyncio.sleep(0.1)
    return {"processed": len(items), "items": items, "status": "completed"}


# Event loop is now managed by pytest-asyncio
# Use @pytest.mark.asyncio(scope='session') on test functions that need session-scoped event loop


@pytest.fixture
async def api_tool() -> Tool:
    """Fixture providing an API tool."""
    return Tool(
        function=mock_api_call,
        schema_={
            "name": "api_call",
            "description": "Make an API call",
            "parameters": {
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "string",
                        "description": "API endpoint to call",
                    },
                    "params": {
                        "type": "object",
                        "description": "Optional parameters",
                        "default": {},
                    },
                },
                "required": ["endpoint"],
            },
        },
    )


@pytest.fixture
async def processing_tool() -> Tool:
    """Fixture providing a data processing tool."""
    return Tool(
        function=mock_data_processing,
        schema_={
            "name": "process_data",
            "description": "Process data items",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of items to process",
                    }
                },
                "required": ["items"],
            },
        },
    )


@pytest.fixture(autouse=True)
async def cleanup_queues() -> AsyncGenerator[None, None]:
    """Cleanup any queues after each test."""
    yield
    # Allow pending tasks to complete
    await asyncio.sleep(0)

    # Get all tasks and cancel non-test tasks
    tasks = asyncio.all_tasks()
    test_tasks = {asyncio.current_task()}
    for task in tasks - test_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


@pytest.fixture(autouse=True)
def mock_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock asyncio.sleep for faster tests."""
    original_sleep = asyncio.sleep

    async def fast_sleep(delay: float) -> None:
        # For timing tests (0.1s or more), use real sleep
        if delay >= 0.1:
            await original_sleep(delay)
        # For shorter delays (e.g., refresh intervals), use minimal delay
        else:
            await original_sleep(0.001)

    monkeypatch.setattr(asyncio, "sleep", fast_sleep)


async def assert_action_status(
    action: Any, expected_status: EventStatus, timeout: float = 1.0
) -> None:
    """Assert that an action reaches expected status within timeout."""
    start_time = asyncio.get_event_loop().time()
    while (
        action.status != expected_status
        and (asyncio.get_event_loop().time() - start_time) < timeout
    ):
        await asyncio.sleep(0.1)

    assert (
        action.status == expected_status
    ), f"Action status {action.status} != {expected_status}"


async def assert_all_actions_status(
    actions: list[Any], expected_status: EventStatus, timeout: float = 2.0
) -> None:
    """Assert that all actions reach expected status within timeout."""
    for action in actions:
        await assert_action_status(action, expected_status, timeout=timeout)


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
