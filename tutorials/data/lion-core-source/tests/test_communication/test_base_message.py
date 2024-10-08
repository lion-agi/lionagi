import pytest
from pydantic import ValidationError

from lion_core.communication.message import MessageRole, RoledMessage
from lion_core.generic.note import Note
from lion_core.sys_utils import SysUtil


def test_roled_message_init():
    msg = RoledMessage(
        role=MessageRole.USER,
        content=Note(text="Hello"),
        sender=SysUtil.id(),
    )
    assert msg.role == MessageRole.USER
    assert msg.content.get(["text"]) == "Hello"


def test_roled_message_init_invalid_role():
    with pytest.raises(ValueError):
        RoledMessage(role="invalid_role", content=Note(text="Hello"))


def test_roled_message_image_content_no_images():
    msg = RoledMessage(role=MessageRole.USER, content=Note(text="No images"))
    assert msg.image_content is None


def test_roled_message_chat_msg():
    msg = RoledMessage(
        role=MessageRole.ASSISTANT, content=Note(text="Response")
    )
    chat_msg = msg.chat_msg
    assert chat_msg["role"] == "assistant"
    assert chat_msg["content"] == "{'text': 'Response'}"


def test_roled_message_chat_msg_with_images():
    content = Note(
        text="Image description",
        images=["base64_image_data"],
        image_detail="low",
    )
    msg = RoledMessage(role=MessageRole.USER, content=content)
    chat_msg = msg.chat_msg
    assert isinstance(chat_msg["content"], dict)
    assert "images" in chat_msg["content"]


def test_roled_message_validate_role():
    assert (
        RoledMessage._validate_role(MessageRole.SYSTEM) == MessageRole.SYSTEM
    )
    with pytest.raises(ValueError):
        RoledMessage._validate_role("invalid_role")


def test_roled_message_format_content():
    msg = RoledMessage(role=MessageRole.USER, content=Note(text="Hello"))
    formatted = msg._format_content()
    assert formatted["role"] == "user"
    assert formatted["content"] == "{'text': 'Hello'}"


def test_roled_message_clone():
    original = RoledMessage(
        role=MessageRole.ASSISTANT,
        content=Note(text="Original"),
        sender=SysUtil.id(),
    )
    cloned = original.clone()
    assert cloned.role == original.role
    assert cloned.content.to_dict() == original.content.to_dict()
    assert cloned.ln_id != original.ln_id
    assert cloned.metadata.get(["clone_from"]) == original


def test_roled_message_from_dict():
    data = {
        "role": "user",
        "content": {"text": "Hello"},
        "recipient": SysUtil.id(),
    }
    msg = RoledMessage(**data)
    assert msg.role == MessageRole.USER
    assert msg.content.get("text") == "Hello"
    assert msg.sender == "N/A"


def test_roled_message_from_dict_invalid_data():
    invalid_data = {"role": "invalid_role", "content": "Not a Note object"}
    with pytest.raises(ValidationError):
        RoledMessage.from_dict(invalid_data)


# def test_roled_message_str_representation():
#     msg = RoledMessage(
#         role=MessageRole.SYSTEM,
#         content=Note(text="System message"),
#         sender="system",
#     )
#     str_repr = str(msg)
#     assert "Message(role=system" in str_repr
#     assert "sender=system" in str_repr
#     assert "content='{'text': 'System message'}'" in str_repr


def test_roled_message_long_content_str():
    long_text = "A" * 100
    msg = RoledMessage(role=MessageRole.USER, content=Note(text=long_text))
    str_repr = str(msg)
    assert len(str_repr) < 200  # Ensure it's truncated
    assert "..." in str_repr


def test_roled_message_empty_content():
    msg = RoledMessage(role=MessageRole.USER, content=Note())
    assert msg.content.to_dict() == {}


def test_roled_message_clone_with_complex_content():
    complex_content = Note(
        text_="Complex",
        list_=[1, 2, 3],
        dict_={"a": 1, "b": 2},
        nested_=Note(inner="Nested"),
    )
    original = RoledMessage(role=MessageRole.USER, content=complex_content)
    cloned = original.clone()
    assert cloned.content.to_dict() == original.content.to_dict()


# Edge case: Handling of very large content
def test_roled_message_large_content():
    large_content = Note(text="A" * 1000000)  # 1 million characters
    msg = RoledMessage(role=MessageRole.ASSISTANT, content=large_content)
    assert (
        len(str(msg)) < 2000
    )  # Ensure string representation is reasonably sized


# Edge case: Ensure proper handling of None values
def test_roled_message_none_values():
    msg = RoledMessage(role=MessageRole.SYSTEM, content=Note(field=None))
    assert msg.content.get("field") is None
    assert "None" in str(msg)


# Test for potential memory leaks in clone method
def test_roled_message_clone_memory():
    import sys

    original = RoledMessage(
        role=MessageRole.USER, content=Note(text="Memory test")
    )
    initial_size = sys.getsizeof(original)
    clones = [original.clone() for _ in range(1000)]
    assert (
        sys.getsizeof(clones[-1]) - initial_size < 1000
    )  # Ensure no significant memory increase


# Test thread safety of clone method
def test_roled_message_clone_thread_safety():
    import threading

    original = RoledMessage(
        role=MessageRole.ASSISTANT, content=Note(text="Thread test")
    )
    clones = []

    def clone_message():
        clones.append(original.clone())

    threads = [threading.Thread(target=clone_message) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(clones) == 100
    assert all(c.content.get("text") == "Thread test" for c in clones)


# Test handling of circular references
def test_roled_message_circular_reference():
    content = Note(text="Circular")
    content.set("self_ref", content)
    msg = RoledMessage(role=MessageRole.USER, content=content)
    cloned = msg.clone()
    assert cloned.content.get("self_ref") is cloned.content


# Test for potential issues with Unicode characters
def test_roled_message_unicode_handling():
    unicode_content = Note(text="Unicode test: 你好世界! 🌍")
    msg = RoledMessage(role=MessageRole.USER, content=unicode_content)
    cloned = msg.clone()
    assert cloned.content.get("text") == "Unicode test: 你好世界! 🌍"
    str_repr = str(cloned)
    assert "你好世界" in str_repr and "🌍" in str_repr


# Test handling of very long role names (edge case)
def test_roled_message_long_role_name():
    long_role = "a" * 1000
    with pytest.raises(ValueError):
        RoledMessage(role=long_role, content=Note(text="Long role test"))


# Test for potential issues with time-sensitive operations
def test_roled_message_time_sensitivity():
    import time

    msg = RoledMessage(role=MessageRole.SYSTEM, content=Note(text="Time test"))
    time.sleep(0.1)
    cloned = msg.clone()
    assert cloned.timestamp > msg.timestamp


# Test handling of invalid UTF-8 sequences
def test_roled_message_invalid_utf8():
    invalid_utf8 = b"Invalid UTF-8: \xff"
    with pytest.raises(UnicodeDecodeError):
        RoledMessage(
            role=MessageRole.USER,
            content=Note(text=invalid_utf8.decode("utf-8")),
        )


# Test for potential issues with multi-threaded access
def test_roled_message_multithreaded_access():
    import threading

    msg = RoledMessage(role=MessageRole.ASSISTANT, content=Note(counter=0))
    lock = threading.Lock()

    def increment_counter():
        with lock:
            current = msg.content.get("counter")
            msg.content.set("counter", current + 1)

    threads = [threading.Thread(target=increment_counter) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert msg.content.get("counter") == 100
