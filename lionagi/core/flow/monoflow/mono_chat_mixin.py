from abc import ABC
from typing import Any

from lionagi.core.messages.schema import Instruction
from lionagi.core.schema.base_node import TOOL_TYPE
from lionagi.libs import (
    ln_nested as nested,
    ln_func_call as func_call,
    ln_convert as convert,
)
from lionagi.libs.ln_parse import ParseUtil, StringMatch


class MonoChatConfigMixin(ABC):

    def _create_chat_config(
        self,
        instruction: Instruction | str | dict[str, Any],
        context: Any | None = None,
        sender: str | None = None,
        system: str | dict[str, Any] | None = None,
        tools: TOOL_TYPE = False,
        output_fields=None,
        **kwargs,
    ) -> Any:

        if system:
            self.branch.change_first_system_message(system)
        self.branch.add_message(
            instruction=instruction,
            context=context,
            sender=sender,
            output_fields=output_fields,
        )

        if "tool_parsed" in kwargs:
            kwargs.pop("tool_parsed")
            tool_kwarg = {"tools": tools}
            kwargs = {**tool_kwarg, **kwargs}
        else:
            if tools and self.branch.has_tools:
                kwargs = self.branch.tool_manager.parse_tool(tools=tools, **kwargs)

        config = {**self.branch.llmconfig, **kwargs}
        if sender is not None:
            config.update({"sender": sender})

        return config


class MonoChatInvokeMixin(ABC):
    async def _output(self, invoke, out, output_fields):
        content_ = self.branch.last_message_content

        if invoke:
            try:
                await self._invoke_tools(content_)
            except:
                pass
        if out:
            return self._return_response(content_, output_fields)

    @staticmethod
    def _return_response(content_, output_fields):
        out_ = ""

        if len(content_.items()) == 1 and len(nested.get_flattened_keys(content_)) == 1:
            key = nested.get_flattened_keys(content_)[0]
            out_ = content_[key]

        if output_fields:
            try:
                if isinstance(out_, dict):
                    out_ = ParseUtil.md_to_json(out_.values())
                else:
                    out_ = ParseUtil.md_to_json(out_)
                out_ = StringMatch.correct_keys(output_fields=output_fields, out_=out_)
            except:
                pass

        return out_

    async def _invoke_tools(self, content_):
        tool_uses = content_
        func_calls = func_call.lcall(
            [convert.to_dict(i) for i in tool_uses["action_request"]],
            self.branch.tool_manager.get_function_call,
        )

        outs = await func_call.alcall(func_calls, self.branch.tool_manager.invoke)
        outs = convert.to_list(outs, flatten=True)

        for out_, f in zip(outs, func_calls):
            self.branch.add_message(
                response={
                    "function": f[0],
                    "arguments": f[1],
                    "output": out_,
                }
            )

    def _process_chatcompletion(self, payload, completion, sender):
        if "choices" in completion:
            add_msg_config = {"response": completion["choices"][0]}
            if sender is not None:
                add_msg_config["sender"] = sender

            self.branch.datalogger.append(input_data=payload, output_data=completion)
            self.branch.add_message(**add_msg_config)
            self.branch.status_tracker.num_tasks_succeeded += 1
        else:
            self.branch.status_tracker.num_tasks_failed += 1

    async def _call_chatcompletion(self, sender=None, with_sender=False, **kwargs):
        messages = (
            self.branch.chat_messages
            if not with_sender
            else self.branch.chat_messages_with_sender
        )
        payload, completion = await self.branch.service.serve_chat(
            messages=messages, **kwargs
        )
        self._process_chatcompletion(payload, completion, sender)


class MonoChatMixin(MonoChatConfigMixin, MonoChatInvokeMixin, ABC):
    pass
