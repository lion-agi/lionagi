
#  Class API Reference

The `` class offers a suite of static methods designed for data type conversion and manipulation, simplifying the handling of various data formats and structures.

## to_dict

Converts a given input to a dictionary. It supports converting JSON strings to dictionaries, directly returning dictionary inputs, or raising errors for unsupported types.

### Usage

```python
dict_obj = .to_dict(input_)
```

### Parameters

- `input_`: The input to be converted to a dictionary, which can be a JSON string or a dictionary.

## is_same_dtype

Checks if all elements in an input list or dictionary values are of the same data type.

### Usage

```python
is_homogeneous = .is_same_dtype(input_, dtype=None)
```

### Parameters

- `input_`: A list or dictionary to check.
- `dtype`: Optional; the data type to check against. If not provided, the type of the first element is used as the reference.

## xml_to_dict

Converts an XML `ElementTree.Element` to a dictionary, preserving hierarchy and structure.

### Usage

```python
xml_dict = .xml_to_dict(root)
```

### Parameters

- `root`: The root `ElementTree.Element` of the XML structure to convert.

## str_to_num

Converts a string to a numeric type (int or float), with options for upper and lower bounds, and precision.

### Usage

```python
number = .to_num(input_, upper_bound=None, lower_bound=None, num_type=int,
                            precision=None)
```

### Parameters

- `input_`: The string containing the numeric value to convert.
- `upper_bound`: Optional; specifies an upper bound for the numeric value.
- `lower_bound`: Optional; specifies a lower bound for the numeric value.
- `num_type`: The numeric type to convert to (`int` or `float`).
- `precision`: Optional; specifies the number of decimal places for float conversions.

## strip_lower

Converts any input to a lowercase string, stripping leading and trailing whitespace.

### Usage

```python
stripped_lower_str = .strip_lower(input_)
```

### Parameters

- `input_`: The input to convert to a lowercase, stripped string.


## to_df

Converts various types of inputs into a pandas DataFrame. This method supports converting lists of dictionaries, DataFrames, Series, or a combination of these into a single DataFrame.

### Usage

```python
df = .to_df(item, how="all", drop_kwargs=None, reset_index=True, **kwargs)
```

### Parameters

- `item`: Input data to be converted into a DataFrame. Can be a list of dictionaries, DataFrames, Series, or a single DataFrame or Series.
- `how`: Specifies how to handle null values when concatenating. Defaults to `"all"`.
- `drop_kwargs`: Additional keyword arguments for pandas' `dropna` method.
- `reset_index`: Whether to reset the DataFrame's index after conversion. Defaults to `True`.
- `**kwargs`: Additional keyword arguments for pandas' `concat` method (when applicable).

## to_readable_dict

Converts a dictionary or a list into a JSON-formatted string for easier readability. This method is particularly useful for presenting or logging complex data structures in a human-readable format.

### Usage

```python
readable_json = .to_readable_dict(input_)
```

### Parameters

- `input_`: The dictionary or list to convert into a readable JSON string.
