"""
Utilities for converting various input types into dictionaries.

This module provides functions to convert different data structures into
dictionaries or lists of dictionaries, handling special cases and formats.

Functions:
    to_dict: Convert various input types into a dictionary.
    replace_nans: Replace NaN values in a dictionary with None.
    xml_to_dict: Convert an XML element and its children to a dictionary.
"""

from collections import defaultdict
from collections.abc import Mapping
import json
from typing import Any, Union, Callable, TypeVar, Dict, List

from pandas import DataFrame, isna

T = TypeVar('T')

def to_dict(
    input_: Any,
    /,
    as_list: bool = True,
    use_model_dump: bool = True,
    str_type: str = "json",
    **kwargs: Any
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Convert various types of input into a dictionary.

    Args:
        input_: The input data to convert.
        as_list: If True, converts DataFrame rows to a list of dictionaries.
        use_model_dump: If True, use model_dump method if available.
        str_type: The type of string to convert. Options: "json", "xml".
        **kwargs: Additional arguments to pass to conversion methods.

    Returns:
        The converted dictionary or list of dictionaries.

    Raises:
        ValueError: If the input type is unsupported or conversion fails.
    """
    if isinstance(input_, list):
        result = _convert_list(input_, as_list, use_model_dump, str_type, **kwargs)
        if len(result) == 1:
            return result[0]
        return result

    result = _to_dict(input_, as_list, use_model_dump, str_type, **kwargs)
    
    if not result:
        return {}
    
    if isinstance(result, list) and len(result) == 1 and isinstance(result[0], dict):
        return result[0]
    
    return result

def _convert_list(
    input_: List[Any],
    as_list: bool,
    use_model_dump: bool,
    str_type: str,
    **kwargs: Any
) -> List[Dict[str, Any]]:
    """Convert a list of inputs to a list of dictionaries."""
    return [
        to_dict(
            item,
            as_list=as_list,
            use_model_dump=use_model_dump,
            str_type=str_type,
            **kwargs
        )
        for item in input_
    ]

def _to_dict(
    input_: Any,
    as_list: bool,
    use_model_dump: bool,
    str_type: str,
    **kwargs: Any
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Helper function to convert the input into a dictionary."""
    conversion_methods = [
        (_is_dict_like, _convert_dict_like),
        (_is_string, _convert_string),
        (_is_dataframe, _convert_dataframe),
        (_has_model_dump, _convert_model_dump),
        (_has_to_dict, _convert_to_dict),
        (_has_json, _convert_json),
        (_has_dict, _convert_dict_attr),
        (_is_iterable, _convert_iterable),
    ]

    for check, convert in conversion_methods:
        if check(input_):
            return convert(input_, as_list, use_model_dump, str_type, **kwargs)
    
    raise TypeError("Input type is unsupported.")

# Type checking functions
def _is_dict_like(obj: Any) -> bool:
    return isinstance(obj, (dict, Mapping))

def _is_string(obj: Any) -> bool:
    return isinstance(obj, str)

def _is_dataframe(obj: Any) -> bool:
    return isinstance(obj, DataFrame)

def _has_model_dump(obj: Any) -> bool:
    return hasattr(obj, "model_dump")

def _has_to_dict(obj: Any) -> bool:
    return hasattr(obj, "to_dict")

def _has_json(obj: Any) -> bool:
    return hasattr(obj, "json")

def _has_dict(obj: Any) -> bool:
    return hasattr(obj, "dict")

def _is_iterable(obj: Any) -> bool:
    try:
        iter(obj)
        return True
    except TypeError:
        return False

# Conversion functions
def _convert_dict_like(
    obj: Union[Dict[Any, Any], Mapping],
    *args: Any,
    **kwargs: Any
) -> Dict[str, Any]:
    return dict(obj)

def _convert_string(
    obj: str,
    as_list: bool,
    use_model_dump: bool,
    str_type: str,
    **kwargs: Any
) -> Dict[str, Any]:
    if str_type == "xml":
        result = xml_to_dict(obj)
    elif str_type == "json":
        result = json.loads(obj, **kwargs)
    else:
        raise TypeError(f"Unsupported string type: {str_type}")

    if not isinstance(result, dict):
        raise ValueError("Input string cannot be converted into a dictionary.")
    return result

def _convert_dataframe(
    obj: DataFrame,
    as_list: bool,
    *args: Any,
    **kwargs: Any
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    if as_list:
        return [replace_nans(row.to_dict(**kwargs)) for _, row in obj.iterrows()]
    return obj.to_dict(**kwargs)

def _convert_model_dump(
    obj: Any,
    *args: Any,
    **kwargs: Any
) -> Dict[str, Any]:
    return obj.model_dump(**kwargs)

def _convert_to_dict(
    obj: Any,
    *args: Any,
    **kwargs: Any
) -> Dict[str, Any]:
    return obj.to_dict(**kwargs)

def _convert_json(
    obj: Any,
    *args: Any,
    **kwargs: Any
) -> Dict[str, Any]:
    return json.loads(obj.json(**kwargs))

def _convert_dict_attr(
    obj: Any,
    *args: Any,
    **kwargs: Any
) -> Dict[str, Any]:
    return obj.dict(**kwargs)

def _convert_iterable(
    obj: Any,
    *args: Any,
    **kwargs: Any
) -> Dict[str, Any]:
    return dict(obj)

def replace_nans(d: Dict[Any, Any]) -> Dict[Any, Any]:
    """Replace NaN values in a dictionary with None."""
    return {k: (None if isna(v) else v) for k, v in d.items()}

def xml_to_dict(root: Any) -> Dict[str, Any]:
    """Convert an XML element and its children to a dictionary."""
    def parse_xml(element: Any, parent: Dict[str, Any]) -> None:
        children = list(element)
        if children:
            d = defaultdict(list)
            for child in children:
                parse_xml(child, d)
            parent[element.tag].append(d if len(d) > 1 else d[next(iter(d))])
        else:
            parent[element.tag].append(element.text)

    result = defaultdict(list)
    parse_xml(root, result)
    return {k: v[0] if len(v) == 1 else v for k, v in result.items()}



import unittest
import pandas as pd


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
        self.assertEqual(to_dict([]), [])

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


if __name__ == "__main__":
    unittest.main()