# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Component protocol implementation with adapter pattern support.
Provides base component class with format conversion capabilities.
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import Field

from .adapter import Adapter, AdapterRegistry, ComponentRegistry
from .models import BaseAutoModel

__all__ = ("Component",)


class Component(BaseAutoModel):
    """Base component with adapter registry and format conversion support."""

    # Class-level adapter registry
    _adapter_registry: ClassVar = ComponentRegistry

    metadata: dict[str, Any] = {}
    embedding: list[float] = Field(
        default_factory=list,
        description="Optional embedding vector for the model",
    )

    def adapt_to(self, object_key: str, /, *args, **kwargs: Any) -> Any:
        """Convert component to target format using registered adapter."""
        kwargs["many"] = False
        return self._get_adapter_registry().adapt_to(
            self, object_key, *args, **kwargs
        )

    @classmethod
    def list_adapters(cls) -> list[str]:
        """Get list of registered adapter keys."""

        return cls._get_adapter_registry().list_adapters()

    @classmethod
    def register_adapter(cls, adapter: type[Adapter]) -> None:
        """Register new adapter class."""
        cls._get_adapter_registry().register(adapter)

    @classmethod
    def _get_adapter_registry(cls) -> AdapterRegistry:
        """Get or initialize adapter registry instance."""
        if isinstance(cls._adapter_registry, type):
            cls._adapter_registry = cls._adapter_registry()
        return cls._adapter_registry

    @classmethod
    def adapt_from(
        cls, obj: Any, object_key: str, /, **kwargs: Any
    ) -> Component:
        """Create component instance from source object using adapter."""
        kwargs["many"] = False
        dict_ = cls._get_adapter_registry().adapt_from(
            cls, obj, object_key, **kwargs
        )
        return cls.from_dict(dict_)


# File: lion/protocols/component.py
