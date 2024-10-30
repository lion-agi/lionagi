# ParseUtil and StringMatch API Reference

This API reference provides documentation for the `ParseUtil` and `StringMatch` classes, which offer utility functions for parsing and matching strings.

## Table of Contents

1. [ParseUtil](#parseutil)
   - [fuzzy_parse_json](#fuzzy_parse_json)
   - [fix_json_string](#fix_json_string)
   - [escape_chars_in_json](#escape_chars_in_json)
   - [extract_code_block](#extract_code_block)
   - [md_to_json](#md_to_json)
   - [_extract_docstring_details_google](#_extract_docstring_details_google)
   - [_extract_docstring_details_rest](#_extract_docstring_details_rest)
   - [_extract_docstring_details](#_extract_docstring_details)
   - [_python_to_json_type](#_python_to_json_type)
   - [_func_to_schema](#_func_to_schema)
2. [StringMatch](#stringmatch)
   - [jaro_distance](#jaro_distance)
   - [jaro_winkler_similarity](#jaro_winkler_similarity)
   - [levenshtein_distance](#levenshtein_distance)
   - [correct_dict_keys](#correct_dict_keys)
   - [choose_most_similar](#choose_most_similar)
   - [force_validate_dict](#force_validate_dict) ^b73a5b

## ParseUtil

The `ParseUtil` class provides utility functions for parsing and manipulating strings, particularly in the context of JSON and Markdown.

### fuzzy_parse_json

```python
@staticmethod
def fuzzy_parse_json(str_to_parse: str, *, strict: bool = False) -> Any
```

Parses a potentially incomplete or malformed JSON string by adding missing closing brackets or braces.

**Args:**
- `str_to_parse` (str): The JSON string to parse.
- `strict` (bool, optional): If True, enforces strict JSON syntax. Defaults to False.

**Returns:**
The parsed JSON object, typically a dictionary or list.

**Raises:**
- `ValueError`: If parsing fails even after attempting to correct the string.

### fix_json_string

```python
@staticmethod
def fix_json_string(str_to_parse: str) -> str
```

Fixes a JSON string by adding missing closing brackets or braces.

**Args:**
- `str_to_parse` (str): The JSON string to fix.

**Returns:**
The fixed JSON string.

**Raises:**
- `ValueError`: If there are mismatched or extra closing brackets.

### escape_chars_in_json

```python
@staticmethod
def escape_chars_in_json(value: str, char_map: dict = None) -> str
```

Escapes special characters in a JSON string using a specified character map.

**Args:**
- `value` (str): The string to be escaped.
- `char_map` (dict, optional): A dictionary mapping characters to their escaped versions. If not provided, a default mapping that escapes newlines, carriage returns, tabs, and double quotes is used.

**Returns:**
The escaped JSON string.

### extract_code_block

```python
@staticmethod
def extract_code_block(str_to_parse: str, language: str | None = None, regex_pattern: str | None = None, *, parser: Callable[[str], Any]) -> Any
```

Extracts and parses a code block from Markdown content.

**Args:**
- `str_to_parse` (str): The Markdown content to search.
- `language` (str, optional): An optional language specifier for the code block. If provided, only code blocks of this language are considered.
- `regex_pattern` (str, optional): An optional regular expression pattern to use for finding the code block. If provided, it overrides the language parameter.
- `parser` (Callable[[str], Any]): A function to parse the extracted code block string.

**Returns:**
The result of parsing the code block with the provided parser function.

**Raises:**
- `ValueError`: If no code block is found in the Markdown content.

### md_to_json

```python
@staticmethod
def md_to_json(str_to_parse: str, *, expected_keys: list[str] | None = None, parser: Callable[[str], Any] | None = None) -> Any
```

Extracts a JSON code block from Markdown content, parses it, and verifies required keys.

**Args:**
- `str_to_parse` (str): The Markdown content to parse.
- `expected_keys` (list[str], optional): An optional list of keys expected to be present in the parsed JSON object.
- `parser` (Callable[[str], Any], optional): An optional function to parse the extracted code block. If not provided, `fuzzy_parse_json` is used with default settings.

**Returns:**
The parsed JSON object from the Markdown content.

**Raises:**
- `ValueError`: If the JSON code block is missing, or if any of the expected keys are missing from the parsed JSON object.

### _extract_docstring_details_google

```python
@staticmethod
def _extract_docstring_details_google(func: Callable) -> tuple[str, dict[str, str]]
```

Extracts the function description and parameter descriptions from the docstring following the Google style format.

**Args:**
- `func` (Callable): The function from which to extract docstring details.

**Returns:**
A tuple containing the function description and a dictionary with parameter names as keys and their descriptions as values.

### _extract_docstring_details_rest

```python
@staticmethod
def _extract_docstring_details_rest(func: Callable) -> tuple[str, dict[str, str]]
```

Extracts the function description and parameter descriptions from the docstring following the reStructuredText (reST) style format.

**Args:**
- `func` (Callable): The function from which to extract docstring details.

**Returns:**
A tuple containing the function description and a dictionary with parameter names as keys and their descriptions as values.

### _extract_docstring_details

```python
@staticmethod
def _extract_docstring_details(func: Callable, style: str = "google") -> tuple[str, dict[str, str]]
```

Extracts the function description and parameter descriptions from the docstring of the given function using either Google style or reStructuredText (reST) style format.

**Args:**
- `func` (Callable): The function from which to extract docstring details.
- `style` (str): The style of docstring to parse ('google' or 'reST').

**Returns:**
A tuple containing the function description and a dictionary with parameter names as keys and their descriptions as values.

**Raises:**
- `ValueError`: If an unsupported style is provided.

### _python_to_json_type

```python
@staticmethod
def _python_to_json_type(py_type: str) -> str
```

Converts a Python type to its JSON type equivalent.

**Args:**
- `py_type` (str): The name of the Python type.

**Returns:**
The corresponding JSON type.

### _func_to_schema

```python
@staticmethod
def _func_to_schema(func: Callable, style: str = "google") -> dict[str, Any]
```

Generates a schema description for a given function, using typing hints and docstrings. The schema includes the function's name, description, and parameters.

**Args:**
- `func` (Callable): The function to generate a schema for.
- `style` (str): The docstring format ('google' or 'reST').

**Returns:**
A schema describing the function.

## StringMatch

The `StringMatch` class provides utility functions for comparing and matching strings using various string similarity metrics.

### jaro_distance

```python
@staticmethod
def jaro_distance(s: str, t: str) -> float
```

Calculates the Jaro distance between two strings.

**Args:**
- `s` (str): The first string to compare.
- `t` (str): The second string to compare.

**Returns:**
A float representing the Jaro distance between the two strings, ranging from 0 to 1, where 1 means the strings are identical.

### jaro_winkler_similarity

```python
@staticmethod
def jaro_winkler_similarity(s: str, t: str, scaling: float = 0.1) -> float
```

Calculates the Jaro-Winkler similarity between two strings.

**Args:**
- `s` (str): The first string to compare.
- `t` (str): The second string to compare.
- `scaling` (float, optional): The scaling factor for how much the score is adjusted upwards for having common prefixes. The scaling factor should be less than 1, and a typical value is 0.1.

**Returns:**
A float representing the Jaro-Winkler similarity between the two strings, ranging from 0 to 1, where 1 means the strings are identical.

### levenshtein_distance

```python
@staticmethod
def levenshtein_distance(a: str, b: str) -> int
```

Calculates the Levenshtein distance between two strings.

**Args:**
- `a` (str): The first string to compare.
- `b` (str): The second string to compare.

**Returns:**
An integer representing the Levenshtein distance between the two strings.

### correct_dict_keys

```python
@staticmethod
def correct_dict_keys(keys: dict | list[str], dict_: dict, score_func: Callable[[str, str], float] = None) -> dict
```

Corrects the keys of a dictionary based on a list of correct keys using string similarity.

**Args:**
- `keys` (dict | list[str]): The correct keys to match against.
- `dict_` (dict): The dictionary with keys to correct.
- `score_func` (Callable[[str, str], float], optional): The function to use for calculating string similarity scores. Defaults to `jaro_winkler_similarity`.

**Returns:**
A new dictionary with corrected keys.

### choose_most_similar

```python
@staticmethod
def choose_most_similar(word: str, correct_words_list: list[str], score_func: Callable[[str, str], float] = None) -> str
```

Chooses the most similar word from a list of correct words based on string similarity.

**Args:**
- `word` (str): The word to find a similar match for.
- `correct_words_list` (list[str]): The list of correct words to compare against.
- `score_func` (Callable[[str, str], float], optional): The function to use for calculating string similarity scores. Defaults to `jaro_winkler_similarity`.

**Returns:**
The most similar word from the list of correct words.

### force_validate_dict

```python
@staticmethod
def force_validate_dict(x: Any, keys: dict | list[str]) -> dict
```

Forces the validation of a dictionary by correcting its keys based on a list of correct keys using string similarity.

**Args:**
- `x` (Any): The input to validate as a dictionary. Can be a string or a dictionary.
- `keys` (dict | list[str]): The correct keys to match against.

**Returns:**
A validated dictionary with corrected keys.

**Raises:**
- `ValueError`: If the input cannot be validated as a dictionary.

That covers the main components and functions provided by the `ParseUtil` and `StringMatch` classes. Let me know if you have any further questions!
