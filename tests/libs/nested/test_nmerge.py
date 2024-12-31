# import pytest

# from lion_core.libs.data_handlers._nmerge import nmerge


# @pytest.mark.parametrize(
#     "data, expected, overwrite",
#     [
#         (
#             [{"a": 1, "b": 2}, {"b": 3, "c": 4}, {"b": 4, "e": 5}],
#             {"a": 1, "b": [2, 3, 4], "c": 4, "e": 5},
#             False,
#         ),
#         ([{"a": 1, "b": 2}, {"b": 3, "c": 4}], {"a": 1, "b": 3, "c": 4}, True),
#     ],
# )
# def test_nmerge_dicts(data, expected, overwrite):
#     assert nmerge(data, overwrite=overwrite) == expected


# @pytest.mark.parametrize(
#     "data, expected, dict_sequence",
#     [
#         (
#             [{"a": 1, "b": 2}, {"b": 3, "c": 4}],
#             {"a": 1, "b": 2, "b1": 3, "c": 4},
#             True,
#         ),
#     ],
# )
# def test_nmerge_dicts_with_sequence(data, expected, dict_sequence):
#     assert nmerge(data, dict_sequence=dict_sequence) == expected


# @pytest.mark.parametrize(
#     "data, expected, sort_list",
#     [
#         ([[1, 3], [2, 4], [5, 6]], [1, 3, 2, 4, 5, 6], False),
#         ([[3, 1], [6, 2], [5, 4]], [1, 2, 3, 4, 5, 6], True),
#     ],
# )
# def test_nmerge_lists(data, expected, sort_list):
#     assert nmerge(data, sort_list=sort_list) == expected


# def test_nmerge_lists_with_custom_sort():
#     data = [["apple", "banana"], ["cherry", "date"]]
#     expected = ["date", "apple", "banana", "cherry"]
#     assert nmerge(data, sort_list=True, custom_sort=len) == expected


# def test_nmerge_mixed_structures():
#     data = [{"a": [1, 2]}, {"a": [3, 4]}]
#     expected = {"a": [[1, 2], [3, 4]]}
#     assert nmerge(data) == expected


# def test_nmerge_empty_list():
#     assert nmerge([]) == {}


# def test_nmerge_single_element_list():
#     data = [{"a": 1}]
#     expected = {"a": 1}
#     assert nmerge(data) == expected


# def test_nmerge_incompatible_types():
#     data = [{"a": 1}, [2, 3]]
#     with pytest.raises(TypeError):
#         nmerge(data)


# def test_nmerge_deep_merge_dicts():
#     data = [{"a": {"b": 1}}, {"a": {"c": 2}}]
#     expected = {"a": [{"b": 1}, {"c": 2}]}
#     assert nmerge(data) == expected


# def test_nmerge_invalid_input():
#     with pytest.raises(TypeError):
#         nmerge("invalid_input")


# @pytest.mark.parametrize(
#     "data, expected",
#     [
#         (
#             [{"a": 1, "b": {"c": 2}}, {"b": {"d": 3}}],
#             {"a": 1, "b": [{"c": 2}, {"d": 3}]},
#         ),
#         (
#             [{"a": [1, 2]}, {"a": [3, 4]}, {"a": [5, 6]}],
#             {"a": [[1, 2], [3, 4], [5, 6]]},
#         ),
#         (
#             [{"a": {"b": [1, 2]}}, {"a": {"b": [3, 4]}}],
#             {"a": [{"b": [1, 2]}, {"b": [3, 4]}]},
#         ),
#     ],
# )
# def test_nmerge_nested_structures(data, expected):
#     assert nmerge(data) == expected


# def test_nmerge_with_none_values():
#     data = [{"a": 1, "b": None}, {"b": 2, "c": None}]
#     expected = {"a": 1, "b": [None, 2], "c": None}
#     assert nmerge(data) == expected


# @pytest.mark.parametrize(
#     "data, expected",
#     [
#         ([{"a": {1, 2}}, {"a": {2, 3}}], {"a": [{1, 2}, {2, 3}]}),
#         (
#             [{"a": frozenset([1, 2])}, {"a": frozenset([2, 3])}],
#             {"a": [frozenset([1, 2]), frozenset([2, 3])]},
#         ),
#     ],
# )
# def test_nmerge_with_sets(data, expected):
#     assert nmerge(data) == expected


# def test_nmerge_with_tuples():
#     data = [{"a": (1, 2)}, {"a": (3, 4)}]
#     expected = {"a": [(1, 2), (3, 4)]}
#     assert nmerge(data) == expected


# def test_nmerge_with_bytes():
#     data = [{"a": b"hello"}, {"a": b"world"}]
#     expected = {"a": [b"hello", b"world"]}
#     assert nmerge(data) == expected


# def test_nmerge_with_bytearray():
#     data = [{"a": bytearray(b"hello")}, {"a": bytearray(b"world")}]
#     expected = {"a": [bytearray(b"hello"), bytearray(b"world")]}
#     assert nmerge(data) == expected


# def test_nmerge_with_complex_numbers():
#     data = [{"a": 1 + 2j}, {"a": 3 + 4j}]
#     expected = {"a": [1 + 2j, 3 + 4j]}
#     assert nmerge(data) == expected


# def test_nmerge_with_boolean_values():
#     data = [{"a": True}, {"a": False}, {"b": True}]
#     expected = {"a": [True, False], "b": True}
#     assert nmerge(data) == expected


# def test_nmerge_with_none_values():
#     data = [{"a": None}, {"b": 1}, {"a": 2}]
#     expected = {"a": [None, 2], "b": 1}
#     assert nmerge(data) == expected


# def test_nmerge_with_empty_dicts():
#     data = [{}, {"a": 1}, {}, {"b": 2}, {}]
#     expected = {"a": 1, "b": 2}
#     assert nmerge(data) == expected


# def test_nmerge_with_empty_lists():
#     data = [[], [1, 2], [], [3, 4], []]
#     expected = [1, 2, 3, 4]
#     assert nmerge(data) == expected


# def test_nmerge_with_mixed_empty_structures():
#     data = [{}, [], {"a": 1}, [2, 3], {}]
#     with pytest.raises(TypeError):
#         nmerge(data)


# def test_nmerge_with_custom_objects():
#     class CustomObj:
#         def __init__(self, value):
#             self.value = value

#     obj1 = CustomObj(1)
#     obj2 = CustomObj(2)
#     data = [{"a": obj1}, {"a": obj2}]
#     result = nmerge(data)
#     assert isinstance(result["a"], list)
#     assert all(isinstance(obj, CustomObj) for obj in result["a"])
#     assert [obj.value for obj in result["a"]] == [1, 2]


# def test_nmerge_with_large_input(benchmark):
#     large_data = [{"key": i} for i in range(10000)]
#     result = benchmark(nmerge, large_data)
#     assert len(result["key"]) == 10000


# def test_nmerge_with_deeply_nested_structures():
#     data = [
#         {"a": {"b": {"c": {"d": 1}}}},
#         {"a": {"b": {"c": {"e": 2}}}},
#         {"a": {"b": {"f": 3}}},
#     ]
#     expected = {"a": [{"b": {"c": [{"d": 1}, {"e": 2}]}}, {"b": {"f": 3}}]}
#     assert nmerge(data) == expected


# @pytest.mark.parametrize(
#     "overwrite, expected",
#     [
#         (False, {"a": 1, "b": [2, 3, 4], "c": 3}),
#         (True, {"a": 1, "b": 4, "c": 3}),
#     ],
# )
# def test_nmerge_overwrite_behavior(overwrite, expected):
#     data = [{"a": 1, "b": 2}, {"b": 3}, {"b": 4, "c": 3}]
#     assert nmerge(data, overwrite=overwrite) == expected


# def test_nmerge_dict_sequence():
#     data = [{"a": 1}, {"a": 2}, {"a": 3}]
#     expected = {"a": 1, "a1": 2, "a2": 3}
#     assert nmerge(data, dict_sequence=True) == expected


# def test_nmerge_dict_sequence_with_existing_keys():
#     data = [{"a": 1, "a1": 2}, {"a": 3, "a2": 4}]
#     expected = {"a": 1, "a1": 2, "a2": 3, "a3": 4}
#     assert nmerge(data, dict_sequence=True) == expected


# def test_nmerge_sort_list_with_mixed_types():
#     data = [[3, "a", 1.5], [2, "c", 1.2], ["b", 1, 2.5]]
#     expected = [1, 1.2, 1.5, 2, 2.5, 3, "a", "b", "c"]
#     assert nmerge(data, sort_list=True) == expected


# def test_nmerge_custom_sort_with_key_function():
#     data = [["apple", "banana"], ["cherry", "date"]]
#     expected = ["apple", "cherry", "banana", "date"]
#     assert (
#         nmerge(data, sort_list=True, custom_sort=lambda x: len(x)) == expected
#     )


# def test_nmerge_with_duplicate_keys_no_overwrite():
#     data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
#     expected = {"a": [1, 3], "b": [2, 4]}
#     assert nmerge(data, overwrite=False) == expected


# def test_nmerge_with_duplicate_keys_overwrite():
#     data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
#     expected = {"a": 3, "b": 4}
#     assert nmerge(data, overwrite=True) == expected


# def test_nmerge_with_different_value_types():
#     data = [{"a": 1}, {"a": "string"}, {"a": [1, 2, 3]}]
#     expected = {"a": [1, "string", [1, 2, 3]]}
#     assert nmerge(data) == expected


# def test_nmerge_with_conflicting_types():
#     data = [{"a": {"b": 1}}, {"a": [1, 2, 3]}]
#     expected = {"a": [{"b": 1}, [1, 2, 3]]}
#     assert nmerge(data) == expected


# @pytest.mark.parametrize(
#     "input_data, expected",
#     [
#         ([1, 2, 3], [1, 2, 3]),
#         (["a", "b", "c"], ["a", "b", "c"]),
#         ([True, False, True], [True, False, True]),
#         ([1.1, 2.2, 3.3], [1.1, 2.2, 3.3]),
#     ],
# )
# def test_nmerge_single_level_lists(input_data, expected):
#     assert nmerge([input_data]) == expected


# def test_nmerge_with_generator_input():
#     def gen():
#         yield {"a": 1}
#         yield {"b": 2}

#     expected = {"a": 1, "b": 2}
#     assert nmerge(gen()) == expected


# def test_nmerge_with_all_python_basic_types():
#     data = [
#         {"int": 1, "float": 2.0, "complex": 1 + 2j},
#         {
#             "str": "string",
#             "bytes": b"bytes",
#             "bytearray": bytearray(b"bytearray"),
#         },
#         {
#             "list": [1, 2, 3],
#             "tuple": (4, 5, 6),
#             "set": {7, 8, 9},
#             "frozenset": frozenset([10, 11, 12]),
#         },
#         {"dict": {"key": "value"}, "bool": True, "none": None},
#     ]
#     result = nmerge(data)
#     assert isinstance(result["int"], int)
#     assert isinstance(result["float"], float)
#     assert isinstance(result["complex"], complex)
#     assert isinstance(result["str"], str)
#     assert isinstance(result["bytes"], bytes)
#     assert isinstance(result["bytearray"], bytearray)
#     assert isinstance(result["list"], list)
#     assert isinstance(result["tuple"], tuple)
#     assert isinstance(result["set"], set)
#     assert isinstance(result["frozenset"], frozenset)
#     assert isinstance(result["dict"], dict)
#     assert isinstance(result["bool"], bool)
#     assert result["none"] is None


# # File: tests/test_nmerge.py
