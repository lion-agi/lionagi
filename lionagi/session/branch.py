# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, Literal

import pandas as pd
from jinja2 import Template
from pydantic import BaseModel, Field, JsonValue, PrivateAttr

from lionagi.libs.validate.fuzzy_validate_mapping import fuzzy_validate_mapping
from lionagi.operatives.action.function_calling import FunctionCalling
from lionagi.operatives.types import (
    ActionManager,
    ActionResponseModel,
    FuncTool,
    Instruct,
    Operative,
    Step,
    Tool,
    ToolRef,
)
from lionagi.protocols.generic.log import Log
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
    LogManager,
    LogManagerConfig,
    Mail,
    Mailbox,
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
from lionagi.service.imodel import iModel
from lionagi.service.manager import iModelManager
from lionagi.settings import Settings
from lionagi.utils import UNDEFINED, alcall, breakdown_pydantic_annotation


class Branch(Element, Communicatable, Relational):

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
        **kwargs,
    ):

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

        chat_model = chat_model or imodel or iModel(**Settings.iModel.CHAT)
        parse_model = parse_model or iModel(**Settings.iModel.PARSE)

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
            self._log_manager = LogManager.from_config(log_config)
        else:
            self._log_manager = LogManager(**Settings.Config.LOG)

    @property
    def system(self) -> System | None:
        return self._message_manager.system

    @property
    def msgs(self):
        return self._message_manager

    @property
    def acts(self):
        return self._action_manager

    @property
    def mdls(self):
        return self._imodel_manager

    # @property
    # def oprt(self):
    #     return self._operative_manager

    @property
    def messages(self):
        return self._message_manager.messages

    @property
    def logs(self):
        return self._log_manager.logs

    @property
    def chat_model(self) -> iModel:
        return self._imodel_manager.chat

    @chat_model.setter
    def chat_model(self, value: iModel):
        self._imodel_manager.register_imodel("chat", value)

    @property
    def parse_model(self) -> iModel:
        return self._imodel_manager.parse

    @parse_model.setter
    def parse_model(self, value: iModel):
        self._imodel_manager.register_imodel("parse", value)

    @property
    def tools(self):
        return self._action_manager.registry

    async def aclone(self, sender: ID.Ref = None) -> "Branch":
        async with self.msgs.messages:
            return self.clone(sender)

    async def operate(
        self,
        instruct: Instruct,
        *,
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
        fuzzy_match_kwargs: dict = None,
        operative_kwargs: dict = None,
        **kwargs,
    ) -> list | BaseModel | None | dict | str:

        chat_model = chat_model or imodel or self.chat_model
        parse_model = parse_model or chat_model

        if operative is None:
            operative_kwargs = operative_kwargs or {}
            operative_kwargs["base_type"] = response_format
            operative = Step.request_operative(**operative_kwargs)

        if invoke_actions and tools:
            tool_schemas = self.acts.get_tool_schema(tools)

        ins, res = await self.invoke_chat(
            instruction=instruct.instruction,
            guidance=instruct.guidance,
            context=instruct.context,
            sender=sender,
            recipient=recipient,
            request_model=response_format or operative.request_type,
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
            return operative.response_str_dict

        response_model = operative.update_response_model(res.response)

        if not isinstance(response_model, BaseModel):
            response_model = await self.parse(
                text=res.response,
                request_type=operative.request_type,
                max_retries=operative.max_retries,
                handle_validation="return_value",
                **(fuzzy_match_kwargs or {}),
            )
            response_model = operative.update_response_model(response_model)

        if not invoke_actions:
            return operative

        if (
            getattr(response_model, "action_required", None) is True
            and getattr(response_model, "action_requests", None) is not None
        ):
            action_response_models = await alcall(
                response_model.action_requests,
                self.invoke_action,
            )
            response_model = operative.update_response_model(
                data={"action_responses": action_response_models},
                response_model=response_model,
            )

        return response_model

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
                request_model=request_type,
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
        **kwargs,
    ):
        if response_format and request_model:
            raise ValueError(
                "Cannot specify both response_format and request_model"
                "as they are aliases for the same parameter."
            )
        request_model = response_format or request_model
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
            request_model=request_model,
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

        if request_model is not None:
            return await self.parse(
                text=res.response,
                request_type=request_model,
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
        action_request: ActionRequest | BaseModel | dict,
        suppress_errors: bool = False,
    ) -> ActionResponse:
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
            self._log_manager.log(Log.create(func_call))
            tool = self._action_manager.registry[action_request.function]

            if not isinstance(action_request, ActionRequest):
                action_request = ActionRequest.create(
                    function=func,
                    arguments=args,
                    sender=self.id,
                    recipient=tool.id,
                )
                await self.msgs.a_add_message(action_request=action_request)

            await self.msgs.a_add_message(
                action_request=action_request,
                action_response=func_call.response,
            )

            return ActionResponseModel(
                function=action_request.function,
                arguments=action_request.arguments,
                output=func_call,
            )
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
        request_model: type[BaseModel] = None,
        progression=None,
        imodel: iModel = None,
        tool_schemas=None,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        **kwargs,
    ) -> tuple[Instruction, AssistantResponse]:

        ins: Instruction = self.msgs.create_instruction(
            instruction=instruction,
            guidance=guidance,
            context=context,
            sender=sender or self.user or "user",
            recipient=recipient or self.id,
            request_model=request_model,
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
                _to_use.append(i.model_copy())
            if isinstance(i, Instruction):
                if _action_responses:
                    j = i.model_copy()
                    d_ = [k.content for k in _action_responses]
                    for z in d_:
                        if z not in j.context:
                            j.context.append(z)

                    _to_use.append(j)
                    _action_responses = set()
                else:
                    _to_use.append(i)

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

        if self.msgs.system:
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
                        "First message in progress must be an Instruction or System"
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
        """
        Split a branch, creating a new branch with the same messages and tools.

        Args:
            branch: The branch to split or its identifier.

        Returns:
            The newly created branch.
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
        )
        for message in branch_clone.msgs.messages:
            message.sender = sender or self.id
            message.recipient = branch_clone.id
        return branch_clone

    def to_df(self, *, progression: Progression = None) -> pd.DataFrame:
        if progression is None:
            progression = self.msgs.progression

        msgs = [
            self.msgs.messages[i]
            for i in progression
            if i in self.msgs.messages
        ]
        p = Pile(collections=msgs)
        return p.to_df(columns=MESSAGE_FIELDS)

    async def _instruct(self, instruct: Instruct, /, **kwargs):
        config = {**instruct.to_dict(), **kwargs}
        if any(i in config for i in Instruct.reserved_kwargs):
            return await self.operate(**config)
        return await self.communicate(**config)

    def send(
        self,
        recipient: IDType,
        category: PackageCategory | None,
        package: Any,
        request_source: IDType | None = None,
    ) -> None:
        package = Package(
            category=category,
            package=package,
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
        """
        Receives mail from a sender.

        Args:
            sender (str): The ID of the sender.
            message (bool): Whether to process message mails.
            tool (bool): Whether to process tool mails.
            imodel (bool): Whether to process imodel mails.

        Raises:
            ValueError: If the sender does not exist or the mail category is
            invalid.
        """
        skipped_requests = Progression()
        if not isinstance(sender, str):
            sender = sender.id
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
                self.messages.include(new_message)
                self.mailbox.pile_.pop(mail_id)

            elif mail.category == "tool" and tool:
                if not isinstance(mail.package.package, Tool):
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
        async with self.mailbox.pile_:
            self.send(recipient, category, package, request_source)

    async def areceive(
        self,
        sender: IDType,
        message: bool = False,
        tool: bool = False,
        imodel: bool = False,
    ):
        async with self.mailbox.pile_:
            self.receive(sender, message, tool, imodel)

    def receive_all(self) -> None:
        """Receives mail from all senders."""
        for key in list(self.mailbox.pending_ins.keys()):
            self.receive(key)
