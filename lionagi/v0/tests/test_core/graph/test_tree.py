# TODO
# import unittest
# from lionagi.core.graph.tree import TreeNode, Tree
#
# class TestTreeNode(unittest.TestCase):
#     def setUp(self):
#         self.parent_node = TreeNode(id_="parent", content="Parent Node")
#         self.child_node1 = TreeNode(id_="child1", content="Child Node 1")
#         self.child_node2 = TreeNode(id_="child2", content="Child Node 2")
#
#     def test_relate_child(self):
#         self.parent_node.relate_child(self.child_node1)
#         self.assertIn("child1", self.parent_node.children)
#         self.assertEqual(self.child_node1.parent, self.parent_node)
#
#     def test_relate_children(self):
#         self.parent_node.relate_child([self.child_node1, self.child_node2])
#         self.assertIn("child1", self.parent_node.children)
#         self.assertIn("child2", self.parent_node.children)
#         self.assertEqual(self.child_node1.parent, self.parent_node)
#         self.assertEqual(self.child_node2.parent, self.parent_node)
#
#     def test_relate_parent(self):
#         self.child_node1.relate_parent(self.parent_node)
#         self.assertIn("child1", self.parent_node.children)
#         self.assertEqual(self.child_node1.parent, self.parent_node)
#
#     def test_unrelate_child(self):
#         self.parent_node.relate_child(self.child_node1)
#         self.parent_node.unrelate_child(self.child_node1)
#         self.assertNotIn("child1", self.parent_node.children)
#         self.assertIsNone(self.child_node1.parent)
#
#     def test_unrelate_parent(self):
#         self.child_node1.relate_parent(self.parent_node)
#         self.child_node1.unrelate_parent()
#         self.assertNotIn("child1", self.parent_node.children)
#         self.assertIsNone(self.child_node1.parent)
#
# class TestTree(unittest.TestCase):
#     def setUp(self):
#         self.tree = Tree()
#         self.root = TreeNode(id_="root", content="Root Node")
#         self.child_node1 = TreeNode(id_="child1", content="Child Node 1")
#         self.child_node2 = TreeNode(id_="child2", content="Child Node 2")
#         self.grandchild_node = TreeNode(id_="grandchild", content="Grandchild Node")
#
#     def test_add_node(self):
#         self.tree.add_node(self.root)
#         self.assertIn("root", self.tree.internal_nodes)
#
#     def test_relate_parent_child(self):
#         self.tree.relate_parent_child(self.root, [self.child_node1, self.child_node2])
#         self.assertIn("child1", self.root.children)
#         self.assertIn("child2", self.root.children)
#         self.assertEqual(self.tree.root, self.root)
#
#     def test_tree_structure(self):
#         # Build the tree
#         self.tree.relate_parent_child(self.root, [self.child_node1, self.child_node2])
#         self.tree.relate_parent_child(self.child_node1, self.grandchild_node)
#
#         # Check the tree structure
#         self.assertIn("grandchild", self.child_node1.children)
#         self.assertEqual(self.grandchild_node.parent, self.child_node1)
#         self.assertEqual(self.child_node1.parent, self.root)
#
#     def test_acyclic(self):
#         # Build the tree
#         self.tree.relate_parent_child(self.root, self.child_node1)
#         self.tree.relate_parent_child(self.child_node1, self.child_node2)
#         # Trees should always be acyclic
#         self.assertTrue(self.tree.acyclic)
#
# if __name__ == "__main__":
#     unittest.main()
