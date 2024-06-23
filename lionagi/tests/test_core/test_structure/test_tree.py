#TODO
# import unittest
# from lionagi.new.schema.todo.tree import Tree
# from lionagi.core.generic import TreeNode
#
#
# class TestTree(unittest.TestCase):
#     def setUp(self):
#         self.tree = Tree()
#         self.node1 = TreeNode(id_="node1", content="Node 1")
#         self.node2 = TreeNode(id_="node2", content="Node 2")
#         self.node3 = TreeNode(id_="node3", content="Node 3")
#         self.tree.add_structure_node(self.node1)
#         self.tree.add_structure_node(self.node2)
#         self.tree.add_structure_node(self.node3)
#
#     def test_add_parent_to_child(self):
#         self.tree.add_parent_to_child(self.node1, self.node2)
#         self.assertEqual(self.node2, self.node1.parent)
#         self.assertIn(self.node1, self.node2.children)
#
#     def test_add_child_to_parent(self):
#         self.tree.add_child_to_parent(self.node3, self.node2)
#         self.assertEqual(self.node2, self.node3.parent)
#         self.assertIn(self.node3, self.node2.children)
#
#     def test_find_parent(self):
#         self.tree.add_parent_to_child(self.node1, self.node2)
#         parent = self.tree.find_parent(self.node1)
#         self.assertEqual(self.node2, parent)
#
#     def test_find_child(self):
#         self.tree.add_parent_to_child(self.node1, self.node2)
#         children = self.tree.find_child(self.node2)
#         self.assertIn(self.node1, children)
#
#     def test_parent_child_relationship(self):
#         self.tree.add_parent_to_child(self.node1, self.node2)
#         self.tree.add_child_to_parent(self.node3, self.node2)
#         self.assertIn(self.node1, self.node2.children)
#         self.assertIn(self.node3, self.node2.children)
#         self.assertEqual(self.node2, self.node1.parent)
#         self.assertEqual(self.node2, self.node3.parent)
#
#     # Add more tests as necessary to cover edge cases and other functionalities
#
#
# if __name__ == "__main__":
#     unittest.main()
