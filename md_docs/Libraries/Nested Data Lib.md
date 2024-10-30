
This module provides utility functions for working with nested data structures, including dictionaries and lists. It offers functionality for setting and getting values, merging, flattening, unflattening, filtering, and inserting elements in nested structures.
## Functions:

### `nset`

^878481

`(nested_structure: dict | list, indices: list[int | str], value: Any) -> None`

Sets a value within a nested structure at the specified path defined by indices.

Parameters:
- `nested_structure` (dict | list): The nested structure where the value will be set.
- `indices` (list[int | str]): The path of indices leading to where the value should be set.
- `value` (Any): The value to set at the specified location in the nested structure.

Raises:
- `ValueError`: Raised if the indices list is empty.
- `TypeError`: Raised if the target container is not a list or dictionary, or if the index type is incorrect.

### `nget`
`(nested_structure: dict | list, indices: list[int | str], default: Any | None = None) -> Any`

Retrieves a value from a nested list or dictionary structure, with an option to specify a default value.

Parameters:
- `nested_structure` (dict | list): The nested list or dictionary structure.
- `indices` (list[int | str]): A list of indices to navigate through the structure.
- `default` (Any | None): The default value to return if the target cannot be reached. If `default` is not provided and the target cannot be reached, a `LookupError` is raised.

Returns:
Any: The value at the target location, the default value if provided and the target cannot be reached, or raises an error.

Raises:
- `LookupError`: If the target location cannot be reached or does not exist and no default value is provided.

### `nmerge`
`(nested_structure: list[dict | list], /, *, overwrite: bool = False, dict_sequence: bool = False, sequence_separator: str = "_", sort_list: bool = False, custom_sort: Callable[[Any], Any] | None = None) -> dict | list`

Merges multiple dictionaries, lists, or sequences into a unified structure.

Parameters:
- `nested_structure` (list[dict | list]): A list containing dictionaries, lists, or other iterable objects to merge.
- `overwrite` (bool): Determines whether to overwrite existing keys in dictionaries with those from subsequent dictionaries. Defaults to False, preserving original keys.
- `dict_sequence` (bool): Enables unique key generation for duplicate keys by appending a sequence number, using `sequence_separator` as the delimiter. Applicable only if `overwrite` is False.
- `sequence_separator` (str): The separator used when generating unique keys for duplicate dictionary keys.
- `sort_list` (bool): When True, sort the resulting list after merging. It does not affect dictionaries.
- `custom_sort` (Callable[[Any], Any] | None): An optional callable that defines custom sorting logic for the merged list.

Returns:
dict | list: A merged dictionary or list, depending on the types present in `nested_structure`.

Raises:
- `TypeError`: If `nested_structure` contains objects of incompatible types that cannot be merged.

### `flatten`

^3073e9

`(nested_structure: Any, /, *, parent_key: str = "", sep: str = "_", max_depth: int | None = None, inplace: bool = False, dict_only: bool = False) -> dict | None`

Flattens a nested structure into a dictionary with composite keys.

Parameters:
- `nested_structure` (Any): The nested dictionary or list to flatten.
- `parent_key` (str): A prefix for all keys in the flattened dictionary, useful for nested calls.
- `sep` (str): The separator used between levels in composite keys.
- `max_depth` (int | None): The maximum depth to flatten; if None, flattens completely.
- `inplace` (bool): If True, modifies `nested_structure` in place; otherwise, returns a new dictionary.
- `dict_only` (bool): If True, only flattens nested dictionaries, leaving lists intact.

Returns:
dict | None: A flattened dictionary, or None if `inplace` is True.

Raises:
- `ValueError`: If `inplace` is True but `nested_structure` is not a dictionary.

### `unflatten`
`(flat_dict: dict[str, Any], /, *, sep: str = "_", custom_logic: Callable[[str], Any] | None = None, max_depth: int | None = None) -> dict | list`

Reconstructs a nested structure from a flat dictionary with composite keys.

Parameters:
- `flat_dict` (dict[str, Any]): A flat dictionary with composite keys to unflatten.
- `sep` (str): The separator used in composite keys, indicating nested levels.
- `custom_logic` (Callable[[str], Any] | None): An optional function to process each part of the composite keys.
- `max_depth` (int | None): The maximum depth for nesting during reconstruction.

Returns:
dict | list: The reconstructed nested dictionary or list.

### `nfilter`
`(nested_structure: dict | list, /, condition: Callable[[Any], bool]) -> dict | list`

Filters items in a dictionary or list based on a specified condition.

Parameters:
- `nested_structure` (dict | list): The collection to filter, either a dictionary or a list.
- `condition` (Callable[[Any], bool]): A function that evaluates each input (or key-value pair in the case of dictionaries) against a condition. Returns True to include the input in the result, False otherwise.

Returns:
dict | list: A new collection of the same type as `nested_structure`, containing only items that meet the condition.

Raises:
- `TypeError`: Raised if `nested_structure` is not a dictionary or a list.

### `ninsert`

^3eb329

`(nested_structure: dict | list, /, indices: list[str | int], value: Any, *, sep: str = "_", max_depth: int | None = None, current_depth: int = 0) -> None`

Inserts a value into a nested structure at a specified path.

Parameters:
- `nested_structure` (dict | list): The nested structure to modify.
- `indices` (list[str | int]): The sequence of keys (str for dicts) or indices (int for lists) defining the path to the insertion point.
- `value` (Any): The value to insert at the specified location within `nested_structure`.
- `sep` (str): A separator used when concatenating indices to form composite keys in case of ambiguity. Defaults to '_'.
- `max_depth` (int | None): Limits the depth of insertion. If `None`, no limit is applied.
- `current_depth` (int): Internal use only; tracks the current depth during recursive calls.

### `get_flattened_keys`
`(nested_structure: Any, /, *, sep: str = "_", max_depth: int | None = None, dict_only: bool = False, inplace: bool = False) -> list[str]`

Retrieves keys from a nested structure after flattening.

Parameters:
- `nested_structure` (Any): The nested dictionary or list to process.
- `sep` (str): The separator used between nested keys in the flattened keys. Defaults to '_'.
- `max_depth` (int | None): The maximum depth to flatten. If None, flattens the structure completely.
- `dict_only` (bool): If True, only processes nested dictionaries, leaving lists as values.
- `inplace` (bool): If True, flattens `nested_structure` in place, modifying the original object.

Returns:
list[str]: A list of strings representing the keys in the flattened structure.

Raises:
- `ValueError`: If `inplace` is True but `nested_structure` is not a dictionary.

## Usage Example

```python
from lionagi.libs.ln_nested import nset, nget, nmerge, flatten, unflatten, nfilter, ninsert, get_flattened_keys

# Set a value in a nested structure
data = {'a': {'b': [10, 20]}}
nset(data, ['a', 'b', 1], 99)
assert data == {'a': {'b': [10, 99]}}

# Get a value from a nested structure
nested_dict = {'a': {'b': {'c': 1}}}
value = nget(nested_dict, ['a', 'b', 'c'])
assert value == 1

# Merge nested structures
merged_dict = nmerge([{'a': 1}, {'b': 2}], overwrite=True)
assert merged_dict == {'a': 1, 'b': 2}

# Flatten a nested structure
nested_dict = {'a': {'b': {'c': 1}}}
flattened_dict = flatten(nested_dict)
assert flattened_dict == {'a_b_c': 1}

# Unflatten a flattened dictionary
flat_dict = {'a_b_c': 1}
unflattened_dict = unflatten(flat_dict)
assert unflattened_dict == {'a': {'b': {'c': 1}}}

# Filter a nested structure
filtered_dict = nfilter({'a': 1, 'b': 2, 'c': 3}, lambda x: x[1] > 1)
assert filtered_dict == {'b': 2, 'c': 3}

# Insert a value into a nested structure
data = {'a': {'b': [1, 2]}}
ninsert(data, ['a', 'b', 2], 3)
assert data == {'a': {'b': [1, 2, 3]}}

# Get flattened keys from a nested structure
nested_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
keys = get_flattened_keys(nested_dict)
assert keys == ['a', 'b_c', 'b_d_e']
```

In this example, we demonstrate the usage of various functions provided by the `ln_nested` module for manipulating nested data structures. We set and get values in nested structures, merge multiple structures, flatten and unflatten dictionaries, filter elements based on conditions, insert values at specific paths, and retrieve flattened keys from a nested structure.

These functions provide a convenient way to work with complex nested data structures in a concise and expressive manner.
