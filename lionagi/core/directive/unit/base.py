"""
the base directive
"""

import asyncio
import re
import contextlib
from typing import Any

from lionagi.libs.ln_parse import ParseUtil, StringMatch
from lionagi.libs.ln_func_call import rcall, CallDecorator as cd, Throttle

from lionagi.core.generic.abc import Field, Directive
from lionagi.core.generic import iModel
from lionagi.core.message import Instruction
from lionagi.core.message.util import _parse_action_request
from lionagi.core.validator.validator import Validator
from lionagi.core.report.form import Form



class Chat(Directive):

    default_template = None
    
    def __init__(
        self, branch, imodel: iModel = None, template=None, rulebook=None
    ) -> None:
        self.branch = branch
        if imodel and isinstance(imodel, iModel):
            branch.imodel = imodel
            self.imodel = imodel
        else:
            self.imodel = branch.imodel
        self.form_template = template or self.default_template
        self.validator = Validator(rulebook=rulebook) if rulebook else Validator()
        
    async def direct(self, *args, **kwargs):
        return await self.chat(*args, **kwargs)
    
    async def chat(
        self,
        instruction=None,  # additional instruction
        context=None,  # context to perform the instruction on
        *,
        system=None,  # optionally swap system message
        sender=None,  # sender of the instruction, default "user"
        recipient=None,  # recipient of the instruction, default "branch.ln_id"
        branch=None,
        requested_fields=None,  # fields to request from the context, default None
        form=None,  # form to create instruction from, default None,
        tools=False,  # the tools to use, use True to consider all tools, no tools by default
        invoke_tool=True,  # whether to invoke the tool when function calling, default True
        return_form=True,  # whether to return the form if a form is passed in, otherwise return a dict/str
        strict=False,  # whether to strictly enforce the rule validation, default False
        rulebook=None,  # the rulebook to use for validation, default None, use default rulebook
        imodel=None,  # the optinally swappable iModel for the commands, otherwise self.branch.imodel
        clear_messages=False,
        use_annotation=True,  # whether to use annotation as rule qualifier, default True, (need rulebook if False)
        retries: int = 3,  # kwargs for rcall, number of retries if failed
        delay: float = 0,  # number of seconds to delay before retrying
        backoff_factor: float = 1,  # exponential backoff factor, default 1 (no backoff)
        default=None,  # default value to return if all retries failed
        timeout: (
            float | None
        ) = None,  # timeout for the rcall, default None (no timeout)
        timing: bool = False,  # if timing will return a tuple (output, duration)
        max_concurrency: int = 10_000,  # max concurrency for the chat, default 10_000 (global max concurrency)
        throttle_period: int = None,
        return_branch=False,
        **kwargs,
    ):

        @cd.max_concurrency(max_concurrency)
        async def _inner(**_kwargs):
            return await rcall(self._chat, **_kwargs)

        if throttle_period:
            throttle = Throttle(period=throttle_period)
            _inner = throttle(_inner)

        a = await _inner(
            context=context,
            instruction=instruction,
            system=system,
            sender=sender,
            recipient=recipient,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            invoke_tool=invoke_tool,
            return_form=return_form,
            strict=strict,
            rulebook=rulebook,
            imodel=imodel,
            use_annotation=use_annotation,
            retries=retries,
            delay=delay,
            backoff_factor=backoff_factor,
            default=default,
            timeout=timeout,
            timing=timing,
            branch=branch,
            clear_messages=clear_messages,
            return_branch=return_branch,
            **kwargs,
        )

        if isinstance(a, tuple) and isinstance(a[0], tuple):
            return a[0][0], a[1]
        if isinstance(a, tuple) and not isinstance(a[0], tuple):
            return a[0]

    async def _chat(
        self,
        instruction=None,
        *,
        system=None,
        context=None,
        sender=None,
        recipient=None,
        requested_fields=None,
        form=None,
        tools=False,
        invoke_tool=True,
        return_form=True,
        strict=False,
        rulebook=None,
        imodel=None,
        use_annotation=True,
        branch=None,
        clear_messages=False,
        return_branch=False,
        **kwargs,
    ):
        branch = branch or self.branch
        if clear_messages:
            branch.clear()

        config = self._create_chat_config(
            system=system,
            instruction=instruction,
            context=context,
            sender=sender,
            recipient=recipient,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            **kwargs,
        )

        payload, completion = await self._call_chatcompletion(
            imodel=imodel, branch=branch, **config
        )

        out_ = await self._output(
            payload=payload,
            completion=completion,
            sender=sender,
            invoke_tool=invoke_tool,
            requested_fields=requested_fields,
            form=form,
            return_form=return_form,
            strict=strict,
            rulebook=rulebook,
            use_annotation=use_annotation,
        )

        return out_, branch if return_branch else out_

    def _create_chat_config(
        self,
        system=None,
        instruction=None,
        context=None,
        sender=None,
        recipient=None,
        requested_fields=None,
        form=None,
        tools=False,
        **kwargs,  # additional config for the model
    ) -> Any:

        if system:
            self.branch.add_message(system=system)

        if not form:
            self.branch.add_message(
                instruction=instruction,
                context=context,
                sender=sender,
                recipient=recipient,
                requested_fields=requested_fields,
            )

        else:
            instruct_ = Instruction.from_form(form)
            self.branch.add_message(instruction=instruct_)

        if "tool_parsed" in kwargs:
            kwargs.pop("tool_parsed")
            tool_kwarg = {"tools": tools}
            kwargs = tool_kwarg | kwargs

        elif tools and self.branch.has_tools:
            kwargs = self.branch.tool_manager.parse_tool(tools=tools, **kwargs)

        config = {**self.imodel.config, **kwargs}
        if sender is not None:
            config["sender"] = sender

        return config

    async def _call_chatcompletion(self, imodel=None, branch=None, **kwargs):
        imodel = imodel or self.imodel
        branch = branch or self.branch
        return await imodel.call_chat_completion(branch.to_chat_messages(), **kwargs)

    async def _process_chatcompletion(
        self,
        payload,
        completion,
        sender,
        invoke_tool=True,
        branch=None,
        action_request=None,
    ):
        branch = branch or self.branch
        # process the raw chat completion response
        _msg = None
        if "choices" in completion:

            aa = payload.pop("messages", None)
            branch.update_last_instruction_meta(payload)
            msg = completion.pop("choices", None)
            if msg and isinstance(msg, list):
                msg = msg[0]

            if isinstance(msg, dict):
                _msg = msg.pop("message", None)
                completion.update(msg)

                branch.add_message(
                    assistant_response=_msg, metadata=completion, sender=sender
                )
                branch.imodel.status_tracker.num_tasks_succeeded += 1
        else:
            branch.imodel.status_tracker.num_tasks_failed += 1

        return await self._process_action_request(
            _msg=_msg,
            branch=branch,
            invoke_tool=invoke_tool,
            action_request=action_request,
        )

    async def _process_action_request(
        self, _msg=None, branch=None, invoke_tool=True, action_request=None
    ):
        # if the assistant response contains action request, we add each as a message to branch
        action_request = action_request or _parse_action_request(_msg)

        if action_request is None:
            return _msg if _msg else False

        if action_request:
            for i in action_request:
                if i.function in branch.tool_manager.registry:
                    i.recipient = branch.tool_manager.registry[
                        i.function
                    ].ln_id  # recipient is the tool
                else:
                    raise ValueError(f"Tool {i.function} not found in registry")
                branch.add_message(action_request=i, recipient=i.recipient)

        if invoke_tool:
            # invoke tools and add action response to branch
            tasks = []
            for i in action_request:
                tool = branch.tool_manager.registry[i.function]
                tasks.append(asyncio.create_task(tool.invoke(i.arguments)))

            results = await asyncio.gather(*tasks)

            for idx, item in enumerate(results):
                branch.add_message(
                    action_request=action_request[idx],
                    func_outputs=item,
                    sender=action_request[idx].recipient,
                    recipient=action_request[idx].sender,
                )

        return None

    async def _output(
        self,
        payload,
        completion,
        sender,
        invoke_tool,
        requested_fields,
        form=None,
        return_form=True,
        strict=False,
        rulebook=None,
        use_annotation=True,
        template_name=None,
    ) -> Any:
        _msg = await self._process_chatcompletion(
            payload=payload,
            completion=completion,
            sender=sender,
            invoke_tool=invoke_tool,
        )

        if _msg is None:
            return None

        response_ = self._process_model_response(_msg, requested_fields)

        if form:
            validator = None

            if rulebook is None:
                validator = self.validator
            else:
                validator = Validator(rulebook=rulebook)

            form = await validator.validate_response(
                form=form,
                response=response_,
                strict=strict,
                use_annotation=use_annotation,
            )
            if template_name:
                form.template_name = template_name

            return (
                form
                if return_form
                else {
                    i: form.work_fields[i]
                    for i in form.requested_fields
                    if form.work_fields[i] is not None
                }
            )

        return response_

    @staticmethod
    def _process_model_response(content_, requested_fields):
        out_ = ""

        if "content" in content_:
            out_ = content_["content"]

        if requested_fields:
            with contextlib.suppress(Exception):
                return StringMatch.force_validate_dict(out_, requested_fields)

        if isinstance(out_, str):
            with contextlib.suppress(Exception):
                match = re.search(r"```json\n({.*?})\n```", out_, re.DOTALL)
                if match:
                    out_ = ParseUtil.fuzzy_parse_json(match.group(1))

        return out_ or content_


class UnitTemplate(Form):

    confidence_score: float = Field(
        None,
        description="a numeric score between 0 to 1 formatted in num:0.2f, 1 being very confident and 0 being not confident at all, just guessing",
        validation_kwargs={
            "upper_bound": 1,
            "lower_bound": 0,
            "num_type": float,
            "precision": 2,
        },
    )

    reason: str = Field(
        default_factory=str,
        description="brief reason for the given output, format: This is my best response because ...",
    )
