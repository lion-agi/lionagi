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
    A simpler orchestration than `operate()`, typically without tool invocation.

    **Flow**:
        1. Sends an instruction (or conversation) to the chat model.
        2. Optionally parses the response into a structured model or fields.
        3. Returns either the raw string, the parsed model, or a dict of fields.

    Args:
        instruction (Instruction | dict, optional):
            The user's main query or data.
        guidance (JsonValue, optional):
            Additional instructions or context for the LLM.
        context (JsonValue, optional):
            Extra data or context.
        plain_content (str, optional):
            Plain text content appended to the instruction.
        sender (SenderRecipient, optional):
            Sender ID (defaults to `Branch.user`).
        recipient (SenderRecipient, optional):
            Recipient ID (defaults to `self.id`).
        progression (ID.IDSeq, optional):
            Custom ordering of messages.
        request_model (type[BaseModel] | BaseModel | None, optional):
            Model for validating or structuring the LLM's response.
        response_format (type[BaseModel], optional):
            Alias for `request_model`. If both are provided, raises ValueError.
        request_fields (dict|list[str], optional):
            If you only need certain fields from the LLM's response.
        imodel (iModel, optional):
            Deprecated alias for `chat_model`.
        chat_model (iModel, optional):
            An alternative to the default chat model.
        parse_model (iModel, optional):
            If parsing is needed, you can override the default parse model.
        skip_validation (bool, optional):
            If True, returns the raw response string unvalidated.
        images (list, optional):
            Any relevant images.
        image_detail (Literal["low","high","auto"], optional):
            Image detail level (if used).
        num_parse_retries (int, optional):
            Maximum parsing retries (capped at 5).
        fuzzy_match_kwargs (dict, optional):
            Additional settings for fuzzy field matching (if used).
        clear_messages (bool, optional):
            Whether to clear stored messages before sending.
        operative_model (type[BaseModel], optional):
            Deprecated, alias for `response_format`.
        **kwargs:
            Additional arguments for the underlying LLM call.

    Returns:
        Any:
            - Raw string (if `skip_validation=True`),
            - A validated Pydantic model,
            - A dict of the requested fields,
            - or `None` if parsing fails and `handle_validation='return_none'`.
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
