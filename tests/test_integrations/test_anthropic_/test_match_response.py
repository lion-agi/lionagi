import pytest
from pydantic import ValidationError

from lionagi.integrations.anthropic_.api_endpoints.api_request import (
    AnthropicRequest,
)
from lionagi.integrations.anthropic_.api_endpoints.match_response import (
    match_response,
)


@pytest.fixture
def messages_request():
    return AnthropicRequest(
        api_key="test_key",
        endpoint="messages",
        method="POST",
        content_type="application/json",
    )


def test_match_single_message_response(messages_request):
    response_data = {
        "id": "msg_123",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "Hello! How can I help you today?",
            }
        ],
        "model": "claude-2",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": 5,
            "output_tokens": 10,
            "cache_creation_input_tokens": None,
            "cache_read_input_tokens": None,
        },
    }

    result = match_response(messages_request, response_data)
    assert isinstance(result, dict)
    assert "choices" in result
    assert len(result["choices"]) == 1
    assert (
        result["choices"][0]["message"]["content"]
        == "Hello! How can I help you today?"
    )
    assert result["choices"][0]["message"]["role"] == "assistant"
    assert result["model"] == "claude-2"
    assert result["usage"]["input_tokens"] == 5
    assert result["usage"]["output_tokens"] == 10


def test_match_stream_response(messages_request):
    stream_data = [
        {
            "type": "message_start",
            "message": {
                "id": "msg_123",
                "type": "message",
                "role": "assistant",
                "model": "claude-3-sonnet",
                "content": [],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 49, "output_tokens": 4},
            },
        },
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {"type": "text", "text": ""},
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "Hello"},
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": " world"},
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "!"},
        },
        {
            "type": "message_delta",
            "delta": {"stop_reason": "end_turn", "stop_sequence": None},
            "usage": {"output_tokens": 10},
        },
        {"type": "message_stop"},
    ]

    result = match_response(messages_request, stream_data)
    assert isinstance(result, list)

    # Check content deltas
    content_deltas = [
        r
        for r in result
        if "choices" in r and r["choices"][0]["delta"].get("content")
    ]
    assert len(content_deltas) == 3
    assert content_deltas[0]["choices"][0]["delta"]["content"] == "Hello"
    assert content_deltas[1]["choices"][0]["delta"]["content"] == " world"
    assert content_deltas[2]["choices"][0]["delta"]["content"] == "!"

    # Check final message with stop
    final_message = result[-1]
    assert "choices" in final_message
    assert final_message["choices"][0]["delta"]["content"] == ""
    assert final_message["choices"][0]["finish_reason"] == "stop"


def test_match_stream_response_with_usage_updates(messages_request):
    stream_data = [
        {
            "type": "message_start",
            "message": {
                "id": "msg_123",
                "type": "message",
                "role": "assistant",
                "model": "claude-3-sonnet",
                "content": [],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 49, "output_tokens": 4},
            },
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "Hello"},
        },
        {
            "type": "message_delta",
            "delta": {"stop_reason": None, "stop_sequence": None},
            "usage": {"output_tokens": 5},
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "!"},
        },
        {
            "type": "message_delta",
            "delta": {"stop_reason": "end_turn", "stop_sequence": None},
            "usage": {"output_tokens": 10},
        },
        {"type": "message_stop"},
    ]

    result = match_response(messages_request, stream_data)
    assert isinstance(result, list)

    # Check content deltas
    content_deltas = [
        r
        for r in result
        if "choices" in r and r["choices"][0]["delta"].get("content")
    ]
    assert len(content_deltas) == 2
    assert content_deltas[0]["choices"][0]["delta"]["content"] == "Hello"
    assert content_deltas[1]["choices"][0]["delta"]["content"] == "!"

    # Check usage updates
    usage_updates = [r for r in result if "usage" in r]
    assert len(usage_updates) >= 2
    assert usage_updates[-2]["usage"]["output_tokens"] == 10

    # Check final message
    final_message = result[-1]
    assert "choices" in final_message
    assert final_message["choices"][0]["delta"]["content"] == ""
    assert final_message["choices"][0]["finish_reason"] == "stop"


def test_match_invalid_endpoint(messages_request):
    messages_request.endpoint = "invalid"
    with pytest.raises(
        ValueError, match="There is no standard response model"
    ):
        match_response(messages_request, {})
