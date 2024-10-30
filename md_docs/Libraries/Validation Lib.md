# Field Validation API Reference

This module provides functions for validating and fixing field values based on their data types.

## Functions

### `check_dict_field(x, keys: list[str] | dict, fix_=True, **kwargs)`

Checks if the given value is a valid dictionary field.

**Args:**
- `x`: The value to check.
- `keys` (list[str] | dict): The expected keys or structure of the dictionary field.
- `fix_` (bool): Flag indicating whether to attempt fixing the value if it's invalid (default: True).
- `**kwargs`: Additional keyword arguments for fixing the value.

**Returns:**
- The original value if it's valid, or the fixed value if `fix_` is True.

**Raises:**
- `ValueError`: If the value is not a valid dictionary field and cannot be fixed.

### `check_action_field(x, fix_=True, **kwargs)`

Checks if the given value is a valid action field.

**Args:**
- `x`: The value to check.
- `fix_` (bool): Flag indicating whether to attempt fixing the value if it's invalid (default: True).
- `**kwargs`: Additional keyword arguments for fixing the value.

**Returns:**
- The original value if it's valid, or the fixed value if `fix_` is True.

**Raises:**
- `ValueError`: If the value is not a valid action field and cannot be fixed.

### `check_number_field(x, fix_=True, **kwargs)`

Checks if the given value is a valid numeric field.

**Args:**
- `x`: The value to check.
- `fix_` (bool): Flag indicating whether to attempt fixing the value if it's invalid (default: True).
- `**kwargs`: Additional keyword arguments for fixing the value.

**Returns:**
- The original value if it's valid, or the fixed value if `fix_` is True.

**Raises:**
- `ValueError`: If the value is not a valid numeric field and cannot be fixed.

### `check_bool_field(x, fix_=True)`

Checks if the given value is a valid boolean field.

**Args:**
- `x`: The value to check.
- `fix_` (bool): Flag indicating whether to attempt fixing the value if it's invalid (default: True).

**Returns:**
- The original value if it's valid, or the fixed value if `fix_` is True.

**Raises:**
- `ValueError`: If the value is not a valid boolean field and cannot be fixed.

### `check_str_field(x, *args, fix_=True, **kwargs)`

Checks if the given value is a valid string field.

**Args:**
- `x`: The value to check.
- `*args`: Additional positional arguments for fixing the value.
- `fix_` (bool): Flag indicating whether to attempt fixing the value if it's invalid (default: True).
- `**kwargs`: Additional keyword arguments for fixing the value.

**Returns:**
- The original value if it's valid, or the fixed value if `fix_` is True.

**Raises:**
- `ValueError`: If the value is not a valid string field and cannot be fixed.

### `check_enum_field(x, choices, fix_=True, **kwargs)`

Checks if the given value is a valid enum field.

**Args:**
- `x`: The value to check.
- `choices`: The list of valid choices for the enum field.
- `fix_` (bool): Flag indicating whether to attempt fixing the value if it's invalid (default: True).
- `**kwargs`: Additional keyword arguments for fixing the value.

**Returns:**
- The original value if it's valid, or the fixed value if `fix_` is True.

**Raises:**
- `ValueError`: If the value is not a valid enum field and cannot be fixed.

## Private Helper Functions

- `_has_action_keys(dict_)`: Checks if a dictionary has the required keys for an action field.
- `_fix_action_field(x, discard_=True)`: Attempts to fix an invalid action field value.
- `_fix_number_field(x, *args, **kwargs)`: Attempts to fix an invalid numeric field value.
- `_fix_bool_field(x)`: Attempts to fix an invalid boolean field value.
- `_fix_str_field(x)`: Attempts to fix an invalid string field value.
- `_fix_enum_field(x, choices, **kwargs)`: Attempts to fix an invalid enum field value.

## Constants

- `validation_funcs`: A dictionary mapping data types to their corresponding validation functions.
  - `"number"`: `check_number_field`
  - `"bool"`: `check_bool_field`
  - `"str"`: `check_str_field`
  - `"enum"`: `check_enum_field`
  - `"action"`: `check_action_field`
  - `"dict"`: `check_dict_field`

## Imported Modules

- `from .ln_convert import to_str, is_same_dtype, to_list, to_dict, to_num, strip_lower`
- `from .ln_parse import StringMatch, ParseUtil`
