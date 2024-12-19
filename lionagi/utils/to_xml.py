from typing import Any


def to_xml(
    obj: dict | list | str | int | float | bool | None,
    root_name: str = "root",
) -> str:
    """
    Convert a dictionary into an XML formatted string.

    Rules:
    - A dictionary key becomes an XML tag.
    - If the dictionary value is:
      - A primitive type (str, int, float, bool, None): it becomes the text content of the tag.
      - A list: each element of the list will repeat the same tag.
      - Another dictionary: it is recursively converted to nested XML.
    - root_name sets the top-level XML element name.

    Args:
        obj: The Python object to convert (typically a dictionary).
        root_name: The name of the root XML element.

    Returns:
        A string representing the XML.

    Examples:
        >>> to_xml({"a": 1, "b": {"c": "hello", "d": [10, 20]}}, root_name="data")
        '<data><a>1</a><b><c>hello</c><d>10</d><d>20</d></b></data>'
    """

    def _convert(value: Any, tag_name: str) -> str:
        # If value is a dict, recursively convert its keys
        if isinstance(value, dict):
            inner = "".join(_convert(v, k) for k, v in value.items())
            return f"<{tag_name}>{inner}</{tag_name}>"
        # If value is a list, repeat the same tag for each element
        elif isinstance(value, list):
            return "".join(_convert(item, tag_name) for item in value)
        # If value is a primitive, convert to string and place inside tag
        else:
            text = "" if value is None else str(value)
            # Escape special XML characters if needed (minimal)
            text = (
                text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;")
            )
            return f"<{tag_name}>{text}</{tag_name}>"

    # If top-level obj is not a dict, wrap it in one
    if not isinstance(obj, dict):
        obj = {root_name: obj}

    inner_xml = "".join(_convert(v, k) for k, v in obj.items())
    return f"<{root_name}>{inner_xml}</{root_name}>"
