import pytest
from pydantic import ValidationError

from lionagi.integrations.openai_.api_endpoints.chat_completions.response.choice_models import (
    Choice,
    ChunkChoice,
)
from lionagi.integrations.openai_.api_endpoints.chat_completions.response.function_models import (
    Function,
    ToolCall,
)
from lionagi.integrations.openai_.api_endpoints.chat_completions.response.message_models import (
    Message,
)
from lionagi.integrations.openai_.api_endpoints.chat_completions.response.response_body import (
    OpenAIChatCompletionChunkResponseBody,
    OpenAIChatCompletionResponseBody,
)
from lionagi.integrations.openai_.api_endpoints.chat_completions.response.usage_models import (
    CompletionTokensDetails,
    Usage,
)


def test_completion_response_validation():
    # Test valid response
    valid_response = OpenAIChatCompletionResponseBody(
        id="chatcmpl-123",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=Message(
                    role="assistant",
                    content="Hello! How can I help you today?",
                ),
                logprobs=None,
            )
        ],
        created=1677858242,
        model="gpt-4",
        system_fingerprint="fp-123",
        object="chat.completion",
        usage=Usage(
            completion_tokens=10,
            prompt_tokens=5,
            total_tokens=15,
            completion_tokens_details=CompletionTokensDetails(
                reasoning_tokens=10
            ),
        ),
    )
    assert valid_response.id == "chatcmpl-123"
    assert len(valid_response.choices) == 1
    assert (
        valid_response.choices[0].message.content
        == "Hello! How can I help you today?"
    )
    assert valid_response.usage.total_tokens == 15

    # Test response with tool calls
    tool_response = OpenAIChatCompletionResponseBody(
        id="chatcmpl-124",
        choices=[
            Choice(
                finish_reason="tool_calls",
                index=0,
                message=Message(
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
                ),
                logprobs=None,
            )
        ],
        created=1677858242,
        model="gpt-4",
        system_fingerprint="fp-124",
        object="chat.completion",
        usage=Usage(
            completion_tokens=8,
            prompt_tokens=5,
            total_tokens=13,
            completion_tokens_details=CompletionTokensDetails(
                reasoning_tokens=8
            ),
        ),
    )
    assert tool_response.choices[0].finish_reason == "tool_calls"
    assert (
        tool_response.choices[0].message.tool_calls[0].function.name
        == "get_weather"
    )

    # Test response with refusal
    refusal_response = OpenAIChatCompletionResponseBody(
        id="chatcmpl-125",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=Message(
                    role="assistant",
                    content=None,
                    refusal="I cannot assist with that request.",
                ),
                logprobs=None,
            )
        ],
        created=1677858242,
        model="gpt-4",
        system_fingerprint="fp-125",
        object="chat.completion",
        usage=Usage(
            completion_tokens=8,
            prompt_tokens=5,
            total_tokens=13,
            completion_tokens_details=CompletionTokensDetails(
                reasoning_tokens=8
            ),
        ),
    )
    assert (
        refusal_response.choices[0].message.refusal
        == "I cannot assist with that request."
    )

    # Test invalid response without required fields
    with pytest.raises(ValidationError):
        OpenAIChatCompletionResponseBody(
            id="chatcmpl-123",
            choices=[],  # Empty choices
            created=1677858242,
            model="gpt-4",
            object="chat.completion",
            usage=Usage(
                completion_tokens=0,
                prompt_tokens=0,
                total_tokens=0,
                completion_tokens_details=CompletionTokensDetails(
                    reasoning_tokens=0
                ),
            ),
        )


def test_chunk_response_validation():
    # Test valid chunk response
    valid_chunk = OpenAIChatCompletionChunkResponseBody(
        id="chatcmpl-123",
        choices=[
            ChunkChoice(
                delta=Message(role="assistant", content="Hello"),
                finish_reason=None,
                index=0,
                logprobs=None,
            )
        ],
        created=1677858242,
        model="gpt-4",
        system_fingerprint="fp-123",
        object="chat.completion.chunk",
    )
    assert valid_chunk.id == "chatcmpl-123"
    assert valid_chunk.choices[0].delta.content == "Hello"

    # Test final chunk with finish reason
    final_chunk = OpenAIChatCompletionChunkResponseBody(
        id="chatcmpl-123",
        choices=[
            ChunkChoice(
                delta=Message(role="assistant", content="!"),
                finish_reason="stop",
                index=0,
                logprobs=None,
            )
        ],
        created=1677858242,
        model="gpt-4",
        system_fingerprint="fp-123",
        object="chat.completion.chunk",
        usage=Usage(
            completion_tokens=10,
            prompt_tokens=5,
            total_tokens=15,
            completion_tokens_details=CompletionTokensDetails(
                reasoning_tokens=10
            ),
        ),
    )
    assert final_chunk.choices[0].finish_reason == "stop"
    assert final_chunk.usage is not None

    # Test invalid chunk without required fields
    with pytest.raises(ValidationError):
        OpenAIChatCompletionChunkResponseBody(
            id="chatcmpl-123",
            choices=[],  # Empty choices
            created=1677858242,
            model="gpt-4",
            object="chat.completion.chunk",
        )
