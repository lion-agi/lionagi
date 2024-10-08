import pytest

from lion_core.communication.instruction import (
    Instruction,
    format_image_content,
    prepare_instruction_content,
    prepare_request_response_format,
)
from lion_core.communication.message import MessageFlag, MessageRole
from lion_core.form.form import Form
from lion_core.generic.note import Note
from lion_core.sys_utils import SysUtil


# Helper function to create a mock BaseTask
class MockBaseTask(Form):
    def __init__(self, instruction_dict):
        super().__init__()
        self.instruction_dict = instruction_dict
        self.ln_id = "mock_task_id"


# Tests for helper functions
def test_prepare_request_response_format():
    fields = {"field1": "description1", "field2": "description2"}
    result = prepare_request_response_format(fields)
    assert "```json" in result
    assert "field1" in result
    assert "field2" in result


def test_format_image_content():
    text = "Sample text"
    images = ["base64_image1", "base64_image2"]
    result = format_image_content(text, images, "low")
    assert len(result) == 3
    assert result[0]["type"] == "text"
    assert result[1]["type"] == "image_url"
    assert result[2]["type"] == "image_url"


def test_prepare_instruction_content():
    result = prepare_instruction_content(
        instruction="Test instruction",
        context="Test context",
        request_fields={"field1": "desc1"},
        images=["image1"],
        image_detail="high",
    )
    assert isinstance(result, Note)
    assert result.get("instruction") == "Test instruction"
    assert result.get("context") == ["Test context"]
    assert "request_response_format" in result.to_dict()


# Tests for Instruction class
def test_instruction_init():
    instruction = Instruction("Test instruction", context="Test context")
    assert instruction.role == MessageRole.USER
    assert instruction.sender == "user"
    assert instruction.recipient == "N/A"
    assert instruction.instruction == "Test instruction"


def test_instruction_init_with_all_params():
    instruction = Instruction(
        "Test instruction",
        context="Test context",
        images=["image1"],
        sender=SysUtil.id(),
        recipient=SysUtil.id(),
        request_fields={"field1": "desc1"},
        image_detail="high",
    )
    assert "images" in instruction.content.to_dict()
    assert instruction.content.get("image_detail") == "high"


def test_instruction_init_with_message_load():
    protected_params = {
        "role": MessageRole.USER,
        "content": Note(instruction="Test"),
        "sender": "user",
    }
    instruction = Instruction(
        MessageFlag.MESSAGE_LOAD,
        context=MessageFlag.MESSAGE_LOAD,
        images=MessageFlag.MESSAGE_LOAD,
        sender=MessageFlag.MESSAGE_LOAD,
        recipient=MessageFlag.MESSAGE_LOAD,
        request_fields=MessageFlag.MESSAGE_LOAD,
        image_detail=MessageFlag.MESSAGE_LOAD,
        guidance=MessageFlag.MESSAGE_LOAD,
        protected_init_params=protected_params,
    )
    assert instruction.role == MessageRole.USER
    assert instruction.instruction == "Test"


def test_instruction_init_with_message_clone():
    instruction = Instruction(
        MessageFlag.MESSAGE_CLONE,
        context=MessageFlag.MESSAGE_CLONE,
        images=MessageFlag.MESSAGE_CLONE,
        sender=MessageFlag.MESSAGE_CLONE,
        recipient=MessageFlag.MESSAGE_CLONE,
        request_fields=MessageFlag.MESSAGE_CLONE,
        guidance=MessageFlag.MESSAGE_LOAD,
        image_detail=MessageFlag.MESSAGE_CLONE,
    )
    assert instruction.role == MessageRole.USER


def test_instruction_update_request_fields():
    instruction = Instruction("Test", request_fields={"field1": "desc1"})
    instruction.update_request_fields({"field2": "desc2"})
    assert "field1" in instruction.content["request_fields"]
    assert "field2" in instruction.content["request_fields"]


def test_instruction_update_context():
    instruction = Instruction("Test")
    instruction.update_context("context1", "context2", key="value")
    assert len(instruction.content["context"]) == 3
    assert "context1" in instruction.content["context"]
    assert {"key": "value"} in instruction.content["context"]


def test_instruction_format_content():
    instruction = Instruction("Test", images=["image1"], image_detail="low")
    formatted = instruction._format_content()
    assert isinstance(formatted["content"], list)
    assert formatted["content"][0]["type"] == "text"
    assert formatted["content"][1]["type"] == "image_url"


# Edge cases and additional tests
def test_instruction_empty_init():
    instruction = Instruction(None)
    assert instruction.instruction == "N/A"


def test_instruction_with_large_context():
    large_context = ["context"] * 1000
    instruction = Instruction("Test", context=large_context)
    assert len(instruction.content["context"]) == 1000


def test_instruction_with_many_images():
    many_images = ["image"] * 100
    instruction = Instruction("Test", images=many_images)
    assert len(instruction.content["images"]) == 100


def test_instruction_update_context_empty():
    instruction = Instruction("Test")
    instruction.update_context()
    assert "context" in instruction.content.to_dict()
    assert instruction.content["context"] == []


def test_instruction_format_content_no_images():
    instruction = Instruction("Test")
    formatted = instruction._format_content()
    assert isinstance(formatted["content"], str)


def test_instruction_with_unicode():
    instruction = Instruction("Test 你好", context="Context こんにちは")
    assert "你好" in instruction.instruction
    assert "こんにちは" in instruction.content["context"][0]


def test_instruction_with_special_characters():
    special_chars = "!@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`"
    instruction = Instruction(special_chars)
    assert instruction.instruction == special_chars


def test_instruction_with_very_long_instruction():
    long_instruction = "a" * 10000
    instruction = Instruction(long_instruction)
    assert len(instruction.instruction) == 10000


def test_instruction_update_request_fields_multiple_times():
    instruction = Instruction("Test", request_fields={"field1": "desc1"})
    instruction.update_request_fields({"field2": "desc2"})
    instruction.update_request_fields({"field3": "desc3"})
    assert len(instruction.content["request_fields"]) == 3


def test_instruction_update_context_multiple_times():
    instruction = Instruction("Test")
    instruction.update_context("context1")
    instruction.update_context("context2")
    instruction.update_context(key="value")
    assert len(instruction.content["context"]) == 3


def test_instruction_with_empty_request_fields():
    instruction = Instruction("Test", request_fields={})
    assert "instruction" in instruction.content.to_dict()
    assert instruction.content["instruction"] == "Test"


def test_instruction_with_none_values():
    instruction = Instruction(
        "Test", context=None, images=None, request_fields=None
    )
    assert "context" not in instruction.content.to_dict()
    assert "images" not in instruction.content.to_dict()
    assert "request_fields" not in instruction.content.to_dict()


def test_instruction_update_request_fields_override():
    instruction = Instruction("Test", request_fields={"field1": "desc1"})
    instruction.update_request_fields({"field1": "new_desc"})
    assert instruction.content["request_fields"]["field1"] == "new_desc"


# Performance test
def test_instruction_performance():
    import time

    start_time = time.time()
    for _ in range(1000):
        Instruction(
            "Test",
            context="Context",
            images=["image1"],
            request_fields={"field1": "desc1"},
        )
    end_time = time.time()
    assert (
        end_time - start_time < 1
    )  # Should create 1000 instructions in less than 1 second


# Thread safety test
def test_instruction_thread_safety():
    import threading

    def create_instruction():
        Instruction("Test", context=f"Context {threading.get_ident()}")

    threads = [threading.Thread(target=create_instruction) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# Test with maximum possible fields
def test_instruction_max_fields():
    max_fields = {f"field{i}": f"desc{i}" for i in range(1000)}
    instruction = Instruction("Test", request_fields=max_fields)
    assert len(instruction.content["request_fields"]) == 1000


# Test with very large base64 image
def test_instruction_large_image():
    large_image = "a" * 1000000  # 1MB base64 string
    instruction = Instruction("Test", images=[large_image])
    assert len(instruction.content["images"][0]) == 1000000


# Test instruction with all possible image details
@pytest.mark.parametrize("image_detail", ["low", "high", "auto"])
def test_instruction_all_image_details(image_detail):
    instruction = Instruction(
        "Test", images=["image1"], image_detail=image_detail
    )
    assert instruction.content["image_detail"] == image_detail


# Test instruction with mixed types in context
def test_instruction_mixed_context_types():
    mixed_context = ["string", 123, {"key": "value"}, ["list", "items"]]
    instruction = Instruction("Test", context=mixed_context)
    assert instruction.content["context"] == mixed_context


# Test updating context with various types
def test_instruction_update_context_various_types():
    instruction = Instruction("Test")
    instruction.update_context(
        "string", 123, {"key": "value"}, ["list", "items"]
    )
    assert len(instruction.content["context"]) == 4
    assert isinstance(instruction.content["context"][1], int)
    assert isinstance(instruction.content["context"][2], dict)


# Test clone method
def test_instruction_clone():
    original = Instruction("Test", context="Original context")
    cloned = original.clone()
    assert original.instruction == cloned.instruction


# Test for potential memory leaks
def test_instruction_memory_usage():
    import sys

    initial_size = sys.getsizeof(Instruction("Test"))
    large_instruction = Instruction("Test", context="a" * 1000000)
    large_size = sys.getsizeof(large_instruction)
    assert (
        large_size - initial_size < 2000000
    )  # Ensure no significant unexpected memory increase


# Test with invalid UTF-8 sequences
def test_instruction_invalid_utf8():
    invalid_utf8 = b"Invalid UTF-8: \xff"
    with pytest.raises(UnicodeDecodeError):
        Instruction(invalid_utf8.decode("utf-8"))
