def to_readable_dict(input_: Any, /) -> str:
    """Converts a given input to a readable dictionary format.

    Args:
        input_ (Any): The input data to convert.

    Returns:
        str: A JSON string representation of the input dictionary.

    Raises:
        ValueError: If the input cannot be converted to a dictionary.
    """
    try:
        dict_ = to_dict(input_)
        return json.dumps(dict_, indent=4) if isinstance(dict_, dict) else str(dict_)
    except Exception as e:
        raise ValueError(f"Could not convert given input to readable dict: {e}") from e
