# import pytest

# from lion_core.libs.data_handlers._flatten import flatten, get_flattened_keys


# @pytest.mark.parametrize(
#     "data, expected, sep, max_depth, dict_only",
#     [
#         (
#             {"a": 1, "b": {"c": 2, "d": {"e": 3}}},
#             {"a": 1, "b|c": 2, "b|d|e": 3},
#             "|",
#             None,
#             False,
#         ),
#         (
#             {"a": 1, "b": [1, 2, {"c": 3}]},
#             {"a": 1, "b|0": 1, "b|1": 2, "b|2|c": 3},
#             "|",
#             None,
#             False,
#         ),
#         (
#             {"a": [1, {"b": 2}], "c": {"d": [3, {"e": 4}]}},
#             {"a|0": 1, "a|1|b": 2, "c|d|0": 3, "c|d|1|e": 4},
#             "|",
#             None,
#             False,
#         ),
#         ({}, {}, "|", None, False),
#         ([], {}, "|", None, False),
#         ({"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 2, "c": 3}, "|", None, False),
#         (
#             {"a": 1, "b": {"c": 2, "d": {"e": 3}}},
#             {"a": 1, "b|c": 2, "b|d": {"e": 3}},
#             "|",
#             2,
#             False,
#         ),
#         (
#             {"a": 1, "b": {"c": 2, "d": [3, {"e": 4}]}},
#             {"a": 1, "b|c": 2, "b|d": [3, {"e": 4}]},
#             "|",
#             None,
#             True,
#         ),
#         (
#             {"a": 1, "b": {"c": 2, "d": {"e": 3}}},
#             {"a": 1, "b/c": 2, "b/d/e": 3},
#             "/",
#             None,
#             False,
#         ),
#         ({"a": {"b": {"c": {"d": 1}}}}, {"a|b|c|d": 1}, "|", None, False),
#         (
#             {"a": [1, [2, [3]]]},
#             {"a|0": 1, "a|1|0": 2, "a|1|1|0": 3},
#             "|",
#             None,
#             False,
#         ),
#         (
#             {"a": 1, "b": [2, 3]},
#             {"a": 1, "b|0": 2, "b|1": 3},
#             "|",
#             None,
#             False,
#         ),
#         ({"a": {1, 2, 3}}, {"a": {1, 2, 3}}, "|", None, False),
#         (
#             {"a": frozenset([1, 2, 3])},
#             {"a": frozenset([1, 2, 3])},
#             "|",
#             None,
#             False,
#         ),
#     ],
# )
# def test_flatten(data, expected, sep, max_depth, dict_only):
#     assert (
#         flatten(data, sep=sep, max_depth=max_depth, dict_only=dict_only)
#         == expected
#     )


# def test_flatten_in_place():
#     data = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
#     expected = {"a": 1, "b|c": 2, "b|d|e": 3}
#     flatten(data, inplace=True)
#     assert data == expected


# def test_flatten_invalid_in_place():
#     data = [1, 2, 3]
#     with pytest.raises(
#         ValueError, match="Object must be a dictionary when 'inplace' is True."
#     ):
#         flatten(data, inplace=True)


# def test_flatten_none_data():
#     with pytest.raises(
#         ValueError,
#         match="Cannot flatten NoneType objects.",
#     ):
#         flatten(None)


# def test_flatten_non_string_keys():
#     with pytest.raises(
#         ValueError,
#         match="Unable to convert input to dictionary: Unsupported key type: int. Only string keys are acceptable.",
#     ):
#         flatten({1: "a", 2: "b"})


# @pytest.mark.parametrize(
#     "data, expected, sep, max_depth, dict_only",
#     [
#         (
#             {"a": 1, "b": {"c": 2, "d": {"e": 3}}},
#             ["a", "b|c", "b|d|e"],
#             "|",
#             None,
#             False,
#         ),
#         (
#             {"a": 1, "b": [1, 2, {"c": 3}]},
#             ["a", "b|0", "b|1", "b|2|c"],
#             "|",
#             None,
#             False,
#         ),
#         ({}, [], "|", None, False),
#         ([], [], "|", None, False),
#         (
#             {"a": 1, "b": {"c": 2, "d": {"e": 3}}},
#             ["a", "b|c", "b|d"],
#             "|",
#             2,
#             False,
#         ),
#         (
#             {"a": 1, "b": {"c": 2, "d": [3, {"e": 4}]}},
#             ["a", "b|c", "b|d"],
#             "|",
#             None,
#             True,
#         ),
#     ],
# )
# def test_get_flattened_keys(data, expected, sep, max_depth, dict_only):
#     assert (
#         get_flattened_keys(
#             data, sep=sep, max_depth=max_depth, dict_only=dict_only
#         )
#         == expected
#     )


# def test_get_flattened_keys_inplace():
#     data = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
#     expected = ["a", "b|c", "b|d|e"]
#     assert get_flattened_keys(data) == expected


# # File: tests/test_flatten.py
