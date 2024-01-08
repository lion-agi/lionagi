import unittest

from ..utils.flat_util import *

class TestFlattenDict(unittest.TestCase): 

    def test_flatten_empty_dict(self): 
        self.assertEqual(flatten_dict({}), {})

    def test_flatten_flat_dict(self):
        self.assertEqual(flatten_dict({'a': 1, 'b': 2, 'c': 3}), {'a': 1, 'b': 2, 'c': 3})

    def test_flatten_nested_dict(self):
        nested_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3, 'f': 4}}}
        expected_flat_dict = {'a': 1, 'b_c': 2, 'b_d_e': 3, 'b_d_f': 4}
        self.assertEqual(flatten_dict(nested_dict), expected_flat_dict)

    def test_flatten_dict_with_custom_separator(self):
        nested_dict = {'a': {'b': 1, 'c': {'d': 2}}}
        expected_flat_dict = {'a.b': 1, 'a.c.d': 2}
        self.assertEqual(flatten_dict(nested_dict, sep='.'), expected_flat_dict)

    def test_flatten_dict_with_empty_subdict(self):
        nested_dict = {'a': 1, 'b': {}}
        expected_flat_dict = {'a': 1}
        self.assertEqual(flatten_dict(nested_dict), expected_flat_dict)

    def test_flatten_dict_with_non_dict_values(self):
        nested_dict = {'a': [1, 2, 3], 'b': 'string', 'c': {'d': 4}}
        expected_flat_dict = {'a': [1, 2, 3], 'b': 'string', 'c_d': 4}
        self.assertEqual(flatten_dict(nested_dict), expected_flat_dict)

class TestFlattenList(unittest.TestCase): 
    def test_flatten_empty_list(self): self.assertEqual(flatten_list([]), [])

    def test_flatten_flat_list(self):
        self.assertEqual(flatten_list([1, 2, 3]), [1, 2, 3])

    def test_flatten_nested_list(self):
        self.assertEqual(flatten_list([1, [2, [3, 4]], 5]), [1, 2, 3, 4, 5])

    def test_flatten_list_with_None(self):
        self.assertEqual(flatten_list([1, None, [2, None], 3], dropna=True), [1, 2, 3])
        self.assertEqual(flatten_list([1, None, [2, None], 3], dropna=False), [1, None, 2, None, 3])

    def test_flatten_list_with_other_datatypes(self):
        self.assertEqual(flatten_list([1, "string", [2, (3, 4)], 5]), [1, "string", 2, (3, 4), 5])

    def test_flatten_list_with_multiple_nested_lists(self):
        self.assertEqual(flatten_list([[1, [2, 3]], [4, [5, [6, 7]]]]), [1, 2, 3, 4, 5, 6, 7])

class TestChangeSeparator(unittest.TestCase):

    def test_change_separator_basic(self):
        input_dict = {'a_b': 1, 'a_b_c': 2, 'd': 3}
        expected_dict = {'a-b': 1, 'a-b-c': 2, 'd': 3}
        result_dict = change_separator(input_dict, '_', '-')
        self.assertEqual(expected_dict, result_dict)

    def test_change_separator_no_change(self):
        input_dict = {'a-b': 1, 'b-c': 2}
        expected_dict = {'a-b': 1, 'b-c': 2}
        result_dict = change_separator(input_dict, '_', '-')
        self.assertEqual(expected_dict, result_dict)

    def test_change_separator_empty_dict(self):
        self.assertEqual({}, change_separator({}, '_', '-'))

    def test_change_separator_same_separators(self):
        input_dict = {'a_b': 1, 'b_c': 2}
        expected_dict = {'a_b': 1, 'b_c': 2}
        result_dict = change_separator(input_dict, '_', '_')
        self.assertEqual(expected_dict, result_dict)

    def test_change_separator_multiple_occurrences(self):
        input_dict = {'a_b_c_b': 1, 'd_e_f_e': 2}
        expected_dict = {'a-b-c-b': 1, 'd-e-f-e': 2}
        result_dict = change_separator(input_dict, '_', '-')
        self.assertEqual(expected_dict, result_dict)
        
class TestUnflattenDict(unittest.TestCase):

    def test_unflatten_simple(self):
        flat_dict = {'a_b_c': 1, 'a_b_d': 2}
        expected = {'a': {'b': {'c': 1, 'd': 2}}}
        self.assertEqual(unflatten_dict(flat_dict), expected)

    def test_unflatten_with_int_keys(self):
        flat_dict = {'1_2_3': 'a', '1_2_4': 'b'}
        expected = {1: {2: {3: 'a', 4: 'b'}}}
        self.assertEqual(unflatten_dict(flat_dict), expected)

    def test_unflatten_with_mixed_keys(self):
        flat_dict = {'a_2_c': 1, 'a_2_d': 2, 'b_3': 3}
        expected = {'a': {2: {'c': 1, 'd': 2}}, 'b': {3: 3}}
        self.assertEqual(unflatten_dict(flat_dict), expected)

    def test_unflatten_with_custom_separator(self):
        flat_dict = {'a|b|c': 1, 'a|b|d': 2}
        expected = {'a': {'b': {'c': 1, 'd': 2}}}
        self.assertEqual(unflatten_dict(flat_dict, sep='|'), expected)

    def test_unflatten_with_non_dict_value(self):
        flat_dict = {'a_b': [1, 2, 3], 'a_c': (4, 5)}
        expected = {'a': {'b': [1, 2, 3], 'c': (4, 5)}}
        self.assertEqual(unflatten_dict(flat_dict), expected)

    def test_unflatten_with_nested_list(self):
        flat_dict = {'a_0': 1, 'a_1': 2, 'b_0': 3, 'b_1': 4}
        expected = {'a': [1, 2], 'b': [3, 4]}
        self.assertEqual(unflatten_dict(flat_dict), expected)

    def test_unflatten_with_overlapping_keys(self):
        flat_dict = {'a_b': 1, 'a': 2}
        with self.assertRaises(ValueError):
            unflatten_dict(flat_dict)

class TestIsFlattenable(unittest.TestCase):

    def test_flattenable_dict(self):
        self.assertTrue(is_flattenable({'a': {'b': 1}, 'c': [2, 3]}))

    def test_flattenable_list(self):
        self.assertTrue(is_flattenable([1, {'a': 2}, [3]]))

    def test_non_flattenable_dict(self):
        self.assertFalse(is_flattenable({'a': 1, 'b': 2}))

    def test_non_flattenable_list(self):
        self.assertFalse(is_flattenable([1, 2, 3]))

    def test_empty_dict(self):
        self.assertFalse(is_flattenable({}))

    def test_empty_list(self):
        self.assertFalse(is_flattenable([]))

    def test_non_flattenable_types(self):
        self.assertFalse(is_flattenable(1))
        self.assertFalse(is_flattenable(1.0))
        self.assertFalse(is_flattenable('string'))
        self.assertFalse(is_flattenable(None))

    def test_nested_mix_flattenable(self):
        self.assertTrue(is_flattenable({'a': [{'b': 1}], 'c': (2, 3)}))

    def test_deeply_nested_flattenable(self):
        self.assertTrue(is_flattenable({'a': {'b': {'c': {'d': [1]}}}}))
        

def default_logic_func(parent_key, key, value, sep='_'):
    new_key = f"{parent_key}{sep}{key}" if parent_key else key
    return new_key, value


class TestFlattenWithCustomLogic(unittest.TestCase):
    def test_flatten_dict(self):
        input_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        expected_output = {'a': 1, 'b_c': 2, 'b_d_e': 3}
        self.assertEqual(flatten_with_custom_logic(input_dict, default_logic_func), expected_output)

    def test_flatten_list(self):
        input_list = [1, 2, [3, 4]]
        expected_output = {'0': 1, '1': 2, '2_0': 3, '2_1': 4}
        self.assertEqual(flatten_with_custom_logic(input_list, default_logic_func), expected_output)


    def test_empty_dict(self):
        self.assertEqual(flatten_with_custom_logic({}, default_logic_func), {})

    def test_empty_list(self):
        self.assertEqual(flatten_with_custom_logic([], default_logic_func), {})

    def test_nested_combination(self):
        input_obj = {'a': [{'b': 1}, {'c': 2}], 'd': []}
        expected_output = {'a_0_b': 1, 'a_1_c': 2, 'd': None}
        self.assertEqual(flatten_with_custom_logic(input_obj, default_logic_func), expected_output)

    def test_custom_separator(self):
        input_obj = {'a': 1, 'b': {'c': 2}}
        expected_output = {'a': 1, 'b#c': 2}
        self.assertEqual(flatten_with_custom_logic(input_obj, default_logic_func, sep='#'), expected_output)

    def test_logic_func_none(self):
        input_obj = {'a': 1, 'b': {'c': 2}}
        expected_output = {'a': 1, 'b_c': 2}
        self.assertEqual(flatten_with_custom_logic(input_obj, None), expected_output)

    def test_obj_with_none_values(self):
        input_obj = {'a': None, 'b': {'c': None}}
        expected_output = {'a': None, 'b_c': None}
        self.assertEqual(flatten_with_custom_logic(input_obj, default_logic_func), expected_output)

    def test_custom_logic_func(self):
        def custom_logic(parent_key, key, value, sep='_'):
            new_key = f"{parent_key}{sep}{key}".upper() if parent_key else key.upper()
            return new_key, value*2 if isinstance(value, int) else value
        
        input_obj = {'a': 1, 'b': {'c': 2}}
        expected_output = {'A': 2, 'B_C': 4}
        self.assertEqual(flatten_with_custom_logic(input_obj, custom_logic), expected_output)

class TestDynamicFlatten(unittest.TestCase):

    def test_flatten_dict(self):
        sample_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        flattened = dynamic_flatten(sample_dict)
        expected = {'a': 1, 'b_c': 2, 'b_d_e': 3}
        self.assertEqual(flattened, expected)

    def test_flatten_list(self):
        sample_list = [1, 2, [3, 4]]
        flattened = dynamic_flatten(sample_list)
        expected = {'0': 1, '1': 2, '2_0': 3, '2_1': 4}
        self.assertEqual(flattened, expected)

    def test_flatten_with_max_depth(self):
        sample_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        flattened = dynamic_flatten(sample_dict, max_depth=1)
        expected = {'a': 1, 'b_c': 2, 'b_d': {'e': 3}}
        self.assertEqual(flattened, expected)

    def test_flatten_with_different_separator(self):
        sample_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        flattened = dynamic_flatten(sample_dict, sep='.')
        expected = {'a': 1, 'b.c': 2, 'b.d.e': 3}
        self.assertEqual(flattened, expected)

    def test_flatten_empty_dictionary(self):
        sample_dict = {}
        flattened = dynamic_flatten(sample_dict)
        expected = {}
        self.assertEqual(flattened, expected)

    def test_flatten_empty_list(self):
        sample_list = []
        flattened = dynamic_flatten(sample_list)
        expected = {}
        self.assertEqual(flattened, expected)

    def test_flatten_non_dict_non_list(self):
        with self.assertRaises(TypeError):
            dynamic_flatten(42)

    def test_flatten_nested_empty_dict(self):
        sample_dict = {'a': {}, 'b': {'c': {}}}
        flattened = dynamic_flatten(sample_dict)
        expected = {'a': {}, 'b_c': {}}
        self.assertEqual(flattened, expected)

    def test_flatten_nested_empty_list(self):
        sample_list = [1, [], [3, []]]
        flattened = dynamic_flatten(sample_list)
        expected = {'0': 1, '1': [], '2_0': 3, '2_1': []}
        self.assertEqual(flattened, expected)
        
# class TestDynamicUnflatten(unittest.TestCase):

#     def test_unflatten_dict(self):
#         flat_dict = {'a': 1, 'b_c': 2, 'b_d_e': 3}
#         expected = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
#         self.assertEqual(dynamic_unflatten(flat_dict), expected)


#     def test_unflatten_with_different_separator(self):
#         flat_dict = {'a': 1, 'b.c': 2, 'b.d.e': 3}
#         expected = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
#         self.assertEqual(dynamic_unflatten(flat_dict, sep='.'), expected)

#     def test_unflatten_empty_dict(self):
#         flat_dict = {}
#         expected = []
#         self.assertEqual(dynamic_unflatten(flat_dict), expected)

#     def test_unflatten_empty_string_keys(self):
#         flat_dict = {'': 1}
#         expected = {'': 1}
#         self.assertEqual(dynamic_unflatten(flat_dict), expected)

#     def test_unflatten_single_key(self):
#         flat_dict = {'a': 1}
#         expected = {'a': 1}
#         self.assertEqual(dynamic_unflatten(flat_dict), expected)

#     def test_unflatten_nested_empty_dict(self):
#         flat_dict = {'a': {}, 'b_c': {}}
#         expected = {'a': {}, 'b': {'c': {}}}
#         self.assertEqual(dynamic_unflatten(flat_dict), expected)


#     def test_unflatten_max_depth(self):
#         flat_dict = {'a_b_c_d_e': 1}
#         expected = {'a': {'b': {'c': {'d': {'e': 1}}}}}
#         self.assertEqual(dynamic_unflatten(flat_dict, max_depth=3), expected)
        
class TestUnflattenToList(unittest.TestCase): 
    
    def test_unflatten_simple_list(self): 
        flat_dict = {'0': 'a', '1': 'b', '2': 'c'} 
        expected = ['a', 'b', 'c'] 
        self.assertEqual(unflatten_to_list(flat_dict), expected)

    def test_unflatten_nested_dicts_in_list(self):
        flat_dict = {'0_a': 'value1', '1_b': 'value2', '2_c_d': 'value3'}
        expected = [{'a': 'value1'}, {'b': 'value2'}, {'c': {'d': 'value3'}}]
        self.assertEqual(unflatten_to_list(flat_dict), expected)

    def test_unflatten_empty_dict(self):
        flat_dict = {}
        expected = []
        self.assertEqual(unflatten_to_list(flat_dict), expected)

    def test_unflatten_with_custom_separator(self):
        flat_dict = {'0-a': 'value1', '1-b': 'value2', '2-c-d': 'value3'}
        expected = [{'a': 'value1'}, {'b': 'value2'}, {'c': {'d': 'value3'}}]
        self.assertEqual(unflatten_to_list(flat_dict, sep='-'), expected)

    def test_unflatten_with_sparse_indices(self):
        flat_dict = {'0': 'value1', '2': 'value2', '5': 'value3'}
        expected = ['value1', None, 'value2', None, None, 'value3']
        self.assertEqual(unflatten_to_list(flat_dict), expected)
    
    def test_unflatten_with_negative_indices(self):
        flat_dict = {'-1': 'value1', '1': 'value2'}
        with self.assertRaises(ValueError):  # Expect ValueError instead of IndexError
            unflatten_to_list(flat_dict)

    def test_unflatten_with_custom_separator(self):
        flat_dict = {'0-a': 'value1', '1-b': 'value2', '2-c-d': 'value3'}
        expected = [{'a': 'value1'}, {'b': 'value2'}, {'c': {'d': 'value3'}}]
        self.assertEqual(unflatten_to_list(flat_dict, sep='-'), expected)
        

class TestFlattenIterable(unittest.TestCase):

    def test_flatten_empty_list(self):
        self.assertEqual(list(flatten_iterable([])), [])

    def test_flatten_nested_lists(self):
        nested_list = [1, [2, [3, 4], 5], 6]
        expected_flat_list = [1, 2, 3, 4, 5, 6]
        self.assertEqual(list(flatten_iterable(nested_list)), expected_flat_list)

    def test_flatten_nested_tuples(self):
        nested_tuple = (1, (2, (3, 4), 5), 6)
        expected_flat_list = [1, 2, 3, 4, 5, 6]
        self.assertEqual(list(flatten_iterable(nested_tuple)), expected_flat_list)

    def test_flatten_with_max_depth(self):
        nested_list = [1, [2, [3, 4], 5], 6]
        expected_flat_list_depth_1 = [1, [2, [3, 4], 5], 6]
        self.assertEqual(list(flatten_iterable(nested_list, max_depth=1)), expected_flat_list_depth_1)
        
        expected_flat_list_depth_2 = [1, 2, [3, 4], 5, 6]
        self.assertEqual(list(flatten_iterable(nested_list, max_depth=2)), expected_flat_list_depth_2)

    # def test_flatten_strings(self):
    #     nested_list = ["hello", ["world", ["!"]]]
    #     expected_flat_list = ["hello", "world", ["!"]]
    #     self.assertEqual(list(flatten_iterable(nested_list)), expected_flat_list)

    def test_flatten_with_non_iterable(self):
        nested_list = [1, [2, 3], 4, "text", 5]
        expected_flat_list = [1, 2, 3, 4, "text", 5]
        self.assertEqual(list(flatten_iterable(nested_list)), expected_flat_list)

    def test_flatten_with_none_max_depth(self):
        nested_list = [1, [2, [3, [4, [5]]]]]
        expected_flat_list = [1, 2, 3, 4, 5]
        self.assertEqual(list(flatten_iterable(nested_list, max_depth=None)), expected_flat_list)

    def test_flatten_iterable_to_list_function(self):
        nested_list = [1, [2, [3, 4], 5], 6]
        expected_flat_list = [1, 2, 3, 4, 5, 6]
        self.assertEqual(flatten_iterable_to_list(nested_list), expected_flat_list)

        nested_list_with_depth = [1, [2, [3, [4, [5]]]]]
        expected_flat_list_with_depth = [1, 2, [3, [4, [5]]]]
        self.assertEqual(flatten_iterable_to_list(nested_list_with_depth, max_depth=2), expected_flat_list_with_depth)
        
        
class TestUnflattenDictWithCustomLogic(unittest.TestCase):
    
    @staticmethod
    def logic_func_upper(key: str, value: Any) -> Tuple[str, Any]:
        return key.upper(), value

    @staticmethod
    def logic_func_append_prefix(key: str, value: Any) -> Tuple[str, Any]:
 
        return f"prefix_{key}", value

    # def test_unflatten_dict_with_uppercase_logic(self):
    #     flat_dict = {'a_1': 10, 'b_2': 20, 'c_sub_1': 30}
    #     expected_dict = {'A': {'1': 10}, 'B': {'2': 20}, 'C_SUB': {'1': 30}}
    #     self.assertEqual(
    #         unflatten_dict_with_custom_logic(flat_dict, self.logic_func_upper),
    #         expected_dict
    #     )

    # def test_unflatten_dict_with_prefix_logic(self):
    #     flat_dict = {'a_1': 10, 'b_2': 20, 'c_sub_1': 30}
    #     expected_dict = {'prefix_a': {'prefix_1': 10}, 'prefix_b': {'prefix_2': 20}, 'prefix_c_sub': {'prefix_1': 30}}
    #     self.assertEqual(
    #         unflatten_dict_with_custom_logic(flat_dict, self.logic_func_append_prefix),
    #         expected_dict
    #     )

    def test_unflatten_dict_with_no_modification_logic(self):
        flat_dict = {'a_1': 10, 'b_2': 20, 'c_sub_1': 30}
        identity_logic_func = lambda key, value: (key, value)
        expected_dict = {'a': {'1': 10}, 'b': {'2': 20}, 'c': {'sub': {'1': 30}}}
        self.assertEqual(
            unflatten_dict_with_custom_logic(flat_dict, identity_logic_func),
            expected_dict
        )

    def test_unflatten_dict_empty(self):
        flat_dict = {}
        self.assertEqual(
            unflatten_dict_with_custom_logic(flat_dict, self.logic_func_upper),
            {}
        )
        
if __name__ == "main":
    unittest.main()