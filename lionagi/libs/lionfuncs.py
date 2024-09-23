from typing import Any, TypeVar, Union, overload, Literal, TypeAlias
from pandas import DataFrame, Series, concat
from pandas.core.generic import NDFrame

from lion_core.libs import (
    nget,
    nset,
    npop,
    to_dict,
    to_list,
    to_num,
    to_str,
    lcall,
    bcall,
    alcall,
    mcall,
    pcall,
    rcall,
    tcall,
    ucall,
    validate_mapping,
    md_to_json,
    dict_to_xml,
    CallDecorator,
)


# Type aliases for cleaner type hints
PandasObject: TypeAlias = Union[DataFrame, Series, NDFrame]
PandasInput: TypeAlias = Union[Any, list[PandasObject]]

T = TypeVar("T", DataFrame, Series, NDFrame)


@overload
def to_df(
    input_: PandasObject,
    /,
    *,
    drop_how: Literal["any", "all"] = "all",
    drop_kwargs: dict[str, Any] | None = None,
    reset_index: bool = True,
    **kwargs: Any,
) -> DataFrame: ...


@overload
def to_df(
    input_: list[T],
    /,
    *,
    drop_how: Literal["any", "all"] = "all",
    drop_kwargs: dict[str, Any] | None = None,
    reset_index: bool = True,
    **kwargs: Any,
) -> DataFrame: ...


@overload
def to_df(
    input_: Any,
    /,
    *,
    drop_how: Literal["any", "all"] = "all",
    drop_kwargs: dict[str, Any] | None = None,
    reset_index: bool = True,
    **kwargs: Any,
) -> DataFrame: ...


def to_df(
    input_: PandasInput,
    /,
    *,
    drop_how: Literal["any", "all"] = "all",
    drop_kwargs: dict[str, Any] | None = None,
    reset_index: bool = True,
    **kwargs: Any,
) -> DataFrame:
    """
    Convert various input types to a pandas DataFrame.

    Handles single pandas objects, lists of pandas objects, and other types
    convertible to DataFrame. Drops NA values and optionally resets the index.

    Args:
        input_: Input data to convert.
        drop_how: Method to drop NA values ('any' or 'all').
        drop_kwargs: Additional arguments for dropna().
        reset_index: Whether to reset the index of the resulting DataFrame.
        **kwargs: Additional arguments passed to DataFrame constructor or concat.

    Returns:
        DataFrame: Processed pandas DataFrame.

    Raises:
        ValueError: If input cannot be converted to DataFrame.
    """
    drop_kwargs = drop_kwargs or {}

    if isinstance(input_, list):
        df = _process_list_input(input_, **kwargs)
    elif isinstance(input_, PandasObject):
        df = input_.to_frame() if isinstance(input_, Series) else input_
    else:
        try:
            df = DataFrame(input_, **kwargs)
        except Exception as e:
            raise ValueError(f"Error converting input to DataFrame: {e}") from e

    if "thresh" not in drop_kwargs:
        drop_kwargs["how"] = drop_how
    df = df.dropna(**drop_kwargs)
    return df.reset_index(drop=True) if reset_index else df


def _process_list_input(input_: list[Any], **kwargs) -> DataFrame:
    """Process list inputs, handling empty lists and lists of pandas objects."""
    if not input_:
        return DataFrame()

    if isinstance(input_[0], PandasObject):
        try:
            return concat(
                input_,
                axis=1 if all(isinstance(i, Series) for i in input_) else 0,
                **kwargs,
            )
        except Exception as e:
            raise ValueError(f"Error concatenating pandas objects: {e}") from e
    else:
        try:
            return DataFrame(input_, **kwargs)
        except Exception as e:
            raise ValueError(f"Error converting list to DataFrame: {e}") from e


__all__ = [
    "nget",
    "nset",
    "npop",
    "to_df",
    "to_dict",
    "to_list",
    "to_num",
    "to_str",
    "lcall",
    "alcall",
    "bcall",
    "mcall",
    "pcall",
    "rcall",
    "tcall",
    "ucall",
    "validate_mapping",
    "md_to_json",
    "dict_to_xml",
    "CallDecorator",
]
