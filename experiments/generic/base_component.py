
    
import unittest
from unittest.mock import patch
import pandas as pd
from pydantic import ValidationError

import unittest
from unittest.mock import patch
import pandas as pd
from pydantic import ValidationError


class TestBaseComponent(unittest.TestCase):
    def setUp(self):
        self.component = BaseComponent(
            content="test content",
            metadata={"key": "value", "nested": {"key": "nested_value"}},
        )

    def test_to_json_str(self):
        json_str = self.component.to_json_str()
        self.assertIsInstance(json_str, str)
        self.assertIn("test content", json_str)
        self.assertIn('"key":"value"', json_str)
        self.assertIn('"nested":{"key":"nested_value"}', json_str)

    def test_to_dict(self):
        dict_repr = self.component.to_dict()
        self.assertIsInstance(dict_repr, dict)
        self.assertEqual(dict_repr["content"], "test content")
        self.assertEqual(dict_repr["meta"], {"key": "value", "nested": {"key": "nested_value"}})

    def test_to_xml(self):
        xml_str = self.component.to_xml()
        self.assertIsInstance(xml_str, str)
        self.assertIn("<BaseComponent>", xml_str)
        self.assertIn("<content>test content</content>", xml_str)
        self.assertIn("<meta><key>value</key><nested><key>nested_value</key></nested></meta>", xml_str)

    def test_to_pd_series(self):
        series = self.component.to_pd_series()
        self.assertIsInstance(series, pd.Series)
        self.assertEqual(series["content"], "test content")
        self.assertEqual(series["meta"], {"key": "value", "nested": {"key": "nested_value"}})

    def test_from_obj_dict(self):
        obj = {"content": "test", "meta": {"key": "value", "nested": {"key": "nested_value"}}}
        component = BaseComponent.from_obj(obj)
        self.assertIsInstance(component, BaseComponent)
        self.assertEqual(component.content, "test")
        self.assertEqual(component.metadata, {"key": "value", "nested": {"key": "nested_value"}})

    def test_from_obj_str(self):
        json_str = '{"content": "test", "meta": {"key": "value", "nested": {"key": "nested_value"}}}'
        component = BaseComponent.from_obj(json_str)
        self.assertIsInstance(component, BaseComponent)
        self.assertEqual(component.content, "test")
        self.assertEqual(component.metadata, {"key": "value", "nested": {"key": "nested_value"}})

    def test_from_obj_str_fuzzy_parse(self):
        json_str = "{'content': 'test', 'meta': {'key': 'value', 'nested': {'key': 'nested_value'}}}"
        component = BaseComponent.from_obj(json_str, fuzzy_parse=True)
        self.assertIsInstance(component, BaseComponent)
        self.assertEqual(component.content, "test")
        self.assertEqual(component.metadata, {"key": "value", "nested": {"key": "nested_value"}})

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

    def test_from_obj_list_with_metadata(self):
        obj_list = [{"content": "test1", "meta": {"key": "value1"}}, {"content": "test2", "meta": {"key": "value2"}}]
        components = BaseComponent.from_obj(obj_list)
        self.assertIsInstance(components, list)
        self.assertEqual(len(components), 2)
        self.assertIsInstance(components[0], BaseComponent)
        self.assertEqual(components[0].content, "test1")
        self.assertEqual(components[0].metadata, {"key": "value1"})
        self.assertEqual(components[1].content, "test2")
        self.assertEqual(components[1].metadata, {"key": "value2"})

    def test_from_obj_pd_series(self):
        series = pd.Series({"content": "test", "meta": {"key": "value", "nested": {"key": "nested_value"}}})
        component = BaseComponent.from_obj(series)
        self.assertIsInstance(component, BaseComponent)
        self.assertEqual(component.content, "test")
        self.assertEqual(component.metadata, {"key": "value", "nested": {"key": "nested_value"}})

    def test_from_obj_pd_dataframe(self):
        df = pd.DataFrame([{"content": "test1", "meta": {"key": "value1"}}, {"content": "test2", "meta": {"key": "value2"}}])
        components = BaseComponent.from_obj(df)
        self.assertIsInstance(components, list)
        self.assertEqual(len(components), 2)
        self.assertIsInstance(components[0], BaseComponent)
        self.assertEqual(components[0].content, "test1")
        self.assertEqual(components[0].metadata, {"key": "value1"})
        self.assertEqual(components[1].content, "test2")
        self.assertEqual(components[1].metadata, {"key": "value2"})

    def test_from_obj_base_model(self):
        obj = BaseComponent(content="test", metadata={"key": "value", "nested": {"key": "nested_value"}})
        component = BaseComponent.from_obj(obj)
        self.assertIsInstance(component, BaseComponent)
        self.assertEqual(component.content, "test")
        self.assertEqual(component.metadata, {"key": "value", "nested": {"key": "nested_value"}})

    def test_from_obj_unsupported_type(self):
        with self.assertRaises(NotImplementedError):
            BaseComponent.from_obj(123)

    def test_meta_keys(self):
        keys = self.component.meta_keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(keys, ["key", "nested"])

    def test_meta_keys_flattened(self):
        keys = self.component.meta_keys(flattened=True)
        self.assertIsInstance(keys, list)
        self.assertEqual(keys, ["key", "nested_key"])

    def test_meta_keys_flattened_custom_separator(self):
        keys = self.component.meta_keys(flattened=True, sep="_")
        self.assertIsInstance(keys, list)
        self.assertEqual(keys, ["key", "nested_key"])

    def test_meta_has_key(self):
        self.assertTrue(self.component.meta_has_key("key"))
        self.assertTrue(self.component.meta_has_key("nested"))
        self.assertFalse(self.component.meta_has_key("invalid"))

    def test_meta_has_key_flattened(self):
        self.assertTrue(self.component.meta_has_key("nested_key", flattened=True))
        self.assertFalse(self.component.meta_has_key("nested_invalid", flattened=True))

    def test_meta_get(self):
        value = self.component.meta_get("key")
        self.assertEqual(value, "value")

    def test_meta_get_nested(self):
        value = self.component.meta_get(indices=["nested", "key"])
        self.assertEqual(value, "nested_value")

    def test_meta_get_default(self):
        value = self.component.meta_get("invalid", default="default")
        self.assertEqual(value, "default")

    def test_meta_get_indices(self):
        self.component.metadata = {"key": ["value1", "value2"]}
        value = self.component.meta_get(indices=["key", 1])
        self.assertEqual(value, "value2")

    def test_meta_get_indices_default(self):
        value = self.component.meta_get(indices=["invalid", 0], default="default")
        self.assertEqual(value, "default")

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
        inserted = self.component.meta_insert(["nested", "new_key"], "new_value")
        self.assertTrue(inserted)
        self.assertEqual(self.component.metadata["nested"]["new_key"], "new_value")

    def test_meta_insert_invalid_key(self):
        try:
            self.component.meta_insert(["invalid", "key"], "value")
        except KeyError as e:
            self.assertIn("invalid", str(e))

    def test_meta_pop(self):
        value = self.component.meta_pop("key")
        self.assertEqual(value, "value")
        self.assertNotIn("key", self.component.metadata)

    def test_meta_pop_default(self):
        value = self.component.meta_pop("invalid", default="default")
        self.assertEqual(value, "default")

    def test_meta_merge(self):
        additional_metadata = {"new_key": "new_value", "nested": {"new_nested_key": "new_nested_value"}}
        self.component.meta_merge(additional_metadata)
        self.assertEqual(self.component.metadata["key"], "value")
        self.assertEqual(self.component.metadata["new_key"], "new_value")
        self.assertEqual(self.component.metadata["nested"]["key"], "nested_value")
        # self.assertEqual(self.component.metadata["nested"]["new_nested_key"], "new_nested_value")

    def test_meta_merge_overwrite(self):
        additional_metadata = {"key": "new_value", "nested": {"key": "new_nested_value"}}
        self.component.meta_merge(additional_metadata, overwrite=True)
        self.assertEqual(self.component.metadata["key"], "new_value")
        self.assertEqual(self.component.metadata["nested"]["key"], "new_nested_value")

    def test_meta_clear(self):
        self.component.meta_clear()
        self.assertEqual(self.component.metadata, {})

    def test_meta_filter(self):
        self.component.metadata = {"key1": 1, "key2": 2, "key3": 3}
        filtered_metadata = self.component.meta_filter(lambda item: item[1] > 1)
        self.assertEqual(filtered_metadata, {"key2": 2, "key3": 3})

    def test_meta_filter_empty(self):
        filtered_metadata = self.component.meta_filter(lambda item: False)
        self.assertEqual(filtered_metadata, {})

    def test_class_name(self):
        class_name = BaseComponent.class_name()
        self.assertEqual(class_name, "BaseComponent")

    def test_field_annotations(self):
        annotations = self.component.field_annotations
        self.assertIsInstance(annotations, dict)
        self.assertEqual(annotations["content"], ["str", "dict[str, typing.any]", "none", "typing.any"])
        self.assertEqual(annotations["id_"], ["str"])
        self.assertEqual(annotations["timestamp"], ["str"])
        self.assertEqual(annotations["metadata"], ["dict"])
        self.assertEqual(annotations["label"], ["str", "none"])

    def test_get_field_attr_default(self):
        default_value = self.component.get_field_attr("invalid", "description", default="default")
        self.assertEqual(default_value, "default")

    def test_get_field_attr_not_found(self):
        try:
            self.component.get_field_attr("invalid", "description")
        except Exception as e:
            self.assertIn("invalid", str(e))

    def test_field_has_attr(self):
        # self.assertTrue(self.component._field_has_attr("content", "validation_alias"))
        self.assertFalse(self.component._field_has_attr("content", "invalid_attr"))


    def test_repr(self):
        repr_str = repr(self.component)
        self.assertIn("BaseComponent", repr_str)
        self.assertIn("content", repr_str)
        self.assertIn("test content", repr_str)
        self.assertIn("meta", repr_str)
        self.assertIn("key", repr_str)
        self.assertIn("value", repr_str)
        self.assertIn("nested", repr_str)
        self.assertIn("nested_value", repr_str)

if __name__ == "__main__":
    unittest.main()