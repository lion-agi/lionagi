import pytest
from pydantic import ValidationError

from lionagi.integrations.perplexity_.api_endpoints.chat_completions.request.request_body import (
    Message,
    PerplexityChatCompletionRequestBody,
)
from lionagi.integrations.perplexity_.api_endpoints.chat_completions.response.response_body import (
    Choice,
)
from lionagi.integrations.perplexity_.api_endpoints.chat_completions.response.response_body import (
    Message as ResponseMessage,
)
from lionagi.integrations.perplexity_.api_endpoints.chat_completions.response.response_body import (
    PerplexityChatCompletionResponseBody,
    RelatedQuestion,
)
from lionagi.integrations.perplexity_.api_endpoints.data_models import (
    Citation,
    Usage,
)


def test_message_validation():
    # Test valid message
    message = Message(role="user", content="Hello")
    assert message.role == "user"
    assert message.content == "Hello"

    # Test invalid role
    with pytest.raises(ValidationError):
        Message(role="invalid_role", content="Hello")

    # Test missing content
    with pytest.raises(ValidationError):
        Message(role="user")

    # Test missing role
    with pytest.raises(ValidationError):
        Message(content="Hello")


def test_chat_completion_request_validation():
    # Test valid request
    request = PerplexityChatCompletionRequestBody(
        model="llama-3.1-sonar-small-128k-online",
        messages=[
            Message(role="system", content="You are a helpful assistant"),
            Message(role="user", content="Hello"),
        ],
        temperature=0.7,
        top_p=0.9,
    )
    assert request.model == "llama-3.1-sonar-small-128k-online"
    assert len(request.messages) == 2
    assert request.temperature == 0.7
    assert request.top_p == 0.9

    # Test invalid temperature
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            temperature=2.0,
        )

    # Test invalid top_p
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            top_p=1.5,
        )

    # Test invalid search_domain_filter length
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            search_domain_filter=["domain1", "domain2", "domain3", "domain4"],
        )

    # Test invalid search_recency_filter
    with pytest.raises(ValidationError):
        PerplexityChatCompletionRequestBody(
            model="llama-3.1-sonar-small-128k-online",
            messages=[Message(role="user", content="Hello")],
            search_recency_filter="invalid",
        )


def test_chat_completion_response_validation():
    # Test valid response
    response = PerplexityChatCompletionResponseBody(
        id="resp_123",
        model="llama-3.1-sonar-small-128k-online",
        object="chat.completion",
        created=1234567890,
        choices=[
            Choice(
                index=0,
                message=ResponseMessage(role="assistant", content="Hello!"),
                finish_reason="stop",
            )
        ],
        usage=Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        citations=[
            Citation(
                url="https://example.com",
                text="Example text",
                title="Example Title",
            )
        ],
        related_questions=[RelatedQuestion(text="What is the weather like?")],
    )
    assert response.id == "resp_123"
    assert response.model == "llama-3.1-sonar-small-128k-online"
    assert response.object == "chat.completion"
    assert len(response.choices) == 1
    assert response.usage.total_tokens == 15
    assert len(response.citations) == 1
    assert len(response.related_questions) == 1

    # Test missing required fields
    with pytest.raises(ValidationError):
        PerplexityChatCompletionResponseBody()

    # Test invalid choice finish_reason
    with pytest.raises(ValidationError):
        PerplexityChatCompletionResponseBody(
            id="resp_123",
            model="llama-3.1-sonar-small-128k-online",
            object="chat.completion",
            created=1234567890,
            choices=[
                Choice(
                    index=0,
                    message=ResponseMessage(
                        role="assistant", content="Hello!"
                    ),
                    finish_reason="invalid",
                )
            ],
            usage=Usage(
                prompt_tokens=10, completion_tokens=5, total_tokens=15
            ),
        )


def test_usage_validation():
    # Test valid usage
    usage = Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 5
    assert usage.total_tokens == 15

    # Test missing fields
    with pytest.raises(ValidationError):
        Usage(prompt_tokens=10)

    # Test negative tokens
    with pytest.raises(ValidationError):
        Usage(prompt_tokens=-1, completion_tokens=5, total_tokens=4)


def test_citation_validation():
    # Test valid citation
    citation = Citation(
        url="https://example.com",
        text="Example text",
        title="Example Title",
        year=2024,
        author="John Doe",
    )
    assert citation.url == "https://example.com"
    assert citation.text == "Example text"
    assert citation.title == "Example Title"
    assert citation.year == 2024
    assert citation.author == "John Doe"

    # Test minimal citation
    citation = Citation(url="https://example.com")
    assert citation.url == "https://example.com"
    assert citation.text is None
    assert citation.title is None
    assert citation.year is None
    assert citation.author is None

    # Test missing required url
    with pytest.raises(ValidationError):
        Citation(text="Example text")


def test_related_question_validation():
    # Test valid related question
    question = RelatedQuestion(text="What is the weather like?")
    assert question.text == "What is the weather like?"

    # Test missing text
    with pytest.raises(ValidationError):
        RelatedQuestion()
