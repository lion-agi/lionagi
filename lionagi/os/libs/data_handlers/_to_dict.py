from collections import defaultdict
from collections.abc import Mapping
import json
from typing import Any
from pandas import DataFrame


def to_dict(
    input_, /, as_list: bool = True, use_model_dump: bool = True, **kwargs
) -> dict | list[dict]:
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
    if isinstance(input_, list):
        return [
            to_dict(i, as_list=as_list, use_model_dump=use_model_dump, **kwargs)
            for i in input_
        ]
    return _to_dict(input_, df_as_list=as_list, use_model_dump=use_model_dump, **kwargs)


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
        return json.loads(input_, **kwargs)

    if isinstance(input_, DataFrame):
        if df_as_list:
            return [row.to_dict(**kwargs) for _, row in input_.iterrows()]

    if use_model_dump and hasattr(input_, "model_dump"):
        return input_.model_dump(**kwargs)

    if hasattr(input_, "to_dict"):
        return input_.to_dict(**kwargs)

    if hasattr(input_, "json"):
        return json.loads(input_.json(**kwargs))

    if hasattr(input_, "dict"):
        return input_.dict(**kwargs)

    raise ValueError(f"Unsupported input type: {type(input_)}")


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
