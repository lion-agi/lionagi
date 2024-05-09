"""
the base directive
"""

import re
import contextlib
from abc import ABC
from typing import Any

from lionagi.libs.ln_convert import to_dict, to_list
from lionagi.libs.ln_nested import get_flattened_keys
from lionagi.libs.ln_func_call import lcall, alcall
from lionagi.libs.ln_parse import ParseUtil, StringMatch

from ..generic import Model
from ..message import Instruction


class BaseDirective(ABC):

    default_template = None

    def __init__(self, branch, model: Model = None, template_=None) -> None:
        self.branch = branch
        if model and isinstance(model, Model):
            branch.model = model
            self.model = model
        else:
            self.model = branch.model
        self.form_template = template_ or self.default_template

    @property
    def class_name(self) -> str:
        return self._class_name()

    @classmethod
    def _class_name(cls) -> str:
        return cls.__name__

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
        **kwargs,
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

        config = {**self.model.config, **kwargs}
        if sender is not None:
            config["sender"] = sender

        return config

    async def _call_chatcompletion(self, **kwargs):
        return await self.model.call_chat_completion(
            self.branch.to_chat_messages(), **kwargs
        )

    async def _process_chatcompletion(self, payload, completion, sender):
        if "choices" in completion:
            add_msg_config = {"assistant_response": completion["choices"][0]}
            if sender is not None:
                add_msg_config["sender"] = sender

            self.branch.datalogger.append(input_data=payload, output_data=completion)
            self.branch.add_message(**add_msg_config)
            self.branch.model.status_tracker.num_tasks_succeeded += 1
        else:
            self.branch.model.status_tracker.num_tasks_failed += 1

    @staticmethod
    def _process_model_response(content_, requested_fields):
        out_ = ""

        if len(content_.items()) == 1 and len(get_flattened_keys(content_)) == 1:
            key = get_flattened_keys(content_)[0]
            out_ = content_[key]

        if requested_fields:
            with contextlib.suppress(Exception):
                return StringMatch.force_validate_dict(out_, requested_fields)

        if isinstance(out_, str):
            with contextlib.suppress(Exception):
                match = re.search(r"```json\n({.*?})\n```", out_, re.DOTALL)
                if match:
                    out_ = ParseUtil.fuzzy_parse_json(match.group(1))

        return out_

    # TODO: modify direct tool invokation with action request/response
    async def _invoke_tools(self, content_=None, function_calling=None):
        if function_calling is None and content_ is not None:
            tool_uses = content_
            function_calling = lcall(
                [to_dict(i) for i in tool_uses["action_request"]],
                self.branch.tool_manager.parse_tool_response,
            )

        outs = await alcall(function_calling, self.branch.tool_manager.invoke)
        outs = to_list(outs, flatten=True)

        a = []
        for out_, f in zip(outs, function_calling):
            res = {
                "function": f[0],
                "arguments": f[1],
                "output": out_,
            }
            self.branch.add_message(response=res)
            a.append(res)

        return a

    async def _output(
        self,
        invoke_tool,
        out,
        requested_fields,
        function_calling=None,
        form=None,
        return_form=True,
    ):
        content_ = self.branch.messages[-1].content

        if invoke_tool:
            with contextlib.suppress(Exception):
                await self._invoke_tools(content_, function_calling=function_calling)

        response_ = self._process_model_response(content_, requested_fields)

        if form:
            form._process_response(response_)
            return form if return_form else form.outputs

        if out:
            return response_
