import numpy as np
import pandas as pd
from lionagi.os.libs.data_handlers import *
from lionagi.os.libs.data_handlers._util import *
from lionagi.os.libs.data_handlers._flatten import (
    _dynamic_flatten_in_place,
    _dynamic_flatten_generator,
)
from lionagi.os.libs.data_handlers._nfilter import _filter_dict, _filter_list
from lionagi.os.libs.data_handlers._ninsert import handle_list_insert
from lionagi.os.libs.data_handlers._nmerge import (
    _deep_merge_dicts,
    _merge_dicts,
    _merge_sequences,
)
from lionagi.os.libs.data_handlers._nset import ensure_list_index
from lionagi.os.libs.data_handlers._to_num import (
    str_to_num,
    _convert_to_num,
    _extract_numbers,
)


import unittest


class TestFlattenFunctions(unittest.TestCase):

    def test_flatten_dict(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        expected_output = {"a[^_^]b[^_^]c": 1}
        self.assertEqual(flatten(nested_dict), expected_output)

    def test_flatten_list(self):
        nested_list = [1, [2, [3]]]
        expected_output = {"0": 1, "1[^_^]0": 2, "1[^_^]1[^_^]0": 3}
        self.assertEqual(flatten(nested_list), expected_output)

    def test_flatten_mixed_structure(self):
        nested_structure = {"a": [1, {"b": 2}]}
        expected_output = {"a[^_^]0": 1, "a[^_^]1[^_^]b": 2}
        self.assertEqual(flatten(nested_structure), expected_output)

    def test_flatten_with_max_depth(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        expected_output = {"a[^_^]b": {"c": 1}}
        self.assertEqual(flatten(nested_dict, max_depth=1), expected_output)

    def test_flatten_dict_only(self):
        nested_structure = {"a": [1, {"b": 2}]}
        expected_output = {"a": [1, {"b": 2}]}
        self.assertEqual(flatten(nested_structure, dict_only=True), expected_output)

    def test_flatten_inplace(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        flatten(nested_dict, inplace=True)
        expected_output = {"a[^_^]b[^_^]c": 1}
        self.assertEqual(nested_dict, expected_output)

    def test_flatten_inplace_error(self):
        nested_list = [1, [2, [3]]]
        with self.assertRaises(ValueError):
            flatten(nested_list, inplace=True)

    def test_get_flattened_keys(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        expected_output = ["a[^_^]b[^_^]c"]
        self.assertEqual(get_flattened_keys(nested_dict), expected_output)

    def test_get_flattened_keys_with_max_depth(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        expected_output = ["a[^_^]b"]
        self.assertEqual(get_flattened_keys(nested_dict, max_depth=1), expected_output)

    def test_dynamic_flatten_in_place(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        _dynamic_flatten_in_place(nested_dict)
        expected_output = {"a[^_^]b[^_^]c": 1}
        self.assertEqual(nested_dict, expected_output)

    def test_dynamic_flatten_generator(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        expected_output = {"a[^_^]b[^_^]c": 1}
        result = dict(_dynamic_flatten_generator(nested_dict, ()))
        self.assertEqual(result, expected_output)

    def test_dynamic_flatten_generator_with_max_depth(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        expected_output = {"a[^_^]b": {"c": 1}}
        result = dict(_dynamic_flatten_generator(nested_dict, (), max_depth=1))
        self.assertEqual(result, expected_output)

    def test_dynamic_flatten_generator_list(self):
        nested_list = [1, [2, [3]]]
        expected_output = {"0": 1, "1[^_^]0": 2, "1[^_^]1[^_^]0": 3}
        result = dict(_dynamic_flatten_generator(nested_list, ()))
        self.assertEqual(result, expected_output)


class TestNFilterFunctions(unittest.TestCase):

    def test_nfilter_dict(self):
        nested_dict = {"a": 1, "b": 2, "c": 3}
        condition = lambda item: item[1] > 1
        expected_output = {"b": 2, "c": 3}
        self.assertEqual(nfilter(nested_dict, condition), expected_output)

    def test_nfilter_list(self):
        nested_list = [1, 2, 3, 4, 5]
        condition = lambda x: x % 2 == 0
        expected_output = [2, 4]
        self.assertEqual(nfilter(nested_list, condition), expected_output)

    def test_nfilter_nested_dict(self):
        nested_dict = {"a": {"b": 2, "c": 3}, "d": {"e": 1}}
        condition = lambda item: sum(item[1].values()) > 3
        expected_output = {"a": {"b": 2, "c": 3}}
        self.assertEqual(nfilter(nested_dict, condition), expected_output)

    def test_nfilter_nested_list(self):
        nested_list = [[1, 2], [3, 4], [5, 6]]
        condition = lambda x: sum(x) > 5
        expected_output = [[3, 4], [5, 6]]
        self.assertEqual(nfilter(nested_list, condition), expected_output)

    def test_nfilter_empty_dict(self):
        nested_dict = {}
        condition = lambda item: item[1] > 1
        expected_output = {}
        self.assertEqual(nfilter(nested_dict, condition), expected_output)

    def test_nfilter_empty_list(self):
        nested_list = []
        condition = lambda x: x % 2 == 0
        expected_output = []
        self.assertEqual(nfilter(nested_list, condition), expected_output)

    def test_nfilter_invalid_type(self):
        with self.assertRaises(TypeError):
            nfilter("invalid", lambda x: x)

    def test_filter_dict(self):
        dictionary = {"a": 1, "b": 2, "c": 3}
        condition = lambda item: item[1] > 1
        expected_output = {"b": 2, "c": 3}
        self.assertEqual(_filter_dict(dictionary, condition), expected_output)

    def test_filter_list(self):
        lst = [1, 2, 3, 4, 5]
        condition = lambda x: x % 2 == 0
        expected_output = [2, 4]
        self.assertEqual(_filter_list(lst, condition), expected_output)

    def test_nfilter_complex_nested_list(self):
        nested_list = [{"a": 1}, {"b": 2}, {"c": {"d": 3}}, {"e": {"f": 4}}]
        condition = lambda x: isinstance(x, dict) and "e" in x
        expected_output = [{"e": {"f": 4}}]
        self.assertEqual(nfilter(nested_list, condition), expected_output)

    def test_nfilter_mixed_nested_structure(self):
        nested_structure = {"a": [1, 2], "b": [3, 4], "c": {"d": 5, "e": 6}}
        condition = lambda item: isinstance(item, tuple) and "c" in item
        expected_output = {"c": {"d": 5, "e": 6}}
        self.assertEqual(nfilter(nested_structure, condition), expected_output)

    def test_nfilter_nested_list_of_dicts(self):
        nested_list = [{"a": 1}, {"b": 2, "c": 3}, {"d": 4}]
        condition = lambda x: sum(x.values()) > 3
        expected_output = [{"b": 2, "c": 3}, {"d": 4}]
        self.assertEqual(nfilter(nested_list, condition), expected_output)

    def test_nfilter_nested_dict_of_lists(self):
        nested_dict = {"a": [1, 2], "b": [3, 4, 5], "c": [6]}
        condition = lambda item: len(item[1]) > 2
        expected_output = {"b": [3, 4, 5]}
        self.assertEqual(nfilter(nested_dict, condition), expected_output)


class TestNGetFunction(unittest.TestCase):

    def test_nget_with_valid_dict(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        indices = ["a", "b", "c"]
        self.assertEqual(nget(nested_dict, indices), 1)

    def test_nget_with_valid_list(self):
        nested_list = [1, [2, [3, 4]]]
        indices = [1, 1, 0]
        self.assertEqual(nget(nested_list, indices), 3)

    def test_nget_with_invalid_index_and_default_dict(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        indices = ["a", "b", "d"]
        self.assertEqual(nget(nested_dict, indices, default="default"), "default")

    def test_nget_with_invalid_index_and_default_list(self):
        nested_list = [1, [2, [3, 4]]]
        indices = [1, 2, 0]
        self.assertEqual(nget(nested_list, indices, default="default"), "default")

    def test_nget_with_invalid_index_and_no_default_dict(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        indices = ["a", "b", "d"]
        with self.assertRaises(LookupError):
            nget(nested_dict, indices)

    def test_nget_with_invalid_index_and_no_default_list(self):
        nested_list = [1, [2, [3, 4]]]
        indices = [1, 2, 0]
        with self.assertRaises(LookupError):
            nget(nested_list, indices)

    def test_nget_with_out_of_range_index(self):
        nested_list = [1, [2, [3, 4]]]
        indices = [1, 1, 5]
        with self.assertRaises(LookupError):
            nget(nested_list, indices)

    def test_nget_with_key_error(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        indices = ["a", "x", "c"]
        with self.assertRaises(LookupError):
            nget(nested_dict, indices)

    def test_nget_with_type_error(self):
        nested_list = [1, {"a": 2}, [3, 4]]
        indices = [1, "a", 0]
        with self.assertRaises(LookupError):
            nget(nested_list, indices)

    def test_nget_deeply_nested_mixed_types(self):
        nested_structure = {"a": [{"b": [1, 2, {"c": 3}]}]}
        indices = ["a", 0, "b", 2, "c"]
        self.assertEqual(nget(nested_structure, indices), 3)

    def test_nget_with_single_index(self):
        nested_list = [1, 2, 3]
        indices = [1]
        self.assertEqual(nget(nested_list, indices), 2)

    def test_nget_with_empty_indices(self):
        nested_dict = {"a": 1}
        indices = []
        with self.assertRaises(LookupError):
            nget(nested_dict, indices)

    def test_nget_missing_intermediate_indices(self):
        nested_dict = {"a": {"b": {"c": 1}}}
        indices = ["a", "x", "c"]
        self.assertEqual(nget(nested_dict, indices, default="default"), "default")

    def test_nget_with_none_values(self):
        nested_dict = {"a": {"b": None}}
        indices = ["a", "b"]
        self.assertIsNone(nget(nested_dict, indices))


class TestNInsertFunction(unittest.TestCase):

    def test_ninsert_into_dict(self):
        nested_dict = {"a": {"b": [10, 20]}}
        indices = ["a", "b", 2]
        value = 99
        ninsert(nested_dict, indices, value)
        expected_output = {"a": {"b": [10, 20, 99]}}
        self.assertEqual(nested_dict, expected_output)

    def test_ninsert_into_list(self):
        nested_list = [0, [1, 2], 3]
        indices = [1, 2]
        value = 99
        ninsert(nested_list, indices, value)
        expected_output = [0, [1, 2, 99], 3]
        self.assertEqual(nested_list, expected_output)

    def test_ninsert_create_intermediate_dict(self):
        nested_dict = {}
        indices = ["a", "b", "c"]
        value = 1
        ninsert(nested_dict, indices, value)
        expected_output = {"a": {"b": {"c": 1}}}
        self.assertEqual(nested_dict, expected_output)

    def test_ninsert_create_intermediate_list(self):
        nested_list = []
        indices = [0, 1]
        value = 4
        ninsert(nested_list, indices, value)
        expected_output = [[None, 4]]
        self.assertEqual(nested_list, expected_output)

    def test_ninsert_with_empty_indices(self):
        nested_dict = {"a": {"b": [10, 20]}}
        indices = []
        value = 99
        with self.assertRaises(ValueError):
            ninsert(nested_dict, indices, value)

    def test_ninsert_invalid_container(self):
        nested_list = [0, [1, 2], 3]
        indices = [1, "a"]
        value = 99
        with self.assertRaises(TypeError):
            ninsert(nested_list, indices, value)

    def test_ensure_list_insert(self):
        lst = [1, 2]
        handle_list_insert(lst, 4, 5)
        expected_output = [1, 2, None, None, 5]
        self.assertEqual(lst, expected_output)

    def test_ninsert_dict_in_list(self):
        nested_list = []
        indices = [0, "a"]
        value = 1
        ninsert(nested_list, indices, value)
        expected_output = [{"a": 1}]
        self.assertEqual(nested_list, expected_output)

    def test_ninsert_list_in_dict(self):
        nested_dict = {"a": {}}
        indices = ["a", "b", 1]
        value = 99
        ninsert(nested_dict, indices, value)
        expected_output = {"a": {"b": [None, 99]}}
        self.assertEqual(nested_dict, expected_output)

    # New edge cases

    def test_ninsert_negative_index(self):
        nested_list = [1, [2, 3, 4]]
        indices = [1, -1]
        value = 99
        ninsert(nested_list, indices, value)
        expected_output = [1, [2, 3, 99]]
        self.assertEqual(nested_list, expected_output)

    def test_ninsert_overwrite_existing_value(self):
        nested_dict = {"a": {"b": {"c": 10}}}
        indices = ["a", "b", "c"]
        value = 20
        ninsert(nested_dict, indices, value)
        expected_output = {"a": {"b": {"c": 20}}}
        self.assertEqual(nested_dict, expected_output)

    def test_ninsert_with_max_depth(self):
        nested_dict = {"a": {"b": {"c": 10}}}
        indices = "a/b/e"
        value = 99
        ninsert(nested_dict, indices, value, max_depth=2, sep="/")
        expected_output = {"a": {"b": {"c": 10, "e": 99}}}
        self.assertEqual(nested_dict, expected_output)

    def test_ninsert_list_of_dicts(self):
        nested_list = [{"a": 1}, {"b": 2}]
        indices = [1, "c"]
        value = 3
        ninsert(nested_list, indices, value)
        expected_output = [{"a": 1}, {"b": 2, "c": 3}]
        self.assertEqual(nested_list, expected_output)

    def test_ninsert_complex_structure(self):
        nested_structure = {"a": [1, {"b": [2, {"c": 3}]}]}
        indices = ["a", 1, "b", 1, "d"]
        value = 99
        ninsert(nested_structure, indices, value)
        expected_output = {"a": [1, {"b": [2, {"c": 3, "d": 99}]}]}
        self.assertEqual(nested_structure, expected_output)


class TestNMergeFunction(unittest.TestCase):

    def test_nmerge_with_dicts_overwrite(self):
        nested_structure = [{"a": 1}, {"b": 2}, {"a": 3}]
        expected_output = {"a": 3, "b": 2}
        self.assertEqual(nmerge(nested_structure, overwrite=True), expected_output)

    def test_nmerge_with_dicts_no_overwrite(self):
        nested_structure = [{"a": 1}, {"b": 2}, {"a": 3}]
        expected_output = {"a": [1, 3], "b": 2}
        self.assertEqual(nmerge(nested_structure, overwrite=False), expected_output)

    def test_nmerge_with_dicts_sequence(self):
        nested_structure = [{"a": 1}, {"a": 2}, {"a": 3}]
        expected_output = {"a": 1, "a[^_^]1": 2, "a[^_^]2": 3}
        self.assertEqual(nmerge(nested_structure, dict_sequence=True), expected_output)

    def test_nmerge_with_lists_no_sort(self):
        nested_structure = [[1, 2], [3, 4]]
        expected_output = [1, 2, 3, 4]
        self.assertEqual(nmerge(nested_structure, sort_list=False), expected_output)

    def test_nmerge_with_lists_sort(self):
        nested_structure = [[3, 1], [4, 2]]
        expected_output = [1, 2, 3, 4]
        self.assertEqual(nmerge(nested_structure, sort_list=True), expected_output)

    def test_nmerge_with_lists_custom_sort(self):
        nested_structure = [[3, 1], [4, 2]]
        expected_output = [4, 3, 2, 1]
        self.assertEqual(
            nmerge(nested_structure, sort_list=True, custom_sort=lambda x: -x),
            expected_output,
        )

    def test_nmerge_with_mixed_types(self):
        nested_structure = [{"a": 1}, [2, 3]]
        with self.assertRaises(TypeError):
            nmerge(nested_structure)

    def test_deep_merge_dicts(self):
        dict1 = {"a": {"b": 1}, "c": 3}
        dict2 = {"a": {"d": 2}, "c": 4}
        expected_output = {"a": {"b": 1, "d": 2}, "c": [3, 4]}
        self.assertEqual(_deep_merge_dicts(dict1, dict2), expected_output)

    def test_merge_dicts(self):
        iterables = [{"a": 1}, {"b": 2}, {"a": 3}]
        expected_output = {"a": 3, "b": 2}
        self.assertEqual(
            _merge_dicts(
                iterables,
                dict_update=True,
                dict_sequence=False,
                sequence_separator="|",
            ),
            expected_output,
        )

    def test_merge_dicts_with_sequence(self):
        iterables = [{"a": 1}, {"a": 2}, {"a": 3}]
        expected_output = {"a": 1, "a[^_^]1": 2, "a[^_^]2": 3}
        self.assertEqual(
            _merge_dicts(
                iterables,
                dict_update=False,
                dict_sequence=True,
                sequence_separator="|",
            ),
            expected_output,
        )

    def test_merge_sequences_no_sort(self):
        iterables = [[1, 2], [3, 4]]
        expected_output = [1, 2, 3, 4]
        self.assertEqual(_merge_sequences(iterables, sort_list=False), expected_output)

    def test_merge_sequences_sort(self):
        iterables = [[3, 1], [4, 2]]
        expected_output = [1, 2, 3, 4]
        self.assertEqual(_merge_sequences(iterables, sort_list=True), expected_output)

    def test_merge_sequences_custom_sort(self):
        iterables = [[3, 1], [4, 2]]
        expected_output = [4, 3, 2, 1]
        self.assertEqual(
            _merge_sequences(iterables, sort_list=True, custom_sort=lambda x: -x),
            expected_output,
        )

    def test_nmerge_with_empty_list(self):
        nested_structure = []
        expected_output = {}
        self.assertEqual(nmerge(nested_structure), expected_output)

    def test_nmerge_with_empty_dicts(self):
        nested_structure = [{}, {}]
        expected_output = {}
        self.assertEqual(nmerge(nested_structure), expected_output)

    def test_nmerge_with_empty_lists(self):
        nested_structure = [[], []]
        expected_output = []
        self.assertEqual(nmerge(nested_structure), expected_output)

    def test_nmerge_with_empty_and_non_empty_dicts(self):
        nested_structure = [{}, {"a": 1}, {}]
        expected_output = {"a": 1}
        self.assertEqual(nmerge(nested_structure), expected_output)

    def test_nmerge_with_empty_and_non_empty_lists(self):
        nested_structure = [[], [1, 2], []]
        expected_output = [1, 2]
        self.assertEqual(nmerge(nested_structure), expected_output)

    def test_nmerge_with_nested_dicts(self):
        nested_structure = [{"a": {"b": 1}}, {"a": {"c": 2}}]
        expected_output = {"a": {"b": 1, "c": 2}}
        self.assertEqual(nmerge(nested_structure, overwrite=True), expected_output)

    def test_nmerge_with_nested_lists(self):
        nested_structure = [[[1, 2]], [[3, 4]]]
        expected_output = [[1, 2], [3, 4]]
        self.assertEqual(nmerge(nested_structure, sort_list=False), expected_output)


class TestNSetFunction(unittest.TestCase):

    def test_nset_into_dict(self):
        nested_dict = {"a": {"b": [10, 20]}}
        indices = ["a", "b", 1]
        value = 99
        nset(nested_dict, indices, value)
        expected_output = {"a": {"b": [10, 99]}}
        self.assertEqual(nested_dict, expected_output)

    def test_nset_into_list(self):
        nested_list = [0, [1, 2], 3]
        indices = [1, 1]
        value = 99
        nset(nested_list, indices, value)
        expected_output = [0, [1, 99], 3]
        self.assertEqual(nested_list, expected_output)

    def test_nset_create_intermediate_dict(self):
        nested_dict = {}
        indices = ["a", "b", "c"]
        value = 1
        nset(nested_dict, indices, value)
        expected_output = {"a": {"b": {"c": 1}}}
        self.assertEqual(nested_dict, expected_output)

    def test_nset_create_intermediate_list(self):
        nested_list = []
        indices = [0, 1]
        value = 4
        nset(nested_list, indices, value)
        expected_output = [[None, 4]]
        self.assertEqual(nested_list, expected_output)

    def test_nset_with_empty_indices(self):
        nested_dict = {"a": {"b": [10, 20]}}
        indices = []
        value = 99
        with self.assertRaises(ValueError):
            nset(nested_dict, indices, value)

    def test_nset_invalid_container(self):
        nested_list = [0, [1, 2], 3]
        indices = [1, "a"]
        value = 99
        with self.assertRaises(TypeError):
            nset(nested_list, indices, value)

    def test_ensure_list_index(self):
        lst = [1, 2]
        ensure_list_index(lst, 4)
        expected_output = [1, 2, None, None, None]
        self.assertEqual(lst, expected_output)

    def test_ensure_list_index_with_default(self):
        lst = [1, 2]
        ensure_list_index(lst, 4, default=0)
        expected_output = [1, 2, 0, 0, 0]
        self.assertEqual(lst, expected_output)

    def test_nset_dict_in_list(self):
        nested_list = []
        indices = [0, "a"]
        value = 1
        nset(nested_list, indices, value)
        expected_output = [{"a": 1}]
        self.assertEqual(nested_list, expected_output)

    def test_nset_list_in_dict(self):
        nested_dict = {"a": {}}
        indices = ["a", "b", 1]
        value = 99
        nset(nested_dict, indices, value)
        expected_output = {"a": {"b": [None, 99]}}
        self.assertEqual(nested_dict, expected_output)

    def test_nset_deeply_nested_dict(self):
        nested_dict = {"a": {"b": {"c": {"d": {"e": 5}}}}}
        indices = ["a", "b", "c", "d", "e"]
        value = 99
        nset(nested_dict, indices, value)
        expected_output = {"a": {"b": {"c": {"d": {"e": 99}}}}}
        self.assertEqual(nested_dict, expected_output)

    def test_nset_deeply_nested_list(self):
        nested_list = [[[1, 2, [3, 4]]]]
        indices = [0, 0, 2, 1]
        value = 99
        nset(nested_list, indices, value)
        expected_output = [[[1, 2, [3, 99]]]]
        self.assertEqual(nested_list, expected_output)

    def test_nset_mixed_nested_structure(self):
        nested_structure = {"a": [{"b": {"c": [1, 2, 3]}}]}
        indices = ["a", 0, "b", "c", 2]
        value = 99
        nset(nested_structure, indices, value)
        expected_output = {"a": [{"b": {"c": [1, 2, 99]}}]}
        self.assertEqual(nested_structure, expected_output)

    def test_nset_extend_list_with_none(self):
        nested_list = [1, 2]
        indices = [4]
        value = 99
        nset(nested_list, indices, value)
        expected_output = [1, 2, None, None, 99]
        self.assertEqual(nested_list, expected_output)

    def test_nset_extend_list_with_default_value(self):
        nested_list = [1, 2]
        indices = [4]
        value = 99
        ensure_list_index(nested_list, 4, default=0)
        nset(nested_list, indices, value)
        expected_output = [1, 2, 0, 0, 99]
        self.assertEqual(nested_list, expected_output)

    def test_nset_overwrite_existing_value(self):
        nested_dict = {"a": {"b": {"c": 5}}}
        indices = ["a", "b", "c"]
        value = 99
        nset(nested_dict, indices, value)
        expected_output = {"a": {"b": {"c": 99}}}
        self.assertEqual(nested_dict, expected_output)

    def test_nset_on_shallow_list(self):
        nested_list = [1, 2, 3]
        indices = [1]
        value = 99
        nset(nested_list, indices, value)
        expected_output = [1, 99, 3]
        self.assertEqual(nested_list, expected_output)


class TestToDfFunction(unittest.TestCase):

    def test_single_dict(self):
        data = {"a": [1, 2], "b": [3, 4]}
        df = pd.DataFrame(data)
        self.assertTrue(to_df(data).equals(df))

    def test_list_of_dicts(self):
        data = [{"a": 1, "b": 3}, {"a": 2, "b": 4}]
        df = pd.DataFrame(data)
        self.assertTrue(to_df(data).equals(df))

    def test_dataframe(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        self.assertTrue(to_df(df).equals(df))

    def test_series(self):
        series = pd.Series([1, 2, 3], name="a")
        df = pd.DataFrame(series)
        self.assertTrue(to_df(series).equals(df))

    def test_empty_list(self):
        self.assertTrue(to_df([]).empty)

    def test_list_of_dataframes(self):
        df1 = pd.DataFrame({"a": [1, 2]})
        df2 = pd.DataFrame({"b": [3, 4]})
        combined_df = pd.concat([df1, df2], axis=0)
        combined_df.reset_index(drop=True, inplace=True)
        self.assertTrue(to_df([df1, df2]).equals(combined_df))

    def test_reset_index(self):
        data = {"a": [1, 2], "b": [3, 4]}
        df = pd.DataFrame(data).reset_index(drop=True)
        self.assertTrue(to_df(data, reset_index=True).equals(df))

    def test_dropna(self):
        data = {"a": [1, None], "b": [None, 4]}
        df = pd.DataFrame(data).dropna(how="all")
        self.assertTrue(to_df(data, drop_how="all").equals(df))

    def test_unsupported_type(self):
        with self.assertRaises(ValueError):
            to_df(5)

    def test_list_of_series(self):
        series1 = pd.Series([1, 2, 3], name="a")
        series2 = pd.Series([4, 5, 6], name="b")
        combined_df = pd.concat([series1, series2], axis=1)
        self.assertTrue(to_df([series1, series2]).equals(combined_df))

    def test_list_of_mixed_ndframe(self):
        df = pd.DataFrame({"a": [1, 2]})
        series = pd.Series([3, 4], name="b")
        combined_df = pd.concat([df, series], axis=0)
        combined_df.reset_index(drop=True, inplace=True)
        self.assertTrue(to_df([df, series]).equals(combined_df))

    def test_dict_with_series(self):
        data = {"a": pd.Series([1, 2]), "b": pd.Series([3, 4])}
        df = pd.DataFrame(data)
        self.assertTrue(to_df(data).equals(df))

    def test_list_of_lists(self):
        data = [[1, 2], [3, 4]]
        df = pd.DataFrame(data)
        self.assertTrue(to_df(data).equals(df))

    def test_with_kwargs(self):
        data = {"a": [1, 2], "b": [3, 4]}
        df = pd.DataFrame(data, dtype=float)
        self.assertTrue(to_df(data, dtype=float).equals(df))

    def test_list_of_empty_dataframes(self):
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()
        combined_df = pd.concat([df1, df2], axis=0)
        self.assertTrue(to_df([df1, df2]).equals(combined_df))

    def test_nested_list_of_dicts(self):
        data = [{"a": 1, "b": [{"c": 2}, {"d": 3}]}]
        with self.assertRaises(ValueError):
            to_df(data)


class TestToDictFunction(unittest.TestCase):

    def test_dict_input(self):
        self.assertEqual(to_dict({"a": 1, "b": 2}), {"a": 1, "b": 2})

    def test_list_of_dicts_input(self):
        self.assertEqual(to_dict([{"a": 1}, {"b": 2}]), [{"a": 1}, {"b": 2}])

    def test_json_string(self):
        self.assertEqual(to_dict('{"a": 1, "b": 2}'), {"a": 1, "b": 2})

    def test_dataframe(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        self.assertEqual(to_dict(df), [{"a": 1, "b": 3}, {"a": 2, "b": 4}])

    def test_model_dump(self):
        class Model:
            def model_dump(self):
                return {"a": 1, "b": 2}

        model = Model()
        self.assertEqual(to_dict(model), {"a": 1, "b": 2})

    def test_to_dict_method(self):
        class CustomObject:
            def to_dict(self):
                return {"a": 1, "b": 2}

        obj = CustomObject()
        self.assertEqual(to_dict(obj), {"a": 1, "b": 2})

    def test_dict_method(self):
        class CustomObject:
            def dict(self):
                return {"a": 1, "b": 2}

        obj = CustomObject()
        self.assertEqual(to_dict(obj), {"a": 1, "b": 2})

    def test_unsupported_type(self):
        with self.assertRaises(TypeError):
            to_dict(5)

    def test_list_of_series(self):
        series1 = pd.Series([1, 2, 3], name="a")
        series2 = pd.Series([4, 5, 6], name="b")
        combined_df = pd.concat([series1, series2], axis=1)
        self.assertTrue(
            to_dict(combined_df), [{"a": 1, "b": 4}, {"a": 2, "b": 5}, {"a": 3, "b": 6}]
        )

    def test_list_of_mixed_ndframe(self):
        df = pd.DataFrame({"a": [1, 2]})
        series = pd.Series([3, 4], name="b")
        combined_df = pd.concat([df, series], axis=1)
        self.assertTrue(to_dict(combined_df), [{"a": 1, "b": 3}, {"a": 2, "b": 4}])

    def test_dict_with_series(self):
        data = {"a": pd.Series([1, 2]), "b": pd.Series([3, 4])}
        df = pd.DataFrame(data)
        self.assertEqual(to_dict(df), [{"a": 1, "b": 3}, {"a": 2, "b": 4}])

    def test_list_of_lists(self):
        data = [[1, 2], [3, 4]]
        df = pd.DataFrame(data)
        self.assertTrue(to_dict(df), [{"0": 1, "1": 2}, {"0": 3, "1": 4}])

    def test_with_kwargs(self):
        data = {"a": [1, 2], "b": [3, 4]}
        df = pd.DataFrame(data, dtype=float)
        self.assertTrue(to_dict(df), [{"a": 1.0, "b": 3.0}, {"a": 2.0, "b": 4.0}])

    def test_list_of_empty_dataframes(self):
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()
        combined_df = pd.concat([df1, df2], axis=0)
        self.assertEqual(to_dict(combined_df), {})

    def test_nested_list_of_dicts(self):
        data = [{"a": 1, "b": [{"c": 2}, {"d": 3}]}]
        self.assertEqual(to_dict(data), data[0])

    def test_empty_dict(self):
        self.assertEqual(to_dict({}), {})

    def test_empty_list(self):
        self.assertEqual(to_dict([]), {})

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        self.assertEqual(to_dict(df), {})

    def test_json_list(self):
        self.assertRaises(ValueError, to_dict, '[{"a": 1}, {"b": 2}]')

    def test_dataframe_with_nan(self):
        df = pd.DataFrame({"a": [1, None], "b": [None, 4]})
        expected_output = [{"a": 1, "b": None}, {"a": None, "b": 4}]
        self.assertEqual(to_dict(df), expected_output)

    def test_dataframe_single_column(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        self.assertEqual(to_dict(df), [{"a": 1}, {"a": 2}, {"a": 3}])

    def test_nested_dict(self):
        nested_dict = {"a": 1, "b": {"c": 2, "d": 3}}
        self.assertEqual(to_dict(nested_dict), nested_dict)

    def test_list_of_empty_dicts(self):
        self.assertEqual(to_dict([{}, {}]), [{}, {}])

    def test_string_list(self):
        with self.assertRaises(ValueError):
            to_dict('["a", "b", "c"]')

    def test_custom_json_method(self):
        class CustomObject:
            def json(self):
                return '{"a": 1, "b": 2}'

        obj = CustomObject()
        self.assertEqual(to_dict(obj), {"a": 1, "b": 2})


class TestToListFunction(unittest.TestCase):

    def test_single_non_iterable(self):
        self.assertEqual(to_list(5), [5])
        self.assertEqual(to_list("test"), ["test"])
        self.assertEqual(to_list(b"bytes"), [b"bytes"])

    def test_iterables(self):
        self.assertEqual(to_list([1, 2, 3]), [1, 2, 3])
        self.assertEqual(to_list((1, 2, 3)), [1, 2, 3])
        self.assertEqual(to_list({1, 2, 3}), [1, 2, 3])

    def test_nested_lists(self):
        self.assertEqual(to_list([1, [2, 3], [[4], 5]]), [1, 2, 3, 4, 5])
        self.assertEqual(to_list([1, [2, None], [[4], 5]], dropna=True), [1, 2, 4, 5])
        self.assertEqual(
            to_list([1, [2, None], [[4], 5]], dropna=False), [1, 2, None, 4, 5]
        )

    def test_non_flatten(self):
        self.assertEqual(
            to_list([1, [2, 3], [[4], 5]], flatten=False), [1, [2, 3], [[4], 5]]
        )

    def test_mappings(self):
        self.assertEqual(to_list({"a": 1, "b": 2}), [{"a": 1, "b": 2}])

    def test_empty_input(self):
        self.assertEqual(to_list([]), [])
        self.assertEqual(to_list(None), [])
        self.assertEqual(to_list([None]), [])

    def test_mixed_inputs(self):
        self.assertEqual(
            to_list([1, "string", [3, b"bytes"], None]), [1, "string", 3, b"bytes"]
        )

    def test_nested_tuples(self):
        self.assertEqual(to_list((1, (2, 3), ((4,), 5))), [1, 2, 3, 4, 5])

    def test_set_with_none(self):
        self.assertEqual(to_list({1, 2, None}), [1, 2])
        self.assertEqual(to_list({1, 2, None}, dropna=False), [None, 1, 2])

    def test_generator(self):
        def gen():
            yield 1
            yield 2
            yield 3

        self.assertEqual(to_list(gen()), [1, 2, 3])

    def test_deeply_nested_lists(self):
        nested_list = [1, [2, [3, [4, [5, [6, [7, [8, [9, [10]]]]]]]]]]
        self.assertEqual(to_list(nested_list), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_mixed_iterables(self):
        mixed_iterables = [1, (2, 3), {4, 5}, [[6, 7], 8]]
        self.assertEqual(to_list(mixed_iterables), [1, 2, 3, 4, 5, 6, 7, 8])

    def test_dict_with_iterable_values(self):
        dict_iterables = {"a": [1, 2], "b": (3, 4), "c": {5, 6}}
        self.assertEqual(
            to_list(dict_iterables), [{"a": [1, 2], "b": (3, 4), "c": {5, 6}}]
        )

    def test_nested_empty_lists(self):
        self.assertEqual(to_list([[], [[]], [[[]]]]), [])

    def test_edge_case_strings(self):
        self.assertEqual(to_list(""), [""])
        self.assertEqual(to_list(" "), [" "])
        self.assertEqual(to_list(["", " "]), ["", " "])

    def test_numpy_array(self):
        np_array = np.array([1, 2, 3])
        self.assertEqual(to_list(np_array), [1, 2, 3])

    def test_custom_iterable_class(self):
        class CustomIterable:
            def __iter__(self):
                yield 1
                yield 2
                yield 3

        self.assertEqual(to_list(CustomIterable()), [1, 2, 3])


class TestToNumFunctions(unittest.TestCase):

    def test_to_num_with_integer_string(self):
        self.assertEqual(to_num("123"), 123)

    def test_to_num_with_float_string(self):
        self.assertEqual(to_num("123.45"), 123.45)

    def test_to_num_with_mixed_string(self):
        self.assertEqual(to_num("The price is 123.45 dollars"), 123.45)

    def test_to_num_with_negative_number(self):
        self.assertEqual(to_num("-123.45"), -123.45)

    def test_to_num_with_no_number(self):
        with self.assertRaises(ValueError):
            to_num("No numbers here")

    def test_to_num_with_upper_bound(self):
        with self.assertRaises(ValueError):
            to_num("123.45", upper_bound=100)

    def test_to_num_with_lower_bound(self):
        with self.assertRaises(ValueError):
            to_num("123.45", lower_bound=200)

    def test_to_num_with_bounds(self):
        self.assertEqual(to_num("150", lower_bound=100, upper_bound=200), 150)

    def test_to_num_with_int_type(self):
        self.assertEqual(to_num("123.45", num_type=int), 123)

    def test_to_num_with_float_type(self):
        self.assertEqual(to_num("123", num_type=float), 123.0)

    def test_to_num_with_precision(self):
        self.assertEqual(to_num("123.4567", precision=2), 123.46)

    def test_str_to_num_with_valid_string(self):
        self.assertEqual(str_to_num("123"), 123)

    def test_str_to_num_with_invalid_string(self):
        with self.assertRaises(ValueError):
            str_to_num("No numbers here")

    def test_str_to_num_with_upper_bound(self):
        with self.assertRaises(ValueError):
            str_to_num("123.45", upper_bound=100)

    def test_str_to_num_with_lower_bound(self):
        with self.assertRaises(ValueError):
            str_to_num("123.45", lower_bound=200)

    def test_str_to_num_with_bounds(self):
        self.assertEqual(str_to_num("150", lower_bound=100, upper_bound=200), 150)

    def test_str_to_num_with_int_type(self):
        self.assertEqual(str_to_num("123.45", num_type=int), 123)

    def test_str_to_num_with_float_type(self):
        self.assertEqual(str_to_num("123", num_type=float), 123.0)

    def test_str_to_num_with_precision(self):
        self.assertEqual(str_to_num("123.4567", precision=2, num_type=float), 123.46)

    def test_extract_first_number_with_valid_string(self):
        self.assertEqual(_extract_numbers("The price is 123.45 dollars"), ["123.45"])

    def test_extract_first_number_with_no_number(self):
        self.assertEqual(_extract_numbers("No numbers here"), [])

    def test_convert_to_num_with_int_type(self):
        self.assertEqual(_convert_to_num("123.45", num_type=int), 123)

    def test_convert_to_num_with_float_type(self):
        self.assertEqual(_convert_to_num("123.45", num_type=float), 123.45)

    def test_convert_to_num_with_invalid_type(self):
        with self.assertRaises(ValueError):
            _convert_to_num("123.45", num_type=str)

    def test_convert_to_num_with_precision(self):
        self.assertEqual(
            _convert_to_num("123.4567", num_type=float, precision=2), 123.46
        )

    def test_to_num_with_multiple_numbers(self):
        self.assertEqual(to_num("There are 123 apples and 45 oranges"), 123)

    def test_to_num_with_multiple_numbers_and_num_count(self):
        self.assertEqual(
            to_num("There are 123 apples and 45 oranges", num_count=2), [123, 45]
        )

    def test_to_num_with_large_number(self):
        self.assertEqual(to_num("123456789012345"), 123456789012345)

    def test_to_num_with_small_number(self):
        self.assertEqual(to_num("0.000000123"), 0.000000123)

    def test_to_num_with_special_characters(self):
        self.assertEqual(to_num("Price: $123.45!"), 123.45)

    def test_to_num_with_hexadecimal(self):
        with self.assertRaises(ValueError):
            to_num("0x1A")

    def test_to_num_with_binary(self):
        with self.assertRaises(ValueError):
            to_num("0b1101")

    def test_to_num_with_list(self):
        with self.assertRaises(TypeError):
            to_num([1, 2, 3])

    def test_to_num_with_dict(self):
        with self.assertRaises(ValueError):
            to_num({"key": "value"})

    def test_to_num_with_mixed_string(self):
        self.assertEqual(to_num("Value is 123 and 456"), 123)

    def test_to_num_with_fraction(self):
        self.assertEqual(to_num("1/6"), 1 / 6)

    def test_to_num_with_fraction_and_num_count(self):
        self.assertEqual(to_num("1/6 and 2/3", num_count=2), [1 / 6, 2 / 3])

    def test_to_num_with_upper_and_lower_bounds(self):
        with self.assertRaises(ValueError):
            to_num("150", lower_bound=100, upper_bound=140)

    def test_to_num_with_complex_number(self):
        self.assertEqual(to_num("1+2j", num_type=complex), 1 + 2j)

    def test_to_num_with_multiple_complex_numbers(self):
        self.assertEqual(
            to_num("1+2j and 3-4j", num_type=complex, num_count=2), [1 + 2j, 3 - 4j]
        )


class TestUtilities(unittest.TestCase):

    def test_is_homogeneous_list(self):
        self.assertTrue(is_homogeneous([1, 2, 3], int))
        self.assertFalse(is_homogeneous([1, "2", 3], int))
        self.assertTrue(is_homogeneous(["a", "b", "c"], str))

    def test_is_homogeneous_dict(self):
        self.assertTrue(is_homogeneous({"a": 1, "b": 2}, int))
        self.assertFalse(is_homogeneous({"a": 1, "b": "2"}, int))
        self.assertTrue(is_homogeneous({"a": "x", "b": "y"}, str))

    def test_is_same_dtype_list(self):
        self.assertTrue(is_same_dtype([1, 2, 3]))
        self.assertFalse(is_same_dtype([1, "2", 3]))
        self.assertTrue(is_same_dtype([1.1, 2.2, 3.3], float))

    def test_is_same_dtype_dict(self):
        self.assertTrue(is_same_dtype({"a": 1, "b": 2}))
        self.assertFalse(is_same_dtype({"a": 1, "b": "2"}))
        self.assertTrue(is_same_dtype({"a": 1.1, "b": 2.2}, float))

    def test_is_same_dtype_return_dtype(self):
        result, dtype = is_same_dtype([1, 2, 3], return_dtype=True)
        self.assertTrue(result)
        self.assertEqual(dtype, int)

    def test_is_structure_homogeneous(self):
        self.assertTrue(is_structure_homogeneous({"a": {"b": 1}, "c": {"d": 2}}))
        self.assertFalse(is_structure_homogeneous({"a": {"b": 1}, "c": [1, 2]}))
        self.assertFalse(is_structure_homogeneous([{"a": 1}, {"b": 2}]))
        self.assertFalse(is_structure_homogeneous([{"a": 1}, ["b", 2]]))

    def test_is_structure_homogeneous_return_structure_type(self):
        result, structure_type = is_structure_homogeneous(
            {"a": {"b": 1}, "c": {"d": 2}}, return_structure_type=True
        )
        self.assertTrue(result)
        self.assertEqual(structure_type, dict)

    def test_deep_update(self):
        original = {"a": {"b": 1}, "c": 2}
        update = {"a": {"b": 2, "d": 3}, "e": 4}
        expected = {"a": {"b": 2, "d": 3}, "c": 2, "e": 4}
        self.assertEqual(deep_update(original, update), expected)

    def test_deep_update_empty(self):
        original = {}
        update = {"a": {"b": 2, "d": 3}, "e": 4}
        expected = {"a": {"b": 2, "d": 3}, "e": 4}
        self.assertEqual(deep_update(original, update), expected)

    def test_get_target_container(self):
        nested = {"a": {"b": {"c": 1}}}
        self.assertEqual(get_target_container(nested, ["a", "b"]), {"c": 1})

    def test_get_target_container_list(self):
        nested = [1, [2, 3], 4]
        self.assertEqual(get_target_container(nested, [1]), [2, 3])

    def test_get_target_container_mixed(self):
        nested = {"a": [{"b": 1}, {"c": 2}]}
        self.assertEqual(get_target_container(nested, ["a", 1]), {"c": 2})

    def test_get_target_container_index_error(self):
        nested = [1, [2, 3], 4]
        with self.assertRaises(IndexError):
            get_target_container(nested, [5])

    def test_get_target_container_key_error(self):
        nested = {"a": {"b": {"c": 1}}}
        with self.assertRaises(KeyError):
            get_target_container(nested, ["a", "d"])

    def test_get_target_container_type_error(self):
        nested = {"a": {"b": {"c": 1}}}
        with self.assertRaises(TypeError):
            get_target_container(nested, ["a", "b", "c", 0])


class TestUnflattenFunction(unittest.TestCase):

    def test_simple_case(self):
        flat_dict = {"a/b": 1, "a/c": 2}
        expected = {"a": {"b": 1, "c": 2}}
        self.assertEqual(unflatten(flat_dict), expected)

    def test_multiple_levels(self):
        flat_dict = {"a/b/c": 1, "a/b/d": 2}
        expected = {"a": {"b": {"c": 1, "d": 2}}}
        self.assertEqual(unflatten(flat_dict), expected)

    def test_with_different_separator(self):
        flat_dict = {"a.b": 1, "a.c": 2}
        expected = {"a": {"b": 1, "c": 2}}
        self.assertEqual(unflatten(flat_dict, sep="."), expected)

    def test_list_conversion(self):
        flat_dict = {"0/a": 1, "0/b": 2, "1/a": 3, "1/b": 4}
        expected = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        self.assertEqual(unflatten(flat_dict), expected)

    def test_nested_lists(self):
        flat_dict = {"0/0": 1, "0/1": 2, "1/0": 3, "1/1": 4}
        expected = [[1, 2], [3, 4]]
        self.assertEqual(unflatten(flat_dict), expected)

    def test_single_key(self):
        flat_dict = {"a": 1}
        expected = {"a": 1}
        self.assertEqual(unflatten(flat_dict), expected)

    def test_empty_dict(self):
        flat_dict = {}
        expected = {}
        self.assertEqual(unflatten(flat_dict), expected)

    def test_complex_case(self):
        flat_dict = {"a/b/c": 1, "a/b/d": 2, "a/e": 3, "f": 4}
        expected = {"a": {"b": {"c": 1, "d": 2}, "e": 3}, "f": 4}
        self.assertEqual(unflatten(flat_dict), expected)

    def test_with_dict_value(self):
        flat_dict = {"a/b": {"c/d": 1}}
        expected = {"a": {"b": {"c": {"d": 1}}}}
        self.assertEqual(unflatten(flat_dict), expected)

    def test_mixed_types(self):
        flat_dict = {"a/b": 1, "a/c": "string", "a/d": [1, 2, 3]}
        expected = {"a": {"b": 1, "c": "string", "d": [1, 2, 3]}}
        self.assertEqual(unflatten(flat_dict), expected)


if __name__ == "__main__":
    unittest.main()
