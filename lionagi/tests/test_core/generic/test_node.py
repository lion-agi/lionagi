
import unittest
from unittest.mock import MagicMock, patch
from lionagi.core.generic.node import Node, Relations
from lionagi.core.generic.edge import Edge
from lionagi.core.generic.condition import Condition

class TestNode(unittest.TestCase):
    def setUp(self):
        self.node1 = Node(id_="node1", content="Node 1 content")
        self.node2 = Node(id_="node2", content="Node 2 content")
        self.node3 = Node(id_="node3", content="Node 3 content")

    def test_related_nodes(self):
        self.node1.relate(self.node2)
        self.node1.relate(self.node3)
        self.assertEqual(self.node1.related_nodes, {"node2", "node3"})

    def test_edges(self):
        self.node1.relate(self.node2)
        self.node1.relate(self.node3)
        self.assertEqual(len(self.node1.edges), 2)

    def test_node_relations(self):
        self.node1.relate(self.node2)
        self.node1.relate(self.node3)
        node_relations = self.node1.node_relations
        self.assertTrue("node2" in node_relations["points_to"] or "node2" in node_relations["pointed_by"])
        self.assertTrue("node3" in node_relations["points_to"] or "node3" in node_relations["pointed_by"])

    def test_predecessors_and_successors(self):
        self.node1.relate(self.node2, node_as="head")
        self.node2.relate(self.node3, node_as="head")
        self.assertEqual(self.node2.precedessors, ["node1"])
        self.assertEqual(self.node2.successors, ["node3"])

    def test_relate(self):
        self.node1.relate(self.node2)
        self.assertTrue(self.node1.edges and self.node2.edges)

    def test_relate_invalid_self_as(self):
        with self.assertRaises(ValueError):
            self.node1.relate(self.node2, node_as="invalid")

    def test_unrelate(self):
        self.node1.relate(self.node2)
        self.assertTrue(self.node1.unrelate(self.node2))
        self.assertFalse(self.node1.related_nodes)

    def test_unrelate_specific_edge(self):
        self.node1.relate(self.node2)
        edge_id = next(iter(self.node1.edges))
        self.assertTrue(self.node1.unrelate(self.node2, edge=edge_id))
        self.assertFalse(self.node1.edges)

    def test_unrelate_invalid_node(self):
        with self.assertRaises(ValueError):
            self.node1.unrelate(self.node2)

    @patch("lionagi.integrations.bridge.LlamaIndexBridge.to_llama_index_node")
    def test_to_llama_index(self, mock_to_llama_index_node):
        mock_llama_node = MagicMock()
        mock_to_llama_index_node.return_value = mock_llama_node
        result = self.node1.to_llama_index()
        self.assertEqual(result, mock_llama_node)

    @patch("lionagi.integrations.bridge.LangchainBridge.to_langchain_document")
    def test_to_langchain(self, mock_to_langchain_document):
        mock_lc_doc = MagicMock()
        mock_to_langchain_document.return_value = mock_lc_doc
        result = self.node1.to_langchain()
        self.assertEqual(result, mock_lc_doc)

    def test_from_llama_index(self):
        mock_llama_node = MagicMock()
        mock_llama_node.to_dict.return_value = {"id_": "llama_node", "content": "Llama node content"}
        node = Node.from_llama_index(mock_llama_node)
        self.assertEqual(node.id_, "llama_node")
        self.assertEqual(node.content, "Llama node content")

    def test_from_langchain(self):
        mock_lc_doc = MagicMock()
        mock_lc_doc.to_json.return_value = {"id": "lc_doc", "kwargs": {"content": "Langchain document content"}}
        node = Node.from_langchain(mock_lc_doc)
        self.assertEqual(node.lc_id, "lc_doc")
        self.assertEqual(node.content, "Langchain document content")

    def test_str_representation(self):
        node = Node(id_="node1", content="Node content", metadata={"key": "value"}, timestamp="2023-06-09")
        expected = "Node(node1, Node content, {'key': 'value'}, (2023-06-09))"
        self.assertEqual(str(node), expected)

if __name__ == "__main__":
    unittest.main()
