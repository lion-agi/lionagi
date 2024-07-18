#TODO
# import unittest
# from unittest.mock import MagicMock, patch
# from lionagi.core.graph.graph import Graph
# from lionagi.core.generic.node import Node
# from lionagi.core.generic.edge import Edge
#
# class TestGraph(unittest.TestCase):
#
#     def setUp(self):
#         self.graph = Graph()
#         self.node1 = Node(id_="node1", content="Node 1 content")
#         self.node2 = Node(id_="node2", content="Node 2 content")
#         self.node3 = Node(id_="node3", content="Node 3 content")
#         self.graph.add_node(self.node1)
#         self.graph.add_node(self.node2)
#         self.graph.add_node(self.node3)
#
#     def test_graph_heads(self):
#         self.graph.relate_nodes(self.node1, self.node2)
#         self.assertEqual(["node1"], self.graph.graph_heads)
#
#
#     def test_acyclic(self):
#         self.graph.relate_nodes(self.node1, self.node2)
#         self.assertTrue(self.graph.acyclic)
#
#         self.graph.relate_nodes(self.node2, self.node1)  # Creating a cycle
#         self.assertFalse(self.graph.acyclic)
#
#     @patch("lionagi.libs.SysUtil.check_import")
#     def test_to_networkx_success(self, mock_check_import):
#         mock_check_import.return_value = None
#         with patch("networkx.DiGraph") as mock_digraph:
#             mock_graph = MagicMock()
#             mock_digraph.return_value = mock_graph
#             result = self.graph.to_networkx()
#             self.assertEqual(result, mock_graph)
#
#     @patch("lionagi.libs.SysUtil.check_import")
#     def test_to_networkx_empty_graph(self, mock_check_import):
#         mock_check_import.return_value = None
#         with patch("networkx.DiGraph") as mock_digraph:
#             mock_graph = MagicMock()
#             mock_digraph.return_value = mock_graph
#
#             self.graph.internal_nodes = {}
#             result = self.graph.to_networkx()
#
#             self.assertEqual(result, mock_graph)
#             mock_check_import.assert_called_once_with("networkx")
#             mock_digraph.assert_called_once()
#             mock_graph.add_node.assert_not_called()
#             mock_graph.add_edge.assert_not_called()
#
#     def test_add_node(self):
#         new_node = Node(id_="node4", content="Node 4 content")
#         self.graph.add_node(new_node)
#         self.assertIn("node4", self.graph.internal_nodes)
#
#     def test_remove_node(self):
#         self.graph.remove_node(self.node1)
#         self.assertNotIn("node1", self.graph.internal_nodes)
#
#     def test_clear(self):
#         self.graph.clear()
#         self.assertEqual(len(self.graph.internal_nodes), 0)
#         self.assertTrue(self.graph.is_empty)
#
# if __name__ == "__main__":
#     unittest.main()
