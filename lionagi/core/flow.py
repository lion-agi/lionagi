from typing import Any, Dict, List, Optional, Union
from lionagi.utils import as_dict, lcall, to_list, alcall, get_flattened_keys
from lionagi.schema import Tool
from lionagi.core.messages import Instruction, System


class ChatFlow:

    @staticmethod
    async def call_chatcompletion(branch, sender=None, with_sender=False, tokenizer_kwargs={}, **kwargs):
        """
        Asynchronously calls the chat completion service with the current message queue.
        
        Args:
            branch: The Branch instance calling the service.
            sender (Optional[str]): The name of the sender to include in chat completions.
            with_sender (bool): If True, includes sender information in messages.
            tokenizer_kwargs (dict): Keyword arguments for the tokenizer used in chat completion.
            **kwargs: Arbitrary keyword arguments for the chat completion service.

        Examples:
            >>> await ChatFlow.call_chatcompletion(branch, sender="user")
        """
        messages = branch.chat_messages if not with_sender else branch.chat_messages_with_sender
        payload, completion = await branch.service.serve_chat(
            messages=messages, tokenizer_kwargs=tokenizer_kwargs, **kwargs
        )
        if "choices" in completion:
            add_msg_config = {"response":completion['choices'][0]}
            if sender is not None:
                add_msg_config["sender"] = sender

            branch.logger.add_entry({"input": payload, "output": completion})
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
        **kwargs) -> Any:

        """
        a chat conversation with LLM, processing instructions and system messages, optionally invoking tools.

        Args:
            branch: The Branch instance to perform chat operations.
            instruction (Union[Instruction, str]): The instruction for the chat.
            context (Optional[Any]): Additional context for the chat.
            sender (Optional[str]): The sender of the chat message.
            system (Optional[Union[System, str, Dict[str, Any]]]): System message to be processed.
            tools (Union[bool, Tool, List[Tool], str, List[str]]): Specifies tools to be invoked.
            out (bool): If True, outputs the chat response.
            invoke (bool): If True, invokes tools as part of the chat.
            **kwargs: Arbitrary keyword arguments for chat completion.

        Examples:
            >>> await ChatFlow.chat(branch, "Ask about user preferences")
        """
        if system:
            branch.change_first_system_message(system)
        branch.add_message(instruction=instruction, context=context, sender=sender)

        if 'tool_parsed' in kwargs:
            kwargs.pop('tool_parsed')
            tool_kwarg = {'tools': tools}
            kwargs = {**tool_kwarg, **kwargs}
        else:
            if tools and branch.has_tools:
                kwargs = branch.tool_manager._tool_parser(tools=tools, **kwargs)

        config = {**branch.llmconfig, **kwargs}
        if sender is not None: 
            config.update({"sender": sender})
        
        await branch.call_chatcompletion(**config)
        
        async def _output():
            content_ = as_dict(branch.messages.content.iloc[-1])
            if invoke:
                try:
                    tool_uses = content_
                    func_calls = lcall(
                        [as_dict(i) for i in tool_uses["action_list"]], 
                        branch.tool_manager.get_function_call
                    )
                    
                    outs = await alcall(func_calls, branch.tool_manager.invoke)
                    outs = to_list(outs, flatten=True)

                    for out_, f in zip(outs, func_calls):
                        branch.add_message(
                            response={
                                "function": f[0], 
                                "arguments": f[1], 
                                "output": out_
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
        context = None,
        sender = None,
        system = None,
        tools = None, 
        num_rounds: int = 1,
        **kwargs 
    ):
        """
        Performs a reason-action cycle with optional tool invocation over multiple rounds.

        Args:
            branch: The Branch instance to perform ReAct operations.
            instruction (Union[Instruction, str]): Initial instruction for the cycle.
            context: Context relevant to the instruction.
            sender (Optional[str]): Identifier for the message sender.
            system: Initial system message or configuration.
            tools: Tools to be registered or used during the cycle.
            num_rounds (int): Number of reason-action cycles to perform.
            **kwargs: Additional keyword arguments for customization.

        Examples:
            >>> await ChatFlow.ReAct(branch, "Analyze user feedback", num_rounds=2)
        """
        if tools is not None:
            if isinstance(tools, list) and isinstance(tools[0], Tool):
                branch.register_tools(tools)
        
        if branch.tool_manager.registry == {}:
            raise ValueError("No tools found, You need to register tools for ReAct (reason-action)")
        
        else:
            kwargs = branch.tool_manager._tool_parser(tools=True, **kwargs)

        out = ''
        i = 0
        while i < num_rounds:
            prompt = f"""you have {(num_rounds-i)*2} step left in current task. if available, integrate previous tool responses. perform reasoning and prepare action plan according to available tools only, apply divide and conquer technique.
            """ 
            instruct = {"Notice": prompt}
            
            if i == 0:
                instruct["Task"] = instruction
                out = await branch.chat(
                    instruction=instruct, context=context, 
                    system=system, sender=sender, **kwargs
                )
        
            elif i >0:
                out = await branch.chat(
                    instruction=instruct, sender=sender, **kwargs
                )
                
            prompt = f"""
                you have {(num_rounds-i)*2-1} step left in current task, invoke tool usage to perform actions
            """
            out = await branch.chat(prompt, tool_choice="auto", tool_parsed=True, sender=sender, **kwargs)

            i += 1
            if not branch._is_invoked():
                return out
    
        if branch._is_invoked():
            prompt = """
                present the final result to user
            """
            return await branch.chat(prompt, sender=sender, tool_parsed=True, **kwargs)
        else:
            return out

    @staticmethod
    async def auto_followup(
        branch,
        instruction: Union[Instruction, str],
        context = None,
        sender = None,
        system = None,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        max_followup: int = 3,
        out=True, 
        **kwargs
    ) -> None:
        """
        Automatically performs follow-up actions based on chat interactions and tool invocations.

        Args:
            branch: The Branch instance to perform follow-up operations.
            instruction (Union[Instruction, str]): The initial instruction for follow-up.
            context: Context relevant to the instruction.
            sender (Optional[str]): Identifier for the message sender.
            system: Initial system message or configuration.
            tools: Specifies tools to be considered for follow-up actions.
            max_followup (int): Maximum number of follow-up chats allowed.
            out (bool): If True, outputs the result of the follow-up action.
            **kwargs: Additional keyword arguments for follow-up customization.

        Examples:
            >>> await ChatFlow.auto_followup(branch, "Finalize report", max_followup=2)
        """
        if branch.tool_manager.registry != {} and tools:
            kwargs = branch.tool_manager._tool_parser(tools=tools, **kwargs)

        n_tries = 0
        while (max_followup - n_tries) > 0:
            prompt = f"""
                In the current task you are allowed a maximum of another {max_followup-n_tries} followup chats. 
                if further actions are needed, invoke tools usage. If you are done, present the final result 
                to user without further tool usage
            """
            if n_tries > 0:
                _out = await branch.chat(prompt, sender=sender, tool_choice="auto", tool_parsed=True, **kwargs)
                n_tries += 1
                
                if not branch._is_invoked():
                    return _out if out else None
                                
            elif n_tries == 0:
                instruct = {"notice": prompt, "task": instruction}
                out = await branch.chat(
                    instruct, context=context, system=system, sender=sender, tool_choice="auto", 
                    tool_parsed=True, **kwargs
                )
                n_tries += 1
                
                if not branch._is_invoked():
                    return _out if out else None

        if branch._is_invoked():
            """
            In the current task, you are at your last step, present the final result to user
            """
            return await branch.chat(instruction, sender=sender, tool_parsed=True, **kwargs)

    # async def followup(
    #     self,
    #     instruction: Union[Instruction, str],
    #     context = None,
    #     sender = None,
    #     system = None,
    #     tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
    #     max_followup: int = 3,
    #     out=True, 
    #     **kwargs
    # ) -> None:

    #     """
    #     auto tool usages until LLM decides done. Then presents final results. 
    #     """

    #     if self.tool_manager.registry != {} and tools:
    #         kwargs = self.tool_manager._tool_parser(tools=tools, **kwargs)

    #     n_tries = 0
    #     while (max_followup - n_tries) > 0:
    #         prompt = f"""
    #             In the current task you are allowed a maximum of another {max_followup-n_tries} followup chats. 
    #             if further actions are needed, invoke tools usage. If you are done, present the final result 
    #             to user without further tool usage.
    #         """
    #         if n_tries > 0:
    #             _out = await self.chat(prompt, sender=sender, tool_choice="auto", tool_parsed=True, **kwargs)
    #             n_tries += 1
                
    #             if not self._is_invoked():
    #                 return _out if out else None
                                
    #         elif n_tries == 0:
    #             instruct = {"notice": prompt, "task": instruction}
    #             out = await self.chat(
    #                 instruct, context=context, system=system, sender=sender, tool_choice="auto", 
    #                 tool_parsed=True, **kwargs
    #             )
    #             n_tries += 1
                
    #             if not self._is_invoked():
    #                 return _out if out else None
    
        # async def auto_ReAct(
    #     self,
    #     instruction: Union[Instruction, str],
    #     context = None,
    #     sender = None,
    #     system = None,
    #     tools = None, 
    #     max_rounds: int = 1,
        
    #     fallback: Optional[Callable] = None,
    #     fallback_kwargs: Optional[Dict] = None,
    #     **kwargs 
    # ):
    #     if tools is not None:
    #         if isinstance(tools, list) and isinstance(tools[0], Tool):
    #             self.register_tools(tools)
        
    #     if self.tool_manager.registry == {}:
    #         raise ValueError("No tools found, You need to register tools for ReAct (reason-action)")
        
    #     else:
    #         kwargs = self.tool_manager._tool_parser(tools=True, **kwargs)

    #     i = 0
    #     while i < max_rounds:
    #         prompt = f"""
    #             you have {(max_rounds-i)*2} step left in current task. reflect, perform 
    #             reason for action plan according to available tools only, apply divide and conquer technique, retain from invoking functions
    #         """ 
    #         instruct = {"Notice": prompt}
            
    #         if i == 0:
    #             instruct["Task"] = instruction
    #             await self.chat(
    #                 instruction=instruct, context=context, 
    #                 system=system, out=False, sender=sender, **kwargs
    #             )
        
    #         elif i >0:
    #             await self.chat(
    #                 instruction=instruct, out=False, sender=sender, **kwargs
    #             )
                
    #         prompt = f"""
    #             you have {(max_rounds-i)*2-1} step left in current task, invoke tool usage to perform the action
    #         """
    #         await self.chat(prompt, tool_choice="auto", tool_parsed=True, out=False,sender=sender, **kwargs)

    #         i += 1

    #     if self._is_invoked():
    #         if fallback is not None:
    #             if asyncio.iscoroutinefunction(fallback):
    #                 return await fallback(**fallback_kwargs)
    #             else:
    #                 return fallback(**fallback_kwargs)
    #         prompt = """
    #             present the final result to user
    #         """
    #         return await self.chat(prompt, sender=sender, tool_parsed=True, **kwargs)


# from .sessions import Session

# def get_config(temperature, max_tokens, key_scheme, n):
#     f = lambda i:{
#         "temperature": temperature[i], 
#         "max_tokens": max_tokens[i],
#     }
#     return {
#         "key": f"{key_scheme}{n+1}", 
#         "config": f(n)
#         }

# async def run_workflow(
#     session, prompts, temperature, max_tokens, 
#     key_scheme, num_prompts, context
# ):
#     for i in range(num_prompts): 
#         key_, config_ = get_config(temperature, max_tokens, key_scheme, i)
#         if i == 0:
#             await session.initiate(instruction=prompts[key_], context=context, **config_)
#         else: 
#             await session.followup(instruction=prompts[key_], **config_)
        
#         return session

# async def run_auto_workflow(
#     session, prompts, temperature, max_tokens, 
#     key_scheme, num_prompts, context
# ):
#     for i in range(num_prompts): 
#         key_, config_ = get_config(temperature, max_tokens, key_scheme, i)
#         if i == 0:
#             await session.initiate(instruction=prompts[key_], context=context, **config_)
#         else: 
#             await session.auto_followup(instruction=prompts[key_], **config_)
        
#         return session
    
# async def run_session(
#     prompts, dir, llmconfig, key_scheme, num_prompts, 
#     temperature, max_tokens, type_=None, tools=None
# ):
#     prompts_ = prompts.copy()
#     session = Session(
#         system=prompts_.pop('system', 'You are a helpful assistant'), 
#         dir = dir,
#         llmconfig = llmconfig
#     )
#     if tools:
#         session.register_tools(tools)
#     if type_ is None: 
#         session = await run_workflow(
#             session, prompts_, temperature, max_tokens, 
#             key_scheme=key_scheme, num_prompts=num_prompts
#             )
#     elif type_ == 'auto': 
#         session = await run_auto_workflow(
#             session, prompts_, temperature, max_tokens, 
#             key_scheme=key_scheme, num_prompts=num_prompts
#             )
        
#     return session
