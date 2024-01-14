from collections import defaultdict
from collections.abc import Iterable as ABCIterable
from copy import deepcopy
from itertools import chain
from typing import Any, Callable, Dict, Generator, List, Tuple, Union, Iterable


class NestedUtil:

    @staticmethod
    def filter(collection: Union[Dict, List], condition: Callable[[Any], bool]) -> Union[Dict, List]:
        """Filters a collection (either a dictionary or a list) based on a given condition.

        This static method delegates to either `filter_dict` or `filter_list` based on the
        type of the collection.

        Args:
            collection: A collection to filter, either a dictionary or a list.
            
            condition: A callable that takes an item (key-value pair for dictionaries, single item for lists)
                and returns a boolean. If True, the item is included in the result.

        Returns:
            A new collection of the same type as the input, containing only the items that meet the condition.

        Raises:
            TypeError: If the collection is neither a dictionary nor a list.

        """
        if isinstance(collection, Dict):
            return NestedUtil._filter_dict(collection, condition)
        elif isinstance(collection, List):
            return NestedUtil._filter_list(collection, condition)
        else:
            raise TypeError("The collection must be either a Dict or a List.")

    @staticmethod
    def set_value(nested_structure: Union[List, Dict], indices: List[Union[int, str]], value: Any) -> None:
        """Sets a value in a nested list or dictionary structure.

        Navigates through the nested structure according to the specified indices and sets the
        value at the target location. The indices can be a mix of integers (for lists) and
        strings (for dictionaries).

        Args:
            nested_structure: The nested list or dictionary structure.
            
            indices: A list of indices to navigate through the structure.
            
            value: The value to set at the target location.

        Raises:
            ValueError: If the indices list is empty.
            
            TypeError: If the target container or the last index is of an incorrect type.
        """
        if not indices:
            raise ValueError("Indices list is empty, cannot determine target container")

        target_container = NestedUtil._get_target_container(nested_structure, indices[:-1])
        last_index = indices[-1]

        if isinstance(target_container, list):
            NestedUtil._ensure_list_index(target_container, last_index)
            target_container[last_index] = value
        elif isinstance(target_container, dict):
            target_container[last_index] = value
        else:
            raise TypeError("Cannot set value on non-list/dict element")

    @staticmethod
    def get_value(nested_structure: Union[List, Dict], indices: List[Union[int, str]]) -> Any:
        """Retrieves a value from a nested list or dictionary structure.

        Navigates through the nested structure using the specified indices and retrieves the value
        at the target location. The indices can be integers for lists and strings for dictionaries.

        Args:
            nested_structure: The nested list or dictionary structure.
            
            indices: A list of indices to navigate through the structure.

        Returns:
            The value at the target location, or None if the target cannot be reached or does not exist.

        """
        try:
            target_container = NestedUtil._get_target_container(nested_structure, indices[:-1])
            last_index = indices[-1]

            if isinstance(target_container, list) and isinstance(last_index, int) and last_index < len(target_container):
                return target_container[last_index]
            elif isinstance(target_container, dict) and last_index in target_container:
                return target_container[last_index]
            else:
                return None  # Index out of bounds or not found
        except (IndexError, KeyError, TypeError):
            return None

    @staticmethod
    def merge(iterables: List[Union[Dict, List, Iterable]], 
              dict_update: bool = False, 
              dict_sequence: bool = False, 
              sequence_separator: str = '_', 
              sort_list: bool = False, 
              custom_sort: Callable[[Any], Any] = None) -> Union[Dict, List]:
        """Merges a list of dictionaries or sequences into a single dictionary or list.

        Args:
            iterables: A list of dictionaries or sequences to be merged.
            
            dict_update: If merging dictionaries, whether to overwrite values of the same key.
            
            dict_sequence: If merging dictionaries, whether to create unique keys for duplicate keys.
            
            sequence_separator: Separator for creating unique keys when dict_sequence is True.
            
            sort_list: If merging sequences, whether to sort the merged list.
            
            custom_sort: Custom sorting function for sorting the merged sequence.

        Returns:
            A merged dictionary or list based on the type of elements in iterables.

        Raises:
            TypeError: If the elements of iterables are not all of the same type.
        """
        if NestedUtil._is_homogeneous(iterables, Dict):
            return NestedUtil._merge_dicts(iterables, dict_update, dict_sequence, sequence_separator)
        elif NestedUtil._is_homogeneous(iterables, (List, Iterable)) and not any(isinstance(it, str) for it in iterables):
            return NestedUtil._merge_sequences(iterables, sort_list, custom_sort)
        else:
            raise TypeError("All items in the input list must be of the same type, either Dict, List, or Iterable.")

    @staticmethod
    def dynamic_flatten(obj: Any, parent_key: str = '', sep: str = '_', 
                        max_depth: Union[int, None] = None, inplace: bool = False,
                        dict_only: bool = False) -> Dict:
        """
        Recursively flattens a nested dictionary (and optionally other iterables) 
        into a single-level dictionary with keys as the path.

        Args:
            obj (Any): The object to flatten. Can be a dictionary, list, or other iterables.
            
            parent_key (str, optional): The base key for the flattened dictionary. Defaults to ''.
            
            sep (str, optional): Separator to use in the keys of the flattened dictionary. Defaults to '_'.
            
            max_depth (Union[int, None], optional): Maximum depth to flatten. If None, flattens completely. 
            Defaults to None.
            inplace (bool, optional): If True, modifies the original object; otherwise, returns a new object. Defaults to False.
            
            dict_only (bool, optional): If True, flattens only dictionaries; otherwise, flattens lists and other iterables too. Defaults to False.

        Returns:
            Dict: The flattened dictionary.
        """
        
        parent_key_tuple = tuple(parent_key.split(sep)) if parent_key else ()
        if inplace:
            NestedUtil._dynamic_flatten_in_place(obj, parent_key, sep, max_depth, dict_only=dict_only)
            return obj
        return dict(NestedUtil._dynamic_flatten_generator(obj, parent_key_tuple, sep, max_depth, dict_only=dict_only))

    @staticmethod
    def handle_list_insert(sub_obj: List, part: int, value: Any):
        """
        Inserts or replaces a value in a list at a specified index. If the index is 
        beyond the current size of the list, the list is extended with `None` values.

        Args:
            sub_obj (List): The list in which the value needs to be inserted.
            
            part (int): The index at which the value should be inserted.
            
            value (Any): The value to insert into the list.

        Returns:
            None: This function modifies the input list in place and returns None.
        """
        while len(sub_obj) <= part:
            sub_obj.append(None)
        sub_obj[part] = value

    @staticmethod
    def insert(sub_obj: Union[Dict, List], parts: List[Union[str, int]], 
            value: Any, max_depth: Union[int, None] = None, current_depth: int = 0):
        """
        Recursively inserts a value into a nested structure (dictionary or list) based on 
        the specified path (parts).

        Args:
            sub_obj (Union[Dict, List]): The object (dictionary or list) to modify.
            
            parts (List[Union[str, int]]): The path where the value needs to be inserted.
            
            value (Any): The value to insert.
            
            max_depth (Union[int, None], optional): Maximum depth for insertion. Defaults to None.
            
            current_depth (int, optional): Current depth in recursion. Defaults to 0.

        Returns:
            None: This function modifies the input object in place and returns None.
        """
        for part in parts[:-1]:
            # Stop nesting further if max_depth is reached
            if max_depth is not None and current_depth >= max_depth:
                if isinstance(sub_obj, list):
                    NestedUtil.handle_list_insert(sub_obj, part, {parts[-1]: value})
                else:
                    sub_obj[part] = {parts[-1]: value}
                return

            if isinstance(part, str) and part.isdigit():
                part = int(part)
            if isinstance(part, int):
                # Ensure sub_obj is a list when part is an integer
                if not isinstance(sub_obj, list):
                    sub_obj = sub_obj.setdefault(part, [])
                NestedUtil.handle_list_insert(sub_obj, part, None)  # Refactored to use handle_list_insert
                next_part = parts[parts.index(part) + 1]
                is_next_part_digit = isinstance(next_part, str) and next_part.isdigit()
                if sub_obj[part] is None:
                    sub_obj[part] = [] if (max_depth is None or current_depth < max_depth - 1) and is_next_part_digit else {}
                sub_obj = sub_obj[part]
            else:
                sub_obj = sub_obj.setdefault(part, {})
            current_depth += 1

        last_part = parts[-1]
        if isinstance(last_part, int) and isinstance(sub_obj, list):
            NestedUtil.handle_list_insert(sub_obj, last_part, value)
        else:
            sub_obj[last_part] = value

    @staticmethod
    def dynamic_unflatten_dict(
        flat_dict: Dict[str, Any], sep: str = '_', 
        custom_logic: Union[Callable[[str], Any], None] = None, 
        max_depth: Union[int, None] = None
    ) -> Union[Dict, List]:
        """
        Converts a flat dictionary with composite keys into a nested dictionary or list.

        Args:
            flat_dict (Dict[str, Any]): The flat dictionary to unflatten.
            
            sep (str, optional): Separator used in composite keys. Defaults to '_'.
            
            custom_logic (Union[Callable[[str], Any], None], optional): Custom function to process parts of the keys. Defaults to None.
            
            max_depth (Union[int, None], optional): Maximum depth for nesting. Defaults to None.
            
        Returns:
            Union[Dict, List]: The unflattened dictionary or list.
        """
        unflattened = {}
        for composite_key, value in flat_dict.items():
            parts = composite_key.split(sep)
            if custom_logic:
                parts = [custom_logic(part) for part in parts]
            else:
                parts = [int(part) if part.isdigit() else part for part in parts]
            NestedUtil.insert(unflattened, parts, value, max_depth)

        if isinstance(unflattened, dict) and all(isinstance(k, int) for k in unflattened.keys()):
            max_index = max(unflattened.keys(), default=-1)
            return [unflattened.get(i) for i in range(max_index + 1)]
        if not unflattened:
            return {}
        return unflattened

    @staticmethod
    def unflatten_to_list(flat_dict: Dict[str, Any], sep: str = '_') -> List:
        """
        Converts a flat dictionary with string keys to a nested list structure.

        Args:
            flat_dict (Dict[str, Any]): The flat dictionary to convert.
            sep (str, optional): The separator used in the flat dictionary keys. Defaults to '_'.

        Returns:
            List: The resulting nested list structure.
        """
        result_list = []
        for flat_key, value in flat_dict.items():
            indices = [NestedUtil._convert_to_int_if_possible(p) for p in flat_key.split(sep)]
            NestedUtil._insert_with_dict_handling(result_list, indices, value)
        return result_list

    @staticmethod
    def print(nested_structure: Union[Dict, List], indent: int = 0) -> None:
        """
        Prints a nested list or dictionary with indentation to visually represent the nesting.

        Args:
            nested_structure (Union[Dict, List]): The nested list or dictionary to print.
            indent (int, optional): The initial indentation level. Defaults to 0.

        Returns:
            None: This function prints the nested structure and returns None.
        """
        if isinstance(nested_structure, list):
            NestedUtil._print_iterable(nested_structure, indent)
        elif isinstance(nested_structure, dict):
            NestedUtil._print_dict(nested_structure, indent)

    @staticmethod
    def get_flattened_keys(obj: Any, sep: str = '_', max_depth: Union[int, None] = None, 
                        dict_only: bool = False, inplace: bool = False) -> List[str]:
        if inplace:
            obj_copy = deepcopy(obj)
            NestedUtil.dynamic_flatten(obj_copy, sep=sep, max_depth=max_depth, inplace=True, dict_only=dict_only)
            return list(obj_copy.keys())
        else:
            return list(NestedUtil.dynamic_flatten(obj, sep=sep, max_depth=max_depth, dict_only=dict_only).keys())

    @staticmethod
    def flatten_list(l: List, dropna: bool = True) -> List:
        """
        Flattens a nested list into a single-level list.

        Args:
            l (List): The nested list to flatten.
            dropna (bool, optional): If True, removes None values from the flattened list. Defaults to True.

        Returns:
            List: The flattened list, with or without None values based on the dropna parameter.
        """
        flattened_list = list(NestedUtil._flatten_list_generator(l, dropna))
        return NestedUtil._dropna(flattened_list) if dropna else flattened_list

    @staticmethod
    def _insert_with_dict_handling(result_list: Union[Dict, List], 
                                indices: List[Union[int, str]], 
                                value: Any, 
                                current_depth: int = 0):
        """
        Inserts a value into a nested list at the specified indices. If the index does not exist, 
        it creates the necessary structure (list) to accommodate the value at the specified index.

        Args:
            result_list (Union[Dict, List]): The list or dictionary to insert the value into.
            indices (List[Union[int, str]]): The indices where the value should be inserted.
            value (Any): The value to insert.
            current_depth (int, optional): The current depth in the nested list or dictionary. Defaults to 0.

        Examples:
            >>> _insert_with_dict_handling([[], []], [1, 0], 'a')
            >>> _insert_with_dict_handling([['a'], []], [1, 1], 'b')
        """
        for index in indices[:-1]:
            if isinstance(result_list, list):
                if len(result_list) <= index:
                    result_list += [[]] * (index - len(result_list) + 1)
                result_list = result_list[index]
            elif isinstance(result_list, dict):
                result_list = result_list.setdefault(index, {})
            current_depth += 1
        last_index = indices[-1]
        if isinstance(result_list, list):
            if len(result_list) <= last_index:
                result_list += [None] * (last_index - len(result_list) + 1)
            result_list[last_index] = value
        else:
            result_list[last_index] = value

    @staticmethod
    def _filter_dict(dictionary: Dict[Any, Any], condition: Callable[[Any], bool]) -> Dict[Any, Any]:
        """Filters a dictionary based on a given condition.

        This static method iterates over each key-value pair in the dictionary and retains
        those pairs where the condition function returns True.

        Args:
            dictionary: A dictionary to filter.
            
            condition: A callable that takes a key-value pair tuple and returns a boolean.
                If True, the pair is included in the result.

        Returns:
            A new dictionary containing only the key-value pairs that meet the condition.

        """
        return {k: v for k, v in dictionary.items() if condition((k, v))}

    @staticmethod
    def _filter_list(lst: List[Any], condition: Callable[[Any], bool]) -> List[Any]:
        """Filters a list based on a given condition.

        Iterates over each item in the list and includes it in the result if the condition function
        returns True for that item.

        Args:
            lst: A list to filter.
            
            condition: A callable that takes an item from the list and returns a boolean.
                If True, the item is included in the result.

        Returns:
            A new list containing only the items that meet the condition.

        """
        return [item for item in lst if condition(item)]
    
    @staticmethod
    def _ensure_list_index(lst: List, index: int, default=None) -> None:
        """Ensures that a list is at least as long as a specified index.

        This method appends the default value to the list until its length is at least
        equal to the specified index + 1. This ensures that accessing the list at the
        specified index will not result in an IndexError.

        Args:
            lst: The list to be modified.
            
            index: The index the list should extend to.
            
            default: The default value to append to the list. Defaults to None.

        """
        while len(lst) <= index:
            lst.append(default)
            
    @staticmethod
    def _deep_update(original: Dict, update: Dict) -> Dict:
        """Recursively updates a dictionary with another dictionary.

        For each key-value pair in the update dictionary, this method updates the original dictionary.
        If the value corresponding to a key is itself a dictionary, the update is applied recursively.

        Args:
            original: The original dictionary to be updated.
            
            update: The dictionary with updates to be applied.

        Returns:
            The updated dictionary with the values from the update dictionary applied.
            
        """
        for key, value in update.items():
            if isinstance(value, dict) and key in original:
                original[key] = NestedUtil._deep_update(original.get(key, {}), value)
            else:
                original[key] = value
        return original
    
    @staticmethod
    def _merge_dicts(iterables: List[Dict[Any, Any]], dict_update: bool, dict_sequence: bool, sequence_separator: str) -> Dict[Any, Any]:
        """Merges a list of dictionaries into a single dictionary.

        Args:
            iterables: A list of dictionaries to be merged.
            dict_update: If True, the value of a key in a later dictionary overwrites the previous one.
            dict_sequence: If True, instead of overwriting, keys are made unique by appending a sequence number.
            sequence_separator: The separator to use when creating unique keys in case of dict_sequence.

        Returns:
            A merged dictionary containing the combined key-value pairs from all dictionaries in the list.
        """
        merged_dict = {}
        sequence_counters = defaultdict(int)
        
        for d in iterables:
            for key, value in d.items():
                if key not in merged_dict or dict_update:
                    merged_dict[key] = value
                elif dict_sequence:
                    sequence_counters[key] += 1
                    new_key = f"{key}{sequence_separator}{sequence_counters[key]}"
                    merged_dict[new_key] = value
                    
        return merged_dict

    @staticmethod
    def _merge_sequences(iterables: List[Iterable], sort_list: bool, custom_sort: Callable[[Any], Any] = None) -> List:
        """Merges a list of sequences (like lists) into a single list.

        Args:
            iterables: A list of iterables to be merged.
            sort_list: If True, the merged list will be sorted.
            custom_sort: A custom sorting function; used only if sort_list is True.

        Returns:
            A merged list containing elements from all iterables in the list.
        """
        merged_list = list(chain(*iterables))
        if sort_list:
            if custom_sort:
                return sorted(merged_list, key=custom_sort)
            
            else:
                return sorted(merged_list, key=lambda x: (isinstance(x, str), x))
        return merged_list

    @staticmethod
    def _is_homogeneous(iterables: List[Union[Dict, List, Iterable]], type_check: type) -> bool:
        """Checks if all elements in a list are of the same specified type.

        Args:
            iterables: A list of elements to check.
            type_check: The type to check against.

        Returns:
            True if all elements in the list are of the specified type; otherwise False.
        """
        return all(isinstance(it, type_check) for it in iterables)
    
    @staticmethod
    def _dynamic_flatten_generator(obj: Any, parent_key: Tuple[str, ...], sep: str = '_', 
                                   max_depth: Union[int, None] = None, current_depth: int = 0, 
                                   dict_only: bool = False) -> Generator[Tuple[str, Any], None, None]:
        """A generator to flatten a nested dictionary or list into key-value pairs.

        This method recursively traverses the nested dictionary or list and yields flattened key-value pairs.

        Args:
            obj: The nested object (dictionary or list) to flatten.
            parent_key: Tuple of parent keys leading to the current object.
            sep: Separator used between keys in the flattened output.
            max_depth: Maximum depth to flatten. None indicates no depth limit.
            current_depth: The current depth level in the nested object.
            dict_only: If True, only processes nested dictionaries, skipping other types in lists.

        Yields:
            Tuple[str, Any]: Flattened key-value pair as a tuple.
        """
        if max_depth is not None and current_depth > max_depth:
            yield sep.join(parent_key), obj
            return

        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = parent_key + (k,)
                yield from NestedUtil._dynamic_flatten_generator(v, new_key, sep, max_depth, current_depth + 1, dict_only)
        elif isinstance(obj, list) and not dict_only:
            for i, item in enumerate(obj):
                new_key = parent_key + (str(i),)
                yield from NestedUtil._dynamic_flatten_generator(item, new_key, sep, max_depth, current_depth + 1, dict_only)
        else:
            yield sep.join(parent_key), obj

    @staticmethod
    def _deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
        """Merges two dictionaries deeply.

        For each key in `dict2`, updates or adds the key-value pair to `dict1`. If values 
        for the same key are dictionaries, merge them recursively.

        Args:
            dict1: The dictionary to be updated.
            dict2: The dictionary with values to update `dict1`.

        Returns:
            The updated dictionary `dict1`.
        """
        for key in dict2:
            if key in dict1:
                if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    NestedUtil.deep_merge_dicts(dict1[key], dict2[key])
                else:
                    dict1[key] = dict2[key]
            else:
                dict1[key] = dict2[key]
        return dict1

    @staticmethod
    def _tuples_to_dict(tuples_list: List[Tuple[str, Any]]) -> Dict:
        """Converts a list of tuples into a dictionary.

        Each tuple in the list should be a key-value pair, where the key is a string
        that represents the nested keys separated by underscores.

        Args:
            tuples_list: A list of tuples where each tuple is a (key, value) pair.

        Returns:
            A dictionary created from the tuples.
        """
        result_dict = {}
        for key, value in tuples_list:
            NestedUtil.insert(result_dict, key.split('_'), value)
        return result_dict
    
    @staticmethod
    def _dynamic_flatten_in_place(obj: Any, parent_key: str = '', sep: str = '_', 
                                max_depth: Union[int, None] = None, 
                                current_depth: int = 0, dict_only: bool = False) -> None:
        """
        Helper function to flatten the object in place.

        Args:
            obj (Any): The object to flatten.
            parent_key (str, optional): The base key for the flattened dictionary. Defaults to ''.
            sep (str, optional): Separator used in keys. Defaults to '_'.
            max_depth (Union[int, None], optional): Maximum depth to flatten. Defaults to None.
            current_depth (int, optional): Current depth in recursion. Defaults to 0.
            dict_only (bool, optional): If True, flattens only dictionaries. Defaults to False.

        Returns:
            None: This function modifies the input object in place and returns None.
        """
        if isinstance(obj, dict):
            keys_to_delete = []
            items = list(obj.items())  # Create a copy of the dictionary items

            for k, v in items:
                new_key = f"{parent_key}{sep}{k}" if parent_key else k

                if isinstance(v, dict) and (max_depth is None or current_depth < max_depth):
                    NestedUtil._dynamic_flatten_in_place(v, new_key, sep, max_depth, current_depth + 1, dict_only)
                    keys_to_delete.append(k)
                    obj.update(v)
                elif not dict_only and (isinstance(v, list) or not isinstance(v, (dict, list))):
                    obj[new_key] = v
                    if parent_key:
                        keys_to_delete.append(k)

            for k in keys_to_delete:
                del obj[k]

    @staticmethod
    def _dynamic_flatten_generator(obj: Any, parent_key: Tuple[str, ...], 
                                sep: str = '_', max_depth: Union[int, None] = None, 
                                current_depth: int = 0, dict_only: bool = False
                                ) -> Generator[Tuple[str, Any], None, None]:
        """
        Generator function to dynamically flatten an object.

        Args:
            obj (Any): The object to flatten.
            parent_key (Tuple[str, ...]): Tuple of keys representing the current path in the flattened structure.
            sep (str, optional): Separator used in keys. Defaults to '_'.
            max_depth (Union[int, None], optional): Maximum depth to flatten. Defaults to None.
            current_depth (int, optional): Current depth in recursion. Defaults to 0.
            dict_only (bool, optional): If True, flattens only dictionaries. Defaults to False.

        Yields:
            Generator[Tuple[str, Any], None, None]: Yields key-value pairs of the flattened object.
        """
        if max_depth is not None and current_depth > max_depth:
            yield sep.join(parent_key), obj
            return

        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = parent_key + (k,)
                yield from NestedUtil._dynamic_flatten_generator(v, new_key, sep, 
                                                    max_depth, current_depth + 1, dict_only)
        elif isinstance(obj, list) and not dict_only:
            for i, item in enumerate(obj):
                new_key = parent_key + (str(i),)
                yield from NestedUtil._dynamic_flatten_generator(item, new_key, sep, 
                                                    max_depth, current_depth + 1, dict_only)
        else:
            yield sep.join(parent_key), obj

    @staticmethod
    def _extend_list_to_index(lst: List[Any], index: int, fill_value: Any = None) -> None:
        """
        Extends a list to a specified index with a fill value.

        Args:
            lst (List[Any]): The list to extend.
            index (int): The index to extend the list to.
            fill_value (Any, optional): The value to fill the extended part of the list with. Defaults to None.

        Returns:
            None: This function modifies the input list in place and returns None.
        """
        while len(lst) <= index:
            lst.append(fill_value)

    @staticmethod
    def _convert_to_int_if_possible(s: str) -> Union[int, str]:
        """
        Converts a string to an integer if possible; otherwise, returns the string.

        Args:
            s (str): The string to convert.

        Returns:
            Union[int, str]: The converted integer or the original string.
        """
        return int(s) if s.lstrip('-').isdigit() else s

    @staticmethod
    def _insert_with_dict_handling(result_list: Union[Dict, List], 
                                indices: List[Union[int, str]], 
                                value: Any, 
                                current_depth: int = 0):
        """
        Helper function to insert a value into a list or dictionary at a nested location 
        defined by indices.

        Args:
            result_list (Union[Dict, List]): The list or dictionary to insert into.
            indices (List[Union[int, str]]): The indices defining where to insert the value.
            value (Any): The value to insert.
            current_depth (int, optional): The current depth in the nested structure. Defaults to 0.

        Returns:
            None: This function modifies the input list or dictionary in place and returns None.
        """
        for index in indices[:-1]:
            if isinstance(result_list, list):
                NestedUtil._extend_list_to_index(result_list, index, [])
                result_list = result_list[index]
            elif isinstance(result_list, dict):
                result_list = result_list.setdefault(index, {})
            current_depth += 1
        last_index = indices[-1]
        if isinstance(result_list, list):
            NestedUtil._extend_list_to_index(result_list, last_index)
            result_list[last_index] = value
        else:
            result_list[last_index] = value
            
    @staticmethod
    def _is_iterable(obj: Any) -> bool:
        """
        Determines if the given object is iterable.

        Args:
            obj (Any): The object to be checked.

        Returns:
            bool: True if the object is iterable, False otherwise.
        """
        return isinstance(obj, ABCIterable) and not isinstance(obj, str)

    @staticmethod
    def _print_dict(nested_dict: Dict, indent: int) -> None:
        print(" " * indent + "{")
        for key, value in nested_dict.items():
            if NestedUtil._is_iterable(value):
                print(f"{' ' * (indent + 2)}{key}:")
                NestedUtil._print_iterable(value, indent + 4)
            else:
                print(f"{' ' * (indent + 2)}{key}: {value}")
        print(" " * indent + "}")

    @staticmethod
    def _print_iterable(iterable: Iterable, indent: int) -> None:
        for item in iterable:
            if isinstance(item, list):
                print(" " * indent + "[")
                NestedUtil._print_iterable(item, indent + 2)
                print(" " * indent + "]")
            elif isinstance(item, dict):
                NestedUtil._print_dict(item, indent)
            else:
                print(" " * indent + str(item))
                
    @staticmethod
    def _dropna(l: List) -> List:
        """
        Removes None values from a list.

        Args:
            l (List): The list to remove None values from.

        Returns:
            List: A new list with None values removed.
        """
        return [item for item in l if item is not None]

    @staticmethod
    def _flatten_list_generator(l: List, dropna: bool = True) -> Generator[Any, None, None]:
        """
        Generator to flatten a nested list.

        Args:
            l (List): The nested list to flatten.
            dropna (bool, optional): If True, removes None values during the flattening process. Defaults to True.

        Yields:
            Generator[Any, None, None]: Yields elements of the flattened list.
        """
        for i in l:
            if isinstance(i, list):
                yield from NestedUtil._flatten_list_generator(i, dropna)
            else:
                yield i

    @staticmethod
    def _get_target_container(nested_list: Union[List, Dict], indices: List[Union[int, str]]) -> Union[List, Dict]:
        current_element = nested_list
        for index in indices:
            if isinstance(current_element, list):
                if isinstance(index, int) and 0 <= index < len(current_element):
                    current_element = current_element[index]
                else:
                    raise IndexError("List index out of range")
            elif isinstance(current_element, dict):
                if index in current_element:
                    current_element = current_element[index]
                else:
                    raise KeyError("Key not found in dictionary")
            else:
                raise TypeError("Current element is neither a list nor a dictionary")
        return current_element
    