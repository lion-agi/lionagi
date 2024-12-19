import contextlib
import json
import re
from typing import Any


def fuzzy_parse_json(
    str_to_parse: str, /
) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Attempt to parse a JSON string, trying a few minimal "fuzzy" fixes if needed.

    Steps:
    1. Parse directly with json.loads.
    2. Replace single quotes with double quotes, normalize spacing, and try again.
    3. Attempt to fix unmatched brackets using fix_json_string.
    4. If all fail, raise ValueError.

    Args:
        str_to_parse: The JSON string to parse

    Returns:
        Parsed JSON (dict or list of dicts)

    Raises:
        ValueError: If the string cannot be parsed as valid JSON
        TypeError: If the input is not a string
    """
    _check_valid_str(str_to_parse)

    # 1. Direct attempt
    with contextlib.suppress(Exception):
        return json.loads(str_to_parse)

    # 2. Try cleaning: replace single quotes with double and normalize
    cleaned = _clean_json_string(str_to_parse.replace("'", '"'))
    with contextlib.suppress(Exception):
        return json.loads(cleaned)

    # 3. Try fixing brackets
    fixed = fix_json_string(cleaned)
    with contextlib.suppress(Exception):
        return json.loads(fixed)

    # If all attempts fail
    raise ValueError("Invalid JSON string")


def _check_valid_str(str_to_parse: str, /):
    if not isinstance(str_to_parse, str):
        raise TypeError("Input must be a string")
    if not str_to_parse.strip():
        raise ValueError("Input string is empty")


def _clean_json_string(s: str) -> str:
    """Basic normalization: replace unescaped single quotes, trim spaces, ensure keys are quoted."""
    # Replace unescaped single quotes with double quotes
    # '(?<!\\)'" means a single quote not preceded by a backslash
    s = re.sub(r"(?<!\\)'", '"', s)
    # Collapse multiple whitespaces
    s = re.sub(r"\s+", " ", s)
    # Ensure keys are quoted
    # This attempts to find patterns like { key: value } and turn them into {"key": value}
    s = re.sub(r'([{,])\s*([^"\s]+)\s*:', r'\1"\2":', s)
    return s.strip()


def fix_json_string(str_to_parse: str, /) -> str:
    """Try to fix JSON string by ensuring brackets are matched properly."""
    if not str_to_parse:
        raise ValueError("Input string is empty")

    brackets = {"{": "}", "[": "]"}
    open_brackets = []
    pos = 0
    length = len(str_to_parse)

    while pos < length:
        char = str_to_parse[pos]

        if char == "\\":
            pos += 2  # Skip escaped chars
            continue

        if char == '"':
            pos += 1
            # skip string content
            while pos < length:
                if str_to_parse[pos] == "\\":
                    pos += 2
                    continue
                if str_to_parse[pos] == '"':
                    pos += 1
                    break
                pos += 1
            continue

        if char in brackets:
            open_brackets.append(brackets[char])
        elif char in brackets.values():
            if not open_brackets:
                # Extra closing bracket
                # Better to raise error than guess
                raise ValueError("Extra closing bracket found.")
            if open_brackets[-1] != char:
                # Mismatched bracket
                raise ValueError("Mismatched brackets.")
            open_brackets.pop()

        pos += 1

    # Add missing closing brackets if any
    if open_brackets:
        str_to_parse += "".join(reversed(open_brackets))

    return str_to_parse
