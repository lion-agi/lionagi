import pytest
from pydantic import ValidationError

from lionagi.integrations.openai_.api_endpoints.api_request import (
    OpenAIRequest,
)
from lionagi.integrations.openai_.api_endpoints.audio.transcription_models import (
    OpenAITranscriptionResponseBody,
    OpenAIVerboseTranscriptionResponseBody,
)
from lionagi.integrations.openai_.api_endpoints.audio.translation_models import (
    OpenAITranslationResponseBody,
)
from lionagi.integrations.openai_.api_endpoints.chat_completions.response.response_body import (
    OpenAIChatCompletionChunkResponseBody,
    OpenAIChatCompletionResponseBody,
)
from lionagi.integrations.openai_.api_endpoints.embeddings.response_body import (
    OpenAIEmbeddingResponseBody,
)
from lionagi.integrations.openai_.api_endpoints.match_response import (
    match_response,
)


@pytest.fixture
def chat_request():
    return OpenAIRequest(
        api_key="test_key", endpoint="chat/completions", method="POST"
    )


@pytest.fixture
def embeddings_request():
    return OpenAIRequest(
        api_key="test_key", endpoint="embeddings", method="POST"
    )


@pytest.fixture
def transcription_request():
    return OpenAIRequest(
        api_key="test_key", endpoint="audio/transcriptions", method="POST"
    )


def test_match_chat_completion_response(chat_request):
    response_data = {
        "id": "chatcmpl-123",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Hello!"},
                "finish_reason": "stop",
                "logprobs": None,
            }
        ],
        "created": 1677858242,
        "model": "gpt-4",
        "system_fingerprint": "fp-123",
        "object": "chat.completion",
        "usage": {
            "prompt_tokens": 5,
            "completion_tokens": 1,
            "total_tokens": 6,
            "completion_tokens_details": {"reasoning_tokens": 1},
        },
    }

    result = match_response(chat_request, response_data)
    assert isinstance(result, OpenAIChatCompletionResponseBody)
    assert result.id == "chatcmpl-123"
    assert result.choices[0].message.content == "Hello!"
    assert result.usage.total_tokens == 6


def test_match_chat_completion_stream(chat_request):
    stream_data = [
        {
            "id": "chatcmpl-123",
            "choices": [
                {
                    "delta": {"role": "assistant", "content": "Hello"},
                    "index": 0,
                    "finish_reason": None,
                    "logprobs": None,
                }
            ],
            "created": 1677858242,
            "model": "gpt-4",
            "system_fingerprint": "fp-123",
            "object": "chat.completion.chunk",
        },
        {
            "id": "chatcmpl-123",
            "choices": [
                {
                    "delta": {"content": "!"},
                    "index": 0,
                    "finish_reason": "stop",
                    "logprobs": None,
                }
            ],
            "created": 1677858242,
            "model": "gpt-4",
            "system_fingerprint": "fp-123",
            "object": "chat.completion.chunk",
        },
    ]

    result = match_response(chat_request, stream_data)
    assert isinstance(result, list)
    assert all(
        isinstance(chunk, OpenAIChatCompletionChunkResponseBody)
        for chunk in result
    )
    assert result[0].choices[0].delta.content == "Hello"
    assert result[1].choices[0].delta.content == "!"


def test_match_embeddings_response(embeddings_request):
    response_data = {
        "object": "list",
        "data": [
            {"object": "embedding", "embedding": [0.1, 0.2, 0.3], "index": 0}
        ],
        "model": "text-embedding-ada-002",
        "usage": {"prompt_tokens": 5, "total_tokens": 5},
    }

    result = match_response(embeddings_request, response_data)
    assert isinstance(result, OpenAIEmbeddingResponseBody)
    assert len(result.data) == 1
    assert result.data[0].embedding == [0.1, 0.2, 0.3]
    assert result.usage.total_tokens == 5


def test_match_transcription_response(transcription_request):
    # Test basic transcription
    basic_response = {"text": "Hello, world!"}
    result = match_response(transcription_request, basic_response)
    assert isinstance(result, OpenAITranscriptionResponseBody)
    assert result.text == "Hello, world!"

    # Test verbose transcription
    verbose_response = {
        "task": "transcribe",
        "language": "en",
        "duration": 1.5,
        "text": "Hello, world!",
        "segments": [
            {
                "id": 0,
                "seek": 0,
                "start": 0.0,
                "end": 1.5,
                "text": "Hello, world!",
                "tokens": [1, 2, 3],
                "temperature": 0.0,
                "avg_logprob": -0.5,
                "compression_ratio": 1.0,
                "no_speech_prob": 0.1,
            }
        ],
    }
    result = match_response(transcription_request, verbose_response)
    assert isinstance(result, OpenAIVerboseTranscriptionResponseBody)
    assert result.text == "Hello, world!"
    assert len(result.segments) == 1
    assert result.duration == 1.5


def test_match_translation_response(transcription_request):
    transcription_request.endpoint = (
        "audio/translations"  # Change endpoint for translation
    )

    response_data = {"text": "Bonjour le monde!"}

    result = match_response(transcription_request, response_data)
    assert isinstance(result, OpenAITranslationResponseBody)
    assert result.text == "Bonjour le monde!"


def test_match_invalid_response(chat_request):
    # Test with invalid endpoint
    chat_request.endpoint = "invalid/endpoint"
    with pytest.raises(ValueError, match="no standard response model"):
        match_response(chat_request, {})

    # Test with invalid response data
    chat_request.endpoint = "chat/completions"
    with pytest.raises(ValidationError):
        match_response(chat_request, {"invalid": "data"})
