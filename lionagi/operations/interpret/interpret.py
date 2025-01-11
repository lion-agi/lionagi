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
    """
    Interprets (rewrites) a user's raw input into a more formal or structured
    LLM prompt. This function can be seen as a "prompt translator," which
    ensures the user's original query is clarified or enhanced for better
    LLM responses.

    The method calls `branch.communicate()` behind the scenes with a system prompt
    that instructs the LLM to rewrite the input. You can provide additional
    parameters in `**kwargs` (e.g., `parse_model`, `skip_validation`, etc.)
    if you want to shape how the rewriting is done.

    Args:
        branch (Branch):
            The active branch context for messages, logging, etc.
        text (str):
            The raw user input or question that needs interpreting.
        domain (str | None, optional):
            Optional domain hint (e.g. "finance", "marketing", "devops").
            The LLM can use this hint to tailor its rewriting approach.
        style (str | None, optional):
            Optional style hint (e.g. "concise", "detailed").
        **kwargs:
            Additional arguments passed to `branch.communicate()`,
            such as `parse_model`, `skip_validation`, `temperature`, etc.

    Returns:
        str:
            A refined or "improved" user prompt string, suitable for feeding
            back into the LLM as a clearer instruction.

    Example:
        refined = await interpret(
            branch=my_branch, text="How do I do marketing analytics?",
            domain="marketing", style="detailed"
        )
        # refined might be "Explain step-by-step how to set up a marketing analytics
        #  pipeline to track campaign performance..."
    """
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

    refined_prompt = await branch.communicate(
        instruction=instruction,
        guidance=guidance,
        context=context,
        skip_validation=True,
        **kwargs,
    )
    return str(refined_prompt)
