import pytest
from pydantic import ValidationError

from lionagi.integrations.perplexity_.api_endpoints.chat_completions.response.response_body import (
    Choice,
    Message,
    PerplexityChatCompletionResponseBody,
    RelatedQuestion,
)
from lionagi.integrations.perplexity_.api_endpoints.data_models import (
    Citation,
    Usage,
)


def test_message_validation():
    # Test valid message
    message = Message(role="assistant", content="Hello!")
    assert message.role == "assistant"
    assert message.content == "Hello!"

    # Test missing role
    with pytest.raises(ValidationError):
        Message(content="Hello!")

    # Test missing content
    with pytest.raises(ValidationError):
        Message(role="assistant")


def test_choice_validation():
    # Test valid choice
    choice = Choice(
        index=0,
        message=Message(role="assistant", content="Hello!"),
        finish_reason="stop",
    )
    assert choice.index == 0
    assert choice.message.content == "Hello!"
    assert choice.finish_reason == "stop"

    # Test invalid finish_reason
    with pytest.raises(ValidationError):
        Choice(
            index=0,
            message=Message(role="assistant", content="Hello!"),
            finish_reason="invalid",
        )

    # Test missing required fields
    with pytest.raises(ValidationError):
        Choice(index=0, message=Message(role="assistant", content="Hello!"))

    with pytest.raises(ValidationError):
        Choice(index=0, finish_reason="stop")


def test_usage_validation():
    # Test valid usage
    usage = Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 20
    assert usage.total_tokens == 30

    # Test missing fields
    with pytest.raises(ValidationError):
        Usage(prompt_tokens=10, completion_tokens=20)

    with pytest.raises(ValidationError):
        Usage(prompt_tokens=10, total_tokens=30)

    with pytest.raises(ValidationError):
        Usage(completion_tokens=20, total_tokens=30)


def test_citation_validation():
    # Test valid citation with all fields
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

    # Test minimal valid citation
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


def test_chat_completion_response_validation():
    # Test valid response with all fields
    response = PerplexityChatCompletionResponseBody(
        id="resp_123",
        model="llama-3.1-sonar-small-128k-online",
        object="chat.completion",
        created=1234567890,
        choices=[
            Choice(
                index=0,
                message=Message(role="assistant", content="Hello!"),
                finish_reason="stop",
            )
        ],
        usage=Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        citations=[
            Citation(
                url="https://example.com",
                text="Example text",
                title="Example Title",
                year=2024,
                author="John Doe",
            )
        ],
        related_questions=[RelatedQuestion(text="What is the weather like?")],
    )
    assert response.id == "resp_123"
    assert response.model == "llama-3.1-sonar-small-128k-online"
    assert response.object == "chat.completion"
    assert response.created == 1234567890
    assert len(response.choices) == 1
    assert response.choices[0].message.content == "Hello!"
    assert response.usage.total_tokens == 30
    assert len(response.citations) == 1
    assert len(response.related_questions) == 1

    # Test minimal valid response
    response = PerplexityChatCompletionResponseBody(
        id="resp_123",
        model="llama-3.1-sonar-small-128k-online",
        object="chat.completion",
        created=1234567890,
        choices=[
            Choice(
                index=0,
                message=Message(role="assistant", content="Hello!"),
                finish_reason="stop",
            )
        ],
        usage=Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
    )
    assert response.citations is None
    assert response.related_questions is None

    # Test missing required fields
    with pytest.raises(ValidationError):
        PerplexityChatCompletionResponseBody(
            id="resp_123",
            model="llama-3.1-sonar-small-128k-online",
            object="chat.completion",
            created=1234567890,
            choices=[
                Choice(
                    index=0,
                    message=Message(role="assistant", content="Hello!"),
                    finish_reason="stop",
                )
            ],
        )

    with pytest.raises(ValidationError):
        PerplexityChatCompletionResponseBody(
            id="resp_123",
            model="llama-3.1-sonar-small-128k-online",
            object="chat.completion",
            created=1234567890,
            usage=Usage(
                prompt_tokens=10, completion_tokens=20, total_tokens=30
            ),
        )


def test_streaming_response_validation():
    # Test delta message in streaming response
    response = PerplexityChatCompletionResponseBody(
        id="resp_123",
        model="llama-3.1-sonar-small-128k-online",
        object="chat.completion",
        created=1234567890,
        choices=[
            Choice(
                index=0,
                message=Message(role="assistant", content="H"),
                finish_reason=None,  # No finish reason in streaming chunks
            )
        ],
        usage=Usage(prompt_tokens=10, completion_tokens=1, total_tokens=11),
    )
    assert response.choices[0].message.content == "H"
    assert response.choices[0].finish_reason is None
