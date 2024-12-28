from abc import ABC
from typing import Any, ClassVar

from pydantic import Field

from .._adapter import DEFAULT_ADAPTERS, Adaptable, AdapterRegistry
from .element import Element

__all__ = (
    "Relational",
    "Node",
)


class NodeAdapterRegistry(AdapterRegistry):
    """Adapter registry for nodes."""


for i in DEFAULT_ADAPTERS:
    NodeAdapterRegistry.register(i)


class Relational(ABC):
    """Base class for all relational elements."""

    pass


class Node(Element, Adaptable, Relational):
    """Base class for all nodes."""

    metadata: dict = Field(default_factory=dict)

    embedding: list[float] | None = None

    adapter_registry: ClassVar[AdapterRegistry] = NodeAdapterRegistry

    def adapt_to(
        self, obj_key: str, /, many: bool = False, **kwargs: Any
    ) -> Any:
        """Convert this component to another format using registered adapters.

        Args:
            obj_key: Key identifying the target format.
            *args: Additional positional arguments for the adapter.
            **kwargs: Additional keyword arguments for the adapter.

        Returns:
            Any: The component converted to the target format.
        """
        return self._get_adapter_registry().adapt_to(
            self, obj_key, many=many, **kwargs
        )

    @classmethod
    def adapt_from(
        cls, obj: Any, obj_key: str, /, many: bool = False, **kwargs: Any
    ):
        """Create a component instance from another format using registered adapters.

        Args:
            obj: The object to convert from.
            obj_key: Key identifying the source format.
            **kwargs: Additional arguments for the adapter.

        Returns:
            Component: A new component instance.
        """
        dict_ = cls._get_adapter_registry().adapt_from(
            cls, obj, obj_key, many=many, **kwargs
        )
        return cls.from_dict(dict_)
