from lionagi.core.schema.base_node import *
import json
import xml.etree.ElementTree as ET
import unittest

class TestBaseComponent(unittest.TestCase):

    def setUp(self):
        self.component = BaseComponent(metadata={"initial_key": "initial_value"})

    def test_default_id_generation(self):
        component = BaseComponent()
        self.assertIsNotNone(component.id_)
        self.assertIsInstance(component.id_, str)

    def test_metadata_default_factory(self):
        component = BaseComponent()
        self.assertEqual(component.metadata, {})

    # def test_content_field_validation(self):
    #     # Assuming AliasChoices correctly handles aliasing, this test aims to confirm that
    #     valid_content = 'Test content'
    #     component = BaseComponent(content=valid_content)
    #     self.assertEqual(component.content, valid_content)

    def test_json_serialization(self):
        """Test that an object is correctly serialized to JSON."""
        component = BaseComponent(metadata={"key": "value"})
        component_json = component.to_json_string()

        # Convert JSON string back to a dictionary to check values
        component_dict = json.loads(component_json)

        # Assuming 'id_' and 'timestamp' are automatically generated and thus not predictable
        self.assertIn("node_id", component_dict)
        self.assertIn("timestamp", component_dict)
        self.assertEqual(component_dict["meta"], {"key": "value"})

    def test_from_json_valid_data(self):
        """Test object creation from valid JSON string."""
        json_str = '{"node_id": "test_id123", "timestamp": "2021-01-01T00:00:00", "meta": {"key": "value"}}'
        component = BaseComponent.from_json(json_str)

        self.assertEqual(component.id_, "test_id123")
        self.assertEqual(component.timestamp, "2021-01-01T00:00:00")
        self.assertEqual(component.metadata, {"key": "value"})

    def test_dictionary_serialization(self):
        """Test that an object is correctly serialized to a dictionary."""
        component = BaseComponent(metadata={"key": "value"})
        component_dict = component.to_dict()

        # Check if the keys and values are correctly serialized
        self.assertIn("node_id", component_dict)
        self.assertIn("timestamp", component_dict)
        self.assertEqual(component_dict["meta"], {"key": "value"})

    def test_from_dict_valid_data(self):
        """Test object creation from a valid dictionary."""
        dict_data = {"node_id": "test_id123", "timestamp": "2021-01-01T00:00:00", "meta": {"key": "value"}}
        component = BaseComponent.from_dict(dict_data)

        self.assertEqual(component.id_, "test_id123")
        self.assertEqual(component.timestamp, "2021-01-01T00:00:00")
        self.assertEqual(component.metadata, {"key": "value"})

    def test_deserialization_with_extra_fields(self):
        """Test deserialization from a dictionary with extra fields."""
        dict_data = {
            "node_id": "test_id123",
            "timestamp": "2021-01-01T00:00:00",
            "meta": {"key": "value"},
            "extra_field": "extra_value"
        }
        component = BaseComponent.from_dict(dict_data)

        # Verify the extra field is ignored or handled according to the class Config
        self.assertEqual(component.id_, "test_id123")
        self.assertTrue(hasattr(component, 'extra_field') == ('allow' in BaseComponent.Config.extra))

    def test_xml_serialization(self):
        """Test that an object is correctly serialized to XML."""
        metadata = {"key": "value", "nested": {"subkey": "subvalue"}}
        component = BaseComponent(metadata=metadata)
        component_xml = component.to_xml()

        # Parse the XML to verify its structure and contents
        root = ET.fromstring(component_xml)

        self.assertEqual(root.tag, component.__class__.__name__)
        self.assertTrue(any(child.tag == "meta" and child.text is None for child in root))

        # Verifying nested metadata serialization
        for meta in root.findall('meta'):
            for child in meta:
                if child.tag == "nested":
                    self.assertTrue(any(subchild.tag == "subkey" and subchild.text == "subvalue" for subchild in child))

    # def test_xml_deserialization_valid_data(self):
    #     """Test object creation from a valid XML string."""
    #     xml_str = '<BaseComponent><node_id>test_id123</node_id><timestamp>2021-01-01T00:00:00</timestamp><meta><key>value</key></meta></BaseComponent>'
    #     component = BaseComponent.from_xml(xml_str)
    #
    #     self.assertEqual(component.id_, "test_id123")
    #     self.assertEqual(component.timestamp, "2021-01-01T00:00:00")
    #     self.assertEqual(component.metadata, {"key": "value"})

    def test_conversion_to_pandas_series(self):
        """Test converting an instance to a Pandas Series."""
        metadata = {"key": "value"}
        component = BaseComponent(metadata=metadata)
        series = component.to_pd_series()

        self.assertIsInstance(series, pd.Series)
        # Check for specific fields in the series; adjust according to your class
        self.assertEqual(series["meta"], metadata)
        self.assertIn("node_id", series.index)
        self.assertIn("timestamp", series.index)

    def test_initialization_from_pandas_series(self):
        """Test initializing an instance from a Pandas Series."""
        data = {
            "node_id": "test_id",
            "timestamp": "2021-01-01T00:00:00",
            "meta": {"key": "value"}
        }
        series = pd.Series(data)
        component = BaseComponent.from_pd_series(series)

        self.assertEqual(component.id_, "test_id")
        self.assertEqual(component.timestamp, "2021-01-01T00:00:00")
        self.assertEqual(component.metadata, {"key": "value"})

    def test_has_metadata_key(self):
        """Test checking the existence of a metadata key."""
        self.assertTrue(self.component.has_meta_key("initial_key"))
        self.assertFalse(self.component.has_meta_key("nonexistent_key"))

    def test_metadata_addition_and_retrieval(self):
        """Test adding and retrieving metadata."""
        self.component.metadata["new_key"] = "new_value"
        self.assertEqual(self.component.meta_get("new_key"), "new_value")

    def test_metadata_key_renaming(self):
        """Test renaming an existing metadata key."""
        self.assertTrue(self.component.meta_change_key("initial_key", "renamed_key"))
        self.assertIn("renamed_key", self.component.metadata)
        self.assertNotIn("initial_key", self.component.metadata)

    def test_removing_metadata(self):
        """Test removing metadata."""
        value = self.component.meta_pop("initial_key")
        self.assertEqual(value, "initial_value")
        self.assertNotIn("initial_key", self.component.metadata)

    def test_merging_metadata(self):
        """Test merging additional metadata."""
        self.component.meta_merge({"added_key": "added_value"}, overwrite=False)
        self.assertEqual(self.component.metadata, {"initial_key": "initial_value", "added_key": "added_value"})
        self.component.meta_merge({"initial_key": "new_value"}, overwrite=True)
        self.assertEqual(self.component.metadata["initial_key"], "new_value")

    def test_clearing_metadata(self):
        """Test clearing all metadata."""
        self.component.meta_clear()
        self.assertEqual(self.component.metadata, {})

    def test_filtering_metadata(self):
        """Test filtering metadata with a predicate function."""
        self.component.meta_merge({"number": 10, "text": "string"})
        filtered = self.component.meta_filter(lambda x: isinstance(x, int))
        self.assertEqual(filtered, {"number": 10})
        self.assertNotIn("text", filtered)

    def test_metadata_validation(self):
        """Test validating metadata against a schema."""
        self.component.metadata = {"number": 10, "text": "string"}
        schema = {"number": int, "text": str}
        self.assertTrue(self.component.meta_validate(schema))

    def test_class_name_retrieval(self):
        """Ensure class_name() returns the correct class name."""
        self.assertEqual(BaseComponent.class_name(), "BaseComponent")

    def test_instance_copying(self):
        """Test copying of an instance."""
        original = BaseComponent(metadata={"key": "value"})
        cloned = original.copy(deep=True)

        # Ensure the cloned instance is not the same as the original
        self.assertIsNot(original, cloned)
        # Verify that the cloned instance has the same metadata as the original
        self.assertEqual(cloned.metadata, original.metadata)

        # Modify the original instance and ensure the cloned instance is unaffected
        original.metadata["key"] = "new_value"
        self.assertNotEqual(cloned.metadata["key"], original.metadata["key"])

    def test_from_dict_with_invalid_type(self):
        """Test from_dict method with invalid type for an attribute."""
        invalid_data = {"node_id": 123, "metadata": {"key": "value"}}  # node_id should be a string
        with self.assertRaises(ValidationError):
            BaseComponent.from_dict(invalid_data)

class TestBaseNode(unittest.TestCase):
    def test_content_initialization(self):
        """Test various types of content during initialization."""
        text_content = "This is a text content."
        dict_content = {"key": "value"}
        none_content = None

        text_node = BaseNode(content=text_content)
        dict_node = BaseNode(content=dict_content)
        none_node = BaseNode(content=none_content)

        self.assertEqual(text_node.content, text_content)
        self.assertEqual(dict_node.content, dict_content)
        self.assertIsNone(none_node.content)

    def test_content_assignment(self):
        """Test updating content with various types."""
        node = BaseNode()
        node.content = "New text content."
        self.assertEqual(node.content, "New text content.")

        node.content = {"new_key": "new_value"}
        self.assertEqual(node.content, {"new_key": "new_value"})

    def test_content_str_serialization(self):
        """Test the content_str property for different content types."""
        text_node = BaseNode(content="Text content")
        dict_node = BaseNode(content={"key": "value"})

        self.assertEqual(text_node.content_str, "Text content")
        self.assertEqual(dict_node.content_str, '{"key": "value"}')

    def test_string_representation(self):
        """Test the custom string representation of the instance."""
        node = BaseNode(content="A" * 60, metadata={"meta_key": "meta_value"})
        node_str = str(node)

        self.assertTrue(node_str.startswith("BaseNode("))
        self.assertIn("...", node_str)

    def test_inheritance_integrity_metadata(self):
        """Ensure inherited metadata functionality works correctly."""
        node = BaseNode(metadata={"inherited": "true"})
        self.assertTrue(node.has_meta_key("inherited"))

class TestBaseRelatableNode(unittest.TestCase):

    def test_add_related_node(self):
        """Test adding unique and duplicate node IDs."""
        relatable_node = BaseRelatableNode()
        result_add_first = relatable_node.add_related_node("node_1")
        result_add_duplicate = relatable_node.add_related_node("node_1")  # Attempt to add duplicate

        self.assertTrue(result_add_first)
        self.assertFalse(result_add_duplicate)
        self.assertEqual(len(relatable_node.related_nodes), 1)
        self.assertIn("node_1", relatable_node.related_nodes)

    def test_remove_related_node(self):
        """Test removing existing and non-existing node IDs."""
        relatable_node = BaseRelatableNode(related_nodes=["node_1"])
        result_remove_existing = relatable_node.remove_related_node("node_1")
        result_remove_non_existing = relatable_node.remove_related_node("node_2")  # Attempt to remove non-existing

        self.assertTrue(result_remove_existing)
        self.assertFalse(result_remove_non_existing)
        self.assertEqual(len(relatable_node.related_nodes), 0)

    def test_initialization_with_defaults(self):
        """Test the default initialization of related_nodes and label."""
        relatable_node = BaseRelatableNode()
        self.assertEqual(relatable_node.related_nodes, [])
        self.assertIsNone(relatable_node.label)

    def test_label_assignment(self):
        """Test label assignment."""
        relatable_node = BaseRelatableNode()
        relatable_node.label = "New Label"
        self.assertEqual(relatable_node.label, "New Label")

class TestBaseActionNode(unittest.TestCase):
    def test_attributes_assignment(self):
        """Test assigning and accessing custom attributes."""

        def sample_function():
            return "Function Called"

        action_node = Tool(func=sample_function, schema_={'schema': 'schema example'})
        action_node.manual = "Manual Text"
        action_node.parser = "Parser Object"

        self.assertEqual(action_node.func, sample_function)
        self.assertEqual(action_node.manual, "Manual Text")
        self.assertEqual(action_node.parser, "Parser Object")

    def test_serialize_func(self):
        """Test the serialization of the func attribute."""

        def test_func():
            pass

        action_node = Tool(func=test_func, schema_={'schema': 'schema example'})
        serialized_func_name = action_node.serialize_func(action_node.func)

        self.assertEqual(serialized_func_name, "test_func")


if __name__ == '__main__':
    unittest.main()
