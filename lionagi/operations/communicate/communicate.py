# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import TYPE_CHECKING

from lionagi.libs.validate.fuzzy_validate_mapping import fuzzy_validate_mapping
from lionagi.utils import UNDEFINED

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def communicate(
    branch: "Branch",
    instruction=None,
    *,
    guidance=None,
    context=None,
    plain_content=None,
    sender=None,
    recipient=None,
    progression=None,
    request_model=None,
    response_format=None,
    request_fields=None,
    imodel=None,
    chat_model=None,
    parse_model=None,
    skip_validation=False,
    images=None,
    image_detail="auto",
    num_parse_retries=3,
    fuzzy_match_kwargs=None,
    clear_messages=False,
    operative_model=None,
    include_token_usage_to_model: bool = False,
    **kwargs,
):
    if operative_model:
        logging.warning(
            "operative_model is deprecated. Use response_format instead."
        )
    if (
        (operative_model and response_format)
        or (operative_model and request_model)
        or (response_format and request_model)
    ):
        raise ValueError(
            "Cannot specify both operative_model and response_format"
            "or operative_model and request_model as they are aliases"
            "for the same parameter."
        )

    response_format = response_format or operative_model or request_model

    imodel = imodel or chat_model or branch.chat_model
    parse_model = parse_model or branch.parse_model

    if clear_messages:
        branch.msgs.clear_messages()

    if num_parse_retries > 5:
        logging.warning(
            f"Are you sure you want to retry {num_parse_retries} "
            "times? lowering retry attempts to 5. Suggestion is under 3"
        )
        num_parse_retries = 5

    ins, res = await branch.chat(
        instruction=instruction,
        guidance=guidance,
        context=context,
        sender=sender,
        recipient=recipient,
        response_format=response_format,
        progression=progression,
        imodel=imodel,
        images=images,
        image_detail=image_detail,
        plain_content=plain_content,
        return_ins_res_message=True,
        include_token_usage_to_model=include_token_usage_to_model,
        **kwargs,
    )
    branch.msgs.add_message(instruction=ins)
    branch.msgs.add_message(assistant_response=res)

    if skip_validation:
        return res.response

    if response_format is not None:
        return await branch.parse(
            text=res.response,
            request_type=response_format,
            max_retries=num_parse_retries,
            **(fuzzy_match_kwargs or {}),
        )

    if request_fields is not None:
        _d = fuzzy_validate_mapping(
            res.response,
            request_fields,
            handle_unmatched="force",
            fill_value=UNDEFINED,
        )
        return {k: v for k, v in _d.items() if v != UNDEFINED}

    return res.response
