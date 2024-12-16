import pytest
from pydantic import ValidationError

from lionagi.integrations.perplexity_.api_endpoints.chat_completions.request.request_body import (
    Message,
    PerplexityChatCompletionRequestBody,
)


def test_message_validation():
    # Test valid messages
    message = Message(role="user", content="Hello")
    assert message.role == "user"
    assert message.content == "Hello"

    message = Message(role="assistant", content="Hi there!")
    assert message.role == "assistant"
    assert message.content == "Hi there!"

    message = Message(role="system", content="You are a helpful assistant")
    assert message.role == "system"
    assert message.content == "You are a helpful assistant"

    # Test invalid role
    with pytest.raises(ValidationError):
        Message(role="invalid", content="Hello")

    # Test empty content
    with pytest.raises(ValidationError):
        Message(role="user", content="")

    # Test missing content
    with pytest.raises(ValidationError):
        Message(role="user")

    # Test missing role
    with pytest.raises(ValidationError):
        Message(content="Hello")


def test_chat_completion_request_validation():
    # Test minimal valid request
    request = PerplexityChatCompletionRequestBody(
        model="llama-3.1-sonar-small-128k-online",
        messages=[Message(role="user", content="Hello")],
    )
    assert request.model == "llama-3.1-sonar-small-128k-online"
    assert len(request.messages) == 1
    assert request.temperature == 0.2  # default value
    assert request.top_p == 0.9  # default value

    # Test full request with all optional parameters
    request = PerplexityChatCompletionRequestBody(
        model="llama-3.1-sonar-small-128k-online",
        messages=[
            Message(role="system", content="You are a helpful assistant"),
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!"),
            Message(role="user", content="How are you?"),
        ],
        max_tokens=100,
        temperature=0.7,
        top_p=0.95,
        search_domain_filter=["example.com", "test.com"],
        return_images=True,
        return_related_questions=True,
        search_recency_filter="week",
        top_k=10,
        stream=True,
        presence_penalty=0.5,
        frequency_penalty=1.2,
    )
    assert len(request.messages) == 4
    assert request.max_tokens == 100
    assert request.temperature == 0.7
    assert request.top_p == 0.95
    assert request.search_domain_filter == ["example.com", "test.com"]
    assert request.return_images is True
    assert request.return_related_questions is True
    assert request.search_recency_filter == "week"
    assert request.top_k == 10
    assert request.stream is True
    assert request.presence_penalty == 0.5
    assert request.frequency_penalty == 1.2

    # Test invalid temperature (too high)
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            temperature=2.0,
        )

    # Test invalid temperature (too low)
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            temperature=-0.1,
        )

    # Test invalid top_p (too high)
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            top_p=1.1,
        )

    # Test invalid top_p (too low)
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            top_p=-0.1,
        )

    # Test invalid search_domain_filter (too many domains)
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            search_domain_filter=[
                "domain1.com",
                "domain2.com",
                "domain3.com",
                "domain4.com",
            ],
        )

    # Test invalid search_recency_filter
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            search_recency_filter="invalid",
        )

    # Test invalid top_k (too high)
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            top_k=2049,
        )

    # Test invalid presence_penalty (too high)
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            presence_penalty=2.1,
        )

    # Test invalid frequency_penalty (too low)
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            frequency_penalty=0,
        )
