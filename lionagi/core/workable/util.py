from lionagi.os.lib import strip_lower


def get_input_output_fields(str_: str) -> list[list[str]]:
    """
    Parses an assignment string to extract input and output fields.

    Args:
        str_ (str): The assignment string in the format 'inputs -> outputs'.

    Returns:
        list[list[str]]: A list containing two lists - one for input fields and one for requested fields.

    Raises:
        ValueError: If the assignment string is None or if it does not contain '->' indicating invalid format.
    """
    if str_ is None:
        return [], []

    if "->" not in str_:
        raise ValueError("Invalid assignment format. Expected 'inputs -> outputs'.")

    inputs, outputs = str_.split("->")

    input_fields = [strip_lower(i) for i in inputs.split(",")]
    requested_fields = [strip_lower(o) for o in outputs.split(",")]

    return input_fields, requested_fields
