import pytest

from lionagi.messages.types import ActionRequest
from lionagi.protocols.types import MessageRole, Note


def test_action_request_initialization():
    """Test basic initialization of ActionRequest"""
    function = "test_function"
    arguments = {"arg1": "value1", "arg2": "value2"}

    request = ActionRequest(
        function=function,
        arguments=arguments,
        sender="user",  # Using valid system role
        recipient="assistant",  # Using valid system role
    )

    assert request.role == MessageRole.ASSISTANT
    assert request.function == function
    assert request.arguments == arguments
    assert request.sender == "user"
    assert request.recipient == "assistant"
    assert not request.is_responded


def test_action_request_with_callable():
    """Test ActionRequest initialization with a callable function"""

    def test_func():
        pass

    arguments = {"arg1": "value1"}
    request = ActionRequest(function=test_func, arguments=arguments)

    assert request.function == "test_func"
    assert request.arguments == arguments


def test_action_request_invalid_arguments():
    """Test ActionRequest initialization with invalid arguments"""
    with pytest.raises(ValueError, match="Arguments must be a dictionary."):
        ActionRequest(function="test", arguments="invalid")


def test_action_request_response_tracking():
    """Test tracking of action response"""
    request = ActionRequest(
        function="test", arguments={}, sender="user", recipient="assistant"
    )
    assert request.action_response_id is None
    assert not request.is_responded

    # Simulate setting response ID
    request.content["action_response_id"] = "test_response_id"
    assert request.action_response_id == "test_response_id"
    assert request.is_responded


def test_action_request_content_format():
    """Test the format of action request content"""
    function = "test_function"
    arguments = {"arg1": "value1"}
    request = ActionRequest(
        function=function,
        arguments=arguments,
        sender="user",
        recipient="assistant",
    )

    formatted = request._format_content()
    assert formatted["role"] == MessageRole.ASSISTANT.value
    assert isinstance(formatted["content"], dict)
    assert formatted["content"]["function"] == function
    assert formatted["content"]["arguments"] == arguments


def test_action_request_request_property():
    """Test the request property of ActionRequest"""
    function = "test_function"
    arguments = {"arg1": "value1"}
    request = ActionRequest(
        function=function,
        arguments=arguments,
        sender="user",
        recipient="assistant",
    )

    request_dict = request.request
    assert request_dict["function"] == function
    assert request_dict["arguments"] == arguments
    assert (
        "output" not in request_dict
    )  # Should not include output in request dict


def test_prepare_action_request():
    """Test prepare_action_request utility function"""
    from lionagi.messages.action_request import prepare_action_request

    function = "test_function"
    arguments = {"arg1": "value1"}

    result = prepare_action_request(function, arguments)
    assert isinstance(result, Note)
    assert result["action_request"]["function"] == function
    assert result["action_request"]["arguments"] == arguments


def test_action_request_clone():
    """Test cloning an ActionRequest"""
    original = ActionRequest(
        function="test_function",
        arguments={"arg1": "value1"},
        sender="user",
        recipient="assistant",
    )

    cloned = original.clone()

    assert cloned.role == original.role
    assert cloned.function == original.function
    assert cloned.arguments == original.arguments
    assert cloned.content == original.content
    assert cloned.metadata["clone_from"] == original


def test_action_request_str_representation():
    """Test string representation of ActionRequest"""
    request = ActionRequest(
        function="test_function",
        arguments={"arg1": "value1"},
        sender="user",
        recipient="assistant",
    )

    str_repr = str(request)
    assert "Message" in str_repr
    assert "role=MessageRole.ASSISTANT" in str_repr
    assert "test_function" in str_repr
