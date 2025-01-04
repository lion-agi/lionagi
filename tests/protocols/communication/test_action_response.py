import pytest

from lionagi.protocols.types import ActionRequest, ActionResponse, MessageRole


def test_action_response_initialization():
    """Test basic initialization of ActionResponse"""
    action_request = ActionRequest.create(
        function="test_function",
        arguments={"arg1": "value1"},
        sender="user",
        recipient="assistant",
    )
    output = {"result": "success"}

    response = ActionResponse.create(
        action_request=action_request, output=output
    )

    assert response.role == MessageRole.ACTION
    assert response.function == action_request.function
    assert response.arguments == action_request.arguments
    assert response.output == output
    assert response.sender == action_request.recipient
    assert response.recipient == action_request.sender
    assert response.action_request_id == action_request.id


def test_action_response_links_to_request():
    """Test that ActionResponse properly links to its ActionRequest"""
    action_request = ActionRequest.create(
        function="test", arguments={}, sender="user", recipient="assistant"
    )
    response = ActionResponse.create(action_request=action_request)

    assert action_request.is_responded
    assert action_request.action_response_id == response.id


def test_action_response_content_format():
    """Test the format of action response content"""
    action_request = ActionRequest.create(
        function="test",
        arguments={"arg": "value"},
        sender="user",
        recipient="assistant",
    )
    output = {"status": "complete"}
    response = ActionResponse.create(
        action_request=action_request, output=output
    )

    formatted = response.chat_msg
    assert formatted["role"] == MessageRole.ACTION.value
    assert isinstance(formatted["content"], str)


def test_action_response_properties():
    """Test various properties of ActionResponse"""
    action_request = ActionRequest.create(
        function="test_function",
        arguments={"param": "value"},
        sender="user",
        recipient="assistant",
    )
    output = {"status": "success"}
    response = ActionResponse.create(
        action_request=action_request, output=output
    )

    assert response.function == "test_function"
    assert response.arguments == {"param": "value"}
    assert response.output == output
    assert isinstance(response.response, dict)
    assert "function" in response.response
    assert "arguments" in response.response
    assert "output" in response.response


def test_prepare_action_response_content():
    """Test prepare_action_response_content utility function"""
    from lionagi.protocols.messages.action_response import (
        prepare_action_response_content,
    )

    action_request = ActionRequest.create(
        function="test",
        arguments={"arg": "value"},
        sender="user",
        recipient="assistant",
    )
    output = {"result": "success"}

    content = prepare_action_response_content(action_request, output)
    assert isinstance(content, dict)
    assert content["action_request_id"] == str(action_request.id)
    assert content["action_response"]["function"] == action_request.function
    assert content["action_response"]["arguments"] == action_request.arguments
    assert content["action_response"]["output"] == output


def test_action_response_clone():
    """Test cloning an ActionResponse"""
    action_request = ActionRequest.create(
        function="test", arguments={}, sender="user", recipient="assistant"
    )
    original = ActionResponse.create(
        action_request=action_request, output={"status": "success"}
    )

    cloned = original.clone()

    assert cloned.role == original.role
    assert cloned.function == original.function
    assert cloned.arguments == original.arguments
    assert cloned.output == original.output
    assert cloned.content == original.content
    assert cloned.metadata["clone_from"] == original


def test_action_response_str_representation():
    """Test string representation of ActionResponse"""
    action_request = ActionRequest.create(
        function="test_function",
        arguments={},
        sender="user",
        recipient="assistant",
    )
    response = ActionResponse.create(
        action_request=action_request, output={"status": "complete"}
    )

    str_repr = str(response)
    assert "Message" in str_repr
    assert "role=action" in str_repr
    assert "action_request_id" in str_repr
