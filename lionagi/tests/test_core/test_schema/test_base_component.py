import unittest
from unittest.mock import patch
import pandas as pd
from pydantic import ValidationError
from lionagi.core.schema.base_component import BaseComponent

class TestBaseComponent(unittest.TestCase):
    def setUp(self):
        self.component = BaseComponent(content="test content", metadata={"key": "value"})
        
    def test_to_json_str(self):
        json_str = self.component.to_json_str()
        self.assertIsInstance(json_str, str)
        self.assertIn("test content", json_str)
        self.assertIn('{"key":"value"}', json_str)

    def test_to_dict(self):
        dict_repr = self.component.to_dict()
        self.assertIsInstance(dict_repr, dict)
        self.assertEqual(dict_repr["content"], "test content")
        self.assertEqual(dict_repr["meta"], {"key": "value"})

    def test_to_xml(self):
        xml_str = self.component.to_xml()
        self.assertIsInstance(xml_str, str)
        self.assertIn("<BaseComponent>", xml_str)
        self.assertIn("<content>test content</content>", xml_str)
        self.assertIn("<meta><key>value</key></meta>", xml_str)

    def test_to_pd_series(self):
        series = self.component.to_pd_series()
        self.assertIsInstance(series, pd.Series)
        self.assertEqual(series["content"], "test content")
        self.assertEqual(series["meta"], {"key": "value"})

    def test_from_obj_dict(self):
        obj = {"content": "test", "meta": {"key": "value"}}
        component = BaseComponent.from_obj(obj)
        self.assertIsInstance(component, BaseComponent)
        self.assertEqual(component.content, "test")
        self.assertEqual(component.metadata, {"key": "value"})

    def test_from_obj_str(self):
        json_str = '{"content": "test", "meta": {"key": "value"}}'
        component = BaseComponent.from_obj(json_str)
        self.assertIsInstance(component, BaseComponent)
        self.assertEqual(component.content, "test")
        self.assertEqual(component.metadata, {"key": "value"})

    def test_from_obj_str_fuzzy_parse(self):
        json_str = '{"content": "test", "meta": {"key": "value"}}'
        component = BaseComponent.from_obj(json_str, fuzzy_parse=True)
        self.assertIsInstance(component, BaseComponent)
        self.assertEqual(component.content, "test")
        self.assertEqual(component.metadata, {"key": "value"})

    def test_from_obj_str_invalid_json(self):
        json_str = "invalid json"
        with self.assertRaises(ValueError):
            BaseComponent.from_obj(json_str)

    def test_from_obj_list(self):
        obj_list = [{"content": "test1"}, {"content": "test2"}]
        components = BaseComponent.from_obj(obj_list)
        self.assertIsInstance(components, list)
        self.assertEqual(len(components), 2)
        self.assertIsInstance(components[0], BaseComponent)
        self.assertEqual(components[0].content, "test1")
        self.assertEqual(components[1].content, "test2")

    def test_from_obj_pd_series(self):
        series = pd.Series({"content": "test", "meta": {"key": "value"}})
        component = BaseComponent.from_obj(series)
        self.assertIsInstance(component, BaseComponent)
        self.assertEqual(component.content, "test")
        self.assertEqual(component.metadata, {"key": "value"})

    def test_from_obj_pd_dataframe(self):
        df = pd.DataFrame([{"content": "test1"}, {"content": "test2"}])
        components = BaseComponent.from_obj(df)
        self.assertIsInstance(components, list)
        self.assertEqual(len(components), 2)
        self.assertIsInstance(components[0], BaseComponent)
        self.assertEqual(components[0].content, "test1")
        self.assertEqual(components[1].content, "test2")

    def test_from_obj_base_model(self):
        obj = BaseComponent(content="test", metadata={"key": "value"})
        component = BaseComponent.from_obj(obj.to_dict())
        self.assertIsInstance(component, BaseComponent)
        self.assertEqual(component.content, "test")
        self.assertEqual(component.metadata, {"key": "value"})

    def test_meta_keys(self):
        keys = self.component.meta_keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(keys, ["key"])

    def test_meta_keys_flattened(self):
        self.component.metadata = {"key1": {"nested": "value"}, "key2": "value2"}
        keys = self.component.meta_keys(flattened=True, sep="_")
        self.assertIsInstance(keys, list)
        self.assertEqual(keys, ["key1_nested", "key2"])

    def test_meta_has_key(self):
        self.assertTrue(self.component.meta_has_key("key"))
        self.assertFalse(self.component.meta_has_key("invalid"))

    def test_meta_has_key_flattened(self):
        self.component.metadata = {"key1": {"nested": "value"}, "key2": "value2"}
        self.assertTrue(self.component.meta_has_key("key1_nested", flattened=True))
        self.assertFalse(self.component.meta_has_key("key1_invalid", flattened=True))

    def test_meta_get(self):
        value = self.component.meta_get("key")
        self.assertEqual(value, "value")

    def test_meta_get_default(self):
        value = self.component.meta_get("invalid", default="default")
        self.assertEqual(value, "default")

    def test_meta_get_indices(self):
        self.component.metadata = {"key": ["value1", "value2"]}
        value = self.component.meta_get(indices=["key", 1], default=None)
        self.assertEqual(value, "value2")

    def test_meta_change_key(self):
        self.component.metadata = {"old_key": "value"}
        changed = self.component.meta_change_key("old_key", "new_key")
        self.assertTrue(changed)
        self.assertIn("new_key", self.component.metadata)
        self.assertNotIn("old_key", self.component.metadata)

    def test_meta_change_key_invalid(self):
        changed = self.component.meta_change_key("invalid", "new_key")
        self.assertFalse(changed)
        self.assertNotIn("new_key", self.component.metadata)

    def test_meta_insert(self):
        self.component.metadata = {"key": {"nested": "value"}}
        inserted = self.component.meta_insert(["key", "new_key"], "new_value")
        self.assertTrue(inserted)
        self.assertEqual(self.component.metadata["key"]["new_key"], "new_value")

    def test_meta_pop(self):
        self.component.metadata = {"key": "value"}
        value = self.component.meta_pop("key")
        self.assertEqual(value, "value")
        self.assertNotIn("key", self.component.metadata)

    def test_meta_pop_default(self):
        value = self.component.meta_pop("invalid", default="default")
        self.assertEqual(value, "default")

    def test_meta_merge(self):
        self.component.metadata = {"key1": "value1"}
        additional_metadata = {"key2": "value2"}
        self.component.meta_merge(additional_metadata)
        self.assertEqual(self.component.metadata, {"key1": "value1", "key2": "value2"})

    def test_meta_merge_overwrite(self):
        self.component.metadata = {"key": "value1"}
        additional_metadata = {"key": "value2"}
        self.component.meta_merge(additional_metadata, overwrite=True)
        self.assertEqual(self.component.metadata, {"key": "value2"})

    def test_meta_clear(self):
        self.component.metadata = {"key": "value"}
        self.component.meta_clear()
        self.assertEqual(self.component.metadata, {})

    def test_meta_filter(self):
        self.component.metadata = {"key1": 1, "key2": 2, "key3": 3}
        filtered_metadata = self.component.meta_filter(lambda item: item[1] > 1)
        self.assertEqual(filtered_metadata, {"key2": 2, "key3": 3})

    def test_class_name(self):
        class_name = BaseComponent.class_name()
        self.assertEqual(class_name, "BaseComponent")

    def test_property_schema(self):
        schema = self.component.property_schema
        self.assertIsInstance(schema, dict)
        self.assertIn("text", schema)
        self.assertIn("node_id", schema)
        self.assertIn("timestamp", schema)
        self.assertIn("meta", schema)
        self.assertIn("label", schema)

    def test_property_keys(self):
        keys = self.component.property_keys
        self.assertIsInstance(keys, list)
        self.assertIn("text", keys)
        self.assertIn("node_id", keys)
        self.assertIn("timestamp", keys)
        self.assertIn("meta", keys)
        self.assertIn("label", keys)

    def test_copy(self):
        copy = self.component.copy()
        self.assertIsInstance(copy, BaseComponent)
        self.assertEqual(copy.content, self.component.content)
        self.assertEqual(copy.metadata, self.component.metadata)
        self.assertIsNot(copy, self.component)

    def test_copy_update(self):
        copy = self.component.copy(update={"content": "updated content"})
        self.assertEqual(copy.content, "updated content")
        self.assertNotEqual(copy.content, self.component.content)

    def test_repr(self):
        repr_str = repr(self.component)
        self.assertIn("BaseComponent", repr_str)
        self.assertIn("content", repr_str)
        self.assertIn("meta", repr_str)


if __name__ == "__main__":
    unittest.main()