# TODO

# import unittest
# from unittest.mock import MagicMock, patch
# from lionagi.core.tool.structure import *
#
#
# class TestBaseStructure(unittest.TestCase):
#     def setUp(self):
#         self.structure = BaseStructure()
#         self.node1 = BaseNode(id_="node1")
#         self.node2 = BaseNode(id_="node2")
#         self.node3 = BaseNode(id_="node3")
#         self.edge1 = Edge(id_="edge1", source_node_id="node1", target_node_id="node2")
#         self.edge2 = Edge(id_="edge2", source_node_id="node2", target_node_id="node3")
#
#     def test_node_edges_property(self):
#         self.node1.in_relations = {"edge1": self.edge1}
#         self.node1.out_relations = {"edge2": self.edge2}
#         self.structure.structure_nodes = {"node1": self.node1}
#         expected_result = {
#             "node1": {"in": {"edge1": self.edge1}, "out": {"edge2": self.edge2}}
#         }
#         self.assertEqual(self.structure.node_edges, expected_result)
#
#     def test_get_node_edges_with_node(self):
#         self.node1.out_relations = {"edge1": self.edge1}
#         self.node1.in_relations = {"edge2": self.edge2}
#         self.structure.structure_nodes = {"node1": self.node1}
#         self.assertEqual(
#             self.structure.get_node_edges(self.node1, direction="out"), [self.edge1]
#         )
#         self.assertEqual(
#             self.structure.get_node_edges(self.node1, direction="in"), [self.edge2]
#         )
#         self.assertEqual(
#             self.structure.get_node_edges(self.node1, direction="all"),
#             [self.edge2, self.edge1],
#         )
#
#     def test_get_node_edges_without_node(self):
#         self.structure.structure_edges = {"edge1": self.edge1, "edge2": self.edge2}
#         self.assertEqual(self.structure.get_node_edges(), [self.edge1, self.edge2])
#
#     def test_get_node_edges_node_not_found(self):
#         invalid_node = BaseNode(id_="invalid_node")
#         try:
#             self.structure.get_node_edges(invalid_node)
#         except KeyError as e:
#             self.assertEqual(str(e), f"node {invalid_node.id_} is not found")
#
#     def test_has_structure_edge_with_edge_object(self):
#         self.structure.structure_edges = {"edge1": self.edge1}
#         self.assertTrue(self.structure.has_structure_edge(self.edge1))
#
#     def test_has_structure_edge_with_edge_id(self):
#         self.structure.structure_edges = {"edge1": self.edge1}
#         self.assertTrue(self.structure.has_structure_edge("edge1"))
#
#     def test_get_structure_edge_with_edge_object(self):
#         self.structure.structure_edges = {"edge1": self.edge1}
#         self.assertEqual(self.structure.get_structure_edge(self.edge1), self.edge1)
#
#     def test_get_structure_edge_with_edge_id(self):
#         self.structure.structure_edges = {"edge1": self.edge1}
#         self.assertEqual(self.structure.get_structure_edge("edge1"), self.edge1)
#
#     def test_add_structure_edge_success(self):
#         self.structure.structure_nodes = {"node1": self.node1, "node2": self.node2}
#         self.structure.add_structure_edge(self.edge1)
#         self.assertEqual(self.structure.structure_edges, {"edge1": self.edge1})
#         self.assertEqual(self.node1.out_relations, {"node2": self.edge1})
#         self.assertEqual(self.node2.in_relations, {"node1": self.edge1})
#
#     def test_add_structure_edge_failure(self):
#         with self.assertRaises(ValueError):
#             self.structure.add_structure_edge(self.edge1)
#
#     def test_remove_structure_edge_with_edge_object(self):
#         self.structure.structure_edges = {"edge1": self.edge1}
#         self.structure.structure_nodes = {"node1": self.node1, "node2": self.node2}
#         self.node1.out_relations = {"node2": self.edge1}
#         self.node2.in_relations = {"node1": self.edge1}
#         self.structure.remove_structure_edge(self.edge1)
#         self.assertEqual(self.structure.structure_edges, {})
#         self.assertEqual(self.node1.out_relations, {})
#         self.assertEqual(self.node2.in_relations, {})
#
#     def test_remove_structure_edge_with_edge_id(self):
#         self.structure.structure_edges = {"edge1": self.edge1}
#         self.structure.structure_nodes = {"node1": self.node1, "node2": self.node2}
#         self.node1.out_relations = {"node2": self.edge1}
#         self.node2.in_relations = {"node1": self.edge1}
#         self.structure.remove_structure_edge("edge1")
#         self.assertEqual(self.structure.structure_edges, {})
#         self.assertEqual(self.node1.out_relations, {})
#         self.assertEqual(self.node2.in_relations, {})
#
#     def test_remove_structure_node_success(self):
#         self.structure.structure_nodes = {"node1": self.node1, "node2": self.node2}
#         self.structure.structure_edges = {"edge1": self.edge1}
#         self.node1.out_relations = {"node2": self.edge1}
#         self.node2.in_relations = {"node1": self.edge1}
#         self.structure.remove_structure_node(self.node1)
#         self.assertEqual(self.structure.structure_nodes, {"node2": self.node2})
#         self.assertEqual(self.structure.structure_edges, {})
#
#     def test_remove_structure_node_failure(self):
#         with self.assertRaises(ValueError):
#             self.structure.remove_structure_node(self.node1)
#
#     def test_add_structure_node_with_base_node(self):
#         self.structure.add_structure_node(self.node1)
#         self.assertEqual(self.structure.structure_nodes, {"node1": self.node1})
#
#     def test_add_structure_node_with_list(self):
#         self.structure.add_structure_node([self.node1, self.node2])
#         self.assertEqual(
#             self.structure.structure_nodes, {"node1": self.node1, "node2": self.node2}
#         )
#
#     def test_add_structure_node_with_dict(self):
#         self.structure.add_structure_node({"node1": self.node1, "node2": self.node2})
#         self.assertEqual(
#             self.structure.structure_nodes, {"node1": self.node1, "node2": self.node2}
#         )
#
#     def test_add_structure_node_unsupported_type(self):
#         with self.assertRaises(NotImplementedError):
#             self.structure.add_structure_node(1)
#
#     def test_get_structure_node_with_node_id(self):
#         self.structure.structure_nodes = {"node1": self.node1}
#         self.assertEqual(self.structure.get_structure_node("node1"), self.node1)
#
#     def test_get_structure_node_with_base_node(self):
#         self.structure.structure_nodes = {"node1": self.node1}
#         self.assertEqual(self.structure.get_structure_node(self.node1), self.node1)
#
#     def test_get_structure_node_with_list(self):
#         self.structure.structure_nodes = {"node1": self.node1, "node2": self.node2}
#         self.assertEqual(
#             self.structure.get_structure_node(["node1", "node2"]),
#             [self.node1, self.node2],
#         )
#
#     def test_pop_structure_node_with_node_id(self):
#         self.structure.structure_nodes = {"node1": self.node1}
#         self.assertEqual(self.structure.pop_structure_node("node1"), self.node1)
#         self.assertEqual(self.structure.structure_nodes, {})
#
#     def test_pop_structure_node_with_base_node(self):
#         self.structure.structure_nodes = {"node1": self.node1}
#         self.assertEqual(self.structure.pop_structure_node(self.node1), self.node1)
#         self.assertEqual(self.structure.structure_nodes, {})
#
#     def test_pop_structure_node_with_list(self):
#         self.structure.structure_nodes = {"node1": self.node1, "node2": self.node2}
#         self.assertEqual(
#             self.structure.pop_structure_node(["node1", "node2"]),
#             [self.node1, self.node2],
#         )
#         self.assertEqual(self.structure.structure_nodes, {})
#
#     def test_pop_structure_node_unsupported_type(self):
#         with self.assertRaises(NotImplementedError):
#             self.structure.pop_structure_node(1)
#
#     def test_has_structure_node_with_node_id(self):
#         self.structure.structure_nodes = {"node1": self.node1}
#         self.assertTrue(self.structure.has_structure_node("node1"))
#         self.assertFalse(self.structure.has_structure_node("node2"))
#
#     def test_has_structure_node_with_base_node(self):
#         self.structure.structure_nodes = {"node1": self.node1}
#         self.assertTrue(self.structure.has_structure_node(self.node1))
#         self.assertFalse(self.structure.has_structure_node(self.node2))
#
#     def test_has_structure_node_with_list(self):
#         self.structure.structure_nodes = {"node1": self.node1, "node2": self.node2}
#         self.assertTrue(self.structure.has_structure_node(["node1", "node2"]))
#         self.assertFalse(self.structure.has_structure_node(["node1", "node3"]))
#
#     def test_is_empty_property(self):
#         self.assertTrue(self.structure.is_empty)
#         self.structure.structure_nodes = {"node1": self.node1}
#         self.assertFalse(self.structure.is_empty)
#
#     def test_clear_method(self):
#         self.structure.structure_nodes = {"node1": self.node1}
#         self.structure.structure_edges = {"edge1": self.edge1}
#         self.structure.clear()
#         self.assertEqual(self.structure.structure_nodes, {})
#         self.assertEqual(self.structure.structure_edges, {})
#
#
# if __name__ == "__main__":
#     unittest.main()
