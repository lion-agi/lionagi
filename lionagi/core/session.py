from collections import deque
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from lionagi.utils.sys_util import create_path
from lionagi.utils import to_list, to_df
from lionagi.schema import Tool
from lionagi.iservices.base_service import BaseService
from lionagi.core.branch import Branch
from lionagi.core.branch_manager import BranchManager
from lionagi.core.messages import Instruction, System


class Session:

    def __init__(
        self,
        system: Optional[Union[str, System]] = None,
        sender: Optional[str] = None,
        llmconfig: Optional[Dict[str, Any]] = None,
        service: Optional[BaseService] = None,
        branches: Optional[Dict[str, Branch]] = None,
        default_branch: Optional[Branch] = None,
        default_branch_name: Optional[str] = None,
        tools: Optional[List[Tool]] = None, 
        instruction_sets: Optional[List[Instruction]] = None, 
        tool_manager: Optional[Any] = None,
        messages: Optional[List[Dict[str, Any]]] = None, 
        logger: Optional[Any] = None, 
        dir: Optional[str] = None
    ):
        """Initialize a new session with optional configuration for managing conversations.

        Args:
            system (Optional[Union[str, System]]): The system message.
            sender (Optional[str]): the default sender name for default branch
            llmconfig (Optional[Dict[str, Any]]): Configuration for language learning models.
            service (Optional[BaseService]): External service instance.
            branches (Optional[Dict[str, Branch]]): Dictionary of branch instances.
            default_branch (Optional[Branch]): The default branch for the session.
            default_branch_name (Optional[str]): The name of the default branch.
            tools (Optional[List[Tool]]): List of tools available for the session.
            instruction_sets (Optional[List[Instruction]]): List of instruction sets.
            tool_manager (Optional[Any]): Manager for handling tools.
            messages (Optional[List[Dict[str, Any]]]): Initial list of messages.
            logger (Optional[Any]): Logger instance for the session.
            dir (Optional[str]): Directory path for saving session data.

        Examples:
            >>> session = Session(system="you are a helpful assistant", sender="researcher")
        """
        self.branches = branches if isinstance(branches, dict) else {}
        self.service = service 
        self.setup_default_branch(
            system=system, sender=sender, default_branch=default_branch,
            default_branch_name=default_branch_name, messages=messages,
            instruction_sets=instruction_sets, tool_manager=tool_manager, 
            service=service, llmconfig=llmconfig, tools=tools, 
            dir=dir, logger=logger)
        self.branch_manager = BranchManager(self.branches)
        self.logger = self.default_branch.logger
  

# --- default branch methods ---- #

    @property
    def messages(self):
        return self.default_branch.messages

    @property
    def messages_describe(self) -> Dict[str, Any]:
        """
        Provides a descriptive summary of all messages in the branch.

        Returns:
            Dict[str, Any]: A dictionary containing summaries of messages by role and sender, total message count,
            instruction sets, registered tools, and message details.

        Examples:
            >>> session.messages_describe
            {'total_messages': 100, 'by_sender': {'User123': 60, 'Bot': 40}}
        """
        return self.default_branch.messages_describe

    @property
    def has_tools(self) -> bool:
        """
        Checks if there are any tools registered in the tool manager.

        Returns:
            bool: True if there are tools registered, False otherwise.

        Examples:
            >>> session.has_tools
            True
        """
        return self.default_branch.has_tools

    @property
    def last_message(self) -> pd.Series:
        """
        Retrieves the last message from the conversation.

        Returns:
            pd.Series: The last message as a pandas Series.
        """
        return self.default_branch.last_message
    
    @property
    def first_system(self) -> pd.Series:
        """
        Retrieves the first system message from the conversation.

        Returns:
            pd.Series: The first system message as a pandas Series.
        """
        return self.default_branch.first_system
        
    @property
    def last_response(self) -> pd.Series:
        """
        Retrieves the last response message from the conversation.

        Returns:
            pd.Series: The last response message as a pandas Series.
        """
        return self.default_branch.last_response

    @property
    def last_response_content(self) -> Dict:
        """
        Retrieves the content of the last response message from the conversation.

        Returns:
            Dict: The content of the last response message as a dictionary
        """
        return self.default_branch.last_response_content

    @property
    def action_request(self) -> pd.DataFrame:
        """
        Retrieves all action request messages from the conversation.

        Returns:
            pd.DataFrame: A DataFrame containing all action request messages.
        """
        return self.default_branch.action_request
    
    @property
    def action_response(self) -> pd.DataFrame:
        """
        Retrieves all action response messages from the conversation.

        Returns:
            pd.DataFrame: A DataFrame containing all action response messages.
        """
        return self.default_branch.action_response

    @property
    def responses(self) -> pd.DataFrame:
        """
        Retrieves all response messages from the conversation.

        Returns:
            pd.DataFrame: A DataFrame containing all response messages.
        """
        return self.default_branch.responses

    @property
    def assistant_responses(self) -> pd.DataFrame:
        """
        Retrieves all assistant responses from the conversation, excluding action requests and responses.

        Returns:
            pd.DataFrame: A DataFrame containing assistant responses excluding action requests and responses.
        """
        return self.default_branch.assistant_responses

    @property
    def info(self) -> Dict[str, int]:
        """
        Get a summary of the conversation messages categorized by role.

        Returns:
            Dict[str, int]: A dictionary with keys as message roles and values as counts.
        """
        
        return self.default_branch.info
    
    @property
    def sender_info(self) -> Dict[str, int]:
        """
        Provides a descriptive summary of the conversation, including total message count and summary by sender.

        Returns:
            Dict[str, Any]: A dictionary containing the total number of messages and a summary categorized by sender.
        """
        return self.default_branch.sender_info

    @classmethod
    def from_csv(
        cls,
        filepath,
        system: Optional[Union[str, System]] = None,
        sender: Optional[str] = None,
        llmconfig: Optional[Dict[str, Any]] = None,
        service: BaseService = None,
        branches: Optional[Dict[str, Branch]] = None,
        default_branch: Optional[Branch] = None,
        default_branch_name: str = 'main',
        tools = None, 
        instruction_sets=None, tool_manager=None,
        **kwargs) -> 'Session':
        """
        Creates a Session instance from a CSV file containing messages.

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
            system=system,
            sender=sender,
            llmconfig=llmconfig,
            service=service,
            branches=branches,
            default_branch=default_branch,
            default_branch_name=default_branch_name,
            tools = tools, 
            instruction_sets=instruction_sets, 
            tool_manager=tool_manager,
            messages=df, **kwargs
        )
        
        return self

    @classmethod
    def from_json(
        cls,
        filepath,
        system: Optional[Union[str, System]] = None,
        sender: Optional[str] = None,
        llmconfig: Optional[Dict[str, Any]] = None,
        service: BaseService = None,
        branches: Optional[Dict[str, Branch]] = None,
        default_branch: Optional[Branch] = None,
        default_branch_name: str = 'main',
        tools = None, 
        instruction_sets=None, tool_manager=None,
        **kwargs) -> 'Session':
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
            system=system,
            sender=sender,
            llmconfig=llmconfig,
            service=service,
            branches=branches,
            default_branch=default_branch,
            default_branch_name=default_branch_name,
            tools = tools, 
            instruction_sets=instruction_sets, 
            tool_manager=tool_manager,
            messages=df, **kwargs
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

    @property
    def all_messages(self) -> pd.DataFrame:
        """
        return all messages across branches
        """
        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.messages))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    def register_tools(self, tools):
        self.default_branch.register_tools(tools)

# ----- chatflow ----#
    async def call_chatcompletion(self, branch=None, sender=None, with_sender=False, tokenizer_kwargs={}, **kwargs):
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
        branch = self.get_branch(branch)
        await branch.call_chatcompletion(
            sender=sender, with_sender=with_sender, 
            tokenizer_kwargs=tokenizer_kwargs, **kwargs
        )
    
    async def chat(
        self,
        instruction: Union[Instruction, str],
        branch=None,
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
        branch = self.get_branch(branch)
        return await branch.chat(
            instruction=instruction, context=context, 
            sender=sender, system=system, tools=tools, 
            out=out, invoke=invoke, **kwargs
        )

    async def ReAct(
        self,
        instruction: Union[Instruction, str],
        branch=None,
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
        branch = self.get_branch(branch)

        return await branch.ReAct(
            instruction=instruction, context=context, 
            sender=sender, system=system, tools=tools, 
            num_rounds=num_rounds, **kwargs
        )

    async def auto_followup(
        self,
        instruction: Union[Instruction, str],
        branch=None,
        context = None,
        sender = None,
        system = None,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        max_followup: int = 3,
        out=True, 
        **kwargs):
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
        branch = self.get_branch(branch)
        return await branch.auto_followup(
            instruction=instruction, context=context, 
            sender=sender, system=system, tools=tools, 
            max_followup=max_followup, out=out, **kwargs
        )

# ---- branch manipulation ---- #        
    def new_branch(
        self, 
        branch_name: Optional[str] = None,
        system=None,
        sender=None,
        messages: Optional[pd.DataFrame] = None,
        instruction_sets = None,
        tool_manager = None,
        service = None,
        llmconfig = None,
        tools=None,
    ) -> None:     
        """Create a new branch with the specified configurations.

        Args:
            branch_name (Optional[str]): Name of the new branch.
            system (Optional[Union[System, str]]): System or context identifier for the new branch.
            sender (Optional[str]): Default sender identifier for the new branch.
            messages (Optional[pd.DataFrame]): Initial set of messages for the new branch.
            instruction_sets (Optional[Any]): Instruction sets for the new branch.
            tool_manager (Optional[Any]): Tool manager for handling tools in the new branch.
            service (Optional[BaseService]): External service instance for the new branch.
            llmconfig (Optional[Dict[str, Any]]): Configuration for language learning models in the new branch.
            tools (Optional[List[Tool]]): List of tools available for the new branch.

        Raises:
            ValueError: If the branch name already exists.

        Examples:
            >>> session.new_branch("new_branch_name")
        """
        if branch_name in self.branches.keys():
            raise ValueError(f'Invalid new branch name {branch_name}. Branch already existed.')
        new_branch = Branch(
            name=branch_name,
            messages=messages,
            instruction_sets=instruction_sets, 
            tool_manager=tool_manager, 
            service=service, 
            llmconfig=llmconfig, 
            tools=tools
        )
        if system:
            new_branch.add_message(system=system, sender=sender)

        self.branches[branch_name] = new_branch
        self.branch_manager.sources[branch_name] = new_branch
        self.branch_manager.requests[branch_name] = {}

    def get_branch(
        self, 
        branch: Optional[Union[Branch, str]] = None, 
        get_name: bool = False
    ) -> Union[Branch, Tuple[Branch, str]]:
        """
        Retrieve a branch by name or instance.

        Args:
            branch (Optional[Union[Branch, str]]): The branch name or instance to retrieve.
            get_name (bool): If True, returns a tuple of the branch instance and its name.

        Returns:
            Union[Branch, Tuple[Branch, str]]: The branch instance or a tuple of the branch instance and its name.

        Raises:
            ValueError: If the branch name does not exist or the branch input is invalid.

        Examples:
            >>> branch_instance = session.get_branch("existing_branch_name")
            >>> branch_instance, branch_name = session.get_branch("existing_branch_name", get_name=True)
        """
        if isinstance(branch, str):
            if branch not in self.branches.keys():
                raise ValueError(f'Invalid branch name {branch}. Not exist.')
            else:
                if get_name: 
                    return self.branches[branch], branch
                return self.branches[branch]
        
        elif isinstance(branch, Branch) and branch in self.branches.values():
            if get_name:
                return branch, [key for key, value in self.branches.items() if value == branch][0]
            return branch

        elif branch is None:
            if get_name:
                return self.default_branch, self.default_branch_name
            return self.default_branch
        
        else:
            raise ValueError(f'Invalid branch input {branch}.')

    def change_default_branch(self, branch: Union[str, Branch]) -> None:
        """Change the default branch of the session.

        Args:
            branch (Union[str, Branch]): The branch name or instance to set as the new default.

        Examples:
            >>> session.change_default_branch("new_default_branch")
        """
        branch_, name_ = self.get_branch(branch, get_name=True)
        self.default_branch = branch_
        self.default_branch_name = name_

    def delete_branch(self, branch: Union[Branch, str], verbose: bool = True) -> bool:
        """Delete a branch from the session.

        Args:
            branch (Union[Branch, str]): The branch name or instance to delete.
            verbose (bool): If True, prints a message upon deletion.

        Returns:
            bool: True if the branch was successfully deleted.

        Raises:
            ValueError: If attempting to delete the current default branch.

        Examples:
            >>> session.delete_branch("branch_to_delete")
        """
        _, branch_name = self.get_branch(branch, get_name=True)

        if branch_name == self.default_branch_name:
            raise ValueError(
                f'{branch_name} is the current default branch, please switch to another branch before delete it.'
            )
        else:
            self.branches.pop(branch_name)
            # self.branch_manager.sources.pop(branch_name)
            self.branch_manager.requests.pop(branch_name)
            if verbose:
                print(f'Branch {branch_name} is deleted.')
            return True

    def merge_branch(
        self, 
        from_: Union[str, Branch], 
        to_branch: Union[str, Branch], 
        update: bool = True, 
        del_: bool = False
    ) -> None:
        """Merge messages and settings from one branch to another.

        Args:
            from_ (Union[str, Branch]): The source branch name or instance.
            to_ (Union[str, Branch]): The target branch name or instance where the merge will happen.
            update (bool): If True, updates the target branch with the source branch's settings.
            del_ (bool): If True, deletes the source branch after merging.

        Examples:
            >>> session.merge_branch("source_branch", "target_branch", del_=True)
        """
        from_ = self.get_branch(branch=from_)
        to_branch, to_name = self.get_branch(branch=to_branch, get_name=True)
        to_branch.merge_branch(from_, update=update)
        
        if del_:
            if from_ == self.default_branch:
                self.default_branch_name = to_name
                self.default_branch = to_branch
            self.delete_branch(from_, verbose=False)

    def collect(self, from_: Union[str, Branch, List[str], List[Branch]] = None):
        """
        Collects requests from specified branches or from all branches if none are specified.

        This method is intended to aggregate data or requests from one or more branches for processing or analysis.

        Args:
            from_ (Optional[Union[str, Branch, List[Union[str, Branch]]]]): The branch(es) from which to collect requests.
                Can be a single branch name, a single branch instance, a list of branch names, a list of branch instances, or None.
                If None, requests are collected from all branches.

        Examples:
            >>> session.collect("branch_name")
            >>> session.collect([branch_instance_1, "branch_name_2"])
            >>> session.collect()  # Collects from all branches
        """
        if from_ is None:
            for branch in self.branches.keys():
                self.branch_manager.collect(branch)
        else:
            if not isinstance(from_, list):
                from_ = [from_]
            for branch in from_:
                if isinstance(branch, Branch):
                    branch = branch.name
                if isinstance(branch, str):
                    self.branch_manager.collect(branch)

    def send(self, to_: Union[str, Branch, List[str], List[Branch]] = None):
        """
        Sends requests or data to specified branches or to all branches if none are specified.

        This method facilitates the distribution of data or requests to one or more branches, potentially for further action or processing.

        Args:
            to_ (Optional[Union[str, Branch, List[Union[str, Branch]]]]): The target branch(es) to which to send requests.
                Can be a single branch name, a single branch instance, a list of branch names, a list of branch instances, or None.
                If None, requests are sent to all branches.

        Examples:
            >>> session.send("target_branch")
            >>> session.send([branch_instance_1, "target_branch_2"])
            >>> session.send()  # Sends to all branches
        """
        if to_ is None:
            for branch in self.branches.keys():
                self.branch_manager.send(branch)
        else:
            if not isinstance(to_, list):
                to_ = [to_]
            for branch in to_:
                if isinstance(branch, Branch):
                    branch = branch.name
                if isinstance(branch, str):
                    self.branch_manager.send(branch)

    def collect_send_all(self, receive_all=False):
        """
        Collects and sends requests across all branches, optionally invoking a receive operation on each branch.

        This method is a convenience function for performing a full cycle of collect and send operations across all branches, 
        useful in scenarios where data or requests need to be aggregated and then distributed uniformly.

        Args:
            receive_all (bool): If True, triggers a `receive_all` method on each branch after sending requests, 
                which can be used to process or acknowledge the received data.

        Examples:
            >>> session.collect_send_all()
            >>> session.collect_send_all(receive_all=True)
        """
        self.collect()
        self.send()
        if receive_all:
            for branch in self.branches.values():
                branch.receive_all()

    def setup_default_branch(self, **kwargs):
        self._setup_default_branch(**kwargs)
        self._verify_default_branch()

    def _verify_default_branch(self):
        if self.branches:
            if self.default_branch_name not in self.branches.keys():
                raise ValueError('default branch name is not in imported branches')
            if self.default_branch is not self.branches[self.default_branch_name]:
                raise ValueError(f'default branch does not match Branch object under {self.default_branch_name}')
            
        if not self.branches:
            self.branches[self.default_branch_name] = self.default_branch

    def _setup_default_branch(
        self, system, sender, default_branch, default_branch_name, messages, 
        instruction_sets, tool_manager, service, llmconfig, tools, dir, logger
    ):
        
        branch = default_branch or Branch(
            name=default_branch_name, service=service, llmconfig=llmconfig, tools=tools,
            tool_manager=tool_manager, instruction_sets=instruction_sets, messages=messages, dir=dir, logger=logger
        )
        
        self.default_branch = branch
        self.default_branch_name = default_branch_name or 'main'
        if system:
            self.default_branch.add_message(system=system, sender=sender)

        self.llmconfig = self.default_branch.llmconfig
        
    # def add_instruction_set(self, name: str, instruction_set: InstructionSet) -> None:
    #     """
    #     Adds an instruction set to the current active branch.
    #
    #     Args:
    #         name (str): The name of the instruction set.
    #         instruction_set (InstructionSet): The instruction set to add.
    #     """
    #     self.default_branch.add_instruction_set(name, instruction_set)
    #
    # def remove_instruction_set(self, name: str) -> bool:
    #     """
    #     Removes an instruction set from the current active branch.
    #
    #     Args:
    #         name (str): The name of the instruction set to remove.
    #
    #     Returns:
    #         bool: True if the instruction set is removed, False otherwise.
    #     """
    #     return self.default_branch.remove_instruction_set(name)
    