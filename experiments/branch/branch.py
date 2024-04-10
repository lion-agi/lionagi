import json
import pandas as pd

from typing import Any, Dict, List, Optional, Union
from collections import deque
from dotenv import load_dotenv

from lionagi.libs import to_dict, get_flattened_keys, alcall, lcall, to_list
from lionagi.libs.sys_util import is_same_dtype
from lionagi.core.message.schema import Tool
from working.base_service import StatusTracker, BaseService
from lionagi.services.oai import OpenAIService
from lionagi.services.openrouter import OpenRouterService

from lionagi.integrations.provider import oai_schema
from lionagi.integrations.provider import openrouter_schema
from working.to_do import ActionManager

from lionagi.core.session import Instruction, System
from lionagi.core.session import InstructionSet

from lionagi.core.session import Conversation, validate_messages
from lionagi.core.session import Request

load_dotenv()


class Branch(Conversation):
    """
    Manages a conversation branch within the application, handling messages, instruction sets, 
    tools registrations, and provider interactions for a single conversation flow. Extends the
    Conversation class to provide specialized functionalities like message handling, tools
    management, and integration with external services.

    Attributes:
        messages (pd.DataFrame): Dataframe storing conversation messages.
        instruction_sets (Dict[str, InstructionSet]): Dictionary mapping instruction set names to their instances.
        action_manager (ToolManager): Manages tools available within the conversation.
        status_tracker (StatusTracker): Tracks the status of various tasks within the conversation.
        name (Optional[str]): Identifier for the branch.
        pending_ins (Dict): Dictionary storing incoming requests.
        pending_outs (deque): Queue for outgoing requests.
        service (BaseService): Service instance for interaction with external services.
        llmconfig (Dict): Configuration for language model interactions.

    Methods:
        __init__(self, name=None, messages=None, instruction_sets=None, action_manager=None,
                 provider=None, llmconfig=None):
            Initializes a new Branch instance with optional configurations.

        clone(self) -> 'Branch':
            Creates a deep copy of the current Branch instance.

        merge_branch(self, branch: 'Branch', update: True):
            Merges another branch into the current Branch instance.

        send(self, recipient: str, category: str, package: Any):
            Sends a package package to a specified recipient.

        receive(self, sender: str, messages=True, tools=True, provider=True, llmconfig=True):
            Processes and integrates received package packages based on their titles.

        receive_all(self):
            Processes all pending incoming requests from all senders.

        call_chatcompletion(self, sender=None, with_sender=False, **kwargs):
            Asynchronously calls the chat.py completion provider with the current message queue.

        chat.py(self, instruction: Union[BaseInstruction, str], context=None, sender=None, system=None,
             tools=False, out=True, invoke=True, **kwargs) -> Any:
            Asynchronously handles a chat.py interaction within the branch.

        ReAct(self, instruction: Union[BaseInstruction, str], context=None, sender=None, system=None,
              tools=None, num_rounds=1, **kwargs):
            Performs a sequence of reasoning and action based on the given instruction over multiple rounds.

        auto_followup(self, instruction: Union[BaseInstruction, str], context=None, sender=None,
                      system=None, tools=False, max_followup=3, out=True, **kwargs) -> None:
            Automatically performs follow-up tools until a specified condition is met or the maximum number of follow-ups is reached.
    
    Note:
        This class is designed to be used within an asynchronous environment, where methods like
        `chat.py`, `ReAct`, and `auto_followup` are particularly useful for handling complex conversation flows.
    """

    def __init__(
            self,
            name: Optional[str] = None,
            messages: Optional[pd.DataFrame] = None,
            instruction_sets: Optional[Dict[str, InstructionSet]] = None,
            action_manager: Optional[ActionManager] = None,
            service: Optional[BaseService] = None,
            llmconfig: Optional[Dict] = None,
    ):
        """
        Initializes a new Branch instance.

        Args:
            name (Optional[str]): Name of the branch, providing an identifier within the conversational system. Defaults to None.
            messages (Optional[pd.DataFrame]): A pandas DataFrame containing the conversation's messages. Initializes with an empty DataFrame if None. Defaults to None.
            instruction_sets (Optional[Dict[str, InstructionSet]]): Dictionary mapping instruction set names to InstructionSet objects for conversation flow management. Defaults to {}.
            action_manager (Optional[ToolManager]): Manages tools within the branch. Creates a new instance if None. Defaults to None.
            service (Optional[BaseService]): Interacts with external services. Initializes a default provider based on branch configuration if None. Defaults to None.
            llmconfig (Optional[Dict]): Configuration for language model interactions. Sets up default configuration based on the provider type if None. Defaults to None.
        """
        super().__init__()
        self.messages = (
            messages
            if messages is not None
            else pd.DataFrame(
                columns=["node_id", "role", "sender", "timestamp", "content"]
            )
        )
        self.instruction_sets = instruction_sets if instruction_sets else {}
        self.action_manager = action_manager if action_manager else ActionManager()
        self.status_tracker = StatusTracker()
        self._add_service(service, llmconfig)
        self.name = name
        self.pending_ins = {}
        self.pending_outs = deque()

    @property
    def chat_messages(self):
        return self._to_chatcompletion_message()

    @property
    def chat_messages_with_sender(self):
        return self._to_chatcompletion_message(with_sender=True)

    @property
    def messages_describe(self) -> Dict[str, Any]:
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self._info(),
            "summary_by_sender": self._info(use_sender=True),
            "instruction_sets": self.instruction_sets,
            "registered_tools": self.action_manager.registry,
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    @property
    def has_tools(self) -> bool:
        return self.action_manager.registry != {}

    # ----- tools manager methods ----- #

    def register_tools(self, tools: Union[Tool, List[Tool]]):
        """
        Registers a tools or a list of tools with the branch's tools manager.

        This makes the tools available for use within the conversation.

        Args:
            tools (Union[Tool, List[Tool]]): A single Tool instance or a list of Tool instances to be registered.

        Examples:
            >>> branch.register_actions(tools)
            >>> branch.register_actions([tool1, tool2])
        """
        if not isinstance(tools, list):
            tools = [tools]
        self.action_manager.register_tools(tools=tools)

    def delete_tool(self, tools: Union[Tool, List[Tool], str, List[str]],
                    verbose=True) -> bool:
        """
        Deletes one or more tools from the branch's tools manager registry.

        This can be done using either tools instances or their names.

        Args:
            tools (Union[Tool, List[Tool], str, List[str]]): A single Tool instance, a list of Tool instances, a tools name, or a list of tools names to be deleted.
            verbose (bool): If True, prints a success message upon successful deletion. Defaults to True.

        Returns:
            bool: True if the tools(s) were successfully deleted, False otherwise.

        Examples:
            >>> branch.delete_actions("tool_name")
            >>> branch.delete_actions(["tool_name1", "tool_name2"])
            >>> branch.delete_actions(tool_instance)
            >>> branch.delete_actions([tool_instance1, tool_instance2])
        """
        if isinstance(tools, list):
            if is_same_dtype(tools, str):
                for tool in tools:
                    if tool in self.action_manager.registry:
                        self.action_manager.registry.pop(tool)
                if verbose:
                    print("tools successfully deleted")
                return True
            elif is_same_dtype(tools, Tool):
                for tool in tools:
                    if tool.name in self.action_manager.registry:
                        self.action_manager.registry.pop(tool.name)
                if verbose:
                    print("tools successfully deleted")
                return True
        if verbose:
            print("tools deletion failed")
        return False

    # ----- branch manipulation ----- #
    def clone(self) -> 'Branch':
        """
        Creates a deep copy of the current Branch instance.

        This method duplicates the Branch's state, including its messages, instruction sets, and tools registrations, but creates a new ToolManager instance for the cloned branch.

        Returns:
            Branch: A new Branch instance that is a deep copy of the current instance.

        Examples:
            >>> cloned_branch = branch.clone()
        """
        cloned = Branch(
            messages=self.messages.copy(),
            instruction_sets=self.instruction_sets.copy(),
            action_manager=ActionManager()
        )
        tools = [
            tool for tool in self.action_manager.registry.values()]

        cloned.register_tools(tools)

        return cloned

    def merge_branch(self, branch: 'Branch', update: bool = True):
        """
        Merges another branch into the current Branch instance.

        Incorporates messages, instruction sets, and tools registrations from the specified branch. Optionally updates existing instruction sets and tools if duplicates are found.

        Args:
            branch (Branch): The branch to merge into the current branch.
            update (bool): If True, existing instruction sets and tools are updated with those from the merged branch. Defaults to True.

        Examples:
            >>> branch.merge_branch(another_branch)
        """

        message_copy = branch.messages.copy()
        self.messages = self.messages.merge(message_copy, how='outer')

        if update:
            self.instruction_sets.update(branch.instruction_sets)
            self.action_manager.registry.update(
                branch.action_manager.registry
            )
        else:
            for key, value in branch.instruction_sets.items():
                if key not in self.instruction_sets:
                    self.instruction_sets[key] = value

            for key, value in branch.action_manager.registry.items():
                if key not in self.action_manager.registry:
                    self.action_manager.registry[key] = value

    # ----- intra-branch communication methods ----- #
    def send(self, to_name, title, package):
        """
        Sends a package package to a specified recipient.

        Packages are queued in `pending_outs` for dispatch. The function doesn't immediately send the package but prepares it for delivery.

        Args:
            to_name (str): The name of the recipient branch.
            title (str): The category or category of the package (e.g., 'messages', 'tools', 'provider', 'llmconfig').
            package (Any): The actual data or object to be sent, its expected type depends on the category.

        Examples:
            >>> branch.send("another_branch", "messages", message_dataframe)
            >>> branch.send("service_branch", "provider", service_config)
        """
        request = Request(from_name=self.name, to_name=to_name, title=title,
                          request=package)
        self.pending_outs.append(request)

    def receive(self, from_name, messages=True, tool=True, service=True, llmconfig=True):
        """
        Processes and integrates received package packages based on their titles.

        Handles incoming requests by updating the branch's state with the received data. It can selectively process requests based on the type specified by the `category` of the package.

        Args:
            from_name (str): The name of the sender whose packages are to be processed.
            messages (bool): If True, processes 'messages' requests. Defaults to True.
            tool (bool): If True, processes 'tools' requests. Defaults to True.
            service (bool): If True, processes 'provider' requests. Defaults to True.
            llmconfig (bool): If True, processes 'llmconfig' requests. Defaults to True.

        Raises:
            ValueError: If no package is found from the specified sender, or if any of the packages have an invalid format.

        Examples:
            >>> branch.receive("another_branch")
        """
        skipped_requests = deque()
        if from_name not in self.pending_ins:
            raise ValueError(f'No package from {from_name}')
        while self.pending_ins[from_name]:
            request = self.pending_ins[from_name].popleft()

            if request.category == 'messages' and messages:
                if not isinstance(request.package, pd.DataFrame):
                    raise ValueError('Invalid messages format')
                validate_messages(request.package)
                self.messages = self.messages.merge(request.package, how='outer')
                continue

            elif request.category == 'tools' and tool:
                if not isinstance(request.package, Tool):
                    raise ValueError('Invalid tools format')
                self.action_manager.register_tools([request.package])

            elif request.category == 'provider' and service:
                if not isinstance(request.package, BaseService):
                    raise ValueError('Invalid provider format')
                self.service = request.package

            elif request.category == 'llmconfig' and llmconfig:
                if not isinstance(request.package, dict):
                    raise ValueError('Invalid llmconfig format')
                self.llmconfig.update(request.package)

            else:
                skipped_requests.append(request)

        self.pending_ins[from_name] = skipped_requests

    def receive_all(self):
        """
        Processes all pending incoming requests from all senders.

        This method iterates through all senders with pending requests and processes each using the `receive` method. It ensures that all queued incoming data is integrated into the branch's state.

        Examples:
            >>> branch.receive_all()
        """
        for key in list(self.pending_ins.keys()):
            self.receive(key)

    # ----- provider methods ----- #

    async def call_chatcompletion(self, sender=None, with_sender=False, **kwargs):
        """
        Asynchronously calls the chat.py completion provider with the current message queue.

        This method prepares the messages for chat.py completion, sends the package to the configured provider, and handles the assistant_response. The method supports additional keyword arguments that are passed directly to the provider.

        Args:
            sender (Optional[str]): The name of the sender to be included in the chat.py completion package. Defaults to None.
            with_sender (bool): If True, includes the sender's name in the messages. Defaults to False.
            **kwargs: Arbitrary keyword arguments passed directly to the chat.py completion provider.

        Examples:
            >>> await branch._call_chatcompletion()
        """
        messages = self.chat_messages if not with_sender else self.chat_messages_with_sender
        payload, completion = await self.service.serve_chat(
            messages=messages, **kwargs)
        if "choices" in completion:
            add_msg_config = {"assistant_response": completion['choices'][0]}
            if sender is not None:
                add_msg_config["sender"] = sender

            self.add_message(**add_msg_config)
            self.status_tracker.num_tasks_succeeded += 1
        else:
            self.status_tracker.num_tasks_failed += 1

    # ----- chat.py methods ----- #

    async def chat(
            self,
            instruction: Union[Instruction, str],
            context: Optional[Any] = None,
            sender: Optional[str] = None,
            system: Optional[Union[System, str, Dict[str, Any]]] = None,
            tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
            out: bool = True,
            invoke: bool = True,
            **kwargs
    ) -> Any:
        """
        Asynchronously handles a chat.py interaction within the branch.

        This method adds a new message based on the provided instruction, optionally using specified tools, and processes the chat.py completion.

        Args:
            instruction (Union[BaseInstruction, str]): The instruction or query to process.
            context (Optional[Any]): Additional context for the chat.py completion package. Defaults to None.
            sender (Optional[str]): The name of the sender. Defaults to None.
            system (Optional[Union[System, str, Dict[str, Any]]]): System message or configuration. Defaults to None.
            tools (Union[bool, Tool, List[Tool], str, List[str]]): Specifies if and which tools to use in the chat.py. Defaults to False.
            out (bool): If True, the output of the chat.py completion is returned. Defaults to True.
            invoke (bool): If True, invokes any action as determined by the chat.py completion. Defaults to True.
            **kwargs: Arbitrary keyword arguments for further customization.

        Returns:
            Any: The result of the chat.py interaction, which could be varied based on the input_ and configuration.

        Examples:
            >>> result = await branch.chat.py("How's the weather?")
        """

        if system:
            self.change_first_system_message(system)
        self.add_message(instruction=instruction, context=context, sender=sender)

        if 'tool_parsed' in kwargs:
            kwargs.pop('tool_parsed')
            tool_kwarg = {'tools': tools}
            kwargs = {**tool_kwarg, **kwargs}
        else:
            if tools and self.has_tools:
                kwargs = self.action_manager._tool_parser(tools=tools, **kwargs)

        config = {**self.llmconfig, **kwargs}
        if sender is not None:
            config.update({"sender": sender})

        await self.call_chatcompletion(**config)

        async def _output():
            content_ = to_dict(self.messages.content.iloc[-1])
            if invoke:
                try:
                    tool_uses = content_
                    func_calls = lcall(
                        [to_dict(i) for i in tool_uses["action_list"]],
                        self.action_manager.get_function_call
                    )

                    outs = await alcall(func_calls, self.action_manager.invoke)
                    outs = to_list(outs, flatten=True)

                    for out_, f in zip(outs, func_calls):
                        self.add_message(
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

    async def ReAct(
            self,
            instruction: Union[Instruction, str],
            context=None,
            sender=None,
            system=None,
            tools=None,
            num_rounds: int = 1,
            **kwargs
    ):
        """
        Performs a sequence of reasoning and action based on the given instruction over multiple rounds.

        In each round, the method reflects on the task, devises an action plan using available tools, and invokes the necessary tools usage to execute the plan.

        Args:
            instruction (Union[BaseInstruction, str]): The initial task or question to start the reasoning and action process.
            context: Optional context to influence the reasoning process. Defaults to None.
            sender (Optional[str]): The name of the sender initiating the ReAct process. Defaults to None.
            system: Optional system message or configuration to be considered during the process. Defaults to None.
            tools: Specifies the tools to be considered for action plans. Defaults to None.
            num_rounds (int): The number of reasoning-action rounds to be performed. Defaults to 1.
            **kwargs: Arbitrary keyword arguments for further customization.

        Returns:
            The final output after completing the specified number of reasoning-action rounds.

        Examples:
            >>> await branch.ReAct("Prepare a report on recent sales trends.", num_rounds=2)
        """
        if tools is not None:
            if isinstance(tools, list) and isinstance(tools[0], Tool):
                self.register_tools(tools)

        if self.action_manager.registry == {}:
            raise ValueError(
                "No tools found, You need to register tools for ReAct (reason-action)")

        else:
            kwargs = self.action_manager._tool_parser(tools=True, **kwargs)

        out = ''
        i = 0
        while i < num_rounds:
            prompt = f"""you have {(num_rounds - i) * 2} step left in current task. if available, integrate previous tools responses. perform reasoning and prepare action plan according to available tools only, apply divide and conquer technique.
            """
            instruct = {"Notice": prompt}

            if i == 0:
                instruct["Task"] = instruction
                out = await self.chat(
                    instruction=instruct, context=context,
                    system=system, sender=sender, **kwargs
                )

            elif i > 0:
                out = await self.chat(
                    instruction=instruct, sender=sender, **kwargs
                )

            prompt = f"""
                you have {(num_rounds - i) * 2 - 1} step left in current task, invoke tools usage to perform tools
            """
            out = await self.chat(prompt, tool_choice="auto", tool_parsed=True,
                                  sender=sender, **kwargs)

            i += 1
            if not self._is_invoked():
                return out

        if self._is_invoked():
            prompt = """
                present the final result to user
            """
            return await self.chat(prompt, sender=sender, tool_parsed=True, **kwargs)
        else:
            return out

    # async def auto_ReAct(
    #     self,
    #     instruction: Union[BaseInstruction, str],
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
    #         format_prompt = f"""
    #             you have {(max_rounds-i)*2} step left in current task. reflect, perform 
    #             reason for action plan according to available tools only, apply divide and conquer technique, retain from invoking functions
    #         """ 
    #         instruct = {"Notice": format_prompt}

    #         if i == 0:
    #             instruct["Task"] = instruction
    #             await self.chat.py(
    #                 instruction=instruct, context=context, 
    #                 system=system, out=False, sender=sender, **kwargs
    #             )

    #         elif i >0:
    #             await self.chat.py(
    #                 instruction=instruct, out=False, sender=sender, **kwargs
    #             )

    #         format_prompt = f"""
    #             you have {(max_rounds-i)*2-1} step left in current task, invoke tools usage to perform the action
    #         """
    #         await self.chat.py(format_prompt, tool_choice="auto", tool_parsed=True, out=False,sender=sender, **kwargs)

    #         i += 1

    #     if self._is_invoked():
    #         if fallback is not None:
    #             if asyncio.iscoroutinefunction(fallback):
    #                 return await fallback(**fallback_kwargs)
    #             else:
    #                 return fallback(**fallback_kwargs)
    #         format_prompt = """
    #             present the final result to user
    #         """
    #         return await self.chat.py(format_prompt, sender=sender, tool_parsed=True, **kwargs)

    async def auto_followup(
            self,
            instruction: Union[Instruction, str],
            context=None,
            sender=None,
            system=None,
            tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
            max_followup: int = 3,
            out=True,
            **kwargs
    ) -> None:

        """
        Automatically performs follow-up tools until a specified condition is met or the maximum number of follow-ups is reached.

        This method allows for iterative refinement and follow-up based on the instruction, using available tools and considering feedback from each step.

        Args:
            instruction (Union[BaseInstruction, str]): The instruction to initiate the follow-up process.
            context: Optional context relevant to the follow-up tools. Defaults to None.
            sender (Optional[str]): The name of the sender. Defaults to None.
            system: Optional system configuration affecting the follow-up process. Defaults to None.
            tools (Union[bool, Tool, List[Tool], str, List[str], List[Dict]]): Specifies the tools to be used during follow-up tools. Defaults to False.
            max_followup (int): The maximum number of follow-up iterations. Defaults to 3.
            out (bool): If True, the final result is returned. Defaults to True.
            **kwargs: Arbitrary keyword arguments for additional customization.

        Returns:
            The final result after all follow-up tools are completed, if `out` is True.

        Examples:
            >>> await branch.auto_followup("Update the database with new entries.", max_followup=2)
        """

        if self.action_manager.registry != {} and tools:
            kwargs = self.action_manager._tool_parser(tools=tools, **kwargs)

        n_tries = 0
        while (max_followup - n_tries) > 0:
            prompt = f"""
                In the current task you are allowed a maximum of another {max_followup - n_tries} followup chats. 
                if further tools are needed, invoke tools usage. If you are done, present the final result 
                to user without further tools usage
            """
            if n_tries > 0:
                _out = await self.chat(prompt, sender=sender, tool_choice="auto",
                                       tool_parsed=True, **kwargs)
                n_tries += 1

                if not self._is_invoked():
                    return _out if out else None

            elif n_tries == 0:
                instruct = {"notice": prompt, "task": instruction}
                out = await self.chat(
                    instruct, context=context, system=system, sender=sender,
                    tool_choice="auto",
                    tool_parsed=True, **kwargs
                )
                n_tries += 1

                if not self._is_invoked():
                    return _out if out else None

        if self._is_invoked():
            """
            In the current task, you are at your last step, present the final result to user
            """
            return await self.chat(instruction, sender=sender, tool_parsed=True, **kwargs)

    # async def followup(
    #     self,
    #     instruction: Union[BaseInstruction, str],
    #     context = None,
    #     sender = None,
    #     system = None,
    #     tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
    #     max_followup: int = 3,
    #     out=True, 
    #     **kwargs
    # ) -> None:

    #     """
    #     auto tools usages until LLM decides done. Then presents final results.
    #     """

    #     if self.action_manager.registry != {} and tools:
    #         kwargs = self.action_manager._tool_parser(tools=tools, **kwargs)

    #     n_tries = 0
    #     while (max_followup - n_tries) > 0:
    #         format_prompt = f"""
    #             In the current task you are allowed a maximum of another {max_followup-n_tries} followup chats. 
    #             if further tools are needed, invoke tools usage. If you are done, present the final result
    #             to user without further tools usage.
    #         """
    #         if n_tries > 0:
    #             _out = await self.chat.py(format_prompt, sender=sender, tool_choice="auto", tool_parsed=True, **kwargs)
    #             n_tries += 1

    #             if not self._is_invoked():
    #                 return _out if out else None

    #         elif n_tries == 0:
    #             instruct = {"notice": format_prompt, "task": instruction}
    #             out = await self.chat.py(
    #                 instruct, context=context, system=system, sender=sender, tool_choice="auto", 
    #                 tool_parsed=True, **kwargs
    #             )
    #             n_tries += 1

    #             if not self._is_invoked():
    #                 return _out if out else None

    def _add_service(self, service, llmconfig):
        service = service or OpenAIService()
        self.service = service
        if llmconfig:
            self.llmconfig = llmconfig
        else:
            if isinstance(service, OpenAIService):
                self.llmconfig = oai_schema["chat.py/completions"]["config"]
            elif isinstance(service, OpenRouterService):
                self.llmconfig = openrouter_schema["chat.py/completions"]["config"]
            else:
                self.llmconfig = {}

    def _to_chatcompletion_message(self, with_sender=False) -> List[Dict[str, Any]]:
        message = []

        for _, row in self.messages.iterrows():
            content_ = row['content']
            if content_.startswith('Sender'):
                content_ = content_.split(':', 1)[1]

            if isinstance(content_, str):
                try:
                    content_ = json.dumps(to_dict(content_))
                except Exception as e:
                    raise ValueError(
                        f"Error in serealizing, {row['node_id']} {content_}: {e}")

            out = {"role": row['role'], "content": content_}
            if with_sender:
                out['content'] = f"Sender {row['sender']}: {content_}"

            message.append(out)
        return message

    def _is_invoked(self) -> bool:
        """
        Check if the conversation has been invoked with an action assistant_response.

        Returns:
            bool: True if the conversation has been invoked, False otherwise.

        """
        content = self.messages.iloc[-1]['content']
        try:
            if (
                    to_dict(content)['action_response'].keys() >= {'function',
                                                                   'arguments', 'output'}
            ):
                return True
        except:
            return False

    # def add_instruction_set(self, name: str, instruction_set: InstructionSet):
    #     """
    #     Add an instruction set to the conversation.
    #
    #     Args:
    #         name (str): The name of the instruction set.
    #         instruction_set (InstructionSet): The instruction set to add.
    #
    #     Examples:
    #         >>> branch.add_instruction_set("greet", InstructionSet(instructions=["Hello", "Hi"]))
    #     """
    #     self.instruction_sets[name] = instruction_set

    # def remove_instruction_set(self, name: str) -> bool:
    #     """
    #     Remove an instruction set from the conversation.
    #
    #     Args:
    #         name (str): The name of the instruction set to remove.
    #
    #     Returns:
    #         bool: True if the instruction set was removed, False otherwise.
    #
    #     Examples:
    #         >>> branch.remove_instruction_set("greet")
    #         True
    #     """
    #     return self.instruction_sets.pop(name)

    # async def instruction_set_auto_followup(
    #     self,
    #     instruction_set: InstructionSet,
    #     num: Union[int, List[int]] = 3,
    #     **kwargs
    # ) -> None:
    #     """
    #     Automatically perform follow-up chats for an entire instruction set.
    #
    #     This method asynchronously conducts follow-up chats for each instruction in the provided instruction set,
    #     handling tools invocations as specified.
    #
    #     Args:
    #         instruction_set (InstructionSet): The instruction set to process.
    #         num (Union[int, List[int]]): The maximum number of follow-up chats to perform for each instruction,
    #                                       or a list of maximum numbers corresponding to each instruction.
    #         **kwargs: Additional keyword arguments to pass to the chat.py completion provider.
    #
    #     Raises:
    #         ValueError: If the length of `num` as a list does not match the number of instructions in the set.
    #
    #     Examples:
    #         >>> instruction_set = InstructionSet(instructions=["What's the weather?", "And for tomorrow?"])
    #         >>> await branch.instruction_set_auto_followup(instruction_set)
    #     """
    #
    #     if isinstance(num, List):
    #         if len(num) != instruction_set.instruct_len:
    #             raise ValueError(
    #                 'Unmatched auto_followup num size and instructions set size'
    #             )
    #     current_instruct_node = instruction_set.get_instruction_by_id(
    #         instruction_set.first_instruct
    #     )
    #     for i in range(instruction_set.instruct_len):
    #         num_ = num if isinstance(num, int) else num[i]
    #         tools = instruction_set.get_tools(current_instruct_node)
    #         if tools:
    #             await self.auto_followup(
    #                 current_instruct_node, num=num_, tools=tools, self=self, **kwargs
    #             )
    #         else:
    #             await self.chat.py(current_instruct_node)
    #         current_instruct_node = instruction_set.get_next_instruction(
    #             current_instruct_node
    #         )
