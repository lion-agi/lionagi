import json
import re
from typing import Any

from .parse import fuzzy_parse_json


def to_json(
    string: str | list[str], /, fuzzy_parse: bool = False
) -> list[dict[str, Any]] | dict:
    """Extract and parse JSON content from a string or markdown code blocks.

    This function attempts to parse JSON directly from the input string first.
    If that fails, it looks for JSON content within markdown code blocks
    (denoted by ```json).

    Args:
        string: Input string or list of strings to parse. If a list is provided,
               it will be joined with newlines.

    Returns:
        - A dictionary if a single JSON object is found
        - A list of dictionaries if multiple JSON objects are found
        - An empty list if no valid JSON is found

    Examples:
        >>> to_json('{"key": "value"}')
        {'key': 'value'}

        >>> to_json('''
        ... ```json
        ... {"key": "value"}
        ... ```
        ... ''')
        {'key': 'value'}

        >>> to_json('''
        ... ```json
        ... {"key1": "value1"}
        ... ```
        ... ```json
        ... {"key2": "value2"}
        ... ```
        ... ''')
        [{'key1': 'value1'}, {'key2': 'value2'}]
    """

    if isinstance(string, list):
        string = "\n".join(string)

    # Try direct JSON parsing first
    try:
        if fuzzy_parse:
            return fuzzy_parse_json(string)
        return json.loads(string)
    except Exception:
        pass

    # Look for JSON in markdown code blocks
    pattern = r"```json\s*(.*?)\s*```"
    matches = re.findall(pattern, string, re.DOTALL)

    if not matches:
        return []

    if len(matches) == 1:
        return json.loads(matches[0])

    if fuzzy_parse:
        return [fuzzy_parse_json(match) for match in matches]
    return [json.loads(match) for match in matches]
