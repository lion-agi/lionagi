"""Integration tests for action processing workflow."""

import asyncio
from collections.abc import Callable
from typing import Any

import pytest

from lionagi.action.base import Action
from lionagi.action.function_calling import FunctionCalling
from lionagi.action.tool import Tool
from lionagi.protocols.types import EventStatus
from tests.action.utils.mock_processor import MockProcessor
from tests.action.utils.test_base import ActionTestBase


class TestActionProcessing(ActionTestBase):
    """Integration tests for complete action processing workflow."""

    @pytest.fixture
    async def async_success_tool(self) -> Tool:
        """Fixture providing tool that succeeds."""

        async def success_func(value: Any = None) -> dict[str, Any]:
            await asyncio.sleep(0.1)
            return {"result": value or "success"}

        return Tool(
            function=success_func,
            schema_={
                "name": "success_func",
                "parameters": {
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                },
            },
        )

    @pytest.fixture
    async def async_error_tool(self) -> Tool:
        """Fixture providing tool that fails."""

        async def error_func() -> None:
            await asyncio.sleep(0.1)
            raise ValueError("Simulated error")

        return Tool(
            function=error_func,
            schema_={
                "name": "error_func",
                "parameters": {"type": "object", "properties": {}},
            },
        )

    @pytest.mark.asyncio
    async def test_successful_action_processing(
        self, mock_processor: MockProcessor, async_success_tool: Tool
    ):
        """Test successful processing of action through tool execution."""
        # Create function calling with success tool
        action = FunctionCalling.create(
            tool=async_success_tool, arguments={"value": "test_value"}
        )

        # Process the action
        await mock_processor.enqueue(action)
        await mock_processor.process()

        # Verify results
        await self.assert_action_status(action, EventStatus.COMPLETED)
        await self.assert_processor_state(mock_processor, expected_processed=1)

        self.verify_action_results(
            action, expected_result={"result": "test_value"}
        )

    @pytest.mark.asyncio
    async def test_failed_action_processing(
        self, mock_processor: MockProcessor, async_error_tool: Tool
    ):
        """Test failed action processing with error handling."""
        # Create function calling with error tool
        action = FunctionCalling.create(tool=async_error_tool, arguments={})

        # Process the action
        await mock_processor.enqueue(action)
        await mock_processor.process()

        # Verify error handling
        await self.assert_action_status(action, EventStatus.FAILED)
        await self.assert_processor_state(
            mock_processor, expected_processed=0, expected_failed=1
        )

        self.verify_action_results(action, expected_error="Simulated error")

    @pytest.mark.asyncio
    async def test_concurrent_action_processing(
        self, mock_processor: MockProcessor, async_success_tool: Tool
    ):
        """Test concurrent processing of multiple actions."""
        # Create multiple actions
        actions = []
        for i in range(5):
            action = FunctionCalling.create(
                tool=async_success_tool, arguments={"value": f"test_{i}"}
            )
            actions.append(action)
            await mock_processor.enqueue(action)

        # Process all actions
        await mock_processor.process()

        # Verify all completed successfully
        await self.assert_all_actions_status(actions, EventStatus.COMPLETED)
        await self.assert_processor_state(mock_processor, expected_processed=5)

        # Verify results
        for i, action in enumerate(actions):
            self.verify_action_results(
                action, expected_result={"result": f"test_{i}"}
            )

    @pytest.mark.asyncio
    async def test_action_retry_behavior(self, async_success_tool: Tool):
        """Test action retry behavior on failure."""
        # Create processor with retry configuration
        processor = MockProcessor(
            should_fail=True, max_retries=2, processing_time=0.1
        )

        # Create and process action
        action = FunctionCalling.create(
            tool=async_success_tool, arguments={"value": "retry_test"}
        )

        await processor.enqueue(action)
        await processor.process()

        # Verify retry attempts and final failure
        await self.assert_action_status(action, EventStatus.FAILED)
        assert processor.retry_counts[str(action.id)] == 2

        await processor.stop()

    @pytest.mark.asyncio
    async def test_processor_capacity_handling(
        self, mock_processor: MockProcessor, async_success_tool: Tool
    ):
        """Test processor handles capacity limits correctly."""
        # Set small capacity
        mock_processor.capacity = 2

        # Create more actions than capacity
        actions = []
        for _ in range(5):
            action = FunctionCalling.create(
                tool=async_success_tool, arguments={"value": "capacity_test"}
            )
            actions.append(action)
            await mock_processor.enqueue(action)

        # Process actions
        await mock_processor.process()

        # Verify all eventually complete despite capacity limit
        await self.assert_all_actions_status(actions, EventStatus.COMPLETED)
        await self.assert_processor_state(mock_processor, expected_processed=5)
