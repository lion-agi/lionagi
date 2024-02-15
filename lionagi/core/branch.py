import json
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from lionagi.utils.sys_util import create_path, is_same_dtype
from lionagi.utils import as_dict, lcall,to_df, to_list, CoreUtil


from lionagi.iservices.base_service import BaseService, StatusTracker
from lionagi.iservices.oai import OpenAIService
from lionagi.iservices.openrouter import OpenRouterService
from lionagi.configs.oai_configs import oai_schema
from lionagi.configs.openrouter_configs import openrouter_schema
from lionagi.schema import DataLogger, Tool
from lionagi.tools.tool_manager import ToolManager
from lionagi.core.branch_manager import Request
from lionagi.core.instruction_set import InstructionSet
from lionagi.core.messages import Instruction, Message, Response, System
from lionagi.core.flow import ChatFlow

OAIService = None
try:
    OAIService = OpenAIService()
except:
    pass

class Branch:
    _cols = ["node_id", "role", "sender", "timestamp", "content"]
    
    def __init__(self, name: Optional[str] = None, messages: Optional[pd.DataFrame] = None,
                instruction_sets: Optional[Dict[str, InstructionSet]] = None,
                tool_manager: Optional[ToolManager] = None, service: Optional[BaseService] = None, llmconfig: Optional[Dict] = None, tools=None, dir=None, logger=None):
        """
        Initializes a new instance of the Branch class.

        Args:
            name (Optional[str]): The name of the branch.
            messages (Optional[pd.DataFrame]): A DataFrame containing messages for the branch.
            instruction_sets (Optional[Dict[str, InstructionSet]]): A dictionary of instruction sets.
            tool_manager (Optional[ToolManager]): The tool manager for the branch.
            service (Optional[BaseService]): The service associated with the branch.
            llmconfig (Optional[Dict]): Configuration for the LLM service.
            tools (Optional[List[Tool]]): Initial list of tools to register with the tool manager.
            dir (Optional[str]): Directory path for data logging.

        Examples:
            >>> branch = Branch(name="CustomerService")
            >>> branch_with_messages = Branch(name="Support", messages=pd.DataFrame(columns=["node_id", "content"]))
        """
        
        self.messages = pd.DataFrame(columns=Branch._cols)
        self.messages = (
            messages
            if messages is not None
            else pd.DataFrame(
                columns=["node_id", "role", "sender", "timestamp", "content"]
            )
        )
        self.tool_manager = tool_manager if tool_manager else ToolManager()
        try:
            self.register_tools(tools)
        except Exception as e:
            raise TypeError(f"Error in registering tools: {e}")
        
        self.instruction_sets = instruction_sets if instruction_sets else {}
        self.status_tracker = StatusTracker()
        self._add_service(service, llmconfig)
        self.name = name
        self.pending_ins = {}
        self.pending_outs = deque()
        self.logger = logger or DataLogger(dir=dir)


# ---- properties ---- #
    @property
    def chat_messages(self):
        """
        Generates chat completion messages without sender information.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing chat messages.
        """
        return self._to_chatcompletion_message()

    @property
    def chat_messages_with_sender(self):
        """
        Generates chat completion messages including sender information.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing chat messages with sender details.
        """
        return self._to_chatcompletion_message(with_sender=True) 

    @property
    def messages_describe(self) -> Dict[str, Any]:
        """
        Provides a descriptive summary of all messages in the branch.

        Returns:
            Dict[str, Any]: A dictionary containing summaries of messages by role and sender, 
            total message count, instruction sets, registered tools, and message details.
        """
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self._info(),
            "summary_by_sender": self._info(use_sender=True),
            "instruction_sets": self.instruction_sets,
            "registered_tools": self.tool_manager.registry,
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    @property
    def has_tools(self) -> bool:
        """
        Checks if there are any tools registered in the tool manager.

        Returns:
            bool: True if there are tools registered, False otherwise.
        """
        return self.tool_manager.registry != {}

    @property
    def last_message(self) -> pd.Series:
        """
        Retrieves the last message from the conversation.

        Returns:
            pd.Series: The last message as a pandas Series.
        """
        return CoreUtil.get_rows(self.messages, n=1, from_='last')
    
    @property
    def first_system(self) -> pd.Series:
        """
        Retrieves the first system message from the conversation.

        Returns:
            pd.Series: The first system message as a pandas Series.
        """
        return CoreUtil.get_rows(self.messages, role='system', n=1, from_='front')
        
    @property
    def last_response(self) -> pd.Series:
        """
        Retrieves the last response message from the conversation.

        Returns:
            pd.Series: The last response message as a pandas Series.
        """
        return CoreUtil.get_rows(self.messages, role='assistant', n=1, from_='last')

    @property
    def last_response_content(self) -> Dict:
        """
        Retrieves the content of the last response message from the conversation.

        Returns:
            Dict: The content of the last response message as a dictionary
        """
        return as_dict(self.last_response.content.iloc[-1])

    @property
    def action_request(self) -> pd.DataFrame:
        """
        Retrieves all action request messages from the conversation.

        Returns:
            pd.DataFrame: A DataFrame containing all action request messages.
        """
        return to_df(self.messages[self.messages.sender == 'action_request'])
    
    @property
    def action_response(self) -> pd.DataFrame:
        """
        Retrieves all action response messages from the conversation.

        Returns:
            pd.DataFrame: A DataFrame containing all action response messages.
        """
        return to_df(self.messages[self.messages.sender == 'action_response'])

    @property
    def responses(self) -> pd.DataFrame:
        """
        Retrieves all response messages from the conversation.

        Returns:
            pd.DataFrame: A DataFrame containing all response messages.
        """
        return to_df(self.messages[self.messages.role == 'assistant'])

    @property
    def assistant_responses(self) -> pd.DataFrame:
        """
        Retrieves all assistant responses from the conversation, excluding action requests and responses.

        Returns:
            pd.DataFrame: A DataFrame containing assistant responses excluding action requests and responses.
        """
        a_responses = self.responses[self.responses.sender != 'action_response']
        a_responses = a_responses[a_responses.sender != 'action_request']
        return to_df(a_responses)

    @property
    def info(self) -> Dict[str, int]:
        """
        Get a summary of the conversation messages categorized by role.

        Returns:
            Dict[str, int]: A dictionary with keys as message roles and values as counts.
        """
        
        return self._info()
    
    @property
    def sender_info(self) -> Dict[str, int]:
        """
        Provides a descriptive summary of the conversation, including total message count and summary by sender.

        Returns:
            Dict[str, Any]: A dictionary containing the total number of messages and a summary categorized by sender.
        """
        return self._info(use_sender=True)
    
    @property
    def describe(self) -> Dict[str, Any]:
        """
        Provides a descriptive summary of the conversation, including the total number of messages,
        a summary by role, and the first five messages.

        Returns:
            Dict[str, Any]: A dictionary containing the total number of messages, summary by role, and a list of the first maximum five message dictionaries.
        """
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self._info(),
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ][: self.len_messages -1 if self.len_messages < 5 else 5],
        }

# ---- I/O ---- #
    @classmethod
    def from_csv(cls, filepath: str, name: Optional[str] = None,
                instruction_sets: Optional[Dict[str, InstructionSet]] = None,
                tool_manager: Optional[ToolManager] = None, service: Optional[BaseService] = None,
                llmconfig: Optional[Dict] = None, tools=None, **kwargs) -> 'Branch':
        """
        Creates a Branch instance from a CSV file containing messages.

        Args:
            filepath (str): Path to the CSV file.
            name (Optional[str]): Name of the branch, default is None.
            instruction_sets (Optional[Dict[str, InstructionSet]]): Instruction sets, default is None.
            tool_manager (Optional[ToolManager]): Tool manager for the branch, default is None.
            service (Optional[BaseService]): External service for the branch, default is None.
            llmconfig (Optional[Dict]): Configuration for language learning models, default is None.
            tools (Optional[List[Tool]]): Initial list of tools to register, default is None.
            **kwargs: Additional keyword arguments for pd.read_csv().

        Returns:
            Branch: A new Branch instance created from the CSV data.

        Examples:
            >>> branch = Branch.from_csv("path/to/messages.csv", name="ImportedBranch")
        """
        df = pd.read_csv(filepath, **kwargs)
        self = cls(
            name=name, 
            messages=df, 
            instruction_sets=instruction_sets, 
            tool_manager=tool_manager, 
            service=service,
            llmconfig=llmconfig,
            tools=tools
        )
        
        return self

    @classmethod
    def from_json(cls, filepath: str, name: Optional[str] = None,
                instruction_sets: Optional[Dict[str, InstructionSet]] = None,
                tool_manager: Optional[ToolManager] = None, service: Optional[BaseService] = None,
                llmconfig: Optional[Dict] = None, **kwargs) -> 'Branch':
        """
        Creates a Branch instance from a JSON file containing messages.

        Args:
            filepath (str): Path to the JSON file.
            name (Optional[str]): Name of the branch, default is None.
            instruction_sets (Optional[Dict[str, InstructionSet]]): Instruction sets, default is None.
            tool_manager (Optional[ToolManager]): Tool manager for the branch, default is None.
            service (Optional[BaseService]): External service for the branch, default is None.
            llmconfig (Optional[Dict]): Configuration for language learning models, default is None.
            **kwargs: Additional keyword arguments for pd.read_json().

        Returns:
            Branch: A new Branch instance created from the JSON data.

        Examples:
            >>> branch = Branch.from_json("path/to/messages.json", name="JSONBranch")
        """
        df = pd.read_json(filepath, **kwargs)
        self = cls(
            name=name, 
            messages=df, 
            instruction_sets=instruction_sets, 
            tool_manager=tool_manager, 
            service=service,
            llmconfig=llmconfig
        )
        return self


    def to_csv(self, filename: str = 'messages.csv', file_exist_ok: bool = False,
            timestamp: bool = True, time_prefix: bool = False,
            verbose: bool = True, clear: bool = True, **kwargs):
        """
        Saves the branch's messages to a CSV file.

        Args:
            filename (str): The name of the output CSV file, default is 'messages.csv'.
            file_exist_ok (bool): If True, does not raise an error if the directory already exists, default is False.
            timestamp (bool): If True, appends a timestamp to the filename, default is True.
            time_prefix (bool): If True, adds a timestamp prefix to the filename, default is False.
            verbose (bool): If True, prints a message upon successful save, default is True.
            clear (bool): If True, clears the messages after saving, default is True.
            **kwargs: Additional keyword arguments for DataFrame.to_csv().

        Examples:
            >>> branch.to_csv("exported_messages.csv")
            >>> branch.to_csv("timed_export.csv", timestamp=True, time_prefix=True)
        """
        
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        filepath = create_path(
            self.logger.dir, filename, timestamp=timestamp, 
            dir_exist_ok=file_exist_ok, time_prefix=time_prefix
        )
        
        try:
            self.messages.to_csv(filepath, **kwargs)
            if verbose:
                print(f"{len(self.messages)} messages saved to {filepath}")
            if clear:
                self.clear_messages()
        except Exception as e:
            raise ValueError(f"Error in saving to csv: {e}")

    def to_json(self, filename: str = 'messages.json', file_exist_ok: bool = False,
                timestamp: bool = True, time_prefix: bool = False,
                verbose: bool = True, clear: bool = True, **kwargs):
        """
        Saves the branch's messages to a JSON file.

        Args:
            filename (str): The name of the output JSON file, default is 'messages.json'.
            file_exist_ok (bool): If True, does not raise an error if the directory already exists, default is False.
            timestamp (bool): If True, appends a timestamp to the filename, default is True.
            time_prefix (bool): If True, adds a timestamp prefix to the filename, default is False.
            verbose (bool): If True, prints a message upon successful save, default is True.
            clear (bool): If True, clears the messages after saving, default is True.
            **kwargs: Additional keyword arguments for DataFrame.to_json().

        Examples:
            >>> branch.to_json("exported_messages.json")
            >>> branch.to_json("timed_export.json", timestamp=True, time_prefix=True)
        """
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = create_path(
            self.dir, filename, timestamp=timestamp, 
            dir_exist_ok=file_exist_ok, time_prefix=time_prefix
        )
        
        try:
            self.messages.to_json(
                filepath, orient="records", lines=True, 
                date_format="iso", **kwargs
            )
            if clear:
                self.clear_messages()
            if verbose:
                print(f"{len(self.messages)} messages saved to {filepath}")
        except Exception as e:
            raise ValueError(f"Error in saving to json: {e}")

    def log_to_csv(self, filename: str = 'log.csv', file_exist_ok: bool = False, timestamp: bool = True,
                time_prefix: bool = False, verbose: bool = True, clear: bool = True, **kwargs):
        """
        Saves the branch's log data to a CSV file.

        This method is designed to export log data, potentially including operations and interactions,
        to a CSV file for analysis or record-keeping.

        Args:
            filename (str): The name of the output CSV file. Defaults to 'log.csv'.
            file_exist_ok (bool): If True, will not raise an error if the directory already exists. Defaults to False.
            timestamp (bool): If True, appends a timestamp to the filename for uniqueness. Defaults to True.
            time_prefix (bool): If True, adds a timestamp prefix to the filename. Defaults to False.
            verbose (bool): If True, prints a success message upon completion. Defaults to True.
            clear (bool): If True, clears the log after saving. Defaults to True.
            **kwargs: Additional keyword arguments for `DataFrame.to_csv()`.

        Examples:
            >>> branch.log_to_csv("branch_log.csv")
            >>> branch.log_to_csv("detailed_branch_log.csv", timestamp=True, verbose=True)
        """
        self.logger.to_csv(
            filename=filename, file_exist_ok=file_exist_ok, timestamp=timestamp, 
            time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
        )

    def log_to_json(self, filename: str = 'log.json', file_exist_ok: bool = False, timestamp: bool = True,
                    time_prefix: bool = False, verbose: bool = True, clear: bool = True, **kwargs):
        """
        Saves the branch's log data to a JSON file.

        Useful for exporting log data in JSON format, allowing for easy integration with web applications
        and services that consume JSON.

        Args:
            filename (str): The name of the output JSON file. Defaults to 'log.json'.
            file_exist_ok (bool): If directory existence should not raise an error. Defaults to False.
            timestamp (bool): If True, appends a timestamp to the filename. Defaults to True.
            time_prefix (bool): If True, adds a timestamp prefix to the filename. Defaults to False.
            verbose (bool): If True, prints a success message upon completion. Defaults to True.
            clear (bool): If True, clears the log after saving. Defaults to True.
            **kwargs: Additional keyword arguments for `DataFrame.to_json()`.

        Examples:
            >>> branch.log_to_json("branch_log.json")
            >>> branch.log_to_json("detailed_branch_log.json", verbose=True, timestamp=True)
        """
        self.logger.to_json(
            filename=filename, file_exist_ok=file_exist_ok, timestamp=timestamp, 
            time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
        )

# ----- chatflow ----#
    async def call_chatcompletion(self, sender=None, with_sender=False, tokenizer_kwargs={}, **kwargs):
        """
        Asynchronously calls the chat completion service with the current message queue.

        This method prepares the messages for chat completion, sends the request to the configured service, and handles the response. The method supports additional keyword arguments that are passed directly to the service.

        Args:
            sender (Optional[str]): The name of the sender to be included in the chat completion request. Defaults to None.
            with_sender (bool): If True, includes the sender's name in the messages. Defaults to False.
            **kwargs: Arbitrary keyword arguments passed directly to the chat completion service.

        Examples:
            >>> await branch.call_chatcompletion()
        """
        await ChatFlow.call_chatcompletion(
            self, sender=sender, with_sender=with_sender, 
            tokenizer_kwargs=tokenizer_kwargs, **kwargs
        )
    
    async def chat(
        self,
        instruction: Union[Instruction, str],
        context: Optional[Any] = None,
        sender: Optional[str] = None,
        system: Optional[Union[System, str, Dict[str, Any]]] = None,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        out: bool = True,
        invoke: bool = True,
        **kwargs) -> Any:
        """
        Initiates a chat conversation, processing instructions and system messages, optionally invoking tools.

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
        return await ChatFlow.chat(
            self, instruction=instruction, context=context, 
            sender=sender, system=system, tools=tools, 
            out=out, invoke=invoke, **kwargs
        )

    async def ReAct(
        self,
        instruction: Union[Instruction, str],
        context = None,
        sender = None,
        system = None,
        tools = None, 
        num_rounds: int = 1,
        **kwargs ):
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
        return await ChatFlow.ReAct(
            self, instruction=instruction, context=context, 
            sender=sender, system=system, tools=tools, 
            num_rounds=num_rounds, **kwargs
        )

    async def auto_followup(
        self,
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
        return await ChatFlow.auto_followup(
            self, instruction=instruction, context=context, 
            sender=sender, system=system, tools=tools, 
            max_followup=max_followup, out=out, **kwargs
        )

# ---- branch operations ---- #
    def clone(self) -> 'Branch':
        """
        Creates a copy of the current Branch instance.

        This method is useful for duplicating the branch's state, including its messages,
        instruction sets, and tool registrations, into a new, independent Branch instance.

        Returns:
            Branch: A new Branch instance that is a deep copy of the current one.

        Examples:
            >>> cloned_branch = original_branch.clone()
            >>> assert cloned_branch.messages.equals(original_branch.messages)
        """
        cloned = Branch(
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
        Merges another branch into the current Branch instance.

        Incorporates messages, instruction sets, and tool registrations from the specified branch,
        optionally updating existing instruction sets and tools if duplicates are found.

        Args:
            branch (Branch): The branch to merge into the current one.
            update (bool): If True, existing instruction sets and tools are updated. Defaults to True.

        Examples:
            >>> main_branch.merge_branch(another_branch, update=True)
            >>> main_branch.merge_branch(temporary_branch, update=False)
        """

        message_copy = branch.messages.copy()
        self.messages = self.messages.merge(message_copy, how='outer')

        if update:
            self.instruction_sets.update(branch.instruction_sets)
            self.tool_manager.registry.update(
                branch.tool_manager.registry
            )
        else:
            for key, value in branch.instruction_sets.items():
                if key not in self.instruction_sets:
                    self.instruction_sets[key] = value

            for key, value in branch.tool_manager.registry.items():
                if key not in self.tool_manager.registry:
                    self.tool_manager.registry[key] = value

# ----- tool manager methods ----- #
    def register_tools(self, tools: Union[Tool, List[Tool]]) -> None:
        """
        Registers one or more tools with the branch's tool manager.

        This method allows for the dynamic addition of tools to the branch, enhancing its
        capabilities and interactions with users or external systems.

        Args:
            tools (Union[Tool, List[Tool]]): A single tool instance or a list of Tool instances to register.

        Examples:
            >>> branch.register_tools(tool_instance)
            >>> branch.register_tools([tool_one, tool_two, tool_three])
        """
        if not isinstance(tools, list):
            tools = [tools]
        self.tool_manager.register_tools(tools=tools)

    def delete_tool(self, tools: Union[Tool, List[Tool], str, List[str]], verbose=True) -> bool:
        """
        Deletes one or more tools from the branch's tool manager.

        This method allows for the removal of tools previously registered with the branch, either by tool instance or name.

        Args:
            tools (Union[Tool, List[Tool], str, List[str]]): A single tool instance, tool name, or a list of either to be deleted.
            verbose (bool): If True, prints a success message upon deletion. Defaults to True.

        Returns:
            bool: True if the tool(s) were successfully deleted, False otherwise.

        Examples:
            >>> branch.delete_tool("tool_name")
            >>> branch.delete_tool(tool_instance)
            >>> branch.delete_tool(["tool_one", "tool_two"])
        """
        if isinstance(tools, list):
            if is_same_dtype(tools, str):
                for tool in tools:
                    if tool in self.tool_manager.registry:
                        self.tool_manager.registry.pop(tool)
                if verbose:
                    print("tools successfully deleted")
                return True
            elif is_same_dtype(tools, Tool):
                for tool in tools:
                    if tool.name in self.tool_manager.registry:
                        self.tool_manager.registry.pop(tool.name)
                if verbose:
                    print("tools successfully deleted")
                return True
        if verbose:
            print("tools deletion failed")
        return False

# ---- message operations ----#
    def add_message(self, system: Optional[Union[dict, list, System]] = None,
                    instruction: Optional[Union[dict, list, Instruction]] = None,
                    context: Optional[Union[str, Dict[str, Any]]] = None,
                    response: Optional[Union[dict, list, Response]] = None,
                    sender: Optional[str] = None) -> None:
        """
        Adds a message to the branch's conversation.

        Supports adding different types of messages: system, instruction, and response. Each message
        type is added with a timestamp and sender information.

        Args:
            system (Optional[Union[dict, list, System]]): System message to add.
            instruction (Optional[Union[dict, list, Instruction]]): Instruction message to add.
            context (Optional[Union[str, Dict[str, Any]]]): Context associated with the instruction.
            response (Optional[Union[dict, list, Response]]): Response message to add.
            sender (Optional[str]): Identifier for the sender of the message.

        Examples:
            >>> branch.add_message(system={'content': 'System initialized'}, sender='system')
            >>> branch.add_message(instruction={'content': 'Please respond'}, sender='user')
        """
        msg = self._create_message(
            system=system, instruction=instruction, 
            context=context, response=response, sender=sender
        )
        message_dict = msg.to_dict()
        if isinstance(as_dict(message_dict['content']), dict):
            message_dict['content'] = json.dumps(message_dict['content'])
        message_dict['timestamp'] = datetime.now().isoformat()
        self.messages.loc[len(self.messages)] = message_dict
    
    def remove_message(self, node_id: str) -> None:
        """
        Removes a message from the branch's conversation based on its node ID.

        Args:
            node_id (str): The unique identifier of the message to be removed.

        Examples:
            >>> branch.remove_message("12345")
        """
        CoreUtil.remove_message(self.messages, node_id)
    
    def update_message(
        self, value: Any, node_id: Optional[str] = None, col: str = 'node_id'
    ) -> None:
        """
        Updates a message in the conversation based on its node_id.

        Args:
            value (Any): The new value to update the message with.
            node_id (Optional[str], optional): The node_id of the message to be updated. Defaults to None.
            col (str, optional): The column to be updated. Defaults to 'node_id'.

        Returns:
            bool: True if the update was successful, False otherwise.

        Examples:
            >>> conversation.update_message('Updated content', node_id='12345', col='content')
        """
        return CoreUtil.update_row(self.messages, node_id=node_id, col=col, value=value)
    
    def change_first_system_message(
        self, system: Union[str, Dict[str, Any], System], sender: Optional[str] = None
    ):
        """
        Updates the first system message in the branch's conversation.

        Args:
            system (Union[str, Dict[str, Any], System]): The new system message content.
            sender (Optional[str]): The sender of the system message. Defaults to None.

        Raises:
            ValueError: If there are no system messages in the conversation.

        Examples:
            >>> branch.change_first_system_message({'content': 'System rebooted'}, sender='system')
        """
        if self.len_systems == 0:
            raise ValueError("There is no system message in the messages.")
        
        if not isinstance(system, (str, Dict, System)):
            raise ValueError("Input cannot be converted into a system message.")
            
        elif isinstance(system, (str, Dict)):
            system = System(system, sender=sender)
            
        elif isinstance(system, System):
            message_dict = system.to_dict()
            if sender:
                message_dict['sender'] = sender
            message_dict['timestamp'] = datetime.now().isoformat()
            sys_index = self.messages[self.messages.role == 'system'].index
            self.messages.loc[sys_index[0]] = message_dict

    def rollback(self, steps: int) -> None:
        """
        Removes the last 'n' messages from the conversation.

        Args:
            steps (int): The number of messages to remove from the end of the conversation.

        Raises:
            ValueError: If 'steps' is not a positive integer or exceeds the number of messages.

        Examples:
            >>> conversation.rollback(2)
        """
        return CoreUtil.remove_last_n_rows(self.messages, steps)

    def clear_messages(self) -> None:
        """
        Clears all messages from the conversation, resetting it to an empty state.

        Examples:
            >>> conversation.clear_messages()
        """
        self.messages = pd.DataFrame(columns=Branch._cols)
            
    def replace_keyword(
        self,
        keyword: str, 
        replacement: str, 
        col: str = 'content',
        case_sensitive: bool = False
    ) -> None:
        """
        Replaces all occurrences of a keyword in a specified column of the conversation's messages with a given replacement.

        Args:
            keyword (str): The keyword to be replaced.
            replacement (str): The string to replace the keyword with.
            col (str, optional): The column where the replacement should occur. Defaults to 'content'.
            case_sensitive (bool, optional): If True, the replacement is case sensitive. Defaults to False.

        Examples:
            >>> conversation.replace_keyword('hello', 'hi', col='content')
        """
        CoreUtil.replace_keyword(
            self.messages, keyword, replacement, col=col, 
            case_sensitive=case_sensitive
        )
        
    def search_keywords(
        self, 
        keywords: Union[str, list],
        case_sensitive: bool = False, reset_index: bool = False, dropna: bool = False
    ) -> pd.DataFrame:
        """
        Searches for messages containing specified keywords within the conversation.

        Args:
            keywords (Union[str, list]): The keyword(s) to search for within the conversation's messages.
            case_sensitive (bool, optional): If True, the search is case sensitive. Defaults to False.
            reset_index (bool, optional): If True, resets the index of the resulting DataFrame. Defaults to False.
            dropna (bool, optional): If True, drops messages with NA values before searching. Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame containing messages that match the search criteria.

        Examples:
            >>> df_matching = conversation.search_keywords('urgent', case_sensitive=True)
        """
        return CoreUtil.search_keywords(
            self.messages, keywords, case_sensitive, reset_index, dropna
        )
        
    def extend(self, messages: pd.DataFrame, **kwargs) -> None:
        """
        Extends the conversation by appending new messages, optionally avoiding duplicates based on specified criteria.

        Args:
            messages (pd.DataFrame): A DataFrame containing new messages to append to the conversation.
            **kwargs: Additional keyword arguments for handling duplicates (passed to pandas' drop_duplicates method).

        Examples:
            >>> new_messages = pd.DataFrame([...])
            >>> conversation.extend(new_messages)
        """
        self.messages = CoreUtil.extend(self.messages, messages, **kwargs)
        
    def filter_by(
        self,
        role: Optional[str] = None, 
        sender: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        content_keywords: Optional[Union[str, list]] = None,
        case_sensitive: bool = False
    ) -> pd.DataFrame:
        """
        Filters the conversation's messages based on specified criteria such as role, sender, time range, and keywords.

        Args:
            role (Optional[str]): Filter messages by role (e.g., 'user', 'assistant', 'system').
            sender (Optional[str]): Filter messages by sender.
            start_time (Optional[datetime]): Filter messages sent after this time.
            end_time (Optional[datetime]): Filter messages sent before this time.
            content_keywords (Optional[Union[str, list]]): Filter messages containing these keywords.
            case_sensitive (bool, optional): If True, keyword search is case sensitive. Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame containing messages that match the filter criteria.

        Examples:
            >>> filtered_df = conversation.filter_by(role='user', content_keywords=['urgent', 'immediate'])
        """
        return CoreUtil.filter_messages_by(
            self.messages, role=role, sender=sender, 
            start_time=start_time, end_time=end_time, 
            content_keywords=content_keywords, case_sensitive=case_sensitive
        )

# ----- intra-branch communication methods ----- #
    def send(self, to_name, title, package):
        """
        Sends a request package to a specified recipient.

        Packages are queued in `pending_outs` for dispatch. The function doesn't immediately send the package but prepares it for delivery.

        Args:
            to_name (str): The name of the recipient branch.
            title (str): The title or category of the request (e.g., 'messages', 'tool', 'service', 'llmconfig').
            package (Any): The actual data or object to be sent, its expected type depends on the title.

        Examples:
            >>> branch.send("another_branch", "messages", message_dataframe)
            >>> branch.send("service_branch", "service", service_config)
        """
        request = Request(from_name=self.name, to_name=to_name, title=title, request=package)
        self.pending_outs.append(request)

    def receive(self, from_name, messages=True, tool=True, service=True, llmconfig=True):
        """
        Processes and integrates received request packages based on their titles.

        Handles incoming requests by updating the branch's state with the received data. It can selectively process requests based on the type specified by the `title` of the request.

        Args:
            from_name (str): The name of the sender whose packages are to be processed.
            messages (bool): If True, processes 'messages' requests. Defaults to True.
            tool (bool): If True, processes 'tool' requests. Defaults to True.
            service (bool): If True, processes 'service' requests. Defaults to True.
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

            if request.title == 'messages' and messages:
                if not isinstance(request.request, pd.DataFrame):
                    raise ValueError('Invalid messages format')
                CoreUtil.validate_messages(request.request)
                self.messages = self.messages.merge(request.request, how='outer')
                continue

            elif request.title == 'tool' and tool:
                if not isinstance(request.request, Tool):
                    raise ValueError('Invalid tool format')
                self.tool_manager.register_tools([request.request])

            elif request.title == 'service' and service:
                if not isinstance(request.request, BaseService):
                    raise ValueError('Invalid service format')
                self.service = request.request

            elif request.title == 'llmconfig' and llmconfig:
                if not isinstance(request.request, dict):
                    raise ValueError('Invalid llmconfig format')
                self.llmconfig.update(request.request)

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
    
    def _add_service(self, service, llmconfig):
        service = service or OpenAIService()
        self.service=service
        if llmconfig:
            self.llmconfig = llmconfig
        else:
            if isinstance(service, OpenAIService):
                self.llmconfig = oai_schema["chat/completions"]["config"]
            elif isinstance(service, OpenRouterService):
                self.llmconfig = openrouter_schema["chat/completions"]["config"]
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
                    content_ = json.dumps(as_dict(content_))
                except Exception as e:
                    raise ValueError(f"Error in serealizing, {row['node_id']} {content_}: {e}")
                
            out = {"role": row['role'], "content": content_}
            if with_sender:
                out['content'] = f"Sender {row['sender']}: {content_}"
            
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

    def _create_message(
        self,
        system: Optional[Union[dict, list, System]] = None,
        instruction: Optional[Union[dict, list, Instruction]] = None,
        context: Optional[Union[str, Dict[str, Any]]] = None,
        response: Optional[Union[dict, list, Response]] = None,
        sender: Optional[str] = None
    ) -> Message:
        """
        Creates a message object based on the given parameters, ensuring only one message type is specified.

        Args:
            system (Optional[Union[dict, list, System]]): System message to be added.
            instruction (Optional[Union[dict, list, Instruction]]): Instruction message to be added.
            context (Optional[Union[str, Dict[str, Any]]]): Context for the instruction message.
            response (Optional[Union[dict, list, Response]]): Response message to be added.
            sender (Optional[str]): The sender of the message.

        Returns:
            Message: A Message object created from the provided parameters.

        Raises:
            ValueError: If more than one message type is specified or if the parameters do not form a valid message.
        """
        if sum(lcall([system, instruction, response], bool)) != 1:
            raise ValueError("Error: Message must have one and only one role.")
        
        else:
            if isinstance(any([system, instruction, response]), Message):
                if system:
                    return system
                elif instruction:
                    return instruction
                elif response:
                    return response

            msg = 0
            if response:
                msg = Response(response=response, sender=sender)
            elif instruction:
                msg = Instruction(instruction=instruction, 
                                  context=context, sender=sender)
            elif system:
                msg = System(system=system, sender=sender)
            return msg

    def _info(self, use_sender: bool = False) -> Dict[str, int]:
        """
        Generates a summary of the conversation's messages, either by role or sender.

        Args:
            use_sender (bool, optional): If True, generates the summary based on sender. If False, uses role. Defaults to False.

        Returns:
            Dict[str, int]: A dictionary with counts of messages, categorized either by role or sender.
        """
        messages = self.messages['sender'] if use_sender else self.messages['role']
        result = messages.value_counts().to_dict()
        result['total'] = len(self.len_messages)
        
        return result



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
    #     handling tool invocations as specified.
    #
    #     Args:
    #         instruction_set (InstructionSet): The instruction set to process.
    #         num (Union[int, List[int]]): The maximum number of follow-up chats to perform for each instruction,
    #                                       or a list of maximum numbers corresponding to each instruction.
    #         **kwargs: Additional keyword arguments to pass to the chat completion service.
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
    #             await self.chat(current_instruct_node)
    #         current_instruct_node = instruction_set.get_next_instruction(
    #             current_instruct_node
    #         )
    