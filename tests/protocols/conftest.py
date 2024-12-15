"""Pytest configuration for protocol tests."""

import asyncio

import pytest


def pytest_configure(config):
    """Configure pytest-asyncio."""
    # Set asyncio mode
    config.option.asyncio_mode = "auto"

    # Explicitly set the default fixture loop scope
    setattr(config.option, "asyncio_default_fixture_loop_scope", "function")


@pytest.fixture(scope="session")
def event_loop_policy():
    """Configure event loop policy for the test session."""
    policy = asyncio.get_event_loop_policy()
    return policy


@pytest.fixture(scope="function")
async def log_manager_context():
    """Provide a clean event loop for each test function."""
    loop = asyncio.get_event_loop()
    yield loop

    # Clean up any pending tasks
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()

    if pending:
        await asyncio.gather(*pending, return_exceptions=True)
