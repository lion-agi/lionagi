import pytest

from lionagi.protocols.action.function_calling import FunctionCalling
from lionagi.protocols.action.manager import ActionManager
from lionagi.protocols.action.request_response_model import ActionRequestModel
from lionagi.protocols.action.tool import Tool
from lionagi.protocols.generic.event import Execution
from lionagi.protocols.messages.action_request import ActionRequest


# Helper functions for testing
async def helper_func(x: int = 0, y: str = "default") -> str:
    """Test function."""
    return f"{x}-{y}"


def another_helper_func(x: int = 0) -> int:
    """Another test function."""
    return x + 1


@pytest.fixture
def action_manager():
    """Fixture for creating an ActionManager instance."""
    return ActionManager()


@pytest.fixture
def populated_manager():
    """Fixture for creating an ActionManager with pre-registered tools."""
    manager = ActionManager()
    manager.register_tools([helper_func, another_helper_func])
    return manager


def test_action_manager_init():
    """Test ActionManager initialization."""
    manager = ActionManager()
    assert isinstance(manager.registry, dict)
    assert len(manager.registry) == 0

    # Test with pre-registered tools
    tool = Tool(func_callable=helper_func)
    manager = ActionManager(registry={"helper_func": tool})
    assert len(manager.registry) == 1
    assert "helper_func" in manager.registry


def test_tool_registration(action_manager):
    """Test tool registration functionality."""
    # Test registering a callable
    action_manager.register_tool(helper_func)
    assert helper_func.__name__ in action_manager.registry

    # Test registering a Tool object
    tool = Tool(func_callable=another_helper_func)
    action_manager.register_tool(tool)
    assert tool.function in action_manager.registry

    # Test duplicate registration
    with pytest.raises(ValueError):
        action_manager.register_tool(helper_func)

    # Test update existing tool
    action_manager.register_tool(helper_func, update=True)
    assert helper_func.__name__ in action_manager.registry


def test_tool_registration_validation(action_manager):
    """Test tool registration validation."""
    # Test invalid tool type
    with pytest.raises(TypeError):
        action_manager.register_tool("not_a_tool")

    # Test registering multiple tools
    tools = [helper_func, another_helper_func]
    action_manager.register_tools(tools)
    assert all(func.__name__ in action_manager.registry for func in tools)


def test_contains_check(populated_manager):
    """Test tool existence checking."""
    # Test with function name
    assert "helper_func" in populated_manager

    # Test with callable
    assert helper_func in populated_manager

    # Test with Tool object
    tool = populated_manager.registry["helper_func"]
    assert tool in populated_manager

    # Test non-existent tool
    assert "non_existent" not in populated_manager


@pytest.mark.asyncio
async def test_match_tool_action_request(populated_manager):
    """Test matching tool from ActionRequest."""
    # Test with ActionRequest
    request = ActionRequest.create(function="helper_func", arguments={"x": 1})
    result = populated_manager.match_tool(request)
    assert isinstance(result, FunctionCalling)
    assert result.function == "helper_func"

    # Test with ActionRequestModel
    model = ActionRequestModel(function="helper_func", arguments={"x": 1})
    result = populated_manager.match_tool(model)
    assert isinstance(result, FunctionCalling)
    assert result.function == "helper_func"

    # Test invalid function name
    with pytest.raises(ValueError):
        populated_manager.match_tool(
            ActionRequest.create(function="invalid_func", arguments={})
        )


def test_schema_list(populated_manager):
    """Test retrieving tool schemas."""
    schemas = populated_manager.schema_list
    assert isinstance(schemas, list)
    assert len(schemas) == 2
    assert all("function" in schema for schema in schemas)


def test_get_tool_schema(populated_manager):
    """Test retrieving specific tool schemas."""
    # Test with boolean=True (all tools)
    result = populated_manager.get_tool_schema(True)
    assert "tools" in result
    assert len(result["tools"]) == 2

    # Test with boolean=False (no tools)
    result = populated_manager.get_tool_schema(False)
    assert "tools" not in result

    # Test with specific tool
    result = populated_manager.get_tool_schema("helper_func")
    assert "tools" in result
    assert isinstance(result["tools"], dict)
    assert result["tools"]["function"]["name"] == "helper_func"

    # Test with list of tools
    result = populated_manager.get_tool_schema(
        ["helper_func", "another_helper_func"]
    )
    assert "tools" in result
    assert isinstance(result["tools"], list)
    assert len(result["tools"]) == 2

    # Test with invalid tool
    with pytest.raises(ValueError):
        populated_manager.get_tool_schema("invalid_func")

    # Test with invalid type
    with pytest.raises(TypeError):
        populated_manager.get_tool_schema(123)
