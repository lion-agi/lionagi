# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

RESTRICTED_FIELDS = {
    "input_fields",
    "request_fields",
    "init_input_kwargs",
    "output_fields",
}


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
