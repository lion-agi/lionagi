from lionabc.exceptions import (
    LionOperationError,
    LionTypeError,
    LionValueError,
)

from lion_core.generic.note import note

RESTRICTED_FIELDS = {
    "input_fields",
    "request_fields",
    "init_input_kwargs",
    "output_fields",
}

_err_map = {
    "type": {
        "not_dict": lambda x: LionTypeError(
            message="Input should be a valid dictionary for init.",
            expected_type=dict,
            actual_type=type(x),
        ),
        "not_form_instance": lambda x: LionTypeError(
            message="Invalid form. Should be a instance of Form.",
            expected_type="Form",
            actual_type=type(x),
        ),
        "not_form_class": lambda x: LionTypeError(
            message="Invalid form class, must be a subclass of Form.",
            expected_type="Type[Form]",
            actual_type=type(x),
        ),
        "not_list": lambda x, y: LionTypeError(
            message=y,
            expected_type="list[str]",
            actual_type=type(x),
        ),
    },
    "assignment": {
        "no_assignment": LionValueError(
            "Please provide a valid assignment for this form.",
            "Example assignment: 'input1, input2 -> output'.",
        ),
        "invalid_assignment": lambda x: LionValueError(
            f"Invalid assignment. Field {x} is not found in the form."
        ),
        "explicit_task": LionValueError(
            "Explicitly defining task is not supported. "
            "Please use task_description.",
        ),
        "explcit_input": LionValueError(
            message=(
                "Explicitly defining input_fields is not supported. "
                "Please use assignment to indicate them."
            )
        ),
        "explcit_request": LionValueError(
            message=(
                "Explicitly defining request_fields is not supported. "
                "Please use assignment to indicate them."
            )
        ),
        "strict": lambda x: AttributeError(
            f"The form is set to strict_assignment. {x} "
            "should not be modified after init.",
        ),
        "strict_processed": LionOperationError(
            "The strict form has been processed, and cannot be worked on again"
        ),
        "missing_input": LionValueError(
            "Input fields are missing in the assignment.",
        ),
        "missing_request": LionValueError(
            "Request fields are missing in the assignment.",
        ),
        "incomplete_input": lambda x: LionOperationError(
            message=f"Input fields {x} are not completed.",
        ),
        "incomplete_request": lambda x: LionOperationError(
            message=f"Request fields {x} are not completed.",
        ),
    },
    "field": {
        "missing": lambda x: LionValueError(f"Field {x} is missing."),
        "error": lambda x: LionOperationError(f"Field operation failed: {x}"),
        "modify_input_request_list": LionValueError(
            "input_fields/request_fields list should not be modified"
            "directly. Please use append_to_input/append_to_request"
        ),
        "modify_restricted": lambda x: LionValueError(
            f"{x} should not be modified directly."
        ),
    },
}

ERR_MAP = note(**_err_map)


def get_input_output_fields(str_: str) -> tuple[list[str], list[str]]:
    if str_ is None:
        return [], []

    if "->" not in str_:
        raise ValueError(
            "Invalid assignment format. Expected 'inputs -> outputs'.",
        )

    inputs, outputs = str_.split("->")
    input_fields = [str(i).strip().lower() for i in inputs.split(",")]
    request_fields = [str(o).strip().lower() for o in outputs.split(",")]

    return input_fields, request_fields
