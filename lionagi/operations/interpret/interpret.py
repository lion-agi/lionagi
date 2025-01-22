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
    sample_writing: str | None = None,
    **kwargs,
) -> str:
    instruction = "You are given a user's raw instruction or question. Rewrite it into a clearer prompt."
    guidance = (
        f"Domain hint: {domain or 'general'}. "
        f"Desired style: {style or 'concise'}. "
        "Guidelines:\n"
        "1) Identify local-file references or possible external data usage."
        "2) State final user objective explicitly."
        "3) No tool calls or system actions, only the improved query text."
        "4) Return only that improved user prompt as final."
    )
    if sample_writing:
        guidance += f" Sample writing: {sample_writing}"

    context = [f"User input: {text}"]

    # Default temperature if none provided
    refined_prompt = await branch.chat(
        instruction=instruction + "\n" + kwargs.get("instruction", ""),
        guidance=guidance + "\n" + kwargs.get("guidance", ""),
        context=context,
        temperature=kwargs.get("temperature", 0.2),
        **{
            k: v
            for k, v in kwargs.items()
            if k not in ("instruction", "guidance", "temperature", "context")
        },
    )

    return str(refined_prompt)
