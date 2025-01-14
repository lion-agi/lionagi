# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
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
    """
    A registry that allows users to register multiple adapter types under
    a key (usually a file extension or a short string like "json").
    Then, code can call `adapt_from` or `adapt_to` using that key.
    """

    _adapters: dict[str, Adapter] = {}

    @classmethod
    def list_adapters(cls) -> list[str]:
        """
        Returns the list of adapter keys currently registered.

        Returns
        -------
        list[str]
            All keys under which adapters have been registered.
        """
        return list(cls._adapters.keys())

    @classmethod
    def register(cls, adapter: type[Adapter]) -> None:
        """
        Register a new adapter class or instance with the registry.
        The adapter must provide all members of the `Adapter` protocol.

        Parameters
        ----------
        adapter : type[Adapter]
            The adapter class (or instance) to register.

        Raises
        ------
        AttributeError
            If the adapter is missing one of the required methods/attributes.
        """
        for member in ADAPTER_MEMBERS:
            if not hasattr(adapter, member):
                _str = getattr(adapter, "obj_key", None) or repr(adapter)
                _str = _str[:50] if len(_str) > 50 else _str
                raise AttributeError(
                    f"Adapter {_str} missing required methods."
                )
        if isinstance(adapter, type):
            # If it's a class, instantiate
            cls._adapters[adapter.obj_key] = adapter()
        else:
            # Otherwise assume it's already an instance
            cls._adapters[adapter.obj_key] = adapter

    @classmethod
    def get(cls, obj_key: str) -> Adapter:
        """
        Retrieve an adapter by its registered key.

        Parameters
        ----------
        obj_key : str
            The key or extension (e.g., ".csv").

        Returns
        -------
        Adapter
            The adapter instance matching this key, or None if not found.

        Raises
        ------
        KeyError
            If no adapter is found under that key.
        """
        if obj_key not in cls._adapters:
            raise KeyError(
                f"No adapter registered under key '{obj_key}'. "
                f"Available: {cls.list_adapters()}"
            )

    @classmethod
    def adapt_from(
        cls,
        subj_cls: type[T],
        obj: Any,
        obj_key: str,
        **kwargs,
    ) -> dict | list[dict]:
        """
        Use the appropriate adapter to convert `obj` -> dict/list-of-dict.

        Parameters
        ----------
        subj_cls : type[T]
            The internal class or type we are eventually constructing.
        obj : Any
            The external data source (file path, raw JSON, etc.).
        obj_key : str
            The adapter key or extension (e.g. "json", ".csv").
        **kwargs
            Extra arguments passed to the adapter's 'from_obj' method.

        Returns
        -------
        dict|list[dict]
            The dictionary representation or a list of them.

        Raises
        ------
        Exception
            If the adapter fails to parse or transform the data.
        """
        try:
            return cls.get(obj_key).from_obj(subj_cls, obj, **kwargs)
        except Exception as e:
            logging.error(
                f"Failed `adapt_from` using key={obj_key}. Error: {e}"
            )
            raise

    @classmethod
    def adapt_to(cls, subj: T, obj_key: str, **kwargs) -> Any:
        """
        Use the appropriate adapter to serialize `subj` -> external format.

        Parameters
        ----------
        subj : T
            The internal object to serialize.
        obj_key : str
            The adapter key or extension.
        **kwargs
            Extra arguments for the adapter's 'to_obj' method.

        Returns
        -------
        Any
            The transformed object (e.g., string data, or writing to file).
        """
        try:
            return cls.get(obj_key).to_obj(subj, **kwargs)
        except Exception as e:
            logging.error(f"Failed `adapt_to` using key={obj_key}. Error: {e}")
            raise


# File: lionagi/protocols/adapters/adapter.py
