import unittest
from lionagi.os.collections.abc.element import Element
from lionagi.os.collections.node.node import Node
from lionagi.os.collections.pile.pile import pile
from lionagi.os.collections.flow.progression import progression
from lionagi.os.collections.flow.exchange import Exchange


class TestExchange(unittest.TestCase):

    def setUp(self):
        # Setup for creating initial nodes, piles, and progressions
        self.nodes = [Node(content=i) for i in range(10)]
        self.pile1 = pile(self.nodes)
        self.prog1 = progression(self.nodes[:5], name="left")
        self.prog2 = progression(self.nodes[5:], name="right")
        self.exchange = Exchange()

    def test_initialization(self):
        self.assertEqual(len(self.exchange.pile), 0)
        self.assertEqual(len(self.exchange.pending_ins), 0)
        self.assertEqual(len(self.exchange.pending_outs), 0)

    def test_include_in(self):
        sender_id = "sender1"
        for node in self.nodes[:5]:
            node.sender = sender_id
            self.exchange.include(node, "in")

        self.assertEqual(len(self.exchange.pile), 5)
        self.assertIn(sender_id, self.exchange.pending_ins)
        self.assertEqual(len(self.exchange.pending_ins[sender_id]), 5)

    def test_include_out(self):
        for node in self.nodes[:5]:
            self.exchange.include(node, "out")

        self.assertEqual(len(self.exchange.pile), 5)
        self.assertEqual(len(self.exchange.pending_outs), 5)

    def test_exclude(self):
        for node in self.nodes[:5]:
            self.exchange.include(node, "out")

        node_to_remove = self.nodes[0]
        self.exchange.exclude(node_to_remove)
        self.assertNotIn(node_to_remove, self.exchange.pile)
        self.assertNotIn(node_to_remove, self.exchange.pending_outs)

    def test_exclude_from_in(self):
        sender_id = "sender1"
        for node in self.nodes[:5]:
            node.sender = sender_id
            self.exchange.include(node, "in")

        node_to_remove = self.nodes[0]
        self.exchange.exclude(node_to_remove)
        self.assertNotIn(node_to_remove, self.exchange.pile)
        self.assertNotIn(node_to_remove, self.exchange.pending_ins[sender_id])

    def test_senders(self):
        sender_id = "sender1"
        for node in self.nodes[:5]:
            node.sender = sender_id
            self.exchange.include(node, "in")

        self.assertIn(sender_id, self.exchange.senders)

    def test_to_dict(self):
        for node in self.nodes[:5]:
            self.exchange.include(node, "out")

        exchange_dict = self.exchange.to_dict()
        self.assertIn("pile", exchange_dict)
        self.assertIn("pending_ins", exchange_dict)
        self.assertIn("pending_outs", exchange_dict)

    def test_bool(self):
        self.assertTrue(self.exchange)

    # Additional Tests for Edge Cases
    def test_include_non_sendable(self):
        non_sendable = Element()
        with self.assertRaises(AttributeError):
            self.exchange.include(non_sendable, "in")

    def test_exclude_nonexistent_item(self):
        non_existent_node = Node(content="nonexistent")
        result = self.exchange.exclude(non_existent_node)
        self.assertTrue(result)

    def test_include_multiple_items_in(self):
        sender_id = "sender2"
        new_nodes = [Node(content="new_node1"), Node(content="new_node2")]
        for new_node in new_nodes:
            new_node.sender = sender_id
            self.exchange.include(new_node, "in")

        self.assertEqual(len(self.exchange.pile), 2)
        self.assertEqual(len(self.exchange.pending_ins[sender_id]), 2)

    def test_include_multiple_items_out(self):
        new_nodes = [Node(content="new_node1"), Node(content="new_node2")]
        for new_node in new_nodes:
            self.exchange.include(new_node, "out")

        self.assertEqual(len(self.exchange.pile), 2)
        self.assertEqual(len(self.exchange.pending_outs), 2)

    def test_exclude_from_empty_exchange(self):
        result = self.exchange.exclude(Node(content="nonexistent"))
        self.assertTrue(result)

    def test_clear_empty_exchange(self):
        self.exchange.pile.clear()
        self.exchange.pending_ins.clear()
        self.exchange.pending_outs.clear()
        self.assertEqual(len(self.exchange.pile), 0)
        self.assertEqual(len(self.exchange.pending_ins), 0)
        self.assertEqual(len(self.exchange.pending_outs), 0)

    def test_clear_exchange(self):
        sender_id = "sender3"
        for node in self.nodes[:5]:
            node.sender = sender_id
            self.exchange.include(node, "in")
        for node in self.nodes[5:]:
            self.exchange.include(node, "out")

        self.exchange.pile.clear()
        self.exchange.pending_ins.clear()
        self.exchange.pending_outs.clear()

        self.assertEqual(len(self.exchange.pile), 0)
        self.assertEqual(len(self.exchange.pending_ins), 0)
        self.assertEqual(len(self.exchange.pending_outs), 0)


if __name__ == "__main__":
    unittest.main()
