
from unittest.mock import patch, MagicMock
from pydantic import BaseModel, Field
from pandas import Series, DataFrame
from lionagi.core.generic.component import *


class TestBaseNode(unittest.TestCase):
    def setUp(self):
        self.node = BaseNode(
            id_="test_id",
            timestamp="2023-06-08T10:00:00",
            content="Test content",
            metadata={"key1": "value1", "key2": {"nested_key": "nested_value"}},
        )

    def test_class_name(self):
        self.assertEqual(self.node.class_name(), "BaseNode")

    def test_field_annotations(self):
        annotations = self.node._field_annotations
        self.assertEqual(annotations["id_"], ["str"])
        self.assertEqual(annotations["timestamp"], ["str"])
        self.assertEqual(annotations["content"], ['typing.any', 'none'])
        self.assertEqual(annotations["metadata"], ["dict"])

    def test_get_field_attr(self):
        self.assertEqual(self.node._get_field_attr("id_", "description"), "A 32-char unique hash identifier for the node.")

    def test_get_field_annotation(self):
        self.assertEqual(self.node._get_field_annotation("id_"), {"id_": ["str"]})
        self.assertEqual(self.node._get_field_annotation(["id_", "timestamp"]), {"id_": ["str"], "timestamp": ["str"]})
        with self.assertRaises(TypeError):
            self.node._get_field_annotation(123)

    def test_field_has_attr(self):
        self.assertTrue(self.node._field_has_attr("id_", "description"))
        self.assertFalse(self.node._field_has_attr("id_", "non_existent_attr"))

    def test_to_json_str(self):
        json_str = self.node.to_json_str()
        self.assertIsInstance(json_str, str)
        self.assertIn('"id_":"test_id"', json_str)
        self.assertIn('"timestamp":"2023-06-08T10:00:00"', json_str)
        self.assertIn('"content":"Test content"', json_str)
        self.assertIn('"meta":{"key1":"value1","key2":{"nested_key":"nested_value"}}', json_str)

    def test_to_dict(self):
        dict_data = self.node.to_dict()
        self.assertIsInstance(dict_data, dict)
        self.assertEqual(dict_data["id_"], "test_id")
        self.assertEqual(dict_data["timestamp"], "2023-06-08T10:00:00")
        self.assertEqual(dict_data["content"], "Test content")
        self.assertEqual(dict_data["meta"], {"key1": "value1", "key2": {"nested_key": "nested_value"}})

    def test_to_xml(self):
        xml_str = self.node.to_xml()
        self.assertIsInstance(xml_str, str)
        self.assertIn("<BaseNode>", xml_str)
        self.assertIn("<id_>test_id</id_>", xml_str)
        self.assertIn("<timestamp>2023-06-08T10:00:00</timestamp>", xml_str)
        self.assertIn("<content>Test content</content>", xml_str)
        self.assertIn("<meta>", xml_str)
        self.assertIn("<key1>value1</key1>", xml_str)
        self.assertIn("<key2>", xml_str)
        self.assertIn("<nested_key>nested_value</nested_key>", xml_str)
        self.assertIn("</key2>", xml_str)
        self.assertIn("</meta>", xml_str)
        self.assertIn("</BaseNode>", xml_str)

    def test_to_pd_series(self):
        series = self.node.to_pd_series()
        self.assertIsInstance(series, Series)
        self.assertEqual(series["id_"], "test_id")
        self.assertEqual(series["timestamp"], "2023-06-08T10:00:00")
        self.assertEqual(series["content"], "Test content")
        self.assertEqual(series["meta"], {"key1": "value1", "key2": {"nested_key": "nested_value"}})

    def test_from_obj_dict(self):
        dict_data = {
            "id_": "dict_id",
            "timestamp": "2023-06-08T11:00:00",
            "content": "Dict content",
            "metadata": {"dict_key": "dict_value"},
        }
        node = BaseNode.from_obj(dict_data)
        self.assertIsInstance(node, BaseNode)
        self.assertEqual(node.id_, "dict_id")
        self.assertEqual(node.timestamp, "2023-06-08T11:00:00")
        self.assertEqual(node.content, "Dict content")
        self.assertEqual(node.metadata, {"dict_key": "dict_value"})

    def test_from_obj_str(self):
        json_str = '{"id_": "json_id", "timestamp": "2023-06-08T12:00:00", "content": "JSON content", "metadata": {"json_key": "json_value"}}'
        node = BaseNode.from_obj(json_str)
        self.assertIsInstance(node, BaseNode)
        self.assertEqual(node.id_, "json_id")
        self.assertEqual(node.timestamp, "2023-06-08T12:00:00")
        self.assertEqual(node.content, "JSON content")
        self.assertEqual(node.metadata, {"json_key": "json_value"})

    @patch("lionagi.libs.ParseUtil.fuzzy_parse_json")
    def test_from_obj_str_fuzzy_parse(self, mock_fuzzy_parse):
        fuzzy_str = "id_: fuzzy_id, timestamp: '2023-06-08T13:00:00', content: 'Fuzzy content', metadata: {fuzzy_key: 'fuzzy_value'}"
        mock_fuzzy_parse.return_value = {
            "id_": "fuzzy_id",
            "timestamp": "2023-06-08T13:00:00",
            "content": "Fuzzy content",
            "metadata": {"fuzzy_key": "fuzzy_value"},
        }
        node = BaseNode.from_obj(fuzzy_str, fuzzy_parse=True)
        self.assertIsInstance(node, BaseNode)
        self.assertEqual(node.id_, "fuzzy_id")
        self.assertEqual(node.timestamp, "2023-06-08T13:00:00")
        self.assertEqual(node.content, "Fuzzy content")
        self.assertEqual(node.metadata, {"fuzzy_key": "fuzzy_value"})
        mock_fuzzy_parse.assert_called_once_with(fuzzy_str)

    def test_from_obj_list(self):
        list_data = [
            {"id_": "list_id1", "timestamp": "2023-06-08T14:00:00", "content": "List content 1", "metadata": {"list_key1": "list_value1"}},
            {"id_": "list_id2", "timestamp": "2023-06-08T15:00:00", "content": "List content 2", "metadata": {"list_key2": "list_value2"}},
        ]
        nodes = BaseNode.from_obj(list_data)
        self.assertIsInstance(nodes, list)
        self.assertEqual(len(nodes), 2)
        self.assertIsInstance(nodes[0], BaseNode)
        self.assertIsInstance(nodes[1], BaseNode)
        self.assertEqual(nodes[0].id_, "list_id1")
        self.assertEqual(nodes[1].id_, "list_id2")

    def test_from_obj_series(self):
        series_data = Series({
            "id_": "series_id",
            "timestamp": "2023-06-08T16:00:00",
            "content": "Series content",
            "metadata": {"series_key": "series_value"},
        })
        node = BaseNode.from_obj(series_data)
        self.assertIsInstance(node, BaseNode)
        self.assertEqual(node.id_, "series_id")
        self.assertEqual(node.timestamp, "2023-06-08T16:00:00")
        self.assertEqual(node.content, "Series content")
        self.assertEqual(node.metadata, {"series_key": "series_value"})

    def test_from_obj_dataframe(self):
        df_data = DataFrame([
            {"id_": "df_id1", "timestamp": "2023-06-08T17:00:00", "content": "DF content 1", "metadata": {"df_key1": "df_value1"}},
            {"id_": "df_id2", "timestamp": "2023-06-08T18:00:00", "content": "DF content 2", "metadata": {"df_key2": "df_value2"}},
        ])
        nodes = BaseNode.from_obj(df_data)
        self.assertIsInstance(nodes, list)
        self.assertEqual(len(nodes), 2)
        self.assertIsInstance(nodes[0], BaseNode)
        self.assertIsInstance(nodes[1], BaseNode)
        self.assertEqual(nodes[0].id_, "df_id1")
        self.assertEqual(nodes[1].id_, "df_id2")

    def test_from_obj_base_model(self):
        class CustomModel(BaseModel):
            id_: str = Field(default_factory=lambda: "custom_model_id")
            timestamp: str = "2023-06-08T19:00:00"
            content: str = "Custom content"
            metadata: dict = {"custom_key": "custom_value"}

        custom_model = CustomModel()
        node = BaseNode.from_obj(custom_model)
        self.assertIsInstance(node, BaseNode)
        self.assertEqual(node.id_, "custom_model_id")
        self.assertEqual(node.timestamp, "2023-06-08T19:00:00")
        self.assertEqual(node.content, "Custom content")
        self.assertEqual(node.metadata, {"custom_key": "custom_value"})

    def test_from_obj_unsupported_type(self):
        with self.assertRaises(NotImplementedError):
            BaseNode.from_obj(123)

    def test_meta_get(self):
        self.assertEqual(self.node.meta_get("key1"), "value1")
        self.assertIsNone(self.node.meta_get("non_existent_key"))
        self.assertEqual(self.node.meta_get("non_existent_key", default="default_value"), "default_value")

    def test_meta_change_key(self):
        self.assertTrue(self.node.meta_change_key("key1", "new_key1"))
        self.assertEqual(self.node.metadata, {"new_key1": "value1", "key2": {"nested_key": "nested_value"}})
        self.assertFalse(self.node.meta_change_key("non_existent_key", "new_key"))

    @patch("lionagi.libs.nested.ninsert")
    def test_meta_insert(self, mock_ninsert):
        mock_ninsert.return_value = True
        self.assertTrue(self.node.meta_insert("key3", "value3"))
        mock_ninsert.assert_called_once_with(self.node.metadata, "key3", "value3")

        mock_ninsert.reset_mock()
        mock_ninsert.return_value = True
        self.assertTrue(self.node.meta_insert(["key2", "new_nested_key"], "new_nested_value"))
        mock_ninsert.assert_called_once_with(self.node.metadata, ["key2", "new_nested_key"], "new_nested_value")

    @patch("lionagi.libs.nested.nmerge")
    def test_meta_merge(self, mock_nmerge):
        additional_metadata = {'key1': 'new_value1', 'key4': 'value4'}
        mock_nmerge.return_value = {"key1": "value1", "key2": {"nested_key": "nested_value"}, "key4": "value4"}
        self.node.meta_merge(additional_metadata)
        self.assertEqual(self.node.metadata, {"key1": "value1", "key2": {"nested_key": "nested_value"}, "key4": "value4"})

        mock_nmerge.reset_mock()
        mock_nmerge.return_value = {"key1": "new_value1", "key2": {"nested_key": "nested_value"}, "key4": "value4"}
        self.node.meta_merge(additional_metadata, overwrite=True)
        self.assertEqual(self.node.metadata, {"key1": "new_value1", "key2": {"nested_key": "nested_value"}, "key4": "value4"})

if __name__ == "__main__":
    unittest.main()
    
=======
from pydantic import BaseModel
from pandas import Series
import pandas as pd
from lionagi.core.generic.component import BaseNode


class TestBaseNode(unittest.TestCase):

    def test_basic_properties(self):
        node = BaseNode(content="Hello World")
        self.assertIsInstance(node.id_, str)
        self.assertEqual(len(node.id_), 32)
        self.assertEqual(node.content, "Hello World")
        self.assertEqual(node.metadata, {})

    def test_serialization_json(self):
        node = BaseNode(content="Hello World")
        self.assertIn("id_", node.to_json_str())

    def test_serialization_dict(self):
        node = BaseNode(content="Hello World")
        result = node.to_dict()
        self.assertIn("id_", result)
        self.assertEqual(result["content"], "Hello World")

    def test_serialization_xml(self):
        node = BaseNode(content="Hello World")
        xml_str = node.to_xml()
        self.assertIn("<BaseNode>", xml_str)
        self.assertIn("</BaseNode>", xml_str)

    def test_conversion_to_pandas_series(self):
        node = BaseNode(content="Hello World")
        series = node.to_pd_series()
        self.assertIsInstance(series, Series)
        self.assertEqual(series["content"], "Hello World")

    def test_field_management(self):
        node = BaseNode(content="Hello World")
        node._add_field("new_field", annotation=str, default="default value")
        self.assertIn("new_field", node._field_annotations)
        self.assertEqual(getattr(node, "new_field", None), "default value")

    def test_creation_from_dict(self):
        data = {"a": 1, "b": 2}
        node = BaseNode.from_obj(data)
        self.assertIn("a", node.to_dict())

    def test_creation_from_json_str(self):
        json_str = '{"a": 1, "b": 2}'
        node = BaseNode.from_obj(json_str)
        self.assertIn("a", node.to_dict())

    def test_creation_from_fuzzy_json_str(self):
        json_str = '{"name": "John", "age": 30, "city": ["New York", "DC", "LA"]'
        node = BaseNode.from_obj(json_str, fuzzy_parse=True)
        self.assertIn("name", node.to_dict())

    def test_creation_from_pandas_series(self):
        series = pd.Series({"a": 1, "b": 2})
        node = BaseNode.from_obj(series)
        self.assertIn("a", node.to_dict())

    def test_creation_from_pandas_dataframe(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]}, index=["row1", "row2"])
        nodes = BaseNode.from_obj(df)
        self.assertIsInstance(nodes, list)
        self.assertEqual(len(nodes), 2)

    def test_creation_from_pydantic_model(self):
        class CustomModel(BaseModel):
            a: int
            b: str

        custom_model = CustomModel(a=1, b="hello")
        node = BaseNode.from_obj(custom_model)
        self.assertIn("a", node.to_dict())

    def test_metadata_manipulation(self):
        node = BaseNode()
        node.meta_insert("key", "value")
        self.assertEqual(node.metadata["key"], "value")
        node.meta_change_key("key", "new_key")
        self.assertIn("new_key", node.metadata)
        node.meta_merge({"additional_key": "additional_value"})
        self.assertIn("additional_key", node.metadata)


if __name__ == "__main__":
    unittest.main()
