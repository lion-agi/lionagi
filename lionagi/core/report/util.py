from lionagi.libs import convert


system_fields = [
    "ln_id",
    "timestamp",
    "metadata",
    "meta",
    "extra_fields",
    "content",
    "created",
    "form",
    "report",
    "work",
    "assignment",
    "assignments",
    "input_fields",
    "requested_fields",
    "instruction",
    "system",
]


def get_input_output_fields(str_: str) -> list[list[str]]:

    inputs, outputs = str_.split("->")

    input_fields = [convert.strip_lower(i) for i in inputs.split(",")]
    requested_fields = [convert.strip_lower(o) for o in outputs.split(",")]

    return input_fields, requested_fields
