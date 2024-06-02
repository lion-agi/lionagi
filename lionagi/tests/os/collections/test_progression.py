import unittest
from lionagi.os.collections.abc import ItemNotFoundError
from lionagi.os.collections.flow.progression import Progression
from lionagi.os.collections.node.node import Node


class TestProgression(unittest.TestCase):

    def setUp(self):
        self.nodes = [Node() for _ in range(5)]
        self.p = Progression(order=[node.ln_id for node in self.nodes])

    def test_initial_order(self):
        self.assertEqual(self.p.order, [node.ln_id for node in self.nodes])

    def test_append_node(self):
        new_node = Node()
        self.p.append(new_node)
        self.assertIn(new_node.ln_id, self.p.order)
        self.assertEqual(len(self.p), 6)

    def test_extend_single_node(self):
        new_node = Node()
        self.p.extend(new_node)
        self.assertIn(new_node.ln_id, self.p.order)
        self.assertEqual(len(self.p), 6)

    def test_extend_multiple_nodes(self):
        new_nodes = [Node() for _ in range(3)]
        self.p.extend(new_nodes)
        for node in new_nodes:
            self.assertIn(node.ln_id, self.p.order)
        self.assertEqual(len(self.p), 8)

    def test_include_node(self):
        new_node = Node()
        self.p.include(new_node)
        self.assertIn(new_node.ln_id, self.p.order)

    def test_getitem_slice(self):
        slice_result = self.p[1:5]
        self.assertEqual(slice_result.order, self.p.order[1:5])

    def test_setitem(self):
        new_node = Node()
        self.p[0] = new_node.ln_id
        self.assertEqual(self.p[0], new_node.ln_id)

    def test_add_node(self):
        new_node = Node()
        new_prog = self.p + new_node
        self.assertIn(new_node.ln_id, new_prog.order)

    def test_iadd_node(self):
        new_node = Node()
        self.p += new_node
        self.assertIn(new_node.ln_id, self.p.order)

    def test_subtract_node(self):
        node_to_remove = self.nodes[0]
        self.p -= node_to_remove.ln_id
        self.assertNotIn(node_to_remove.ln_id, self.p.order)

    def test_isubtract_node(self):
        node_to_remove = self.nodes[0]
        self.p -= node_to_remove.ln_id
        self.assertNotIn(node_to_remove.ln_id, self.p.order)

    def test_popleft(self):
        leftmost = self.p.order[0]
        self.assertEqual(self.p.popleft(), leftmost)
        self.assertNotIn(leftmost, self.p.order)

    def test_exclude_node(self):
        node_to_exclude = self.nodes[0]
        self.p.exclude(node_to_exclude.ln_id)
        self.assertNotIn(node_to_exclude.ln_id, self.p.order)

    def test_clear(self):
        self.p.clear()
        self.assertEqual(len(self.p), 0)

    def test_to_dict(self):
        p_dict = self.p.to_dict()
        self.assertEqual(p_dict["order"], self.p.order)
        self.assertEqual(p_dict["name"], self.p.name)

    def test_bool(self):
        self.assertTrue(bool(self.p))

    def test_remove_nonexistent_node(self):
        non_existent_node = Node()
        with self.assertRaises(ItemNotFoundError):
            self.p.remove(non_existent_node.ln_id)

    def test_pop_index_error(self):
        with self.assertRaises(ItemNotFoundError):
            self.p.pop(100)

    def test_popleft_index_error(self):
        empty_prog = Progression()
        with self.assertRaises(ItemNotFoundError):
            empty_prog.popleft()

    def test_iteration(self):
        nodes_list = [node.ln_id for node in self.nodes]
        for i, node in enumerate(self.p):
            self.assertEqual(node, nodes_list[i])

    def test_contains(self):
        node_to_check = self.nodes[0]
        self.assertIn(node_to_check.ln_id, self.p)

    def test_not_contains(self):
        non_existent_node = Node()
        self.assertNotIn(non_existent_node.ln_id, self.p)

    def test_equality(self):
        new_prog = Progression(order=[node.ln_id for node in self.nodes])
        self.assertEqual(self.p.order, new_prog.order)

    def test_inequality(self):
        new_node = Node()
        new_prog = self.p + new_node
        self.assertNotEqual(self.p.order, new_prog)


if __name__ == "__main__":
    unittest.main()
