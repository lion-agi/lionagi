def get_keys(structure):
    """
    Retrieve the keys from a given structure.

    Args:
        structure (dict or list): The structure from which to get the keys.

    Returns:
        list: A list of keys if the structure is a dictionary or a list of
        indices if the structure is a list. Returns None if the structure is
        neither a dictionary nor a list.
    """
    if isinstance(structure, dict):
        return list(structure.keys())
    elif isinstance(structure, list):
        return list(range(len(structure)))
    return None


class Container:
    """
    A container class that manages a given structure and provides methods to
    navigate and manipulate the structure's elements.
    """

    def __init__(self, structure):
        """
        Initialize the container with a given structure.

        Args:
            structure (dict or list): The initial structure to be managed by
            the container.
        """
        self.current_key = None
        self.structure = self._convert_dict_to_list(structure)
        self.keys = get_keys(self.structure)
        self.current = self.structure
        

    def next(self):
        """
        Move to the next key in the structure.

        Returns:
            The next key if available, otherwise None.
        """
        if self.current_key is None:
            if self.keys:
                self.current_key = self.keys[0]
                return self.current_key
        else:
            index = self.keys.index(self.current_key)
            if index < len(self.keys) - 1:
                self.current_key = self.keys[index + 1]
                return self.current_key
        return None

    def get_current(self):
        """
        Get the current value in the structure.

        Returns:
            The current value if the current key is set, otherwise None.
        """
        if self.current_key is not None:
            return self.current[self.current_key]
        return None

    def get_current_key(self):
        """
        Get the current key.

        Returns:
            The current key.
        """
        return self.current_key

    def set_current(self, value):
        """
        Set the current structure to a new value and reset the keys.

        Args:
            value (dict or list): The new structure to be managed by the
            container.
        """
        self.structure = self._convert_dict_to_list(value)
        self.keys = get_keys(self.structure)
        self.current = self.structure
        self.current_key = None

    def set_current_key(self, key):
        """
        Set the current key to a given key if it exists in the structure.

        Args:
            key: The key to be set as the current key.
        """
        if key in self.keys:
            self.current_key = key

    def get_current_value(self):
        """
        Get the current value in the structure.

        Returns:
            The current value if the current key is set, otherwise None.
        """
        if self.current_key is not None:
            return self.current[self.current_key]
        return None

    def set_current_value(self, value):
        """
        Set the current value in the structure.

        Args:
            value: The value to be set at the current key.
        """
        if self.current_key is not None:
            self.current[self.current_key] = value

    def get_current_structure(self):
        """
        Get the current structure managed by the container.

        Returns:
            The current structure.
        """
        return self.structure

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
