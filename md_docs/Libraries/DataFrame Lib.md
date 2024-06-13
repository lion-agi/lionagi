
### `extend_dataframe`

`(df1: pd.DataFrame, df2: pd.DataFrame, /, unique_col: str = "node_id", keep="first", **kwargs) -> pd.DataFrame`

Merges two DataFrames while ensuring no duplicate entries based on a specified unique column.

Parameters:
- `df1` (pd.DataFrame): The primary DataFrame.
- `df2` (pd.DataFrame): The DataFrame to merge with the primary DataFrame.
- `unique_col` (str): The column name to check for duplicate entries. Defaults to 'node_id'.
- `keep` (str): Determines which duplicates to keep. Defaults to 'first'.
- `**kwargs`: Additional keyword arguments for `drop_duplicates`.

Returns:
- pd.DataFrame: A DataFrame combined from `df1` and `df2` with duplicates removed based on the unique column.

Raises:
- ValueError: If there is an error in extending the messages or if there is no data to extend.

### `search_keywords`
`(df: pd.DataFrame, /, keywords: str | list[str], *, column: str = "content", case_sensitive: bool = False, reset_index: bool = False, dropna: bool = False) -> pd.DataFrame`

Filters a DataFrame for rows where a specified column contains given keywords.

Parameters:
- `df` (pd.DataFrame): The DataFrame to search through.
- `keywords` (str | list[str]): A keyword or list of keywords to search for.
- `column` (str): The column to perform the search in. Defaults to "content".
- `case_sensitive` (bool): Whether the search should be case-sensitive. Defaults to False.
- `reset_index` (bool): Whether to reset the DataFrame's index after filtering. Defaults to False.
- `dropna` (bool): Whether to drop rows with NA values before searching. Defaults to False.

Returns:
- pd.DataFrame: A filtered DataFrame containing only rows where the specified column contains any of the provided keywords.

### `replace_keyword`
`(df: pd.DataFrame, /, keyword: str, replacement: str, *, inplace=True, column: str = "content", case_sensitive: bool = False) -> pd.DataFrame | bool`

Replaces occurrences of a specified keyword with a replacement string in a DataFrame column.

Parameters:
- `df` (pd.DataFrame): The DataFrame to modify.
- `keyword` (str): The keyword to be replaced.
- `replacement` (str): The string to replace the keyword with.
- `inplace` (bool): Whether to modify the DataFrame in place. Defaults to True.
- `column` (str): The column in which to perform the replacement. Defaults to "content".
- `case_sensitive` (bool): If True, performs a case-sensitive replacement. Defaults to False.

Returns:
- pd.DataFrame | bool: The modified DataFrame if `inplace` is False, otherwise True.

### `read_csv`
`(filepath: str, **kwargs) -> pd.DataFrame`

Reads a CSV file into a DataFrame with optional additional pandas read_csv parameters.

Parameters:
- `filepath` (str): The path to the CSV file to read.
- `**kwargs`: Additional keyword arguments to pass to pandas.read_csv function.

Returns:
- pd.DataFrame: A DataFrame containing the data read from the CSV file.

### `read_json`
`(filepath, **kwargs) -> pd.DataFrame`

Reads a JSON file into a DataFrame with optional additional pandas read_json parameters.

Parameters:
- `filepath` (str): The path to the JSON file to read.
- `**kwargs`: Additional keyword arguments to pass to pandas.read_json function.

Returns:
- pd.DataFrame: A DataFrame containing the data read from the JSON file.

### `remove_last_n_rows`
`(df: pd.DataFrame, steps: int) -> pd.DataFrame`

Removes the last 'n' rows from a DataFrame.

Parameters:
- `df` (pd.DataFrame): The DataFrame from which to remove rows.
- `steps` (int): The number of rows to remove from the end of the DataFrame.

Returns:
- pd.DataFrame: A DataFrame with the last 'n' rows removed.

Raises:
- ValueError: If `steps` is negative or greater than the number of rows in the DataFrame.

### `update_row`
`(df: pd.DataFrame, row: str | int, column: str | int, value: Any) -> bool`

Updates a row's value for a specified column in a DataFrame.

Parameters:
- `df` (pd.DataFrame): The DataFrame to update.
- `row` (str | int): The index or label of the row to update.
- `column` (str | int): The column whose value is to be updated.
- `value` (Any): The new value to set for the specified row and column.

Returns:
- bool: True if the update was successful, False otherwise.

## Usage Examples

```python
import pandas as pd
from lionagi.libs.dataframe import extend_dataframe, search_keywords, replace_keyword, read_csv, read_json, remove_last_n_rows, update_row

# Create sample DataFrames
df1 = pd.DataFrame({'node_id': [1, 2, 3], 'content': ['apple', 'banana', 'orange']})
df2 = pd.DataFrame({'node_id': [3, 4, 5], 'content': ['grape', 'kiwi', 'mango']})

# Extend DataFrame
extended_df = extend_dataframe(df1, df2)
print(extended_df)

# Search keywords
filtered_df = search_keywords(extended_df, keywords=['apple', 'banana'], column='content')
print(filtered_df)

# Replace keyword
replace_keyword(extended_df, keyword='apple', replacement='pineapple', inplace=True)
print(extended_df)

# Read CSV
csv_df = read_csv('data.csv')
print(csv_df)

# Read JSON
json_df = read_json('data.json')
print(json_df)

# Remove last n rows
modified_df = remove_last_n_rows(extended_df, steps=2)
print(modified_df)

# Update row
update_row(extended_df, row=0, column='content', value='watermelon')
print(extended_df)
```

In these examples, we demonstrate how to use the various utility functions provided by the module. We create sample DataFrames, extend them, search for keywords, replace keywords, read from CSV and JSON files, remove rows, and update row values.