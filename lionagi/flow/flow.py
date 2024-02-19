from typing import Any, Dict, List, Optional, Union
from lionagi.util import to_dict, lcall, to_list, alcall, get_flattened_keys
from lionagi.schema import BaseTool
from lionagi.message import Instruction, System


class ChatFlow:
    """
    Facilitates asynchronous communication and interaction flows within a chat environment,
    leveraging Language Learning Models (LLMs) and custom tools for dynamic conversation
    management. The class provides static methods for handling chat completions, executing
    chat-based instructions, and managing reason-action cycles with optional tool invocation.

    This utility class acts as an intermediary between the chat interface and backend
    services, including LLMs and toolsets, to enhance conversational capabilities and
    automate responses based on the current context, system states, or user inputs.

    Methods:
        call_chatcompletion:
            Asynchronously calls the chat completion provider with the current message
            queue, integrating LLM services for response generation. Supports inclusion
            of sender information and customization of tokenizer parameters.

        chat:
            Conducts a chat session by processing instructions and optionally invoking
            tools based on the chat content. It allows for a flexible integration of
            system messages, context, and sender details to tailor the chat flow.

        ReAct:
            Performs a reason-action cycle, allowing for multiple rounds of reasoning
            and action planning based on the initial instructions and available tools.
            Supports tool invocation to enhance the decision-making process.

        auto_followup:
            Automatically generates follow-up actions based on previous chat interactions
            and tool outputs. It facilitates extended conversation flows by iterating
            through additional reasoning and action steps as needed.

    Usage Examples:
        - Asynchronously calling a chat completion service to generate responses.
        - Managing chat sessions with dynamic instruction processing and tool invocation.
        - Executing complex reason-action cycles to simulate decision-making processes.
        - Automating follow-up actions to maintain engagement and address user queries.

    Note:
        ChatFlow methods are designed to be used asynchronously within an event loop,
        making it suitable for real-time chat applications or services that require
        concurrent processing of chat interactions and background tasks.
    """

    @staticmethod
    async def call_chatcompletion(branch, sender=None, with_sender=False,
                                  tokenizer_kwargs=None, **kwargs):
        """
        Asynchronously calls the chat completion service with the current message queue,
        incorporating LLM services for dynamic response generation. This method updates
        the branch with chat completions and logs the interaction.

        Args:
            branch: The Branch instance invoking the chat completion.
            sender (Optional[str]): Specifies the sender's name to include in completions.
            with_sender (bool): If True, includes sender information in chat messages.
            tokenizer_kwargs (dict): Keyword arguments for the tokenizer in chat completion.
            **kwargs: Additional arguments for the chat completion service.

        Usage:
            - Integrating LLM services to generate chat completions.
            - Logging chat interactions and updating the branch's status tracker.

        Note:
            This method is intended to be used within asynchronous workflows, enhancing
            real-time conversational capabilities with LLM-based response generation.
        """

        messages = branch.chat_messages if not with_sender else branch.chat_messages_with_sender
        payload, completion = await branch.service.serve_chat(
            messages=messages, tokenizer_kwargs=tokenizer_kwargs or {}, **kwargs
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
    async def chat(branch, instruction: Union[Instruction, str],
                   context: Optional[Any] = None,
                   sender: Optional[str] = None,
                   system: Optional[Union[System, str, Dict[str, Any]]] = None,
                   tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
                   out: bool = True,
                   invoke: bool = True, **kwargs) -> Any:
        """
        Conducts an asynchronous chat session, processing instructions and optionally
        invoking tools. This flexible method accommodates system messages, context,
        and sender details to tailor the chat flow according to specific requirements.

        Args:
            branch: The Branch instance for chat operations.
            instruction: The chat instruction, either as a string or Instruction object.
            context: Optional context for enriching the chat conversation.
            sender: Optional identifier for the sender of the chat message.
            system: Optional system message or configuration for the chat.
            tools: Specifies tools to invoke as part of the chat session.
            out (bool): If True, outputs the response of the chat session.
            invoke (bool): If True, allows for tool invocation during the chat.
            **kwargs: Arbitrary keyword arguments for chat completion customization.

        Usage:
            - Processing chat instructions with optional context and sender details.
            - Invoking tools based on the chat content to enhance conversation flows.

        Note:
            This method leverages asynchronous processing to support real-time interactions
            and dynamic response generation in chat applications.
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
                kwargs = branch.action_manager._tool_parser(tools=tools, **kwargs)

        config = {**branch.llmconfig, **kwargs}
        if sender is not None:
            config.update({"sender": sender})

        await ChatFlow.call_chatcompletion(branch, **config)

        async def _output():
            content_ = branch.last_message_content
            if invoke:
                try:
                    tool_uses = content_
                    func_calls = lcall(
                        [to_dict(i) for i in tool_uses["action_list"]],
                        branch.action_manager.get_function_call
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
    async def ReAct(branch, instruction: Union[Instruction, str], context=None,
                    sender=None, system=None, tools=None, num_rounds: int = 1, **kwargs):
        """
        Performs a reason-action cycle with optional tool invocation over multiple rounds,
        simulating decision-making processes based on initial instructions and available tools.

        Args:
            branch: The Branch instance to perform ReAct operations.
            instruction: Initial instruction for the cycle, as a string or Instruction object.
            context: Context relevant to the instruction, enhancing the reasoning process.
            sender: Identifier for the message sender, enriching the conversational context.
            system: Initial system message or configuration for the chat session.
            tools: Tools to be invoked during the reason-action cycle.
            num_rounds (int): Number of reason-action cycles to execute.
            **kwargs: Additional keyword arguments for customization and tool invocation.

        Usage:
            - Executing complex reason-action cycles to facilitate decision-making.
            - Invoking tools to perform actions based on reasoned outcomes.

        Note:
            ReAct cycles aim to enhance conversational decision-making by iteratively
            processing instructions, invoking tools, and generating actions.
        """

        if tools is not None:
            if isinstance(tools, list) and isinstance(tools[0], Tool):
                branch.register_tools(tools)

        if branch.action_manager.registry == {}:
            raise ValueError(
                "No tools found, You need to register tools for ReAct (reason-action)")

        else:
            kwargs = branch.action_manager._tool_parser(tools=True, **kwargs)

        out = ''
        i = 0
        while i < num_rounds:
            prompt = f"""
                you have {(num_rounds - i) * 2} step left in current task. 
                if available, integrate previous tool responses. perform reasoning and 
                prepare action plan according to available tools only, apply divide and 
                conquer technique.
            """
            _instruct = {"Notice": prompt}

            if i == 0:
                _instruct["Task"] = instruction
                out = await ChatFlow.chat(
                    branch=branch,
                    instruction=_instruct, context=context,
                    system=system, sender=sender, **kwargs
                )

            elif i > 0:
                out = await ChatFlow.chat(
                    branch=branch,
                    instruction=_instruct, sender=sender, **kwargs
                )

            prompt = f"""
                you have {(num_rounds - i) * 2 - 1} step left in current task, invoke tool
                usage to perform actions
            """
            out = await ChatFlow.chat(
                branch=branch, instruction=prompt, tool_choice="auto",
                tool_parsed=True,
                sender=sender, **kwargs)

            i += 1
            if not branch._is_invoked():
                return out

        if branch._is_invoked():
            prompt = """
                present the final result to user
            """
            return awaitChatFlow.chat(
                branch=branch, instruction=prompt, sender=sender, tool_parsed=True,
                **kwargs)
        else:
            return out

    @staticmethod
    async def auto_followup(branch, instruction: Union[Instruction, str], context=None,
                            sender=None, system=None,
                            tools: Union[bool, Tool, List[Tool], str, List[str], List[
                                Dict]] = False,
                            max_followup: int = 3, out=True, **kwargs) -> None:
        """
        Automatically generates follow-up actions based on previous chat interactions
        and tool invocations. This method iterates through reasoning and action steps
        to maintain engagement and address user queries effectively.

        Args:
            branch: The Branch instance for follow-up operations.
            instruction: The initial instruction for follow-up, as a string or Instruction.
            context: Context relevant to the instruction, supporting the follow-up process.
            sender: Identifier for the message sender, adding context to the follow-up.
            system: Initial system message or configuration for the session.
            tools: Specifies tools to consider for follow-up actions.
            max_followup (int): Maximum number of follow-up chats allowed.
            out (bool): If True, outputs the result of the follow-up action.
            **kwargs: Additional keyword arguments for follow-up customization.

        Usage:
            - Managing extended conversation flows with automated follow-up actions.
            - Leveraging tool outputs to inform subsequent follow-up steps.

        Note:
            This method supports extended engagement in chat applications by automating
            the generation of follow-up actions based on conversational context and tool
            responses.
        """

        if branch.action_manager.registry != {} and tools:
            kwargs = branch.action_manager._tool_parser(tools=tools, **kwargs)

        n_tries = 0
        while (max_followup - n_tries) > 0:
            prompt = f"""
                In the current task you are allowed a maximum of another {max_followup - n_tries} followup chats. 
                if further actions are needed, invoke tools usage. If you are done, present the final result 
                to user without further tool usage
            """
            if n_tries > 0:
                _out = await ChatFlow.chat(
                    branch=branch, instruction=prompt, sender=sender, tool_choice="auto",
                    tool_parsed=True, **kwargs)
                n_tries += 1

                if not branch._is_invoked():
                    return _out if out else None

            elif n_tries == 0:
                _instruct = {"notice": prompt, "task": instruction}
                _out = await ChatFlow.chat(
                    branch=branch, instruction=_instruct, context=context, system=system,
                    sender=sender,
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
            return await ChatFlow.chat(
                branch=branch, instruction=instruction, sender=sender,
                tool_parsed=True,
                **kwargs)

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

    #     if self.action_manager.registry != {} and tools:
    #         kwargs = self.action_manager._tool_parser(tools=tools, **kwargs)

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

    #     if self.action_manager.registry == {}:
    #         raise ValueError("No tools found, You need to register tools for ReAct (reason-action)")

    #     else:
    #         kwargs = self.action_manager._tool_parser(tools=True, **kwargs)

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
#     temperature, max_tokens, type_=None, tools=None
# ):
#     prompts_ = prompts.copy()
#     session = Session(
#         system=prompts_.pop('system', 'You are a helpful assistant'), 
#         directory = directory,
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
