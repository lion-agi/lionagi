from abc import ABC
from typing import Any, Callable, TypeVar

from pydantic import BaseModel

import lionagi.libs.ln_nested as nested

from lionagi.libs.sys_util import SysUtil


T = TypeVar("T")  # Generic type for return type of from_obj method


class BaseMetaManageMixin(ABC, BaseModel):

    def meta_keys(self, flattened: bool = False, **kwargs) -> list[str]:
        """
        Retrieves a list of metadata keys.

        Args:
            flattened (bool): If True, returns keys from a flattened metadata structure.
            **kwargs: Additional keyword arguments passed to the flattening function.

        Returns:
            list[str]: List of metadata keys.
        """
        if flattened:
            return nested.get_flattened_keys(self.metadata, **kwargs)
        return list(self.metadata.keys())

    def meta_has_key(self, key: str, flattened: bool = False, **kwargs) -> bool:
        """
        Checks if a specified key exists in the metadata.

        Args:
            key (str): The key to check.
            flattened (bool): If True, checks within a flattened metadata structure.
            **kwargs: Additional keyword arguments for flattening.

        Returns:
            bool: True if key exists, False otherwise.
        """
        if flattened:
            return key in nested.get_flattened_keys(self.metadata, **kwargs)
        return key in self.metadata

    def meta_get(
        self, key: str, indices: list[str | int] = None, default: Any = None
    ) -> Any:
        """
        Retrieves the value associated with a given key from the metadata.

        Args:
            key (str): The key for the desired value.
            indices: Optional indices for nested retrieval.
            default (Any): The default value to return if the key is not found.

        Returns:
            Any: The value associated with the key or the default value.
        """
        if indices:
            return nested.nget(self.metadata, key, indices, default)
        return self.metadata.get(key, default)

    def meta_change_key(self, old_key: str, new_key: str) -> bool:
        """
        Renames a key in the metadata.

        Args:
            old_key (str): The current key name.
            new_key (str): The new key name.

        Returns:
            bool: True if the key was changed, False otherwise.
        """
        if old_key in self.metadata:
            SysUtil.change_dict_key(self.metadata, old_key, new_key)
            return True
        return False

    def meta_insert(self, indices: str | list, value: Any, **kwargs) -> bool:
        """
        Inserts a value into the metadata at specified indices.

        Args:
            indices (str | list): The indices where the value should be inserted.
            value (Any): The value to insert.
            **kwargs: Additional keyword arguments.

        Returns:
            bool: True if the insertion was successful, False otherwise.
        """
        return nested.ninsert(self.metadata, indices, value, **kwargs)

    # ToDo: do a nested pop
    def meta_pop(self, key: str, default: Any = None) -> Any:
        """
        Removes a key from the metadata and returns its value.

        Args:
            key (str): The key to remove.
            default (Any): The default value to return if the key is not found.

        Returns:
            Any: The value of the removed key or the default value.
        """
        return self.metadata.pop(key, default)

    def meta_merge(
        self, additional_metadata: dict[str, Any], overwrite: bool = False, **kwargs
    ) -> None:
        """
        Merges additional metadata into the existing metadata.

        Args:
            additional_metadata (dict[str, Any]): The metadata to merge in.
            overwrite (bool): If True, existing keys will be overwritten by those in additional_metadata.
            **kwargs: Additional keyword arguments for the merge.

        Returns:
            None
        """
        nested.nmerge(
            [self.metadata, additional_metadata], overwrite=overwrite, **kwargs
        )

        for key, value in additional_metadata.items():
            if overwrite or key not in self.metadata:
                self.metadata[key] = value

    def meta_clear(self) -> None:
        """
        Clears all metadata.

        Returns:
            None
        """
        self.metadata.clear()

    def meta_filter(self, condition: Callable[[Any, Any], bool]) -> dict[str, Any]:
        """
        Filters the metadata based on a condition.

        Args:
            condition (Callable[[Any, Any], bool]): The condition function to apply.

        Returns:
            dict[str, Any]: The filtered metadata.
        """
        return nested.nfilter(self.metadata, condition)
