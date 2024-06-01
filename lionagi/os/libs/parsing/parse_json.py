import re
from typing import Any, Callable
from ..data_handlers import to_dict
from .util import md_json_char_map


def fuzzy_parse_json(
    str_to_parse: str, *, strict: bool = False, return_str: bool = False
):
    """
    Parses a potentially incomplete or malformed JSON string by adding missing closing brackets or braces.

    Tries to parse the input string as JSON and, on failure due to formatting errors, attempts to correct
    the string by appending necessary closing characters before retrying.

    Args:
            s (str): The JSON string to parse.
            strict (bool, optional): If True, enforces strict JSON syntax. Defaults to False.

    Returns:
            The parsed JSON object, typically a dictionary or list.

    Raises:
            ValueError: If parsing fails even after attempting to correct the string.

    Example:
            >>> fuzzy_parse_json('{"name": "John", "age": 30, "city": "New York"')
            {'name': 'John', 'age': 30, 'city': 'New York'}
    """

    def _return_str(x):
        return x, str_to_parse

    try:
        result = to_dict(str_to_parse, strict=strict)
        return _return_str(result) if return_str else result

    except Exception:
        fixed_s = fix_json_string(str_to_parse)
        try:
            result = to_dict(fixed_s, strict=strict)
            return _return_str(result) if return_str else result

        except Exception:
            try:
                fixed_s = fixed_s.replace("'", '"')
                result = to_dict(fixed_s, strict=strict)
                return _return_str(result) if return_str else result

            except Exception as e:
                raise ValueError(
                    f"Failed to parse JSON after fixing attempts: {e}"
                ) from e


def fix_json_string(str_to_parse: str) -> str:

    brackets = {"{": "}", "[": "]"}
    open_brackets = []

    for char in str_to_parse:
        if char in brackets:
            open_brackets.append(brackets[char])
        elif char in brackets.values():
            if not open_brackets or open_brackets[-1] != char:
                raise ValueError("Mismatched or extra closing bracket found.")
            open_brackets.pop()

    return str_to_parse + "".join(reversed(open_brackets))


def escape_chars_in_json(value: str, char_map=None) -> str:
    """
    Escapes special characters in a JSON string using a specified character map.

    This method replaces newline, carriage return, tab, and double quote characters
    in a given string with their escaped versions defined in the character map. If no map is provided,
    a default mapping is used.

    Args:
            value: The string to be escaped.
            char_map: An optional dictionary mapping characters to their escaped versions.
                    If not provided, a default mapping that escapes newlines, carriage returns,
                    tabs, and double quotes is used.

    Returns:
            The escaped JSON string.

    Examples:
            >>> escape_chars_in_json('Line 1\nLine 2')
            'Line 1\\nLine 2'
    """

    def replacement(match):
        char = match.group(0)
        _char_map = char_map or md_json_char_map
        return _char_map.get(char, char)  # Default to the char itself if not in map

    # Match any of the special characters to be escaped.
    return re.sub(r'[\n\r\t"]', replacement, value)


# inspired by langchain_core.output_parsers.json (MIT License)
# https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/output_parsers/json.py
@staticmethod
def extract_json_block(
    str_to_parse: str,
    language: str | None = None,
    regex_pattern: str | None = None,
    *,
    parser: Callable[[str], Any] = None,
) -> Any:
    """
    Extracts and parses a code block from Markdown content.

    This method searches for a code block in the given Markdown string, optionally
    filtered by language. If a code block is found, it is parsed using the provided parser function.

    Args:
            str_to_parse: The Markdown content to search.
            language: An optional language specifier for the code block. If provided,
                    only code blocks of this language are considered.
            regex_pattern: An optional regular expression pattern to use for finding the code block.
                    If provided, it overrides the language parameter.
            parser: A function to parse the extracted code block string.

    Returns:
            The result of parsing the code block with the provided parser function.

    Raises:
            ValueError: If no code block is found in the Markdown content.

    Examples:
            >>> extract_code_block('```python\\nprint("Hello, world!")\\n```', language='python', parser=lambda x: x)
            'print("Hello, world!")'
    """

    if language:
        regex_pattern = rf"```{language}\n?(.*?)\n?```"
    else:
        regex_pattern = r"```\n?(.*?)\n?```"

    match = re.search(regex_pattern, str_to_parse, re.DOTALL)
    code_str = ""
    if match:
        code_str = match[1].strip()
    else:
        raise ValueError(
            f"No {language or 'specified'} code block found in the Markdown content."
        )
    if not match:
        str_to_parse = str_to_parse.strip()
        if str_to_parse.startswith("```json\n") and str_to_parse.endswith("\n```"):
            str_to_parse = str_to_parse[8:-4].strip()

    parser = parser or fuzzy_parse_json
    return parser(code_str)


@staticmethod
def md_to_json(
    str_to_parse: str,
    *,
    expected_keys: list[str] | None = None,
    parser: Callable[[str], Any] | None = None,
) -> Any:
    """
    Extracts a JSON code block from Markdown content, parses it, and verifies required keys.

    This method uses `extract_code_block` to find and parse a JSON code block within the given
    Markdown string. It then optionally verifies that the parsed JSON object contains all expected keys.

    Args:
            str_to_parse: The Markdown content to parse.
            expected_keys: An optional list of keys expected to be present in the parsed JSON object.
            parser: An optional function to parse the extracted code block. If not provided,
                    `fuzzy_parse_json` is used with default settings.

    Returns:
            The parsed JSON object from the Markdown content.

    Raises:
            ValueError: If the JSON code block is missing, or if any of the expected keys are missing
                    from the parsed JSON object.

    Examples:
            >>> md_to_json('```json\\n{"key": "value"}\\n```', expected_keys=['key'])
            {'key': 'value'}
    """
    json_obj = extract_json_block(
        str_to_parse, language="json", parser=parser or fuzzy_parse_json
    )

    if expected_keys:
        if missing_keys := [key for key in expected_keys if key not in json_obj]:
            raise ValueError(
                f"Missing expected keys in JSON object: {', '.join(missing_keys)}"
            )

    return json_obj
