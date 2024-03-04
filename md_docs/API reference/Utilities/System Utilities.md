

# SysUtil Class API Reference

This document provides a comprehensive overview of the `SysUtil` class, which offers utility functions for system-level operations and data manipulation.

## change_dict_key

Changes a key in a dictionary if the old key exists.

### Usage

```python
SysUtil.change_dict_key(dict_, old_key, new_key)
```

### Parameters

- `dict_`: The dictionary to modify.
- `old_key`: The key to be changed.
- `new_key`: The new key to replace `old_key`.

## get_timestamp

Returns a timestamp string with optional custom separators for ':' and '.'.

### Usage

```python
timestamp = SysUtil.get_timestamp(sep="_")
```

### Parameters

- `separator`: Custom separator to replace ':' and '.' in the timestamp. Defaults to "_".

### Returns

- A string representing the current timestamp.

## is_schema

Validates if the given dictionary matches the expected schema types.

### Usage

```python
is_valid = SysUtil.is_schema(dict_, schema)
```

### Parameters

- `dict_`: The dictionary to validate.
- `schema`: A dictionary where keys match those in `dict_` and values are the expected types.

### Returns

- `True` if `dict_` matches the schema, `False` otherwise.

## create_copy

Creates deep copies of the input, either as a single copy or a list of copies.

### Usage

```python
copy_or_copies = SysUtil.create_copy(input_, num=1)
```

### Parameters

- `input_`: The object to copy.
- `num`: The number of copies to create. Defaults to 1.

### Returns

- A single copy or a list of copies of `input_`.

## create_id

Generates a unique identifier based on the current time and random bytes.

### Usage

```python
unique_id = SysUtil.create_id(n=32)
```

### Parameters

- `n`: The length of the identifier. Defaults to 32.

### Returns

- A string representing a unique identifier.

## get_bins

Organizes indices of strings into bins based on a cumulative upper limit.

### Usage

```python
bins = SysUtil.get_bins(input_, upper=2000)
```

### Parameters

- `input_`: A list of strings to be organized into bins.
- `upper`: The cumulative upper limit for each bin. Defaults to 2000.

### Returns

- A list of lists, where each inner list contains indices of strings that cumulatively do not exceed `upper`.

The `SysUtil` class provides essential functionalities for working with data structures, generating unique identifiers, and manipulating datetime objects and strings, emphasizing efficiency and reliability in system-level operations and data handling.
