# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any, ClassVar

from pydantic import Field

from .adapter import Adapter, AdapterRegistry, ComponentRegistry
from .models import BaseAutoModel

__all__ = ("Component",)


class Component(BaseAutoModel):
    # Class-level adapter registry
    _adapter_registry: ClassVar = ComponentRegistry

    metadata: dict[str, Any] = {}
    embedding: list[float] = Field(
        default_factory=list,
        description="Optional embedding vector for the model",
    )

    def adapt_to(self, object_key: str, /, *args, **kwargs: Any) -> Any:
        """
        Asynchronously adapt the component to another object type.

        Args:
            object_key: Target object type identifier
            *args: Additional positional arguments for adapter
            **kwargs: Additional keyword arguments for adapter

        Returns:
            The adapted object.

        Example:
            >>> json_str = await component.adapt_to("json")
        """
        kwargs["many"] = False
        return self._get_adapter_registry().adapt_to(
            self, object_key, *args, **kwargs
        )

    @classmethod
    def list_adapters(cls) -> list[str]:
        """
        List available adapters. This is a synchronous operation since it just
        returns a list of registered adapter keys from memory.

        Returns:
            List of registered adapter keys.

        Example:
            >>> adapters = Component.list_adapters()
            >>> print(adapters)  # ['json', ...]
        """
        return cls._get_adapter_registry().list_adapters()

    @classmethod
    def register_adapter(cls, adapter: type[Adapter]) -> None:
        """
        Register a new adapter type. This remains synchronous since adapter registration
        is an in-memory operation.

        Args:
            adapter: Adapter class to register

        Raises:
            ValueError: If adapter is invalid
        """
        cls._get_adapter_registry().register(adapter)

    @classmethod
    def _get_adapter_registry(cls) -> AdapterRegistry:
        """
        Get the adapter registry for the class. Remains synchronous since it's just returning
        or creating a registry instance.

        Returns:
            AdapterRegistry: Registry instance
        """
        if isinstance(cls._adapter_registry, type):
            cls._adapter_registry = cls._adapter_registry()
        return cls._adapter_registry

    @classmethod
    def adapt_from(
        cls, obj: Any, object_key: str, /, **kwargs: Any
    ) -> "Component":
        """
        Asynchronously create a component from an adapted object.

        Args:
            obj: Object to adapt from
            object_key: Source object type identifier
            **kwargs: Additional adapter arguments

        Returns:
            New component instance

        Example:
            >>> json_str = '{"name": "test"}'
            >>> component = await Component.adapt_from(json_str, "json")
        """
        kwargs["many"] = False
        dict_ = cls._get_adapter_registry().adapt_from(
            cls, obj, object_key, **kwargs
        )
        return cls.from_dict(dict_)


# File: lion/protocols/component.py
