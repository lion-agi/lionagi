import pytest

from lion_core.communication.assistant_response import AssistantResponse
from lion_core.communication.message import MessageFlag, MessageRole


# Basic functionality tests
def test_assistant_response_init():
    response = AssistantResponse(
        {"content": "Test response"}, "assistant", "user"
    )
    assert response.role == MessageRole.ASSISTANT
    assert response.sender == "assistant"
    assert response.recipient == "user"
    assert response.response == "Test response"


def test_assistant_response_init_default_sender():
    response = AssistantResponse({"content": "Test response"}, None, "user")
    assert response.sender == "N/A"


def test_assistant_response_init_with_message_load():
    protected_params = {
        "role": MessageRole.ASSISTANT,
        "content": {"assistant_response": "Test"},
        "sender": "assistant",
    }
    response = AssistantResponse(
        MessageFlag.MESSAGE_LOAD,
        MessageFlag.MESSAGE_LOAD,
        MessageFlag.MESSAGE_LOAD,
        protected_init_params=protected_params,
    )
    assert response.role == MessageRole.ASSISTANT
    assert response.response == "Test"


def test_assistant_response_init_with_message_clone():
    response = AssistantResponse(
        MessageFlag.MESSAGE_CLONE,
        MessageFlag.MESSAGE_CLONE,
        MessageFlag.MESSAGE_CLONE,
    )
    assert response.role == MessageRole.ASSISTANT


# Edge cases and additional tests
def test_assistant_response_empty_content():
    response = AssistantResponse({"content": ""}, "assistant", "user")
    assert response.response == ""


def test_assistant_response_missing_content():
    response = AssistantResponse({}, "assistant", "user")
    assert response.response == ""


def test_assistant_response_none_content():
    response = AssistantResponse(None, "assistant", "user")
    assert response.response == ""


def test_assistant_response_very_long_content():
    long_content = "a" * 10000
    response = AssistantResponse(
        {"content": long_content}, "assistant", "user"
    )
    assert len(response.response) == 10000


def test_assistant_response_with_special_characters():
    special_chars = "!@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`"
    response = AssistantResponse(
        {"content": special_chars}, "assistant", "user"
    )
    assert response.response == special_chars


def test_assistant_response_with_unicode():
    unicode_content = "你好世界 - Hello World - こんにちは世界"
    response = AssistantResponse(
        {"content": unicode_content}, "assistant", "user"
    )
    assert response.response == unicode_content


def test_assistant_response_serialization():
    response = AssistantResponse(
        {"content": "Test response"}, "assistant", "user"
    )
    serialized = response.to_dict()
    deserialized = AssistantResponse.from_dict(serialized)
    assert deserialized.response == response.response
    assert deserialized.sender == response.sender


def test_assistant_response_clone():
    original = AssistantResponse(
        {"content": "Original response"}, "assistant", "user"
    )
    cloned = original.clone()
    assert cloned.response == original.response
    assert cloned.ln_id != original.ln_id


# Performance test
def test_assistant_response_performance():
    import time

    start_time = time.time()
    for _ in range(1000):
        AssistantResponse({"content": "Test response"}, "assistant", "user")
    end_time = time.time()
    assert (
        end_time - start_time < 1
    )  # Should create 1000 AssistantResponse objects in less than 1 second


# Thread safety test
def test_assistant_response_thread_safety():
    import threading

    def create_response():
        AssistantResponse(
            {"content": f"Thread {threading.get_ident()}"}, "assistant", "user"
        )

    threads = [threading.Thread(target=create_response) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# Test with invalid UTF-8 sequences
def test_assistant_response_invalid_utf8():
    invalid_utf8 = b"Invalid UTF-8: \xff"
    with pytest.raises(UnicodeDecodeError):
        AssistantResponse(
            {"content": invalid_utf8.decode("utf-8")}, "assistant", "user"
        )


# Test assistant response with various content types
@pytest.mark.parametrize(
    "content",
    [
        123,
        3.14,
        True,
        ["list", "item"],
        {"nested": "dict"},
    ],
)
def test_assistant_response_various_content_types(content):
    response = AssistantResponse({"content": content}, "assistant", "user")
    assert response.response == content


# Test for potential memory leaks
def test_assistant_response_memory_usage():
    import sys

    initial_size = sys.getsizeof(
        AssistantResponse({"content": "Test"}, "assistant", "user")
    )
    large_response = AssistantResponse(
        {"content": "a" * 1000000}, "assistant", "user"
    )
    large_size = sys.getsizeof(large_response)
    assert (
        large_size - initial_size < 2000000
    )  # Ensure no significant unexpected memory increase


# Test assistant response with empty strings for all parameters
def test_assistant_response_empty_strings():
    response = AssistantResponse({"content": ""}, None, None)
    assert response.response == ""
    assert response.sender == "N/A"
    assert response.recipient == "N/A"


# Test assistant response with None values for sender and recipient
def test_assistant_response_none_values():
    response = AssistantResponse({"content": "Test"}, None, None)
    assert response.sender == "N/A"
    assert response.recipient == "N/A"


# Test assistant response with various types in the content dictionary
def test_assistant_response_complex_content():
    complex_content = {
        "content": "Main content",
        "additional_info": {
            "nested": ["list", "of", "items"],
            "number": 42,
            "boolean": True,
        },
    }
    response = AssistantResponse(complex_content, "assistant", "user")
    assert response.response == "Main content"


# Test assistant response with missing 'content' key
def test_assistant_response_missing_content_key():
    response = AssistantResponse({"other_key": "value"}, "assistant", "user")
    assert response.response == {"other_key": "value"}


# Test assistant response with non-dict input
def test_assistant_response_non_dict_input():
    response = AssistantResponse("Just a string", "assistant", "user")
    assert response.response == "Just a string"


# Test assistant response with very large input
def test_assistant_response_very_large_input():
    large_input = {"content": "a" * 1000000}  # 1MB of content
    response = AssistantResponse(large_input, "assistant", "user")
    assert len(response.response) == 1000000
