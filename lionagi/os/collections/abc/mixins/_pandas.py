from pandas import Series, DataFrame

from typing import TypeVar

T = TypeVar("T")


class PandasComponentMixin:

    def to_pd_series(self, *args, pd_kwargs=None, dropna=False, **kwargs) -> Series:
        """Convert the node to a Pandas Series."""
        pd_kwargs = pd_kwargs or {}
        dict_ = self.to_dict(*args, dropna=dropna, **kwargs)
        return Series(dict_, **pd_kwargs)

    @classmethod
    def _from_pd_series(
        cls, obj: Series, /, *args, pd_kwargs: dict | None = None, **kwargs
    ) -> T:
        """Create a node instance from a Pandas Series."""
        pd_kwargs = pd_kwargs or {}
        return cls.from_obj(obj.to_dict(**pd_kwargs), *args, **kwargs)

    @classmethod
    def _from_pd_dataframe(
        cls,
        obj: DataFrame,
        /,
        *args,
        pd_kwargs: dict | None = None,
        include_index=False,
        **kwargs,
    ) -> list[T]:
        """Create a list of node instances from a Pandas DataFrame."""
        pd_kwargs = pd_kwargs or {}

        _objs = []
        for index, row in obj.iterrows():
            _obj = cls.from_obj(row, *args, **pd_kwargs, **kwargs)
            if include_index:
                _obj.metadata["df_index"] = index
            _objs.append(_obj)

        return _objs
