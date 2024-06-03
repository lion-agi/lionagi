import re
from typing import Any, Callable

from lionagi.os.libs.parsers.util import md_json_char_map
from lionagi.os.libs.parsers.fuzzy_parse_json import fuzzy_parse_json


def md_to_json(
    str_to_parse: str,
    *,
    expected_keys: list[str] | None = None,
    parser: Callable[[str], Any] | None = None,
) -> Any:
    """
    Parse a JSON block from a Markdown string and validate its keys.

    This function extracts a JSON block from a Markdown string using the
    `extract_json_block` function and validates the presence of expected
    keys in the parsed JSON object.

    Args:
        str_to_parse: The Markdown string to parse.
        expected_keys: A list of keys expected to be present in the JSON
            object. If provided, the function will raise a ValueError if
            any of the expected keys are missing.
        parser: A custom parser function to parse the JSON string. If not
            provided, the `fuzzy_parse_json` function will be used.

    Returns:
        The parsed JSON object.

    Raises:
        ValueError: If the expected keys are not present in the JSON
            object or if no JSON block is found.
    """
    json_obj = extract_json_block(str_to_parse, parser=parser or fuzzy_parse_json)

    if expected_keys:
        missing_keys = [key for key in expected_keys if key not in json_obj]
        if missing_keys:
            raise ValueError(
                f"Missing expected keys in JSON object: {', '.join(missing_keys)}"
            )

    return json_obj


def escape_chars_in_json(value: str, char_map: dict | None = None) -> str:
    """
    Escape special characters in a JSON string using a character map.

    This function replaces newline, carriage return, tab, and double
    quote characters in the given string with their escaped versions
    defined in the character map. If no map is provided, a default
    mapping is used.

    Args:
        value: The string to be escaped.
        char_map: An optional dictionary mapping characters to their
            escaped versions. If not provided, a default mapping that
            escapes newlines, carriage returns, tabs, and double quotes
            is used.

    Returns:
        The escaped JSON string.

    Example:
        >>> escape_chars_in_json('Line 1\\nLine 2')
        'Line 1\\\\nLine 2'
    """
    char_map = char_map or md_json_char_map
    for k, v in char_map.items():
        value = value.replace(k, v)
    return value


def extract_json_block(
    str_to_parse: str,
    regex_pattern: str | None = None,
    *,
    parser: Callable[[str], Any] = None,
) -> Any:
    """
    Extract and parse a JSON block from Markdown content.

    This function searches for a JSON block in the given Markdown string
    using a regular expression pattern. If a JSON block is found, it is
    parsed using the provided parser function.

    Args:
        str_to_parse: The Markdown content to search.
        regex_pattern: An optional regular expression pattern to use for
            finding the JSON block. If not provided, a default pattern
            that matches a JSON block enclosed in triple backticks is
            used.
        parser: A function to parse the extracted JSON string. If not
            provided, the `fuzzy_parse_json` function will be used.

    Returns:
        The result of parsing the JSON block with the provided parser
        function.

    Raises:
        ValueError: If no JSON block is found in the Markdown content.

    Example:
        >>> extract_json_block('```json\\n{"key": "value"}\\n```')
        {'key': 'value'}
    """
    regex_pattern = regex_pattern or r"```json\n?(.*?)\n?```"

    match = re.search(regex_pattern, str_to_parse, re.DOTALL)
    if match:
        code_str = match.group(1).strip()
    else:
        str_to_parse = str_to_parse.strip()
        if str_to_parse.startswith("```json\n") and str_to_parse.endswith("\n```"):
            code_str = str_to_parse[8:-4].strip()
        else:
            raise ValueError("No JSON code block found in the Markdown content.")

    parser = parser or fuzzy_parse_json
    return parser(code_str)
