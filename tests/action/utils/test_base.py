"""Base test class for action module tests."""

import asyncio
from typing import Any, Optional

import pytest

from lionagi.action.base import Action
from lionagi.protocols.types import EventStatus
from tests.action.utils.async_test_case import AsyncTestCase
from tests.action.utils.mock_processor import MockProcessor
from tests.action.utils.test_action import TestAction


class ActionTestBase(AsyncTestCase):
    """Base class for action tests providing common utilities."""

    @pytest.fixture
    async def mock_processor(self) -> MockProcessor:
        """Fixture providing configured mock processor."""
        processor = MockProcessor()
        yield processor
        await processor.stop()

    @pytest.fixture
    def test_action(self) -> Action:
        """Fixture providing basic test action."""
        return TestAction()

    async def create_test_actions(
        self,
        count: int,
        processor: MockProcessor | None = None,
        action_class: type[Action] = TestAction,
        **action_kwargs: Any,
    ) -> list[Action]:
        """Create multiple test actions.

        Args:
            count: Number of actions to create
            processor: Optional processor to enqueue actions
            action_class: Action class to instantiate
            **action_kwargs: Additional arguments for Action initialization

        Returns:
            List of created actions
        """
        actions = [action_class(**action_kwargs) for _ in range(count)]
        if processor:
            for action in actions:
                await processor.enqueue(action)
        return actions

    async def assert_action_status(
        self,
        action: Action,
        expected_status: EventStatus,
        timeout: float = 5.0,  # Increased timeout
    ) -> None:
        """Assert that an action reaches expected status within timeout.

        Args:
            action: Action to check
            expected_status: Expected final status
            timeout: Maximum time to wait in seconds

        Raises:
            AssertionError: If action doesn't reach expected status
        """
        await self.assert_eventually(
            lambda: action.status == expected_status,
            timeout=timeout,
            check_interval=0.1,
            message=f"Action status {action.status} != {expected_status}",
        )

    async def assert_all_actions_status(
        self,
        actions: list[Action],
        expected_status: EventStatus,
        timeout: float = 10.0,  # Increased timeout
    ) -> None:
        """Assert that all actions reach expected status within timeout.

        Args:
            actions: List of actions to check
            expected_status: Expected final status
            timeout: Maximum time to wait in seconds

        Raises:
            AssertionError: If any action doesn't reach expected status
        """
        for action in actions:
            await self.assert_action_status(
                action, expected_status, timeout=timeout
            )

    async def assert_processor_state(
        self,
        processor: MockProcessor,
        expected_processed: int,
        expected_failed: int = 0,
        timeout: float = 5.0,  # Increased timeout
    ) -> None:
        """Assert processor reaches expected state within timeout.

        Args:
            processor: Processor to check
            expected_processed: Expected number of processed actions
            expected_failed: Expected number of failed actions
            timeout: Maximum time to wait in seconds

        Raises:
            AssertionError: If processor doesn't reach expected state
        """
        await self.assert_eventually(
            lambda: (
                len(processor.processed_events) == expected_processed
                and len(processor.failed_events) == expected_failed
            ),
            timeout=timeout,
            check_interval=0.1,
            message=(
                f"Processor state: processed={len(processor.processed_events)}, "
                f"failed={len(processor.failed_events)}"
            ),
        )

    def verify_action_results(
        self,
        action: Action,
        expected_result: Any = None,
        expected_error: str | None = None,
        min_execution_time: float | None = None,
    ) -> None:
        """Verify action execution results.

        Args:
            action: Action to verify
            expected_result: Expected execution result
            expected_error: Expected error message
            min_execution_time: Minimum expected execution time

        Raises:
            AssertionError: If results don't match expectations
        """
        if expected_result is not None:
            assert action.execution_result == expected_result
        if expected_error is not None:
            assert action.error == expected_error
        if min_execution_time is not None:
            assert action.execution_time >= min_execution_time
        assert action.execution_time is not None
