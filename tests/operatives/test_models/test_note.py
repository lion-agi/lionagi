"""Tests for Note class."""

import pytest

from lionagi.operatives.models.note import Note
from lionagi.utils import UNDEFINED


class TestNote:
    """Test suite for Note class."""

    def test_basic_initialization(self):
        """Test basic Note initialization."""
        note = Note(field1="value1", field2=123)

        assert note.content["field1"] == "value1"
        assert note.content["field2"] == 123

    def test_empty_initialization(self):
        """Test empty Note initialization."""
        note = Note()
        assert isinstance(note.content, dict)
        assert len(note.content) == 0

    def test_nested_content(self):
        """Test Note with nested content."""
        note = Note(
            field1={"nested1": "value1", "nested2": {"deep": "value2"}},
            field2=[1, 2, 3],
        )

        assert note.content["field1"]["nested1"] == "value1"
        assert note.content["field1"]["nested2"]["deep"] == "value2"
        assert note.content["field2"] == [1, 2, 3]

    def test_to_dict_method(self):
        """Test to_dict method."""
        data = {
            "field1": "value1",
            "field2": UNDEFINED,
            "field3": {"nested": "value2"},
        }
        note = Note(**data)

        result = note.to_dict()
        assert "field1" in result
        assert "field2" not in result  # UNDEFINED should be excluded
        assert result["field3"]["nested"] == "value2"

    def test_pop_method(self):
        """Test pop method with various indices."""
        note = Note(
            field1={"nested1": "value1", "nested2": "value2"}, field2=[1, 2, 3]
        )

        # Pop single level
        value = note.pop("field2")
        assert value == [1, 2, 3]
        assert "field2" not in note.content

        # Pop nested value
        value = note.pop(["field1", "nested1"])
        assert value == "value1"
        assert "nested1" not in note.content["field1"]

        # Pop with default
        value = note.pop("nonexistent", default="default")
        assert value == "default"

    def test_insert_method(self):
        """Test insert method."""
        note = Note()

        # Insert single level
        note.insert("field1", "value1")
        assert note.content["field1"] == "value1"

        # Insert nested
        note.insert(["nested", "deep"], "value2")
        assert note.content["nested"]["deep"] == "value2"

    def test_set_method(self):
        """Test set method."""
        note = Note(field1="initial")

        # Set existing value
        note.set("field1", "updated")
        assert note.content["field1"] == "updated"

        # Set new value
        note.set("field2", "new")
        assert note.content["field2"] == "new"

        # Set nested value
        note.set(["nested", "deep"], "value")
        assert note.content["nested"]["deep"] == "value"

    def test_get_method(self):
        """Test get method."""
        note = Note(field1="value1", nested={"deep": "value2"})

        # Get single level
        assert note.get("field1") == "value1"

        # Get nested
        assert note.get(["nested", "deep"]) == "value2"

        # Get with default
        assert note.get("nonexistent", default="default") == "default"

        # Get nested with default
        assert (
            note.get(["nested", "nonexistent"], default="default") == "default"
        )

    def test_keys_method(self):
        """Test keys method with flat and nested options."""
        note = Note(
            field1="value1",
            nested={"deep1": "value2", "deep2": {"deeper": "value3"}},
        )

        # Regular keys
        keys = note.keys()
        assert set(keys) == {"field1", "nested"}

        # Flat keys
        flat_keys = note.keys(flat=True)
        expected_keys = {
            ("field1",),
            ("nested", "deep1"),
            ("nested", "deep2", "deeper"),
        }
        assert set(flat_keys) == expected_keys

    def test_values_method(self):
        """Test values method with flat and nested options."""
        note = Note(field1="value1", nested={"deep": "value2"})

        # Regular values
        values = list(note.values())
        assert "value1" in values
        assert isinstance(values[1], dict)

        # Flat values
        flat_values = list(note.values(flat=True))
        assert set(flat_values) == {"value1", "value2"}

    def test_items_method(self):
        """Test items method with flat and nested options."""
        note = Note(field1="value1", nested={"deep": "value2"})

        # Regular items
        items = note.content
        assert items["field1"] == "value1"
        assert isinstance(items["nested"], dict)

        # Flat items
        flat_items = dict(note.items(flat=True))
        assert flat_items[("field1",)] == "value1"
        assert flat_items[("nested", "deep")] == "value2"

    def test_clear_method(self):
        """Test clear method."""
        note = Note(field1="value1", field2="value2")
        note.clear()

        assert len(note.content) == 0

    def test_update_method(self):
        """Test update method."""
        note = Note(field1="value1", nested={"deep": "value2"})

        # Update existing dict
        note.update(["nested"], {"new_deep": "value3"})
        assert note.content["nested"]["new_deep"] == "value3"
        assert note.content["nested"]["deep"] == "value2"

        # Update list
        note.update("list_field", [1, 2])
        note.update("list_field", [3, 4])
        assert note.content["list_field"] == [1, 2, 3, 4]

        # Update with Note instance
        other_note = Note(new_field="value4")
        note.update([], other_note)
        assert note.content["new_field"] == "value4"

    def test_special_methods(self):
        """Test special methods."""
        note = Note(field1="value1", field2="value2")

        # __contains__
        assert "field1" in note
        assert "nonexistent" not in note

        # __len__
        assert len(note) == 2

        # __iter__
        assert set(iter(note)) == {"field1", "field2"}

        # __str__ and __repr__
        assert str(note) == str(note.content)
        assert repr(note) == repr(note.content)

        # __getitem__
        assert note["field1"] == "value1"

        # __setitem__
        note["new_field"] = "value3"
        assert note.content["new_field"] == "value3"

    def test_from_dict_method(self):
        """Test from_dict class method."""
        data = {"field1": "value1", "nested": {"deep": "value2"}}

        note = Note.from_dict(data)
        assert note.content == data
        assert note.get(["nested", "deep"]) == "value2"

    def test_error_handling(self):
        """Test error handling."""
        note = Note()

        # Access non-existent nested path
        with pytest.raises(KeyError):
            note.pop(["nonexistent", "deep"])

    def test_nested_operations(self):
        """Test operations on deeply nested structures."""
        note = Note(level1={"level2": {"level3": {"value": "deep"}}})

        # Deep get
        assert note.get(["level1", "level2", "level3", "value"]) == "deep"

        # Deep set
        note.set(["level1", "level2", "new3", "value"], "new_deep")
        assert note.get(["level1", "level2", "new3", "value"]) == "new_deep"

        # Deep pop
        value = note.pop(["level1", "level2", "level3"])
        assert value == {"value": "deep"}
        assert "level3" not in note.content["level1"]["level2"]
