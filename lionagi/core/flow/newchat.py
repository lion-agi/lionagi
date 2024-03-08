from typing import Any, Dict, List, Optional, Union

from lionagi.libs import to_dict, lcall, to_list, alcall, get_flattened_keys
from lionagi.core.message.schema import Instruction, System, Tool


class BaseChatFlow:
    
    def __init__(self, branch):
        self.branch = branch
        
    def process_chatcompletion(self, payload, completion, sender):
        if "choices" in completion:
            add_msg_config = {"response": completion["choices"][0]}
            if sender is not None:
                add_msg_config["sender"] = sender

            self.branch.datalogger.append(input_data=payload, output_data=completion)
            self.branch.add_message(**add_msg_config)
            self.branch.status_tracker.num_tasks_succeeded += 1
        else:
            self.branch.status_tracker.num_tasks_failed += 1
        
    async def call_chatcompletion(self, sender=None, with_sender=False, **kwargs):
        messages = (
            self.branch.chat_messages
            if not with_sender
            else self.branch.chat_messages_with_sender
        )
        payload, completion = await self.branch.service.serve_chat(messages=messages, **kwargs)
        self.process_chatcompletion(payload, completion, sender)
    
    def create_chat_config(
        self, 
        instruction: Instruction | str,
        context: Optional[Any] = None,
        sender: Optional[str] = None,
        system: Optional[Union[System, str, Dict[str, Any]]] = None,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        **kwargs,
    ) -> Any:

        if system:
            self.branch.change_first_system_message(system)
        self.branch.add_message(instruction=instruction, context=context, sender=sender)

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

    def get_tool_calls(self, content_):
        tool_uses = content_
        func_calls = lcall(
            [to_dict(i) for i in tool_uses["action_request"]],
            self.branch.tool_manager.get_function_call,
        )
        
        return func_calls

    @staticmethod
    async def invoke_tools(self, func_calls):
        outs = await alcall(func_calls, self.branch.tool_manager.invoke)
        outs = to_list(outs, flatten=True)

        for out_, f in zip(outs, func_calls):
            self.branch.add_message(
                response={
                    "function": f[0],
                    "arguments": f[1],
                    "output": out_,
                }
            )

    async def output(self, invoke=True, out=True):
        content_ = self.branch.last_message_content
        if invoke:
            try:
                tool_calls = self.get_tool_calls(content_)
                await self.invoke_tools(tool_calls)
            except:
                pass
        if out:
            return self.return_response(content_)

    
    @staticmethod
    def return_response(content_):            
        if (
            len(content_.items()) == 1
            and len(get_flattened_keys(content_)) == 1
        ):
            key = get_flattened_keys(content_)[0]
            return content_[key]
        return content_

    async def chat(
        self,
        instruction: Union[Instruction, str],
        context: Optional[Any] = None,
        sender: Optional[str] = None,
        system: Optional[Union[System, str, Dict[str, Any]]] = None,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        out: bool = True,
        invoke: bool = True,
        **kwargs,
    ) -> Any:

        config = self.create_chat_config(
            instruction, context, sender, system, tools, **kwargs
        )

        await self.call_chatcompletion(**config)
        return self.output(invoke, out)



class ReActFlow(BaseChatFlow):
    
    def __init__(self, branch):
        super().__init__(branch)
    
    def create_config(self, tools, **kwargs):
        
        if tools is not None:
            if isinstance(tools, list) and isinstance(tools[0], Tool):
                self.branch.tool_manager.register_tools(tools)

        if not self.branch.tool_manager.has_tools:
            raise ValueError(
                "No tools found, You need to register tools for ReAct (reason-action)"
            )

        return self.branch.tool_manager.parse_tool(tools=True, **kwargs)

    async def ReAct(
        self,
        instruction: Union[Instruction, str],
        context=None,
        sender=None,
        system=None,
        tools=None,
        num_rounds: int = 1,
        **kwargs,
    ):

        config = self.create_config(tools, **kwargs)

        i = 0
        while i < num_rounds:
            prompt = f"""you have {(num_rounds-i)*2} step left in current task. if available, 
            integrate previous tool responses. perform reasoning and prepare action plan 
            according to available tools only, apply divide and conquer technique.
            """
            instruct = {"Notice": prompt}

            if i == 0:
                instruct["Task"] = instruction
                await self.chat(
                    instruction=instruct,
                    context=context,
                    system=system,
                    sender=sender,
                    **kwargs,
                )

            elif i > 0:
                await self.chat(instruction=instruct, sender=sender, **config)

            prompt = f"""
                you have {(num_rounds-i)*2-1} step left in current task, invoke tool usage to perform actions
            """
            await self.chat(
                prompt, tool_choice="auto", tool_parsed=True, sender=sender, **config
            )

            i += 1

        prompt = "present the final result to user"
        return await self.chat(prompt, sender=sender, tool_parsed=True, **config)
