import threading
from ....lion_core.collections.container import Container


class Index:
    """
    A class to manage a flat dictionary with various index operations.
    """

    def __init__(self, flat_dict):
        """
        Initialize the Index with a flat dictionary.

        Args:
            flat_dict (dict): The flat dictionary to be managed.
        """
        self.flat_dict = flat_dict
        self.cache = {}
        self.lock = threading.Lock()

    def is_valid_index(self, index):
        """
        Check if the given index is valid.

        Args:
            index (str): The index to be checked.

        Returns:
            bool: True if the index is valid, False otherwise.
        """
        return index in self.flat_dict

    def validate_indices(self, indices):
        """
        Validate a list of indices, ensuring all are valid.

        Args:
            indices (list): The list of indices to be validated.

        Raises:
            KeyError: If any index in the list is not found.
        """
        for index in indices:
            if not self.is_valid_index(index):
                raise KeyError(f"Index '{index}' not found")

    def get_value(self, index):
        """
        Retrieve the value for a given index.

        Args:
            index (str): The index to retrieve the value for.

        Returns:
            The value associated with the index.

        Raises:
            KeyError: If the index is not found.
        """
        if self.is_valid_index(index):
            return self.flat_dict[index]
        else:
            raise KeyError(f"Index '{index}' not found")

    def set_value(self, index, value):
        """
        Set the value for a given index.

        Args:
            index (str): The index to set the value for.
            value: The value to be set.

        Raises:
            KeyError: If the index is not found.
        """
        if self.is_valid_index(index):
            self.flat_dict[index] = value
        else:
            raise KeyError(f"Index '{index}' not found")

    def delete_value(self, index):
        """
        Delete the value for a given index.

        Args:
            index (str): The index to delete the value for.

        Raises:
            KeyError: If the index is not found.
        """
        if self.is_valid_index(index):
            del self.flat_dict[index]
        else:
            raise KeyError(f"Index '{index}' not found")

    def get_container(self, indices):
        """
        Retrieve a container with a nested structure built from given indices.

        Args:
            indices (list): The list of indices to build the container from.

        Returns:
            Container: A container with the nested structure.
        """
        nested_structure = self._build_structure(indices)
        return Container(nested_structure)

    def _build_structure(self, indices):
        """
        Build a nested structure from a list of indices.

        Args:
            indices (list): The list of indices to build the structure from.

        Returns:
            The nested structure.
        """
        structure = {}
        for index in indices:
            parts = index.split("/")
            current = structure
            for part in parts[:-1]:
                if part.isdigit():
                    part = int(part)
                if part not in current:
                    current[part] = {}
                current = current[part]
            last_part = parts[-1]
            if last_part.isdigit():
                last_part = int(last_part)
            current[last_part] = self.flat_dict[index]
        return self._convert_dict_to_list(structure)

    def _convert_dict_to_list(self, structure):
        """
        Convert a dictionary with integer keys to a list, preserving the
        original structure otherwise.

        Args:
            structure (dict): The structure to be converted.

        Returns:
            The converted structure.
        """
        if isinstance(structure, dict):
            keys = list(structure.keys())
            if all(isinstance(key, int) or key.isdigit() for key in keys):
                return [structure[key] for key in sorted(structure.keys(), key=int)]
            return {
                key: self._convert_dict_to_list(value)
                for key, value in structure.items()
            }
        return structure
