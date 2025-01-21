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
    instruction = """
You are given a user's raw instruction or question. Your task is to rewrite it into a clearer, more structured prompt for an LLM or system, making any implicit or missing details explicit. 

Follow these guidelines:

1. **Dissect the user's request**:
   - If the user references a local file, note it clearly (e.g., "paper_file_path": "…").
   - If the user might need external references or up-to-date data, mention that possibility.
   - If the user's question is ambiguous, propose clarifications.
   
2. **Be explicit about the user's final objective**:
   - For example, if the user wants a comparison with other works, add that as a bullet point or sub-question.
   - If the user wants a summary plus code snippet, highlight that in your structured prompt.

3. **Do NOT produce final system actions**:
   - You're not calling any tools directly here; only rewriting the user query to reflect potential next steps.
   - If the user's request might require searching or doc reading, note it as an *option*, e.g. "Potential tool usage: {search, partial doc read}."

4. **Return only the improved user prompt**:
   - The final output should be a single text block or short JSON specifying the clarified user request.
   - Keep it concise yet thorough.

For instance, if the user's original text is:
"Please read my local PDF on RL and compare it to the newest research methods from exa or perplexity."

A re-written version might be:
"**Task**: 
- Summarize the local PDF (paper_file_path: 'myRLpaper.pdf'). 
- Compare its approach with recent reinforcement learning research found via exa/perplexity searches.
**Potential Tool Usage**: 
- Doc reading (reader_tool)
- External search (search_exa, search_perplexity)
**Output**: 
- A structured summary + comparative analysis."

Now, apply this rewriting to the input below. Return only the re-written prompt.
        """
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

    refined_prompt = await branch.chat(
        context=context,
        **kwargs,
    )
    return str(refined_prompt)
