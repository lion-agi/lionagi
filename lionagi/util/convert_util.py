import json
import re
from collections import defaultdict
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Type
from pandas import DataFrame, Series, concat

number_regex = re.compile(r"-?\d+\.?\d*")


def to_dict(input_: Any) -> Dict[Any, Any]:
    return ConvertUtil.to_dict(input_)


def str_to_num(
    input_: str,
    upper_bound: float | None = None,
    lower_bound: float | None = None,
    num_type: Type[int | float] = int,
    precision: int | None = None,
) -> int | float:
    return ConvertUtil.str_to_num(input_, upper_bound, lower_bound, num_type, precision)


def to_df(
    item: List[Dict[Any, Any] | DataFrame | Series] | DataFrame | Series,
    how: str = "all",
    drop_kwargs: Dict[str, Any] | None = None,
    reset_index: bool = True,
    **kwargs: Any,
) -> DataFrame:
    return ConvertUtil.to_df(item, how, drop_kwargs, reset_index, **kwargs)


def to_readable_dict(input_: Dict[Any, Any] | List[Any]) -> str | List[Any]:
    return ConvertUtil.to_readable_dict(input_)


class ConvertUtil:

    @staticmethod
    def to_dict(input_: Any) -> Dict[Any, Any]:

        if isinstance(input_, str):
            try:
                return json.loads(input_)
            except json.JSONDecodeError as e:
                raise ValueError(f"Could not convert input_ to dict: {e}") from e

        elif isinstance(input_, dict):
            return input_
        else:
            raise TypeError(
                f"Could not convert input_ to dict: {type(input_).__name__} given."
            )

    @staticmethod
    def is_same_dtype(input_: list | dict, dtype: Type | None = None) -> bool:
        if not input_:
            return True

        iterable = input_.values() if isinstance(input_, dict) else input_
        first_element_type = type(next(iter(iterable), None))

        dtype = dtype or first_element_type

        return all(isinstance(element, dtype) for element in iterable)

    @staticmethod
    def xml_to_dict(root: ET.Element) -> Dict[str, Any]:
        def parse_xml(element: ET.Element, parent: Dict[str, Any]):
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

    @staticmethod
    def str_to_num(
        input_: str,
        upper_bound: float | None = None,
        lower_bound: float | None = None,
        num_type: Type[int | float] = int,
        precision: int | None = None,
    ) -> int | float:
        number_str = ConvertUtil._extract_first_number(input_)
        if number_str is None:
            raise ValueError(f"No numeric values found in the string: {input_}")

        number = ConvertUtil._convert_to_num(number_str, num_type, precision)

        if upper_bound is not None and number > upper_bound:
            raise ValueError(
                f"Number {number} is greater than the upper bound of {upper_bound}."
            )

        if lower_bound is not None and number < lower_bound:
            raise ValueError(
                f"Number {number} is less than the lower bound of {lower_bound}."
            )

        return number

    @staticmethod
    def strip_lower(input_: Any) -> str:
        try:
            return str(input_).strip().lower()
        except Exception as e:
            raise ValueError(
                f"Could not convert input_ to string: {input_}, Error: {e}"
            )

    @staticmethod
    def _extract_first_number(input_: str) -> str | None:
        match = number_regex.search(input_)
        return match.group(0) if match else None

    @staticmethod
    def _convert_to_num(
        number_str: str, num_type: Type[int | float] = int, precision: int | None = None
    ) -> int | float:
        if num_type is int:
            return int(float(number_str))
        elif num_type is float:
            number = float(number_str)
            return round(number, precision) if precision is not None else number
        else:
            raise ValueError(f"Invalid number type: {num_type}")

    @staticmethod
    def is_homogeneous(iterables: List[Any] | Dict[Any, Any], type_check: type) -> bool:
        if isinstance(iterables, list):
            return all(isinstance(it, type_check) for it in iterables)
        return isinstance(iterables, type_check)

    @staticmethod
    def to_readable_dict(input_: Dict[Any, Any] | List[Any]) -> str | List[Any]:
        return json.dumps(input_, indent=4) if isinstance(input_, dict) else input_

    @staticmethod
    def to_df(
        item: List[Dict[Any, Any] | DataFrame | Series] | DataFrame | Series,
        how: str = "all",
        drop_kwargs: Dict[str, Any] | None = None,
        reset_index: bool = True,
        **kwargs: Any,
    ) -> DataFrame:
        if drop_kwargs is None:
            drop_kwargs = {}
        dfs = ""
        try:
            if isinstance(item, list):
                if ConvertUtil.is_homogeneous(item, dict):
                    dfs = DataFrame(item)
                elif ConvertUtil.is_homogeneous(item, (DataFrame, Series)):
                    dfs = concat(item, **kwargs)
                else:
                    raise ValueError(
                        "Item list is not homogeneous or cannot be converted to DataFrame."
                    )
            elif isinstance(item, (DataFrame, Series)):
                dfs = item.copy() if isinstance(item, DataFrame) else DataFrame(item)
            else:
                raise TypeError("Unsupported type for conversion to DataFrame.")

            dfs.dropna(**(drop_kwargs | {"how": how}), inplace=True)

            if reset_index:
                dfs.reset_index(drop=True, inplace=True)

            return dfs

        except Exception as e:
            raise ValueError(f"Error converting item to DataFrame: {e}") from e
