from lionagi.libs.ln_convert import strip_lower

from typing_extensions import deprecated

from lionagi.os.sys_utils import format_deprecated_msg


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.action.function_calling.FunctionCalling",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
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
