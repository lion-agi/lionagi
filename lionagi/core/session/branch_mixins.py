# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from abc import ABC
from collections.abc import Callable
from typing import Literal

from pydantic import JsonValue

from lionagi.core.typing import (
    ID,
    UNDEFINED,
    BaseModel,
    FieldModel,
    NewModelParams,
)
from lionagi.integrations.litellm_.imodel import LiteiModel
from lionagi.integrations.pydantic_ import break_down_pydantic_annotation
from lionagi.libs.func.types import alcall
from lionagi.libs.parse import to_json, validate_mapping
from lionagi.protocols.operatives import (
    ActionRequestModel,
    ActionResponseModel,
    Operative,
    Step,
)
from lionagi.service import iModel

from ..action.action_manager import FUNCTOOL, Tool
from ..communication.types import (
    ActionRequest,
    ActionResponse,
    AssistantResponse,
    Instruction,
)


class BranchActionMixin(ABC):

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

            result = await self.acts.invoke(action_request)
            tool = self.acts.registry[action_request.function]

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

    def get_tool_schema(
        self,
        tools: str | Tool | list[Tool | str] | bool,
        auto_register: bool = True,
    ) -> dict:
        tools = tools if isinstance(tools, list) else [tools]
        if auto_register:
            for i in tools:
                if isinstance(i, Tool | Callable) and i not in self.acts:
                    self.acts.register_tools(i)
        return self.acts.get_tool_schema(tools)


class BranchOperationMixin(ABC):
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
        imodel: iModel | LiteiModel = None,
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
        retry_imodel: iModel | LiteiModel = None,
        retry_kwargs: dict = {},
        auto_retry_parse: bool = True,
        field_models: list[FieldModel] | None = None,
        skip_validation: bool = False,
        tools: str | Tool | list[Tool | str] | bool = None,
        request_params: NewModelParams = None,
        request_param_kwargs: dict = {},
        response_params: NewModelParams = None,
        response_param_kwargs: dict = {},
        **kwargs,
    ) -> list | BaseModel | None | dict | str:
        imodel = imodel or self.imodel
        retry_imodel = retry_imodel or imodel

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
        parse_imodel = self.parse_imodel or imodel or self.imodel
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
            if isinstance(parse_imodel, iModel):
                api_request = parse_imodel.parse_to_data_model(**api_request)

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
        imodel: iModel | LiteiModel = None,
        tool_schemas=None,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        **kwargs,
    ) -> tuple[Instruction, AssistantResponse]:

        ins = self.msgs.create_instruction(
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
        messages = [self.msgs.messages[i] for i in progress]

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
                if not isinstance(first_instruction, Instruction):
                    raise ValueError(
                        "First message in progress must be an Instruction or System"
                    )
                first_instruction = first_instruction.model_copy()
                first_instruction.guidance = self.msgs.system.system_info + (
                    first_instruction.guidance or ""
                )
                messages[0] = first_instruction

        else:
            messages.append(ins)

        kwargs["messages"] = [i.chat_msg for i in messages]
        imodel = imodel or self.imodel
        api_response = None

        if isinstance(imodel, LiteiModel):
            api_response = await imodel.invoke(**kwargs)
        elif isinstance(imodel, iModel):
            data_model = imodel.parse_to_data_model(**kwargs)
            api_response = await imodel.invoke(**data_model)

        res = AssistantResponse(
            assistant_response=api_response,
            sender=self,
            recipient=self.user,
        )
        return ins, res

    async def communicate(
        self,
        instruction: Instruction | JsonValue = None,
        guidance: JsonValue = None,
        context: JsonValue = None,
        sender: ID.SenderRecipient = None,
        recipient: ID.SenderRecipient = None,
        progress: ID.IDSeq = None,
        request_model: type[BaseModel] | BaseModel = None,
        request_fields: dict | list[str] = None,
        imodel: iModel | LiteiModel = None,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        tools: str | FUNCTOOL | list[FUNCTOOL | str] | bool = None,
        num_parse_retries: int = 0,
        retry_imodel: iModel | LiteiModel = None,
        retry_kwargs: dict = {},
        handle_validation: Literal[
            "raise", "return_value", "return_none"
        ] = "return_value",
        skip_validation: bool = False,
        clear_messages: bool = False,
        invoke_action: bool = True,
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

        imodel = imodel or self.imodel
        retry_imodel = retry_imodel or imodel
        if clear_messages:
            self.msgs.clear_messages()

        if num_parse_retries > 5:
            logging.warning(
                f"Are you sure you want to retry {num_parse_retries} "
                "times? lowering retry attempts to 5. Suggestion is under 3"
            )
            num_parse_retries = 5

        tool_schemas = None
        if invoke_action and tools:
            tool_schemas = self.get_tool_schema(tools)

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
            tool_schemas=tool_schemas,
            **kwargs,
        )
        await self.msgs.a_add_message(instruction=ins)
        await self.msgs.a_add_message(assistant_response=res)

        action_request_models = None
        action_response_models = None

        if skip_validation:
            return res.response

        if invoke_action and tools:
            action_request_models = ActionRequestModel.create(res.response)

        if action_request_models and invoke_action:
            action_response_models = await alcall(
                action_request_models,
                self.invoke_action,
                suppress_errors=True,
            )

        if action_request_models and not action_response_models:
            for i in action_request_models:
                await self.msgs.a_add_message(
                    action_request_model=i,
                    sender=self,
                    recipient=None,
                )

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
                            await self.msgs.a_add_message(
                                assistant_response=res
                            )
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
                                await self.msgs.a_add_message(
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
                        f"format, retrying... with {retry_imodel.model}"
                    )
                    _, res = await self._invoke_imodel(
                        instruction="reformat text into specified model",
                        context=res.response,
                        request_model=request_model,
                        request_fields=request_fields,
                        progress=[],
                        imodel=retry_imodel or imodel,
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
