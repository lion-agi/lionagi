import unittest
from lionagi.os.collections.node.tree_node import TreeNode
from lionagi.os.collections.graph.tree import Tree


class TestTreeNode(unittest.TestCase):

    def setUp(self):
        self.tree_node1 = TreeNode()
        self.tree_node2 = TreeNode()
        self.tree_node3 = TreeNode()
        self.tree_node4 = TreeNode()
        self.tree = Tree()

    def test_initialization(self):
        self.assertIsNone(self.tree_node1.parent)
        self.assertEqual(self.tree_node1.children, [])
        self.assertIsInstance(self.tree_node1, TreeNode)
        self.assertIsInstance(self.tree_node1.ln_id, str)

    def test_relate_child(self):
        self.tree_node1.relate_child([self.tree_node2, self.tree_node3])
        self.assertIn(self.tree_node2.ln_id, self.tree_node1.children)
        self.assertIn(self.tree_node3.ln_id, self.tree_node1.children)
        self.assertEqual(self.tree_node2.parent, self.tree_node1)
        self.assertEqual(self.tree_node3.parent, self.tree_node1)

    def test_relate_parent(self):
        self.tree_node1.relate_parent(self.tree_node4)
        self.assertEqual(self.tree_node1.parent, self.tree_node4)
        self.assertIn(self.tree_node1.ln_id, self.tree_node4.children)

    def test_unrelate_parent(self):
        self.tree_node1.relate_parent(self.tree_node4)
        self.tree_node1.unrelate_parent()
        self.assertIsNone(self.tree_node1.parent)

    def test_unrelate_child(self):
        self.tree_node1.relate_child([self.tree_node2, self.tree_node3])
        self.tree_node1.unrelate_child([self.tree_node2, self.tree_node3])
        self.assertNotIn(self.tree_node2.ln_id, self.tree_node1.children)
        self.assertNotIn(self.tree_node3.ln_id, self.tree_node1.children)
        self.assertIsNone(self.tree_node2.parent)
        self.assertIsNone(self.tree_node3.parent)

    def test_tree_integration(self):
        self.tree.relate_parent_child(
            self.tree_node1, [self.tree_node2, self.tree_node3, self.tree_node4]
        )
        self.assertEqual(len(self.tree.internal_nodes), 4)
        self.assertEqual(len(self.tree_node1.children), 3)
        self.assertEqual(self.tree.root, self.tree_node1)

    def test_tree_node_edges(self):
        self.tree_node1.relate_child([self.tree_node2, self.tree_node3])
        df = self.tree_node1.edges.to_df()
        self.assertEqual(len(df), 2)
        self.assertIn(self.tree_node2.ln_id, df["tail"].values)
        self.assertIn(self.tree_node3.ln_id, df["tail"].values)

    def test_tree_display(self):
        # This test is mainly to check if the display function runs without errors
        self.tree.relate_parent_child(
            self.tree_node1, [self.tree_node2, self.tree_node3, self.tree_node4]
        )
        try:
            self.tree.display()
        except Exception as e:
            self.fail(f"Tree display method raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
