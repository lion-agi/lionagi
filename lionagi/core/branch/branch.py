import json

import pandas as pd

from typing import Any, Callable, Dict, List, Optional, Union
import asyncio
from dotenv import load_dotenv

from lionagi.utils import alcall, as_dict, get_flattened_keys, lcall
from lionagi.schema import Tool
from lionagi._services.base_service import StatusTracker
from lionagi._services.oai import OpenAIService
from lionagi.configs.oai_configs import oai_schema
from lionagi.tools.tool_manager import ToolManager

from ..messages.messages import Instruction, System
from ..instruction_set.instruction_set import InstructionSet

from .conversation import Conversation

load_dotenv()

oai_service = OpenAIService()

class Branch(Conversation):
    """
    Represents a conversation branch with messages, instruction sets, and tool management.

    A `Branch` is a type of conversation that can have messages, system instructions, and registered tools
    for interacting with external services or tools.

    Attributes:
        dir (str): The directory path for storing logs.
        messages (pd.DataFrame): A DataFrame containing conversation messages.
        instruction_sets (Dict[str, InstructionSet]): A dictionary of instruction sets mapped by their names.
        tool_manager (ToolManager): An instance of ToolManager for managing tools.
        service (OpenAIService): An instance of OpenAIService to interact with OpenAI API.
        status_tracker (StatusTracker): An instance of StatusTracker to keep track of the status.
        llmconfig (Dict): Configuration for the language model.

    Examples:
        >>> branch = Branch(dir="path/to/log")
        >>> branch.add_instruction_set("greet", InstructionSet(instructions=["Hello", "Hi"]))
        >>> branch.remove_instruction_set("greet")
        True
        >>> tool = Tool(name="calculator")
        >>> branch.register_tools(tool)
        >>> branch.messages_describe()  # doctest: +SKIP
        {'total_messages': 0, 'summary_by_role': ..., 'summary_by_sender': ..., 'instruction_sets': {}, 'registered_tools': {'calculator': ...}, 'messages': []}
    """

    def __init__(
        self,
        dir: Optional[str] = None,
        messages: Optional[pd.DataFrame] = None,
        instruction_sets: Optional[Dict[str, InstructionSet]] = None,
        tool_manager: Optional[ToolManager] = None,
        service: OpenAIService = oai_service,
        llmconfig: Optional[Dict] = None,
    ):
        """
        Initializes a new Branch instance.

        Args:
            dir (Optional[str]): The directory path for storing logs.
            messages (Optional[pd.DataFrame]): A DataFrame containing conversation messages.
            instruction_sets (Optional[Dict[str, InstructionSet]]): A dictionary of instruction sets.
            tool_manager (Optional[ToolManager]): An instance of ToolManager for managing tools.
            service (OpenAIService): The OpenAI service instance.
            llmconfig (Optional[Dict]): Configuration for the language model.
        """
        super().__init__(dir)
        self.messages = (
            messages
            if messages is not None
            else pd.DataFrame(
                columns=["node_id", "role", "sender", "timestamp", "content"]
            )
        )
        self.instruction_sets = instruction_sets if instruction_sets else {}
        self.tool_manager = tool_manager if tool_manager else ToolManager()

        self.service=service
        self.status_tracker = StatusTracker()
        self.llmconfig = llmconfig or oai_schema["chat/completions"]["config"]

    def change_system_message(
        self, system: Union[str, Dict[str, Any], System], sender: Optional[str] = None
    ):
        """
        Change the system message of the conversation.

        Args:
            system (Union[str, Dict[str, Any], System]): The new system message.
            sender (Optional[str]): The sender of the system message.

        Raises:
            ValueError: If the input cannot be converted into a system message.

        Examples:
            >>> branch.change_system_message("System update", sender="admin")
            >>> branch.change_system_message({"text": "System reboot", "type": "update"})
        """
        if isinstance(system, (str, Dict)):
            system = System(system, sender=sender)
        if isinstance(system, System):
            message_dict = system.to_dict()
            if sender:
                message_dict['sender'] = sender
            message_dict['timestamp'] = str(pd.Timestamp.now())
            self.add_message(system=message_dict)
            df = self.messages[self.messages.role == 'system']
            df.loc[0] = message_dict
        else:
            raise ValueError("Input cannot be converted into a system message.")

    def add_instruction_set(self, name: str, instruction_set: InstructionSet):
        """
        Add an instruction set to the conversation.

        Args:
            name (str): The name of the instruction set.
            instruction_set (InstructionSet): The instruction set to add.

        Examples:
            >>> branch.add_instruction_set("greet", InstructionSet(instructions=["Hello", "Hi"]))
        """
        self.instruction_sets[name] = instruction_set

    def remove_instruction_set(self, name: str) -> bool:
        """
        Remove an instruction set from the conversation.

        Args:
            name (str): The name of the instruction set to remove.

        Returns:
            bool: True if the instruction set was removed, False otherwise.

        Examples:
            >>> branch.remove_instruction_set("greet")
            True
        """
        return self.instruction_sets.pop(name)

    def register_tools(self, tools: Union[Tool, List[Tool]]):
        """
        Register one or more tools with the conversation's tool manager.

        Args:
            tools (Union[Tool, List[Tool]]): The tools to register.

        Examples:
            >>> tool = Tool(name="calculator")
            >>> branch.register_tools(tool)
        """
        if not isinstance(tools, list):
            tools = [tools]
        self.tool_manager.register_tools(tools=tools)

    def delete_tool(self, name: str) -> bool:
        """
        Delete a tool from the conversation's tool manager.

        Args:
            name (str): The name of the tool to delete.

        Returns:
            bool: True if the tool was deleted, False otherwise.

        Examples:
            >>> branch.delete_tool("calculator")
            True
        """
        if name in self.tool_manager.registry:
            self.tool_manager.registry.pop(name)
            return True
        return False

    def clone(self) -> 'Branch':
        """
        Create a clone of the conversation.

        Returns:
            Branch: A new Branch object that is a clone of the current conversation.

        Examples:
            >>> cloned_branch = branch.clone()
        """
        cloned = Branch(
            dir = self._logger.dir,
            messages=self.messages.copy(), 
            instruction_sets=self.instruction_sets.copy(),
            tool_manager=ToolManager()
        )
        tools = [
            tool for tool in self.tool_manager.registry.values()]
        
        cloned.register_tools(tools)

        return cloned

    def merge_branch(self, branch: 'Branch', update: bool = True):
        """
        Merge another Branch into this Branch.

        Args:
            branch (Branch): The Branch to merge into this one.
            update (bool): If True, update existing instruction sets and tools, 
                otherwise only add non-existing ones.

        """
        message_copy = branch.messages.copy()
        branch_system = message_copy.loc[0]
        message_copy.drop(0, inplace=True)
        self.messages = self.messages.merge(message_copy, how='outer')

        if update:
            self.instruction_sets.update(branch.instruction_sets)
            self.tool_manager.registry.update(
                branch.tool_manager.registry
            )
            self.messages.loc[0] = branch_system
        else:
            for key, value in branch.instruction_sets.items():
                if key not in self.instruction_sets:
                    self.instruction_sets[key] = value

            for key, value in branch.tool_manager.registry.items():
                if key not in self.tool_manager.registry:
                    self.tool_manager.registry[key] = value

    def messages_describe(self) -> Dict[str, Any]:
        """
        Describe the conversation and its messages.

        Returns:
            Dict[str, Any]: A dictionary containing information about the conversation and its messages.

        Examples:
            >>> description = branch.messages_describe()
            >>> print(description["total_messages"])
            0
        """
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self.info(),
            "summary_by_sender": self.info(use_sender=True),
            "instruction_sets": self.instruction_sets,
            "registered_tools": self.tool_manager.registry,
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    def to_chatcompletion_message(self) -> List[Dict[str, Any]]:
        """
        Convert the conversation into a chat completion message format suitable for the OpenAI API.

        Returns:
            List[Dict[str, Any]]: A list of messages in chat completion message format.

        Examples:
            >>> chat_completion_message = branch.to_chatcompletion_message()
        """
        message = []
        for _, row in self.messages.iterrows():
            content_ = row['content']
            if content_.startswith('Sender'):
                content_ = content_.split(':', 1)[1]
            if isinstance(content_, str):
                try:
                    content_ = json.dumps(as_dict(content_))
                except Exception as e:
                    raise ValueError(f"Error in serealizing, {row['node_id']} {content_}: {e}")
                
            out = {"role": row['role'], "content": content_}
            message.append(out)
        return message

    def _is_invoked(self) -> bool:
        """
        Check if the conversation has been invoked with an action response.

        Returns:
            bool: True if the conversation has been invoked, False otherwise.

        """
        content = self.messages.iloc[-1]['content']
        try:
            if (
                as_dict(content)['action_response'].keys() >= {'function', 'arguments', 'output'}
            ):
                return True
        except:
            return False
    
    async def call_chatcompletion(self, **kwargs):
        """
        Call the chat completion service with the current conversation messages.

        This method asynchronously sends the messages to the OpenAI service and updates the conversation
        with the response.

        Args:
            **kwargs: Additional keyword arguments to pass to the chat completion service.

        """
        messages = self.to_chatcompletion_message()
        payload, completion = await self.service.serve_chat(messages=messages, **kwargs)
        if "choices" in completion:
            self._logger.add_entry({"input": payload, "output": completion})
            self.add_message(response=completion['choices'][0])
            self.status_tracker.num_tasks_succeeded += 1
        else:
            self.status_tracker.num_tasks_failed += 1

    @property
    def has_tools(self) -> bool:
        """
        Check if there are any tools registered in the tool manager.

        Returns:
            bool: True if there are tools registered, False otherwise.

        """
        return self.tool_manager.registry != {}

    async def chat(
        self,
        instruction: Union[Instruction, str],
        system: Optional[Union[System, str, Dict[str, Any]]] = None,
        context: Optional[Any] = None,
        out: bool = True,
        sender: Optional[str] = None,
        invoke: bool = True,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        **kwargs
    ) -> Any:
        """
        Conduct a chat with the conversation, processing instructions and potentially using tools.

        This method asynchronously handles a chat instruction, updates the conversation with the response,
        and performs tool invocations if specified.

        Args:
            instruction (Union[Instruction, str]): The chat instruction to process.
            system (Optional[Union[System, str, Dict[str, Any]]]): The system message to include in the chat.
            context (Optional[Any]): Additional context to include in the chat.
            out (bool): If True, return the output of the chat.
            sender (Optional[str]): The sender of the chat instruction.
            invoke (bool): If True, invoke tools based on the chat response.
            tools (Union[bool, Tool, List[Tool], str, List[str]]): Tools to potentially use during the chat.
            **kwargs: Additional keyword arguments to pass to the chat completion service.

        Returns:
            Any: The output of the chat, if out is True.

        Examples:
            >>> result = await branch.chat("What is the weather today?")
            >>> print(result)
        """
        
        config = {**self.llmconfig}
        
        if system:
            self.change_system_message(system)
        self.add_message(instruction=instruction, context=context, sender=sender)

        if 'tool_parsed' in kwargs:
            kwargs.pop('tool_parsed')
            tool_kwarg = {'tools': tools}
            kwargs = {**tool_kwarg, **kwargs}
            config.update(kwargs)
        else:
            if tools and self.has_tools:
                kwargs = self.tool_manager._tool_parser(tools=tools, **kwargs)
                config.update(kwargs)

        await self.call_chatcompletion(**config)
        
        async def _output():
            content_ = as_dict(self.messages.content.iloc[-1])
            if invoke:
                try:
                    tool_uses = content_
                    func_calls = lcall(
                        [as_dict(i) for i in tool_uses["action_list"]], 
                        self.tool_manager.get_function_call
                    )
                    outs = await alcall(func_calls, self.tool_manager.invoke)
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

    async def auto_followup(
        self,
        instruction: Union[Instruction, str],
        num: int = 3,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        fallback: Optional[Callable] = None,
        fallback_kwargs: Optional[Dict] = None,
        **kwargs
    ) -> None:
        """
        Automatically perform follow-up chats based on the conversation state.

        This method asynchronously conducts follow-up chats based on the conversation state and tool invocations,
        with an optional fallback if the maximum number of follow-ups is reached.

        Args:
            instruction (Union[Instruction, str]): The chat instruction to process.
            num (int): The maximum number of follow-up chats to perform.
            tools (Union[bool, Tool, List[Tool], str, List[str], List[Dict]]): Tools to potentially use during the chats.
            fallback (Optional[Callable]): A fallback function to call if the maximum number of follow-ups is reached.
            fallback_kwargs (Optional[Dict]): Keyword arguments to pass to the fallback function.
            **kwargs: Additional keyword arguments to pass to the chat completion service.

        Examples:
            >>> await branch.auto_followup("Could you elaborate on that?")
        """
        if self.tool_manager.registry != {} and tools:
            kwargs = self.tool_manager._tool_parser(tools=tools, **kwargs)

        cont_ = True
        while num > 0 and cont_ is True:
            if tools:
                await self.chat(instruction, tool_choice="auto", tool_parsed=True, out=False, **kwargs)
            else:
                await self.chat(instruction, tool_parsed=True,  out=False, **kwargs)
            num -= 1
            cont_ = True if self._is_invoked() else False
        if num == 0:
            if fallback is not None:
                if asyncio.iscoroutinefunction(fallback):
                    return await fallback(**fallback_kwargs)
                else:
                    return fallback(**fallback_kwargs)
            return await self.chat(instruction, tool_parsed=True, **kwargs)
        
    async def instruction_set_auto_followup(
        self,
        instruction_set: InstructionSet,
        num: Union[int, List[int]] = 3,
        **kwargs
    ) -> None:
        """
        Automatically perform follow-up chats for an entire instruction set.

        This method asynchronously conducts follow-up chats for each instruction in the provided instruction set,
        handling tool invocations as specified.

        Args:
            instruction_set (InstructionSet): The instruction set to process.
            num (Union[int, List[int]]): The maximum number of follow-up chats to perform for each instruction,
                                          or a list of maximum numbers corresponding to each instruction.
            **kwargs: Additional keyword arguments to pass to the chat completion service.

        Raises:
            ValueError: If the length of `num` as a list does not match the number of instructions in the set.

        Examples:
            >>> instruction_set = InstructionSet(instructions=["What's the weather?", "And for tomorrow?"])
            >>> await branch.instruction_set_auto_followup(instruction_set)
        """

        if isinstance(num, List):
            if len(num) != instruction_set.instruct_len:
                raise ValueError(
                    'Unmatched auto_followup num size and instructions set size'
                )
        current_instruct_node = instruction_set.get_instruction_by_id(
            instruction_set.first_instruct
        )
        for i in range(instruction_set.instruct_len):
            num_ = num if isinstance(num, int) else num[i]
            tools = instruction_set.get_tools(current_instruct_node)
            if tools:
                await self.auto_followup(
                    current_instruct_node, num=num_, tools=tools, self=self, **kwargs
                )
            else:
                await self.chat(current_instruct_node)
            current_instruct_node = instruction_set.get_next_instruction(
                current_instruct_node
            )
