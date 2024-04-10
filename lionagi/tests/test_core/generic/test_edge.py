import unittest
from lionagi.core.generic.edge import *


class TestEdge(unittest.TestCase):
    def setUp(self):
        self.edge = Edge(
            id_="test_edge_id",
            timestamp="2023-06-08T10:00:00",
            head="head_node_id",
            tail="tail_node_id",
            label="test_label",
        )

    def test_field_annotations(self):
        annotations = self.edge._field_annotations
        self.assertEqual(annotations["head"], ["str"])
        self.assertEqual(annotations["tail"], ["str"])
        self.assertEqual(annotations["condition"], ["lionagi.core.generic.condition.condition", "none"])
        self.assertEqual(annotations["label"], ["str", "none"])

    def test_field_has_attr(self):
        self.assertTrue(self.edge._field_has_attr("head", "title"))
        self.assertTrue(self.edge._field_has_attr("tail", "description"))
        self.assertFalse(self.edge._field_has_attr("label", "non_existent_attr"))

    def test_to_dict(self):
        dict_data = self.edge.to_dict()
        self.assertIsInstance(dict_data, dict)
        self.assertEqual(dict_data["id_"], "test_edge_id")
        self.assertEqual(dict_data["timestamp"], "2023-06-08T10:00:00")
        self.assertEqual(dict_data["head"], "head_node_id")
        self.assertEqual(dict_data["tail"], "tail_node_id")
        self.assertIsNone(dict_data["condition"])
        self.assertEqual(dict_data["label"], "test_label")

    def test_validate_head_tail(self):
        node1 = BaseNode(id_="node1_id")
        node2 = BaseNode(id_="node2_id")

        validated_value = Edge._validate_head_tail(node1)
        self.assertEqual(validated_value, "node1_id")

        validated_value = Edge._validate_head_tail("node2_id")
        self.assertEqual(validated_value, "node2_id")

    # @patch.object(Condition, "check", return_value=True)
    # def test_check_condition_success(self, mock_check):
    #     condition = Condition()
    #     self.edge.condition = condition

    #     obj = {"key": "value"}
    #     result = self.edge.check_condition(obj)
    #     self.assertTrue(result)
    #     mock_check.assert_called_once_with(obj)

    def test_check_condition_no_condition(self):
        self.edge.condition = None
        obj = {"key": "value"}
        with self.assertRaises(ValueError):
            self.edge.check_condition(obj)

    def test_from_obj_dict(self):
        dict_data = {
            "id_": "dict_edge_id",
            "timestamp": "2023-06-08T11:00:00",
            "head": "dict_head_node_id",
            "tail": "dict_tail_node_id",
            "label": "dict_label",
        }
        edge = Edge.from_obj(dict_data)
        self.assertIsInstance(edge, Edge)
        self.assertEqual(edge.id_, "dict_edge_id")
        self.assertEqual(edge.timestamp, "2023-06-08T11:00:00")
        self.assertEqual(edge.head, "dict_head_node_id")
        self.assertEqual(edge.tail, "dict_tail_node_id")
        self.assertEqual(edge.label, "dict_label")

    def test_from_obj_str(self):
        json_str = '{"id_": "json_edge_id", "timestamp": "2023-06-08T12:00:00", "head": "json_head_node_id", "tail": "json_tail_node_id", "label": "json_label"}'
        edge = Edge.from_obj(json_str)
        self.assertIsInstance(edge, Edge)
        self.assertEqual(edge.id_, "json_edge_id")
        self.assertEqual(edge.timestamp, "2023-06-08T12:00:00")
        self.assertEqual(edge.head, "json_head_node_id")
        self.assertEqual(edge.tail, "json_tail_node_id")
        self.assertEqual(edge.label, "json_label")

    def test_from_obj_list(self):
        list_data = [
            {"id_": "edge1_id", "timestamp": "2023-06-08T13:00:00", "head": "head1_id", "tail": "tail1_id", "label": "label1"},
            {"id_": "edge2_id", "timestamp": "2023-06-08T14:00:00", "head": "head2_id", "tail": "tail2_id", "label": "label2"},
        ]
        edges = Edge.from_obj(list_data)
        self.assertIsInstance(edges, list)
        self.assertEqual(len(edges), 2)
        self.assertIsInstance(edges[0], Edge)
        self.assertIsInstance(edges[1], Edge)
        self.assertEqual(edges[0].id_, "edge1_id")
        self.assertEqual(edges[1].id_, "edge2_id")

    def test_from_obj_unsupported_type(self):
        with self.assertRaises(NotImplementedError):
            Edge.from_obj(123)


if __name__ == "__main__":
    unittest.main()
