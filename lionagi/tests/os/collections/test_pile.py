import unittest
import asyncio
from lionagi.os.collections.pile.pile import Pile
from lionagi.os.collections.node.node import Node


class TestPile(unittest.TestCase):

    def setUp(self):
        """Create initial nodes and piles for testing."""
        self.nodes1 = [Node(content=i) for i in ["A", "B", "C"]]
        self.nodes2 = [Node(content=i) for i in ["D", "E", "F"]]
        self.p1 = Pile(self.nodes1)
        self.p2 = Pile(self.nodes2)

    def test_add_piles(self):
        """Test adding two piles."""
        combined_pile = self.p1 + self.p2
        self.assertEqual(len(combined_pile), 6)
        contents = [node.content for node in combined_pile.values()]
        self.assertListEqual(contents, ["A", "B", "C", "D", "E", "F"])

    def test_subtract_piles(self):
        """Test subtracting nodes from a pile."""
        with self.assertRaises(Exception):
            result_pile = self.p1 - self.nodes2[0]  # D not in p1

    def test_containment(self):
        """Test containment check."""
        self.assertIn(self.nodes1[1], self.p1)  # B in p1
        self.assertNotIn(self.nodes2[0], self.p1)  # D not in p1

    def test_include_nodes(self):
        """Test including nodes in a pile."""
        self.p1.include(self.nodes2)
        self.assertEqual(len(self.p1), 6)
        contents = [node.content for node in self.p1.values()]
        self.assertListEqual(contents, ["A", "B", "C", "D", "E", "F"])

    def test_exclude_nodes(self):
        """Test excluding nodes from a pile."""
        self.p1.include(self.nodes2)  # Include first to have something to exclude
        self.p1.exclude(self.nodes2)
        self.assertEqual(len(self.p1), 5)
        contents = [node.content for node in self.p1.values()]
        self.assertListEqual(contents, ["A", "B", "C", "E", "F"])

    def test_get_item_by_index(self):
        """Test getting an item by index."""
        node = self.p1[0]
        self.assertEqual(node.content, "A")

    def test_set_item_by_index(self):
        """Test setting an item at a specific index."""
        new_node = Node(content="Updated Node")
        self.p1[0] = new_node
        self.assertEqual(self.p1[0].content, "Updated Node")

    def test_insert_item(self):
        """Test inserting an item at a specific position."""
        new_node = Node(content="Inserted Node")
        self.p1.insert(0, new_node)
        self.assertEqual(self.p1[0].content, "Inserted Node")
        self.assertEqual(len(self.p1), 4)

    def test_homogenous(self):
        """Test if all items in the pile are of the same type."""
        self.assertTrue(self.p1.is_homogenous())
        with self.assertRaises(AttributeError):
            mixed_pile = Pile(self.nodes1 + [123])  # Adding an int to mix types

    def test_is_empty(self):
        """Test if the pile is empty."""
        empty_pile = Pile()
        self.assertTrue(empty_pile.is_empty())
        self.assertFalse(self.p1.is_empty())

    def test_pop_item(self):
        """Test popping an item from the pile."""
        popped_node = self.p1.pop(self.nodes1[0].ln_id)
        self.assertEqual(popped_node.content, "A")
        self.assertEqual(len(self.p1), 2)

    def test_clear_pile(self):
        """Test clearing the pile."""
        self.p1.clear()
        self.assertTrue(self.p1.is_empty())

    def test_update_pile(self):
        """Test updating the pile with another pile."""
        self.p1.update(self.p2)
        self.assertEqual(len(self.p1), 6)
        contents = [node.content for node in self.p1.values()]
        self.assertListEqual(contents, ["A", "B", "C", "D", "E", "F"])

    def test_to_dataframe(self):
        """Test converting the pile to a DataFrame."""
        df = self.p1.to_df()
        self.assertEqual(len(df), 3)
        self.assertListEqual(df["content"].tolist(), ["A", "B", "C"])

    def test_create_index(self):
        """Test creating an index for the pile."""
        with self.assertRaises(ValueError):
            self.p1.create_index(index_type="llama_index")

    def test_create_query_engine(self):
        """Test creating a query engine for the pile."""
        with self.assertRaises(ValueError):
            self.p1.create_query_engine(index_type="llama_index")

    def test_create_chat_engine(self):
        """Test creating a chat engine for the pile."""
        with self.assertRaises(ValueError):
            self.p1.create_chat_engine(index_type="llama_index")

    # async def test_query_pile(self):
    #     """Test querying the pile."""
    #     self.p1.create_query_engine(index_type="llama_index")
    #     response = await self.p1.query_pile(query="test query")
    #     self.assertIsInstance(response, str)

    # async def test_chat_pile(self):
    #     """Test chatting with the pile."""
    #     self.p1.create_chat_engine(index_type="llama_index")
    #     response = await self.p1.chat_pile(query="test chat")
    #     self.assertIsInstance(response, str)

    # async def test_embed_pile(self):
    #     """Test embedding the items in the pile."""
    #     await self.p1.embed_pile()
    #     for node in self.p1.values():
    #         self.assertIn("embedding", node._all_fields)

    def test_to_csv(self):
        """Test saving the pile to a CSV file."""
        self.p1.to_csv("test_pile.csv")
        with open("test_pile.csv", "r") as f:
            content = f.read()
        self.assertIn("content", content)

    def test_from_csv(self):
        """Test loading a pile from a CSV file."""
        self.p1.to_csv("test_pile.csv")
        loaded_pile = Pile.from_csv("test_pile.csv")
        self.assertEqual(len(loaded_pile), 3)
        self.assertEqual(loaded_pile[0].content, "A")

    def test_from_dataframe(self):
        """Test loading a pile from a DataFrame."""
        df = self.p1.to_df()
        loaded_pile = Pile.from_df(df)
        self.assertEqual(len(loaded_pile), 3)
        self.assertEqual(loaded_pile[0].content, "A")

    def test_as_query_tool(self):
        """Test creating a query tool for the pile."""
        with self.assertRaises(ValueError):
            tool = self.p1.as_query_tool(index_type="llama_index")

    def test_str_representation(self):
        """Test the string representation of the pile."""
        self.assertIsInstance(str(self.p1), str)

    def test_repr_representation(self):
        """Test the representation of the pile."""
        self.assertIsInstance(repr(self.p1), str)


if __name__ == "__main__":
    unittest.main()
