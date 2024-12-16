import asyncio
from typing import Any

import pytest

from lionagi.core.action.base import EventStatus
from lionagi.core.action.function_calling import FunctionCalling
from lionagi.core.action.tool import Tool
from lionagi.core.typing import UNDEFINED
from lionagi.settings import TimedFuncCallConfig


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
    if isinstance(value, int):
        return value + 1
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
        function=helper_sync_func,
        pre_processor=helper_preprocessor,
        post_processor=helper_postprocessor,
        parser=helper_parser,
    )


@pytest.fixture
def async_tool():
    """Fixture for creating an async tool."""
    return Tool(function=helper_async_func)


@pytest.mark.asyncio
async def test_function_calling_init():
    """Test FunctionCalling initialization."""
    tool = Tool(function=helper_sync_func)
    arguments = {"x": 1, "y": "test"}

    func_call = FunctionCalling(func_tool=tool, arguments=arguments)
    assert func_call.func_tool == tool
    assert func_call.arguments == arguments
    assert func_call.function == "helper_sync_func"
    assert func_call.status == EventStatus.PENDING


@pytest.mark.asyncio
async def test_function_calling_with_sync_function():
    """Test FunctionCalling with synchronous function."""
    tool = Tool(function=helper_sync_func)
    func_call = FunctionCalling(
        func_tool=tool, arguments={"x": 1, "y": "test"}
    )

    result = await func_call.invoke()
    assert result == "1-test"
    assert func_call.status == EventStatus.COMPLETED
    assert func_call.execution_time is not None
    assert func_call.execution_response == "1-test"
    assert func_call.execution_error is None


@pytest.mark.asyncio
async def test_function_calling_with_async_function(async_tool):
    """Test FunctionCalling with asynchronous function."""
    func_call = FunctionCalling(
        func_tool=async_tool, arguments={"x": 1, "y": "test"}
    )

    result = await func_call.invoke()
    assert result == "1-test"
    assert func_call.status == EventStatus.COMPLETED
    assert func_call.execution_time is not None
    assert func_call.execution_response == "1-test"
    assert func_call.execution_error is None


@pytest.mark.asyncio
async def test_function_calling_with_processors(tool_with_processors):
    """Test FunctionCalling with pre/post processors."""
    func_call = FunctionCalling(
        func_tool=tool_with_processors, arguments={"x": 1, "y": "test"}
    )

    result = await func_call.invoke()
    # Pre-processor adds 1 to x, so result should be "2-test"
    # Post-processor adds "processed-" prefix
    # Parser converts to string
    assert result == "processed-2-test"
    assert func_call.status == EventStatus.COMPLETED


@pytest.mark.asyncio
async def test_function_calling_with_parser(tool_with_processors):
    """Test FunctionCalling with result parser."""
    func_call = FunctionCalling(
        func_tool=tool_with_processors, arguments={"x": 1, "y": "test"}
    )

    result = await func_call.invoke()
    assert isinstance(result, str)
    assert func_call.status == EventStatus.COMPLETED


@pytest.mark.asyncio
async def test_function_calling_error_handling():
    """Test FunctionCalling error handling."""

    async def error_func(**kwargs):
        raise ValueError("Test error")

    tool = Tool(function=error_func)
    func_call = FunctionCalling(func_tool=tool, arguments={})

    result = await func_call.invoke()
    assert result is None
    assert func_call.status == EventStatus.FAILED
    assert "Test error" in str(func_call.execution_error)
    assert func_call.execution_time is not None


@pytest.mark.asyncio
async def test_function_calling_with_timed_config():
    """Test FunctionCalling with custom TimedFuncCallConfig."""
    tool = Tool(function=helper_sync_func)
    config = TimedFuncCallConfig(
        initial_delay=0,
        retry_default=UNDEFINED,
        retry_timeout=5,
        retry_timing=True,
    )

    func_call = FunctionCalling(
        func_tool=tool, arguments={"x": 1}, timed_config=config
    )

    assert func_call._timed_config == config
    result = await func_call.invoke()
    assert result == "1-default"
    assert func_call.status == EventStatus.COMPLETED


def test_function_calling_str_representation():
    """Test FunctionCalling string representations."""
    tool = Tool(function=helper_sync_func)
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
    tool = Tool(function=helper_sync_func)
    func_call = FunctionCalling(func_tool=tool, arguments={})

    result = await func_call.invoke()
    assert result == "0-default"  # Should use default values
    assert func_call.status == EventStatus.COMPLETED


@pytest.mark.asyncio
async def test_function_calling_processor_error():
    """Test FunctionCalling with failing processor."""

    async def error_processor(value: Any, **kwargs) -> Any:
        raise ValueError("Processor error")

    tool = Tool(function=helper_sync_func, pre_processor=error_processor)

    func_call = FunctionCalling(func_tool=tool, arguments={"x": 1})

    result = await func_call.invoke()
    assert result is None
    assert func_call.status == EventStatus.FAILED
    assert "Processor error" in str(func_call.execution_error)
