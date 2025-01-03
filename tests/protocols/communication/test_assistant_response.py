from pydantic import BaseModel

from lionagi.protocols.types import AssistantResponse, MessageRole


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
    response = AssistantResponse.create(
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

    response = AssistantResponse.create(
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

    response = AssistantResponse.create(
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
    response = AssistantResponse.create(
        assistant_response=content, sender="assistant", recipient="user"
    )

    assert response.response == content["content"]


def test_assistant_response_empty():
    """Test AssistantResponse with empty response"""
    response = AssistantResponse.create(
        assistant_response="", sender="assistant", recipient="user"
    )

    assert response.response == ""


def test_assistant_response_content_format():
    """Test the format of assistant response content"""
    content = "Test content"
    response = AssistantResponse.create(
        assistant_response=content, sender="assistant", recipient="user"
    )

    formatted = response.chat_msg
    assert formatted["role"] == MessageRole.ASSISTANT.value
    assert content in formatted["content"]


def test_prepare_assistant_response():
    """Test prepare_assistant_response utility function"""
    from lionagi.protocols.messages.assistant_response import (
        prepare_assistant_response,
    )

    # Test with string
    content = "Test response"
    result = prepare_assistant_response(content)
    assert isinstance(result, dict)
    assert result["assistant_response"] == content

    # Test with model response
    model_response = create_mock_response("Model response")
    result = prepare_assistant_response(model_response)
    assert result["assistant_response"] == "Model response"
    assert "model_response" in result

    # Test with stream response
    stream_content = "Stream"
    stream_responses = create_mock_stream_response(stream_content)
    result = prepare_assistant_response(stream_responses)
    assert result["assistant_response"] == stream_content
    assert isinstance(result["model_response"], list)


def test_assistant_response_clone():
    """Test cloning an AssistantResponse"""
    original = AssistantResponse.create(
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
    response = AssistantResponse.create(
        assistant_response="Test response",
        sender="assistant",
        recipient="user",
    )

    str_repr = str(response)
    assert "Message" in str_repr
    assert "role=assistant" in str_repr
    assert "Test response" in str_repr
