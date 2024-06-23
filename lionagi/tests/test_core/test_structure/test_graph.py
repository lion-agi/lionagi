#TODO
# import unittest
# from unittest.mock import MagicMock, patch
# from lionagi.core.generic import BaseNode, Edge
# from lionagi.new.schema.todo.graph import Graph
#
#
# class TestGraph(unittest.TestCase):
#     def setUp(self):
#         self.graph = Graph()
#         self.node1 = BaseNode(id_="node1", content="Node 1")
#         self.node2 = BaseNode(id_="node2", content="Node 2")
#         self.edge1 = Edge(
#             id_="edge1", source_node_id="node1", target_node_id="node2", label="Edge 1"
#         )
#         self.graph.structure_nodes = {"node1": self.node1, "node2": self.node2}
#         self.graph.structure_edges = {"edge1": self.edge1}
#
#     @patch("lionagi.libs.SysUtil.check_import")
#     def test_to_networkx_success(self, mock_check_import):
#         mock_check_import.return_value = None
#         with patch("networkx.DiGraph") as mock_digraph:
#             mock_graph = MagicMock()
#             mock_digraph.return_value = mock_graph
#
#             result = self.graph.to_networkx()
#
#             self.assertEqual(result, mock_graph)
#
#     @patch("lionagi.libs.SysUtil.check_import")
#     def test_to_networkx_empty_graph(self, mock_check_import):
#         mock_check_import.return_value = None
#         with patch("networkx.DiGraph") as mock_digraph:
#             mock_graph = MagicMock()
#             mock_digraph.return_value = mock_graph
#
#             self.graph.structure_nodes = {}
#             self.graph.structure_edges = {}
#             result = self.graph.to_networkx()
#
#             self.assertEqual(result, mock_graph)
#             mock_check_import.assert_called_once_with("networkx")
#             mock_digraph.assert_called_once()
#             mock_graph.add_node.assert_not_called()
#             mock_graph.add_edge.assert_not_called()
#
#     @patch("lionagi.libs.SysUtil.check_import", side_effect=ImportError)
#     def test_to_networkx_import_error(self, mock_check_import):
#         with self.assertRaises(ImportError):
#             self.graph.to_networkx()
#         mock_check_import.assert_called_once_with("networkx")
#
#
# if __name__ == "__main__":
#     unittest.main()
