# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, Literal

import pandas as pd
from jinja2 import Template
from pydantic import BaseModel, Field, JsonValue, PrivateAttr

from lionagi.libs.validate.fuzzy_validate_mapping import fuzzy_validate_mapping
from lionagi.operatives.models.field_model import FieldModel
from lionagi.operatives.models.model_params import ModelParams
from lionagi.operatives.types import (
    ActionManager,
    ActionResponseModel,
    FunctionCalling,
    FuncTool,
    Instruct,
    Operative,
    Step,
    Tool,
    ToolRef,
)
from lionagi.protocols.types import (
    ID,
    MESSAGE_FIELDS,
    ActionRequest,
    ActionResponse,
    AssistantResponse,
    Communicatable,
    Element,
    IDType,
    Instruction,
    Log,
    LogManager,
    LogManagerConfig,
    Mail,
    Mailbox,
    MessageFlag,
    MessageManager,
    MessageRole,
    Package,
    PackageCategory,
    Pile,
    Progression,
    Relational,
    RoledMessage,
    SenderRecipient,
    System,
)
from lionagi.service import iModel, iModelManager
from lionagi.settings import Settings
from lionagi.utils import (
    UNDEFINED,
    alcall,
    breakdown_pydantic_annotation,
    copy,
)

__all__ = ("Branch",)


class Branch(Element, Communicatable, Relational):
    """Manages a conversation 'branch' with messages, tools, and iModels.

    The Branch class orchestrates message handling, model invocation,
    action (tool) execution, logging, and mailbox-based communication.
    It maintains references to a MessageManager, ActionManager, iModelManager,
    and a LogManager, providing high-level methods for combined operations.

    Attributes:
        user (SenderRecipient | None):
            The user or sender of this branch context (e.g., a session object).
        name (str | None):
            A human-readable name for this branch.
        mailbox (Mailbox):
            A mailbox for sending and receiving `Package`s to/from other
            branches or components.
    """

    user: SenderRecipient | None = Field(
        None,
        description=(
            "The user or sender of the branch, typically a session object or"
            "an external user identifier. Please note that this is a distinct"
            "concept from `user` parameter in LLM API calls."
        ),
    )

    name: str | None = Field(
        None,
        description="A human readable name of the branch, if any.",
    )

    mailbox: Mailbox = Field(default_factory=Mailbox, exclude=True)

    _message_manager: MessageManager | None = PrivateAttr(None)
    _action_manager: ActionManager | None = PrivateAttr(None)
    _imodel_manager: iModelManager | None = PrivateAttr(None)
    _log_manager: LogManager | None = PrivateAttr(None)

    def __init__(
        self,
        *,
        user: SenderRecipient = None,
        name: str | None = None,
        messages: Pile[RoledMessage] = None,  # message manager kwargs
        system: System | JsonValue = None,
        system_sender: SenderRecipient = None,
        chat_model: iModel = None,  # imodel manager kwargs
        parse_model: iModel = None,
        imodel: iModel = None,  # deprecated, alias of chat_model
        tools: FuncTool | list[FuncTool] = None,  # action manager kwargs
        log_config: LogManagerConfig | dict = None,  # log manager kwargs
        system_datetime: bool | str = None,
        system_template: Template | str = None,
        system_template_context: dict = None,
        logs: Pile[Log] = None,
        **kwargs,
    ):
        """Initializes a Branch with references to managers and mailbox.

        Args:
            user (SenderRecipient, optional):
                The user or sender of the branch context.
            name (str | None, optional):
                A human-readable name for this branch.
            messages (Pile[RoledMessage], optional):
                Initial messages to seed the MessageManager.
            system (System | JsonValue, optional):
                A system message or data to configure system role.
            system_sender (SenderRecipient, optional):
                Sender to assign if the system message is added.
            chat_model (iModel, optional):
                The chat model used by iModelManager (if not provided,
                falls back to defaults).
            parse_model (iModel, optional):
                The parse model used by iModelManager.
            imodel (iModel, optional):
                Deprecated. Alias for chat_model.
            tools (FuncTool | list[FuncTool], optional):
                Tools for the ActionManager.
            log_config (LogManagerConfig | dict, optional):
                Configuration for the LogManager.
            system_datetime (bool | str, optional):
                Whether to include timestamps in system messages.
            system_template (Template | str, optional):
                A Jinja2 template or template string for system messages.
            system_template_context (dict, optional):
                Context variables for the system template.
            **kwargs: Additional parameters passed to the Element parent init.
        """
        super().__init__(user=user, name=name, **kwargs)

        self._message_manager = MessageManager(messages=messages)
        if any(
            i is not None
            for i in [system, system_sender, system_datetime, system_template]
        ):

            self._message_manager.add_message(
                system=system,
                system_datetime=system_datetime,
                template=system_template,
                template_context=system_template_context,
                recipient=self.id,
                sender=system_sender or self.user or MessageRole.SYSTEM,
            )

        chat_model = chat_model or imodel
        if not chat_model:
            chat_model = iModel(**Settings.iModel.CHAT)
        if not parse_model:
            parse_model = iModel(**Settings.iModel.PARSE)

        if isinstance(chat_model, dict):
            chat_model = iModel.from_dict(chat_model)
        if isinstance(parse_model, dict):
            parse_model = iModel.from_dict(parse_model)

        self._imodel_manager = iModelManager(
            chat=chat_model, parse=parse_model
        )
        self._action_manager = ActionManager(tools)

        if log_config:
            log_config = (
                log_config
                if isinstance(log_config, LogManagerConfig)
                else LogManagerConfig(**log_config)
            )
            self._log_manager = LogManager.from_config(log_config, logs=logs)
        else:
            self._log_manager = LogManager(**Settings.Config.LOG, logs=logs)

    @property
    def system(self) -> System | None:
        """System | None: The system message or configuration."""
        return self._message_manager.system

    @property
    def msgs(self) -> MessageManager:
        """MessageManager: Manages the conversation messages."""
        return self._message_manager

    @property
    def acts(self) -> ActionManager:
        """ActionManager: Manages available tools (actions)."""
        return self._action_manager

    @property
    def mdls(self) -> iModelManager:
        """iModelManager: Manages chat and parse models."""
        return self._imodel_manager

    @property
    def messages(self) -> Pile[RoledMessage]:
        """Pile[RoledMessage]: The collection of messages in this branch."""
        return self._message_manager.messages

    @property
    def logs(self) -> Pile[Log]:
        """Pile[Log]: The collection of log entries for this branch."""
        return self._log_manager.logs

    @property
    def chat_model(self) -> iModel:
        """iModel: The primary (chat) model in the iModelManager."""
        return self._imodel_manager.chat

    @chat_model.setter
    def chat_model(self, value: iModel) -> None:
        """Sets the chat model in the iModelManager.

        Args:
            value (iModel): The new chat model.
        """
        self._imodel_manager.register_imodel("chat", value)

    @property
    def parse_model(self) -> iModel:
        """iModel: The parsing model in the iModelManager."""
        return self._imodel_manager.parse

    @parse_model.setter
    def parse_model(self, value: iModel) -> None:
        """Sets the parse model in the iModelManager.

        Args:
            value (iModel): The new parse model.
        """
        self._imodel_manager.register_imodel("parse", value)

    @property
    def tools(self) -> dict[str, Tool]:
        """dict[str, Tool]: All tools registered in the ActionManager."""
        return self._action_manager.registry

    async def aclone(self, sender: ID.Ref = None) -> "Branch":
        """Asynchronous clone of this Branch.

        Args:
            sender (ID.Ref, optional):
                If provided, sets this sender ID on all cloned messages.

        Returns:
            Branch: A new branch instance with cloned messages.
        """
        async with self.msgs.messages:
            return self.clone(sender)

    async def operate(
        self,
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
        response_format: type[
            BaseModel
        ] = None,  # alias of operative.request_type
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
        """Orchestrates an 'operate' flow with optional tool invocation.

        This method creates or updates an Operative, sends an instruction
        to the chat model, optionally parses the response, and invokes
        requested tools if `invoke_actions` is True.

        Args:
            instruct (Instruct):
                The instruction containing context, guidance, etc.
            sender (SenderRecipient, optional):
                The sender of this operation.
            recipient (SenderRecipient, optional):
                The recipient of this operation.
            progression (Progression, optional):
                Specific progression of messages to use.
            imodel (iModel, optional):
                Deprecated, alias for chat_model.
            chat_model (iModel, optional):
                The chat model to invoke.
            invoke_actions (bool, optional):
                Whether to call requested tools (actions).
            tool_schemas (list[dict], optional):
                Overridden schemas for the tools to be used.
            images (list, optional):
                Additional images for the model context.
            image_detail (Literal["low", "high", "auto"], optional):
                The level of detail for images, if relevant.
            parse_model (iModel, optional):
                The parse model for validating or refining responses.
            skip_validation (bool, optional):
                If True, skip post-response validation steps.
            tools (ToolRef, optional):
                Specific tools to make available if `invoke_actions` is True.
            operative (Operative, optional):
                The operative describing how to handle the response.
            response_format (type[BaseModel], optional):
                An expected response schema (alias of `operative.request_type`).
            fuzzy_match_kwargs (dict, optional):
                Settings for fuzzy validation if used.
            operative_kwargs (dict, optional):
                Additional arguments for creating an Operative if none is given.
            **kwargs: Additional arguments passed to the model invocation.

        Returns:
            list | BaseModel | None | dict | str:
                The final parsed response, or an Operative object, or the
                string/dict if skipping validation or no tools needed.
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
        chat_model = chat_model or imodel or self.chat_model
        parse_model = parse_model or chat_model

        if isinstance(instruct, dict):
            instruct = Instruct(**instruct)

        instruct = instruct or Instruct(
            instruction=instruction,
            guidance=guidance,
            context=context,
        )

        if reason:
            instruct.reason = True
        if actions:
            instruct.actions = True

        operative: Operative = Step.request_operative(
            request_params=request_params,
            reason=instruct.reason,
            actions=instruct.actions,
            exclude_fields=exclude_fields,
            base_type=response_format,
            field_models=field_models,
            **(request_param_kwargs or {}),
        )
        if instruct.actions:
            tools = tools or True
        if invoke_actions and tools:
            tool_schemas = self.acts.get_tool_schema(tools)

        ins, res = await self.invoke_chat(
            instruction=instruct.instruction,
            guidance=instruct.guidance,
            context=instruct.context,
            sender=sender,
            recipient=recipient,
            response_format=operative.request_type,
            progression=progression,
            imodel=chat_model,
            images=images,
            image_detail=image_detail,
            tool_schemas=tool_schemas,
            **kwargs,
        )
        self.msgs.add_message(instruction=ins)
        self.msgs.add_message(assistant_response=res)

        operative.response_str_dict = res.response
        if skip_validation:
            if return_operative:
                return operative
            return operative.response_str_dict

        response_model = operative.update_response_model(res.response)

        if not isinstance(response_model, BaseModel):
            response_model = await self.parse(
                text=res.response,
                request_type=operative.request_type,
                max_retries=operative.max_retries,
                handle_validation="return_value",
            )
            operative.response_model = operative.update_response_model(
                response_model
            )

        if not isinstance(response_model, BaseModel):
            match handle_validation:
                case "return_value":
                    return response_model
                case "return_none":
                    return None
                case "raise":
                    raise ValueError(
                        "Failed to parse response into request format"
                    )

        if not invoke_actions:
            return operative if return_operative else operative.response_model

        if (
            getattr(response_model, "action_required", None) is True
            and getattr(response_model, "action_requests", None) is not None
        ):
            action_response_models = await self.invoke_action(
                response_model.action_requests,
                **(action_kwargs or {}),
            )
            operative = Step.respond_operative(
                response_params=response_params,
                operative=operative,
                additional_data={"action_responses": action_response_models},
                **(response_param_kwargs or {}),
            )
        return operative if return_operative else operative.response_model

    async def parse(
        self,
        text: str,
        handle_validation: Literal[
            "raise", "return_value", "return_none"
        ] = "return_value",
        max_retries: int = 3,
        request_type: type[BaseModel] = None,
        operative: Operative = None,
        similarity_algo="jaro_winkler",
        similarity_threshold: float = 0.85,
        fuzzy_match: bool = True,
        handle_unmatched: Literal[
            "ignore", "raise", "remove", "fill", "force"
        ] = "force",
        fill_value: Any = None,
        fill_mapping: dict[str, Any] | None = None,
        strict: bool = False,
        suppress_conversion_errors: bool = False,
    ):
        """Attempts to parse text into a structured Pydantic model.

        Uses optional fuzzy matching to handle partial or unclear fields.

        Args:
            text (str): The raw text to parse.
            handle_validation (Literal["raise","return_value","return_none"]):
                What to do if parsing fails. Defaults to "return_value".
            max_retries (int):
                How many times to retry parsing if it fails.
            request_type (type[BaseModel], optional):
                The Pydantic model to parse into.
            operative (Operative, optional):
                If provided, uses its model and max_retries setting.
            similarity_algo (str):
                The similarity algorithm for fuzzy field matching.
            similarity_threshold (float):
                A threshold for fuzzy matching (0.0 - 1.0).
            fuzzy_match (bool):
                If True, tries to match unrecognized keys to known ones.
            handle_unmatched (Literal["ignore","raise","remove","fill","force"]):
                How to handle unmatched fields.
            fill_value (Any):
                A default value used when fill is needed.
            fill_mapping (dict[str, Any] | None):
                A mapping from field -> fill value override.
            strict (bool):
                If True, raises errors on ambiguous fields or data types.
            suppress_conversion_errors (bool):
                If True, logs or ignores errors during data conversion.

        Returns:
            BaseModel | Any | None:
                The parsed model instance, or a dict/string/None depending
                on the handling mode.
        """
        _should_try = True
        num_try = 0
        response_model = text
        if operative is not None:
            max_retries = operative.max_retries
            request_type = operative.request_type

        while (
            _should_try
            and num_try < max_retries
            and not isinstance(response_model, BaseModel)
        ):
            num_try += 1
            _, res = await self.invoke_chat(
                instruction="reformat text into specified model",
                guidane="follow the required response format, using the model schema as a guide",
                context=[{"text_to_format": text}],
                response_format=request_type,
                sender=self.user,
                recipient=self.id,
                imodel=self.parse_model,
            )
            if operative is not None:
                response_model = operative.update_response_model(res.response)
            else:
                response_model = fuzzy_validate_mapping(
                    res.response,
                    breakdown_pydantic_annotation(request_type),
                    similarity_algo=similarity_algo,
                    similarity_threshold=similarity_threshold,
                    fuzzy_match=fuzzy_match,
                    handle_unmatched=handle_unmatched,
                    fill_value=fill_value,
                    fill_mapping=fill_mapping,
                    strict=strict,
                    suppress_conversion_errors=suppress_conversion_errors,
                )
                response_model = request_type.model_validate(response_model)

        if not isinstance(response_model, BaseModel):
            match handle_validation:
                case "return_value":
                    return response_model
                case "return_none":
                    return None
                case "raise":
                    raise ValueError(
                        "Failed to parse response into request format"
                    )

        return response_model

    async def communicate(
        self,
        instruction: Instruction | JsonValue = None,
        guidance: JsonValue = None,
        context: JsonValue = None,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
        progression: ID.IDSeq = None,
        request_model: type[BaseModel] | BaseModel | None = None,
        response_format: type[BaseModel] = None,
        request_fields: dict | list[str] = None,
        imodel: iModel = None,  # alias of chat_model
        chat_model: iModel = None,
        parse_model: iModel = None,
        skip_validation: bool = False,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        num_parse_retries: int = 3,
        fuzzy_match_kwargs: dict = None,
        clear_messages: bool = False,
        operative_model: type[BaseModel] = None,
        **kwargs,
    ):
        """Handles a general 'communicate' flow without tool invocation.

        Sends messages to the model, optionally parses the response, and
        can handle simpler field-level validation.

        Args:
            instruction (Instruction | JsonValue, optional):
                The main user query or context.
            guidance (JsonValue, optional):
                Additional LLM instructions.
            context (JsonValue, optional):
                Context data to pass to the LLM.
            sender (SenderRecipient, optional):
                The sender of this message.
            recipient (SenderRecipient, optional):
                The recipient of this message.
            progression (ID.IDSeq, optional):
                A custom progression of conversation messages.
            request_model (type[BaseModel] | BaseModel | None, optional):
                Model for structured responses.
            response_format (type[BaseModel], optional):
                Alias for request_model if both are not given simultaneously.
            request_fields (dict | list[str], optional):
                Simpler field-level mapping if no model is used.
            imodel (iModel, optional):
                Deprecated, alias for chat_model.
            chat_model (iModel, optional):
                Model used for the conversation.
            parse_model (iModel, optional):
                Model used for any parsing operation.
            skip_validation (bool, optional):
                If True, returns the raw response without further checks.
            images (list, optional):
                Additional images if relevant to the LLM context.
            image_detail (Literal["low","high","auto"], optional):
                Level of image detail if used.
            num_parse_retries (int, optional):
                Max times to retry parsing on failure (capped at 5).
            fuzzy_match_kwargs (dict, optional):
                Settings passed to the fuzzy validation function.
            clear_messages (bool, optional):
                If True, clears previously stored messages.
            **kwargs:
                Additional arguments for the LLM call.

        Returns:
            Any:
                The raw string, a validated Pydantic model, or a dict
                of requested fields, depending on the parameters.
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

        imodel = imodel or chat_model or self.chat_model
        parse_model = parse_model or self.parse_model

        if clear_messages:
            self.msgs.clear_messages()

        if num_parse_retries > 5:
            logging.warning(
                f"Are you sure you want to retry {num_parse_retries} "
                "times? lowering retry attempts to 5. Suggestion is under 3"
            )
            num_parse_retries = 5

        ins, res = await self.invoke_chat(
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
            **kwargs,
        )
        self.msgs.add_message(instruction=ins)
        self.msgs.add_message(assistant_response=res)

        if skip_validation:
            return res.response

        if response_format is not None:
            return await self.parse(
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

    async def invoke_action(
        self,
        action_request: list | ActionRequest | BaseModel | dict,
        /,
        suppress_errors: bool = False,
        sanitize_input: bool = False,
        unique_input: bool = False,
        num_retries: int = 0,
        initial_delay: float = 0,
        retry_delay: float = 0,
        backoff_factor: float = 1,
        retry_default: Any = UNDEFINED,
        retry_timeout: float | None = None,
        retry_timing: bool = False,
        max_concurrent: int | None = None,
        throttle_period: float | None = None,
        flatten: bool = True,
        dropna: bool = True,
        unique_output: bool = False,
        flatten_tuple_set: bool = False,
    ):
        params = locals()
        params.pop("self")
        params.pop("action_request")
        return await alcall(
            action_request,
            self._invoke_action,
            **params,
        )

    async def _invoke_action(
        self,
        action_request: ActionRequest | BaseModel | dict,
        suppress_errors: bool = False,
    ) -> ActionResponse:
        """Invokes a tool (action) asynchronously.

        Args:
            action_request (ActionRequest | BaseModel | dict):
                Contains the function name (`function`) and arguments.
            suppress_errors (bool, optional):
                If True, logs errors instead of raising.

        Returns:
            ActionResponse: The result of the tool call.
        """
        try:
            func, args = None, None
            if isinstance(action_request, BaseModel):
                if hasattr(action_request, "function") and hasattr(
                    action_request, "arguments"
                ):
                    func = action_request.function
                    args = action_request.arguments
            elif isinstance(action_request, dict):
                if action_request.keys() >= {"function", "arguments"}:
                    func = action_request["function"]
                    args = action_request["arguments"]

            func_call: FunctionCalling = await self._action_manager.invoke(
                action_request
            )
            if isinstance(func_call, FunctionCalling):
                self._log_manager.log(Log.create(func_call))

                if not isinstance(action_request, ActionRequest):
                    action_request = ActionRequest.create(
                        function=func,
                        arguments=args,
                        sender=self.id,
                        recipient=func_call.func_tool.id,
                    )

                if action_request not in self.messages:
                    self.msgs.add_message(action_request=action_request)

                self.msgs.add_message(
                    action_request=action_request,
                    action_output=func_call.response,
                )

                return ActionResponseModel(
                    function=action_request.function,
                    arguments=action_request.arguments,
                    output=func_call.response,
                )
            if isinstance(func_call, Log):
                self._log_manager.log(func_call)
                return None

        except Exception as e:
            if suppress_errors:
                logging.error(f"Error invoking action: {e}")
            else:
                raise e

    async def invoke_chat(
        self,
        instruction=None,
        guidance=None,
        context=None,
        sender=None,
        recipient=None,
        request_fields=None,
        response_format: type[BaseModel] = None,
        progression=None,
        imodel: iModel = None,
        tool_schemas=None,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        **kwargs,
    ) -> tuple[Instruction, AssistantResponse]:
        """Invokes the chat model with the current conversation history.

        This method constructs a sequence of messages from the stored
        progression, merges any pending action responses into the context,
        and calls the model. The result is then wrapped in an
        AssistantResponse.

        Args:
            instruction (Any):
                The main user instruction text or structured data.
            guidance (Any):
                Additional system or user guidance.
            context (Any):
                Context data to pass to the model.
            sender (Any):
                The user or entity sending this message.
            recipient (Any):
                The intended recipient of this message (default is self.id).
            request_fields (Any):
                A set of fields for partial validation (rarely used).
            request_model (type[BaseModel], optional):
                A specific Pydantic model to request from the LLM.
            progression (Any):
                The conversation flow or message ordering.
            imodel (iModel, optional):
                The chat model to use.
            tool_schemas (Any, optional):
                Additional schemas to pass if tools are invoked.
            images (list, optional):
                Optional list of images.
            image_detail (Literal["low","high","auto"], optional):
                The level of detail for images, if relevant.
            **kwargs:
                Additional model invocation parameters.

        Returns:
            tuple[Instruction, AssistantResponse]:
                The instruction object (with context) and the final
                AssistantResponse from the model call.
        """
        ins: Instruction = self.msgs.create_instruction(
            instruction=instruction,
            guidance=guidance,
            context=context,
            sender=sender or self.user or "user",
            recipient=recipient or self.id,
            response_format=response_format,
            request_fields=request_fields,
            images=images,
            image_detail=image_detail,
            tool_schemas=tool_schemas,
        )

        progression = progression or self.msgs.progression
        messages: list[RoledMessage] = [
            self.msgs.messages[i] for i in progression
        ]

        use_ins = None
        _to_use = []
        _action_responses: set[ActionResponse] = set()

        for i in messages:
            if isinstance(i, ActionResponse):
                _action_responses.add(i)
            if isinstance(i, AssistantResponse):
                j = AssistantResponse(
                    role=i.role,
                    content=copy(i.content),
                    sender=i.sender,
                    recipient=i.recipient,
                    template=i.template,
                )
                _to_use.append(j)
            if isinstance(i, Instruction):
                j = Instruction(
                    role=i.role,
                    content=copy(i.content),
                    sender=i.sender,
                    recipient=i.recipient,
                    template=i.template,
                )
                j.tool_schemas = None
                j.respond_schema_info = None
                j.request_response_format = None

                if _action_responses:
                    d_ = [k.content for k in _action_responses]
                    for z in d_:
                        if z not in j.context:
                            j.context.append(z)

                    _to_use.append(j)
                    _action_responses = set()
                else:
                    _to_use.append(j)

        messages = _to_use
        if _action_responses:
            j = ins.model_copy()
            d_ = [k.content for k in _action_responses]
            for z in d_:
                if z not in j.context:
                    j.context.append(z)
            use_ins = j

        if messages and len(messages) > 1:
            _msgs = [messages[0]]

            for i in messages[1:]:
                if isinstance(i, AssistantResponse):
                    if isinstance(_msgs[-1], AssistantResponse):
                        _msgs[-1].response = (
                            f"{_msgs[-1].response}\n\n{i.response}"
                        )
                    else:
                        _msgs.append(i)
                else:
                    if isinstance(_msgs[-1], AssistantResponse):
                        _msgs.append(i)
            messages = _msgs

        if self.msgs.system and imodel.sequential_exchange:
            messages = [msg for msg in messages if msg.role != "system"]
            first_instruction = None

            if len(messages) == 0:
                first_instruction = ins.model_copy()
                first_instruction.guidance = self.msgs.system.rendered + (
                    first_instruction.guidance or ""
                )
                messages.append(first_instruction)
            elif len(messages) >= 1:
                first_instruction = messages[0]
                if not isinstance(first_instruction, Instruction):
                    raise ValueError(
                        "First message in progression must be an Instruction or System"
                    )
                first_instruction = first_instruction.model_copy()
                first_instruction.guidance = self.msgs.system.rendered + (
                    first_instruction.guidance or ""
                )
                messages[0] = first_instruction
                messages.append(use_ins or ins)

        else:
            messages.append(use_ins or ins)

        kwargs["messages"] = [i.chat_msg for i in messages]
        imodel = imodel or self.chat_model

        api_call = await imodel.invoke(**kwargs)
        self._log_manager.log(Log.create(api_call))

        res = AssistantResponse.create(
            assistant_response=api_call.response,
            sender=self.id,
            recipient=self.user,
        )

        return ins, res

    def clone(self, sender: ID.Ref = None) -> "Branch":
        """Clones this Branch, creating a new instance with the same data.

        Args:
            sender (ID.Ref, optional):
                If provided, sets this sender ID on the cloned messages.
                Otherwise, uses self.id.

        Returns:
            Branch: A new branch with cloned messages and the same tools.
        """
        if sender is not None:
            if not ID.is_id(sender):
                raise ValueError(
                    "Input value for branch.clone sender is not a valid sender"
                )
            sender = ID.get_id(sender)

        system = self.msgs.system.clone() if self.msgs.system else None
        tools = (
            list(self._action_manager.registry.values())
            if self._action_manager.registry
            else None
        )
        branch_clone = Branch(
            system=system,
            user=self.user,
            messages=[i.clone() for i in self.msgs.messages],
            tools=tools,
            metadata={"clone_from": self},
        )
        for message in branch_clone.msgs.messages:
            message.sender = sender or self.id
            message.recipient = branch_clone.id
        return branch_clone

    def to_df(self, *, progression: Progression = None) -> pd.DataFrame:
        """Converts messages in the branch to a Pandas DataFrame.

        Args:
            progression (Progression, optional):
                A custom progression of messages to include. If None, uses
                the existing stored progression.

        Returns:
            pd.DataFrame:
                A DataFrame containing message data for easy inspection
                or serialization.
        """
        if progression is None:
            progression = self.msgs.progression

        msgs = [
            self.msgs.messages[i]
            for i in progression
            if i in self.msgs.messages
        ]
        p = Pile(collections=msgs)
        return p.to_df(columns=MESSAGE_FIELDS)

    async def _instruct(self, instruct: Instruct, /, **kwargs) -> Any:
        """Convenience method for handling an 'Instruct'.

        Checks if the instruct uses reserved kwargs for an 'operate' flow
        (e.g., actions and a response format). Otherwise, falls back to a
        simpler 'communicate' flow.

        Args:
            instruct (Instruct):
                The instruction context and guidance.
            **kwargs:
                Additional arguments for operate or communicate.

        Returns:
            Any: The result of the chosen flow, e.g., a validated response.
        """
        config = {**instruct.to_dict(), **kwargs}
        if any(i in config and config[i] for i in Instruct.reserved_kwargs):
            if "response_format" in config or "request_model" in config:
                return await self.operate(**config)
            for i in Instruct.reserved_kwargs:
                config.pop(i, None)

        return await self.communicate(**config)

    def send(
        self,
        recipient: IDType,
        category: PackageCategory | None,
        item: Any,
        request_source: IDType | None = None,
    ) -> None:
        """Sends a package (wrapped in Mail) to a specific recipient.

        Args:
            recipient (IDType):
                The ID of the recipient entity.
            category (PackageCategory | None):
                The category of the package (e.g., 'message', 'tool', etc.).
            package (Any):
                The payload to send (could be a message, tool, model, etc.).
            request_source (IDType | None):
                The ID that requested this send (if any).
        """
        package = Package(
            category=category,
            item=item,
            request_source=request_source,
        )

        mail = Mail(
            sender=self.id,
            recipient=recipient,
            package=package,
        )
        self.mailbox.append_out(mail)

    def receive(
        self,
        sender: IDType,
        message: bool = False,
        tool: bool = False,
        imodel: bool = False,
    ) -> None:
        """Retrieves mail from a sender, processing it if enabled by parameters.

        Args:
            sender (IDType):
                The ID of the sender.
            message (bool):
                If True, processes mails categorized as "message".
            tool (bool):
                If True, processes mails categorized as "tool".
            imodel (bool):
                If True, processes mails categorized as "imodel".

        Raises:
            ValueError:
                If the sender doesn't exist or if the mail category is invalid
                for the chosen processing options.
        """
        skipped_requests = Progression()
        sender = ID.get_id(sender)
        if sender not in self.mailbox.pending_ins.keys():
            raise ValueError(f"No package from {sender}")
        while self.mailbox.pending_ins[sender]:
            mail_id = self.mailbox.pending_ins[sender].popleft()
            mail: Mail = self.mailbox.pile_[mail_id]

            if mail.category == "message" and message:
                if not isinstance(mail.package.item, RoledMessage):
                    raise ValueError("Invalid message format")
                new_message = mail.package.item.clone()
                new_message.sender = mail.sender
                new_message.recipient = self.id
                self.msgs.messages.include(new_message)
                self.mailbox.pile_.pop(mail_id)

            elif mail.category == "tool" and tool:
                if not isinstance(mail.package.item, Tool):
                    raise ValueError("Invalid tools format")
                self._action_manager.register_tools(mail.package.item)
                self.mailbox.pile_.pop(mail_id)

            elif mail.category == "imodel" and imodel:
                if not isinstance(mail.package.item, iModel):
                    raise ValueError("Invalid iModel format")
                self._imodel_manager.register_imodel(
                    imodel.name or "chat", mail.package.item
                )
                self.mailbox.pile_.pop(mail_id)

            else:
                skipped_requests.append(mail)

        self.mailbox.pending_ins[sender] = skipped_requests

        if len(self.mailbox.pending_ins[sender]) == 0:
            self.mailbox.pending_ins.pop(sender)

    async def asend(
        self,
        recipient: IDType,
        category: PackageCategory | None,
        package: Any,
        request_source: IDType | None = None,
    ):
        """Asynchronous version of send().

        Args:
            recipient (IDType): The ID of the recipient.
            category (PackageCategory | None): The category of the package.
            package (Any): The item(s) to send.
            request_source (IDType | None): The origin of this request.
        """
        async with self.mailbox.pile_:
            self.send(recipient, category, package, request_source)

    async def areceive(
        self,
        sender: IDType,
        message: bool = False,
        tool: bool = False,
        imodel: bool = False,
    ) -> None:
        """Asynchronous version of receive().

        Args:
            sender (IDType): The sender's ID.
            message (bool): Whether to process message packages.
            tool (bool): Whether to process tool packages.
            imodel (bool): Whether to process iModel packages.
        """
        async with self.mailbox.pile_:
            self.receive(sender, message, tool, imodel)

    def receive_all(self) -> None:
        """Receives mail from all senders."""
        for key in list(self.mailbox.pending_ins.keys()):
            self.receive(key)

    def to_dict(self):
        meta = {}
        if "clone_from" in self.metadata:

            meta["clone_from"] = {
                "id": str(self.metadata["clone_from"].id),
                "user": str(self.metadata["clone_from"].user),
                "created_at": self.metadata["clone_from"].created_at,
                "progression": [
                    str(i)
                    for i in self.metadata["clone_from"].msgs.progression
                ],
            }
        meta.update(
            copy({k: v for k, v in self.metadata.items() if k != "clone_from"})
        )

        dict_ = super().to_dict()
        dict_["messages"] = self.messages.to_dict()
        dict_["logs"] = self.logs.to_dict()
        dict_["chat_model"] = self.chat_model.to_dict()
        dict_["parse_model"] = self.parse_model.to_dict()
        if self.system:
            dict_["system"] = self.system.to_dict()
        dict_["log_config"] = self._log_manager._config.model_dump()
        dict_["metadata"] = meta

        return dict_

    @classmethod
    def from_dict(cls, data: dict):
        dict_ = {
            "messages": data.pop("messages", UNDEFINED),
            "logs": data.pop("logs", UNDEFINED),
            "chat_model": data.pop("chat_model", UNDEFINED),
            "parse_model": data.pop("parse_model", UNDEFINED),
            "system": data.pop("system", UNDEFINED),
            "log_config": data.pop("log_config", UNDEFINED),
        }
        params = {}
        for k, v in data.items():
            if isinstance(v, dict) and "id" in v:
                params.update(v)
            else:
                params[k] = v

        params.update(dict_)
        return cls(**{k: v for k, v in params.items() if v is not UNDEFINED})

    def receive_all(self) -> None:
        """Receives mail from all senders."""
        for key in self.mailbox.pending_ins:
            self.receive(key)

    def flagged_messages(
        self,
        include_clone: bool = False,
        include_load: bool = False,
    ) -> None:
        flags = []
        if include_clone:
            flags.append(MessageFlag.MESSAGE_CLONE)
        if include_load:
            flags.append(MessageFlag.MESSAGE_LOAD)
        out = [i for i in self.messages if i._flag in flags]
        return Pile(collections=out, item_type=RoledMessage, strict_type=False)


# File: lionagi/session/branch.py
