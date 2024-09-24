"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Module for parsing chat completions and model responses in Lion framework.

Provides functionality to parse and process chat completions and model
responses, including handling of various JSON and XML formats.
"""

import re
from typing import Any

from lion_core.libs import (
    to_dict,
    validate_mapping,
    fuzzy_parse_json,
    md_to_json,
    extract_json_block,
)
from lionagi.core.generic.model import iModel
from lion_core.session.branch import Branch


async def process_chatcompletion(
    branch: Branch,
    imodel: iModel | None,
    payload: dict,
    completion: dict,
    sender: str,
    costs: tuple[float, float] | None = None,
) -> Any:
    """
    Parse chat completion and update the branch with the response.

    Args:
        branch: The Branch object to update.
        imodel: The iModel object to use for status updates.
        payload: The payload dictionary.
        completion: The completion dictionary from the AI model.
        sender: The sender of the message.
        costs: A tuple of prompt and completion token costs.

    Returns:
        The processed message or None.
    """
    message = None
    imodel = imodel or branch.imodel

    if "choices" in completion:
        payload.pop("messages", None)
        branch.update_last_instruction_meta(payload)
        _choices = completion.pop("choices", None)

        def process_completion_choice(
            choice: dict, c_: tuple[float, float] | None
        ) -> Any:
            if isinstance(choice, dict):
                msg = choice.pop("message", None)
                _completion = completion.copy()
                _completion.update(choice)
                branch.add_message(
                    assistant_response=msg,
                    metadata=_completion,
                    sender=sender,
                )
            a = branch.messages[-1].metadata.get(
                ["extra", "usage", "prompt_tokens"],
                0,
            )
            b = branch.messages[-1].metadata.get(
                ["extra", "usage", "completion_tokens"],
                0,
            )
            m = completion.get("model")
            if m and c_:
                ttl = (a * c_[0] + b * c_[1]) / 1_000_000
                branch.messages[-1].metadata.insert(["extra", "usage", "expense"], ttl)
            return msg

        if _choices and not isinstance(_choices, list):
            _choices = [_choices]

        if _choices and isinstance(_choices, list):
            for _choice in _choices:
                message = process_completion_choice(_choice, c_=costs)

    return message


def process_model_response(
    content_: dict | str,
    request_fields: dict,
    fill_value: Any = None,
    fill_mapping: dict[str, Any] | None = None,
    strict: bool = False,
    handle_unmatched="ignore",
) -> dict | str:
    """
    Parse the response from the AI model into dictionary format if possible.

    Args:
        content_: The content to parse, either a dictionary or a string.
        request_fields: The fields requested in the response.
        fill_value: The value to use for missing fields.
        fill_mapping: A mapping of field names to fill values.
        strict: Whether to use strict parsing.

    Returns:
        The parsed content as a dictionary or the original string if parsing
        fails.
    """
    out_ = content_.get("content", "") if isinstance(content_, dict) else content_

    if isinstance(out_, str):
        parsing_methods = [
            lambda x: to_dict(
                x,
                str_type="json",
                parser=md_to_json,
                suppress=True,
            ),
            lambda x: to_dict(
                x,
                str_type="json",
                parser=fuzzy_parse_json,
                suppress=True,
            ),
            lambda x: to_dict(
                x,
                str_type="json",
                parser=extract_json_block,
                suppress=True,
            ),
            lambda x: to_dict(
                x,
                str_type="xml",
                suppress=True,
            ),
            lambda x: fuzzy_parse_json(
                str_to_parse=re.search(
                    pattern=r"```json\n({.*?})\n```",
                    string=x,
                    flags=re.DOTALL,
                ).group(1),
                suppress=True,
            ),
            lambda x: to_dict(
                re.search(
                    pattern=r"```xml\n({.*?})\n```",
                    string=x,
                    flags=re.DOTALL,
                ).group(1),
                str_type="xml",
                suppress=True,
            ),
            lambda x: fuzzy_parse_json(
                str_to_parse=x.replace("'", '"'),
                suppress=True,
            ),
        ]

        for method in parsing_methods:
            if a_ := method(out_):
                out_ = a_
                break

    if isinstance(out_, dict) and request_fields:
        return validate_mapping(
            out_,
            request_fields,
            score_func=None,
            fuzzy_match=True,
            handle_unmatched=handle_unmatched,
            fill_value=fill_value,
            fill_mapping=fill_mapping,
            strict=strict,
        )
    return out_


async def fallback_structure_model_response(
    content_: dict | str,
    request_fields: dict,
    imodel: iModel,
    fill_value: Any = None,
    fill_mapping: dict[str, Any] | None = None,
    strict: bool = False,
    handle_unmatched="ignore",
    **kwargs,
):
    structured = await imodel.structure(content_, **kwargs)
    return process_model_response(
        content_=structured,
        request_fields=request_fields,
        fill_value=fill_value,
        fill_mapping=fill_mapping,
        strict=strict,
        handle_unmatched=handle_unmatched,
    )


__all__ = ["process_chatcompletion", "process_model_response"]

# File: lion_core/chat/parsing.py
