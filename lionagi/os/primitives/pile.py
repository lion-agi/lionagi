import json
import re
from typing_extensions import override
from pathlib import Path
from typing import Any, ClassVar, Type
from lion_core.generic.pile import Pile as CorePile

from lionagi.os.primitives.node import Node
from ._pile_loader import PileLoaderRegistry, PileLoader

import pandas as pd
from lionagi.app.Pandas.convert import to_df


class Pile(CorePile):
    """async-compatible, ordered collection of Observable elements."""

    _loader_registry: ClassVar = PileLoaderRegistry

    @classmethod
    def get_loader_registry(cls) -> PileLoaderRegistry:
        """Get the converter registry for the class."""
        if isinstance(cls._loader_registry, type):
            cls._loader_registry = cls._loader_registry()
        return cls._loader_registry

    @classmethod
    def load(
        cls,
        items=None,
        item_type=None,
        order=None,
        strict=False,
        csv_: str | Path = None,
        df_: pd.DataFrame = None,
        json_: str | Path = None,
        vector_store: str | Path = None,
        read_file: str | Path = None,
        read_file_kwargs: dict = None,
        **kwargs,
    ):
        config = {
            "item_type": item_type,
            "order": order,
            "strict": strict,
            **(read_file_kwargs or {}),
        }
        if sum([csv_, df_, json_, vector_store, items]) != 1:
            raise ValueError("Only one loader can be used at a time")

        if csv_:
            return cls._load_from(csv_, "csv", config)
        if json_:
            if isinstance(json_, str):
                json_ = Path(json_)
            return cls.from_dict(json.load(open(json_)), **config)
        if vector_store:
            return cls._load_from(vector_store, "llama_index_vector_store", config)
        if read_file:
            return cls._load_from(read_file, "llama_index_read_file", config)
        if df_:
            return cls._load_from(df_, "pd.DataFrame", config)
        if items:
            return cls(items=items, **config, **kwargs)
        raise ValueError("No loader provided")

    @classmethod
    def _load_from(
        cls,
        obj: Any,
        key: str,
        _config: dict,
    ) -> "Pile" | list:
        data = cls.get_loader_registry().load_from(obj, key)
        if not data:
            raise ValueError(f"Could not load data from {obj}")
        data = [data] if not isinstance(data, list) else data
        if isinstance(data[0], dict):
            return cls([Node.from_dict(d) for d in data], **_config)
        elif isinstance(data[0], list):
            return [
                cls([Node.from_dict(d) for d in data_], **_config) for data_ in data
            ]
        raise ValueError(f"Could not load data from {obj}")

    @classmethod
    def register_loader(
        cls,
        key: str,
        loader: Type[PileLoader],
    ) -> None:
        """Register a new converter. Can be used for both a class and/or an instance."""
        cls.get_loader_registry().register(key, loader)

    def to_df(self) -> pd.DataFrame:
        dicts_ = []
        for i in self:
            _dict: dict = i.to_dict()
            if _dict.get("embedding", None):
                _dict["embedding"] = str(_dict.get("embedding"))
            dicts_.append(_dict)
        return to_df(dicts_)

    @override
    def __str__(self):
        return self.to_df().__str__()

    @override
    def __repr__(self):
        return self.to_df().__repr__()

    @override
    def info(self):
        return self.to_df().info()


def pile(
    items=None,
    item_type=None,
    order=None,
    strict=False,
    csv_: str | Path = None,
    df_: pd.DataFrame = None,
    json_: str | Path = None,
    vector_store: str | Path = None,
    read_file: str | Path = None,
    **kwargs,
) -> Pile:
    """
    type alias type for Pile class. Create a new Pile instance.

    Args:
        items: A single or sequence/mapping of observable item(s)
        item_type: Allowed types for items in the pile.
        order: Initial order of items. Defaults to None.
        strict: If True, enforce strict type checking, otherwise
                will allow the subclasses as well.

    Raises:
        LionValueError, LionTypeError

    Returns:
        Pile: A new Pile instance.
    """
    return Pile.load(
        items=items,
        item_type=item_type,
        order=order,
        strict=strict,
        csv_=csv_,
        df_=df_,
        json_=json_,
        vector_store=vector_store,
        read_file=read_file,
        **kwargs,
    )


__all__ = ["Pile", "pile"]
