# Nested Data Structure - `ln_nested`

```
import lionagi.libs.ln_nested as nested
```

## `nset`

```python
nset(nested_structure: dict | list, indices: list[int | str], value: Any) -> None
```

Sets a value within a nested structure at the specified path defined by indices.

### Parameters

- `nested_structure` (dict | list): The nested structure where the value will be set.
- `indices` (list[int | str]): The path of indices leading to where the value should be set.
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

## `nget`

```python
nget(nested_structure: dict | list, indices: list[int | str], default: Any | None = None) -> Any
```

Retrieves a value from a nested list or dictionary structure, with an option to specify a default value.

### Parameters

- `nested_structure` (dict | list): The nested list or dictionary structure.
- `indices` (list[int | str]): A list of indices to navigate through the structure.
- `default` (Any | None): The default value to return if the target cannot be reached. If `default` is not provided and the target cannot be reached, a `LookupError` is raised.

### Returns

- `Any`: The value at the target location, the default value if provided and the target cannot be reached, or raises an error.

### Raises

- `LookupError`: If the target location cannot be reached or does not exist and no default value is provided.

### Examples

```python
data = {'a': {'b': [10, 20]}}
assert nget(data, ['a', 'b', 1]) == 20

nget(data, ['a', 'b', 2])
# Traceback (most recent call last):
#   ...
# LookupError: Target not found and no default value provided.
```

## `nmerge`

```python
nmerge(
    nested_structure: list[dict | list],
    /,
    *,
    overwrite: bool = False,
    dict_sequence: bool = False,
    sequence_separator: str = "_",
    sort_list: bool = False,
    custom_sort: Callable[[Any], Any] | None = None,
) -> dict | list
```

Merges multiple dictionaries, lists, or sequences into a unified structure.

### Parameters

- `nested_structure`: A list containing dictionaries, lists, or other iterable objects to merge.
- `dict_update`: Determines whether to overwrite existing keys in dictionaries with those from subsequent dictionaries. Defaults to False, preserving original keys.
- `dict_sequence`: Enables unique key generation for duplicate keys by appending a sequence number, using `sequence_separator` as the delimiter. Applicable only if `dict_update` is False.
- `sequence_separator`: The separator used when generating unique keys for duplicate dictionary keys.
- `sort_list`: When True, sort the resulting list after merging. It does not affect dictionaries.
- `custom_sort`: An optional Callable that defines custom sorting logic for the merged list.

### Returns

- A merged dictionary or list, depending on the types present in `iterables`.

### Raises

- `TypeError`: If `iterables` contains objects of incompatible types that cannot be merged.

### Examples

```python
nmerge([{'a': 1}, {'b': 2}], overwrite=True)
# {'a': 1, 'b': 2}

nmerge([[1, 2], [3, 4]], sort_list=True)
# [1, 2, 3, 4]
```

## `flatten`

```python
flatten(
    nested_structure: Any,
    /,
    *,
    parent_key: str = "",
    sep: str = "_",
    max_depth: int | None = None,
    inplace: bool = False,
    dict_only: bool = False,
) -> dict | None
```

Flattens a nested structure into a dictionary with composite keys.

### Parameters

- `nested_structure`: The nested dictionary or list to flatten.
- `parent_key`: A prefix for all keys in the flattened dictionary, useful for nested calls.
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
flatten(nested_dict)
# {'a_b_c': 1}

nested_list = [{'a': 1}, {'b': 2}]
flatten(nested_list)
# {'0_a': 1, '1_b': 2}
```


## `unflatten`

```python
unflatten(
    flat_dict: dict[str, Any],
    /,
    *,
    sep: str = "_",
    custom_logic: Callable[[str], Any] | None = None,
    max_depth: int | None = None,
) -> dict | list
```

Reconstructs a nested structure from a flat dictionary with composite keys.

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
unflatten(flat_dict)
# {'a': {'b': {'c': 1}}}

flat_dict = {'0_a': 1, '1_b': 2}
unflatten(flat_dict)
# [{'a': 1}, {'b': 2}]
```

## `nfilter`

```python
nfilter(
    nested_structure: dict | list,
    /,
    condition: Callable[[Any], bool]
) -> dict | list
```

Filters items in a dictionary or list based on a specified condition.

### Parameters

- `nested_structure` (dict | list): The collection to filter, either a dictionary or a list.
- `condition` (Callable[[Any], bool]): A function that evaluates each input (or key-value pair in the case of dictionaries) against a condition. Returns True to include the input in the result, False otherwise.

### Returns

- dict | list: A new collection of the same type as `collection`, containing only items that meet the condition.

### Raises

- `TypeError`: Raised if `collection` is not a dictionary or a list.

### Examples

```python
nfilter({'a': 1, 'b': 2, 'c': 3}, lambda x: x[1] > 1)
# {'b': 2, 'c': 3}

nfilter([1, 2, 3, 4], lambda x: x % 2 == 0)
# [2, 4]
```

## `ninsert`

```python
ninsert(
    nested_structure: dict | list,
    /,
    indices: list[str | int],
    value: Any,
    *,
    sep: str = "_",
    max_depth: int | None = None,
    current_depth: int = 0,
) -> None
```

Inserts a value into a nested structure at a specified path.

### Parameters

- `nested_structure` (dict | list): The nested structure to modify.
- `indices` (list[str | int]): The sequence of keys (str for dicts) or indices (int for lists) defining the path to the insertion point.
- `value` (Any): The value to insert at the specified location within `subject`.
- `sep` (str): A separator used when concatenating indices to form composite keys in case of ambiguity. Defaults to '_'.
- `max_depth` (int | None): Limits the depth of insertion. If `None`, no limit is applied.
- `current_depth` (int): Internal use only; tracks the current depth during recursive calls.

### Examples

```python
subject = {'a': {'b': [1, 2]}}
ninsert(subject, ['a', 'b', 2], 3)
assert subject == {'a': {'b': [1, 2, 3]}}

subject = []
ninsert(subject, [0, 'a'], 1)
assert subject == [{'a': 1}]
```

## `get_flattened_keys`

```python
get_flattened_keys(
    nested_structure: Any,
    /,
    *,
    sep: str = "_",
    max_depth: int | None = None,
    dict_only: bool = False,
    inplace: bool = False,
) -> list[str]
```

Retrieves keys from a nested structure after flattening.

### Parameters

- `nested_structure`: The nested dictionary or list to process.
- `sep`: The separator used between nested keys in the flattened keys. Defaults to '_'.
- `max_depth`: The maximum depth to flatten. If None, flattens the structure completely.
- `dict_only`: If True, only processes nested dictionaries, leaving lists as values.
- `inplace`: If True, flattens `nested_structure` in place, modifying the original object.

### Returns

- A list of strings representing the keys in the flattened structure.

### Raises

- `ValueError`: If `inplace` is True but `nested_structure` is not a dictionary.

### Examples

```python
nested_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
keys = get_flattened_keys(nested_dict)
assert keys == ['a', 'b_c', 'b_d_e']

nested_list = [{'a': 1}, {'b': 2}]
keys = get_flattened_keys(nested_list)
assert keys == ['0_a', '1_b']
```