"""Unit tests for the Action class."""

import asyncio
from datetime import datetime
from uuid import uuid4

import pytest

from lionagi.action.base import Action
from lionagi.protocols.types import EventStatus, Log
from tests.action.utils.test_action import TestAction
from tests.action.utils.test_base import ActionTestBase


class TestActionImplementation(ActionTestBase):
    """Test cases for Action class functionality."""

    def test_action_initialization(self, test_action: TestAction):
        """Test action initialization with default values."""
        assert test_action.status == EventStatus.PENDING
        assert test_action.execution_time is None
        assert test_action.execution_result is None
        assert test_action.error is None

    def test_action_status_transitions(self, test_action: TestAction):
        """Test valid action status transitions."""
        # PENDING -> PROCESSING
        test_action.status = EventStatus.PROCESSING
        assert test_action.status == EventStatus.PROCESSING

        # PROCESSING -> COMPLETED
        test_action.status = EventStatus.COMPLETED
        assert test_action.status == EventStatus.COMPLETED

        # Reset and test failure path
        test_action.status = EventStatus.PENDING
        test_action.status = EventStatus.PROCESSING
        test_action.status = EventStatus.FAILED
        assert test_action.status == EventStatus.FAILED

    def test_action_result_handling(self, test_action: TestAction):
        """Test action result and error handling."""
        test_result = {"key": "value"}
        test_action.execution_result = test_result
        test_action.execution_time = 1.5
        test_action.status = EventStatus.COMPLETED

        assert test_action.execution_result == test_result
        assert test_action.execution_time == 1.5
        assert test_action.error is None

    def test_action_error_handling(self, test_action: TestAction):
        """Test action error handling."""
        error_msg = "Test error message"
        test_action.error = error_msg
        test_action.execution_time = 0.5
        test_action.status = EventStatus.FAILED

        assert test_action.error == error_msg
        assert test_action.execution_time == 0.5
        assert test_action.execution_result is None
        assert test_action.status == EventStatus.FAILED

    def test_action_to_log_conversion(self, test_action: TestAction):
        """Test conversion of action to log entry."""
        # Set mutable fields for log conversion
        test_action.execution_time = 1.0
        test_action.execution_result = {"success": True}
        test_action.status = EventStatus.COMPLETED

        log = test_action.to_log()
        assert isinstance(log, Log)
        assert log.content["status"] == test_action.status
        assert log.content["execution_time"] == test_action.execution_time
        assert log.content["execution_result"] == test_action.execution_result
        assert (
            log.content["created_timestamp"] == test_action.created_timestamp
        )

    def test_action_request_property(self, test_action: TestAction):
        """Test default request property."""
        assert test_action.request == {}

    def test_action_repr(self, test_action: TestAction):
        """Test string representation of action."""
        test_action.status = EventStatus.COMPLETED
        test_action.execution_time = 1.5

        expected = "Action(status=COMPLETED, execution_time=1.5)"
        assert repr(test_action) == expected

    def test_action_from_dict_prevention(self, test_action: TestAction):
        """Test that from_dict raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            test_action.from_dict({})

    @pytest.mark.asyncio
    async def test_action_concurrent_status_updates(self):
        """Test concurrent status updates on action."""
        actions = await self.create_test_actions(5)

        # Simulate concurrent status updates
        async def update_status(action: Action, status: EventStatus):
            action.status = status

        await asyncio.gather(
            *[update_status(a, EventStatus.PROCESSING) for a in actions]
        )

        for action in actions:
            assert action.status == EventStatus.PROCESSING

    @pytest.mark.asyncio
    async def test_action_execution_timing(self):
        """Test action execution timing tracking."""
        action = TestAction(test_delay=0.1)

        async with self.assert_takes_less_than(0.2):
            await action.invoke()

        assert action.execution_time is not None
        assert action.execution_time >= 0.1
        assert action.status == EventStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_action_execution_error(self):
        """Test action execution error handling."""
        error_msg = "Test execution error"
        action = TestAction(test_error=error_msg)

        await action.invoke()

        assert action.status == EventStatus.FAILED
        assert action.error == error_msg
        assert action.execution_time is not None
        assert action.execution_result is None
