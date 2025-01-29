# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def interpret(
    branch: "Branch",
    text: str,
    domain: str | None = None,
    style: str | None = None,
    sample_writing: str | None = None,
    interpret_model: str | None = None,
    **kwargs,
) -> str:
    instruction = (
        "You are given a user's raw instruction or question. Your task is to rewrite it into a clearer,"
        "more structured prompt for an LLM or system, making any implicit or missing details explicit. "
        "Return only the re-written prompt. Do not assume any details not mentioned in the input, nor "
        "give additional instruction than what is explicitly stated."
    )
    guidance = (
        f"Domain hint: {domain or 'general'}. "
        f"Desired style: {style or 'concise'}. "
    )
    if sample_writing:
        guidance += f" Sample writing: {sample_writing}"

    context = [f"User input: {text}"]

    # Default temperature if none provided
    kwargs["guidance"] = guidance + "\n" + kwargs.get("guidance", "")
    kwargs["instruction"] = instruction + "\n" + kwargs.get("instruction", "")
    kwargs["temperature"] = kwargs.get("temperature", 0.1)
    if interpret_model:
        kwargs["chat_model"] = interpret_model

    refined_prompt = await branch.chat(
        context=context,
        **kwargs,
    )
    return str(refined_prompt)
