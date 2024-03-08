from typing import Any, Dict, List, Optional, Union
from lionagi.libs import to_dict, lcall, to_list, alcall, get_flattened_keys
from lionagi.core.message.schema import Instruction, System, Tool


class ChatFlow:

    @staticmethod
    async def call_chatcompletion(branch, sender=None, with_sender=False, **kwargs):
        messages = (
            branch.chat_messages
            if not with_sender
            else branch.chat_messages_with_sender
        )
        payload, completion = await branch.service.serve_chat(messages=messages, **kwargs)
        if "choices" in completion:
            add_msg_config = {"response": completion["choices"][0]}
            if sender is not None:
                add_msg_config["sender"] = sender

            branch.datalogger.append(input_data=payload, output_data=completion)
            branch.add_message(**add_msg_config)
            branch.status_tracker.num_tasks_succeeded += 1
        else:
            branch.status_tracker.num_tasks_failed += 1

    @staticmethod
    async def chat(
        branch,
        instruction: Union[Instruction, str],
        context: Optional[Any] = None,
        sender: Optional[str] = None,
        system: Optional[Union[System, str, Dict[str, Any]]] = None,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        out: bool = True,
        invoke: bool = True,
        **kwargs,
    ) -> Any:
        if system:
            branch.change_first_system_message(system)
        branch.add_message(instruction=instruction, context=context, sender=sender)

        if "tool_parsed" in kwargs:
            kwargs.pop("tool_parsed")
            tool_kwarg = {"tools": tools}
            kwargs = {**tool_kwarg, **kwargs}
        else:
            if tools and branch.has_tools:
                kwargs = branch.tool_manager.parse_tool(tools=tools, **kwargs)

        config = {**branch.llmconfig, **kwargs}
        if sender is not None:
            config.update({"sender": sender})

        await branch.call_chatcompletion(**config)

        async def _output():
            content_ = branch.last_message_content
            if invoke:
                try:
                    tool_uses = content_
                    func_calls = lcall(
                        [to_dict(i) for i in tool_uses["action_request"]],
                        branch.tool_manager.get_function_call,
                    )

                    outs = await alcall(func_calls, branch.tool_manager.invoke)
                    outs = to_list(outs, flatten=True)

                    for out_, f in zip(outs, func_calls):
                        branch.add_message(
                            response={
                                "function": f[0],
                                "arguments": f[1],
                                "output": out_,
                            }
                        )
                except:
                    pass
            if out:
                if (
                    len(content_.items()) == 1
                    and len(get_flattened_keys(content_)) == 1
                ):
                    key = get_flattened_keys(content_)[0]
                    return content_[key]
                return content_

        return await _output()

    @staticmethod
    async def ReAct(
        branch,
        instruction: Union[Instruction, str],
        context=None,
        sender=None,
        system=None,
        tools=None,
        num_rounds: int = 1,
        **kwargs,
    ):
        if tools is not None:
            if isinstance(tools, list) and isinstance(tools[0], Tool):
                branch.register_tools(tools)

        if branch.tool_manager.registry == {}:
            raise ValueError(
                "No tools found, You need to register tools for ReAct (reason-action)"
            )

        else:
            kwargs = branch.tool_manager.parse_tool(tools=True, **kwargs)

        i = 0
        while i < num_rounds:
            prompt = f"""you have {(num_rounds-i)*2} step left in current task. if available, integrate previous tool responses. perform reasoning and prepare action plan according to available tools only, apply divide and conquer technique.
            """
            instruct = {"Notice": prompt}

            if i == 0:
                instruct["Task"] = instruction
                await branch.chat(
                    instruction=instruct,
                    context=context,
                    system=system,
                    sender=sender,
                    **kwargs,
                )

            elif i > 0:
                await branch.chat(instruction=instruct, sender=sender, **kwargs)

            prompt = f"""
                you have {(num_rounds-i)*2-1} step left in current task, invoke tool usage to perform actions
            """
            await branch.chat(
                prompt, tool_choice="auto", tool_parsed=True, sender=sender, **kwargs
            )

            i += 1


        prompt = """
            present the final result to user
        """
        return await branch.chat(prompt, sender=sender, tool_parsed=True, **kwargs)


    @staticmethod
    async def auto_followup(
        branch,
        instruction: Union[Instruction, str],
        context=None,
        sender=None,
        system=None,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        max_followup: int = 3,
        out=True,
        **kwargs,
    ) -> None:
        if branch.tool_manager.registry != {} and tools:
            kwargs = branch.tool_manager.parse_tool(tools=tools, **kwargs)

        n_tries = 0
        while (max_followup - n_tries) > 0:
            prompt = f"""
                In the current task you are allowed a maximum of another {max_followup-n_tries} followup chats. 
                if further actions are needed, invoke tools usage. If you are done, present the final result 
                to user without further tool usage
            """
            if n_tries > 0:
                _out = await branch.chat(
                    prompt,
                    sender=sender,
                    tool_choice="auto",
                    tool_parsed=True,
                    **kwargs,
                )
                n_tries += 1

                if not branch._is_invoked():
                    return _out if out else None

            elif n_tries == 0:
                instruct = {"notice": prompt, "task": instruction}
                out = await branch.chat(
                    instruct,
                    context=context,
                    system=system,
                    sender=sender,
                    tool_choice="auto",
                    tool_parsed=True,
                    **kwargs,
                )
                n_tries += 1


        if branch._is_invoked():
            """
            In the current task, you are at your last step, present the final result to user
            """
            return await branch.chat(
                instruction, sender=sender, tool_parsed=True, **kwargs
            )
