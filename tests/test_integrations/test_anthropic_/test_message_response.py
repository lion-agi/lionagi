import pytest
from pydantic import ValidationError

from lionagi.integrations.anthropic_.api_endpoints.messages.response.content_models import (
    TextContent,
    ToolResultContent,
    ToolUseContent,
)
from lionagi.integrations.anthropic_.api_endpoints.messages.response.response_body import (
    AnthropicMessageResponseBody,
)
from lionagi.integrations.anthropic_.api_endpoints.messages.response.usage_models import (
    Usage,
)


def test_text_content_validation():
    # Test valid text content
    text_content = TextContent(
        type="text",
        text="Hello! How can I help you today?",
    )
    assert text_content.type == "text"
    assert text_content.text == "Hello! How can I help you today?"

    # Test invalid type
    with pytest.raises(ValidationError):
        TextContent(type="invalid", text="Hello")

    # Test missing text
    with pytest.raises(ValidationError):
        TextContent(type="text")


def test_tool_use_content_validation():
    # Test valid tool use content
    tool_use = ToolUseContent(
        type="tool_use",
        id="tool_123",
        name="get_weather",
        input={"location": "San Francisco"},
    )
    assert tool_use.type == "tool_use"
    assert tool_use.id == "tool_123"
    assert tool_use.name == "get_weather"
    assert tool_use.input == {"location": "San Francisco"}

    # Test invalid type
    with pytest.raises(ValidationError):
        ToolUseContent(
            type="invalid",
            id="tool_123",
            name="get_weather",
            input={"location": "San Francisco"},
        )

    # Test missing required fields
    with pytest.raises(ValidationError):
        ToolUseContent(type="tool_use", name="get_weather", input={})


def test_tool_result_content_validation():
    # Test valid tool result content
    tool_result = ToolResultContent(
        type="tool_result",
        tool_use_id="tool_123",
        content="The weather in San Francisco is sunny with a high of 72°F",
    )
    assert tool_result.type == "tool_result"
    assert tool_result.tool_use_id == "tool_123"
    assert "weather in San Francisco" in tool_result.content

    # Test invalid type
    with pytest.raises(ValidationError):
        ToolResultContent(
            type="invalid",
            tool_use_id="tool_123",
            content="Result",
        )

    # Test missing required fields
    with pytest.raises(ValidationError):
        ToolResultContent(type="tool_result", content="Result")


def test_usage_validation():
    # Test valid usage with only required fields
    usage = Usage(
        input_tokens=10,
        output_tokens=20,
    )
    assert usage.input_tokens == 10
    assert usage.output_tokens == 20
    assert usage.cache_creation_input_tokens is None
    assert usage.cache_read_input_tokens is None

    # Test with all fields
    usage = Usage(
        input_tokens=10,
        output_tokens=20,
        cache_creation_input_tokens=5,
        cache_read_input_tokens=10,
    )
    assert usage.cache_creation_input_tokens == 5
    assert usage.cache_read_input_tokens == 10

    # Test missing required fields
    with pytest.raises(ValidationError):
        Usage(input_tokens=10)  # missing output_tokens

    with pytest.raises(ValidationError):
        Usage(output_tokens=20)  # missing input_tokens


def test_message_response_validation():
    # Test basic text response
    response = AnthropicMessageResponseBody(
        id="msg_123",
        type="message",
        role="assistant",
        content=[
            TextContent(type="text", text="Hello! How can I help you today?"),
        ],
        model="claude-2",
        stop_reason="end_turn",
        usage=Usage(input_tokens=5, output_tokens=10),
    )
    assert response.id == "msg_123"
    assert response.type == "message"
    assert response.role == "assistant"
    assert len(response.content) == 1
    assert response.content[0].text == "Hello! How can I help you today?"
    assert response.stop_reason == "end_turn"
    assert response.stop_sequence is None

    # Test response with tool use
    response = AnthropicMessageResponseBody(
        id="msg_124",
        type="message",
        role="assistant",
        content=[
            TextContent(type="text", text="Let me check the weather for you."),
            ToolUseContent(
                type="tool_use",
                id="tool_123",
                name="get_weather",
                input={"location": "San Francisco"},
            ),
            ToolResultContent(
                type="tool_result",
                tool_use_id="tool_123",
                content="Sunny, 72°F",
            ),
            TextContent(
                type="text",
                text="The weather in San Francisco is sunny with a temperature of 72°F.",
            ),
        ],
        model="claude-2",
        stop_reason="end_turn",
        usage=Usage(input_tokens=15, output_tokens=25),
    )
    assert len(response.content) == 4
    assert response.content[1].type == "tool_use"
    assert response.content[2].type == "tool_result"
    assert response.content[2].tool_use_id == response.content[1].id


def test_different_stop_reasons():
    # Test end_turn stop reason
    response = AnthropicMessageResponseBody(
        id="msg_123",
        type="message",
        role="assistant",
        content=[TextContent(type="text", text="Complete response")],
        model="claude-2",
        stop_reason="end_turn",
        usage=Usage(input_tokens=5, output_tokens=10),
    )
    assert response.stop_reason == "end_turn"

    # Test max_tokens stop reason
    response = AnthropicMessageResponseBody(
        id="msg_124",
        type="message",
        role="assistant",
        content=[TextContent(type="text", text="Partial response")],
        model="claude-2",
        stop_reason="max_tokens",
        usage=Usage(input_tokens=5, output_tokens=10),
    )
    assert response.stop_reason == "max_tokens"

    # Test stop_sequence stop reason
    response = AnthropicMessageResponseBody(
        id="msg_125",
        type="message",
        role="assistant",
        content=[TextContent(type="text", text="Response with stop sequence")],
        model="claude-2",
        stop_reason="stop_sequence",
        stop_sequence="\n\nHuman:",
        usage=Usage(input_tokens=5, output_tokens=10),
    )
    assert response.stop_reason == "stop_sequence"
    assert response.stop_sequence == "\n\nHuman:"

    # Test tool_use stop reason
    response = AnthropicMessageResponseBody(
        id="msg_126",
        type="message",
        role="assistant",
        content=[
            ToolUseContent(
                type="tool_use",
                id="tool_123",
                name="get_weather",
                input={"location": "San Francisco"},
            ),
        ],
        model="claude-2",
        stop_reason="tool_use",
        usage=Usage(input_tokens=5, output_tokens=10),
    )
    assert response.stop_reason == "tool_use"
