from collections import deque
from typing import Any, Dict, List, Optional, Union, TypeVar

import pandas as pd

from lionagi.util import to_dict
from lionagi.schema import BaseTool, BaseMail
from lionagi.message import Instruction, System, Response
from lionagi.action import ActionManager
from lionagi.provider import Services, StatusTracker
from lionagi.flow import ChatFlow

from .util import MessageUtil
from .base import Conversation

# default service should change to be settable
try:
    OAIService = OpenAIService()
except:
    pass

T = TypeVar('T', bound='Branch')


# noinspection PyUnresolvedReferences
class Branch(Conversation):
    """
    Extends the Conversation class to manage specialized branches of conversation,
    introducing advanced functionalities such as action management, service integration,
    and complex conversational flows. Branches enable modular development and management
    of conversation logic, catering to distinct conversational contexts or functionalities
    within larger systems.

    Since Branch inherits from the Conversation class, it includes all methods and
    attributes of its parent. For a comprehensive list of inherited functionalities,
    please refer to the Conversation class documentation.

    Attributes:
        branch_name (Optional[str]):
            Identifies the branch for management purposes.

        sender (str):
            Default sender name for messages from this branch, defaults to "system".

        action_manager (ActionManager):
            Manages actions within the branch, enhancing dynamic interaction capabilities.

        service:
            Integrates LLM services, defaulting to OpenAI for advanced natural language
            processing and response generation.

        llmconfig (Dict):
            Configurations for LLM service, preset for OpenAI's chat configurations,
            dictating behavior parameters of the LLM.

        status_tracker (StatusTracker):
            Monitors the status of operations and interactions within the branch.

        instruction_sets (Optional[Dict]):
            Defines instruction sets for structured interactions within the branch.

        pending_ins (Dict):
            Holds incoming messages or requests pending processing.

        pending_outs (deque):
            Queues outgoing messages or actions awaiting dispatch.

    Properties:
        messages_describe:
            Summarizes the branch's messages, including breakdowns by role and sender.

        has_tools:
            Indicates the presence of registered tools in the action manager.

    Methods:
        __init__(self, branch_name=None, system=None, ..., **kwargs):
            Initializes a branch with specific configurations. Inherits initialization
            parameters from Conversation.

        merge_branch(self, branch: 'Branch', update: bool = True):
            Combines another branch into this one, merging their data and configurations.

        register_tools(self, tools: Union[BaseTool, List[BaseTool]]):
            Adds tools to the branch's action manager for additional functionalities.

        delete_tool(self, tools: Union[bool, BaseTool, List[BaseTool], str, List[str], List[Dict[str, Any]]], verbose: bool = True) -> bool:
            Removes specified tools from the action manager.

        send(self, recipient: str, category: str, package: Any):
            Prepares and queues an outgoing package for a recipient.

        receive(self, sender: str, messages: bool = True, ...):
            Processes received packages, updating the branch's state accordingly.

        receive_all(self):
            Processes all pending received packages from all senders.

    Class Methods:
        from_csv(cls, filepath, branch_name=None, ...):
            Creates a Branch instance from CSV data. See Conversation for base method details.

        from_json(cls, filepath, branch_name=None, ...):
            Creates a Branch instance from JSON data. Refer to Conversation for base method specifics.

    Example Usage:
        >>> branch = Branch(branch_name="CustomerSupport", sender="SupportBot")
        >>> branch.register_tools([FAQTool(), BookingTool()])
        >>> branch.merge_branch(other_branch)

    This class leverages the foundational capabilities of the Conversation class,
    introducing additional features tailored for managing complex conversational systems.
    """

    def __init__(self, branch_name=None, system=None, messages=None, service=None,
                 sender=None, llmconfig=None, tools=None, datalogger=None,
                 persist_path=None, instruction_sets=None, action_manager=None, **kwargs):
        """
        Initializes a Branch instance with advanced conversation management settings.

        Extends Conversation to support functionalities like action management and service
        integration, enabling modular development of conversation logic.

        Args:
            branch_name:
                Identifier for the branch, for managing multiple branches.
            system:
                Initial system message or configuration for the branch environment.
            messages:
                Preloaded conversation messages as a pandas DataFrame. Uses Conversation's
                message handling if provided.
            service:
                LLM service for natural language processing, defaults to OpenAI.
            sender:
                Default sender name for system messages, defaults to 'system'.
            llmconfig:
                Configuration for the LLM service, tailored for the integrated service.
            tools:
                List of BaseTool instances to register with the action manager.
            datalogger:
                DataLogger instance for logging activities. If None, initializes a new
                DataLogger with `persist_path`.
            persist_path:
                Path for persisting branch data and logs, used by `datalogger`.
            instruction_sets:
                Instruction sets for structured interaction within the branch.
            action_manager:
                Manages actions within the branch, handling specific commands.
            **kwargs:
                Additional args for Conversation class initialization.

        Example:
            >>> branch = Branch(branch_name="CustomerService", sender="ServiceBot",
                                system="Welcome to Customer Service")
        """

        # init base conversation class
        super().__init__(messages=messages, datalogger=datalogger,
                         persist_path=persist_path, **kwargs)

        # add branch name
        self.branch_name = branch_name
        self.sender = sender or 'system'

        # add action manager and register tools
        self.action_manager = action_manager if action_manager else ActionManager()
        if tools:
            try:
                self.register_tools(tools)
            except Exception as e:
                raise TypeError(f"Error in registering tools: {e}")

        # add service and llmconfig
        self.service, self.llmconfig = self._add_service(service, llmconfig)
        self.status_tracker = StatusTracker()

        # add instruction sets
        self.instruction_sets = instruction_sets

        # add pending ins and outs for mails
        self.pending_ins = {}
        self.pending_outs = deque()

        # add system
        system = system or 'you are a helpful assistant'
        self.add_message(system=system)

    @classmethod
    def from_csv(cls, filepath, branch_name=None, service=None, llmconfig=None,
                 tools=None, datalogger=None, persist_path=None, instruction_sets=None,
                 action_manager=None, read_kwargs=None, **kwargs):
        """
        Creates a Branch instance from CSV file data, with branch-specific configurations.

        Extends Conversation.from_csv by initializing a Branch with additional settings like
        service and tools, using data loaded from a CSV file. Ideal for quickly setting up a
        branch with predefined conversation data and custom functionalities.

        Args:
            filepath: Path to the CSV file with conversation data.
            branch_name: Unique identifier for the branch.
            service: LLM service for natural language processing, defaults to OpenAI.
            llmconfig: Configuration for the LLM service.
            tools: List of BaseTool instances to register.
            datalogger: DataLogger instance for logging activities.
            persist_path: Path for persisting data and logs.
            instruction_sets: Instruction sets for structured interactions.
            action_manager: Manages actions within the branch.
            read_kwargs: Additional kwargs for pd.read_csv().
            **kwargs: Additional arguments for branch initialization.

        Returns:
            Branch: An initialized Branch instance with data from the CSV file.

        Example:
            >>> branch = Branch.from_csv("data/conversations.csv", branch_name="Support")
        """

        self = cls._from_csv(
            filepath=filepath, read_kwargs=read_kwargs, branch_name=branch_name,
            service=service, llmconfig=llmconfig, tools=tools, datalogger=datalogger,
            persist_path=persist_path, instruction_sets=instruction_sets,
            action_manager=action_manager, **kwargs)

        return self

    @classmethod
    def from_json(cls, filepath, branch_name=None, service=None, llmconfig=None,
                  tools=None, datalogger=None, persist_path=None, instruction_sets=None,
                  action_manager=None, read_kwargs=None, **kwargs):
        """
        Creates a Branch instance from JSON file data, including branch-specific settings.

        Similar to from_csv, this method allows initializing a Branch with data from a JSON
        file, complemented by additional configurations like LLM service and custom tools.
        Useful for importing conversation data along with branch enhancements from JSON.

        Args:
            filepath: Path to the JSON file with conversation data.
            branch_name: Identifier for the branch.
            service: Specifies the LLM service, e.g., OpenAI.
            llmconfig: LLM service configuration.
            tools: Tools to register with the action manager.
            datalogger: Instance for logging branch activities.
            persist_path: Storage path for data and logs.
            instruction_sets: Sets of instructions for the branch.
            action_manager: Action manager instance for the branch.
            read_kwargs: Additional kwargs for pd.read_json().
            **kwargs: Extra arguments for branch setup.

        Returns:
            Branch: A Branch instance initialized with JSON file data.

        Example:
            >>> branch = Branch.from_json("data/conversations.json", branch_name="FAQ")
        """

        self = cls._from_json(
            filepath=filepath, read_kwargs=read_kwargs, branch_name=branch_name,
            service=service, llmconfig=llmconfig, tools=tools, datalogger=datalogger,
            persist_path=persist_path, instruction_sets=instruction_sets,
            action_manager=action_manager, **kwargs)

        return self

    @property
    def messages_describe(self) -> Dict[str, Any]:
        """
        Provides a comprehensive summary of the branch's messages and configurations.

        This property compiles various details about the branch's conversation messages,
        including total message count, a summary by role, a summary by sender, the current
        instruction sets, and the list of registered tools. It also includes the entire
        message history formatted as dictionaries.

        Returns:
            Dict[str, Any]: A dictionary containing detailed summaries and the message history.
        """
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
        """
        Indicates whether the branch has any tools registered in the action manager.

        Checks the action manager's registry to determine if any tools have been registered,
        facilitating custom actions or responses within the branch.

        Returns:
            bool: True if there are registered tools, False otherwise.
        """
        return self.action_manager.registry != {}

    # todo: also update other attributes
    def merge_branch(self, branch: 'Branch', update: bool = True) -> None:
        """
        Merges another branch into this one, combining their messages, logs, and configurations.

        This method allows for the integration of messages, datalogger logs, instruction sets,
        and action manager registries from another branch. It can either update existing entries
        or add new ones without replacing.

        Args:
            branch: The Branch instance to merge into this branch.
            update: If True, updates existing configurations. If False, only adds new ones.

        Example:
            >>> main_branch.merge_branch(secondary_branch, update=True)
        """
        message_copy = branch.messages.copy()
        self.messages = self.messages.merge(message_copy, how='outer')
        self.datalogger.extend(branch.datalogger.logs)

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

    # ----- tool manager methods ----- #
    def register_tools(self, tools: Union[BaseTool, List[BaseTool]]) -> None:
        """
        Registers one or more tools with the branch's action manager.

        Tools enhance the branch's capabilities by providing custom actions or responses.
        This method supports registering a single tool or a list of tools.

        Args:
            tools: A single tool or a list of tools to register.

        Example:
            >>> branch.register_tools([FAQTool(), BookingTool()])
        """

        if not isinstance(tools, list):
            tools = to_list(tools, flatten=True, dropna=True)
        self.action_manager.register_tools(tools=tools)

    def delete_tool(self, tools: Union[
        bool, BaseTool, List[BaseTool], str, List[str], List[Dict[str, Any]]],
                    verbose: bool = True) -> bool:
        """
        Deletes specified tools from the branch's action manager registry.

        Allows for removal of tools by name or direct tool instances. Supports deletion of
        single or multiple tools at once. Optionally, prints a success or failure message.

        Args:
            tools: A single tool name, tool instance, or a list thereof to be deleted.
            verbose: If True, prints a confirmation message upon successful deletion.

        Returns:
            bool: True if deletion was successful, False otherwise.

        Example:
            >>> branch.delete_tool("FAQTool", verbose=True)
        """

        if isinstance(tools, list):
            if is_same_dtype(tools, str):
                for tool in tools:
                    if tool in self.action_manager.registry:
                        self.action_manager.registry.pop(tool)
                if verbose:
                    print("tools successfully deleted")
                return True
            elif is_same_dtype(tools, _cols):
                for tool in tools:
                    if tool.name in self.action_manager.registry:
                        self.action_manager.registry.pop(tool.name)
                if verbose:
                    print("tools successfully deleted")
                return True
        if verbose:
            print("tools deletion failed")
        return False

    def send(self, recipient: str, category: str, package: Any) -> None:
        """
        Prepares and queues an outgoing package for a specified recipient.

        Creates a BaseMail object to encapsulate the sender, recipient, category,
        and package content, then adds it to the pending_outs queue for delivery.

        Args:
            recipient: The identifier for the recipient of the package.
            category: The category of the message, defining its purpose or type.
            package: The content or data of the package being sent.

        Example:
            >>> branch.send(recipient="User123", category="update",
                            package={"message": "Your request has been processed."})
        """

        mail_ = BaseMail(
            sender=self.sender, recipient=recipient, category=category,
            package=package)
        self.pending_outs.append(mail_)

    def receive(self, sender: str, messages: bool = True, tool: bool = True,
                service: bool = True, llmconfig: bool = True) -> None:
        """
        Processes incoming packages based on their category, updating the branch state.

        Iterates through pending incoming packages from a specified sender, handling
        each according to its category (e.g., messages, tool, provider, llmconfig).
        Unsupported or invalid package formats are skipped.

        Args:
            sender: The identifier of the sender of the packages.
            messages: If True, processes incoming message packages.
            tool: If True, processes incoming tool packages.
            service: If True, processes incoming service packages.
            llmconfig: If True, processes incoming llmconfig packages.

        Raises:
            ValueError: If no package exists from the sender or if the package format is invalid.

        Example:
            >>> branch.receive(sender="System")
        """

        skipped_requests = deque()
        if sender not in self.pending_ins:
            raise ValueError(f'No package from {sender}')
        while self.pending_ins[sender]:
            mail_ = self.pending_ins[sender].popleft()

            if mail_.category == 'messages' and messages:
                if not isinstance(mail_.package, pd.DataFrame):
                    raise ValueError('Invalid messages format')
                MessageUtil.validate_messages(mail_.package)
                self.messages = self.messages.merge(mail_.package, how='outer')
                continue

            elif mail_.category == 'tool' and tool:
                if not isinstance(mail_.package, _cols):
                    raise ValueError('Invalid tool format')
                self.action_manager.register_tools([mail_.package])

            elif mail_.category == 'provider' and service:
                if not isinstance(mail_.package, BaseService):
                    raise ValueError('Invalid provider format')
                self.service = mail_.package

            elif mail_.category == 'llmconfig' and llmconfig:
                if not isinstance(mail_.package, dict):
                    raise ValueError('Invalid llmconfig format')
                self.llmconfig.update(mail_.package)

            else:
                skipped_requests.append(mail_)

        self.pending_ins[sender] = skipped_requests

    def receive_all(self) -> None:
        """
        Processes all pending received packages from all registered senders.

        Iterates over each sender in the pending_ins dictionary and processes their
        packages using the receive method. This ensures all waiting communications
        are addressed.

        Example:
            >>> branch.receive_all()
        """

        for key in list(self.pending_ins.keys()):
            self.receive(key)

    @staticmethod
    def _add_service(service, llmconfig):
        service = service or OAIService
        if llmconfig is None:
            if isinstance(service, OpenAIService):
                from lionagi.config.oai_configs import oai_schema
                llmconfig = oai_schema["chat/completions"]["config"]
            else:
                llmconfig = {}
        return service, llmconfig

    def _is_invoked(self) -> bool:
        content = self.messages.iloc[-1]['content']
        try:
            if (to_dict(content)['action_response'].keys() >=
                    {'function', 'arguments', 'output'}):
                return True
        except ValueError:
            return False

    # noinspection PyUnresolvedReferences
    async def chat(self, instruction: Union[Instruction, str],
                   context: Optional[Any] = None,
                   sender: Optional[str] = None,
                   system: Optional[Union[System, str, Dict[str, Any]]] = None,
                   tools: Union[bool, BaseTool, List[BaseTool], str, List[str]] = False,
                   out: bool = True, invoke: bool = True, **kwargs) -> Any:

        return await ChatFlow.chat(
            self, instruction=instruction, context=context,
            sender=sender, system=system, tools=tools,
            out=out, invoke=invoke, **kwargs
        )

    async def ReAct(self, instruction: Union[Instruction, str],
                    context: Optional[Any] = None,
                    sender: Optional[str] = None,
                    system: Optional[Union[System, str, Dict[str, Any]]] = None,
                    tools: Union[bool, BaseTool, List[BaseTool], str, List[str]] = False,
                    num_rounds: int = 1, **kwargs) -> None:
        return await ChatFlow.ReAct(
            self, instruction=instruction, context=context,
            sender=sender, system=system, tools=tools,
            num_rounds=num_rounds, **kwargs
        )

    async def auto_followup(
            self,
            instruction: Union[Instruction, str],
            context=None,
            sender=None,
            system=None,
            tools: Union[
                bool, BaseTool, List[BaseTool], str, List[str], List[Dict]] = False,
            max_followup: int = 3,
            out=True,
            **kwargs
    ) -> None:
        return await ChatFlow.auto_followup(
            self, instruction=instruction, context=context,
            sender=sender, system=system, tools=tools,
            max_followup=max_followup, out=out, **kwargs
        )
