"""Tests for action processing with real-world scenarios."""

import asyncio
from typing import Any

import pytest

from lionagi.action.executor import ActionExecutor
from lionagi.action.function_calling import FunctionCalling
from lionagi.action.processor import ActionProcessor
from lionagi.action.tool import Tool
from lionagi.protocols.types import EventStatus


# Example async functions that might be used in real applications
async def fetch_user(user_id: str, **kwargs: Any) -> dict[str, Any]:
    """Simulate fetching user data."""
    await asyncio.sleep(0.1)
    return {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
    }


async def update_profile(
    user_id: str, data: dict[str, Any], **kwargs: Any
) -> dict[str, Any]:
    """Simulate updating user profile."""
    await asyncio.sleep(0.1)
    return {
        "id": user_id,
        "updated": data,
        "timestamp": "2024-01-01T00:00:00Z",
    }


async def send_notification(
    user_id: str, message: str, **kwargs: Any
) -> dict[str, Any]:
    """Simulate sending notification."""
    await asyncio.sleep(0.1)
    return {"user_id": user_id, "message": message, "sent": True}


class TestActionProcessing:
    """Test action processing with realistic scenarios."""

    @pytest.fixture
    def executor(self) -> ActionExecutor:
        """Create executor with realistic configuration."""
        return ActionExecutor(
            processor_class=ActionProcessor,
            processor_config={
                "capacity": 5,  # Handle 5 concurrent operations
                "refresh_time": 0.1,  # Check queue every 100ms
            },
            strict=True,  # Enforce type checking
        )

    @pytest.fixture
    def user_tools(self) -> list[Tool]:
        """Create tools for user operations."""
        return [
            Tool(
                function=fetch_user,
                schema_={
                    "name": "fetch_user",
                    "parameters": {
                        "type": "object",
                        "properties": {"user_id": {"type": "string"}},
                        "required": ["user_id"],
                    },
                },
            ),
            Tool(
                function=update_profile,
                schema_={
                    "name": "update_profile",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "data": {"type": "object"},
                        },
                        "required": ["user_id", "data"],
                    },
                },
            ),
            Tool(
                function=send_notification,
                schema_={
                    "name": "send_notification",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "message": {"type": "string"},
                        },
                        "required": ["user_id", "message"],
                    },
                },
            ),
        ]

    @pytest.mark.asyncio(loop_scope="function")
    async def test_user_operation_workflow(
        self, executor: ActionExecutor, user_tools: list[Tool]
    ) -> None:
        """Test complete user operation workflow."""
        fetch_tool, update_tool, notify_tool = user_tools
        user_id = "123"

        # Start executor
        await executor.start()

        # 1. Fetch user data
        fetch_action = FunctionCalling.create(
            tool=fetch_tool, arguments={"user_id": user_id}
        )
        await executor.append(fetch_action)
        await executor.forward()

        assert fetch_action.status == EventStatus.COMPLETED
        user_data = fetch_action.execution_result

        # 2. Update profile
        update_action = FunctionCalling.create(
            tool=update_tool,
            arguments={"user_id": user_id, "data": {"status": "active"}},
        )
        await executor.append(update_action)
        await executor.forward()

        assert update_action.status == EventStatus.COMPLETED
        update_result = update_action.execution_result

        # 3. Send notification
        notify_action = FunctionCalling.create(
            tool=notify_tool,
            arguments={
                "user_id": user_id,
                "message": "Profile updated successfully",
            },
        )
        await executor.append(notify_action)
        await executor.forward()

        assert notify_action.status == EventStatus.COMPLETED
        notify_result = notify_action.execution_result

        # Verify workflow results
        assert user_data["id"] == user_id
        assert update_result["updated"]["status"] == "active"
        assert notify_result["sent"]

    @pytest.mark.asyncio(loop_scope="function")
    async def test_concurrent_user_operations(
        self, executor: ActionExecutor, user_tools: list[Tool]
    ) -> None:
        """Test concurrent user operations."""
        fetch_tool = user_tools[0]
        user_ids = ["101", "102", "103", "104", "105"]

        # Start executor
        await executor.start()

        # Create multiple fetch operations
        actions = [
            FunctionCalling.create(
                tool=fetch_tool, arguments={"user_id": user_id}
            )
            for user_id in user_ids
        ]

        # Add all actions
        for action in actions:
            await executor.append(action)

        # Process all actions
        await executor.forward()

        # Verify all operations completed
        assert len(executor.completed_action) == len(user_ids)
        for action in actions:
            assert action.status == EventStatus.COMPLETED
            assert action.execution_result["id"] in user_ids

    @pytest.mark.asyncio
    async def test_error_handling_in_workflow(
        self, executor: ActionExecutor, user_tools: list[Tool]
    ) -> None:
        """Test error handling in workflow."""
        update_tool = user_tools[1]

        # Start executor
        await executor.start()

        # Attempt update with invalid data
        action = FunctionCalling.create(
            tool=update_tool,
            arguments={
                "user_id": "123",
                # Missing required 'data' field
            },
        )
        await executor.append(action)
        await executor.forward()

        assert action.status == EventStatus.FAILED
        assert action.error is not None

    @pytest.mark.asyncio
    async def test_processor_capacity_management(
        self, executor: ActionExecutor, user_tools: list[Tool]
    ) -> None:
        """Test processor capacity management."""
        fetch_tool = user_tools[0]

        # Create more actions than processor capacity
        actions = [
            FunctionCalling.create(
                tool=fetch_tool, arguments={"user_id": str(i)}
            )
            for i in range(10)  # 10 actions, capacity is 5
        ]

        # Start executor
        await executor.start()

        # Add all actions
        for action in actions:
            await executor.append(action)

        # Process all actions
        await executor.forward()

        # Verify all actions completed despite capacity limit
        assert len(executor.completed_action) == 10
        assert all(
            action.status == EventStatus.COMPLETED for action in actions
        )

    @pytest.mark.asyncio
    async def test_executor_lifecycle_management(
        self, executor: ActionExecutor, user_tools: list[Tool]
    ) -> None:
        """Test executor lifecycle management."""
        notify_tool = user_tools[2]

        # Start executor
        await executor.start()
        assert executor.processor is not None

        # Add and process an action
        action = FunctionCalling.create(
            tool=notify_tool,
            arguments={"user_id": "123", "message": "Test message"},
        )
        await executor.append(action)
        await executor.forward()

        # Stop executor
        await executor.stop()
        assert executor.processor.is_stopped()

        # Verify action completed before stop
        assert action.status == EventStatus.COMPLETED
