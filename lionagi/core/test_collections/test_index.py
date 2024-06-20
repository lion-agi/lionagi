from lionagi.os.collections.index.index import Index
from lionagi.os.collections.container.container import Container
import unittest


class TestIndex(unittest.TestCase):

    def setUp(self):
        self.flat_dict = {
            "a/0": 1,
            "a/1": 2,
            "a/2/b": 3,
            "c/d": 4,
            "c/e/f": 5,
            "g/h": None,
        }
        self.index = Index(self.flat_dict)

    def test_initialization(self):
        self.assertIsInstance(self.index, Index)
        self.assertEqual(self.index.flat_dict, self.flat_dict)

    def test_is_valid_index(self):
        self.assertTrue(self.index.is_valid_index("a/0"))
        self.assertFalse(self.index.is_valid_index("nonexistent"))

    def test_get_value(self):
        self.assertEqual(self.index.get_value("a/0"), 1)
        with self.assertRaises(KeyError):
            self.index.get_value("nonexistent")

    def test_set_value(self):
        self.index.set_value("a/0", 10)
        self.assertEqual(self.index.get_value("a/0"), 10)
        with self.assertRaises(KeyError):
            self.index.set_value("nonexistent", 10)

    def test_delete_value(self):
        self.index.delete_value("a/0")
        with self.assertRaises(KeyError):
            self.index.get_value("a/0")
        with self.assertRaises(KeyError):
            self.index.delete_value("nonexistent")

    def test_get_container(self):
        indices = ["a/0", "a/1", "a/2/b"]
        container = self.index.get_container(indices)
        self.assertIsInstance(container, Container)

    def test_build_structure(self):
        indices = ["a/0", "a/1", "a/2/b"]
        structure = self.index._build_structure(indices)
        expected_structure = {"a": [1, 2, {"b": 3}]}
        self.assertEqual(structure, expected_structure)

    def test_convert_dict_to_list(self):
        structure = {"0": 1, "1": 2, "2": {"b": 3}}
        converted = self.index._convert_dict_to_list(structure)
        self.assertEqual(converted, [1, 2, {"b": 3}])

    def test_validate_indices_all_valid(self):
        indices = ["a/0", "a/1", "c/d"]
        try:
            self.index.validate_indices(indices)
        except KeyError:
            self.fail("validate_indices raised KeyError unexpectedly!")

    def test_validate_indices_some_invalid(self):
        indices = ["a/0", "nonexistent"]
        with self.assertRaises(KeyError):
            self.index.validate_indices(indices)

    def test_set_value_nested_index(self):
        self.index.set_value("a/2/b", 30)
        self.assertEqual(self.index.get_value("a/2/b"), 30)

    def test_get_container_mixed_indices(self):
        indices = ["a/0", "c/d", "c/e/f"]
        container = self.index.get_container(indices)
        self.assertIsInstance(container, Container)

    def test_build_structure_deeper_nested(self):
        indices = ["a/0", "c/d", "c/e/f"]
        structure = self.index._build_structure(indices)
        expected_structure = {"a": [1], "c": {"d": 4, "e": {"f": 5}}}
        self.assertEqual(structure, expected_structure)

    def test_handle_none_value(self):
        self.assertEqual(self.index.get_value("g/h"), None)
        self.index.set_value("g/h", 6)
        self.assertEqual(self.index.get_value("g/h"), 6)

    def test_build_structure_complex_nested(self):
        indices = ["a/0", "a/1", "a/2/b", "c/d", "c/e/f", "g/h"]
        structure = self.index._build_structure(indices)
        expected_structure = {
            "a": [1, 2, {"b": 3}],
            "c": {"d": 4, "e": {"f": 5}},
            "g": {"h": None},
        }
        self.assertEqual(structure, expected_structure)

    def test_set_value_to_none_index(self):
        self.index.set_value("g/h", 100)
        self.assertEqual(self.index.get_value("g/h"), 100)

    def test_get_container_with_none_and_mixed_types(self):
        indices = ["a/0", "c/d", "g/h"]
        container = self.index.get_container(indices)
        expected_structure = {"a": [1], "c": {"d": 4}, "g": {"h": None}}
        self.assertEqual(container.get_current_structure(), expected_structure)

    def test_convert_dict_to_list_non_digit_keys(self):
        structure = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        converted = self.index._convert_dict_to_list(structure)
        self.assertEqual(converted, {"a": 1, "b": {"c": 2, "d": {"e": 3}}})


if __name__ == "__main__":
    unittest.main(argv=[""], verbosity=2, exit=False)
