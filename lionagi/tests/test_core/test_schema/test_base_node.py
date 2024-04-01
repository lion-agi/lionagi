from lionagi.core.schema.base_node import *
import unittest
from unittest.mock import MagicMock

class TestBaseNode(unittest.TestCase):
    def setUp(self):
        self.node1 = BaseNode(content="Node 1")
        self.node2 = BaseNode(content="Node 2")
        self.node3 = BaseNode(content="Node 3")
        self.edge1 = Edge(source_node_id=self.node1.id_, target_node_id=self.node2.id_, label="Edge 1")
        self.edge2 = Edge(source_node_id=self.node2.id_, target_node_id=self.node3.id_, label="Edge 2")
        self.node1.out_relations[self.node2.id_] = self.edge1
        self.node2.in_relations[self.node1.id_] = self.edge1
        self.node2.out_relations[self.node3.id_] = self.edge2
        self.node3.in_relations[self.node2.id_] = self.edge2

    def test_relations_property(self):
        self.assertEqual(self.node1.relations, {self.node2.id_: self.edge1})
        self.assertEqual(self.node2.relations, {self.node1.id_: self.edge1, self.node3.id_: self.edge2})
        self.assertEqual(self.node3.relations, {self.node2.id_: self.edge2})

    def test_in_edges_property(self):
        self.assertEqual(self.node1.in_edges, [])
        self.assertEqual(self.node2.in_edges, [self.edge1])
        self.assertEqual(self.node3.in_edges, [self.edge2])

    def test_out_edges_property(self):
        self.assertEqual(self.node1.out_edges, [self.edge1])
        self.assertEqual(self.node2.out_edges, [self.edge2])
        self.assertEqual(self.node3.out_edges, [])

    def test_edges_property(self):
        self.assertEqual(self.node1.edges, [self.edge1])
        self.assertEqual(self.node2.edges, [self.edge1, self.edge2])
        self.assertEqual(self.node3.edges, [self.edge2])

    def test_predecessors_property(self):
        self.assertEqual(self.node1.predecessors, [])
        self.assertEqual(self.node2.predecessors, [self.node1.id_])
        self.assertEqual(self.node3.predecessors, [self.node2.id_])

    def test_successors_property(self):
        self.assertEqual(self.node1.successors, [self.node2.id_])
        self.assertEqual(self.node2.successors, [self.node3.id_])
        self.assertEqual(self.node3.successors, [])

    def test_related_nodes_property(self):
        self.assertEqual(self.node1.related_nodes, [self.node2.id_])
        self.assertEqual(self.node2.related_nodes, [self.node1.id_, self.node3.id_])
        self.assertEqual(self.node3.related_nodes, [self.node2.id_])

    def test_is_related_property(self):
        self.assertTrue(self.node1.is_related)
        self.assertTrue(self.node2.is_related)
        self.assertTrue(self.node3.is_related)
        self.assertFalse(BaseNode().is_related)

    def test_has_edge_method(self):
        self.assertTrue(self.node1.has_edge(self.edge1))
        self.assertTrue(self.node1.has_edge(self.edge1.id_))
        self.assertFalse(self.node1.has_edge(self.edge2))
        self.assertFalse(self.node1.has_edge(self.edge2.id_))

    def test_get_edge_method(self):
        self.assertEqual(self.node1.get_edge(self.node2), self.edge1)
        self.assertEqual(self.node1.get_edge(self.node2.id_), self.edge1)
        self.assertIsNone(self.node1.get_edge(self.node3))
        self.assertIsNone(self.node1.get_edge(self.node3.id_))

    def test_is_predecessor_of_method(self):
        self.assertTrue(self.node1.is_predecessor_of(self.node2))
        self.assertTrue(self.node1.is_predecessor_of(self.node2.id_))
        self.assertFalse(self.node1.is_predecessor_of(self.node3))
        self.assertFalse(self.node1.is_predecessor_of(self.node3.id_))

    def test_is_successor_of_method(self):
        self.assertTrue(self.node2.is_successor_of(self.node1))
        self.assertTrue(self.node2.is_successor_of(self.node1.id_))
        self.assertFalse(self.node2.is_successor_of(self.node3))
        self.assertFalse(self.node2.is_successor_of(self.node3.id_))

    def test_is_related_with_method(self):
        self.assertTrue(self.node1.is_related_with(self.node2))
        self.assertTrue(self.node1.is_related_with(self.node2.id_))
        self.assertFalse(self.node1.is_related_with(self.node3))
        self.assertFalse(self.node1.is_related_with(self.node3.id_))

    def test_add_edge_method(self):
        node4 = BaseNode(content="Node 4")
        self.assertTrue(self.node1.add_edge(node4, label="Edge 3", direction=EdgeDirection.OUT))
        self.assertTrue(self.node1.has_edge(self.node1.get_edge(node4)))
        self.assertTrue(node4.has_edge(node4.get_edge(self.node1)))

        self.assertTrue(self.node1.add_edge(node4, direction=EdgeDirection.IN))
        self.assertTrue(self.node1.has_edge(self.node1.get_edge(node4)))
        self.assertTrue(node4.has_edge(node4.get_edge(self.node1)))

        edge = Edge(source_node_id=self.node1.id_, target_node_id=node4.id_, label="Edge 4")
        self.assertTrue(self.node1.add_edge(node4, edge=edge))
        self.assertTrue(self.node1.has_edge(edge))
        self.assertTrue(node4.has_edge(edge))

        self.assertFalse(self.node1.add_edge(MagicMock()))

    def test_pop_edge_method(self):
        self.assertEqual(self.node1.pop_edge(self.node2), self.edge1)
        self.assertFalse(self.node1.has_edge(self.edge1))
        self.assertFalse(self.node2.has_edge(self.edge1))

        self.assertIsNone(self.node1.pop_edge(self.node3))

    def test_content_str_property(self):
        self.assertEqual(self.node1.content_str, "Node 1")
        self.node1.content = {"key": "value"}
        self.assertEqual(self.node1.content_str, '{"key": "value"}')
        self.node1.content = None
        self.assertEqual(self.node1.content_str, "None")

    def test_str_method(self):
        node = BaseNode(content="Sample Content", metadata={"key": "value"})
        self.assertIn("BaseNode", str(node))
        self.assertIn("Sample Content", str(node))
        self.assertIn("{'key': 'value'}", str(node))

        node.content = "Long Content" * 10
        self.assertIn("Long Content", str(node))
        self.assertIn("...", str(node))

        node.metadata = {"key": "Long Metadata" * 10}
        self.assertIn("{'key': 'Long", str(node))
        self.assertIn("...", str(node))

    def test_copy_method(self):
        copy = self.node1.copy()
        self.assertIsInstance(copy, BaseNode)
        self.assertEqual(copy.content, self.node1.content)
        self.assertEqual(copy.metadata, self.node1.metadata)
        self.assertIsNot(copy, self.node1)

    def test_copy_method_with_update(self):
        copy = self.node1.copy(update={"content": "Updated Content"})
        self.assertEqual(copy.content, "Updated Content")
        self.assertNotEqual(copy.content, self.node1.content)

    def test_from_obj_method(self):
        obj = {"content": "Node Content", "metadata": {"key": "value"}}
        node = BaseNode.from_obj(obj)
        self.assertIsInstance(node, BaseNode)
        self.assertEqual(node.content, "Node Content")
        self.assertEqual(node.metadata, {"key": "value"})

    # def test_from_obj_method_with_relations(self):
    #     obj = {
    #         "content": "Node Content",
    #         "in_relations": {self.node1.id_: self.edge1.to_dict()},
    #         "out_relations": {self.node2.id_: self.edge2.to_dict()},
    #     }
    #     node = BaseNode.from_obj(obj)
    #     self.assertIsInstance(node, BaseNode)
    #     self.assertEqual(node.content, "Node Content")
    #     self.assertEqual(node.in_relations, {self.node1.id_: Edge.from_obj(self.edge1.to_dict())})
    #     self.assertEqual(node.out_relations, {self.node2.id_: Edge.from_obj(self.edge2.to_dict())})

    def test_to_dict_method(self):
        node_dict = self.node1.to_dict()
        self.assertIsInstance(node_dict, dict)
        self.assertEqual(node_dict["content"], self.node1.content)
        self.assertEqual(node_dict["meta"], self.node1.metadata)
        self.assertEqual(node_dict["in_relations"], {})

if __name__ == "__main__":
    unittest.main()