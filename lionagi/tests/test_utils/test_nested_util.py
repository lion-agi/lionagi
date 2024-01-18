import unittest
import lionagi.utils.nested_util as n_util

class TestNFilter(unittest.TestCase):

    def test_filter_dictionary_with_condition(self):
        test_dict = {'a': 1, 'b': 2, 'c': 3}
        result = n_util.nfilter(test_dict, lambda item: item[1] > 1)
        self.assertEqual(result, {'b': 2, 'c': 3})

    def test_filter_list_with_condition(self):
        test_list = [1, 2, 3, 4]
        result = n_util.nfilter(test_list, lambda x: x % 2 == 0)
        self.assertEqual(result, [2, 4])

    def test_filter_empty_dictionary(self):
        self.assertEqual(n_util.nfilter({}, lambda item: item[1] > 1), {})

    def test_filter_empty_list(self):
        self.assertEqual(n_util.nfilter([], lambda x: x % 2 == 0), [])

    def test_filter_all_items_fail_condition(self):
        test_dict = {'a': 1, 'b': 2, 'c': 3}
        self.assertEqual(n_util.nfilter(test_dict, lambda item: item[1] > 5), {})

    def test_filter_all_items_pass_condition(self):
        test_list = [1, 2, 3, 4]
        self.assertEqual(n_util.nfilter(test_list, lambda x: x > 0), test_list)

    def test_filter_nested_collections(self):
        nested_dict = {'a': [1, 2, 3], 'b': [4, 5]}
        result = n_util.nfilter(nested_dict, lambda item: len(item[1]) > 2)
        self.assertEqual(result, {'a': [1, 2, 3]})

    def test_filter_invalid_collection_type(self):
        with self.assertRaises(TypeError):
            n_util.nfilter("not a dict or list", lambda x: x)

    def test_filter_with_complex_conditions(self):
        test_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        # Condition: key is not 'a' and value is an even number
        result = n_util.nfilter(test_dict, lambda item: item[0] != 'a' and item[1] % 2 == 0)
        self.assertEqual(result, {'b': 2, 'd': 4})


class TestNSet(unittest.TestCase):

    def test_set_value_in_nested_dict(self):
        nested_dict = {'a': {'b': 1}}
        n_util.nset(nested_dict, ['a', 'b'], 2)
        self.assertEqual(nested_dict['a']['b'], 2)

    def test_set_value_in_nested_list(self):
        nested_list = [[1, 2], [3, 4]]
        n_util.nset(nested_list, [1, 0], 5)
        self.assertEqual(nested_list[1][0], 5)

    def test_set_with_empty_indices_list(self):
        with self.assertRaises(ValueError):
            n_util.nset({}, [], 1)

    def test_set_in_non_list_dict(self):
        with self.assertRaises(TypeError):
            n_util.nset(1, [0], 'value')

    def test_set_with_index_out_of_bounds(self):
        test_list = [1, 2, 3]
        n_util.nset(test_list, [5], 4)
        self.assertEqual(test_list[5], 4)

    def test_set_with_non_existent_dict_key(self):
        test_dict = {'a': 1}
        n_util.nset(test_dict, ['b'], 2)
        self.assertEqual(test_dict['b'], 2)

    def test_set_with_mixed_indices_types(self):
        nested_structure = {'a': [1, {'b': 2}]}
        n_util.nset(nested_structure, ['a', 1, 'b'], 3)
        self.assertEqual(nested_structure['a'][1]['b'], 3)


class TestNGet(unittest.TestCase):

    def test_get_value_from_nested_dict(self):
        nested_dict = {'a': {'b': 1}}
        result = n_util.nget(nested_dict, ['a', 'b'])
        self.assertEqual(result, 1)

    def test_get_value_from_nested_list(self):
        nested_list = [[1, 2], [3, 4]]
        result = n_util.nget(nested_list, [1, 0])
        self.assertEqual(result, 3)

    def test_get_with_non_existent_key_index(self):
        nested_dict = {'a': 1}
        result = n_util.nget(nested_dict, ['b'])
        self.assertIsNone(result)

        nested_list = [1, 2, 3]
        result = n_util.nget(nested_list, [5])
        self.assertIsNone(result)

    def test_get_with_mixed_indices(self):
        nested_structure = {'a': [1, {'b': 2}]}
        result = n_util.nget(nested_structure, ['a', 1, 'b'])
        self.assertEqual(result, 2)

    def test_get_with_invalid_structure_type(self):
        result = n_util.nget(1, [0])  # Attempting to retrieve from an integer, not a list/dict
        self.assertIsNone(result)

    def test_get_with_index_out_of_bounds(self):
        test_list = [1, 2, 3]
        result = n_util.nget(test_list, [5])
        self.assertIsNone(result)


class TestIsStructureHomogeneous(unittest.TestCase):

    def test_homogeneous_structure_list(self):
        test_list = [[1, 2], [3, 4]]
        self.assertTrue(n_util.is_structure_homogeneous(test_list))

    def test_homogeneous_structure_dict(self):
        test_dict = {'a': {'b': 1}, 'c': {'d': 2}}
        self.assertTrue(n_util.is_structure_homogeneous(test_dict))

    def test_heterogeneous_structure(self):
        test_structure = {'a': [1, 2], 'b': {'c': 3}}
        self.assertFalse(n_util.is_structure_homogeneous(test_structure))

    def test_empty_structure(self):
        self.assertTrue(n_util.is_structure_homogeneous([]))
        self.assertTrue(n_util.is_structure_homogeneous({}))

    def test_return_structure_type_flag(self):
        test_list = [1, 2, 3]
        is_homogeneous, structure_type = n_util.is_structure_homogeneous(test_list, return_structure_type=True)
        self.assertTrue(is_homogeneous)
        self.assertIs(structure_type, list)

        test_dict = {'a': 1, 'b': 2}
        is_homogeneous, structure_type = n_util.is_structure_homogeneous(test_dict, return_structure_type=True)
        self.assertTrue(is_homogeneous)
        self.assertIs(structure_type, dict)

        test_mixed = [1, {'a': 2}]
        is_homogeneous, structure_type = n_util.is_structure_homogeneous(test_mixed, return_structure_type=True)
        self.assertFalse(is_homogeneous)
        self.assertIsNone(structure_type)

    def test_deeply_nested_structures(self):
        test_structure = {'a': [{'b': 1}, {'c': [2, 3]}]}
        self.assertFalse(n_util.is_structure_homogeneous(test_structure))

class TestNMerge(unittest.TestCase):

    def test_merge_list_of_dictionaries(self):
        dict_list = [{'a': 1}, {'b': 2}]
        result = n_util.nmerge(dict_list)
        self.assertEqual(result, {'a': 1, 'b': 2})

    def test_merge_list_of_lists(self):
        list_of_lists = [[1, 2], [3, 4]]
        result = n_util.nmerge(list_of_lists)
        self.assertEqual(result, [1, 2, 3, 4])

    def test_merge_empty_list(self):
        self.assertEqual(n_util.nmerge([]), {})

    def test_dict_update_option(self):
        dict_list = [{'a': 1}, {'a': 2, 'b': 3}]
        result = n_util.nmerge(dict_list, dict_update=True)
        self.assertEqual(result, {'a': 2, 'b': 3})

    def test_dict_sequence_option(self):
        dict_list = [{'a': 1}, {'a': 2}]
        result = n_util.nmerge(dict_list, dict_sequence=True, sequence_separator='_')
        self.assertIn('a', result)
        self.assertIn('a_1', result)

    def test_sort_list_option(self):
        list_of_lists = [[3, 1], [4, 2]]
        result = n_util.nmerge(list_of_lists, sort_list=True)
        self.assertEqual(result, [1, 2, 3, 4])

    def test_custom_sort_function(self):
        list_of_lists = [['b', 'a'], ['d', 'c']]
        custom_sort_func = lambda x: x
        result = n_util.nmerge(list_of_lists, sort_list=True, custom_sort=custom_sort_func)
        self.assertEqual(result, ['a', 'b', 'c', 'd'])

    def test_inhomogeneous_type_error(self):
        mixed_list = [{'a': 1}, [1, 2]]
        with self.assertRaises(TypeError):
            n_util.nmerge(mixed_list)


class TestFlatten(unittest.TestCase):

    def test_flatten_nested_dict(self):
        nested_dict = {'a': {'b': 1, 'c': {'d': 2}}}
        result = n_util.flatten(nested_dict)
        self.assertEqual(result, {'a_b': 1, 'a_c_d': 2})

    def test_flatten_nested_list(self):
        nested_list = [[1, 2], [3, [4, 5]]]
        result = n_util.flatten(nested_list)
        self.assertEqual(result, {'0_0': 1, '0_1': 2, '1_0': 3, '1_1_0': 4, '1_1_1': 5})

    def test_flatten_with_max_depth(self):
        nested_dict = {'a': {'b': {'c': 1}}}
        result = n_util.flatten(nested_dict, max_depth=1)
        self.assertEqual(result, {'a_b': {'c': 1}})

    def test_flatten_dict_only(self):
        nested_mix = {'a': [1, 2], 'b': {'c': 3}}
        result = n_util.flatten(nested_mix, dict_only=True)
        self.assertEqual(result, {'a': [1, 2], 'b_c': 3})

    def test_flatten_inplace(self):
        nested_dict = {'a': {'b': 1}}
        n_util.flatten(nested_dict, inplace=True)
        self.assertEqual(nested_dict, {'a_b': 1})

    def test_flatten_empty_structure(self):
        self.assertEqual(n_util.flatten({}), {})
        self.assertEqual(n_util.flatten([]), {})

    def test_flatten_deeply_nested_structure(self):
        deeply_nested = {'a': {'b': {'c': {'d': 1}}}}
        result = n_util.flatten(deeply_nested)
        self.assertEqual(result, {'a_b_c_d': 1})


class TestUnflatten(unittest.TestCase):

    def test_unflatten_to_nested_dict(self):
        flat_dict = {'a_b': 1, 'a_c_d': 2}
        result = n_util.unflatten(flat_dict)
        self.assertEqual(result, {'a': {'b': 1, 'c': {'d': 2}}})

    def test_unflatten_to_nested_list(self):
        flat_dict = {'0_0': 1, '0_1': 2, '1': [3, 4]}
        result = n_util.unflatten(flat_dict)
        self.assertEqual(result, [[1, 2], [3, 4]])

    def test_unflatten_with_custom_separator(self):
        flat_dict = {'a-b': 1, 'a-c-d': 2}
        result = n_util.unflatten(flat_dict, sep='-')
        self.assertEqual(result, {'a': {'b': 1, 'c': {'d': 2}}})

    def test_unflatten_with_custom_logic(self):
        flat_dict = {'a_1': 'one', 'a_2': 'two'}
        custom_logic = lambda key: int(key) if key.isdigit() else key
        result = n_util.unflatten(flat_dict, custom_logic=custom_logic)
        self.assertEqual(result, {'a': [None, 'one', 'two']})

    def test_unflatten_with_max_depth(self):
        flat_dict = {'a_b_c': 1, 'a_b_d': 2}
        result = n_util.unflatten(flat_dict, max_depth=1)
        self.assertEqual(result, {'a': {'b_c': 1, 'b_d': 2}})

    def test_unflatten_with_max_depth_int(self):
        flat_dict = {'0_0_0': 1, '0_1_0': 2}
        result = n_util.unflatten(flat_dict, max_depth=1)
        self.assertEqual(result, [[{'0_0': 1}, {'1_0': 2}]])

    def test_unflatten_empty_flat_dict(self):
        self.assertEqual(n_util.unflatten({}), [])

    def test_unflatten_to_mixed_structure(self):
        flat_dict = {'0_0': 1, '1_key': 2}
        result = n_util.unflatten(flat_dict)
        self.assertEqual(result, [[1], {'key': 2}])


class TestNInsert(unittest.TestCase):

    def test_insert_into_nested_dict(self):
        obj = {}
        n_util.ninsert(obj, ['a', 'b'], 1)
        self.assertEqual(obj, {'a': {'b': 1}})

    def test_insert_into_nested_list(self):
        obj = []
        n_util.ninsert(obj, [0, 1], 'value')
        self.assertEqual(obj, [[None, 'value']])

    def test_insert_with_mixed_paths(self):
        obj = {'a': [{}]}
        n_util.ninsert(obj, ['a', 0, 'b'], 2)
        self.assertEqual(obj, {'a': [{'b': 2}]})

    def test_insert_with_max_depth(self):
        obj = {}
        n_util.ninsert(obj, ['a', 'b', 'c'], 'value', max_depth=1)
        self.assertEqual(obj, {'a': {'b_c': 'value'}})

    def test_insert_into_empty_structure(self):
        obj = {}
        n_util.ninsert(obj, ['a'], 1)
        self.assertEqual(obj, {'a': 1})


class TestGetFlattenedKeys(unittest.TestCase):

    def test_get_keys_from_nested_dict(self):
        nested_dict = {'a': {'b': 1, 'c': {'d': 2}}}
        expected_keys = ['a_b', 'a_c_d']
        self.assertEqual(set(n_util.get_flattened_keys(nested_dict)), set(expected_keys))

    def test_get_keys_from_nested_list(self):
        nested_list = [[1, 2], [3, [4, 5]]]
        expected_keys = ['0_0', '0_1', '1_0', '1_1_0', '1_1_1']
        self.assertEqual(set(n_util.get_flattened_keys(nested_list)), set(expected_keys))

    def test_get_keys_with_max_depth(self):
        nested_dict = {'a': {'b': {'c': 1}}}
        expected_keys = ['a_b']
        self.assertEqual(set(n_util.get_flattened_keys(nested_dict, max_depth=1)), set(expected_keys))

    def test_get_keys_dict_only(self):
        nested_mix = {'a': [1, 2], 'b': {'c': 3}}
        expected_keys = ['a', 'b_c']
        self.assertEqual(set(n_util.get_flattened_keys(nested_mix, dict_only=True)), set(expected_keys))

    def test_get_keys_from_empty_structure(self):
        self.assertEqual(n_util.get_flattened_keys({}), [])

    def test_keys_from_deeply_nested_structure(self):
        deeply_nested = {'a': {'b': {'c': {'d': 1}}}}
        expected_keys = ['a_b_c_d']
        self.assertEqual(set(n_util.get_flattened_keys(deeply_nested)), set(expected_keys))


if __name__ == '__main__':
    unittest.main()
