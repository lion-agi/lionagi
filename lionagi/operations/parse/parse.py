# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel

from lionagi.libs.validate.fuzzy_validate_mapping import fuzzy_validate_mapping
from lionagi.operatives.types import Operative
from lionagi.utils import breakdown_pydantic_annotation

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def parse(
    branch: "Branch",
    text: str,
    handle_validation: Literal[
        "raise", "return_value", "return_none"
    ] = "return_value",
    max_retries: int = 3,
    request_type: type[BaseModel] = None,
    operative: Operative = None,
    similarity_algo="jaro_winkler",
    similarity_threshold: float = 0.85,
    fuzzy_match: bool = True,
    handle_unmatched: Literal[
        "ignore", "raise", "remove", "fill", "force"
    ] = "force",
    fill_value: Any = None,
    fill_mapping: dict[str, Any] | None = None,
    strict: bool = False,
    suppress_conversion_errors: bool = False,
):
    """Attempts to parse text into a structured Pydantic model.

    Uses optional fuzzy matching to handle partial or unclear fields.

    Args:
        text (str): The raw text to parse.
        handle_validation (Literal["raise","return_value","return_none"]):
            What to do if parsing fails. Defaults to "return_value".
        max_retries (int):
            How many times to retry parsing if it fails.
        request_type (type[BaseModel], optional):
            The Pydantic model to parse into.
        operative (Operative, optional):
            If provided, uses its model and max_retries setting.
        similarity_algo (str):
            The similarity algorithm for fuzzy field matching.
        similarity_threshold (float):
            A threshold for fuzzy matching (0.0 - 1.0).
        fuzzy_match (bool):
            If True, tries to match unrecognized keys to known ones.
        handle_unmatched (Literal["ignore","raise","remove","fill","force"]):
            How to handle unmatched fields.
        fill_value (Any):
            A default value used when fill is needed.
        fill_mapping (dict[str, Any] | None):
            A mapping from field -> fill value override.
        strict (bool):
            If True, raises errors on ambiguous fields or data types.
        suppress_conversion_errors (bool):
            If True, logs or ignores errors during data conversion.

    Returns:
        BaseModel | Any | None:
            The parsed model instance, or a dict/string/None depending
            on the handling mode.
    """
    _should_try = True
    num_try = 0
    response_model = text
    if operative is not None:
        max_retries = operative.max_retries
        request_type = operative.request_type

    while (
        _should_try
        and num_try < max_retries
        and not isinstance(response_model, BaseModel)
    ):
        num_try += 1
        _, res = await branch.chat(
            instruction="reformat text into specified model",
            guidane="follow the required response format, using the model schema as a guide",
            context=[{"text_to_format": text}],
            response_format=request_type,
            sender=branch.user,
            recipient=branch.id,
            imodel=branch.parse_model,
        )
        if operative is not None:
            response_model = operative.update_response_model(res.response)
        else:
            response_model = fuzzy_validate_mapping(
                res.response,
                breakdown_pydantic_annotation(request_type),
                similarity_algo=similarity_algo,
                similarity_threshold=similarity_threshold,
                fuzzy_match=fuzzy_match,
                handle_unmatched=handle_unmatched,
                fill_value=fill_value,
                fill_mapping=fill_mapping,
                strict=strict,
                suppress_conversion_errors=suppress_conversion_errors,
            )
            response_model = request_type.model_validate(response_model)

    if not isinstance(response_model, BaseModel):
        match handle_validation:
            case "return_value":
                return response_model
            case "return_none":
                return None
            case "raise":
                raise ValueError(
                    "Failed to parse response into request format"
                )

    return response_model
