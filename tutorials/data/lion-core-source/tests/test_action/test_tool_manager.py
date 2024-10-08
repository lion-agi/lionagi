import pytest

from lion_core.action.function_calling import FunctionCalling
from lion_core.action.tool import Tool, func_to_tool
from lion_core.action.tool_manager import ToolManager


# Mock functions for testing
def mock_function(x: int, y: int) -> int:
    return x + y


async def async_mock_function(x: int, y: int) -> int:
    return x + y


# Fixtures
@pytest.fixture
def tool_manager():
    return ToolManager()


@pytest.fixture
def sample_tool():
    return Tool(function=mock_function)


@pytest.fixture
def sample_async_tool():
    return Tool(function=async_mock_function)


# Test initialization
def test_init():
    tm = ToolManager()
    assert isinstance(tm.registry, dict)
    assert len(tm.registry) == 0


# Test __contains__
def test_contains(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    assert sample_tool in tool_manager
    assert "mock_function" in tool_manager
    assert mock_function in tool_manager
    assert "non_existent_tool" not in tool_manager


# Test register_tool
def test_register_tool(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    assert "mock_function" in tool_manager.registry

    with pytest.raises(ValueError):
        tool_manager.register_tool(sample_tool)

    tool_manager.register_tool(sample_tool, update=True)
    assert tool_manager.registry["mock_function"] == sample_tool


def test_register_callable(tool_manager):
    tool_manager.register_tool(mock_function)
    assert "mock_function" in tool_manager.registry
    assert isinstance(tool_manager.registry["mock_function"], Tool)


def test_register_invalid_tool(tool_manager):
    with pytest.raises(TypeError):
        tool_manager.register_tool("not_a_tool")


# Test match_tool
def test_match_tool_tuple(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    func_call = ("mock_function", {"x": 1, "y": 2})
    result = tool_manager.match_tool(func_call)
    assert isinstance(result, FunctionCalling)
    assert result.func_tool == sample_tool
    assert result.arguments == {"x": 1, "y": 2}


def test_match_tool_dict(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    func_call = {"function": "mock_function", "arguments": {"x": 1, "y": 2}}
    result = tool_manager.match_tool(func_call)
    assert isinstance(result, FunctionCalling)
    assert result.func_tool == sample_tool
    assert result.arguments == {"x": 1, "y": 2}


def test_match_tool_str(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    func_call = '{"function": "mock_function", "arguments": {"x": 1, "y": 2}}'
    result = tool_manager.match_tool(func_call)
    assert isinstance(result, FunctionCalling)
    assert result.func_tool == sample_tool
    assert result.arguments == {"x": 1, "y": 2}


def test_match_tool_invalid(tool_manager):
    with pytest.raises(TypeError):
        tool_manager.match_tool(123)

    with pytest.raises(ValueError):
        tool_manager.match_tool(("non_existent_function", {}))

    with pytest.raises(ValueError):
        tool_manager.match_tool({"invalid": "format"})

    with pytest.raises(ValueError):
        tool_manager.match_tool("invalid_json_string")


# Test invoke
@pytest.mark.asyncio
async def test_invoke(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    result = await tool_manager.invoke(("mock_function", {"x": 1, "y": 2}))
    assert result == 3


@pytest.mark.asyncio
async def test_invoke_async(tool_manager, sample_async_tool):
    tool_manager.register_tool(sample_async_tool)
    result = await tool_manager.invoke(
        ("async_mock_function", {"x": 1, "y": 2})
    )
    assert result == 3


# Edge cases and additional tests
def test_empty_tool_manager(tool_manager):
    assert len(tool_manager.registry) == 0
    assert tool_manager.schema_list == []
    with pytest.raises(ValueError):
        tool_manager.match_tool(("any_function", {}))


def test_register_tool_with_same_name(tool_manager):
    def func1():
        pass

    def func2():
        pass

    tool1 = func_to_tool(func1)[0]
    tool2 = func_to_tool(func2)[0]

    tool_manager.register_tool(tool1)
    tool_manager.register_tool(tool2)  # This should update the existing tool
    assert tool_manager.registry[tool2.function_name] == tool2


def test_match_tool_with_extra_args(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    func_call = ("mock_function", {"x": 1, "y": 2, "z": 3})
    result = tool_manager.match_tool(func_call)
    assert result.arguments == {"x": 1, "y": 2, "z": 3}


def test_get_tool_schema_with_additional_kwargs(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    result = tool_manager.get_tool_schema(sample_tool, extra_param="test")
    assert "tools" in result
    assert isinstance(result["tools"], dict)
    assert result["extra_param"] == "test"


print("All tests for ToolManager completed successfully!")
