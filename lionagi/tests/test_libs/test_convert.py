from lionagi.libs.ln_convert import *
import unittest


class TestToList(unittest.TestCase):

    def test_empty_input(self):
        self.assertEqual(to_list([]), [])

    def test_single_element(self):
        self.assertEqual(to_list(5), [5])

    def test_list_input(self):
        self.assertEqual(to_list([1, [2, 3]], flatten=False), [1, [2, 3]])

    def test_nested_list(self):
        self.assertEqual(to_list([[1, 2], [3, 4]], flatten=True), [1, 2, 3, 4])

    def test_non_list_iterable(self):
        self.assertEqual(to_list((1, 2, 3)), [1, 2, 3])

    def test_string_handling(self):
        self.assertEqual(to_list("abc"), ["abc"])

    def test_drop_none(self):
        self.assertEqual(to_list([1, None, 2], dropna=True), [1, 2])

    class FaultyIterable:
        """An iterable class that raises an exception when iterated over."""

        def __iter__(self):
            return self

        def __next__(self):
            raise RuntimeError("Fault during iteration")

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            to_list(TestToList.FaultyIterable())


class TestIsStructureHomogeneous(unittest.TestCase):

    def test_homogeneous_structure_list(self):
        test_list = [[1, 2], [3, 4]]
        self.assertTrue(is_structure_homogeneous(test_list))

    def test_homogeneous_structure_dict(self):
        test_dict = {"a": {"b": 1}, "c": {"d": 2}}
        self.assertTrue(is_structure_homogeneous(test_dict))

    def test_heterogeneous_structure(self):
        test_structure = {"a": [1, 2], "b": {"c": 3}}
        self.assertFalse(is_structure_homogeneous(test_structure))

    def test_empty_structure(self):
        self.assertTrue(is_structure_homogeneous([]))
        self.assertTrue(is_structure_homogeneous({}))

    def test_return_structure_type_flag(self):
        test_list = [1, 2, 3]
        is_homogeneous, structure_type = is_structure_homogeneous(
            test_list, return_structure_type=True
        )
        self.assertTrue(is_homogeneous)
        self.assertIs(structure_type, list)

        test_dict = {"a": 1, "b": 2}
        is_homogeneous, structure_type = is_structure_homogeneous(
            test_dict, return_structure_type=True
        )
        self.assertTrue(is_homogeneous)
        self.assertIs(structure_type, dict)

        test_mixed = [1, {"a": 2}]
        is_homogeneous, structure_type = is_structure_homogeneous(
            test_mixed, return_structure_type=True
        )
        self.assertFalse(is_homogeneous)
        self.assertIsNone(structure_type)

    def test_deeply_nested_structures(self):
        test_structure = {"a": [{"b": 1}, {"c": [2, 3]}]}
        self.assertFalse(is_structure_homogeneous(test_structure))


if __name__ == "__main__":
    unittest.main()
