import time
from datetime import datetime, timezone

import pytest
from lionabc.exceptions import LionValueError
from pydantic_core._pydantic_core import ValidationError

from lion_core.generic.component import Component
from lion_core.generic.note import Note
from lion_core.sys_utils import SysUtil


@pytest.fixture
def valid_id():
    return SysUtil.id()


@pytest.fixture
def timestamp():
    return datetime.now(timezone.utc).timestamp()


def test_basic_initialization(valid_id, timestamp):
    component = Component(ln_id=valid_id, timestamp=timestamp)
    assert component.ln_id == valid_id
    assert component.timestamp == timestamp
    assert isinstance(component.metadata, Note)
    assert component.content is None
    assert component.embedding == []
    assert component.extra_fields == {}


def test_full_initialization(valid_id, timestamp):
    metadata = Note(key="value")
    content = "Test content"
    embedding = [0.1, 0.2, 0.3]
    extra_fields = {"extra_key": "extra_value"}

    component = Component(
        ln_id=valid_id,
        timestamp=timestamp,
        metadata=metadata,
        content=content,
        embedding=embedding,
        extra_fields=extra_fields,
    )

    assert component.metadata.content == {"key": "value"}
    assert component.content == content
    assert component.embedding == embedding
    assert component.extra_fields == extra_fields


def test_metadata_serialization():
    metadata = Note(key="value")
    component = Component(metadata=metadata)
    serialized = component.model_dump()
    assert serialized["metadata"] == {"key": "value"}


def test_add_field():
    component = Component()
    component.add_field("new_field", "new_value")
    assert component.new_field == "new_value"
    assert "new_field" in component.extra_fields

    with pytest.raises(LionValueError):
        component.add_field("new_field", "another_value")


def test_update_field():
    component = Component()
    component.add_field("test_field", "initial_value")
    component.update_field("test_field", "updated_value")
    assert component.test_field == "updated_value"

    component.update_field("new_field", "new_value")
    assert component.new_field == "new_value"


def test_to_dict_consistency(valid_id, timestamp):
    component = Component(
        ln_id=valid_id,
        timestamp=timestamp,
        content="Test content",
        embedding=[0.1, 0.2, 0.3],
    )
    component.add_field("extra_field", "extra_value")

    dict_repr = component.to_dict()

    assert dict_repr["ln_id"] == valid_id
    assert dict_repr["timestamp"] == timestamp
    assert dict_repr["content"] == "Test content"
    assert dict_repr["embedding"] == [0.1, 0.2, 0.3]
    assert dict_repr["extra_field"] == "extra_value"
    assert dict_repr["lion_class"] == "Component"


def test_from_dict(valid_id, timestamp):
    input_dict = {
        "ln_id": valid_id,
        "timestamp": timestamp,
        "content": "Test content",
        "embedding": [0.1, 0.2, 0.3],
        "extra_field": "extra_value",
        "lion_class": "Component",
    }

    component = Component.from_dict(input_dict)

    assert component.ln_id == valid_id
    assert component.timestamp == timestamp
    assert component.content == "Test content"
    assert component.embedding == [0.1, 0.2, 0.3]
    assert component.extra_field == "extra_value"


def test_nested_structures():
    nested_content = {"level1": {"level2": [1, 2, {"level3": "deep"}]}}
    nested_metadata = Note(meta_level1={"meta_level2": ["a", "b", "c"]})

    component = Component(content=nested_content, metadata=nested_metadata)
    serialized = component.to_dict()

    assert serialized["content"] == nested_content
    assert serialized["metadata"] == nested_metadata.content

    deserialized = Component.from_dict(serialized)
    assert deserialized.content == nested_content
    assert deserialized.metadata.content == nested_metadata.content


def test_large_component():
    large_content = "x" * 1000000  # 1MB of data
    large_embedding = [0.1] * 10000  # 10,000 float embeddings

    component = Component(content=large_content, embedding=large_embedding)
    serialized = component.to_dict()
    deserialized = Component.from_dict(serialized)

    assert len(deserialized.content) == 1000000
    assert len(deserialized.embedding) == 10000


def test_component_equality(valid_id):
    comp1 = Component(ln_id=valid_id, content="Same content")
    time.sleep(0.01)  # Ensure different timestamps
    comp2 = Component(ln_id=valid_id, content="Same content")
    comp3 = Component(ln_id=SysUtil.id(), content="Different content")

    assert comp1 != comp2  # Different timestamps
    assert comp1 != comp3  # Different ln_id and content


def test_component_immutability(valid_id, timestamp):
    component = Component(ln_id=valid_id, timestamp=timestamp)

    with pytest.raises(ValidationError):
        component.ln_id = SysUtil.id()

    with pytest.raises(ValidationError):
        component.timestamp = datetime.now().timestamp()


def test_component_with_note_content():
    note_content = Note(key="value")
    component = Component(content=note_content)
    serialized = component.to_dict()

    assert serialized["content"] == {"key": "value"}

    deserialized = Component.from_dict(serialized)
    assert isinstance(deserialized.content, dict)
    assert deserialized.content == {"key": "value"}


def test_component_string_representations(valid_id):
    component = Component(ln_id=valid_id, content="Test content")
    str_repr = str(component)
    repr_repr = repr(component)

    assert valid_id[:8] in str_repr
    assert "Test content" in str_repr
    assert valid_id in repr_repr
    assert "Test content" in repr_repr


# File: tests/test_generic/test_component.py
