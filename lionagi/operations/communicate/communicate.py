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
    **kwargs,
):
    """
    Simplified version of the chat flow without advanced tool invocation or
    multi-step chaining.

    - Calls `branch.chat()`.
    - (Optionally) parses the response using `branch.parse()` if a model is provided.

    Args:
        branch (Branch): The active branch context.
        instruction (Any): Main user prompt or instruction.
        guidance (Any): Additional system or user guidance text.
        context (Any): Context data or disclaimers to pass.
        plain_content (str): Additional plain text appended to the instruction.
        sender (Any): The sender ID for the message.
        recipient (Any): The recipient ID for the message.
        progression (Any): Custom conversation order.
        request_model (type[BaseModel]|BaseModel, optional): Expected structure for the response.
        response_format (type[BaseModel], optional): Alias for request_model.
        request_fields (dict|list[str], optional): Keys to extract from the response if no model used.
        imodel (iModel, optional): Deprecated alias for chat_model.
        chat_model (iModel, optional): The LLM used to handle conversation.
        parse_model (iModel, optional): The LLM for parsing if needed.
        skip_validation (bool, optional): If True, return raw text from LLM.
        images (list, optional): A list of images.
        image_detail (str, optional): "low", "high", or "auto".
        num_parse_retries (int, optional): Max times to re-parse if it fails.
        fuzzy_match_kwargs (dict, optional): Options for fuzzy field matching.
        clear_messages (bool, optional): If True, clears existing messages.
        operative_model (type[BaseModel], optional): Deprecated alias for response_format.
        **kwargs: Additional arguments for the underlying LLM call.

    Returns:
        Any: The final LLM response as raw text, dict of requested fields,
             or a validated Pydantic model, depending on params.
    """
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
