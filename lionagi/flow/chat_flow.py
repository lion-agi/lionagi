from typing import Any, Dict, List, Optional, Union, TypeVar
from lionagi.util import to_dict, lcall, to_list, alcall, get_flattened_keys
from lionagi.schema import BaseActionNode
from lionagi.message import Instruction, System

T = TypeVar('T', bound=BaseActionNode)



class ChatFlow:
    """
    Facilitates asynchronous communication and interaction flows within a chat environment,
    leveraging Language Learning Models (LLMs) and custom actions for dynamic conversation
    management. The class provides static methods for handling chat completions, executing
    chat-based instructions, and managing reason-action cycles with optional BaseActionNode invocation.

    Methods:
        call_chatcompletion:
            Asynchronously calls the chat completion provider with the current message
            queue, integrating LLM services for response generation. Supports inclusion
            of sender information and customization of tokenizer parameters.

        chat:
            Conducts a chat session by processing instructions and optionally invoking
            actions based on the chat content. It allows for a flexible integration of
            system messages, context, and sender details to tailor the chat flow.

        ReAct:
            Performs a reason-action cycle, allowing for multiple rounds of reasoning
            and action planning based on the initial instructions and available actions.
            Supports BaseActionNode invocation to enhance the decision-making process.

        auto_followup:
            Automatically generates follow-up actions based on previous chat interactions
            and BaseActionNode outputs. It facilitates extended conversation flows by iterating
            through additional reasoning and action steps as needed.

    Usage Examples:
        - Asynchronously calling a chat completion service to generate responses.
        - Managing chat sessions with dynamic instruction processing and BaseActionNode invocation.
        - Executing complex reason-action cycles to simulate decision-making processes.
        - Automating follow-up actions to maintain engagement and address user queries.

    Note:
        ChatFlow methods are designed to be used asynchronously within an event loop,
        making it suitable for real-time chat applications or services that require
        concurrent processing of chat interactions and background tasks.
    """

    @staticmethod
    async def call_chatcompletion(branch, sender=None, with_sender=False, **kwargs):
        """
        Asynchronously calls the chat completion service with the current message queue.

        Args:
            branch: The Branch instance calling the service.
            sender (Optional[str]): The name of the sender to include in chat completions.
            with_sender (bool): If True, includes sender information in messages.
            **kwargs: Arbitrary keyword arguments for the chat completion service.

        Examples:
            >>> await ChatFlow.call_chatcompletion(branch, sender="user")
        """
        messages = branch.chat_messages if not with_sender else branch.chat_messages_with_sender
        payload, completion = await branch.service.serve_chat(
            messages=messages, **kwargs
        )
        if "choices" in completion:
            add_msg_config = {"response": completion['choices'][0]}
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
            actions: Union[bool, T, List[T], str, List[str]] = False,
            out: bool = True,
            invoke: bool = True,
            **kwargs) -> Any:

        """
        a chat conversation with LLM, processing instructions and system messages, optionally invoking actions.

        Args:
            branch: The Branch instance to perform chat operations.
            instruction (Union[Instruction, str]): The instruction for the chat.
            context (Optional[Any]): Additional context for the chat.
            sender (Optional[str]): The sender of the chat message.
            system (Optional[Union[System, str, Dict[str, Any]]]): System message to be processed.
            actions (Union[bool, Tool, List[Tool], str, List[str]]): Specifies actions to be invoked.
            out (bool): If True, outputs the chat response.
            invoke (bool): If True, invokes actions as part of the chat.
            **kwargs: Arbitrary keyword arguments for chat completion.

        Examples:
            >>> await ChatFlow.chat(branch, "Ask about user preferences")
        """
        if system:
            branch.change_first_system_message(system)
        branch.add_message(instruction=instruction, context=context, sender=sender)

        if 'tool_parsed' in kwargs:
            kwargs.pop('tool_parsed')
            action_kwarg = {'tools': actions}
            kwargs = {**action_kwarg, **kwargs}
        else:
            if actions and branch.has_actions:
                kwargs = branch.action_manager._action_parser(actions=actions, **kwargs)

        config = {**branch.llmconfig, **kwargs}
        if sender is not None:
            config.update({"sender": sender})

        await branch.call_chatcompletion(**config)

        async def _output():
            content_ = to_dict(branch.messages.content.iloc[-1])
            if invoke:
                try:
                    acts_ = content_
                    func_calls = lcall(
                        [to_dict(i) for i in acts_["action_list"]],
                        branch.action_manager.get_action_call
                    )

                    outs = await alcall(func_calls, branch.action_manager.invoke)
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
            context=None,
            sender=None,
            system=None,
            actions=None,
            num_rounds: int = 1,
            **kwargs
    ):
        """
        Performs a reason-action cycle with optional actions invocation over multiple rounds.

        Args:
            branch: The Branch instance to perform ReAct operations.
            instruction (Union[Instruction, str]): Initial instruction for the cycle.
            context: Context relevant to the instruction.
            sender (Optional[str]): Identifier for the message sender.
            system: Initial system message or configuration.
            actions: Tools to be registered or used during the cycle.
            num_rounds (int): Number of reason-action cycles to perform.
            **kwargs: Additional keyword arguments for customization.

        Examples:
            >>> await ChatFlow.ReAct(branch, "Analyze user feedback", num_rounds=2)
        """
        if actions is not None:
            if isinstance(actions, list) and isinstance(actions[0], BaseActionNode):
                branch.register(actions)

        if branch.action_manager.registry == {}:
            raise ValueError(
                "No actions found, You need to register actions for ReAct (reason-action)")

        else:
            kwargs = branch.action_manager._action_parser(actions=True, **kwargs)

        out = ''
        i = 0
        while i < num_rounds:
            prompt = f"""you have {(num_rounds - i) * 2} step left in current task. if available, integrate previous actions responses. perform reasoning and prepare action plan according to available actions only, apply divide and conquer technique.
            """
            instruct = {"Notice": prompt}

            if i == 0:
                instruct["Task"] = instruction
                out = await branch.chat(
                    instruction=instruct, context=context,
                    system=system, sender=sender, **kwargs
                )

            elif i > 0:
                out = await branch.chat(
                    instruction=instruct, sender=sender, **kwargs
                )

            prompt = f"""
                you have {(num_rounds - i) * 2 - 1} step left in current task, invoke actions usage to perform actions
            """
            out = await branch.chat(prompt, tool_choice="auto", tool_parsed=True,
                                    sender=sender, **kwargs)

            i += 1
            if not branch._is_invoked():
                return out

        if branch._is_invoked():
            prompt = """
                present the final result to user
            """
            return await branch.chat(prompt, sender=sender, tool_parsed=True,
                                     **kwargs)
        else:
            return out

    @staticmethod
    async def auto_followup(
            branch,
            instruction: Union[Instruction, str],
            context=None,
            sender=None,
            system=None,
            actions: Union[bool, T, List[T], str, List[str], List[Dict]] = False,
            max_followup: int = 3,
            out=True,
            **kwargs
    ) -> None:
        """
        Automatically performs follow-up actions based on chat interactions and actions invocations.

        Args:
            branch: The Branch instance to perform follow-up operations.
            instruction (Union[Instruction, str]): The initial instruction for follow-up.
            context: Context relevant to the instruction.
            sender (Optional[str]): Identifier for the message sender.
            system: Initial system message or configuration.
            actions: Specifies actions to be considered for follow-up actions.
            max_followup (int): Maximum number of follow-up chats allowed.
            out (bool): If True, outputs the result of the follow-up action.
            **kwargs: Additional keyword arguments for follow-up customization.

        Examples:
            >>> await ChatFlow.auto_followup(branch, "Finalize report", max_followup=2)
        """
        if branch.action_manager.registry != {} and actions:
            kwargs = branch.action_manager._tool_action(actions=actions, **kwargs)

        n_tries = 0
        while (max_followup - n_tries) > 0:
            prompt = f"""
                In the current task you are allowed a maximum of another {max_followup - n_tries} followup chats. 
                if further actions are needed, invoke actions usage. If you are done, present the final result 
                to user without further actions usage
            """
            if n_tries > 0:
                _out = await branch.chat(prompt, sender=sender, tool_choice="auto",
                                         tool_parsed=True, **kwargs)
                n_tries += 1

                if not branch._is_invoked():
                    return _out if out else None

            elif n_tries == 0:
                instruct = {"notice": prompt, "task": instruction}
                _out = await branch.chat(
                    instruct, context=context, system=system, sender=sender,
                    tool_choice="auto",
                    tool_parsed=True, **kwargs
                )
                n_tries += 1

                if not branch._is_invoked():
                    return _out if out else None

        if branch._is_invoked():
            """
            In the current task, you are at your last step, present the final result to user
            """
            return await branch.chat(instruction, sender=sender, tool_parsed=True,
                                     **kwargs)

 #     actions = None,
    #     max_rounds: int = 1,

    #     fallback: Optional[Callable] = None,
    #     fallback_kwargs: Optional[Dict] = None,
    #     **kwargs
    # ):
    #     if actions is not None:
    #         if isinstance(actions, list) and isinstance(actions[0], Tool):
    #             self.register_tools(actions)

    #     if self.action_manager.registry == {}:
    #         raise ValueError("No actions found, You need to register actions for ReAct (reason-action)")

    #     else:
    #         kwargs = self.action_manager._tool_parser(actions=True, **kwargs)

    #     i = 0
    #     while i < max_rounds:
    #         prompt = f"""
    #             you have {(max_rounds-i)*2} step left in current task. reflect, perform
    #             reason for action plan according to available actions only, apply divide and conquer technique, retain from invoking functions
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
    #             you have {(max_rounds-i)*2-1} step left in current task, invoke actions usage to perform the action
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
    #     temperature, max_tokens, type_=None, actions=None
    # ):
    #     prompts_ = prompts.copy()
    #     session = Session(
    #         system=prompts_.pop('system', 'You are a helpful assistant'),
    #         dir = dir,
    #         llmconfig = llmconfig
    #     )
    #     if actions:
    #         session.register_tools(actions)
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

    # async def followup(
    #     self,
    #     instruction: Union[Instruction, str],
    #     context = None,
    #     sender = None,
    #     system = None,
    #     actions: Union[bool, BaseActionNode, List[BaseActionNode], str, List[str], List[Dict]] = False,
    #     max_followup: int = 3,
    #     out=True, 
    #     **kwargs
    # ) -> None:

    #     """
    #     auto BaseActionNode usages until LLM decides done. Then presents final results.
    #     """

    #     if self.action_manager.registry != {} and actions:
    #         kwargs = self.action_manager._BaseActionNode_parser(actions=actions, **kwargs)

    #     n_tries = 0
    #     while (max_followup - n_tries) > 0:
    #         prompt = f"""
    #             In the current task you are allowed a maximum of another {max_followup-n_tries} followup chats. 
    #             if further actions are needed, invoke actions usage. If you are done, present the final result
    #             to user without further BaseActionNode usage.
    #         """
    #         if n_tries > 0:
    #             _out = await self.chat(prompt, sender=sender, BaseActionNode_choice="auto", BaseActionNode_parsed=True, **kwargs)
    #             n_tries += 1

    #             if not self._is_invoked():
    #                 return _out if out else None

    #         elif n_tries == 0:
    #             instruct = {"notice": prompt, "task": instruction}
    #             out = await self.chat(
    #                 instruct, context=context, system=system, sender=sender, BaseActionNode_choice="auto",
    #                 BaseActionNode_parsed=True, **kwargs
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
    #     actions = None,
    #     max_rounds: int = 1,

    #     fallback: Optional[Callable] = None,
    #     fallback_kwargs: Optional[Dict] = None,
    #     **kwargs 
    # ):
    #     if actions is not None:
    #         if isinstance(actions, list) and isinstance(actions[0], BaseActionNode):
    #             self.register_BaseActionNodes(actions)

    #     if self.action_manager.registry == {}:
    #         raise ValueError("No actions found, You need to register actions for ReAct (reason-action)")

    #     else:
    #         kwargs = self.action_manager._BaseActionNode_parser(actions=True, **kwargs)

    #     i = 0
    #     while i < max_rounds:
    #         prompt = f"""
    #             you have {(max_rounds-i)*2} step left in current task. reflect, perform 
    #             reason for action plan according to available actions only, apply divide and conquer technique, retain from invoking functions
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
    #             you have {(max_rounds-i)*2-1} step left in current task, invoke BaseActionNode usage to perform the action
    #         """
    #         await self.chat(prompt, BaseActionNode_choice="auto", BaseActionNode_parsed=True, out=False,sender=sender, **kwargs)

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
    #         return await self.chat(prompt, sender=sender, BaseActionNode_parsed=True, **kwargs)

# from .sessions import Session

# def get_config(temperature, max_tokens, key_scheme, num):
#     f = lambda i:{
#         "temperature": temperature[i], 
#         "max_tokens": max_tokens[i],
#     }
#     return {
#         "key": f"{key_scheme}{num+1}",
#         "config": f(num)
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
#     prompts, directory, llmconfig, key_scheme, num_prompts,
#     temperature, max_tokens, type_=None, actions=None
# ):
#     prompts_ = prompts.copy()
#     session = Session(
#         system=prompts_.pop('system', 'You are a helpful assistant'), 
#         directory = directory,
#         llmconfig = llmconfig
#     )
#     if actions:
#         session.register_BaseActionNodes(actions)
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
