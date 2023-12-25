# Writing and running unit tests for the BaseNode class
import unittest
import json

from lionagi.utils.node_util import BaseNode

def create_id():
    return "mocked_id"

class TestBaseNode(unittest.TestCase):
    def test_init(self):
        node = BaseNode()
        self.assertEqual(node.id_, "mocked_id")
        self.assertIsNone(node.label)
        self.assertIsNone(node.content)
        self.assertEqual(node.metadata, {})

    def test_class_name(self):
        self.assertEqual(BaseNode.class_name(), "BaseNode")

    def test_to_json(self):
        node = BaseNode()
        expected_json = json.dumps({"node_id": "mocked_id", "label": None, "content": None, "metadata": {}})
        self.assertEqual(node.to_json(), expected_json)

    def test_to_dict(self):
        node = BaseNode()
        expected_dict = {"node_id": "mocked_id", "label": None, "content": None, "metadata": {}}
        self.assertEqual(node.to_dict(), expected_dict)

    def test_from_json(self):
        json_str = json.dumps({"node_id": "mocked_id", "label": "TestLabel", "content": "TestContent", "metadata": {"key": "value"}})
        node = BaseNode.from_json(json_str)
        self.assertIsInstance(node, BaseNode)
        self.assertEqual(node.id_, "mocked_id")
        self.assertEqual(node.label, "TestLabel")
        self.assertEqual(node.content, "TestContent")
        self.assertEqual(node.metadata, {"key": "value"})

    def test_from_dict(self):
        dict_data = {"node_id": "mocked_id", "label": "TestLabel", "content": "TestContent", "metadata": {"key": "value"}}
        node = BaseNode.from_dict(dict_data)
        self.assertIsInstance(node, BaseNode)
        self.assertEqual(node.id_, "mocked_id")
        self.assertEqual(node.label, "TestLabel")
        self.assertEqual(node.content, "TestContent")
        self.assertEqual(node.metadata, {"key": "value"})

    def test_setters_and_getters(self):
        node = BaseNode()
        node.set_meta(key="value")
        node.set_content("New Content")
        node.set_id("new_id")

        self.assertEqual(node.get_meta(), {"key": "value"})
        self.assertEqual(node.get_content(), "New Content")
        self.assertEqual(node.get_id(), "new_id")

# Running the tests
unittest.main(argv=[''], exit=False)