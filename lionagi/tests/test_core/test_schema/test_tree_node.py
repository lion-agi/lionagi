import unittest
from unittest.mock import MagicMock, patch
from lionagi.core.schema.tree_node import TreeNode, TREE_LABEL, Edge

class TestTreeNode(unittest.TestCase):
    def setUp(self):
        self.node = TreeNode()
        self.parent_node = TreeNode()
        self.child_node1 = TreeNode()
        self.child_node2 = TreeNode()

    def test_parent_property(self):
        self.assertIsNone(self.node.parent)
        self.node.parent = self.parent_node
        self.assertEqual(self.node.parent, self.parent_node)

    def test_children_property(self):
        self.assertEqual(self.node.children, [])
        self.node.children = [self.child_node1.id_, self.child_node2.id_]
        self.assertEqual(self.node.children, [self.child_node1.id_, self.child_node2.id_])

    @patch.object(TreeNode, 'add_edge')
    def test_add_parent_success(self, mock_add_edge):
        self.node.add_parent(self.parent_node)
        mock_add_edge.assert_called_once_with(self.parent_node, label=TREE_LABEL.CHILD)
        self.assertEqual(self.node.parent, self.parent_node)

    @patch.object(TreeNode, 'add_edge', side_effect=Exception('Test Exception'))
    def test_add_parent_failure(self, mock_add_edge):
        with self.assertRaises(Exception):
            self.node.add_parent(self.parent_node)

    @patch.object(TreeNode, 'add_edge')
    def test_add_child_success(self, mock_add_edge):
        self.node.add_child(self.child_node1)
        mock_add_edge.assert_called_once_with(self.child_node1, label=TREE_LABEL.PARENT)
        self.assertIn(self.child_node1.id_, self.node.children)

    @patch.object(TreeNode, 'add_edge', side_effect=Exception('Test Exception'))
    def test_add_child_failure(self, mock_add_edge):
        with self.assertRaises(Exception):
            self.node.add_child(self.child_node1)
        self.assertNotIn(self.child_node1.id_, self.node.children)

    @patch.object(TreeNode, 'pop_edge')
    def test_remove_child(self, mock_pop_edge):
        self.node.children = [self.child_node1.id_]
        self.node.remove_child(self.child_node1)
        mock_pop_edge.assert_called_once_with(self.child_node1)
        self.assertNotIn(self.child_node1.id_, self.node.children)

    def test_has_child_true(self):
        self.node.out_relations = {self.child_node1.id_: MagicMock(spec=Edge, label=TREE_LABEL.PARENT)}
        result = self.node.has_child(self.child_node1)
        self.assertTrue(result)

    def test_has_child_false_wrong_label(self):
        self.node.out_relations = {self.child_node1.id_: MagicMock(spec=Edge, label="other_label")}
        result = self.node.has_child(self.child_node1)
        self.assertFalse(result)

    def test_has_child_false_not_in_relations(self):
        self.node.out_relations = {}
        result = self.node.has_child(self.child_node1)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()