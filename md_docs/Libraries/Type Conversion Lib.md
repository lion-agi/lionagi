# Convert Utility API Reference

This module provides utility functions for converting and manipulating various data types and structures.

### `to_list`
`(input_, /, *, flatten: bool = True, dropna: bool = True) -> list[Any]`

Converts the input object to a list. This function is capable of handling various input types, utilizing single dispatch to specialize for different types such as list, tuple, and set. The default implementation handles general iterables, excluding strings, bytes, bytearrays, and dictionaries, by attempting to convert them to a list, optionally flattening and dropping None values based on the provided arguments.

Parameters:
- `input_` (Any): The input object to convert to a list.
- `flatten` (bool): If True, and the input is a nested list, the function will attempt to flatten it. Default is True.
- `dropna` (bool): If True, None values will be removed from the resulting list. Default is True.

Returns:
`list[Any]`: A list representation of the input, with modifications based on `flatten` and `dropna`.

Raises:
- `ValueError`: If the input type is unsupported or cannot be converted to a list.

Note: This function uses `@singledispatch` to handle different input types via overloading. The default behavior for dictionaries is to wrap them in a list without flattening. For specific behaviors with lists, tuples, sets, and other types, see the registered implementations.

### `to_dict`

^479673

`(input_, /, *args, **kwargs) -> dict[Any, Any]`

Converts the input object to a dictionary. This base function raises a ValueError for unsupported types. The function is overloaded to handle specific input types such as dict, str, pandas.Series, pandas.DataFrame, and Pydantic's BaseModel, utilizing the single dispatch mechanism for type-specific conversions.

Parameters:
- `input_` (Any): The input object to convert to a dictionary.
- `*args`: Variable length argument list for additional options in type-specific handlers.
- `**kwargs`: Arbitrary keyword arguments for additional options in type-specific handlers.

Returns:
`dict[Any, Any]`: A dictionary representation of the input object.

Raises:
- `ValueError`: If the input type is not supported or cannot be converted to a dictionary.

Note: For specific behaviors with dict, str, pandas.Series, pandas.DataFrame, and BaseModel, see the registered implementations.

### `to_str`
`(input_) -> str`

Converts the input object to a string. This function utilizes single dispatch to handle specific input types such as dict, str, list, pandas.Series, and pandas.DataFrame, providing type-specific conversions to string format.

Parameters:
- `input_` (Any): The input object to convert to a string.

Returns:
str: A string representation of the input object.

Note: The base implementation simply uses the str() function for conversion. For detailed behaviors with dict, str, list, pandas.Series, and pandas.DataFrame, refer to the registered implementations.

### `to_df`
`(input_: Any, /, *, how: str = "all", drop_kwargs: dict[str, Any] | None = None, reset_index: bool = True, **kwargs: Any) -> pd.DataFrame`

Converts various input types to a pandas DataFrame, with options for handling missing data and resetting the index. This function is overloaded to handle specific data structures such as lists of dictionaries, lists of pandas objects (DataFrames or Series), and more.

Parameters:
- `input_` (`Any`): The input data to convert into a DataFrame. Accepts a wide range of types thanks to overloads.
- `how` (`str`): Specifies how missing values are dropped. Passed directly to DataFrame.dropna().
- `drop_kwargs` (`dict[str, Any] | None`): Additional keyword arguments for DataFrame.dropna().
- `reset_index` (`bool`): If True, the DataFrame index will be reset, removing the index labels.
- `**kwargs`: Additional keyword arguments passed to the pandas DataFrame constructor.

Returns:
`pd.DataFrame`: A pandas DataFrame constructed from the input data.

Raises:
- `ValueError`: If there is an error during the conversion process.

Note: This function is overloaded to provide specialized behavior for different input types, enhancing its flexibility.

### `to_num`
`(input_: Any, /, *, upper_bound: int | float | None = None, lower_bound: int | float | None = None, num_type: Type[int | float] = int, precision: int | None = None) -> int | float`

Converts the input to a numeric value of specified type, with optional bounds and precision.

Parameters:
- `input_` (Any): The input value to convert. Can be of any type that `to_str` can handle.
- `upper_bound` (float | None): The upper bound for the numeric value. If specified, values above this bound will raise an error.
- `lower_bound` (float | None): The lower bound for the numeric value. If specified, values below this bound will raise an error.
- `num_type` (Type[int | float]): The numeric type to convert to. Can be `int` or `float`.
- `precision` (int | None): The number of decimal places for the result. Applies only to `float` type.

Returns:
`int | float`: The converted numeric value, adhering to specified type and precision.

Raises:
- `ValueError`: If the input cannot be converted to a number, or if it violates the specified bounds.

### `to_readable_dict`
`(input_: Any | list[Any]) -> str | list[Any]`

Converts a given input to a readable dictionary format, either as a string or a list of dictionaries.

Parameters:
- `input_` (`Any | list[Any]`): The input to convert to a readable dictionary format.

Returns:
`str | list[str]`: The readable dictionary format of the input.

### `is_same_dtype`
`(input_: list | dict, dtype: Type | None = None, return_dtype=False) -> bool`

Checks if all elements in a list or dictionary values are of the same data type.

Parameters:
- `input_` (list | dict): The input list or dictionary to check.
- `dtype` (Type | None): The data type to check against. If None, uses the type of the first element.

Returns:
`bool`: True if all elements are of the same type (or if the input is empty), False otherwise.

### `xml_to_dict`
`(root) -> dict[str, Any]`

Converts an XML element to a dictionary.

Parameters:
- `root` (`xml.etree.ElementTree.Element`): The root element of the XML tree.

Returns:
`dict[str, Any]`: A dictionary representation of the XML tree.

### `strip_lower(input_: Any) -> str`

Converts the input to a lowercase string with leading and trailing whitespace removed.

Parameters:
- `input_` (Any): The input value to convert and process.

Returns:
`str`: The processed string.

Raises:
- `ValueError`: If the input cannot be converted to a string.

### `is_structure_homogeneous`
`(structure: Any, return_structure_type: bool = False) -> bool | tuple[bool, type | None]`

Checks if a nested structure is homogeneous, meaning it doesn't contain a mix of lists and dictionaries.

Parameters:
- `structure` (Any): The nested structure to check.
- `return_structure_type` (bool): Flag to indicate whether to return the type of homogeneous structure.

Returns:
`bool | tuple[bool, type | None]`: If `return_structure_type` is False, returns a boolean indicating whether the structure is homogeneous. If `return_structure_type` is True, returns a tuple containing a boolean indicating whether the structure is homogeneous, and the type of the homogeneous structure if it is homogeneous (either list | dict, or None).

### `is_homogeneous`

^6aef9f

`(iterables: list[Any] | dict[Any, Any], type_check: type) -> bool`

Checks if all elements in a list or all values in a dictionary are of the same specified type.

Parameters:
- `iterables` (`list[Any] | dict[Any, Any]`): The input list or dictionary to check.
- `type_check` (`type`): The type to check against.

Returns:
`bool`: True if all elements or values are of the specified type, False otherwise.

## Usage Examples

```python
from lionagi.libs.ln_convert import to_list, to_dict, to_str, to_df, to_num, to_readable_dict, is_same_dtype, xml_to_dict, strip_lower, is_structure_homogeneous, is_homogeneous

# Convert input to list
result = to_list([1, 2, 3, [4, 5]], flatten=True)
print(result)  # Output: [1, 2, 3, 4, 5]

# Convert input to dictionary
result = to_dict('{"name": "John", "age": 30}')
print(result)  # Output: {'name': 'John', 'age': 30}

# Convert input to string
result = to_str([1, 2, 3])
print(result)  # Output: "1, 2, 3"

# Convert input to DataFrame
data = [{'name': 'John', 'age': 30}, {'name': 'Jane', 'age': 25}]
result = to_df(data)
print(result)
#    name  age
# 0  John   30
# 1  Jane   25

# Convert input to numeric value
result = to_num("42", num_type=int)
print(result)  # Output: 42

# Convert input to readable dictionary format
result = to_readable_dict({'name': 'John', 'age': 30})
print(result)
# {
#     "name": "John",
#     "age": 30
# }

# Check if elements in a list or dictionary values are of the same type
result = is_same_dtype([1, 2, 3], dtype=int)
print(result)  # Output: True

# Convert XML to dictionary
import xml.etree.ElementTree as ET
xml_string = '''
<root>
    <name>John</name>
    <age>30</age>
</root>
'''
root = ET.fromstring(xml_string)
result = xml_to_dict(root)
print(result)  # Output: {'name': 'John', 'age': '30'}

# Convert input to lowercase string with leading/trailing whitespace removed
result = strip_lower("  Hello, World!  ")
print(result)  # Output: "hello, world!"

# Check if a nested structure is homogeneous
result = is_structure_homogeneous({'a': {'b': 1}, 'c': {'d': 2}})
print(result)  # Output: True

# Check if all elements in a list or all values in a dictionary are of the same type
result = is_homogeneous([1, 2, 3], type_check=int)
print(result)  # Output: True
```

These examples demonstrate how to use the various conversion and utility functions provided by the `ln_convert` module. You can convert inputs to lists, dictionaries, strings, DataFrames, numeric values, and readable dictionary formats. You can also check if elements in a list or dictionary values are of the same type, convert XML to a dictionary, process strings, check if a nested structure is homogeneous, and check if all elements or values are of the same type.