import asyncio
from .container import Container
from lionagi.os.lib import nget, nset, ninsert, nfilter, nmerge, npop




class ContainerIndex:














    def __init__(self, flat_dict, separator="|"):
        self.flat_dict = flat_dict
        self.cache = {}
        self.lock = asyncio.Lock()
        self.separator = separator

    def is_valid_index(self, index):
        return index in self.flat_dict

    def validate_indices(self, indices):
        for index in indices:
            if not self.is_valid_index(index):
                raise KeyError(f"Index '{index}' not found")

    def get_value(self, index):
        if self.is_valid_index(index):
            return self.flat_dict[index]
        else:
            raise KeyError(f"Index '{index}' not found")

    def set_value(self, index, value):
        if self.is_valid_index(index):
            self.flat_dict[index] = value
        else:
            raise KeyError(f"Index '{index}' not found")

    def delete_value(self, index):
        if self.is_valid_index(index):
            del self.flat_dict[index]
        else:
            raise KeyError(f"Index '{index}' not found")

    def get_container(self, indices):
        nested_structure = self._build_structure(indices)
        return Container(nested_structure)

    def _build_structure(self, indices):
        structure = {}
        for index in indices:
            parts = index.split(self.separator)
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
        if isinstance(structure, dict):
            keys = list(structure.keys())
            if all(isinstance(key, int) or key.isdigit() for key in keys):
                return [structure[key] for key in sorted(structure.keys(), key=int)]
            return {
                key: self._convert_dict_to_list(value)
                for key, value in structure.items()
            }
        return structure
