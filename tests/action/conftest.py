"""Test configuration and shared fixtures for action module tests."""

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


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
        # For timing tests, use real sleep with scaled delay
        if delay >= 0.1:
            await original_sleep(delay)
        else:
            # For other operations, use minimal delay
            await original_sleep(0.001)

    monkeypatch.setattr(asyncio, "sleep", fast_sleep)


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Modify test collection with custom markers."""
    for item in items:
        # Mark performance tests as slow
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.performance)

        # Mark integration tests
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
