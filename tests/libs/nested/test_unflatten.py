# import pytest

# from lion_core.libs.data_handlers._unflatten import unflatten


# @pytest.mark.parametrize(
#     "flat_dict, sep, expected",
#     [
#         (
#             {"a|b|c": 1, "a|b|d": 2, "a|e": 3, "f": 4},
#             "|",
#             {"a": {"b": {"c": 1, "d": 2}, "e": 3}, "f": 4},
#         ),
#         (
#             {"a/b/c": 1, "a/b/d": 2, "a/e": 3, "f": 4},
#             "/",
#             {"a": {"b": {"c": 1, "d": 2}, "e": 3}, "f": 4},
#         ),
#         (
#             {"a.b.c": 1, "a.b.d": 2, "a.e": 3, "f": 4},
#             ".",
#             {"a": {"b": {"c": 1, "d": 2}, "e": 3}, "f": 4},
#         ),
#     ],
# )
# def test_unflatten_dict(flat_dict, sep, expected):
#     assert unflatten(flat_dict, sep=sep) == expected


# def test_unflatten_dict_with_inplace():
#     flat_dict = {"a|b|c": 1, "a|b|d": 2, "a|e": 3, "f": 4}
#     expected = {"a": {"b": {"c": 1, "d": 2}, "e": 3}, "f": 4}
#     result = unflatten(flat_dict, sep="|", inplace=True)
#     assert result == expected
#     assert flat_dict == expected


# @pytest.mark.parametrize(
#     "flat_dict, sep, expected",
#     [
#         (
#             {"0": "a", "1|b|c": 1, "1|b|d": 2, "1|e": 3, "2": "f"},
#             "|",
#             ["a", {"b": {"c": 1, "d": 2}, "e": 3}, "f"],
#         ),
#         ({"0": "x", "1": "y", "2": "z"}, "|", ["x", "y", "z"]),
#     ],
# )
# def test_unflatten_list(flat_dict, sep, expected):
#     assert unflatten(flat_dict, sep=sep) == expected


# def test_unflatten_empty_dict():
#     assert unflatten({}, sep="|") == {}


# @pytest.mark.parametrize(
#     "flat_dict, sep, expected",
#     [
#         (
#             {"a|b|0": 1, "a|b|1": 2, "a|c|d": 3},
#             "|",
#             {"a": {"b": [1, 2], "c": {"d": 3}}},
#         ),
#         (
#             {"a|0|b": 1, "a|1|c": 2, "a|2|d": 3},
#             "|",
#             {"a": [{"b": 1}, {"c": 2}, {"d": 3}]},
#         ),
#     ],
# )
# def test_unflatten_dict_with_mixed_types(flat_dict, sep, expected):
#     assert unflatten(flat_dict, sep=sep) == expected


# def test_unflatten_with_numeric_keys():
#     flat_dict = {"0|a": 1, "0|b": 2, "1|c": 3, "1|d": 4}
#     expected = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
#     assert unflatten(flat_dict, sep="|") == expected


# def test_unflatten_with_deep_nesting():
#     flat_dict = {"a|b|c|d|e": 1, "a|b|c|d|f": 2, "a|b|c|g": 3, "a|h": 4}
#     expected = {"a": {"b": {"c": {"d": {"e": 1, "f": 2}, "g": 3}}, "h": 4}}
#     assert unflatten(flat_dict, sep="|") == expected


# def test_unflatten_with_empty_keys():
#     flat_dict = {"": 1, "a|": 2, "|b": 3, "c||d": 4}
#     expected = {"": 1, "a": {"": 2}, "b": 3, "c": {"": {"d": 4}}}
#     assert unflatten(flat_dict, sep="|") == expected


# def test_unflatten_with_duplicate_keys():
#     flat_dict = {
#         "a|b": 1,
#         "a|b": 2,
#     }  # Note: This is actually not possible in Python dict
#     expected = {"a": {"b": 2}}  # The last value should be kept
#     assert unflatten(flat_dict, sep="|") == expected


# def test_unflatten_with_non_string_keys():
#     flat_dict = {("a", "b"): 1, ("a", "c"): 2}
#     with pytest.raises(TypeError):
#         unflatten(flat_dict, sep="|")


# def test_unflatten_with_invalid_separator():
#     flat_dict = {"a|b": 1, "c|d": 2}
#     with pytest.raises(ValueError):
#         unflatten(flat_dict, sep="")


# def test_unflatten_with_nested_lists():
#     flat_dict = {"a|0|0": 1, "a|0|1": 2, "a|1|0": 3, "a|1|1": 4}
#     expected = {"a": [[1, 2], [3, 4]]}
#     assert unflatten(flat_dict, sep="|") == expected


# def test_unflatten_with_mixed_separators():
#     flat_dict = {"a|b.c": 1, "a|b.d": 2}
#     expected = {"a": {"b": {"c": 1, "d": 2}}}
#     assert unflatten(flat_dict, sep="|") == expected


# def test_unflatten_with_escaped_separator():
#     flat_dict = {"a\\|b": 1, "c": {"d\\|e": 2}}
#     expected = {"a|b": 1, "c": {"d|e": 2}}
#     assert unflatten(flat_dict, sep="|") == expected


# def test_unflatten_with_large_input():
#     flat_dict = {f"level{i}|sublevel": i for i in range(1000)}
#     result = unflatten(flat_dict, sep="|")
#     assert len(result) == 1000
#     assert all(f"level{i}" in result for i in range(1000))
#     assert all(result[f"level{i}"]["sublevel"] == i for i in range(1000))


# def test_unflatten_performance_with_deep_nesting(benchmark):
#     def create_deep_nested():
#         return {
#             "|".join([f"level{i}" for i in range(100)]): i for i in range(100)
#         }

#     flat_dict = create_deep_nested()
#     result = benchmark(unflatten, flat_dict, sep="|")
#     assert len(result) == 1
#     assert result["level0"]["level1"]["level2"] is not None


# def test_unflatten_with_non_dict_input():
#     with pytest.raises(AttributeError):
#         unflatten([1, 2, 3], sep="|")


# def test_unflatten_with_custom_separator_function():
#     def custom_sep(key):
#         return key.split(".")

#     flat_dict = {"a.b.c": 1, "a.b.d": 2, "e": 3}
#     expected = {"a": {"b": {"c": 1, "d": 2}}, "e": 3}
#     assert unflatten(flat_dict, sep=custom_sep) == expected


# def test_unflatten_with_unicode_separator():
#     flat_dict = {"a→b→c": 1, "a→b→d": 2, "e": 3}
#     expected = {"a": {"b": {"c": 1, "d": 2}}, "e": 3}
#     assert unflatten(flat_dict, sep="→") == expected


# def test_unflatten_with_multicharacter_separator():
#     flat_dict = {"a::b::c": 1, "a::b::d": 2, "e": 3}
#     expected = {"a": {"b": {"c": 1, "d": 2}}, "e": 3}
#     assert unflatten(flat_dict, sep="::") == expected


# # File: tests/test_unflatten.py
