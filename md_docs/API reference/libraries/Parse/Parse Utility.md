
The `ParseUtil` class offers a set of static methods designed to assist with parsing and processing strings, particularly for handling JSON data and Markdown content. These utilities simplify common tasks such as parsing slightly malformed JSON, escaping characters in JSON strings, extracting code blocks from Markdown, and converting Python types to their JSON equivalents.

## Methods Overview

### `fuzzy_parse_json`

^e7ab10

Parses a potentially incomplete or malformed JSON string by correcting formatting errors and attempting a parse again.

#### Arguments

- `str_to_parse (str)`: The JSON string to parse.
- `strict (bool, optional)`: Enforces strict JSON syntax. Defaults to False.

#### Returns

- The parsed JSON object, typically a dictionary or list.

### `escape_chars_in_json`

Escapes special characters in a JSON string using a specified character map.

#### Arguments

- `value (str)`: The string to be escaped.
- `char_map (dict, optional)`: Dictionary mapping characters to their escaped versions.

#### Returns

- `str`: The escaped JSON string.

### `extract_code_block`

Extracts and parses a code block from Markdown content.

#### Arguments

- `str_to_parse (str)`: The Markdown content to search.
- `language (str | None, optional)`: Language specifier for the code block.
- `regex_pattern (str | None, optional)`: Regular expression pattern to find the code block.
- `parser (Callable[[str], Any])`: Function to parse the extracted code block string.

#### Returns

- The result of parsing the code block.

### `md_to_json`

^a4f154

Extracts a JSON code block from Markdown content, parses it, and verifies required keys.

#### Arguments

- `str_to_parse (str)`: The Markdown content to parse.
- `expected_keys (list[str] | None, optional)`: Keys expected to be present in the parsed JSON object.
- `parser (Callable[[str], Any] | None, optional)`: Function to parse the extracted code block.

#### Returns

- The parsed JSON object from the Markdown content.

## Examples

### Example: Fuzzy Parsing JSON

```python
json_str = '{"name": "John", "age": 30, "city": "New York"'
parsed_json = ParseUtil.fuzzy_parse_json(json_str)
print(parsed_json)  # Output: {'name': 'John', 'age': 30, 'city': 'New York'}
```

### Example: Escaping Characters in JSON String

```python
json_str = 'Line 1\nLine 2'
escaped_str = ParseUtil.escape_chars_in_json(json_str)
print(escaped_str)  # Output: 'Line 1\\nLine 2'
```

### Example: Extracting and Parsing Code Block from Markdown

```python
markdown_str = '```json\n{"key": "value"}\n```'
parsed_block = ParseUtil.extract_code_block(markdown_str, language='json', parser=lambda x: x)
print(parsed_block)  # Output: {"key": "value"}
```

### Example: Converting Markdown to JSON with Expected Keys

```python
markdown_str = '```json\n{"key1": "value1", "key2": "value2"}\n```'
parsed_json = ParseUtil.md_to_json(markdown_str, expected_keys=['key1', 'key2'])
print(parsed_json)  # Output: {'key1': 'value1', 'key2': 'value2'}
```

The `ParseUtil` class streamlines the parsing and handling of JSON and Markdown data, making it easier to work with potentially malformed or complex string content. These utilities are particularly useful for applications that need to process or transform data represented in these formats.