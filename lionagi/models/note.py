# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import ItemsView, Iterator, ValuesView
from typing import Any, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing_extensions import override

from lionagi.libs.nested.flatten import flatten
from lionagi.libs.nested.nget import nget
from lionagi.libs.nested.ninsert import ninsert
from lionagi.libs.nested.npop import npop
from lionagi.libs.nested.nset import nset
from lionagi.utils import UNDEFINED, copy, to_list

IndiceType: TypeAlias = str | list[str | int]


class Note(BaseModel):
    """Container for managing nested dictionary data structures.

    A flexible container that provides deep nested data access, dictionary-like
    interface, flattening capabilities, and update operations for managing
    complex nested data structures.

    Args:
        **kwargs: Key-value pairs for initial content.

    Attributes:
        content: Nested dictionary structure.
        model_config: Configuration allowing arbitrary types.

    Examples:
        >>> note = Note(
        ...     user={
        ...         "name": "John",
        ...         "settings": {
        ...             "theme": "dark"
        ...         }
        ...     }
        ... )
        >>>
        >>> # Access nested data
        >>> name = note.get(["user", "name"])
        >>> theme = note["user"]["settings"]["theme"]
        >>>
        >>> # Update nested structure
        >>> note.update(["user", "settings"], {"language": "en"})
    """

    content: dict[str, Any] = Field(
        default_factory=dict
    )  # Nested data structure

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize Note with dictionary data.

        Args:
            **kwargs: Key-value pairs that will form the initial nested
                dictionary structure.
        """
        super().__init__()
        self.content = kwargs

    @field_serializer("content")
    def _serialize_content(self, value: Any) -> dict[str, Any]:
        """Serialize content to dictionary format.

        Args:
            value: Content to serialize

        Returns:
            Deep copy of content dictionary
        """
        output_dict = copy(value, deep=True)
        return output_dict

    def to_dict(self) -> dict[str, Any]:
        """Convert Note to dictionary, excluding undefined values.

        Returns:
            Dictionary representation with UNDEFINED values removed
        """
        out = copy(self.content)
        for k, v in self.content.items():
            if v is UNDEFINED:
                out.pop(k)
        return out

    def pop(
        self,
        indices: IndiceType,
        /,
        default: Any = UNDEFINED,
    ) -> Any:
        """Remove and return item from nested structure.

        Removes and returns the value at the specified path in the nested
        structure. If the path doesn't exist and no default is provided,
        raises KeyError.

        Args:
            indices: Path to the item to remove, can be a string for top-level
                keys or a list for nested access.
            default: Value to return if the path is not found. If not provided
                and path is not found, raises KeyError.

        Returns:
            The value that was removed, or the default value if provided and
            path not found.

        Raises:
            KeyError: If the path is not found and no default value is provided.
        """
        indices = to_list(indices, flatten=True, dropna=True)
        return npop(self.content, indices, default)

    def insert(self, indices: IndiceType, value: Any, /) -> None:
        """Insert value into nested structure at specified indices.

        Args:
            indices: Path where to insert
            value: Value to insert
        """
        indices = to_list(indices, flatten=True, dropna=True)
        ninsert(self.content, indices, value)

    def set(self, indices: IndiceType, value: Any, /) -> None:
        """Set value in nested structure at specified indices.

        Args:
            indices: Path where to set
            value: Value to set
        """
        indices = to_list(indices, flatten=True, dropna=True)
        if self.get(indices, None) is None:
            self.insert(indices, value)
        else:
            nset(self.content, indices, value)

    def get(
        self,
        indices: IndiceType,
        /,
        default: Any = UNDEFINED,
    ) -> Any:
        """Get value from nested structure at specified indices.

        Retrieves the value at the specified path in the nested structure.
        If the path doesn't exist and no default is provided, raises KeyError.

        Args:
            indices: Path to the value, can be a string for top-level keys
                or a list for nested access.
            default: Value to return if the path is not found. If not provided
                and path is not found, raises KeyError.

        Returns:
            The value at the specified path, or the default value if provided
            and path not found.

        Raises:
            KeyError: If the path is not found and no default value is provided.
        """
        indices = to_list(indices, flatten=True, dropna=True)
        return nget(self.content, indices, default)

    def keys(self, /, flat: bool = False, **kwargs: Any) -> list:
        """Get keys of the Note.

        Args:
            flat: If True, return flattened keys
            kwargs: Additional flattening options

        Returns:
            List of keys, optionally flattened
        """
        if flat:
            kwargs["coerce_keys"] = kwargs.get("coerce_keys", False)
            kwargs["coerce_sequence"] = kwargs.get("coerce_sequence", "list")
            return flatten(self.content, **kwargs).keys()
        return list(self.content.keys())

    def values(self, /, flat: bool = False, **kwargs: Any) -> ValuesView:
        """Get values of the Note.

        Returns either a view of top-level values or, if flat=True, a view
        of all values in the flattened nested structure.

        Args:
            flat: If True, returns values from all levels of the nested
                structure. If False, returns only top-level values.
            kwargs: Additional options for flattening behavior when flat=True.
                Common options include coerce_keys and coerce_sequence.

        Returns:
            A ValuesView object containing either top-level values or all
            values from the flattened structure if flat=True.
        """
        if flat:
            kwargs["coerce_keys"] = kwargs.get("coerce_keys", False)
            kwargs["coerce_sequence"] = kwargs.get("coerce_sequence", "list")
            return flatten(self.content, **kwargs).values()
        return self.content.values()

    def items(self, /, flat: bool = False, **kwargs: Any) -> ItemsView:
        """Get items of the Note.

        Args:
            flat: If True, return flattened items
            kwargs: Additional flattening options

        Returns:
            View of items, optionally flattened
        """
        if flat:
            kwargs["coerce_keys"] = kwargs.get("coerce_keys", False)
            kwargs["coerce_sequence"] = kwargs.get("coerce_sequence", "list")
            return flatten(self.content, **kwargs).items()
        return self.content.items()

    def clear(self) -> None:
        """Clear all content."""
        self.content.clear()

    def update(
        self,
        indices: IndiceType,
        value: Any,
    ) -> None:
        """Update nested structure at specified indices.

        Updates the value at the specified path in the nested structure.
        The behavior depends on the existing value and the update value:
        - If path doesn't exist: creates it with value (wrapped in list if scalar)
        - If existing is list: extends with value if list, appends if scalar
        - If existing is dict: updates with value if dict, raises error if not

        Args:
            indices: Path to the location to update, can be a string for
                top-level keys or a list for nested access.
            value: The new value to set. Must be compatible with existing
                value type (dict for dict, any value for list).

        Raises:
            ValueError: If trying to update a dictionary with a non-dictionary
                value.
        """
        existing = None
        if not indices:
            existing = self.content
        else:
            existing = self.get(indices, None)

        if existing is None:
            if not isinstance(value, (list, dict)):
                value = [value]
            self.set(indices, value)

        if isinstance(existing, list):
            if isinstance(value, list):
                existing.extend(value)
            else:
                existing.append(value)

        elif isinstance(existing, dict):
            if isinstance(value, self.__class__):
                value = value.content

            if isinstance(value, dict):
                existing.update(value)
            else:
                raise ValueError(
                    "Cannot update a dictionary with a non-dictionary value."
                )

    @classmethod
    def from_dict(cls, kwargs: Any) -> "Note":
        """Create Note instance from dictionary.

        Args:
            kwargs: Dictionary to initialize with

        Returns:
            New Note instance
        """
        return cls(**kwargs)

    def __contains__(self, indices: IndiceType) -> bool:
        """Check if indices exist in content.

        Implements the 'in' operator for checking path existence in the nested
        structure.

        Args:
            indices: Path to check, can be a string for top-level keys or a
                list for nested access.

        Returns:
            True if the path exists in the nested structure, False otherwise.
        """
        return self.content.get(indices, UNDEFINED) is not UNDEFINED

    def __len__(self) -> int:
        """Get length of content.

        Implements len() function to return the number of top-level keys in
        the nested structure.

        Returns:
            The number of top-level keys in the content dictionary.
        """
        return len(self.content)

    def __iter__(self) -> Iterator[str]:
        """Get iterator over content.

        Returns:
            Iterator over top-level keys
        """
        return iter(self.content)

    def __next__(self) -> str:
        """Get next item from content iterator.

        Returns:
            Next key in iteration
        """
        return next(iter(self.content))

    @override
    def __str__(self) -> str:
        """Get string representation of content.

        Implements str() function to provide a simple string representation
        of the Note's content. Uses the standard dictionary string format.

        Returns:
            A string representation of the content dictionary, showing its
            current state.
        """
        return str(self.content)

    @override
    def __repr__(self) -> str:
        """Get detailed string representation of content.

        Returns:
            Detailed string representation of content dict
        """
        return repr(self.content)

    def __getitem__(self, indices: IndiceType) -> Any:
        """Get item using index notation.

        Args:
            indices: Path to value

        Returns:
            Value at path

        Raises:
            KeyError: If path not found
        """
        indices = to_list(indices, flatten=True, dropna=True)
        return self.get(indices)

    def __setitem__(self, indices: IndiceType, value: Any) -> None:
        """Set item using index notation.

        Args:
            indices: Path where to set
            value: Value to set
        """
        self.set(indices, value)
