import pytest
from pydantic import ValidationError

from lionagi.integrations.anthropic_.api_endpoints.messages.request.message_models import (
    Message,
)
from lionagi.integrations.anthropic_.api_endpoints.messages.request.request_body import (
    AnthropicMessageRequestBody,
)


def test_message_validation():
    # Test valid user message
    user_msg = Message(role="user", content="Hello")
    assert user_msg.role == "user"
    assert user_msg.content == "Hello"

    # Test valid assistant message
    assistant_msg = Message(role="assistant", content="Hello! How can I help?")
    assert assistant_msg.role == "assistant"
    assert assistant_msg.content == "Hello! How can I help?"

    # Test invalid role
    with pytest.raises(ValidationError):
        Message(role="invalid", content="Hello")

    # Test missing content
    with pytest.raises(ValidationError):
        Message(role="user")


def test_request_body_validation():
    # Test basic request
    request = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[
            Message(role="user", content="Hello"),
        ],
    )
    assert request.model == "claude-2"
    assert len(request.messages) == 1
    assert request.messages[0].content == "Hello"
    assert request.stream is False  # default value

    # Test with all optional parameters
    request = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[
            Message(role="user", content="Hi"),
            Message(role="assistant", content="Hello!"),
            Message(role="user", content="What's the weather?"),
        ],
        max_tokens=100,
        metadata={"user_id": "123"},
        stop_sequences=["\n\nHuman:", "\n\nAssistant:"],
        stream=True,
        system="You are a helpful weather assistant.",
        temperature=0.7,
        top_k=10,
        top_p=0.9,
    )
    assert len(request.messages) == 3
    assert request.max_tokens == 100
    assert request.metadata == {"user_id": "123"}
    assert len(request.stop_sequences) == 2
    assert request.stream is True
    assert request.system == "You are a helpful weather assistant."
    assert request.temperature == 0.7
    assert request.top_k == 10
    assert request.top_p == 0.9


def test_parameter_constraints():
    # Test temperature range
    with pytest.raises(ValidationError):
        AnthropicMessageRequestBody(
            model="claude-2",
            messages=[Message(role="user", content="Hi")],
            temperature=-0.1,
        )

    with pytest.raises(ValidationError):
        AnthropicMessageRequestBody(
            model="claude-2",
            messages=[Message(role="user", content="Hi")],
            temperature=1.1,
        )

    # Test top_p range
    with pytest.raises(ValidationError):
        AnthropicMessageRequestBody(
            model="claude-2",
            messages=[Message(role="user", content="Hi")],
            top_p=-0.1,
        )

    with pytest.raises(ValidationError):
        AnthropicMessageRequestBody(
            model="claude-2",
            messages=[Message(role="user", content="Hi")],
            top_p=1.1,
        )


def test_conversation_flow():
    # Test a typical conversation flow
    request = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[
            Message(role="user", content="What's the weather like?"),
            Message(
                role="assistant",
                content="I don't have access to current weather data. Would you like me to help you find a weather service?",
            ),
            Message(role="user", content="Yes, please."),
        ],
        system="You are a helpful assistant focused on weather-related queries.",
    )
    assert len(request.messages) == 3
    assert request.system is not None
    assert "weather" in request.system.lower()


def test_streaming_configuration():
    # Test explicit streaming settings
    request = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[Message(role="user", content="Hi")],
        stream=True,
    )
    assert request.stream is True

    request = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[Message(role="user", content="Hi")],
        stream=False,
    )
    assert request.stream is False

    # Test default streaming setting
    request = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[Message(role="user", content="Hi")],
    )
    assert request.stream is False


def test_system_prompt():
    # Test system prompt with various content
    request = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[Message(role="user", content="Hi")],
        system="You are a helpful assistant.",
    )
    assert request.system == "You are a helpful assistant."

    # Test multiline system prompt
    multiline_system = """You are a helpful assistant.
    Please be concise in your responses.
    Always be polite and professional."""
    request = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[Message(role="user", content="Hi")],
        system=multiline_system,
    )
    assert request.system == multiline_system

    # Test empty system prompt
    request = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[Message(role="user", content="Hi")],
        system="",
    )
    assert request.system == ""


def test_message_order():
    # Test alternating user/assistant messages
    request = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[
            Message(role="user", content="Hi"),
            Message(role="assistant", content="Hello!"),
            Message(role="user", content="How are you?"),
            Message(role="assistant", content="I'm doing well, thank you!"),
        ],
    )
    assert len(request.messages) == 4
    assert [msg.role for msg in request.messages] == [
        "user",
        "assistant",
        "user",
        "assistant",
    ]

    # Test consecutive messages of same role
    with pytest.raises(ValidationError):
        AnthropicMessageRequestBody(
            model="claude-2",
            messages=[
                Message(role="user", content="Hi"),
                Message(
                    role="user", content="Hello again"
                ),  # Should not allow consecutive user messages
            ],
        )
