# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Defines the `Adapter` protocol (a formal interface), along with the
`AdapterRegistry` that maps string/file extensions or object keys to
specific adapter implementations.
"""

import logging
from typing import Any, Protocol, TypeVar, runtime_checkable

from typing_extensions import get_protocol_members

T = TypeVar("T")

__all__ = (
    "Adapter",
    "ADAPTER_MEMBERS",
    "AdapterRegistry",
)


@runtime_checkable
class Adapter(Protocol):
    """
    Describes a two-way converter that knows how to transform an object
    from an external representation to an internal format, and vice versa.

    Attributes
    ----------
    obj_key : str
        A unique key or extension that identifies what format this
        adapter supports (e.g. ".csv", "json", "pd_dataframe").

    Methods
    -------
    from_obj(subj_cls: type[T], obj: Any, /, many: bool, **kwargs) -> dict|list[dict]
        Converts a raw external object (file contents, JSON string, etc.)
        into a dictionary or list of dictionaries.
    to_obj(subj: T, /, many: bool, **kwargs) -> Any
        Converts an internal object (e.g., a Pydantic-based model)
        into the target format (file, JSON, DataFrame, etc.).
    """

    obj_key: str

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[T],
        obj: Any,
        /,
        *,
        many: bool,
        **kwargs,
    ) -> dict | list[dict]: ...

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        *,
        many: bool,
        **kwargs,
    ) -> Any: ...


ADAPTER_MEMBERS = get_protocol_members(Adapter)  # duck typing


class AdapterRegistry:

    _adapters: dict[str, Adapter] = {}

    @classmethod
    def list_adapters(cls) -> list[tuple[str | type, ...]]:
        return list(cls._adapters.keys())

    @classmethod
    def register(cls, adapter: type[Adapter]) -> None:
        for member in ADAPTER_MEMBERS:
            if not hasattr(adapter, member):
                _str = getattr(adapter, "obj_key", None) or repr(adapter)
                _str = _str[:50] if len(_str) > 50 else _str
                raise AttributeError(
                    f"Adapter {_str} missing required methods."
                )

        if isinstance(adapter, type):
            cls._adapters[adapter.obj_key] = adapter()
        else:
            cls._adapters[adapter.obj_key] = adapter

    @classmethod
    def get(cls, obj_key: type | str) -> Adapter:
        try:
            return cls._adapters[obj_key]
        except Exception as e:
            logging.error(f"Error getting adapter for {obj_key}. Error: {e}")

    @classmethod
    def adapt_from(
        cls, subj_cls: type[T], obj: Any, obj_key: type | str, **kwargs
    ) -> dict | list[dict]:
        try:
            return cls.get(obj_key).from_obj(subj_cls, obj, **kwargs)
        except Exception as e:
            logging.error(f"Error adapting data from {obj_key}. Error: {e}")
            raise e

    @classmethod
    def adapt_to(cls, subj: T, obj_key: type | str, **kwargs) -> Any:
        try:
            return cls.get(obj_key).to_obj(subj, **kwargs)
        except Exception as e:
            logging.error(f"Error adapting data to {obj_key}. Error: {e}")
            raise e
