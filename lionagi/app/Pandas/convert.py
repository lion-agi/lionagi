from functools import singledispatch
from typing import Any
from pandas import DataFrame, Series, concat
from pandas.core.generic import NDFrame
from lionagi.os import Converter, lionfuncs as ln


@singledispatch
def to_df(
    input_: Any,
    /,
    *,
    drop_how: str = "all",
    drop_kwargs: dict[str, Any] | None = None,
    reset_index: bool = True,
    **kwargs: Any,
) -> DataFrame:
    if drop_kwargs is None:
        drop_kwargs = {}

    try:
        df: DataFrame = DataFrame(input_, **kwargs)

        if "thresh" not in drop_kwargs:
            drop_kwargs["how"] = drop_how
        df = df.dropna(**drop_kwargs)
        return df.reset_index(drop=True) if reset_index else df
    except Exception as e:
        raise ValueError(f"Error converting input_ to DataFrame: {e}") from e


@to_df.register
def _(
    input_: list,
    /,
    *,
    drop_how: str = "all",
    drop_kwargs: dict | None = None,
    reset_index: bool = True,
    **kwargs,
) -> DataFrame:
    if not input_:
        return DataFrame()

    if not isinstance(input_[0], (DataFrame, Series, NDFrame)):
        if drop_kwargs is None:
            drop_kwargs = {}
        try:
            df: DataFrame = DataFrame(input_, **kwargs)
            if "thresh" not in drop_kwargs:
                drop_kwargs["how"] = drop_how
            df = df.dropna(**drop_kwargs)
            return df.reset_index(drop=True) if reset_index else df
        except Exception as e:
            raise ValueError(f"Error converting input_ to DataFrame: {e}") from e

    if drop_kwargs is None:
        drop_kwargs = {}
    try:
        df = concat(
            input_,
            axis=1 if all(isinstance(i, Series) for i in input_) else 0,
            **kwargs,
        )
    except Exception as e1:
        try:
            input_ = ln.to_list(input_)
            df = input_[0]
            if len(input_) > 1:
                for i in input_[1:]:
                    df = concat([df, i], **kwargs)
        except Exception as e2:
            raise ValueError(
                f"Error converting input_ to DataFrame: {e1}, {e2}"
            ) from e2

    drop_kwargs["how"] = drop_how
    df.dropna(**drop_kwargs, inplace=True)
    return df.reset_index(drop=True) if reset_index else df


class PandasSeriesConverter(Converter):

    @staticmethod
    def from_obj(cls, obj: Series, **kwargs: Any) -> dict:
        return ln.to_dict(obj, **kwargs)

    @staticmethod
    def to_obj(self, **kwargs: Any) -> Series:
        return Series(ln.to_dict(self), **kwargs)
