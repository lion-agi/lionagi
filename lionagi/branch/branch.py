import json
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pandas import DataFrame

from lionagi.util import to_dict, lcall
from lionagi.util import to_df

from working.base_service import BaseService, StatusTracker
from lionagi.provider.api.oai import OpenAIService
from lionagi.config.oai_configs import oai_schema
from lionagi.schema import DataLogger, BaseTool
from lionagi.action.base.action_manager import ActionManager
from lionagi.mail.base.base_mail import B
from working.instruction_set import InstructionSet
from lionagi.message.messages import Instruction, BaseMessage, Response, System, \
    MessageField
from lionagi.flow.flow import ChatFlow
from .util import MessageUtil
from .base import Conversation

try:
    OAIService = OpenAIService()
except:
    pass


# noinspection PyUnresolvedReferences
class Branch(Conversation):

    def __init__(self, /, name: Optional[str] = None,
                 messages: Optional[DataFrame] = None,
                 instruction_sets: Optional[Dict[str, InstructionSet]] = None,
                 action_manager: Optional[ActionManager] = None,
                 service: Optional[BaseService] = None, llmconfig: Optional[Dict] = None,
                 tools: Optional[Any] = None,
                 persist_path: Optional[Union[str, Path]] = None,
                 logger: Optional[DataLogger] = None, **data: Any) -> None:
        """
        Initializes a new instance of the Branch class, an extension of the Conversation class
        with added functionality for handling instruction sets, action managers, and service
        integrations.

        This constructor sets up a branch with custom configurations for message handling,
        tool management, and interaction with external services or APIs.

        Args:
            name: Optional; The name of the branch for identification.
            messages: Optional; A DataFrame containing messages for the branch, structured
                      according to the Conversation schema.
            instruction_sets: Optional; A dictionary mapping instruction set identifiers to
                              InstructionSet objects, for processing specific types of messages.
            action_manager: Optional; An ActionManager instance for managing actions within
                            the branch, such as sending emails or processing commands.
            service: Optional; A BaseService instance representing an external service provider,
                     used for tasks such as chat completions or data retrieval.
            llmconfig: Optional; A dictionary with configuration settings for a language learning
                       model (LLM), defining how the branch interacts with AI services.
            tools: Optional; An initial list or single instance of tools to be registered with
                   the branch's tool manager, enhancing its capabilities.
            persist_path: Optional; A directory path where conversation data and logs should be
                          persisted.
            logger: Optional; A DataLogger instance for logging branch activities and interactions.
            **data: Arbitrary keyword arguments that can be passed to the superclass
                   initializer for further customization.

        Examples:
            >>> branch = Branch(name="CustomerService")
            >>> branch_with_messages = Branch(name="Support", messages=pd.DataFrame(columns=["node_id", "content"]))
        """

        super().__init__(**data)
        self.action_manager = action_manager if action_manager else ActionManager()
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
        self.logger = logger or DataLogger(persist_path=persist_path)

    @property
    def messages_describe(self) -> Dict[str, Any]:
        """
        Provides a descriptive summary of all messages in the branch, including counts by role
        and sender, details on instruction sets, and registered tools.

        Returns:
            A dictionary containing key insights and summaries of the branch's messages,
            tools, and configurations, useful for analysis and debugging.

            The dictionary includes:
            - total_messages: The total number of messages in the branch.
            - summary_by_role: A summary of messages categorized by their role.
            - summary_by_sender: A summary of messages categorized by sender.
            - instruction_sets: A list of configured instruction sets.
            - registered_tools: A list of tools registered with the branch's action manager.
            - messages: A list of message dictionaries, providing details for each message.
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
        Checks if there are any tools registered in the tool manager of the branch.

        Returns:
            True if at least one tool is registered within the branch's tool manager,
            False otherwise.
        """

        return self.action_manager.registry != {}

    # ---- I/O ---- #
    @classmethod
    def from_csv(cls, filepath: str, name: Optional[str] = None,
                 instruction_sets: Optional[Dict[str, InstructionSet]] = None,
                 tool_manager: Optional[ActionManager] = None,
                 service: Optional[BaseService] = None,
                 llmconfig: Optional[Dict] = None, tools=None, **kwargs) -> 'Branch':
        """
        Creates a Branch instance from a CSV file containing messages, enabling easy import
        and setup of conversation data from external sources.

        Args:
            filepath: Path to the CSV file containing structured conversation messages.
            name: Optional; Name of the branch, providing a label for identification.
            instruction_sets: Optional; A mapping of identifiers to InstructionSet objects for
                              handling specific message types or instructions.
            tool_manager: Optional; An instance of ActionManager for managing actions and tools
                          within the branch.
            service: Optional; An instance of BaseService to be used as the external service
                     provider for the branch, such as for AI interactions.
            llmconfig: Optional; Configuration settings for a language learning model, tailored
                       to the branch's requirements.
            tools: Optional; A list of tools to be immediately registered with the branch upon
                   creation, enhancing its functionality.
            **kwargs: Additional keyword arguments passed directly to pandas.read_csv() for
                      custom CSV parsing options.

        Returns:
            A new instance of Branch initialized with data from the specified CSV file, along
            with any additional configurations provided through the arguments.

        Examples:
            >>> branch = Branch.from_csv("path/to/messages.csv", name="ImportedBranch")
        """

        df = pd.read_csv(filepath, **kwargs)
        self = cls(
            name=name,
            messages=df,
            instruction_sets=instruction_sets,
            action_manager=action_manager,
            service=service,
            llmconfig=llmconfig,
            tools=tools
        )

        return self

    @classmethod
    def from_json(cls, filepath: str, name: Optional[str] = None,
                  instruction_sets: Optional[Dict[str, InstructionSet]] = None,
                  action_manager: Optional[ActionManager] = None,
                  service: Optional[BaseService] = None,
                  llmconfig: Optional[Dict] = None, **kwargs) -> 'Branch':
        """
        Creates a Branch instance from a JSON file, facilitating the import of conversation
        data and branch configuration from a JSON format.

        Args:
            filepath: The file path to the JSON file with structured conversation messages.
            name: Optional; The branch's name for easy identification.
            instruction_sets: Optional; A dictionary of instruction sets for specific message
                              processing within the branch.
            action_manager: Optional; An ActionManager instance for managing tools and actions.
            service: Optional; A BaseService instance for external services integration, like AI.
            llmconfig: Optional; A dictionary with LLM configurations specific to the branch's use.
            **kwargs: Additional arguments passed directly to pandas.read_json() for custom
                      JSON parsing.

        Returns:
            A Branch instance populated with messages and configurations derived from the JSON
            file, ready for use in conversation handling and processing.

        Examples:
            >>> branch = Branch.from_json("path/to/messages.json", name="JSONBranch")
        """

        df = pd.read_json(filepath, **kwargs)
        self = cls(
            name=name,
            messages=df,
            instruction_sets=instruction_sets,
            action_manager=action_manager,
            service=service,
            llmconfig=llmconfig
        )
        return self

    # ----- chatflow ----#
    # noinspection PyUnresolvedReferences,PyTypeChecker
    async def call_chatcompletion(self, sender: Optional[str] = None,
                                  with_sender: bool = False,
                                  tokenizer_kwargs: Optional[Dict] = None,
                                  **kwargs) -> None:
        """
        Asynchronously calls the chat completion service with the current conversation context.

        Prepares the conversation's messages for chat completion and asynchronously sends the
        request to the configured chat completion provider. This method is particularly useful
        for integrating AI-based response generation or analysis.

        Args:
            sender: Optional; The identifier of the sender for whom chat completion is requested.
            with_sender: If True, includes the sender's identifier in each chat message sent to
                         the chat completion service.
            tokenizer_kwargs: Optional; Additional keyword arguments for the tokenizer used in
                              chat completion. This allows for custom configurations.
            **kwargs: Arbitrary keyword arguments passed directly to the chat completion provider,
                      allowing for extensive customization of the request.

        Examples:
            >>> await branch.call_chatcompletion(sender="user123", with_sender=True)
        """

        if tokenizer_kwargs is None:
            tokenizer_kwargs = {}
        await ChatFlow.call_chatcompletion(
            self, sender=sender, with_sender=with_sender,
            tokenizer_kwargs=tokenizer_kwargs, **kwargs
        )

    # noinspection PyUnresolvedReferences
    async def chat(self, instruction: Union[Instruction, str],
                   context: Optional[Any] = None,
                   sender: Optional[str] = None,
                   system: Optional[Union[System, str, Dict[str, Any]]] = None,
                   tools: Union[bool, BaseTool, List[BaseTool], str, List[str]] = False,
                   out: bool = True, invoke: bool = True, **kwargs) -> Any:
        """
        Initiates an asynchronous chat interaction, processing instructions and optionally invoking tools.

        This method facilitates asynchronous conversation flow, including the processing of
        instructions, system messages, and the optional invocation of registered tools to enhance
        interaction capabilities.

        Args:
            instruction: The instruction for the chat, as either a string or Instruction object.
            context: Optional; Additional context provided for the chat interaction.
            sender: Optional; The identifier of the sender initiating the chat.
            system: Optional; A system message or configuration to be processed.
            tools: Specifies the tools to be invoked during the chat. Can be a boolean, a single
                   tool, a list of tools, or tool identifiers.
            out: If True, includes the output of the chat interaction in the response.
            invoke: If True, allows the invocation of tools as part of the chat interaction.
            **kwargs: Arbitrary keyword arguments for further customization of the chat interaction.

        Returns:
            The result of the chat interaction, which could vary based on the configuration and
            the tools invoked during the process.

        Examples:
            >>> await branch.chat("Query about order status", sender="customer")
        """

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
        """
        Performs an asynchronous reason-action cycle with optional tool invocation over multiple rounds.

        This method processes an instruction through a specified number of reason-action cycles,
        potentially invoking tools and processing system messages to simulate a dynamic conversation
        or decision-making process.

        Args:
            instruction: The initial instruction for the cycle, either as a string or an Instruction object.
            context: Optional; Additional context relevant to the instruction.
            sender: Optional; The identifier for the message sender.
            system: Optional; Initial system message or configuration for the cycle.
            tools: Specifies the tools to be considered for invocation during the cycle.
            num_rounds: The number of reason-action cycles to perform. Defaults to 1.
            **kwargs: Additional keyword arguments for customization of the cycle.

        Examples:
            >>> await branch.ReAct("Check system status", num_rounds=2)
        """

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
        """
        Automatically performs follow-up actions based on chat interactions and tool invocations.

        Args:
            instruction (Union[Instruction, str]): The initial instruction for follow-up.
            context: Context relevant to the instruction.
            sender (Optional[str]): Identifier for the message sender.
            system: Initial system message or configuration.
            tools: Specifies tools to be considered for follow-up actions.
            max_followup (int): Maximum number of follow-up chats allowed.
            out (bool): If True, outputs the result of the follow-up action.
            **kwargs: Additional keyword arguments for follow-up customization.

        """
        return await ChatFlow.auto_followup(
            self, instruction=instruction, context=context,
            sender=sender, system=system, tools=tools,
            max_followup=max_followup, out=out, **kwargs
        )

    # ---- branch operations ---- #
    def clone(self) -> 'Branch':
        """
        Creates a deep copy of the current Branch instance, including its state, messages, and configurations.

        This method is useful for creating independent copies of the Branch for testing, branching
        off conversations, or preserving states before making significant changes.

        Returns:
            A new Branch instance that is a deep copy of the current branch, including all messages,
            instruction sets, tools, and configurations.

        Examples:
            >>> cloned_branch = current_branch.clone()
            >>> assert not cloned_branch is current_branch  # Ensures the clone is a separate instance
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

    def merge_branch(self, branch: 'Branch', update: bool = True) -> None:
        """
        Merges another Branch instance into the current one, combining their messages, instruction sets,
        and tools.

        This method allows for the consolidation of conversation data and configurations from another
        branch, optionally updating existing entries with those from the merged branch.

        Args:
            branch: The Branch instance to be merged into the current branch.
            update: If True, updates existing instruction sets and tools with those from the merged branch.
                    If False, only adds non-existing entries, preserving original data.

        Examples:
            >>> main_branch.merge_branch(secondary_branch, update=True)
            >>> main_branch.merge_branch(temporary_branch, update=False)
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

    # ----- tool manager methods ----- #
    def register_tools(self, tools: Union[BaseTool, List[BaseTool]]) -> None:
        """
        Registers a new tool or a list of tools with the branch, enhancing its functionality.

        This method adds tools to the branch's tool manager, allowing for the integration of
        additional capabilities such as external service interactions, data processing, or
        user interaction enhancements.

        Args:
            tools: A single tool instance or a list of tool instances to be registered.

        Examples:
            >>> branch.register_tools(email_tool)
            >>> branch.register_tools([logging_tool, analytics_tool])
        """

        if not isinstance(tools, list):
            tools = [tools]
        self.action_manager.register_tools(tools=tools)

    def delete_tool(self, tools: Union[
        bool, BaseTool, List[BaseTool], str, List[str], List[Dict[str, Any]]],
                    verbose: bool = True) -> bool:
        """
        Deletes specified tools from the branch's tool manager.

        Allows for the removal of tools by instance, identifier, or a list thereof. This method can
        help manage the active toolset of the branch, particularly useful for dynamic tool management.

        Args:
            tools: The tool or tools to be deleted, specified as tool instances, identifiers, or a list.
            verbose: If True, prints a message indicating the success of the tool deletion process.

        Returns:
            True if the tool(s) were successfully deleted, False otherwise.

        Examples:
            >>> branch.delete_tool("analytics_tool")
            >>> branch.delete_tool([logging_tool, email_tool], verbose=False)
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

    # ----- intra-branch communication methods ----- #
    def send(self, to_name: str, title: str, package: Any) -> None:
        """
        Prepares a package for sending to a specified recipient within the system.

        This method queues a request package with a designated title and payload, intended for
        another branch or service. It's part of the branch's intercommunication mechanism.

        Args:
            to_name: The name of the recipient branch or service.
            title: A brief description or title of the package being sent.
            package: The data or payload to be sent, encapsulated within the package.

        Examples:
            >>> branch.send("FinanceService", "UpdateRequest", {"userId": 123, "updateData": {...}})
        """

        request = B(sender=self.name, recipient=to_name, category=title, request=package)
        self.pending_outs.append(request)

    def receive(self, sender: str, messages: bool = True, tool: bool = True,
                service: bool = True, llmconfig: bool = True) -> None:
        """
        Processes received packages from a specified sender, updating the branch accordingly.

        This method allows for the integration of messages, tools, services, and configurations
        from packages sent by another branch or service, selectively based on the type of content.

        Args:
            sender: The identifier of the sender whose package is to be processed.
            messages: If True, processes packages with messages.
            tool: If True, processes packages with tool configurations.
            service: If True, processes packages with service configurations.
            llmconfig: If True, processes packages with LLM configurations.

        Raises:
            ValueError: If no package is found from the specified sender or if a package has an
                        invalid format.

        Examples:
            >>> branch.receive("DataAnalysisService")
        """

        skipped_requests = deque()
        if sender not in self.pending_ins:
            raise ValueError(f'No package from {sender}')
        while self.pending_ins[sender]:
            request = self.pending_ins[sender].popleft()

            if request.title == 'messages' and messages:
                if not isinstance(request.request, pd.DataFrame):
                    raise ValueError('Invalid messages format')
                MessageUtil.validate_messages(request.request)
                self.messages = self.messages.merge(request.request, how='outer')
                continue

            elif request.title == 'tool' and tool:
                if not isinstance(request.request, _cols):
                    raise ValueError('Invalid tool format')
                self.action_manager.register_tools([request.request])

            elif request.title == 'provider' and service:
                if not isinstance(request.request, BaseService):
                    raise ValueError('Invalid provider format')
                self.service = request.request

            elif request.title == 'llmconfig' and llmconfig:
                if not isinstance(request.request, dict):
                    raise ValueError('Invalid llmconfig format')
                self.llmconfig.update(request.request)

            else:
                skipped_requests.append(request)

        self.pending_ins[sender] = skipped_requests

    def receive_all(self) -> None:
        """
        Processes all pending received packages from all senders, integrating their content into the branch.

        Utilizes the `receive` method to systematically process each queued package, ensuring that
        all incoming data and configurations are applied to the branch.

        Examples:
            >>> branch.receive_all()
        """

        for key in list(self.pending_ins.keys()):
            self.receive(key)

    def _add_service(self, service, llmconfig):
        service = service or OpenAIService()
        self.service = service
        if llmconfig:
            self.llmconfig = llmconfig
        else:
            if isinstance(service, OpenAIService):
                self.llmconfig = oai_schema["chat/completions"]["config"]
            # elif isinstance(provider, OpenRouterService):
            #     self.llmconfig = openrouter_schema["chat/completions"]["config"]
            else:
                self.llmconfig = {}

    def _is_invoked(self) -> bool:
        """
        Check if the conversation has been invoked with an action response.

        Returns:
            bool: True if the conversation has been invoked, False otherwise.

        """
        content = self.messages.iloc[-1]['content']
        try:
            if (to_dict(content)['action_response'].keys() >=
                    {'function', 'arguments', 'output'}):
                return True
        except ValueError:
            return False
