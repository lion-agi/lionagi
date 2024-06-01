from collections import defaultdict
from collections.abc import Mapping
import json
from typing import Any, Union
from pandas import DataFrame, isna
import pandas as pd


def to_dict(
    input_, /, as_list: bool = True, use_model_dump: bool = True, **kwargs
) -> Union[dict, list[dict]]:
    """
    Convert various types of input into a dictionary.

    Args:
        input_ (Any): The input data to convert.
        as_list (bool, optional): If True, converts DataFrame rows to a list
            of dictionaries. Defaults to True.
        use_model_dump (bool, optional): If True, use model_dump method if
            available. Defaults to True.
        **kwargs: Additional arguments to pass to conversion methods.

    Returns:
        dict | list[dict]: The converted dictionary or list of dictionaries.

    Raises:
        json.JSONDecodeError: If the input string cannot be parsed as JSON.
        ValueError: If the input type is unsupported.
    """
    out = None
    if isinstance(input_, list):
        out = [
            to_dict(i, as_list=as_list, use_model_dump=use_model_dump, **kwargs)
            for i in input_
        ]
    else:
        out = _to_dict(
            input_, df_as_list=as_list, use_model_dump=use_model_dump, **kwargs
        )

    if out in [[], {}]:
        return {}

    if isinstance(out, list) and len(out) == 1 and isinstance(out[0], dict):
        return out[0]

    return out


def _to_dict(
    input_, /, df_as_list: bool = True, use_model_dump: bool = True, **kwargs
) -> dict:
    """
    Helper function to convert the input into a dictionary.

    Args:
        input_ (Any): The input data to convert.
        df_as_list (bool, optional): If True, converts DataFrame rows to a
            list of dictionaries. Defaults to True.
        use_model_dump (bool, optional): If True, use model_dump method if
            available. Defaults to True.
        **kwargs: Additional arguments to pass to conversion methods.

    Returns:
        dict: The converted dictionary.

    Raises:
        json.JSONDecodeError: If the input string cannot be parsed as JSON.
        ValueError: If the input type is unsupported.
    """
    if isinstance(input_, dict):
        return input_

    if isinstance(input_, Mapping):
        return dict(input_)

    if isinstance(input_, str):
        a = json.loads(input_, **kwargs)
        if isinstance(a, dict):
            return a
        raise ValueError("Input string cannot be converted into a dictionary.")

    if isinstance(input_, DataFrame):
        if df_as_list:
            return [replace_nans(row.to_dict(**kwargs)) for _, row in input_.iterrows()]

    if use_model_dump and hasattr(input_, "model_dump"):
        return input_.model_dump(**kwargs)

    if hasattr(input_, "to_dict"):
        return input_.to_dict(**kwargs)

    if hasattr(input_, "json"):
        return json.loads(input_.json(**kwargs))

    if hasattr(input_, "dict"):
        return input_.dict(**kwargs)

    try:
        return dict(input_)
    except Exception as e:
        raise e


def replace_nans(d: dict) -> dict:
    """
    Replace NaN values in a dictionary with None.

    Args:
        d (dict): The dictionary to process.

    Returns:
        dict: The processed dictionary with NaN values replaced by None.
    """
    return {k: (None if isna(v) else v) for k, v in d.items()}


def xml_to_dict(root: Any) -> dict[str, Any]:
    """
    Convert an XML element and its children to a dictionary.

    Args:
        root (Any): The root XML element.

    Returns:
        dict[str, Any]: The dictionary representation of the XML structure.
    """

    def parse_xml(element: Any, parent: dict[str, Any]) -> None:
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
