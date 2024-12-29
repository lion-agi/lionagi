import asyncio
from typing import Any

import pytest

from lionagi.protocols.action.function_calling import (
    EventStatus,
    FunctionCalling,
    Tool,
)
from lionagi.utils import UNDEFINED


# Helper functions - not test cases
async def helper_async_func(x: int = 0, y: str = "default") -> str:
    """Test async function."""
    await asyncio.sleep(0.1)
    return f"{x}-{y}"


def helper_sync_func(x: int = 0, y: str = "default") -> str:
    """Test sync function."""
    return f"{x}-{y}"


async def helper_preprocessor(value: Any, **kwargs) -> Any:
    """Test preprocessor."""
    if isinstance(value, dict):
        value["x"] += 1
        return value
    return value


async def helper_postprocessor(result: Any, **kwargs) -> str:
    """Test postprocessor."""
    return f"processed-{result}"


def helper_parser(result: Any) -> str:
    """Test parser."""
    return str(result)


@pytest.fixture
def tool_with_processors():
    """Fixture for creating a tool with processors."""
    return Tool(
        func_callable=helper_sync_func,
        preprocessor=helper_preprocessor,
        postprocessor=helper_postprocessor,
    )


@pytest.fixture
def async_tool():
    """Fixture for creating an async tool."""
    return Tool(func_callable=helper_async_func)


@pytest.mark.asyncio
async def test_function_calling_init():
    """Test FunctionCalling initialization."""
    tool = Tool(func_callable=helper_sync_func)
    arguments = {"x": 1, "y": "test"}

    func_call = FunctionCalling(func_tool=tool, arguments=arguments)
    assert func_call.func_tool == tool
    assert func_call.arguments == arguments
    assert func_call.function == "helper_sync_func"
    assert func_call.status == EventStatus.PENDING


@pytest.mark.asyncio
async def test_function_calling_with_sync_function():
    """Test FunctionCalling with synchronous function."""
    tool = Tool(func_callable=helper_sync_func)
    func_call = FunctionCalling(
        func_tool=tool, arguments={"x": 1, "y": "test"}
    )

    await func_call.invoke()
    result = func_call.response
    assert result == "1-test"
    assert func_call.status == EventStatus.COMPLETED
    assert func_call.execution.duration is not None
    assert func_call.execution.response == "1-test"
    assert func_call.execution.error is None


@pytest.mark.asyncio
async def test_function_calling_with_async_function(async_tool):
    """Test FunctionCalling with asynchronous function."""
    func_call = FunctionCalling(
        func_tool=async_tool, arguments={"x": 1, "y": "test"}
    )

    await func_call.invoke()
    result = func_call.response
    assert result == "1-test"
    assert func_call.status == EventStatus.COMPLETED
    assert func_call.execution.duration is not None
    assert func_call.execution.response == "1-test"
    assert func_call.execution.error is None


@pytest.mark.asyncio
async def test_function_calling_with_processors(tool_with_processors):
    """Test FunctionCalling with pre/post processors."""
    func_call = FunctionCalling(
        func_tool=tool_with_processors, arguments={"x": 1, "y": "test"}
    )

    await func_call.invoke()
    result = func_call.response
    # Pre-processor adds 1 to x, so result should be "2-test"
    # Post-processor adds "processed-" prefix
    # Parser converts to string
    assert result == "processed-2-test"
    assert func_call.status == EventStatus.COMPLETED


@pytest.mark.asyncio
async def test_function_calling_error_handling():
    """Test FunctionCalling error handling."""

    async def error_func():
        raise ValueError("Test error")

    tool = Tool(func_callable=error_func)
    func_call = FunctionCalling(func_tool=tool, arguments={})

    await func_call.invoke()
    result = func_call.response
    assert result is None
    assert func_call.status == EventStatus.FAILED
    assert "Test error" in str(func_call.execution.error)
    assert func_call.execution.duration is not None


def test_function_calling_str_representation():
    """Test FunctionCalling string representations."""
    tool = Tool(func_callable=helper_sync_func)
    func_call = FunctionCalling(
        func_tool=tool, arguments={"x": 1, "y": "test"}
    )

    # Test __str__
    str_rep = str(func_call)
    assert "helper_sync_func" in str_rep
    assert "{'x': 1, 'y': 'test'}" in str_rep

    # Test __repr__
    repr_rep = repr(func_call)
    assert "FunctionCalling" in repr_rep
    assert "helper_sync_func" in repr_rep
    assert "{'x': 1, 'y': 'test'}" in repr_rep


@pytest.mark.asyncio
async def test_function_calling_with_empty_arguments():
    """Test FunctionCalling with empty arguments."""
    tool = Tool(func_callable=helper_sync_func)
    func_call = FunctionCalling(func_tool=tool, arguments={})

    await func_call.invoke()
    result = func_call.response
    assert result == "0-default"  # Should use default values
    assert func_call.status == EventStatus.COMPLETED


@pytest.mark.asyncio
async def test_function_calling_processor_error():
    """Test FunctionCalling with failing processor."""

    async def error_processor(value: Any, **kwargs) -> Any:
        raise ValueError("Processor error")

    tool = Tool(func_callable=helper_sync_func, preprocessor=error_processor)

    func_call = FunctionCalling(func_tool=tool, arguments={"x": 1})

    await func_call.invoke()
    result = func_call.response
    assert result is None
    assert func_call.status == EventStatus.FAILED
    assert "Processor error" in str(func_call.execution.error)
