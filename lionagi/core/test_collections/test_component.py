import unittest
from lionagi.os.collections.abc.component import (
    Component,
    LionValueError,
    LionTypeError,
)
import pandas as pd
from datetime import datetime
import json


class TestComponent(unittest.TestCase):

    def setUp(self):
        """Set up a basic Component instance for testing."""
        self.component = Component()

    def test_initialization(self):
        """Test basic initialization and attributes."""
        self.assertIsInstance(self.component.ln_id, str)
        self.assertIsInstance(self.component.timestamp, str)
        self.assertIsInstance(self.component.metadata, dict)
        self.assertIsNone(self.component.content)
        self.assertEqual(self.component.embedding, [])

    def test_setting_attributes(self):
        """Test setting and updating attributes."""
        self.component.content = 1
        self.assertEqual(self.component.content, 1)
        self.assertIn("content", self.component.metadata["last_updated"])

    def test_class_name(self):
        """Test the class_name property."""
        self.assertEqual(self.component.class_name, "Component")

    def test_to_dict(self):
        """Test converting to dictionary."""
        self.component.content = "example content"
        dict_repr = self.component.to_dict()
        self.assertEqual(dict_repr["content"], "example content")
        self.assertEqual(dict_repr["lion_class"], "Component")

    def test_to_json_str(self):
        """Test converting to JSON string."""
        self.component.content = "example content"
        json_str = self.component.to_json_str()
        self.assertIn('"content": "example content"', json_str)

    def test_to_xml(self):
        """Test converting to XML string."""
        self.component.content = "example content"
        xml_str = self.component.to_xml()
        self.assertIn("<content>example content</content>", xml_str)

    def test_to_pd_series(self):
        """Test converting to Pandas Series."""
        self.component.content = "example content"
        series = self.component.to_pd_series()
        self.assertEqual(series["content"], "example content")

    def test_from_obj_dict(self):
        """Test creating a Component from a dictionary."""
        dict_obj = {"a": 1, "b": 2}
        new_component = Component.from_obj(dict_obj)
        self.assertEqual(new_component.metadata["a"], 1)
        self.assertEqual(new_component.metadata["b"], 2)

    def test_from_obj_str(self):
        """Test creating a Component from a JSON string."""
        json_str = '{"a": 1, "b": 2}'
        new_component = Component.from_obj(json_str)
        self.assertEqual(new_component.metadata["a"], 1)
        self.assertEqual(new_component.metadata["b"], 2)

    def test_from_obj_fuzzy_str(self):
        """Test creating a Component from a fuzzy JSON string."""
        fuzzy_json_str = '{"name": "John", "age": 30, "city": ["New York", "DC", "LA"]'
        new_component = Component.from_obj(fuzzy_json_str, fuzzy_parse=True)
        self.assertEqual(new_component.metadata["name"], "John")
        self.assertEqual(new_component.metadata["age"], 30)
        self.assertEqual(new_component.metadata["city"], ["New York", "DC", "LA"])

    def test_from_obj_series(self):
        """Test creating a Component from a Pandas Series."""
        series_obj = pd.Series({"a": 1, "b": 2})
        new_component = Component.from_obj(series_obj)
        self.assertEqual(new_component.metadata["a"], 1)
        self.assertEqual(new_component.metadata["b"], 2)

    def test_from_obj_dataframe(self):
        """Test creating Components from a Pandas DataFrame."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]}, index=["row1", "row2"])
        components = Component.from_obj(df)
        self.assertEqual(len(components), 2)
        self.assertEqual(components[0].metadata["a"], 1)
        self.assertEqual(components[0].metadata["b"], 3)
        self.assertEqual(components[1].metadata["a"], 2)
        self.assertEqual(components[1].metadata["b"], 4)

    def test_metadata_manipulation(self):
        """Test manipulation of metadata."""
        self.component._meta_insert(["new_key"], "new_value")
        self.assertEqual(self.component.metadata["new_key"], "new_value")
        self.component._meta_set(["new_key"], "updated_value")
        self.assertEqual(self.component.metadata["new_key"], "updated_value")
        nested_value = {"a": 1, "b": 2}
        self.component._meta_insert(["nested", 0], nested_value)
        self.assertEqual(self.component.metadata["nested"][0], nested_value)
        self.assertEqual(self.component._meta_get(["nested", 0, "a"]), 1)

    def test_invalid_metadata_assignment(self):
        """Test invalid direct assignment to metadata."""
        with self.assertRaises(AttributeError):
            self.component.metadata = {}

    def test_field_annotations(self):
        """Test field annotations."""
        annotations = self.component._field_annotations
        self.assertIn("ln_id", annotations)
        self.assertIn("timestamp", annotations)

    def test_dynamic_field_addition(self):
        """Test adding fields dynamically to the Component."""
        self.component._add_field(
            "welcome", str, default="new value", value="hello world again"
        )
        self.assertEqual(
            self.component._get_field_attr("welcome", "default"), "new value"
        )
        self.assertEqual(getattr(self.component, "welcome"), "hello world again")

    def test_validation_error_handling(self):
        """Test handling of validation errors."""
        with self.assertRaises(LionValueError):
            Component.from_obj({"ln_id": 12345})  # Invalid ln_id type

    def test_str_repr_methods(self):
        """Test __str__ and __repr__ methods."""
        self.component.content = "example content"
        self.assertIn("example content", str(self.component))
        self.assertIn("example content", repr(self.component))

    def test_embedded_content(self):
        """Test embedded content handling."""
        embedding_str = "[1.0, 2.0, 3.0]"
        self.component.embedding = self.component._validate_embedding(embedding_str)
        self.assertEqual(self.component.embedding, [1.0, 2.0, 3.0])

    def test_invalid_embedded_content(self):
        """Test invalid embedded content handling."""
        with self.assertRaises(ValueError):
            self.component._validate_embedding("[1.0, 'invalid', 3.0]")

    def test_timestamp_format(self):
        """Test if the timestamp is in the correct format."""
        timestamp = self.component.timestamp
        try:
            datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            self.fail("Timestamp is not in the correct format")

    def test_default_field_values(self):
        """Test the default values of fields."""
        default_fields = self.component._all_fields
        self.assertEqual(default_fields["embedding"].default, [])
        self.assertEqual(default_fields["metadata"].default_factory(), {})
        self.assertEqual(default_fields["extra_fields"].default_factory(), {})
        self.assertIsNone(default_fields["content"].default)

    def test_deeply_nested_metadata(self):
        """Test setting and getting deeply nested metadata."""
        nested_value = {"level1": {"level2": {"level3": "deep_value"}}}
        self.component._meta_insert(["nested", 0], nested_value)
        self.assertEqual(
            self.component._meta_get(["nested", 0, "level1", "level2", "level3"]),
            "deep_value",
        )

    def test_invalid_from_obj_type(self):
        """Test invalid type in from_obj method."""
        with self.assertRaises(LionTypeError):
            Component.from_obj(12345)  # Invalid type

    def test_from_obj_pydantic_model(self):
        """Test creating a Component from a Pydantic BaseModel."""
        from pydantic import BaseModel

        class SampleModel(BaseModel):
            name: str
            age: int

        sample_instance = SampleModel(name="John Doe", age=30)
        new_component = Component.from_obj(sample_instance)
        self.assertEqual(new_component.metadata["name"], "John Doe")
        self.assertEqual(new_component.metadata["age"], 30)

    def test_json_serialization_deserialization(self):
        """Test JSON serialization and deserialization."""
        original_dict = self.component.to_dict()
        json_str = json.dumps(original_dict)
        new_component = Component.from_obj(json_str)
        self.assertEqual(original_dict, new_component.to_dict())


if __name__ == "__main__":
    unittest.main()
