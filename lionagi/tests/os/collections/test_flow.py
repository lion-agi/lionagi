import unittest
from lionagi.os.collections.node.node import Node
from lionagi.os.collections.pile.pile import pile
from lionagi.os.collections.flow.progression import progression
from lionagi.os.collections.flow.flow import flow


class TestFlow(unittest.TestCase):

    def setUp(self):
        # Setup for creating initial nodes, piles, and progressions
        self.nodes = [Node(content=i) for i in range(10)]
        self.pile1 = pile(self.nodes)
        self.prog1 = progression(self.nodes[:5], name="left")
        self.prog2 = progression(self.nodes[5:], name="right")
        self.flow = flow([self.prog1, self.prog2])

    def test_initialization(self):
        self.assertEqual(len(self.flow.sequences), 2)
        self.assertIn("left", self.flow.registry)
        self.assertIn("right", self.flow.registry)

    def test_append_to_flow(self):
        new_node = Node(content="new_node")
        self.flow.append(new_node, "left")
        self.assertIn(new_node.ln_id, self.flow.get("left"))

    def test_exclude_from_flow(self):
        node_to_remove = self.nodes[0]
        self.flow.exclude("left", node_to_remove)
        self.assertNotIn(node_to_remove.ln_id, self.flow.get("left"))

    def test_get_sequence(self):
        seq = self.flow.get("left")
        self.assertEqual(seq, self.prog1)
        seq_default = self.flow.get("nonexistent", default=None)
        self.assertIsNone(seq_default)

    def test_register_sequence(self):
        new_prog = progression(self.nodes[2:4], name="middle")
        self.flow.register(new_prog)
        self.assertIn("middle", self.flow.registry)

    def test_popleft(self):
        first_node_id = self.prog1[0]
        removed_node_id = self.flow.popleft("left")
        self.assertEqual(first_node_id, removed_node_id)
        self.assertNotIn(removed_node_id, self.flow.get("left"))

    def test_shape_and_size(self):
        shape = self.flow.shape()
        self.assertEqual(shape["left"], 5)
        self.assertEqual(shape["right"], 5)
        size = self.flow.size()
        self.assertEqual(size, 10)

    def test_clear(self):
        self.flow.clear()
        self.assertEqual(len(self.flow.sequences), 0)
        self.assertEqual(len(self.flow.registry), 0)

    def test_iteration(self):
        items = list(self.flow)
        self.assertEqual(len(items), 2)

    def test_to_df(self):
        df = self.flow.to_df()
        self.assertEqual(df.shape[0], 2)
        self.assertEqual(df.columns.tolist(), ["order", "name"])

    def test_inclusion_check(self):
        self.assertTrue(self.prog1 in self.flow)
        self.assertTrue(self.prog2 in self.flow)
        try:
            a = Node(content="nonexistent") in self.flow
        except TypeError:
            pass

    # Additional Tests for Edge Cases
    def test_empty_flow_initialization(self):
        empty_flow = flow()
        self.assertEqual(len(empty_flow.sequences), 0)
        self.assertEqual(len(empty_flow.registry), 0)

    def test_append_to_nonexistent_sequence(self):
        new_node = Node(content="new_node")
        self.flow.append(new_node, "nonexistent")
        self.assertIn(new_node.ln_id, self.flow.get("nonexistent"))

    def test_exclude_nonexistent_item(self):
        non_existent_node = Node(content="nonexistent")
        result = self.flow.exclude("left", non_existent_node)
        self.assertTrue(result)

    def test_exclude_nonexistent_sequence(self):
        result = self.flow.exclude("nonexistent")
        self.assertFalse(result)

    def test_get_nonexistent_sequence(self):
        try:
            self.flow.get("nonexistent")
        except Exception as e:
            if e.__class__.__name__ == "LionTypeError":
                return
            raise AssertionError("LionTypeError not raised")

    def test_register_existing_sequence_name(self):
        with self.assertRaises(ValueError):
            self.flow.register(self.prog1, name="right")

    def test_popleft_nonexistent_sequence(self):
        try:
            self.flow.popleft("nonexistent")
        except Exception as e:
            if e.__class__.__name__ == "LionTypeError":
                return
            raise AssertionError("LionTypeError not raised")

    def test_append_multiple_items(self):
        new_nodes = [Node(content="new_node1"), Node(content="new_node2")]
        for new_node in new_nodes:
            self.flow.append(new_node, "left")
        for new_node in new_nodes:
            self.assertIn(new_node.ln_id, self.flow.get("left"))

    def test_remove_from_all_sequences(self):
        node_to_remove = self.nodes[0]
        self.flow.append(node_to_remove, "right")
        self.flow.remove(node_to_remove)
        self.assertNotIn(node_to_remove.ln_id, self.flow.get("right"))

    def test_shape_empty_flow(self):
        empty_flow = flow()
        self.assertEqual(empty_flow.shape(), {})

    def test_size_empty_flow(self):
        empty_flow = flow()
        self.assertEqual(empty_flow.size(), 0)

    def test_clear_empty_flow(self):
        empty_flow = flow()
        empty_flow.clear()
        self.assertEqual(len(empty_flow.sequences), 0)
        self.assertEqual(len(empty_flow.registry), 0)


if __name__ == "__main__":
    unittest.main()
