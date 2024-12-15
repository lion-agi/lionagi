"""Tests for FunctionCalling implementation with real tools."""

import asyncio
from typing import Any

import pytest

from lionagi.action.function_calling import FunctionCalling
from lionagi.action.tool import Tool
from lionagi.protocols.types import EventStatus


async def example_api_call(**kwargs: Any) -> dict[str, Any]:
    """Example async API call function."""
    await asyncio.sleep(0.1)  # Simulate network delay
    return {
        "status": "success",
        "data": kwargs,
        "timestamp": "2024-01-01T00:00:00Z",
    }


async def data_processing(**kwargs: Any) -> list[dict[str, Any]]:
    """Example data processing function."""
    items = kwargs.get("items", [])
    processed = [{"item": item, "processed": True} for item in items]
    return processed


async def error_prone_operation(**kwargs: Any) -> None:
    """Example operation that may fail."""
    if kwargs.get("should_fail"):
        raise ValueError("Operation failed as requested")
    return {"status": "success"}


class TestFunctionCalling:
    """Test FunctionCalling with realistic tool scenarios."""

    @pytest.fixture
    def api_tool(self) -> Tool:
        """Create tool for API operations."""
        return Tool(
            function=example_api_call,
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
                        },
                    },
                    "required": ["endpoint"],
                },
            },
        )

    @pytest.fixture
    def processing_tool(self) -> Tool:
        """Create tool for data processing."""
        return Tool(
            function=data_processing,
            schema_={
                "name": "process_data",
                "description": "Process data items",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "items": {"type": "array", "items": {"type": "string"}}
                    },
                },
            },
        )

    @pytest.fixture
    def error_tool(self) -> Tool:
        """Create tool that can fail."""
        return Tool(
            function=error_prone_operation,
            schema_={
                "name": "risky_operation",
                "description": "Operation that may fail",
                "parameters": {
                    "type": "object",
                    "properties": {"should_fail": {"type": "boolean"}},
                },
            },
        )

    @pytest.mark.asyncio(loop_scope="function")
    async def test_api_call_execution(self, api_tool: Tool) -> None:
        """Test executing an API call through FunctionCalling."""
        args = {"endpoint": "/users", "params": {"id": 123}}
        action = FunctionCalling.create(tool=api_tool, arguments=args)

        await action.invoke()

        assert action.status == EventStatus.COMPLETED
        assert action.execution_time >= 0.1  # Account for sleep
        assert action.execution_result["status"] == "success"
        assert action.execution_result["data"] == args
        assert action.error is None

    @pytest.mark.asyncio(loop_scope="function")
    async def test_data_processing(self, processing_tool: Tool) -> None:
        """Test data processing execution."""
        items = ["item1", "item2", "item3"]
        action = FunctionCalling.create(
            tool=processing_tool, arguments={"items": items}
        )

        await action.invoke()

        assert action.status == EventStatus.COMPLETED
        assert len(action.execution_result) == len(items)
        for result, item in zip(action.execution_result, items):
            assert result["item"] == item
            assert result["processed"]

    @pytest.mark.asyncio
    async def test_error_handling(self, error_tool: Tool) -> None:
        """Test error handling in function execution."""
        action = FunctionCalling.create(
            tool=error_tool, arguments={"should_fail": True}
        )

        await action.invoke()

        assert action.status == EventStatus.FAILED
        assert action.execution_time is not None
        assert action.execution_result is None
        assert "Operation failed as requested" in action.error

    @pytest.mark.asyncio
    async def test_concurrent_execution(
        self, api_tool: Tool, processing_tool: Tool
    ) -> None:
        """Test concurrent execution of multiple function calls."""
        actions = [
            FunctionCalling.create(
                tool=api_tool, arguments={"endpoint": f"/resource/{i}"}
            )
            for i in range(3)
        ]
        actions.extend(
            [
                FunctionCalling.create(
                    tool=processing_tool, arguments={"items": [f"item{i}"]}
                )
                for i in range(3)
            ]
        )

        # Execute all actions concurrently
        await asyncio.gather(*(action.invoke() for action in actions))

        assert all(
            action.status == EventStatus.COMPLETED for action in actions
        )
        assert all(action.execution_time is not None for action in actions)
        assert all(action.error is None for action in actions)

    @pytest.mark.asyncio
    async def test_tool_validation(self, api_tool: Tool) -> None:
        """Test tool validation during function calling."""
        # Test with missing required parameter
        action = FunctionCalling.create(
            tool=api_tool,
            arguments={"params": {}},  # Missing required 'endpoint'
        )

        await action.invoke()

        assert action.status == EventStatus.FAILED
        assert "Missing required parameter: endpoint" in action.error

        # Test with invalid parameter type
        action = FunctionCalling.create(
            tool=api_tool,
            arguments={"endpoint": 123, "params": {}},  # Should be string
        )

        await action.invoke()

        assert action.status == EventStatus.FAILED
        assert "Parameter endpoint must be a string" in action.error
        assert action.error is not None

    @pytest.mark.asyncio
    async def test_execution_state_transitions(self, api_tool: Tool) -> None:
        """Test action state transitions during execution."""
        action = FunctionCalling.create(
            tool=api_tool, arguments={"endpoint": "/test"}
        )

        assert action.status == EventStatus.PENDING

        # Start execution
        invoke_task = asyncio.create_task(action.invoke())

        # Allow time for processing to begin
        await asyncio.sleep(0.05)
        assert action.status == EventStatus.PROCESSING

        # Wait for completion
        await invoke_task
        assert action.status == EventStatus.COMPLETED
