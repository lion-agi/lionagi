import pytest
from pydantic import ValidationError

from lionagi.integrations.openai_.api_endpoints.chat_completions.request.message_models import (
    AssistantMessage,
    Function,
    Message,
    SystemMessage,
    ToolCall,
    ToolMessage,
    UserMessage,
)


def test_message_validation():
    # Test valid system message
    system_msg = SystemMessage(
        role="system", content="You are a helpful assistant"
    )
    assert system_msg.role == "system"
    assert system_msg.content == "You are a helpful assistant"

    # Test valid user message
    user_msg = UserMessage(role="user", content="Hello")
    assert user_msg.role == "user"
    assert user_msg.content == "Hello"

    # Test valid assistant message
    assistant_msg = AssistantMessage(
        role="assistant", content="Hello! How can I help?"
    )
    assert assistant_msg.role == "assistant"
    assert assistant_msg.content == "Hello! How can I help?"

    # Test assistant message with tool calls
    tool_msg = AssistantMessage(
        role="assistant",
        content=None,
        tool_calls=[
            ToolCall(
                id="call_1",
                type="function",
                function=Function(
                    name="get_weather",
                    arguments='{"location": "San Francisco"}',
                ),
            )
        ],
    )
    assert tool_msg.role == "assistant"
    assert tool_msg.tool_calls[0].function.name == "get_weather"

    # Test tool message
    tool_response = ToolMessage(
        role="tool", content="The weather is sunny", tool_calls_id="call_1"
    )
    assert tool_response.role == "tool"
    assert tool_response.content == "The weather is sunny"
    assert tool_response.tool_calls_id == "call_1"

    # Test invalid role
    with pytest.raises(ValidationError):
        UserMessage(role="invalid", content="Hello")

    # Test missing content in assistant message
    with pytest.raises(ValidationError):
        AssistantMessage(role="assistant")
