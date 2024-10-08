import pytest

from lion_core.communication.message import MessageFlag, MessageRole
from lion_core.communication.system import (
    DEFAULT_SYSTEM,
    System,
    format_system_content,
)
from lion_core.generic.note import Note
from lion_core.sys_utils import SysUtil


# Tests for format_system_content function
def test_format_system_content_default():
    result = format_system_content(None, DEFAULT_SYSTEM)
    assert isinstance(result, Note)
    assert result.get("system_info") == DEFAULT_SYSTEM


def test_format_system_content_custom():
    custom_message = "Custom system message"
    result = format_system_content(None, custom_message)
    assert result.get("system_info") == custom_message


def test_format_system_content_with_datetime_flag():
    result = format_system_content(True, DEFAULT_SYSTEM)
    assert "System Date:" in result.get("system_info")


def test_format_system_content_with_datetime_string():
    custom_date = "2023-01-01 12:00"
    result = format_system_content(custom_date, DEFAULT_SYSTEM)
    assert custom_date in result.get("system_info")


# Tests for System class
def test_system_init_default():
    system = System()
    assert system.role == MessageRole.SYSTEM
    assert system.sender == "system"
    assert system.recipient == "N/A"
    assert system.system_info == DEFAULT_SYSTEM


def test_system_init_custom():
    custom_message = "Custom system message"
    system = System(
        custom_message, sender=SysUtil.id(), recipient=SysUtil.id()
    )
    assert system.system_info == custom_message


def test_system_init_with_datetime():
    system = System(system_datetime=True)
    assert "System Date:" in system.system_info


def test_system_init_with_message_load():
    protected_params = {
        "role": MessageRole.SYSTEM,
        "content": Note(system_info="Test"),
        "sender": "system",
    }
    system = System(
        MessageFlag.MESSAGE_LOAD,
        sender=MessageFlag.MESSAGE_LOAD,
        recipient=MessageFlag.MESSAGE_LOAD,
        system_datetime=MessageFlag.MESSAGE_LOAD,
        protected_init_params=protected_params,
    )
    assert system.role == MessageRole.SYSTEM
    assert system.system_info == "Test"


def test_system_init_with_message_clone():
    system = System(
        MessageFlag.MESSAGE_CLONE,
        sender=MessageFlag.MESSAGE_CLONE,
        recipient=MessageFlag.MESSAGE_CLONE,
        system_datetime=MessageFlag.MESSAGE_CLONE,
    )
    assert system.role == MessageRole.SYSTEM


# Edge cases and additional tests
def test_system_empty_message():
    system = System("")
    assert system.system_info == DEFAULT_SYSTEM


def test_system_none_message():
    system = System(None)
    assert system.system_info == DEFAULT_SYSTEM


def test_system_very_long_message():
    long_message = "a" * 10000
    system = System(long_message)
    assert len(system.system_info) == 10000


def test_system_with_special_characters():
    special_chars = "!@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`"
    system = System(special_chars)
    assert system.system_info == special_chars


def test_system_with_unicode():
    unicode_message = "你好世界 - Hello World - こんにちは世界"
    system = System(unicode_message)
    assert system.system_info == unicode_message


def test_system_serialization():
    system = System("Test message", system_datetime=True)
    serialized = system.to_dict()
    deserialized = System.from_dict(serialized)
    assert deserialized.system_info == system.system_info
    assert deserialized.sender == system.sender


def test_system_clone():
    original = System("Original message")
    cloned = original.clone()
    assert cloned.system_info == original.system_info
    assert cloned.ln_id != original.ln_id


# Performance test
def test_system_performance():
    import time

    start_time = time.time()
    for _ in range(1000):
        System("Test message", system_datetime=True)
    end_time = time.time()
    assert (
        end_time - start_time < 1
    )  # Should create 1000 System messages in less than 1 second


# Thread safety test
def test_system_thread_safety():
    import threading

    def create_system():
        System(f"Thread {threading.get_ident()}", system_datetime=True)

    threads = [threading.Thread(target=create_system) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# Test with invalid UTF-8 sequences
def test_system_invalid_utf8():
    invalid_utf8 = b"Invalid UTF-8: \xff"
    with pytest.raises(UnicodeDecodeError):
        System(invalid_utf8.decode("utf-8"))


# Test system with different datetime formats
@pytest.mark.parametrize(
    "datetime_format",
    [
        "2023-01-01",
        "2023-01-01 12:00:00",
        "Jan 1, 2023",
        "1/1/2023",
    ],
)
def test_system_various_datetime_formats(datetime_format):
    system = System("Test", system_datetime=datetime_format)
    assert datetime_format in system.system_info


# Test system with very large datetime string
def test_system_large_datetime():
    large_datetime = "a" * 1000000
    system = System("Test", system_datetime=large_datetime)
    assert large_datetime in system.system_info


# Test for potential memory leaks
def test_system_memory_usage():
    import sys

    initial_size = sys.getsizeof(System("Test"))
    large_system = System("a" * 1000000)
    large_size = sys.getsizeof(large_system)
    assert (
        large_size - initial_size < 2000000
    )  # Ensure no significant unexpected memory increase


# Test system with empty strings for all parameters
def test_system_empty_strings():
    system = System("", sender="", recipient="")
    assert system.system_info == DEFAULT_SYSTEM
    assert system.sender == "system"
    assert system.recipient == "N/A"


# Test system with None values for sender and recipient
def test_system_none_values():
    system = System("Test", sender=None, recipient=None)
    assert system.sender == "system"
    assert system.recipient == "N/A"


# Test system with various types of content
@pytest.mark.parametrize(
    "content",
    [
        123,
        3.14,
        True,
        ["list", "item"],
        {"key": "value"},
    ],
)
def test_system_various_content_types(content):
    system = System(content)
    assert str(content) in system.system_info
