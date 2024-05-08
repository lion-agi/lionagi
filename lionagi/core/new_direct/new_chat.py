import re
from abc import ABC
import contextlib
from typing import Any

from lionagi.libs.ln_convert import to_dict, to_list
from lionagi.libs.ln_nested import get_flattened_keys
from lionagi.libs.ln_func_call import lcall, alcall
from lionagi.libs.ln_parse import ParseUtil, StringMatch

from ..generic import Model
from ..message import Instruction
from ..branch.branch import Branch


class BaseDirective(ABC):

    @classmethod
    def class_name(cls) -> str:
        """
        Returns the class name of the flow.
        """
        return cls.__name__


class MonoDirect(BaseDirective):

    def __init__(self, branch: Branch, model: Model=None) -> None:
        self.branch = branch or Branch()
        if model and isinstance(model, Model):
            branch.model = model
            self.model = model
        else:
            self.model = branch.model
        
    def _create_chat_config(
        self,
        system=None,  # system node - JSON serializable
        instruction=None,  # Instruction node - JSON serializable
        context=None,  # JSON serializable
        sender=None,  # str
        recipient=None,  # str
        requested_fields=None,  # dict[str, str]
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
                
        response_ = self._return_response(content_, requested_fields)

        if form:
            form._process_response(response_)
            return form if return_form else form.outputs

        if out:
            return response_

    @staticmethod
    def _return_response(content_, requested_fields):
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
                self.branch.tool_manager.get_function_call,
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

    def _process_chatcompletion(self, payload, completion, sender):
        if "choices" in completion:
            add_msg_config = {"response": completion["choices"][0]}
            if sender is not None:
                add_msg_config["sender"] = sender

            self.branch.datalogger.append(input_data=payload, output_data=completion)
            self.branch.add_message(**add_msg_config)
            self.branch.model.status_tracker.num_tasks_succeeded += 1
        else:
            self.branch.model.status_tracker.num_tasks_failed += 1

    async def _call_chatcompletion(self, **kwargs):
        return await self.model.predict(**kwargs)

    async def chat(
        self,
        system=None,  # system node - JSON serializable
        instruction=None,  # Instruction node - JSON serializable
        context=None,  # JSON serializable
        sender=None,  # str
        recipient=None,  # str
        requested_fields=None,  # dict[str, str]
        form=None,
        tools=False,
        invoke_tool=True, 
        out=True,
        **kwargs,
    ) -> Any:

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

        await self._call_chatcompletion(**config)

        return await self._output(
            invoke_tool=invoke_tool,
            out=out,
            requested_fields=requested_fields,
            form=form,
        )
