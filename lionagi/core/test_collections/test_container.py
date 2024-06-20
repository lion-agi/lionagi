from lionagi.os.collections.container.container import Container

import unittest


class TestContainer(unittest.TestCase):

    def setUp(self):
        nested_structure = {"a": [1, 2, {"b": 3}], "c": {"d": 4}}
        self.container = Container(nested_structure)

    def test_initialization(self):
        self.assertIsInstance(self.container, Container)
        self.assertEqual(
            self.container.get_current_structure(),
            {"a": [1, 2, {"b": 3}], "c": {"d": 4}},
        )

    def test_next(self):
        self.assertEqual(self.container.next(), "a")
        self.assertEqual(self.container.next(), "c")
        self.assertIsNone(self.container.next())

    def test_get_current(self):
        self.container.next()  # move to 'a'
        self.assertEqual(self.container.get_current(), [1, 2, {"b": 3}])

    def test_get_current_key(self):
        self.container.next()  # move to 'a'
        self.assertEqual(self.container.get_current_key(), "a")

    def test_set_current(self):
        new_structure = {"0": 1, "1": 2, "2": {"b": 3}}
        self.container.set_current(new_structure)
        self.assertEqual(self.container.get_current_structure(), [1, 2, {"b": 3}])

    def test_set_current_key(self):
        self.container.next()
        self.container.set_current_key("a")
        self.assertEqual(self.container.get_current_key(), "a")
        self.container.set_current_key("nonexistent")
        self.assertEqual(
            self.container.get_current_key(), "a"
        )  # should not change current key

    def test_get_current_value(self):
        self.container.next()  # move to 'a'
        self.assertEqual(self.container.get_current_value(), [1, 2, {"b": 3}])

    def test_set_current_value(self):
        self.container.next()  # move to 'a'
        self.container.set_current_value([4, 5, {"c": 6}])
        self.assertEqual(self.container.get_current_value(), [4, 5, {"c": 6}])

    def test_convert_to_list(self):
        structure = {"0": 1, "1": 2, "2": {"b": 3}}
        converted = self.container._convert_to_list(structure)
        self.assertEqual(converted, [1, 2, {"b": 3}])

    def test_set_non_existent_current_key(self):
        self.container.set_current_key("nonexistent")
        self.assertIsNone(self.container.get_current_key())

    def test_get_current_no_key(self):
        self.assertIsNone(self.container.get_current())

    def test_set_current_value_no_key(self):
        self.container.set_current_value([7, 8, 9])
        self.assertNotIn([7, 8, 9], self.container.get_current_structure().values())

    def test_set_current_value_new_nested_structure(self):
        self.container.next()  # move to 'a'
        new_nested_structure = {"x": 10, "y": {"z": 11}}
        self.container.set_current_value(new_nested_structure)
        self.assertEqual(self.container.get_current_value(), new_nested_structure)

    def test_convert_to_list_non_digit_keys(self):
        structure = {"a": 1, "b": 2, "c": {"d": 3}}
        converted = self.container._convert_to_list(structure)
        self.assertEqual(converted, {"a": 1, "b": 2, "c": {"d": 3}})

    def test_nested_structure_with_mixed_types(self):
        mixed_structure = {"a": [1, 2, {"b": [3, {"c": 4}]}], "d": {"e": [5, 6]}}
        container = Container(mixed_structure)
        self.assertEqual(
            container.get_current_structure(),
            {"a": [1, 2, {"b": [3, {"c": 4}]}], "d": {"e": [5, 6]}},
        )

    def test_deeply_nested_lists(self):
        deep_structure = [[1, [2, [3, [4]]]]]
        container = Container(deep_structure)
        self.assertEqual(container.get_current_structure(), [[1, [2, [3, [4]]]]])
        container.next()  # move to first list
        self.assertEqual(container.get_current(), [1, [2, [3, [4]]]])

    def test_set_current_different_keys(self):
        new_structure = {"x": 7, "y": 8}
        self.container.set_current(new_structure)
        self.assertEqual(self.container.get_current_structure(), {"x": 7, "y": 8})
        self.container.next()  # move to 'x'
        self.assertEqual(self.container.get_current(), 7)

    def test_next_empty_structure(self):
        empty_container = Container({})
        self.assertIsNone(empty_container.next())

    def test_set_current_value_nested_structure(self):
        self.container.next()  # move to 'a'
        nested_value = {"b": {"c": {"d": 5}}}
        self.container.set_current_value(nested_value)
        self.assertEqual(self.container.get_current_value(), nested_value)


if __name__ == "__main__":
    unittest.main(argv=[""], verbosity=2, exit=False)
