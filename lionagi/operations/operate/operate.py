import logging
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, JsonValue

from lionagi.operatives.models.field_model import FieldModel
from lionagi.operatives.models.model_params import ModelParams
from lionagi.operatives.types import Instruct, Operative, Step, ToolRef
from lionagi.protocols.types import Instruction, Progression, SenderRecipient
from lionagi.service import iModel

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def operate(
    branch: Branch,
    *,
    instruct: Instruct = None,
    instruction: Instruction | JsonValue = None,
    guidance: JsonValue = None,
    context: JsonValue = None,
    sender: SenderRecipient = None,
    recipient: SenderRecipient = None,
    progression: Progression = None,
    imodel: iModel = None,  # deprecated, alias of chat_model
    chat_model: iModel = None,
    invoke_actions: bool = True,
    tool_schemas: list[dict] = None,
    images: list = None,
    image_detail: Literal["low", "high", "auto"] = None,
    parse_model: iModel = None,
    skip_validation: bool = False,
    tools: ToolRef = None,
    operative: Operative = None,
    response_format: type[BaseModel] = None,  # alias of operative.request_type
    return_operative: bool = False,
    actions: bool = False,
    reason: bool = False,
    action_kwargs: dict = None,
    field_models: list[FieldModel] = None,
    exclude_fields: list | dict | None = None,
    request_params: ModelParams = None,
    request_param_kwargs: dict = None,
    response_params: ModelParams = None,
    response_param_kwargs: dict = None,
    handle_validation: Literal[
        "raise", "return_value", "return_none"
    ] = "return_value",
    operative_model: type[BaseModel] = None,
    request_model: type[BaseModel] = None,
    **kwargs,
) -> list | BaseModel | None | dict | str:
    """
    Orchestrates an "operate" flow with optional tool invocation and
    structured response validation.

    **Workflow**:
      1) Builds or updates an `Operative` object to specify how the LLM should respond.
      2) Sends an instruction (`instruct`) or direct `instruction` text to `branch.chat()`.
      3) Optionally validates/parses the result into a model or dictionary.
      4) If `invoke_actions=True`, any requested tool calls are automatically invoked.
      5) Returns either the final structure, raw response, or an updated `Operative`.

    Args:
        branch (Branch):
            The active branch that orchestrates messages, models, and logs.
        instruct (Instruct, optional):
            Contains the instruction, guidance, context, etc. If not provided,
            uses `instruction`, `guidance`, `context` directly.
        instruction (Instruction | JsonValue, optional):
            The main user instruction or content for the LLM.
        guidance (JsonValue, optional):
            Additional system or user instructions.
        context (JsonValue, optional):
            Extra context data.
        sender (SenderRecipient, optional):
            The sender ID for newly added messages.
        recipient (SenderRecipient, optional):
            The recipient ID for newly added messages.
        progression (Progression, optional):
            Custom ordering of conversation messages.
        imodel (iModel, deprecated):
            Alias of `chat_model`.
        chat_model (iModel, optional):
            The LLM used for the main chat operation. Defaults to `branch.chat_model`.
        invoke_actions (bool, optional):
            If `True`, executes any requested tools found in the LLM's response.
        tool_schemas (list[dict], optional):
            Additional schema definitions for tool-based function-calling.
        images (list, optional):
            Optional images appended to the LLM context.
        image_detail (Literal["low","high","auto"], optional):
            The level of image detail, if relevant.
        parse_model (iModel, optional):
            Model used for deeper or specialized parsing, if needed.
        skip_validation (bool, optional):
            If `True`, bypasses final validation and returns raw text or partial structure.
        tools (ToolRef, optional):
            Tools to be registered or made available if `invoke_actions` is True.
        operative (Operative, optional):
            If provided, reuses an existing operative's config for parsing/validation.
        response_format (type[BaseModel], optional):
            Expected Pydantic model for the final response (alias for `operative.request_type`).
        return_operative (bool, optional):
            If `True`, returns the entire `Operative` object after processing
            rather than the structured or raw output.
        actions (bool, optional):
            If `True`, signals that function-calling or "action" usage is expected.
        reason (bool, optional):
            If `True`, signals that the LLM should provide chain-of-thought or reasoning (where applicable).
        action_kwargs (dict | None, optional):
            Additional parameters for the `branch.act()` call if tools are invoked.
        field_models (list[FieldModel] | None, optional):
            Field-level definitions or overrides for the model schema.
        exclude_fields (list|dict|None, optional):
            Which fields to exclude from final validation or model building.
        request_params (ModelParams | None, optional):
            Extra config for building the request model in the operative.
        request_param_kwargs (dict|None, optional):
            Additional kwargs passed to the `ModelParams` constructor for the request.
        response_params (ModelParams | None, optional):
            Config for building the response model after actions.
        response_param_kwargs (dict|None, optional):
            Additional kwargs passed to the `ModelParams` constructor for the response.
        handle_validation (Literal["raise","return_value","return_none"], optional):
            How to handle parsing failures (default: "return_value").
        operative_model (type[BaseModel], deprecated):
            Alias for `response_format`.
        request_model (type[BaseModel], optional):
            Another alias for `response_format`.
        **kwargs:
            Additional keyword arguments passed to the LLM via `branch.chat()`.

    Returns:
        list | BaseModel | None | dict | str:
            - The parsed or raw response from the LLM,
            - `None` if validation fails and `handle_validation='return_none'`,
            - or the entire `Operative` object if `return_operative=True`.

    Raises:
        ValueError:
            - If both `operative_model` and `response_format` or `request_model` are given.
            - If the LLM's response cannot be parsed into the expected format and `handle_validation='raise'`.
    """
    if operative_model:
        logging.warning(
            "`operative_model` is deprecated. Use `response_format` instead."
        )
    if (
        (operative_model and response_format)
        or (operative_model and request_model)
        or (response_format and request_model)
    ):
        raise ValueError(
            "Cannot specify both `operative_model` and `response_format` (or `request_model`) "
            "as they are aliases of each other."
        )

    # Use the final chosen format
    response_format = response_format or operative_model or request_model

    # Decide which chat model to use
    chat_model = chat_model or imodel or branch.chat_model
    parse_model = parse_model or chat_model

    # Convert dict-based instructions to Instruct if needed
    if isinstance(instruct, dict):
        instruct = Instruct(**instruct)

    # Or create a new Instruct if not provided
    instruct = instruct or Instruct(
        instruction=instruction,
        guidance=guidance,
        context=context,
    )

    # If reason or actions are requested, apply them to instruct
    if reason:
        instruct.reason = True
    if actions:
        instruct.actions = True

    # 1) Create or update the Operative
    operative = Step.request_operative(
        request_params=request_params,
        reason=instruct.reason,
        actions=instruct.actions,
        exclude_fields=exclude_fields,
        base_type=response_format,
        field_models=field_models,
        **(request_param_kwargs or {}),
    )

    # If the instruction signals actions, ensure tools are provided
    if instruct.actions:
        tools = tools or True

    # If we want to auto-invoke tools, fetch or generate the schemas
    if invoke_actions and tools:
        tool_schemas = branch.acts.get_tool_schema(tools=tools)

    # 2) Send the instruction to the chat model
    ins, res = await branch.chat(
        instruction=instruct.instruction,
        guidance=instruct.guidance,
        context=instruct.context,
        sender=sender,
        recipient=recipient,
        response_format=operative.request_type,
        progression=progression,
        imodel=chat_model,  # or the override
        images=images,
        image_detail=image_detail,
        tool_schemas=tool_schemas,
        **kwargs,
    )
    branch.msgs.add_message(instruction=ins)
    branch.msgs.add_message(assistant_response=res)

    # 3) Populate the operative with the raw response
    operative.response_str_dict = res.response

    # 4) Possibly skip validation
    if skip_validation:
        return operative if return_operative else operative.response_str_dict

    # 5) Parse or validate the response into the operative’s model
    response_model = operative.update_response_model(res.response)
    if not isinstance(response_model, BaseModel):
        # If the response isn't directly a model, attempt a parse
        response_model = await branch.parse(
            text=res.response,
            request_type=operative.request_type,
            max_retries=operative.max_retries,
            handle_validation="return_value",
        )
        operative.response_model = operative.update_response_model(
            text=response_model
        )

    # If we still fail to parse, handle according to user preference
    if not isinstance(response_model, BaseModel):
        match handle_validation:
            case "return_value":
                return response_model
            case "return_none":
                return None
            case "raise":
                raise ValueError(
                    "Failed to parse the LLM response into the requested format."
                )

    # 6) If no tool invocation is needed, return result or operative
    if not invoke_actions:
        return operative if return_operative else operative.response_model

    # 7) If the model indicates an action is required, call the tools
    if (
        getattr(response_model, "action_required", None) is True
        and getattr(response_model, "action_requests", None) is not None
    ):
        action_response_models = await branch.act(
            response_model.action_requests,
            **(action_kwargs or {}),
        )
        # Possibly refine the operative with the tool outputs
        operative = Step.respond_operative(
            response_params=response_params,
            operative=operative,
            additional_data={"action_responses": action_response_models},
            **(response_param_kwargs or {}),
        )

    # Return final result or the full operative
    return operative if return_operative else operative.response_model
