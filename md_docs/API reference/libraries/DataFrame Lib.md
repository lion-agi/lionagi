```
import lionagi.libs.ln_dataframe as dataframe
```
# DataFrame Extensions

This module extends pandas DataFrame functionalities, providing tools for merging, filtering, replacing, reading data, and more, leveraging the `lionagi.libs.ln_convert` module for type conversions and data manipulation.

## `extend_dataframe` Function

Merges two DataFrames while ensuring no duplicate entries based on a specified unique column.

### Arguments

- `df1 (pd.DataFrame)`: The primary DataFrame.
- `df2 (pd.DataFrame)`: The DataFrame to merge with the primary DataFrame.
- `unique_col (str)`: Column name to check for duplicate entries. Defaults to 'node_id'.
- `keep (str)`: Determines which duplicates (if any) to keep. Defaults to 'first'.
- `**kwargs`: Additional keyword arguments for `drop_duplicates`.

### Returns

`pd.DataFrame`: Combined DataFrame from `df1` and `df2` with duplicates removed based on the unique column.

### Example

```python
df1 = pd.DataFrame({'node_id': [1, 2, 3], 'value': ['A', 'B', 'C']})
df2 = pd.DataFrame({'node_id': [2, 3, 4], 'value': ['D', 'E', 'F']})
extended_df = extend_dataframe(df1, df2)
print(extended_df)
```

## `search_keywords` Function

Filters a DataFrame for rows where a specified column contains given keywords.

### Arguments

- `df (pd.DataFrame)`: DataFrame to search through.
- `keywords (str | list[str])`: Keyword(s) to search for.
- `column (str)`: Column to perform the search in. Defaults to "content".
- `case_sensitive (bool)`: Search case sensitivity. Defaults to False.
- `reset_index (bool)`: Resets DataFrame's index after filtering. Defaults to False.
- `dropna (bool)`: Drops rows with NA values before searching. Defaults to False.

### Returns

`pd.DataFrame`: Filtered DataFrame containing rows where the specified column contains any of the provided keywords.

### Example

```python
df = pd.DataFrame({'content': ['hello', 'world', 'hello world', 'none']})
filtered_df = search_keywords(df, keywords=['hello'], case_sensitive=False)
print(filtered_df)
```

## `replace_keyword` Function

Replaces occurrences of a specified keyword with a replacement string in a DataFrame column.

### Arguments

- `df (pd.DataFrame)`: DataFrame to modify.
- `keyword (str)`: Keyword to be replaced.
- `replacement (str)`: Replacement string.
- `inplace (bool)`: If True, modification is done in-place. Defaults to True.
- `column (str)`: Column for the replacement. Defaults to "content".
- `case_sensitive (bool)`: Case-sensitive replacement. Defaults to False.

### Returns

`pd.DataFrame | bool`: Updated DataFrame if `inplace` is False, True otherwise.

### Example

```python
df = pd.DataFrame({'content': ['Hello world', 'hello Earth', 'Goodbye all']})
replace_keyword(df, 'hello', 'Hi', case_sensitive=False)
print(df)
```

## `read_csv` Function

Reads a CSV file into a DataFrame with optional additional pandas `read_csv` parameters.

### Arguments

- `filepath (str)`: Path to the CSV file to read.
- `**kwargs`: Additional keyword arguments for `pandas.read_csv`.

### Returns

`pd.DataFrame`: DataFrame containing the data read from the CSV file.

### Example

```python
df = read_csv('data.csv')
print(df)
```

## `read_json` Function

Reads a JSON file into a DataFrame with optional additional pandas `read_json` parameters.

### Arguments

- `filepath (str)`: Path to the JSON file to read.
- `**kwargs`: Additional keyword arguments for `pandas.read_json`.

### Returns

`pd.DataFrame`: DataFrame containing the data read from the JSON file.

### Example

```python
df = read_json('data.json')
print(df)
```

## `remove_last_n_rows` Function

Removes the last 'n' rows from a DataFrame.

### Arguments

- `df (pd.DataFrame)`: DataFrame from which to remove rows.
- `steps (int)`: Number of rows to remove from the end.

### Returns

`pd.DataFrame`: DataFrame with the last 'n' rows removed.

### Raises

- `ValueError`: If 'steps' is negative or greater than the number of rows in the DataFrame.

### Example

```python
df = pd.DataFrame({'A': range(5)})
trimmed_df = remove_last_n_rows(df, 2)
print(trimmed_df)
```

## `update_row` Function

Updates a row's value for a specified column in a DataFrame.

### Arguments

- `df (pd.DataFrame)`: DataFrame to update.
- `row (str | int)`: Row index to update.
- `column (str | int)`: Column to update.
- `value (Any)`: New value for the specified column.

### Returns

`bool`: True if the update was successful, False otherwise.

### Example

```python
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
success = update_row(df, 0, 'A', 100)
print(df)
```
