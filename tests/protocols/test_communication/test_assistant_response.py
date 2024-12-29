import pytest
from pydantic import BaseModel

from lionagi.protocols.messages.assistant_response import (
    AssistantResponse,
    MessageRole,
)


class Message(BaseModel):
    """Mock message for model response"""

    content: str | None = None


class Delta(BaseModel):
    """Mock delta for streaming response"""

    content: str | None = None


class Choice(BaseModel):
    """Mock choice for model response"""

    message: Message | None = None
    delta: Delta | None = None


class MockModelResponse(BaseModel):
    """Mock response from an AI model"""

    choices: list[Choice]
    model: str = "test-model"


def create_mock_response(content: str) -> MockModelResponse:
    """Create a mock model response with given content"""
    return MockModelResponse(
        choices=[Choice(message=Message(content=content))]
    )


def create_mock_stream_response(content: str) -> list[MockModelResponse]:
    """Create a mock streaming model response"""
    return [
        MockModelResponse(choices=[Choice(delta=Delta(content=char))])
        for char in content
    ]


def test_assistant_response_initialization():
    """Test basic initialization of AssistantResponse"""
    content = "Test response"
    response = AssistantResponse(
        assistant_response=content, sender="assistant", recipient="user"
    )

    assert response.role == MessageRole.ASSISTANT
    assert response.response == content
    assert response.sender == "assistant"
    assert response.recipient == "user"


def test_assistant_response_with_model_response():
    """Test AssistantResponse with a model response object"""
    content = "Model generated response"
    model_response = create_mock_response(content)

    response = AssistantResponse(
        assistant_response=model_response, sender="assistant", recipient="user"
    )

    assert response.response == content
    assert response.model_response == model_response.model_dump(
        exclude_none=True, exclude_unset=True
    )


def test_assistant_response_with_streaming():
    """Test AssistantResponse with streaming response"""
    content = "Stream response"
    stream_responses = create_mock_stream_response(content)

    response = AssistantResponse(
        assistant_response=stream_responses,
        sender="assistant",
        recipient="user",
    )

    assert response.response == content
    assert isinstance(response.model_response, list)
    assert len(response.model_response) == len(content)


def test_assistant_response_with_dict():
    """Test AssistantResponse with dictionary input"""
    content = {"content": "Dictionary response"}
    response = AssistantResponse(
        assistant_response=content, sender="assistant", recipient="user"
    )

    assert response.response == content["content"]


def test_assistant_response_empty():
    """Test AssistantResponse with empty response"""
    response = AssistantResponse(
        assistant_response="", sender="assistant", recipient="user"
    )

    assert response.response == ""


def test_assistant_response_content_format():
    """Test the format of assistant response content"""
    content = "Test content"
    response = AssistantResponse(
        assistant_response=content, sender="assistant", recipient="user"
    )

    formatted = response._format_content()
    assert formatted["role"] == MessageRole.ASSISTANT.value
    assert formatted["content"] == content


def test_assistant_response_clone():
    """Test cloning an AssistantResponse"""
    original = AssistantResponse(
        assistant_response="Test response",
        sender="assistant",
        recipient="user",
    )

    cloned = original.clone()

    assert cloned.role == original.role
    assert cloned.response == original.response
    assert cloned.content == original.content
    assert cloned.metadata["clone_from"] == original


def test_assistant_response_str_representation():
    """Test string representation of AssistantResponse"""
    response = AssistantResponse(
        assistant_response="Test response",
        sender="assistant",
        recipient="user",
    )

    str_repr = str(response)
    assert "Message" in str_repr
    assert "role=MessageRole.ASSISTANT" in str_repr
    assert "Test response" in str_repr
