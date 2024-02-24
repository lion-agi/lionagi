from lionagi.schema.base_node import *
import unittest

class TestBaseComponent(unittest.TestCase):

    def test_default_id_generation(self):
        component = BaseComponent()
        self.assertIsNotNone(component.id_)
        self.assertIsInstance(component.id_, str)

    def test_metadata_default_factory(self):
        component = BaseComponent()
        self.assertEqual(component.metadata, {})

    def test_content_field_validation(self):
        # Assuming AliasChoices correctly handles aliasing, this test aims to confirm that
        valid_content = 'Test content'
        component = BaseComponent(content=valid_content)
        self.assertEqual(component.content, valid_content)

    def test_has_metadata_key(self):
        node = BaseNode(metadata={"key1": "value1"})
        self.assertTrue(node.has_metadata_key("key1"))
        self.assertFalse(node.has_metadata_key("key2"))

    def test_get_metadata(self):
        node = BaseNode(metadata={"key1": "value1"})
        self.assertEqual(node.get_metadata("key1"), "value1")
        self.assertIsNone(node.get_metadata("key2"))
        self.assertEqual(node.get_metadata("key2", "default"), "default")

    def test_change_metadata_key(self):
        node = BaseNode(metadata={"key1": "value1"})
        node.change_metadata_key("key1", "key2")
        self.assertNotIn("key1", node.metadata)
        self.assertIn("key2", node.metadata)
        self.assertEqual(node.metadata["key2"], "value1")

    def test_merge_metadata(self):
        node = BaseNode(metadata={"key1": "value1"})
        node.merge_metadata({"key2": "value2"}, overwrite=False)
        self.assertEqual(node.metadata, {"key1": "value1", "key2": "value2"})
        node.merge_metadata({"key1": "new_value1"}, overwrite=True)
        self.assertEqual(node.metadata["key1"], "new_value1")

    def test_add_related_node(self):
        node = RelatableNode()
        self.assertTrue(node.add_related_node("node_1"))
        self.assertIn("node_1", node.related_nodes)
        self.assertFalse(node.add_related_node("node_1"))  # Adding again returns False

    def test_remove_related_node(self):
        node = RelatableNode(related_nodes=["node_1"])
        self.assertTrue(node.remove_related_node("node_1"))
        self.assertNotIn("node_1", node.related_nodes)
        self.assertFalse(node.remove_related_node("node_1"))  # Removing non-existent node returns False


if __name__ == '__main__':
    unittest.main()
