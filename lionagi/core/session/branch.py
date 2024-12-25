# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Branch Module for LionAGI Framework.

This module implements the Branch class, which serves as a fundamental
component for managing conversation flows, action execution, and model
interactions within the LionAGI framework. It provides mechanisms for
message handling, tool management, and state tracking.
"""

import logging
from pathlib import Path
from typing import Literal

import pandas as pd
from pydantic import BaseModel, JsonValue, model_validator

from lionagi.core.action import types as action
from lionagi.core.communication import types as co
from lionagi.core.generic import types as ge
from lionagi.core.models import types as mo
from lionagi.core.typing import ID
from lionagi.integrations.litellm_.imodel import LiteiModel
from lionagi.integrations.pydantic_ import break_down_pydantic_annotation
from lionagi.libs.constants import UNDEFINED
from lionagi.libs.func import alcall
from lionagi.libs.parse import to_json, validate_mapping
from lionagi.protocols.operatives import types as op
from lionagi.service.imodel import iModel
from lionagi.settings import Settings


class Branch(ge.Component):
    """
    A class representing a conversation branch with message and tool
    management.

    The Branch class serves as a core component in the LionAGI framework,
    providing:
      - Message management and conversation flow
      - Tool registration and execution
      - Model interactions and response processing
      - State management and cloning capabilities

    Attributes:
        user (str | None): The identifier for the user associated with
            this branch
        name (str | None): Optional name identifier for the branch
        msgs (co.MessageManager): Manager for handling conversation messages
        acts (action.ActionManager): Manager for handling tools and actions
        imodel (iModel | LiteiModel | None): Primary model for interactions
        parse_imodel (iModel | LiteiModel | None): Model used for parsing
            responses
    """

    user: str | None = None
    name: str | None = None
    msgs: co.MessageManager = None
    acts: action.ActionManager = None
    imodel: iModel | LiteiModel | None = None
    parse_imodel: iModel | LiteiModel | None = None

    @model_validator(mode="before")
    def _validate_data(cls, data: dict) -> dict:
        """
        Validate and preprocess input data during model initialization.

        Handles setup of message managers, action managers, and models with
        appropriate default configurations if not provided.

        Args:
            data (dict): Input data dictionary containing branch configuration.
            - user: the user of the branch
            - name: the name of the branch
            - msgs: message manager object
            - messages: list or pile of roled messages
            - logger: a logger object for message manager
            - system: a system message or json value prompt
            - acts: action manager object
            - tools: list of tools to register
            - imodel: primary model for interactions
            - parse_imodel: model for parsing responses
            - ln_id, timestamp, metadata, embedding, content

        Returns:
            dict: Processed and validated data dictionary
        """
        user = data.pop("user", None)
        name = data.pop("name", None)
        message_manager = data.pop("msgs", None)
        if not message_manager:
            message_manager = co.MessageManager(
                messages=data.pop("messages", None),
                logger=data.pop("logger", None),
                system=data.pop("system", None),
            )
        if not message_manager.logger:
            message_manager.logger = ge.LogManager(
                **Settings.Branch.BRANCH.message_log_config.to_dict()
            )

        acts = data.pop("acts", None)
        if not acts:
            acts = action.ActionManager()
            acts.logger = ge.LogManager(
                **Settings.Branch.BRANCH.action_log_config.to_dict()
            )
        if "tools" in data:
            acts.register_tools(data.pop("tools"))

        imodel = data.pop(
            "imodel",
            iModel(**Settings.iModel.CHAT.to_dict()),
        )
        parse_imodel = data.pop(
            "parse_imodel",
            iModel(**Settings.iModel.PARSE.to_dict()),
        )
        out = {
            "user": user,
            "name": name,
            "msgs": message_manager,
            "acts": acts,
            "imodel": imodel,
            "parse_imodel": parse_imodel,
            **data,
        }
        return out

    def dump_log(
        self, clear: bool = True, persist_path: str | Path = None
    ) -> None:
        """
        Dump logs from both message and action managers.

        Will first concat the logs into messages logger, then dump the logs
        into the appropriate path and clear the logs in memory if clear is True.

        Args:
            clear (bool): Whether to clear logs after dumping
            persist_path (str | Path, optional): Path to save the logs
        """
        self.msgs.logger.logs |= self.acts.logger.logs
        self.msgs.logger.dump(clear, persist_path)
        if clear:
            self.acts.logger.logs.clear()

    def to_df(self, *, progress: ge.Progression = None) -> pd.DataFrame:
        """
        Convert branch messages to an organized pandas DataFrame.

        Args:
            progress (generic.Progression, optional): Progress tracker to
                filter messages

        Returns:
            pd.DataFrame: DataFrame containing message history
        """
        if progress is None:
            progress = self.msgs.progress

        msgs = [
            self.msgs.messages[i] for i in progress if i in self.msgs.messages
        ]
        return ge.Pile(items=msgs).to_df(columns=co.MESSAGE_FIELDS)

    async def aclone(self, sender: ID.Ref = None) -> "Branch":
        """
        Asynchronously clone the branch with message safety.

        Args:
            sender (ID.Ref, optional): New sender ID for the cloned branch

        Returns:
            Branch: New branch instance with copied messages and tools
        """
        async with self.msgs.messages:
            return self.clone(sender)

    def clone(self, sender: ID.Ref = None) -> "Branch":
        """
        Create a new branch with copied messages and tools.

        Args:
            sender (ID.Ref, optional): New sender ID for the cloned messages

        Returns:
            Branch: New branch instance with copied configuration

        Raises:
            ValueError: If provided sender is not a valid ID
        """
        if sender is not None:
            if not ID.is_id(sender):
                raise ValueError(
                    "Input value for branch.clone sender is not a valid sender"
                )
            sender = ID.get_id(sender)

        system = self.msgs.system.clone() if self.msgs.system else None
        tools = (
            list(self.acts.registry.values()) if self.acts.registry else None
        )
        branch_clone = Branch(
            system=system,
            user=self.user,
            messages=[i.clone() for i in self.msgs.messages],
            tools=tools,
        )
        for message in branch_clone.msgs.messages:
            message.sender = sender or self.ln_id
            message.recipient = branch_clone.ln_id
        return branch_clone

    async def instruct(self, instruct: op.Instruct, /, **kwargs):
        """
        Process instruction by delegating to appropriate operation method.
        A wrapper around operate and communicate methods.

        Args:
            instruct (op.Instruct): Instruction to process
            **kwargs: Additional configuration parameters

        Returns:
            Result of operation or communication based on instruction type
        """
        config = {**instruct.to_dict(), **kwargs}
        if any(i in config for i in op.OperationInstruct.reserved_kwargs):
            return await self.operate(**config)
        return await self.communicate(**config)

    async def _invoke_action(
        self,
        action_request: co.ActionRequest | op.ActionRequestModel | dict,
        suppress_errors: bool = False,
    ) -> co.ActionResponse:
        """
        Invoke a tool action and record the interaction.

        Args:
            action_request: Specification of the action to perform. Must be:
              - co.ActionRequest
              - op.ActionRequestModel
              - dict with keys 'function' and 'arguments'
                (converted to op.ActionRequestModel)

            suppress_errors (bool): Whether to suppress and log errors
                instead of raising

        Returns:
            co.ActionResponse: Response from the action execution

        Raises:
            Exception: If error occurs and suppress_errors is False
        """
        try:
            func, args = None, None
            if isinstance(action_request, op.ActionRequestModel):
                func = action_request.function
                args = action_request.arguments

            elif isinstance(action_request, dict):
                if action_request.keys() >= {"function", "arguments"}:
                    func = action_request["function"]
                    args = action_request["arguments"]

            result = await self.acts.invoke(action_request)
            tool = self.acts.registry[action_request.function]

            if not isinstance(action_request, co.ActionRequest):
                action_request = self.msgs.add_message(
                    function=func,
                    arguments=args,
                    sender=self,
                    recipient=tool,
                )

            self.msgs.add_message(
                action_request=action_request,
                action_response=result,
            )

            return op.ActionResponseModel(
                function=action_request.function,
                arguments=action_request.arguments,
                output=result,
            )
        except Exception as e:
            if suppress_errors:
                logging.error(f"Error invoking action: {e}")
            else:
                raise e

    def _get_tool_schema(
        self,
        tools: str | action.Tool | list[action.Tool | str] | bool,
        auto_register: bool = True,
    ) -> dict:
        """Retrieve schema information for specified tools.

        Args:
            tools: Tool(s) to get schema for
            auto_register (bool): Whether to automatically register unregistered
                tools

        Returns:
            dict: Schema information for the specified tools
        """
        tools = tools if isinstance(tools, list) else [tools]
        if auto_register:
            for i in tools:
                if isinstance(i, action.FuncTool) and i not in self.acts:
                    self.acts.register_tools(i)
        return self.acts.get_tool_schema(tools)

    async def operate(
        self,
        *,
        instruction: co.Instruction | JsonValue = None,
        guidance: JsonValue = None,
        context: JsonValue = None,
        sender: ID.SenderRecipient = None,
        recipient: ID.SenderRecipient = None,
        operative_model: type[BaseModel] = None,
        progress: ID.IDSeq = None,
        imodel: iModel = None,
        reason: bool = False,
        actions: bool = False,
        exclude_fields: list | dict | None = None,
        handle_validation: Literal[
            "raise", "return_value", "return_none"
        ] = "return_value",
        invoke_actions: bool = True,
        tool_schemas: list[dict] = None,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        max_retries: int = None,
        parse_imodel: iModel = None,
        retry_kwargs: dict = {},
        auto_retry_parse: bool = True,
        field_models: list[mo.FieldModel] | None = None,
        skip_validation: bool = False,
        tools: action.ToolType = None,
        request_params: mo.ModelParams = None,
        request_param_kwargs: dict = {},
        response_params: mo.ModelParams = None,
        response_param_kwargs: dict = {},
        response_format: type[BaseModel] = None,
        **kwargs,
    ) -> list | BaseModel | None | dict | str:
        """
        Execute a complex operation with model interaction and action execution.

        This method manages the complete pipeline of:
          1. Model interaction setup and execution
          2. Response validation and parsing
          3. Action execution (if required)
          4. Result formatting and return

        Args:
            instruction: Primary instruction or prompt for the operation
              (co.Instruction object or JSON serializable data)
            guidance: Additional guidance or context for the model
            context: Supplementary context information
            sender: Operation request source (usually user)
            recipient: Operation target (usually assistant or this branch)
            operative_model: Model for structuring the response (alias with
              response_format)
            progress: Sequence of operations to include (like a list of IDs)
            imodel: Model instance to use (iModel or LiteiModel)
            reason: Whether to include reasoning in the response
            actions: Whether to enable action execution
            exclude_fields: Fields to exclude from processing
            handle_validation: Strategy for validation failures:
              - "raise": raise an error
              - "return_value": return the raw response
              - "return_none": return None
            invoke_actions: Whether to execute requested actions
            tool_schemas: JSON schemas for available tools
            images: List of image data for processing
            image_detail: Level of image detail to process
            max_retries: Maximum retry attempts for failed operations
            parse_imodel: Model instance for parsing responses
            retry_kwargs: Additional retry configuration
            auto_retry_parse: Enable auto parsing retry on failures
            field_models: Additional field models for validation
            skip_validation: Whether to skip response validation
            tools: Tools available for action execution (True = all)
            request_params: Params for model request
            request_param_kwargs: Additional request parameters
            response_params: Params for model response
            response_param_kwargs: Additional response parameters
            response_format: Alias for operative_model
            **kwargs: Additional config options

        Returns:
            Processed and validated response in the requested format. The
            return type varies based on operation configuration.

        Raises:
            ValueError: If incompatible parameters are specified (e.g., both
              response_format and operative_model)
        """
        if response_format and operative_model:
            raise ValueError(
                "Cannot specify both response_format and operative_model"
                "as they are aliases for the same parameter."
            )

        if tool_schemas and tools:
            raise ValueError("Cannot specify both tool_schemas and tools")

        operative_model = operative_model or response_format
        imodel = imodel or self.imodel
        parse_imodel = parse_imodel or imodel

        operative: op.Operative = op.Step.request_operative(
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

        if invoke_actions and actions is True:
            if tools:
                tool_schemas = self._get_tool_schema(tools, auto_register=True)
            else:
                tool_schemas = tool_schemas or self._get_tool_schema(True)

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
        parse_imodel = self.parse_imodel or imodel or self.imodel
        while (
            operative._should_retry
            and isinstance(response_model, str | dict)
            and num_try < max_retries
        ):
            num_try += 1
            if operative.auto_retry_parse:
                instruct = co.Instruction(
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
            if isinstance(parse_imodel, iModel):
                api_request = parse_imodel.parse_to_data_model(**api_request)

            res1 = co.AssistantResponse(
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
                self._invoke_action,
                suppress_errors=True,
            )
            action_response_models = [
                i.model_dump() for i in action_response_models if i
            ]
            operative = op.Step.respond_operative(
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
                act_req = co.ActionRequest(
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

    async def _invoke_imodel(
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
    ) -> tuple[co.Instruction, co.AssistantResponse]:
        """
        Execute model interaction with message management and response handling.

        Manages the core model interaction pipeline, including:
          1. Message preparation and context management
          2. Model invocation
          3. Response processing

        Importantly, this method deals with how messages are handled before
        passing into the LLM. Some models only allow certain conversation
        flows (user -> assistant -> user -> assistant). Some allow system
        messages. Some do not. This method prepares the messages for the
        model while preserving the LionAGI system state.

        Args:
            instruction: Primary instruction for the model
            guidance: Additional guidance context
            context: Context information
            sender: Source of the instruction
            recipient: Target of the instruction
            request_fields: Fields required in the request
            request_model: Model for structuring the request
            progress: History of operations
            imodel: Model instance to use
            tool_schemas: Available tool schemas
            images: List of images to process
            image_detail: Level of image processing detail
            **kwargs: Additional configuration parameters

        Returns:
            tuple:
              (co.Instruction, co.AssistantResponse)
              The processed instruction and the model's response
        """
        ins: co.Instruction = self.msgs.create_instruction(
            instruction=instruction,
            guidance=guidance,
            context=context,
            sender=sender or self.user or "user",
            recipient=recipient or self.ln_id,
            request_model=request_model,
            request_fields=request_fields,
            images=images,
            image_detail=image_detail,
            tool_schemas=tool_schemas,
        )

        progress = progress or self.msgs.progress
        messages: list[co.RoledMessage] = [
            self.msgs.messages[i] for i in progress
        ]

        use_ins = None
        if imodel.sequential_exchange:
            _to_use = []
            _action_responses: set[co.ActionResponse] = set()

            for i in messages:
                if isinstance(i, co.ActionResponse):
                    _action_responses.add(i)
                if isinstance(i, co.AssistantResponse):
                    _to_use.append(i.model_copy())
                if isinstance(i, co.Instruction):
                    if _action_responses:
                        j = i.model_copy()
                        d_ = [k.content.to_dict() for k in _action_responses]
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
                d_ = [k.content.to_dict() for k in _action_responses]
                for z in d_:
                    if z not in j.context:
                        j.context.append(z)
                use_ins = j

            if messages and len(messages) > 1:
                _msgs = [messages[0]]

                for i in messages[1:]:
                    if isinstance(i, co.AssistantResponse):
                        if isinstance(_msgs[-1], co.AssistantResponse):
                            _msgs[-1].response = (
                                f"{_msgs[-1].response}\n\n{i.response}"
                            )
                        else:
                            _msgs.append(i)
                    else:
                        if isinstance(_msgs[-1], co.AssistantResponse):
                            _msgs.append(i)
                messages = _msgs

        if self.msgs.system and "system" not in imodel.allowed_roles:
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
                if not isinstance(first_instruction, co.Instruction):
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
        imodel = imodel or self.imodel
        api_response = None

        if not hasattr(imodel, "parse_to_data_model"):
            api_response = await imodel.invoke(**kwargs)
        else:
            data_model = imodel.parse_to_data_model(**kwargs)
            api_response = await imodel.invoke(**data_model)

        res = co.AssistantResponse(
            assistant_response=api_response,
            sender=self,
            recipient=self.user,
        )
        return ins, res

    async def communicate(
        self,
        instruction: co.Instruction | JsonValue = None,
        guidance: JsonValue = None,
        context: JsonValue = None,
        sender: ID.SenderRecipient = None,
        recipient: ID.SenderRecipient = None,
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
    ) -> dict | BaseModel | str | None:
        """
        Execute a communication operation with model interaction and response
        parsing.

        This method handles the complete communication pipeline, including:
          1. Input validation and preparation
          2. Model interaction
          3. Response parsing and validation
          4. Result formatting

        Args:
            instruction: Primary instruction for communication
            guidance: Additional guidance for the model
            context: Supplementary context information
            sender: Source of the communication
            recipient: Target of the communication
            progress: History sequence to include
            request_model: Model for request structure
            request_fields: Required fields in request
            imodel: Model instance to use
            images: List of images to process
            image_detail: Level of image detail to process
            num_parse_retries: Number of parsing retry attempts
            parse_imodel: Model for parsing responses
            retry_kwargs: Additional retry configuration
            handle_validation: Validation failure handling mode
            skip_validation: Whether to skip validation
            clear_messages: Whether to clear message history
            response_format: Alias for request_model
            **kwargs: Additional configuration options

        Returns:
            Processed and validated response in requested format

        Raises:
            ValueError: If incompatible parameters or validation fails
        """
        if response_format and request_model:
            raise ValueError(
                "Cannot specify both response_format and request_model"
                "as they are aliases for the same parameter."
            )
        request_model = request_model or response_format

        imodel = imodel or self.imodel
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
        self.msgs.add_message(instruction=ins, remove_tool_schemas=True)
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
                        _d = validate_mapping(
                            _d,
                            break_down_pydantic_annotation(request_model),
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
                        _d = validate_mapping(
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
                        _d = validate_mapping(
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
                    _d = validate_mapping(
                        _d,
                        break_down_pydantic_annotation(request_model),
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
