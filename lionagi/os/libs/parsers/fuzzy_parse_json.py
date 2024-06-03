from json import loads


def fuzzy_parse_json(str_to_parse: str) -> dict:
    """
    Attempt to parse a JSON string, applying fixes for common issues.

    This function tries to parse the given JSON string using the `loads`
    function from the `json` module. If the initial parsing fails, it
    attempts to fix common formatting issues in the JSON string using the
    `fix_json_string` function and then tries parsing again. If the JSON
    string contains single quotes, they are replaced with double quotes
    before making a final attempt to parse the string.

    Args:
        str_to_parse: The JSON string to parse.

    Returns:
        The parsed JSON object as a dictionary.

    Raises:
        ValueError: If the JSON string cannot be parsed even after
            attempts to fix it.

    Example:
        >>> fuzzy_parse_json('{"key": "value"}')
        {'key': 'value'}
    """
    try:
        return loads(str_to_parse)
    except Exception:
        fixed_str = fix_json_string(str_to_parse)
        try:
            return loads(fixed_str)
        except Exception:
            try:
                fixed_str = fixed_str.replace("'", '"')
                return loads(fixed_str)
            except Exception as e:
                raise ValueError(
                    f"Failed to parse JSON after fixing attempts: {e}"
                ) from e


def fix_json_string(str_to_parse: str) -> str:
    """
    Fix a JSON string by ensuring all brackets are properly closed.

    This function iterates through the characters of the JSON string and
    keeps track of the opening brackets encountered. If a closing bracket
    is found without a matching opening bracket or if there are extra
    closing brackets, a ValueError is raised. Any remaining opening
    brackets at the end of the string are closed with their corresponding
    closing brackets.

    Args:
        str_to_parse: The JSON string to fix.

    Returns:
        The fixed JSON string with properly closed brackets.

    Raises:
        ValueError: If mismatched or extra closing brackets are found.

    Example:
        >>> fix_json_string('{"key": "value"')
        '{"key": "value"}'
    """
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
