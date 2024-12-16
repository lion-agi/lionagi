"""Tests for the Component class."""

from datetime import datetime

import pytest

from lionagi.core.generic.types import Component
from lionagi.core.typing import UNDEFINED, Field, Note


def test_component_creation():
    """Test basic Component creation."""
    component = Component()
    assert component.ln_id is not None
    assert isinstance(component.created_timestamp, float)
    assert isinstance(component.metadata, Note)
    assert component.content is None
    assert isinstance(component.embedding, list)
    assert len(component.embedding) == 0


def test_component_with_content():
    """Test Component creation with content."""
    content = "Test content"
    component = Component(content=content)
    assert component.content == content


def test_component_with_metadata():
    """Test Component creation with metadata."""
    metadata = Note(key="value")
    component = Component(metadata=metadata)
    assert component.metadata == metadata
    assert component.metadata.get("key") == "value"


def test_component_metadata_immutability():
    """Test that metadata cannot be directly assigned."""
    component = Component()
    with pytest.raises(AttributeError):
        component.metadata = Note()


def test_component_add_field():
    """Test adding a new field to the component."""
    component = Component()
    component.add_field("test_field", value="test_value", annotation=str)
    assert hasattr(component, "test_field")
    assert component.test_field == "test_value"

    # Test adding field that already exists
    with pytest.raises(ValueError):
        component.add_field("test_field", value="another_value")


def test_component_update_field():
    """Test updating an existing field."""
    component = Component()

    # Add field and then update it
    component.add_field("test_field", value="initial_value")
    component.update_field("test_field", value="updated_value")
    assert component.test_field == "updated_value"

    # Update with new annotation
    component.update_field("test_field", annotation=int, value=42)
    assert component.test_field == 42

    # Verify last_updated metadata is set
    assert "test_field" in component.metadata.get("last_updated", {})


def test_component_field_access():
    """Test field access behavior."""
    component = Component()

    # Test accessing non-existent field
    with pytest.raises(AttributeError):
        _ = component.nonexistent_field

    # Test accessing field with default value
    component.add_field("test_field", value="test_value")
    assert component.test_field == "test_value"


def test_component_to_dict():
    """Test Component conversion to dictionary."""
    component = Component(content="test content", metadata=Note(key="value"))
    component.add_field("custom_field", value="custom_value")

    dict_repr = component.to_dict()
    assert isinstance(dict_repr, dict)
    assert dict_repr["content"] == "test content"
    assert dict_repr["metadata"].get("key") == "value"
    assert dict_repr["custom_field"] == "custom_value"
    assert dict_repr["lion_class"] == "Component"


def test_component_from_dict():
    """Test Component creation from dictionary."""
    original = Component(content="test content", metadata=Note(key="value"))
    original.add_field("custom_field", value="custom_value")

    dict_repr = original.to_dict()
    recreated = Component.from_dict(dict_repr)

    assert recreated.content == original.content
    assert recreated.metadata.get("key") == "value"
    assert recreated.custom_field == "custom_value"


def test_component_to_note():
    """Test conversion to Note object."""
    component = Component(content="test content", metadata=Note(key="value"))
    note = component.to_note()
    assert isinstance(note, Note)
    assert note.get("content") == "test content"
    assert note.get("metadata").get("key") == "value"


def test_component_str_representation():
    """Test string representation."""
    component = Component(content="test content")
    str_repr = str(component)
    assert "Component" in str_repr
    assert str(component.ln_id)[:8] in str_repr
    assert "test content" in str_repr


def test_component_repr():
    """Test detailed string representation."""
    component = Component(content="test content", metadata=Note(key="value"))
    repr_str = repr(component)
    assert "Component" in repr_str
    assert "test content" in repr_str
    assert "metadata" in repr_str


def test_component_extra_fields_protection():
    """Test protection of extra_fields attribute."""
    component = Component()
    with pytest.raises(AttributeError):
        component.extra_fields = {}


def test_component_field_updates_timestamp():
    """Test that field updates set last_updated timestamp."""
    component = Component()
    component.add_field("test_field", value="test_value")

    # Get initial timestamp
    initial_timestamp = component.metadata.get("last_updated", {}).get(
        "test_field"
    )
    assert initial_timestamp is not None

    # Update field and check timestamp changed
    component.update_field("test_field", value="new_value")
    new_timestamp = component.metadata.get("last_updated", {}).get(
        "test_field"
    )
    assert new_timestamp > initial_timestamp


def test_component_undefined_field_behavior():
    """Test behavior with UNDEFINED field values."""
    component = Component()
    component.add_field("test_field", value=UNDEFINED)
    assert component.test_field is UNDEFINED

    # Test that UNDEFINED fields are excluded from dict representation
    dict_repr = component.to_dict()
    assert "test_field" not in dict_repr


def test_component_metadata_serialization():
    """Test metadata serialization behavior."""
    metadata = Note(key="value", nested=Note(subkey="subvalue"))
    component = Component(metadata=metadata)

    dict_repr = component.to_dict()
    assert isinstance(dict_repr["metadata"], dict)
    assert dict_repr["metadata"].get("key") == "value"
    assert dict_repr["metadata"].get("nested").get("subkey") == "subvalue"
