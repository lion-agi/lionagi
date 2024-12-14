# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Component protocol implementation with adapter pattern support.
Provides base component class with format conversion capabilities.
"""

from __future__ import annotations

import json
from typing import Any, ClassVar

from pydantic import Field, field_validator

from lionagi.libs.parse.types import to_dict
from lionagi.utils import is_same_dtype

from .adapter import Adapter, AdapterRegistry, ComponentRegistry
from .models import BaseAutoModel, get_class

__all__ = ("Component",)


class Component(BaseAutoModel):
    """Base component with adapter registry and format conversion support."""

    # Class-level adapter registry
    _adapter_registry: ClassVar = ComponentRegistry

    content: Any = None
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
    def from_dict(cls, data: dict[str, Any]) -> Component:
        """Create component instance from dictionary."""
        if "lion_class" in data:
            cls = get_class(data.pop("lion_class"))
            if cls.from_dict != Component.from_dict:
                return cls.from_dict(data)
        return super().from_dict(data)

    @field_validator("metadata", mode="before")
    def _validate_metadata(cls, value: dict[str, Any]) -> dict[str, Any]:
        return to_dict(value, fuzzy_parse=True)

    @field_validator("embedding", mode="before")
    def _validate_embedding(cls, value: list[float]) -> list[float]:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return []
        if isinstance(value, list):
            if is_same_dtype(value, str):
                return [float(v) for v in value]
        return []

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
