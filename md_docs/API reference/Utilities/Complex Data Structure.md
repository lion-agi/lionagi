

# Nested Utility Functions API Reference

This document outlines the API for a set of utility functions designed to manipulate and interact with nested data structures, such as dictionaries and lists. These functions facilitate deep manipulation of nested structures, allowing for setting, getting, and merging data with ease.

## nset

Sets a value within a nested structure at a specified path defined by indices.

### Usage

```python
nset(nested_structure, indices, value)
```

### Parameters

- `nested_structure` (Dict | List): The nested structure where the value will be set.
- `indices` (List[int | str]): The path of indices leading to where the value should be set.
- `value` (Any): The value to set at the specified location in the nested structure.

### Raises

- `ValueError`: Raised if the indices list is empty.
- `TypeError`: Raised if the target container is not a list or dictionary, or if the index type is incorrect.

### Examples

```python
data = {'a': {'b': [10, 20]}}
nset(data, ['a', 'b', 1], 99)
assert data == {'a': {'b': [10, 99]}}

data = [0, [1, 2], 3]
nset(data, [1, 1], 99)
assert data == [0, [1, 99], 3]
```

## nget

Retrieves a value from a nested structure, with an option to specify a default value.

### Usage

```python
result = nget(nested_structure, indices, default=None)
```

### Parameters

- `nested_structure` (Dict | List): The nested structure to search.
- `indices` (List[int | str]): A list of indices to navigate through the structure.
- `default` (Optional[Any]): The default value to return if the target cannot be reached.

### Returns

- The value at the target location, the default value if provided and the target cannot be reached, or raises an error.

### Raises

- `LookupError`: If the target location cannot be reached or does not exist and no default value is provided.

### Examples

```python
data = {'a': {'b': [10, 20]}}
assert nget(data, ['a', 'b', 1]) == 20

try:
    nget(data, ['a', 'b', 2])
except LookupError:
    pass  # Expected behavior since the target does not exist and no default is provided.
```

The functions `nset` and `nget` offer fundamental operations for interacting with nested structures, providing robust mechanisms for setting and retrieving data within complex nested data types. Stay tuned for Part 2, where we will explore more advanced functionalities for merging and flattening nested structures.



## nmerge

Merges multiple dictionaries, lists, or sequences into a unified structure.

### Usage

```python
result = nmerge(nested_structure, dict_update=False, dict_sequence=False, sequence_separator="_", sort_list=False, custom_sort=None)
```

### Parameters

- `nested_structure`: A list containing dictionaries, lists, or other iterable objects to merge.
- `dict_update`: Determines whether to overwrite existing keys in dictionaries. Defaults to False.
- `dict_sequence`: Enables unique key generation for duplicate keys by appending a sequence number, using `sequence_separator` as the delimiter. Applicable only if `dict_update` is False.
- `sequence_separator`: The separator used when generating unique keys for duplicate dictionary keys.
- `sort_list`: When true, sort the resulting list after merging. Does not affect dictionaries.
- `custom_sort`: An optional Callable that defines custom sorting logic for the merged list.

### Returns

- A merged dictionary or list, depending on the types present in `nested_structure`.

### Raises

- `TypeError`: If `nested_structure` contains objects of incompatible types that cannot be merged.

### Examples

```python
merged_dict = nmerge([{'a': 1}, {'b': 2}], dict_update=True)
assert merged_dict == {'a': 1, 'b': 2}

merged_list = nmerge([[1, 2], [3, 4]], sort_list=True)
assert merged_list == [1, 2, 3, 4]
```

## flatten

Flattens a nested structure into a dictionary with composite keys.

### Usage

```python
flat_dict = flatten(nested_structure, parent_key="", sep="_", max_depth=None, inplace=False, dict_only=False)
```

### Parameters

- `nested_structure`: The nested dictionary or list to flatten.
- `parent_key`: A prefix for all keys in the flattened dictionary.
- `sep`: The separator used between levels in composite keys.
- `max_depth`: The maximum depth to flatten; if None, flattens completely.
- `inplace`: If True, modifies `nested_structure` in place; otherwise, returns a new dictionary.
- `dict_only`: If True, only flattens nested dictionaries, leaving lists intact.

### Returns

- A flattened dictionary, or None if `inplace` is True.

### Raises

- `ValueError`: If `inplace` is True but `nested_structure` is not a dictionary.

### Examples

```python
nested_dict = {'a': {'b': {'c': 1}}}
flat_dict = flatten(nested_dict)
assert flat_dict == {'a_b_c': 1}

nested_list = [{'a': 1}, {'b': 2}]
flat_dict = flatten(nested_list, dict_only=True)
assert flat_dict == {'0_a': 1, '1_b': 2}
```

Stay tuned for Part 3, where we will cover the functions for unflattening nested structures and filtering elements based on conditions.


## unflatten

Reconstructs a nested structure from a flat dictionary with composite keys.

### Usage

```python
nested_structure = unflatten(flat_dict, sep="_", custom_logic=None, max_depth=None)
```

### Parameters

- `flat_dict`: A flat dictionary with composite keys to unflatten.
- `sep`: The separator used in composite keys, indicating nested levels.
- `custom_logic`: An optional function to process each part of the composite keys.
- `max_depth`: The maximum depth for nesting during reconstruction.

### Returns

- The reconstructed nested dictionary or list.

### Examples

```python
flat_dict = {'a_b_c': 1}
nested_structure = unflatten(flat_dict)
assert nested_structure == {'a': {'b': {'c': 1}}}

flat_dict = {'0_a': 1, '1_b': 2}
nested_structure = unflatten(flat_dict)
assert nested_structure == [{'a': 1}, {'b': 2}]
```

## nfilter

Filters items in a dictionary or list based on a specified condition.

### Usage

```python
filtered_structure = nfilter(nested_structure, condition)
```

### Parameters

- `nested_structure` (Dict | List): The collection to filter, either a dictionary or a list.
- `condition` (Callable[[Any], bool]): A function that evaluates each item (or key-value pair in the case of dictionaries) against a condition.

### Returns

- A new collection of the same type as `nested_structure`, containing only items that meet the condition.

### Raises

- `TypeError`: Raised if `nested_structure` is not a dictionary or a list.

### Examples

```python
filtered_dict = nfilter({'a': 1, 'b': 2, 'c': 3}, lambda x: x[1] > 1)
assert filtered_dict == {'b': 2, 'c': 3}

filtered_list = nfilter([1, 2, 3, 4], lambda x: x % 2 == 0)
assert filtered_list == [2, 4]
```

The functions `unflatten` and `nfilter` complete the suite of nested utility functions designed to manipulate and interact with complex nested data structures. These utilities offer powerful capabilities for data manipulation, enabling developers to easily navigate, modify, and manage deeply nested data.
