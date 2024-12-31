# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from jinja2 import Template
from pydantic import BaseModel, Field, JsonValue, PrivateAttr

from lionagi.libs.validate.fuzzy_validate_mapping import fuzzy_validate_mapping
from lionagi.operatives.instruct.instruct import Instruct

# from lionagi.operatives.manager import OperativeManager
from lionagi.operatives.operative import Operative
from lionagi.operatives.step import Step
from lionagi.protocols._concepts import Communicatable, Observable, Relational
from lionagi.protocols.generic.element import IDType
from lionagi.protocols.generic.log import LogManagerConfig
from lionagi.protocols.mail.exchange import Exchange, Mail, Mailbox, Package
from lionagi.protocols.mail.package import PackageCategory
from lionagi.protocols.messages.base import (
    MESSAGE_FIELDS,
    MessageRole,
    SenderRecipient,
)
from lionagi.protocols.messages.system import System
from lionagi.protocols.types import (
    ID,
    ActionRequest,
    ActionResponse,
    AssistantResponse,
    Communicatable,
    Instruction,
    LogManager,
    MessageManager,
    Pile,
    Progression,
    Relational,
    RoledMessage,
    SenderRecipient,
)
from lionagi.service.imodel import iModel
from lionagi.service.manager import iModelManager
from lionagi.settings import Settings
from lionagi.utils import (
    UNDEFINED,
    alcall,
    breakdown_pydantic_annotation,
    time,
    to_json,
)


class Branch(Observable, Communicatable, Relational):

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

    mailbox: Mailbox = Field(None)

    _message_manager: MessageManager = PrivateAttr(None)
    _action_manager: ActionManager = PrivateAttr(None)
    _imodel_manager: iModelManager = PrivateAttr(None)
    # _operative_manager: OperativeManager = PrivateAttr(None)
    _log_manager: LogManager = PrivateAttr(None)

    def __init__(
        self,
        *,
        user: SenderRecipient = None,  # base_branch kwargs
        name: str = None,
        mailbox: Exchange = None,
        messages: Pile[RoledMessage] = None,  # message manager kwargs
        save_on_clear: bool = False,
        system: System | JsonValue = None,
        system_sender: SenderRecipient = None,
        system_datetime: bool | str = None,
        system_template: Template | str = None,
        system_template_context: dict = None,
        chat_model: iModel = None,  # imodel manager kwargs
        parse_model: iModel = None,
        imodel: iModel = None,  # deprecated, alias of chat_model
        tools: FuncTool | list[FuncTool] = None,  # action manager kwargs
        log_config: LogManagerConfig | dict = None,  # log manager kwargs
        metadata: dict = None,  # basic Node kwargs
        id: IDType = None,
        created_at: float = None,
    ):
        super().__init__()
        self.id = IDType.validate(id)
        self.created_at: float = created_at or time(type_="timestamp")
        self.metadata = metadata or {}
        self.user = user
        self.name = name
        self.mailbox = mailbox or Exchange()

        self._save_on_clear = save_on_clear
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
        *,
        instruction=None,
        guidance=None,
        context=None,
        sender=None,
        recipient=None,
        operative_model: type[BaseModel] = None,
        progress=None,
        imodel: iModel = None,
        reason: bool = False,
        actions: bool = False,
        exclude_fields: list | dict | None = None,
        handle_validation: Literal[
            "raise", "return_value", "return_none"
        ] = "return_value",
        invoke_actions: bool = True,
        tool_schemas=None,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        max_retries: int = None,
        parse_imodel: iModel = None,
        retry_kwargs: dict = {},
        auto_retry_parse: bool = True,
        field_models: list[FieldModel] | None = None,
        skip_validation: bool = False,
        tools: ToolRef = None,
        request_params: ModelParams = None,
        request_param_kwargs: dict = {},
        response_params: ModelParams = None,
        response_param_kwargs: dict = {},
        **kwargs,
    ) -> list | BaseModel | None | dict | str:
        imodel = imodel or self.chat_model
        parse_imodel = parse_imodel or imodel

        operative: Operative = Step.request_operative(
            request_params=request_params,
            reason=reason,
            actions=actions,
            exclude_fields=exclude_fields,
            base_type=operative_model,
            field_models=field_models,
            **request_param_kwargs,
        )
        if isinstance(max_retries, int) and max_retries > 0:
            operative.max_retries = max_retries

        if auto_retry_parse is True:
            operative.auto_retry_parse = True

        if actions:
            tools = tools or True
        if invoke_actions and tools:
            tool_schemas = self.get_tool_schema(tools)

        ins, res = await self._invoke_imodel(
            instruction=instruction,
            guidance=guidance,
            context=context,
            sender=sender,
            recipient=recipient,
            request_model=operative.request_type,
            progress=progress,
            imodel=imodel,
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
        max_retries = operative.max_retries

        num_try = 0
        parse_imodel = self.parse_model or imodel or self.chat_model
        while (
            operative._should_retry
            and isinstance(response_model, str | dict)
            and num_try < max_retries
        ):
            num_try += 1
            if operative.auto_retry_parse:
                instruct = Instruction(
                    instruction="reformat text into specified model",
                    guidance="follow the required response format, using the model schema as a guide",
                    context=[{"text_to_format": res.response}],
                    request_model=operative.request_type,
                    sender=self.user,
                    recipient=self,
                )

            api_request = {
                "messages": [instruct.chat_msg],
                **retry_kwargs,
            }

            res1 = AssistantResponse(
                sender=self,
                recipient=self.user,
                assistant_response=await parse_imodel.invoke(**api_request),
            )
            response_model = operative.update_response_model(res1.response)

        if isinstance(response_model, dict | str):
            if handle_validation == "raise":
                raise ValueError(
                    "Operative model validation failed. iModel response"
                    " not parsed into operative model:"
                    f" {operative.name}"
                )
            if handle_validation == "return_none":
                return None
            if handle_validation == "return_value":
                return response_model

        if (
            invoke_actions is True
            and getattr(response_model, "action_required", None) is True
            and getattr(response_model, "action_requests", None) is not None
        ):
            action_response_models = await alcall(
                response_model.action_requests,
                self.invoke_action,
                suppress_errors=True,
            )
            action_response_models = [
                i.model_dump() for i in action_response_models if i
            ]
            operative = Step.respond_operative(
                response_params=response_params,
                operative=operative,
                additional_data={"action_responses": action_response_models},
                **response_param_kwargs,
            )
            response_model = operative.response_model
        elif (
            hasattr(response_model, "action_requests")
            and response_model.action_requests
        ):
            for i in response_model.action_requests:
                act_req = ActionRequest(
                    function=i.function,
                    arguments=i.arguments,
                    sender=self,
                )
                self.msgs.add_message(
                    action_request=act_req,
                    sender=act_req.sender,
                    recipient=None,
                )

        return operative.response_model

    async def communicate(
        self,
        instruction: Instruction | JsonValue = None,
        guidance: JsonValue = None,
        context: JsonValue = None,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
        progress: ID.IDSeq = None,
        request_model: type[BaseModel] | BaseModel = None,
        request_fields: dict | list[str] = None,
        imodel: iModel = None,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        num_parse_retries: int = 0,
        parse_imodel: iModel = None,
        retry_kwargs: dict = {},
        handle_validation: Literal[
            "raise", "return_value", "return_none"
        ] = "return_value",
        skip_validation: bool = False,
        clear_messages: bool = False,
        response_format: (
            type[BaseModel] | BaseModel
        ) = None,  # alias of request_model
        **kwargs,
    ):
        if response_format and request_model:
            raise ValueError(
                "Cannot specify both response_format and request_model"
                "as they are aliases for the same parameter."
            )
        request_model = request_model or response_format

        imodel = imodel or self.chat_model
        parse_imodel = parse_imodel or imodel
        if clear_messages:
            self.msgs.clear_messages()

        if num_parse_retries > 5:
            logging.warning(
                f"Are you sure you want to retry {num_parse_retries} "
                "times? lowering retry attempts to 5. Suggestion is under 3"
            )
            num_parse_retries = 5

        ins, res = await self._invoke_imodel(
            instruction=instruction,
            guidance=guidance,
            context=context,
            sender=sender,
            recipient=recipient,
            request_model=request_model,
            progress=progress,
            imodel=imodel,
            images=images,
            image_detail=image_detail,
            **kwargs,
        )
        self.msgs.add_message(instruction=ins)
        self.msgs.add_message(assistant_response=res)

        if skip_validation:
            return res.response

        _d = None
        if request_fields is not None or request_model is not None:
            parse_success = None
            try:
                if request_model:
                    try:
                        _d = to_json(res.response)
                        _d = fuzzy_validate_mapping(
                            _d,
                            breakdown_pydantic_annotation(request_model),
                            handle_unmatched="force",
                            fill_value=UNDEFINED,
                        )
                        _d = {k: v for k, v in _d.items() if v != UNDEFINED}
                        return request_model.model_validate(_d)
                    except Exception:
                        pass
                elif request_fields:
                    try:
                        _d = to_json(res.response)
                        _d = fuzzy_validate_mapping(
                            _d,
                            request_fields,
                            handle_unmatched="force",
                            fill_value=UNDEFINED,
                        )
                        _d = {k: v for k, v in _d.items() if v != UNDEFINED}
                        return _d
                    except Exception:
                        pass
            except Exception:
                parse_success = False
                pass

            while parse_success is False and num_parse_retries > 0:
                if request_fields:
                    try:
                        _d = to_json(res.response)
                        _d = fuzzy_validate_mapping(
                            _d,
                            request_fields,
                            handle_unmatched="force",
                            fill_value=UNDEFINED,
                        )
                        _d = {k: v for k, v in _d.items() if v != UNDEFINED}
                    except Exception:
                        pass
                    if _d and isinstance(_d, dict):
                        parse_success = True
                        if res not in self.msgs.messages:
                            if isinstance(
                                self.msgs.messages[-1], AssistantResponse
                            ):
                                self.msgs.messages[-1].response = res.response
                            else:
                                self.msgs.add_message(assistant_response=res)
                        return _d

                elif request_model:
                    _d = to_json(res.response)
                    _d = fuzzy_validate_mapping(
                        _d,
                        breakdown_pydantic_annotation(request_model),
                        handle_unmatched="force",
                        fill_value=UNDEFINED,
                    )

                    _d = {k: v for k, v in _d.items() if v != UNDEFINED}
                    if _d and isinstance(_d, dict):
                        try:
                            _d = request_model.model_validate(_d)
                            parse_success = True
                            if res not in self.msgs.messages:
                                if isinstance(
                                    self.msgs.messages[-1], AssistantResponse
                                ):
                                    self.msgs.messages[-1].response = (
                                        res.response
                                    )
                                else:
                                    self.msgs.add_message(
                                        assistant_response=res
                                    )
                            return _d
                        except Exception as e:
                            logging.warning(
                                "Failed to parse model response into "
                                f"pydantic model: {e}"
                            )

                if parse_success is False:
                    logging.warning(
                        "Failed to parse response into request "
                        f"format, retrying... with {parse_imodel.model}"
                    )
                    _, res = await self._invoke_imodel(
                        instruction="reformat text into specified model",
                        context=res.response,
                        request_model=request_model,
                        request_fields=request_fields,
                        progress=[],
                        imodel=parse_imodel or imodel,
                        **retry_kwargs,
                    )
                    num_parse_retries -= 1

        if request_fields and not isinstance(_d, dict):
            if handle_validation == "raise":
                raise ValueError(
                    "Failed to parse response into request format"
                )
            if handle_validation == "return_none":
                return None
            if handle_validation == "return_value":
                return res.response

        if request_model and not isinstance(_d, BaseModel):
            if handle_validation == "raise":
                raise ValueError(
                    "Failed to parse response into request format"
                )
            if handle_validation == "return_none":
                return None
            if handle_validation == "return_value":
                return res.response

        return _d if _d else res.response

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

            result = await self._action_manager.invoke(action_request)
            tool = self._action_manager.registry[action_request.function]

            if not isinstance(action_request, ActionRequest):
                action_request = await self.msgs.a_add_message(
                    function=func,
                    arguments=args,
                    sender=self,
                    recipient=tool,
                )

            await self.msgs.a_add_message(
                action_request=action_request,
                action_response=result,
            )

            return ActionResponseModel(
                function=action_request.function,
                arguments=action_request.arguments,
                output=result,
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
        progress=None,
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

        progress = progress or self.msgs.progress
        messages: list[RoledMessage] = [
            self.msgs.messages[i] for i in progress
        ]

        use_ins = None
        if imodel.sequential_exchange:
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

        if (
            self.msgs.system
            and hasattr(imodel, "allowed_roles")
            and "system" not in imodel.allowed_roles
        ):
            messages = [msg for msg in messages if msg.role != "system"]
            first_instruction = None

            if len(messages) == 0:
                first_instruction = ins.model_copy()
                first_instruction.guidance = self.msgs.system.system_info + (
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
                first_instruction.guidance = self.msgs.system.system_info + (
                    first_instruction.guidance or ""
                )
                messages[0] = first_instruction
                messages.append(use_ins or ins)

        else:
            messages.append(use_ins or ins)

        kwargs["messages"] = [i.chat_msg for i in messages]
        imodel = imodel or self.chat_model

        res = AssistantResponse(
            assistant_response=await imodel.invoke(**kwargs),
            sender=self,
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

    def to_df(self, *, progress: Progression = None) -> pd.DataFrame:
        if progress is None:
            progress = self.msgs.progress

        msgs = [
            self.msgs.messages[i] for i in progress if i in self.msgs.messages
        ]
        p = Pile(items=msgs)
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
        sender: ID,
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
        while self.mailbox.pending_ins[sender].size() > 0:
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
                self.tool_manager.register_tools(mail.package.item)
                self.mailbox.pile_.pop(mail_id)

            elif mail.category == "imodel" and imodel:
                if not isinstance(mail.package.item, iModel):
                    raise ValueError("Invalid iModel format")
                self.imodel = mail.package.item
                self.mailbox.pile_.pop(mail_id)

            else:
                skipped_requests.append(mail)

        self.mailbox.pending_ins[sender] = skipped_requests

        if len(self.mailbox.pending_ins[sender]) == 0:
            self.mailbox.pending_ins.pop(sender)

    def receive_all(self) -> None:
        """Receives mail from all senders."""
        for key in list(self.mailbox.pending_ins.keys()):
            self.receive(key)
