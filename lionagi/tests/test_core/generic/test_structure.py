#TODO
# import unittest
# from lionagi.core.generic.structure import *
#
# class TestCondition(Condition):
#     def check(self, node: Node) -> bool:
#         return True
#
# class TestBaseStructure(unittest.TestCase):
#     def setUp(self):
#         self.structure = BaseStructure(id_="test_structure")
#         self.node1 = Node(id_="node1", content="Node 1 content")
#         self.node2 = Node(id_="node2", content="Node 2 content")
#         self.node3 = Node(id_="node3", content="Node 3 content")
#
#     def test_internal_edges(self):
#         self.structure.add_node([self.node1, self.node2])
#         self.structure.relate_nodes(self.node1, self.node2)
#         self.assertEqual(len(self.structure.internal_edges), 1)
#
#     def test_is_empty(self):
#         self.assertTrue(self.structure.is_empty)
#         self.structure.add_node(self.node1)
#         self.assertFalse(self.structure.is_empty)
#
#     def test_add_node_single(self):
#         self.structure.add_node(self.node1)
#         self.assertIn(self.node1.id_, self.structure.internal_nodes)
#
#     def test_add_node_list(self):
#         self.structure.add_node([self.node1, self.node2])
#         self.assertIn(self.node1.id_, self.structure.internal_nodes)
#         self.assertIn(self.node2.id_, self.structure.internal_nodes)
#
#     def test_add_node_dict(self):
#         self.structure.add_node({self.node1.id_: self.node1, self.node2.id_: self.node2})
#         self.assertIn(self.node1.id_, self.structure.internal_nodes)
#         self.assertIn(self.node2.id_, self.structure.internal_nodes)
#
#     def test_add_node_duplicate(self):
#         self.structure.add_node(self.node1)
#         with self.assertRaises(ValueError):
#             self.structure.add_node(self.node1)
#
#     def test_get_node_str(self):
#         self.structure.add_node(self.node1)
#         self.assertEqual(self.structure.get_node(self.node1.id_), self.node1)
#
#     def test_get_node_node(self):
#         self.structure.add_node(self.node1)
#         self.assertEqual(self.structure.get_node(self.node1), self.node1)
#
#     def test_get_node_list(self):
#         self.structure.add_node([self.node1, self.node2])
#         self.assertEqual(self.structure.get_node([self.node1.id_, self.node2.id_]), [self.node1, self.node2])
#
#     def test_get_node_dict(self):
#         self.structure.add_node([self.node1, self.node2])
#         self.assertEqual(self.structure.get_node({self.node1.id_: self.node1, self.node2.id_: self.node2}), [self.node1, self.node2])
#
#     def test_get_node_not_found(self):
#         with self.assertRaises(KeyError):
#             self.structure.get_node("nonexistent_node")
#
#     def test_get_node_default(self):
#         self.assertIsNone(self.structure.get_node("nonexistent_node", default=None))
#
#     def test_remove_node_node(self):
#         self.structure.add_node(self.node1)
#         self.structure.remove_node(self.node1)
#         self.assertNotIn(self.node1.id_, self.structure.internal_nodes)
#
#     def test_remove_node_str(self):
#         self.structure.add_node(self.node1)
#         self.structure.remove_node(self.node1.id_)
#         self.assertNotIn(self.node1.id_, self.structure.internal_nodes)
#
#     def test_remove_node_list(self):
#         self.structure.add_node([self.node1, self.node2])
#         self.structure.remove_node([self.node1, self.node2])
#         self.assertNotIn(self.node1.id_, self.structure.internal_nodes)
#         self.assertNotIn(self.node2.id_, self.structure.internal_nodes)
#
#     def test_remove_node_dict(self):
#         self.structure.add_node([self.node1, self.node2])
#         self.structure.remove_node({self.node1.id_: self.node1, self.node2.id_: self.node2})
#         self.assertNotIn(self.node1.id_, self.structure.internal_nodes)
#         self.assertNotIn(self.node2.id_, self.structure.internal_nodes)
#
#     def test_pop_node_node(self):
#         self.structure.add_node(self.node1)
#         popped_node = self.structure.pop_node(self.node1)
#         self.assertEqual(popped_node, self.node1)
#         self.assertNotIn(self.node1.id_, self.structure.internal_nodes)
#
#     def test_pop_node_str(self):
#         self.structure.add_node(self.node1)
#         popped_node = self.structure.pop_node(self.node1.id_)
#         self.assertEqual(popped_node, self.node1)
#         self.assertNotIn(self.node1.id_, self.structure.internal_nodes)
#
#     def test_pop_node_list(self):
#         self.structure.add_node([self.node1, self.node2])
#         popped_nodes = self.structure.pop_node([self.node1, self.node2])
#         self.assertEqual(popped_nodes, [self.node1, self.node2])
#         self.assertNotIn(self.node1.id_, self.structure.internal_nodes)
#         self.assertNotIn(self.node2.id_, self.structure.internal_nodes)
#
#     def test_pop_node_dict(self):
#         self.structure.add_node([self.node1, self.node2])
#         popped_nodes = self.structure.pop_node({self.node1.id_: self.node1, self.node2.id_: self.node2})
#         self.assertEqual(popped_nodes, [self.node1, self.node2])
#         self.assertNotIn(self.node1.id_, self.structure.internal_nodes)
#         self.assertNotIn(self.node2.id_, self.structure.internal_nodes)
#
#     def test_pop_node_default(self):
#         self.assertIsNone(self.structure.pop_node("nonexistent_node", default=None))
#
#     def test_remove_edge_edge(self):
#         self.structure.add_node([self.node1, self.node2])
#         self.structure.relate_nodes(self.node1, self.node2)
#         edge = list(self.node1.edges.values())[0]
#         self.structure.remove_edge(edge)
#         self.assertNotIn(edge.id_, self.structure.internal_edges)
#
#     def test_remove_edge_str(self):
#         self.structure.add_node([self.node1, self.node2])
#         self.structure.relate_nodes(self.node1, self.node2)
#         edge = list(self.node1.edges.values())[0]
#         self.structure.remove_edge(edge.id_)
#         self.assertNotIn(edge.id_, self.structure.internal_edges)
#
#     def test_remove_edge_list(self):
#         self.structure.add_node([self.node1, self.node2, self.node3])
#         self.structure.relate_nodes(self.node1, self.node2)
#         self.structure.relate_nodes(self.node2, self.node3)
#         edges = list(self.node2.edges.values())
#
#         self.structure.remove_edge(edges)
#         self.assertNotIn(edges[0].id_, self.structure.internal_edges)
#         self.assertNotIn(edges[1].id_, self.structure.internal_edges)
#
#     def test_remove_edge_dict(self):
#         self.structure.add_node([self.node1, self.node2, self.node3])
#         self.structure.relate_nodes(self.node1, self.node2)
#         self.structure.relate_nodes(self.node2, self.node3)
#
#         edge_dict = self.node2.edges
#         edge_list = list(edge_dict.values())
#
#         self.structure.remove_edge(edge_dict)
#         self.assertNotIn(edge_list[0].id_, self.structure.internal_edges)
#         self.assertNotIn(edge_list[1].id_, self.structure.internal_edges)
#
#     def test_remove_edge_not_found(self):
#         with self.assertRaises(ValueError):
#             self.structure.remove_edge("nonexistent_edge")
#
#     def test_clear(self):
#         self.structure.add_node([self.node1, self.node2])
#         self.structure.clear()
#         self.assertTrue(self.structure.is_empty)
#
#     def test_get_node_edges_head(self):
#         self.structure.add_node([self.node1, self.node2])
#         self.structure.relate_nodes(self.node1, self.node2)
#         edges = self.structure.get_node_edges(self.node1, node_as="head")
#         self.assertEqual(len(edges), 1)
#
#     def test_get_node_edges_tail(self):
#         self.structure.add_node([self.node1, self.node2])
#         self.structure.relate_nodes(self.node1, self.node2)
#         edges = self.structure.get_node_edges(self.node2, node_as="tail")
#         self.assertEqual(len(edges), 1)
#
#     def test_get_node_edges_label(self):
#         self.structure.add_node([self.node1, self.node2])
#         self.structure.relate_nodes(self.node1, self.node2, label="test_label")
#         edges = self.structure.get_node_edges(self.node1, node_as="head", label="test_label")
#         self.assertEqual(len(edges), 1)
#
#     def test_add_edge(self):
#         self.structure.relate_nodes(self.node1, self.node2)
#         self.assertIn(self.node1.id_, self.structure.internal_nodes)
#         self.assertIn(self.node2.id_, self.structure.internal_nodes)
#         self.assertEqual(len(self.structure.internal_edges), 1)
#
#     def test_add_edge_with_label(self):
#         self.structure.relate_nodes(self.node1, self.node2, label="test_label")
#         edge = list(self.structure.internal_edges.values())[0]
#         self.assertEqual(edge.label, "test_label")
#
# if __name__ == "__main__":
#     unittest.main()