import unittest
from unittest.mock import AsyncMock, patch
from pydantic import ValidationError
from lionagi.os.collections.abc import Component, get_lion_id, LionIDable, Condition
from lionagi.os.collections.edge.edge import Edge
from lionagi.os.collections.edge.edge_condition import EdgeCondition


class TestEdge(unittest.TestCase):

    def setUp(self):
        self.node1 = Component()
        self.node2 = Component()
        self.edge = Edge(head=self.node1.ln_id, tail=self.node2.ln_id)

    def test_initialization(self):
        """Test initialization of the Edge class."""
        self.assertEqual(self.edge.head, self.node1.ln_id)
        self.assertEqual(self.edge.tail, self.node2.ln_id)
        self.assertIsNone(self.edge.condition)
        self.assertIsNone(self.edge.label)
        self.assertFalse(self.edge.bundle)

    async def test_check_condition_without_condition(self):
        """Test check_condition raises ValueError when condition is not set."""
        with self.assertRaises(ValueError):
            await self.edge.check_condition({})

    @patch("lionagi.core.models.edge.EdgeCondition.applies", new_callable=AsyncMock)
    async def test_check_condition_with_condition(self, mock_applies):
        """Test check_condition with a set condition."""
        mock_applies.return_value = True
        condition = EdgeCondition()
        self.edge.condition = condition
        result = await self.edge.check_condition({})
        self.assertTrue(result)
        mock_applies.assert_awaited_once()

    def test_validate_head_tail(self):
        """Test the head and tail validation."""
        try:
            valid_id = get_lion_id("valid_head")
        except Exception as e:
            if e.__class__.__name__ == "LionTypeError":
                return
        self.assertEqual(Edge._validate_head_tail(valid_id), valid_id)
        with self.assertRaises(ValidationError):
            Edge._validate_head_tail("invalid_id")

    def test_string_condition_none(self):
        """Test string_condition method when condition is None."""
        self.assertIsNone(self.edge.string_condition())

    def test_len(self):
        """Test the __len__ method."""
        self.assertEqual(len(self.edge), 1)

    def test_contains(self):
        """Test the __contains__ method."""
        self.assertIn(self.node1.ln_id, self.edge)
        self.assertIn(self.node2.ln_id, self.edge)
        fake_node = Component()
        self.assertNotIn(fake_node.ln_id, self.edge)


if __name__ == "__main__":
    unittest.main()
