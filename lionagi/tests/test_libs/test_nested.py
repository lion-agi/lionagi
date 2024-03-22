import unittest
from lionagi.libs.ln_nested import *


class TestNSet(unittest.TestCase):
    def test_nset_on_dict(self):
        """Test setting a value in a nested dictionary."""
        data = {"a": {"b": [10, 20]}}
        nset(data, ["a", "b", 1], 99)
        self.assertEqual(data, {"a": {"b": [10, 99]}})

    def test_nset_on_list(self):
        """Test setting a value in a nested list."""
        data = [0, [1, 2], 3]
        nset(data, [1, 1], 99)
        self.assertEqual(data, [0, [1, 99], 3])

    def test_nset_with_empty_indices(self):
        """Test nset with an empty indices list."""
        with self.assertRaises(ValueError):
            nset({}, [], 1)

    def test_nget_with_valid_path(self):
        """Test retrieving a value from a nested structure."""
        data = {"a": {"b": [10, 20, 30]}}
        self.assertEqual(nget(data, ["a", "b", 2]), 30)

    def test_nget_with_default(self):
        """Test nget returning a default value when the path doesn't exist."""
        data = {"a": 1}
        self.assertEqual(nget(data, ["b"], default=99), 99)

    def test_nget_raises_lookup_error(self):
        """Test nget raises LookupError when no default is provided and the path doesn't exist."""
        with self.assertRaises(LookupError):
            nget({"a": 1}, ["b"])

    def test_flatten_and_unflatten_dict(self):
        """Test flattening and then unflattening a nested dictionary."""
        original = {"a": {"b": {"c": 1}}}
        flattened = flatten(original)
        self.assertEqual(flattened, {"a_b_c": 1})
        unflattened = unflatten(flattened)
        self.assertEqual(original, unflattened)

    def test_nfilter_dict(self):
        """Test filtering items in a dictionary."""
        data = {"a": 1, "b": 2, "c": 3}
        filtered = nfilter(data, lambda x: x[1] > 1)
        self.assertEqual(filtered, {"b": 2, "c": 3})

    def test_nfilter_list(self):
        """Test filtering items in a list."""
        data = [1, 2, 3, 4]
        filtered = nfilter(data, lambda x: x % 2 == 0)
        self.assertEqual(filtered, [2, 4])

    def test_ninsert_into_nested_dict(self):
        """Test inserting a value into a nested dictionary."""
        data = {"a": {"b": [1, 2]}}
        ninsert(data, ["a", "b", 2], 3)
        self.assertEqual(data, {"a": {"b": [1, 2, 3]}})

    def test_ninsert_into_nested_list(self):
        """Test inserting a value into a nested list."""
        data = []
        ninsert(data, [0, "a"], 1)
        self.assertEqual(data, [{"a": 1}])


class TestNFilter(unittest.TestCase):

    def test_filter_dictionary_with_condition(self):
        test_dict = {"a": 1, "b": 2, "c": 3}
        result = nfilter(test_dict, lambda item: item[1] > 1)
        self.assertEqual(result, {"b": 2, "c": 3})

    def test_filter_list_with_condition(self):
        test_list = [1, 2, 3, 4]
        result = nfilter(test_list, lambda x: x % 2 == 0)
        self.assertEqual(result, [2, 4])

    def test_filter_empty_dictionary(self):
        self.assertEqual(nfilter({}, lambda item: item[1] > 1), {})

    def test_filter_empty_list(self):
        self.assertEqual(nfilter([], lambda x: x % 2 == 0), [])

    def test_filter_all_items_fail_condition(self):
        test_dict = {"a": 1, "b": 2, "c": 3}
        self.assertEqual(nfilter(test_dict, lambda item: item[1] > 5), {})

    def test_filter_all_items_pass_condition(self):
        test_list = [1, 2, 3, 4]
        self.assertEqual(nfilter(test_list, lambda x: x > 0), test_list)

    def test_filter_nested_collections(self):
        nested_dict = {"a": [1, 2, 3], "b": [4, 5]}
        result = nfilter(nested_dict, lambda item: len(item[1]) > 2)
        self.assertEqual(result, {"a": [1, 2, 3]})

    def test_filter_invalid_collection_type(self):
        with self.assertRaises(TypeError):
            nfilter("not a dict or list", lambda x: x)

    def test_filter_with_complex_conditions(self):
        test_dict = {"a": 1, "b": 2, "c": 3, "d": 4}
        # Condition: key is not 'a' and value is an even number
        result = nfilter(test_dict, lambda item: item[0] != "a" and item[1] % 2 == 0)
        self.assertEqual(result, {"b": 2, "d": 4})


class TestNSet(unittest.TestCase):

    def test_set_value_in_nested_dict(self):
        nested_dict = {"a": {"b": 1}}
        nset(nested_dict, ["a", "b"], 2)
        self.assertEqual(nested_dict["a"]["b"], 2)

    def test_set_value_in_nested_list(self):
        nested_list = [[1, 2], [3, 4]]
        nset(nested_list, [1, 0], 5)
        self.assertEqual(nested_list[1][0], 5)

    def test_set_with_empty_indices_list(self):
        with self.assertRaises(ValueError):
            nset({}, [], 1)

    def test_set_in_non_list_dict(self):
        with self.assertRaises(TypeError):
            nset(1, [0], "value")

    def test_set_with_index_out_of_bounds(self):
        test_list = [1, 2, 3]
        nset(test_list, [5], 4)
        self.assertEqual(test_list[5], 4)

    def test_set_with_non_existent_dict_key(self):
        test_dict = {"a": 1}
        nset(test_dict, ["b"], 2)
        self.assertEqual(test_dict["b"], 2)

    def test_set_with_mixed_indices_types(self):
        nested_structure = {"a": [1, {"b": 2}]}
        nset(nested_structure, ["a", 1, "b"], 3)
        self.assertEqual(nested_structure["a"][1]["b"], 3)


class TestNGet(unittest.TestCase):

    def test_get_value_from_nested_dict(self):
        nested_dict = {"a": {"b": 1}}
        result = nget(nested_dict, ["a", "b"])
        self.assertEqual(result, 1)

    def test_get_value_from_nested_list(self):
        nested_list = [[1, 2], [3, 4]]
        result = nget(nested_list, [1, 0])
        self.assertEqual(result, 3)

    # def test_get_with_non_existent_key_index(self):
    #     nested_dict = {'a': 1}
    #     result = nget(nested_dict, ['b'])
    #     self.assertIsNone(result)

    #     nested_list = [1, 2, 3]
    #     result = nget(nested_list, [5])
    #     self.assertIsNone(result)

    def test_get_with_mixed_indices(self):
        nested_structure = {"a": [1, {"b": 2}]}
        result = nget(nested_structure, ["a", 1, "b"])
        self.assertEqual(result, 2)

    # def test_get_with_invalid_structure_type(self):  #     result = nget(1, [0])  # Attempting to retrieve from an integer, not a list/dict  #     self.assertIsNone(result)

    # def test_get_with_index_out_of_bounds(self):  #     test_list = [1, 2, 3]  #     result = nget(test_list, [5])  #     self.assertIsNone(result)


class TestNMerge(unittest.TestCase):

    def test_merge_list_of_dictionaries(self):
        dict_list = [{"a": 1}, {"b": 2}]
        result = nmerge(dict_list)
        self.assertEqual(result, {"a": 1, "b": 2})

    def test_merge_list_of_lists(self):
        list_of_lists = [[1, 2], [3, 4]]
        result = nmerge(list_of_lists)
        self.assertEqual(result, [1, 2, 3, 4])

    def test_merge_empty_list(self):
        self.assertEqual(nmerge([]), {})

    def test_dict_update_option(self):
        dict_list = [{"a": 1}, {"a": 2, "b": 3}]
        result = nmerge(dict_list, overwrite=True)
        self.assertEqual(result, {"a": 2, "b": 3})

    def test_dict_sequence_option(self):
        dict_list = [{"a": 1}, {"a": 2}]
        result = nmerge(dict_list, dict_sequence=True, sequence_separator="_")
        self.assertIn("a", result)
        self.assertIn("a_1", result)

    def test_sort_list_option(self):
        list_of_lists = [[3, 1], [4, 2]]
        result = nmerge(list_of_lists, sort_list=True)
        self.assertEqual(result, [1, 2, 3, 4])

    def test_custom_sort_function(self):
        list_of_lists = [["b", "a"], ["d", "c"]]
        custom_sort_func = lambda x: x
        result = nmerge(list_of_lists, sort_list=True, custom_sort=custom_sort_func)
        self.assertEqual(result, ["a", "b", "c", "d"])

    def test_inhomogeneous_type_error(self):
        mixed_list = [{"a": 1}, [1, 2]]
        with self.assertRaises(TypeError):
            nmerge(mixed_list)


class TestFlatten(unittest.TestCase):

    def test_flatten_nested_dict(self):
        nested_dict = {"a": {"b": 1, "c": {"d": 2}}}
        result = flatten(nested_dict)
        self.assertEqual(result, {"a_b": 1, "a_c_d": 2})

    def test_flatten_nested_list(self):
        nested_list = [[1, 2], [3, [4, 5]]]
        result = flatten(nested_list)
        self.assertEqual(result, {"0_0": 1, "0_1": 2, "1_0": 3, "1_1_0": 4, "1_1_1": 5})

    def test_flatten_with_max_depth(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        result = flatten(nested_dict, max_depth=1)
        self.assertEqual(result, {"a_b": {"c": 1}})

    def test_flatten_dict_only(self):
        nested_mix = {"a": [1, 2], "b": {"c": 3}}
        result = flatten(nested_mix, dict_only=True)
        self.assertEqual(result, {"a": [1, 2], "b_c": 3})

    def test_flatten_inplace(self):
        nested_dict = {"a": {"b": 1}}
        flatten(nested_dict, inplace=True)
        self.assertEqual(nested_dict, {"a_b": 1})

    def test_flatten_empty_structure(self):
        self.assertEqual(flatten({}), {})
        self.assertEqual(flatten([]), {})

    def test_flatten_deeply_nested_structure(self):
        deeply_nested = {"a": {"b": {"c": {"d": 1}}}}
        result = flatten(deeply_nested)
        self.assertEqual(result, {"a_b_c_d": 1})


class TestUnflatten(unittest.TestCase):

    def test_unflatten_to_nested_dict(self):
        flat_dict = {"a_b": 1, "a_c_d": 2}
        result = unflatten(flat_dict)
        self.assertEqual(result, {"a": {"b": 1, "c": {"d": 2}}})

    def test_unflatten_to_nested_list(self):
        flat_dict = {"0_0": 1, "0_1": 2, "1": [3, 4]}
        result = unflatten(flat_dict)
        self.assertEqual(result, [[1, 2], [3, 4]])

    def test_unflatten_with_custom_separator(self):
        flat_dict = {"a-b": 1, "a-c-d": 2}
        result = unflatten(flat_dict, sep="-")
        self.assertEqual(result, {"a": {"b": 1, "c": {"d": 2}}})

    def test_unflatten_with_custom_logic(self):
        flat_dict = {"a_1": "one", "a_2": "two"}
        custom_logic = lambda key: int(key) if key.isdigit() else key
        result = unflatten(flat_dict, custom_logic=custom_logic)
        self.assertEqual(result, {"a": [None, "one", "two"]})

    def test_unflatten_with_max_depth(self):
        flat_dict = {"a_b_c": 1, "a_b_d": 2}
        result = unflatten(flat_dict, max_depth=1)
        self.assertEqual(result, {"a": {"b_c": 1, "b_d": 2}})

    def test_unflatten_with_max_depth_int(self):
        flat_dict = {"0_0_0": 1, "0_1_0": 2}
        result = unflatten(flat_dict, max_depth=1)
        self.assertEqual(result, [[{"0_0": 1}, {"1_0": 2}]])

    def test_unflatten_empty_flat_dict(self):
        self.assertEqual(unflatten({}), [])

    def test_unflatten_to_mixed_structure(self):
        flat_dict = {"0_0": 1, "1_key": 2}
        result = unflatten(flat_dict)
        self.assertEqual(result, [[1], {"key": 2}])


class TestNInsert(unittest.TestCase):

    def test_insert_into_nested_dict(self):
        obj = {}
        ninsert(obj, ["a", "b"], 1)
        self.assertEqual(obj, {"a": {"b": 1}})

    def test_insert_into_nested_list(self):
        obj = []
        ninsert(obj, [0, 1], "value")
        self.assertEqual(obj, [[None, "value"]])

    def test_insert_with_mixed_paths(self):
        obj = {"a": [{}]}
        ninsert(obj, ["a", 0, "b"], 2)
        self.assertEqual(obj, {"a": [{"b": 2}]})

    def test_insert_with_max_depth(self):
        obj = {}
        ninsert(obj, ["a", "b", "c"], "value", max_depth=1)
        self.assertEqual(obj, {"a": {"b_c": "value"}})

    def test_insert_into_empty_structure(self):
        obj = {}
        ninsert(obj, ["a"], 1)
        self.assertEqual(obj, {"a": 1})


class TestGetFlattenedKeys(unittest.TestCase):

    def test_get_keys_from_nested_dict(self):
        nested_dict = {"a": {"b": 1, "c": {"d": 2}}}
        expected_keys = ["a_b", "a_c_d"]
        self.assertEqual(set(get_flattened_keys(nested_dict)), set(expected_keys))

    def test_get_keys_from_nested_list(self):
        nested_list = [[1, 2], [3, [4, 5]]]
        expected_keys = ["0_0", "0_1", "1_0", "1_1_0", "1_1_1"]
        self.assertEqual(set(get_flattened_keys(nested_list)), set(expected_keys))

    def test_get_keys_with_max_depth(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        expected_keys = ["a_b"]
        self.assertEqual(
            set(get_flattened_keys(nested_dict, max_depth=1)), set(expected_keys)
        )

    def test_get_keys_dict_only(self):
        nested_mix = {"a": [1, 2], "b": {"c": 3}}
        expected_keys = ["a", "b_c"]
        self.assertEqual(
            set(get_flattened_keys(nested_mix, dict_only=True)), set(expected_keys)
        )

    def test_get_keys_from_empty_structure(self):
        self.assertEqual(get_flattened_keys({}), [])

    def test_keys_from_deeply_nested_structure(self):
        deeply_nested = {"a": {"b": {"c": {"d": 1}}}}
        expected_keys = ["a_b_c_d"]
        self.assertEqual(set(get_flattened_keys(deeply_nested)), set(expected_keys))


if __name__ == "__main__":
    unittest.main()
