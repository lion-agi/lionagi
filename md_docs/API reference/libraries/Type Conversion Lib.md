```
import lionagi.libs.ln_convert as convert
```
# Type Conversion

## `to_list` Function

Converts the input object to a list. This function is capable of handling various input types, utilizing single dispatch to specialize for different types such as list, tuple, and set. The default implementation handles general iterables by attempting to convert them to a list, optionally flattening and dropping None values based on provided arguments.

### Arguments

- `input_ (Any)`: The input object to convert to a list.
- `flatten (bool)`: If True, and the input is a nested list, the function will attempt to flatten it. Default is True.
- `dropna (bool)`: If True, None values will be removed from the resulting list. Default is True.

### Returns

`list[Any]`: A list representation of the input, with modifications based on `flatten` and `dropna`.

### Raises

- `ValueError`: If the input type is unsupported or cannot be converted to a list.

### Example

```python
# Converting a nested list with flattening
nested_list = [[1, 2], [3, 4], [5]]
flat_list = to_list(nested_list)
print(flat_list)  # Output: [1, 2, 3, 4, 5]

# Converting a tuple, without dropping None values
tuple_input = (1, None, 3)
tuple_to_list = to_list(tuple_input, dropna=False)
print(tuple_to_list)  # Output: [1, None, 3]

# Converting a set, dropping None values
set_input = {None, 1, 2, 3}
set_to_list = to_list(set_input)
print(set_to_list)  # Output may vary due to set's unordered nature, e.g., [1, 2, 3]
```

Note: Specialized implementations for lists, tuples, and sets may use additional keyword arguments specific to their conversion logic. The default behavior for dictionaries is to wrap them in a list without flattening. For specific behaviors with these and other types, refer to the registered implementations.


## `to_dict` Function

Converts the input object to a dictionary. This function is overloaded to handle specific input types such as `dict`, `str`, `pandas.Series`, `pandas.DataFrame`, and Pydantic's `BaseModel`, utilizing single dispatch for type-specific conversions.

### Arguments

- `input_ (Any)`: The input object to convert to a dictionary.
- `*args`: Variable length argument list for additional options in type-specific handlers.
- `**kwargs`: Arbitrary keyword arguments for additional options in type-specific handlers.

### Returns

`dict[Any, Any]`: A dictionary representation of the input object.

### Raises

- `ValueError`: If the input type is not supported or cannot be converted to a dictionary.

### Examples

**Dictionary Input:**
```python
dict_input = {'key': 'value'}
converted_dict = to_dict(dict_input)
print(converted_dict)  # Output: {'key': 'value'}
```

**JSON String Input:**
```python
json_str = '{"name": "John", "age": 30}'
converted_dict = to_dict(json_str)
print(converted_dict)  # Output: {'name': 'John', 'age': 30}
```

**Pandas Series Input:**
```python
import pandas as pd
series_input = pd.Series([1, 2, 3], index=['a', 'b', 'c'])
converted_dict = to_dict(series_input)
print(converted_dict)  # Output: {'a': 1, 'b': 2, 'c': 3}
```

**Pandas DataFrame Input:**
```python
df_input = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
converted_dict = to_dict(df_input, orient='list')
print(converted_dict)  # Output: {'A': [1, 2], 'B': [3, 4]}
```

**Pydantic BaseModel Input:**
```python
from pydantic import BaseModel
class User(BaseModel):
    name: str
    age: int

user_input = User(name="John", age=30)
converted_dict = to_dict(user_input)
print(converted_dict)  # Output: {'name': 'John', 'age': 30}
```

Note: The default behavior raises a `ValueError` for unsupported types. For dictionaries, the input is returned without modification. For JSON strings, `pandas.Series`, `pandas.DataFrame`, and `BaseModel` instances, specific conversion logic is applied as shown in the examples.


## `to_df` Function

Converts various input types to a pandas DataFrame, offering options for handling missing data and resetting the index. This function is equipped to handle specific data structures such as lists of dictionaries, lists of pandas objects (DataFrames or Series), and others, utilizing single dispatch for enhanced flexibility.

### Arguments

- `input_ (Any)`: The input data to convert into a DataFrame. Accepts a wide range of types.
- `how (str)`: Specifies how missing values are dropped. Passed directly to `DataFrame.dropna()`. Default is "all".
- `drop_kwargs (dict[str, Any] | None)`: Additional keyword arguments for `DataFrame.dropna()`.
- `reset_index (bool)`: If True, the DataFrame index will be reset, removing the index labels. Default is True.
- `**kwargs`: Additional keyword arguments passed to the pandas DataFrame constructor.

### Returns

`pd.DataFrame`: A pandas DataFrame constructed from the input data.

### Raises

- `ValueError`: If there is an error during the conversion process.

### Examples

**List of Dictionaries Input:**
```python
list_dicts = [{'a': 1, 'b': 2}, {'a': 3, 'b': None}]
df = to_df(list_dicts, drop_kwargs={'subset': ['a']})
print(df)
# Output: 
#    a    b
# 0  1  2.0
# 1  3  NaN
```

**List of DataFrames Input:**
```python
import pandas as pd
df1 = pd.DataFrame({'A': [1, 2]})
df2 = pd.DataFrame({'B': [3, 4]})
df = to_df([df1, df2], reset_index=False)
print(df)
# Output: 
#    A   B
# 0  1   3
# 1  2   4
```

**Direct Conversion with Custom Index Reset:**
```python
data = {'col1': [1, 2, None], 'col2': [3, None, 6]}
df = to_df(data, reset_index=False)
print(df)
# Output: 
#    col1  col2
# 0   1.0   3.0
# 1   2.0   NaN
# 2   NaN   6.0
```

Note: The base implementation attempts to directly convert the input to a DataFrame, applying `dropna` and `reset_index` as specified. This function is overloaded to provide specialized behavior for different input types, enhancing its utility and flexibility.

## `to_str` Function

Converts the input object to a string. Utilizes single dispatch to handle specific input types such as `dict`, `str`, `list`, `pandas.Series`, and `pandas.DataFrame`, providing type-specific conversions to string format.

### Arguments

- `input_ (Any)`: The input object to convert to a string.
- `*args, **kwargs`: Additional options for type-specific handlers.

### Returns

`str`: A string representation of the input object.

### Examples

**Dictionary Input:**
```python
dict_input = {'key': 'value'}
string_output = to_str(dict_input)
print(string_output)  # Output: '{"key": "value"}'
```

**List Input:**
```python
list_input = [1, 2, 3]
string_output = to_str(list_input)
print(string_output)  # Output: '1, 2, 3'
```

**Pandas Series Input:**
```python
import pandas as pd
series_input = pd.Series([1, 2, 3], index=['a', 'b', 'c'])
string_output = to_str(series_input)
print(string_output)  # Output might be a JSON string representation depending on pandas version
```

**Pandas DataFrame Input (As List):**
```python
df_input = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
string_output = to_str(df_input, as_list=True)
print(string_output)  # Output might be a JSON string representation of a list of dictionaries depending on pandas version
```

Note: The base implementation uses the `str()` function for conversion. For detailed behaviors with each supported type, refer to the registered implementations.

## `to_num` Function

Converts the input to a numeric value of specified type, with optional bounds and precision.

### Arguments

- `input_ (Any)`: The input value to convert. Can be of any type that `to_str` can handle.
- `upper_bound (int | float | None)`: The upper bound for the numeric value. Values above this are not allowed.
- `lower_bound (int | float | None)`: The lower bound for the numeric value. Values below this are not allowed.
- `num_type (Type[int | float])`: The numeric type to convert to. Either `int` or `float`.
- `precision (int | None)`: The number of decimal places for the result. Only applies to `float`.

### Returns

`int | float`: The converted numeric value, adhering to the specified type and precision.

### Raises

- `ValueError`: If the input cannot be converted to a number, or if it violates the specified bounds.

### Examples

**String to Integer Conversion:**
```python
input_str = "123"
number = to_num(input_str)
print(number)  # Output: 123
```

**String to Float Conversion with Precision:**
```python
input_str = "123.456"
number = to_num(input_str, num_type=float, precision=2)
print(number)  # Output: 123.46
```

**Bounds Enforcement:**
```python
input_str = "150"
number = to_num(input_str, upper_bound=100)
# This will raise a ValueError indicating the number is above the upper bound.
```

Note: Converts string representations of numbers to actual numeric types, with options for enforcing upper and lower bounds and specifying precision for floating-point numbers.


## `to_readable_dict` Function

Converts a given input to a readable dictionary format, either as a string or a list of dictionaries, enhancing readability for debugging and logging purposes.

### Arguments

- `input_ (Any | list[Any])`: The input to convert to a readable dictionary format.

### Returns

`str | list[str]`: The readable dictionary format of the input.

### Raises

- `ValueError`: If the given input cannot be converted to a readable dictionary format.

### Examples

**Dictionary Input:**
```python
dict_input = {'key': 'value', 'number': 123}
readable_str = to_readable_dict(dict_input)
print(readable_str)
# Output: 
# {
#     "key": "value",
#     "number": 123
# }
```

**List of Dictionaries Input:**
```python
list_input = [{'key1': 'value1'}, {'key2': 'value2'}]
readable_str = to_readable_dict(list_input)
# This will raise a ValueError as `to_readable_dict` expects either a dictionary or a single item that can be converted to a dictionary.
```

Note: Aims to produce a human-readable string representation of a dictionary for easier debugging and logging. This function uses JSON formatting to achieve readability.

## `is_same_dtype` Function

Checks if all elements in a list or dictionary values are of the same data type.

### Arguments

- `input_ (list | dict)`: The input list or dictionary to check.
- `dtype (Type | None)`: The data type to check against. If `None`, uses the type of the first element.

### Returns

`bool`: True if all elements or dictionary values are of the same type, False otherwise.

### Examples

**List of Same Type:**
```python
input_list = [1, 2, 3]
print(is_same_dtype(input_list))  # Output: True
```

**Dictionary with Mixed Types:**
```python
input_dict = {'a': 1, 'b': '2', 'c': 3}
print(is_same_dtype(input_dict))  # Output: False
```

Note: Simplifies type consistency checks in lists and dictionaries, facilitating data validation and preprocessing tasks.

## `xml_to_dict` Function

Converts an XML ElementTree to a nested dictionary, useful for parsing XML data into a more manageable format for Python processing.

### Arguments

- `root (xml.etree.ElementTree.Element)`: The root element of the XML tree to convert.

### Returns

`dict[str, Any]`: A dictionary representation of the XML data.

### Examples

Assuming `root` is an XML Element obtained from parsing an XML document:

```python
import xml.etree.ElementTree as ET
xml_data = '''<data><item key="value">Text</item></data>'''
root = ET.fromstring(xml_data)
converted_dict = xml_to_dict(root)
print(converted_dict)
# Output: {'data': {'item': [{'@key': 'value', '#text': 'Text'}]}}
```

Note: Facilitates the conversion of XML data into Python dictionaries, easing the handling and manipulation of XML content within Python applications.

## `strip_lower` Function

Converts the input to a lowercase string with leading and trailing whitespace removed, useful for standardizing string data before processing or storage.

### Arguments

- `input_ (Any)`: The input value to convert and process.

### Returns

`str`: The processed string.

### Raises

- `ValueError`: If the input cannot be converted to a string.

### Examples

**String Input:**
```python
input_str = " Hello, WORLD! "
processed_str = strip_lower(input_str)
print(processed_str)  # Output: 'hello, world!'
```

Note: Helps in preparing string data for comparison or processing by ensuring a consistent format.

## `is_structure_homogeneous` Function

Checks if a nested structure is homogeneous, meaning it does not contain a mix of lists and dictionaries, useful for validating data structures.

### Arguments

- `structure (Any)`: The nested structure to check.
- `return_structure_type (bool)`: Flag to indicate whether to return the type of the homogeneous structure.

### Returns

- If `return_structure_type` is False: `bool` indicating whether the structure is homogeneous.
- If `return_structure_type` is True: Tuple containing a boolean indicating whether the structure is homogeneous, and the type of the homogeneous structure if it is homogeneous (either `list`, `dict`, or `None`).

### Examples

```python
structure = {'a': [1, 2], 'b': [3, 4]}
print(is_structure_homogeneous(structure))
# Output: True

structure = {'a': [1, 2], 'b': {'c': 3}}
print(is_structure_homogeneous(structure))
# Output: False
```

Note: Aids in ensuring data structures are consistent for processing that requires homogeneity in type.

## `is_homogeneous` Function

Determines if all items in a list or all values in a dictionary are of a specified type.

### Arguments

- `iterables (list[Any] | dict[Any, Any])`: The list or dictionary to check.
- `type_check (type)`: The type to check against each item or value.

### Returns

`bool`: True if all items or values match the specified type, False otherwise.

### Examples

**List Check:**
```python
items = [1, 2, 3]
print(is_homogeneous(items, int))  # Output: True
```

**Dictionary Value Check:**
```python
values = {'a': 'hello', 'b': 'world'}
print(is_homogeneous(values, str))  # Output: True
```

Note: Useful for data type validation in collections, ensuring that all items or values conform to a specified type for consistent processing or analysis.
