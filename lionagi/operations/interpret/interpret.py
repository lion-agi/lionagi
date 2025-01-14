# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
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
    **kwargs,
) -> str:
    instruction = (
        "Rewrite the following user input into a clear, structured prompt or "
        "query for an LLM, ensuring any implicit details are made explicit. "
        "Return only the improved user prompt."
    )
    guidance = (
        f"Domain hint: {domain or 'general'}. "
        f"Desired style: {style or 'concise'}. "
        "You can add or clarify context if needed."
    )
    context = [f"User input: {text}"]

    # Default temperature if none provided
    kwargs["temperature"] = kwargs.get("temperature", 0.1)

    refined_prompt = await branch.chat(
        instruction=instruction,
        guidance=guidance,
        context=context,
        **kwargs,
    )
    return str(refined_prompt)
