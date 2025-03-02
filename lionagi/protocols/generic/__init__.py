# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, Optional, Protocol, TypeVar, runtime_checkable

E = TypeVar("E")


@runtime_checkable
class Element(Protocol):
    """Protocol for basic elements in the system.

    This protocol defines the interface for elements that can be
    managed and manipulated within the system. Elements are the fundamental
    building blocks that can be tracked, serialized, and managed.

    Attributes:
        name (str): The element's identifier name
        type (str): The element's type identifier
    """

    @property
    def name(self) -> str:
        """Get the element name."""
        ...

    @property
    def type(self) -> str:
        """Get the element type."""
        ...

    def get_state(self) -> dict[str, Any]:
        """Get current element state.

        Returns:
            Dict containing the serialized element state
        """
        ...

    def set_state(self, state: dict[str, Any]) -> None:
        """Set element state.

        Args:
            state: Dictionary containing the state to restore
        """
        ...

    def to_dict(self) -> dict[str, Any]:
        """Convert element to dictionary representation.

        Returns:
            Dict containing serialized element data
        """
        ...

    def validate(self) -> bool:
        """Validate the element's current state.

        Returns:
            bool: True if valid, False otherwise

        Raises:
            ValueError: If validation fails
        """
        ...
