"""Async test utilities for action module testing."""

import asyncio
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any, Optional, TypeVar

import pytest

T = TypeVar("T")


class AsyncTestCase:
    """Base class for async test cases with utilities."""

    @staticmethod
    async def async_collect(agen: AsyncGenerator[T, None]) -> list[T]:
        """Collect all items from an async generator into a list.

        Args:
            agen: Async generator to collect from

        Returns:
            List containing all generated items
        """
        return [item async for item in agen]

    @staticmethod
    @asynccontextmanager
    async def assert_takes_less_than(seconds: float):
        """Assert that a code block executes within a time limit.

        Args:
            seconds: Maximum allowed execution time in seconds

        Raises:
            AssertionError: If execution takes longer than specified time
        """
        start = asyncio.get_event_loop().time()
        yield
        duration = asyncio.get_event_loop().time() - start
        assert (
            duration < seconds
        ), f"Operation took {duration:.2f}s, expected < {seconds}s"

    @staticmethod
    async def assert_eventually(
        condition: Callable[[], bool],
        timeout: float = 1.0,
        check_interval: float = 0.1,
        message: str | None = None,
    ) -> None:
        """Assert that a condition becomes true within a timeout period.

        Args:
            condition: Function that returns bool indicating if condition is met
            timeout: Maximum time to wait in seconds
            check_interval: Time between condition checks in seconds
            message: Custom error message if condition not met

        Raises:
            AssertionError: If condition not met within timeout
        """
        start = asyncio.get_event_loop().time()
        while True:
            if condition():
                return
            if asyncio.get_event_loop().time() - start > timeout:
                raise AssertionError(
                    message or f"Condition not met within {timeout} seconds"
                )
            # Use a fixed small delay to avoid recursion
            await asyncio.sleep(0.001)

    @staticmethod
    async def mock_async_func(*args: Any, **kwargs: Any) -> None:
        """Mock async function that does nothing."""
        pass

    @staticmethod
    async def mock_async_error(*args: Any, **kwargs: Any) -> None:
        """Mock async function that raises an error."""
        raise Exception("Mock error")


@pytest.fixture
async def async_test_case():
    """Fixture providing AsyncTestCase instance."""
    return AsyncTestCase()
