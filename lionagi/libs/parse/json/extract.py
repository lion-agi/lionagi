import re
from collections.abc import Callable
from typing import Any

from ..type_convert.to_dict import to_dict


def extract_json_blocks(
    str_to_parse: str,
    suppress: bool = True,
    fuzzy_parse: bool = True,
    dropna: bool = True,
) -> list[dict[str, Any]]:
    """
    Extract and parse JSON blocks from the given text.

    This function searches for JSON blocks enclosed in triple backticks
    within the input text, parses them, and returns a list of parsed
    dictionaries.

    Args:
        text: The input text containing JSON blocks.
        suppress: If True, suppress errors during parsing. Default is True.
        fuzzy_parse: If True, use fuzzy parsing for JSON. Default is True.
        dropna: If True, remove None values from the result. Default is True.

    Returns:
        A list of parsed JSON blocks as dictionaries.

    Example:
        >>> text = "```json\n{\"key\": \"value\"}\n```"
        >>> extract_json_blocks(text)
        [{'key': 'value'}]
    """
    pattern = r"```json\s*(.*?)\s*```"
    matches = re.findall(pattern, str_to_parse, re.DOTALL)

    json_blocks = [
        to_dict(match, fuzzy_parse=fuzzy_parse, suppress=suppress)
        for match in matches
    ]

    return [block for block in json_blocks if block] if dropna else json_blocks


def extract_block(
    str_to_parse: str,
    language: str = "json",
    regex_pattern: str | None = None,
    *,
    parser: Callable[[str], Any] | None = None,
    suppress: bool = False,
) -> dict[str, Any] | None:
    """
    Extract and parse a code block from the given string.

    This function searches for a code block in the input string using a
    regular expression pattern, extracts it, and parses it using the
    provided parser function.

    Args:
        str_to_parse: The input string containing the code block.
        language: The language of the code block. Default is "json".
        regex_pattern: Custom regex pattern to find the code block.
            If provided, overrides the default pattern.
        parser: A function to parse the extracted code string.
            If not provided, uses `to_dict` with fuzzy parsing.
        suppress: If True, return None instead of raising an error
            when no code block is found. Default is False.

    Returns:
        The parsed content of the code block as a dictionary,
        or None if no block is found and suppress is True.

    Raises:
        ValueError: If no code block is found and suppress is False.

    Example:
        >>> text = "```json\n{\"key\": \"value\"}\n```"
        >>> extract_block(text)
        {'key': 'value'}
    """
    if not regex_pattern:
        regex_pattern = rf"```{language}\n?(.*?)\n?```"
    if not language:
        regex_pattern = r"```\n?(.*?)\n?```"

    match = re.search(regex_pattern, str_to_parse, re.DOTALL)

    if match:
        code_str = match.group(1).strip()
    elif str_to_parse.startswith(f"```{language}\n") and str_to_parse.endswith(
        "\n```"
    ):
        code_str = str_to_parse[4 + len(language) : -4].strip()
    elif suppress:
        return None
    else:
        raise ValueError("No code block found in the input string.")

    parser = parser or (lambda x: to_dict(x, fuzzy_parse=True, suppress=True))
    return parser(code_str)
