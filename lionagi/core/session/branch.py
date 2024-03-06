from collections import deque
from typing import Any, Optional, Union, TypeVar, Callable


from lionagi.libs.sys_util import PATH_TYPE
from lionagi.libs.ln_api import StatusTracker, BaseService
from lionagi.libs import ln_convert as convert
from lionagi.libs import ln_dataframe as dataframe

from lionagi.core.schema.base_node import TOOL_TYPE, Tool
from lionagi.core.schema.data_logger import DataLogger
from lionagi.core.tool.tool_manager import ToolManager, func_to_tool
from lionagi.core.flow.monoflow import MonoChat

from lionagi.core.session.base.base_branch import BaseBranch
from lionagi.core.session.base.schema import BaseMail, Instruction, System

from lionagi.core.session.base.util import MessageUtil


from dotenv import load_dotenv

load_dotenv()


T = TypeVar("T", bound=Tool)


class Branch(BaseBranch):
    """
    Represents a specific branch of conversation with enhanced functionality for chat, mail management,
    and tool integration.

    Extends `BaseBranch` to include handling for service interactions, tool management, and specialized chat flows.

    Attributes:
        branch_name (str | None): The name of the branch, optional.
        sender (str | None): Default sender identifier for outgoing messages and mails.
        service (BaseService | None): Service used for external communications and operations.
        llmconfig (dict[str, str | int | dict] | None): Configuration for language model services.
        tool_manager (ToolManager | None): Manages tools and functionalities available within the branch.
        pending_ins (Dict[str, deque]): Queues of incoming mail items, organized by sender.
        pending_outs (deque): Queue of outgoing mail items.
    """

    def __init__(
        self,
        branch_name: str | None = None,
        system: dict | list | System | None = None,
        messages: dataframe.ln_DataFrame | None = None,
        service: BaseService | None = None,
        sender: str | None = None,
        llmconfig: dict[str, str | int | dict] | None = None,
        tools: list[Callable | Tool] | None = None,
        datalogger: None | DataLogger = None,
        persist_path: PATH_TYPE | None = None,
        # instruction_sets=None,
        tool_manager: ToolManager | None = None,
        **kwargs,
    ):
        """
        Initializes a new Branch instance with optional parameters for customizing the branch's capabilities and behaviors.

        Args:
            branch_name (str | None): Name of the branch.
            system (Union[dict, list, System, None]): Initial system message or data.
            messages (Union[dataframe.ln_DataFrame, None]): Predefined set of messages to load into the branch.
            service (Union[BaseService, None]): External service for operations like chat completions.
            sender (str | None): Default identifier for the sender of outgoing messages.
            llmconfig (Union[dict[str, str | int | dict], None]): Configuration settings for language models.
            tools (Union[list[Callable | Tool], None]): List of tools or functionalities to register with the branch.
            datalogger (Union[None, DataLogger]): Logger for tracking branch activity.
            persist_path (Union[PATH_TYPE, None]): Filesystem path for persisting branch data.
            tool_manager (Union[ToolManager, None]): Tool manager for the branch.
            **kwargs: Additional keyword arguments for base initialization.
        """

        # init base class
        super().__init__(
            messages=messages,
            datalogger=datalogger,
            persist_path=persist_path,
            **kwargs,
        )

        # add branch name
        self.branch_name = branch_name
        self.sender = sender or "system"

        # add tool manager and register tools
        self.tool_manager = tool_manager if tool_manager else ToolManager()
        if tools:
            try:
                tools_ = []
                _tools = convert.to_list(tools)
                for i in _tools:
                    if isinstance(i, Tool):
                        tools_.append(i)
                    else:
                        tools_.append(func_to_tool(i))

                self.register_tools(tools_)
            except Exception as e:
                raise TypeError(f"Error in registering tools: {e}")

        # add service and llmconfig
        self.service, self.llmconfig = self._add_service(service, llmconfig)
        self.status_tracker = StatusTracker()

        # add instruction sets
        # self.instruction_sets = instruction_sets

        # add pending ins and outs for mails
        self.pending_ins = {}
        self.pending_outs = deque()

        # add system
        if system is not None:
            self.add_message(system=system)

    @classmethod
    def from_csv(
        cls,
        filepath,
        branch_name: str | None = None,
        service: BaseService | None = None,
        llmconfig: dict[str, str | int | dict] | None = None,
        tools: TOOL_TYPE | None = None,
        datalogger: None | DataLogger = None,
        persist_path: PATH_TYPE | None = None,
        # instruction_sets=None,
        tool_manager: ToolManager | None = None,
        read_kwargs=None,
        **kwargs,
    ):
        """
        Creates a branch from messages loaded from a CSV file, along with optional configurations.

        Args:
            filepath: Path to the CSV file containing messages to initialize the branch with.
            Other parameters are similar to the `__init__` method.

        Returns:
            Branch: An instance of `Branch` initialized with messages from the specified CSV file.
        """

        self = cls._from_csv(
            filepath=filepath,
            read_kwargs=read_kwargs,
            branch_name=branch_name,
            service=service,
            llmconfig=llmconfig,
            tools=tools,
            datalogger=datalogger,
            persist_path=persist_path,
            # instruction_sets=instruction_sets,
            tool_manager=tool_manager,
            **kwargs,
        )

        return self

    @classmethod
    def from_json_string(
        cls,
        filepath,
        branch_name: str | None = None,
        service: BaseService | None = None,
        llmconfig: dict[str, str | int | dict] | None = None,
        tools: TOOL_TYPE | None = None,
        datalogger: None | DataLogger = None,
        persist_path: PATH_TYPE | None = None,
        # instruction_sets=None,
        tool_manager: ToolManager | None = None,
        read_kwargs=None,
        **kwargs,
    ):
        """
        Creates a branch from messages loaded from a JSON file, incorporating additional configurations as needed.

        Args:
            filepath: Path to the JSON file containing messages to initialize the branch with.
            Other parameters are analogous to those in the `__init__` method.

        Returns:
            Branch: An instance of `Branch` initialized with messages from the specified JSON file.
        """

        self = cls._from_json(
            filepath=filepath,
            read_kwargs=read_kwargs,
            branch_name=branch_name,
            service=service,
            llmconfig=llmconfig,
            tools=tools,
            datalogger=datalogger,
            persist_path=persist_path,
            # instruction_sets=instruction_sets,
            tool_manager=tool_manager,
            **kwargs,
        )

        return self

    def messages_describe(self) -> dict[str, Any]:
        """
        Provides a descriptive summary of the messages within the branch.

        Returns:
            dict[str, Any]: A dictionary containing a summary of the messages, categorized by role and sender, along with the total message count and a list of messages.
        """
        return dict(
            total_messages=len(self.messages),
            summary_by_role=self._info(),
            summary_by_sender=self._info(use_sender=True),
            # instruction_sets=self.instruction_sets,
            registered_tools=self.tool_manager.registry,
            messages=[msg.to_dict() for _, msg in self.messages.iterrows()],
        )

    @property
    def has_tools(self) -> bool:
        """
        Indicates whether the branch has any registered tools available.

        Returns:
            bool: True if there are registered tools within the tool manager, False otherwise.
        """
        return self.tool_manager.registry != {}

    # todo: also update other attributes
    def merge_branch(self, branch: "Branch", update: bool = True) -> None:
        """
        Merges messages, logs, and tools from another branch into this branch.

        Args:
            branch: The `Branch` instance to merge into this branch.
            update (bool): If True, updates existing tools and logs with those from the merging branch. If False, only adds new items that do not exist in this branch.
        """
        message_copy = branch.messages.copy()
        self.messages = self.messages.merge(message_copy, how="outer")
        self.datalogger.extend(branch.datalogger.log)

        if update:
            # self.instruction_sets.update(branch.instruction_sets)
            self.tool_manager.registry.update(branch.tool_manager.registry)
        else:
            for key, value in branch.instruction_sets.items():
                if key not in self.instruction_sets:
                    self.instruction_sets[key] = value

            for key, value in branch.tool_manager.registry.items():
                if key not in self.tool_manager.registry:
                    self.tool_manager.registry[key] = value

    # ----- tool manager methods ----- #
    def register_tools(self, tools: Union[Tool, list[Tool]]) -> None:
        """
        Registers a list of tools or a single tool with the branch's tool manager.

        Args:
            tools: A single `Tool` object or a list of `Tool` objects to be registered.

        This method integrates provided tools into the branch's operational context, making them available for
        use in processing and responding within the branch's workflows.
        """

        if not isinstance(tools, list):
            tools = [tools]
        self.tool_manager.register_tools(tools=tools)

    def delete_tools(
        self,
        tools: Union[T, list[T], str, list[str]],
        verbose: bool = True,
    ) -> bool:
        """
        Removes specified tools from the branch's tool manager.

        Args:
            tools: A tool (or its identifier string) or a list of tools (or their identifier strings) to be deleted.
            verbose (bool): If True, prints a confirmation message upon successful deletion.

        Returns:
            bool: True if the tool(s) were successfully deleted, False otherwise.

        This method allows for the dynamic management of tools within a branch, enabling the removal of tools
        that are no longer needed or relevant to the branch's operations.
        """

        if not isinstance(tools, list):
            tools = [tools]
        if convert.is_same_dtype(tools, str):
            for act_ in tools:
                if act_ in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_)
            if verbose:
                print("tools successfully deleted")
            return True
        elif convert.is_same_dtype(tools, Tool):
            for act_ in tools:
                if act_.schema_["function"]["name"] in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_.schema_["function"]["name"])
            if verbose:
                print("tools successfully deleted")
            return True
        if verbose:
            print("tools deletion failed")
        return False

    def send(self, recipient: str, category: str, package: Any) -> None:
        """
        Creates and enqueues a mail item for sending to a specified recipient.

        Args:
            recipient (str): The identifier of the recipient.
            category (str): The category of the mail, used for routing and processing.
            package (Any): The content of the mail.

        This method facilitates the internal communication between different parts of the system, using categorized
        mails to carry data, instructions, or responses.
        """
        mail_ = BaseMail(
            sender=self.sender, recipient=recipient, category=category, package=package
        )
        self.pending_outs.append(mail_)

    def receive(
        self,
        sender: str,
        messages: bool = True,
        tools: bool = True,
        service: bool = True,
        llmconfig: bool = True,
    ) -> None:
        """
        Processes incoming mail items from a specified sender, based on category flags.

        Args:
            sender (str): The identifier of the sender whose mail is being processed.
            messages (bool): If True, processes incoming mails categorized as messages.
            tools (bool): If True, processes incoming mails categorized as tools.
            service (bool): If True, processes incoming mails categorized as service updates.
            llmconfig (bool): If True, processes incoming mails containing llmconfig updates.

        Raises:
            ValueError: If no mails are found from the specified sender.

        This method handles the unpacking and integration of content from received mails into the branch's operational
        context, based on the category of each mail item.
        """

        skipped_requests = deque()
        if sender not in self.pending_ins:
            raise ValueError(f"No package from {sender}")
        while self.pending_ins[sender]:
            mail_ = self.pending_ins[sender].popleft()

            if mail_.category == "messages" and messages:
                if not isinstance(mail_.package, dataframe.ln_DataFrame):
                    raise ValueError("Invalid messages format")
                MessageUtil.validate_messages(mail_.package)
                self.messages = self.messages.merge(mail_.package, how="outer")

            elif mail_.category == "tools" and tools:
                if not isinstance(mail_.package, Tool):
                    raise ValueError("Invalid tools format")
                self.tool_manager.register_tools([mail_.package])

            elif mail_.category == "provider" and service:
                from lionagi.libs.ln_api import BaseService

                if not isinstance(mail_.package, BaseService):
                    raise ValueError("Invalid provider format")
                self.service = mail_.package

            elif mail_.category == "llmconfig" and llmconfig:
                if not isinstance(mail_.package, dict):
                    raise ValueError("Invalid llmconfig format")
                self.llmconfig.update(mail_.package)

            else:
                skipped_requests.append(mail_)

        self.pending_ins[sender] = skipped_requests
        if self.pending_ins[sender] == deque():
            self.pending_ins.pop(sender)

    def receive_all(self) -> None:
        """
        Processes all pending incoming mail from all senders.

        This method iterates through all senders with pending mails, processing each according to its
        category and the branch's current operational context.
        """
        for key in list(self.pending_ins.keys()):
            self.receive(key)

    @staticmethod
    def _add_service(service, llmconfig):
        """
        Adds an external service and its configuration to the branch.

        Args:
            service: The service to be added to the branch.
            llmconfig: Configuration details for the language model service.

        Returns:
            A tuple containing the added service and its configuration.

        This internal method ensures the branch is equipped with an external service for processing
        requests and responses, along with the necessary configuration.
        """
        from lionagi.integrations.provider.oai import OpenAIService

        if service is None:
            try:
                from lionagi.integrations.provider import Services

                service = Services.OpenAI()

            except:
                raise ValueError("No available service")
        if llmconfig is None:
            if isinstance(service, OpenAIService):
                from lionagi.integrations.config import oai_schema

                llmconfig = oai_schema["chat/completions"]["config"]
            else:
                llmconfig = {}
        return service, llmconfig

    def _is_invoked(self) -> bool:
        """
        Determines if the branch has been invoked with an actionable response.

        Returns:
            bool: True if the last message in the branch contains an action response indicating that
                  an action has been taken or needs to be taken, False otherwise.

        This method aids in identifying branches where an automated process has been triggered,
        requiring attention or further action.
        """
        content = self.messages.iloc[-1]["content"]
        try:
            action_response = convert.to_dict(content)["action_response"]
            if convert.to_dict(action_response).keys() >= {
                "function",
                "arguments",
                "output",
            }:
            # if MessageUtil.to_dict_content(content)["action_response"].keys() >= {
            #     "function",
            #     "arguments",
            #     "output",
            # }:
                return True
        except:
            return False

    async def chat(
        self,
        instruction: Union[Instruction, str],
        context: Optional[Any] = None,
        sender: Optional[str] = None,
        system: Optional[Union[System, str, dict[str, Any]]] = None,
        tools: Union[bool, T, list[T], str, list[str]] = False,
        out: bool = True,
        invoke: bool = True,
        **kwargs,
    ) -> Any:
        """
        Initiates a chat within the branch using the specified instruction and parameters.

        This asynchronous method processes the instruction and optionally interacts with external tools or services based on the provided configurations.

        Args:
            instruction: The instruction to be processed in the chat.
            context: Additional context for the chat, if any.
            sender: The identifier of the sender of the instruction.
            system: Optional system message or data to be included at the beginning of the chat.
            tools: Specifies whether to use any tools during the chat process.
            out (bool, optional): If True, outputs the response from the chat. Default is True.
            invoke (bool, optional): If True, allows invocation of actions based on the chat outcome. Default is True.
            **kwargs: Additional keyword arguments for configuring the chat process.

        Returns:
            The outcome of the chat process, which may include a response message, action invocations, or tool outputs.
        """
        flow = MonoChat(self)
        return await flow.chat(
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            out=out,
            invoke=invoke,
            **kwargs,
        )

    async def ReAct(
        self,
        instruction: Union[Instruction, str],
        context=None,
        sender: str | None = None,
        system: dict | list | System | None = None,
        tools: TOOL_TYPE | None = None,
        num_rounds: int = 1,
        **kwargs,
    ):
        """
        Processes a reaction or response to an instruction with multiple rounds of interaction.

        Args:
            instruction: The instruction or task for the reaction.
            context: Optional context for the task.
            sender: Sender of the instruction.
            system: Optional system message to include.
            tools: Tools to utilize during the reaction.
            num_rounds: Number of interaction rounds to execute.
            **kwargs: Additional keyword arguments for the reaction process.
        """
        flow = MonoChat(self)
        return await flow.ReAct(
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            num_rounds=num_rounds,
            **kwargs,
        )

    async def auto_followup(
        self,
        instruction: Union[Instruction, str],
        context=None,
        sender: str | None = None,
        system: dict | list | System | None = None,
        tools: Union[bool, T, list[T], str, list[str], list[dict]] = False,
        max_followup: int = 3,
        out=True,
        **kwargs,
    ) -> None:
        """
        Automatically manages follow-up interactions based on an instruction.

        Args:
            instruction: The initial instruction for follow-up.
            context: Optional context for the instruction.
            sender: The sender of the instruction.
            system: Optional system message for initial setup.
            tools: Tools to be considered for follow-up actions.
            max_followup: Maximum number of follow-up interactions allowed.
            out: Specifies whether to output the final result.
            **kwargs: Additional keyword arguments for follow-up configuration.
        """
        flow = MonoChat(self)
        return await flow.auto_followup(
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            max_followup=max_followup,
            out=out,
            **kwargs,
        )

    async def followup(
        self,
        instruction: Union[Instruction, str],
        context=None,
        sender: str | None = None,
        system: dict | list | System | None = None,
        tools: bool | Tool | list[Tool | str | dict] | str = False,
        max_followup: int = 1,
        out=True,
        **kwargs,
    ) -> None:
        """
        Manages a specified number of follow-up interactions for a given instruction.

        Args:
            instruction: The instruction for which follow-ups are being managed.
            context: Optional context relevant to the instruction.
            sender: The identifier of the sender.
            system: Optional initial system message for setup.
            tools: Specifies the use of tools in the follow-up process.
            max_followup: The maximum number of follow-ups to conduct.
            out: Indicates whether to output the final result.
            **kwargs: Additional keyword arguments for configuring the follow-up.
        """
        flow = MonoChat(self)
        return await flow.followup(
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            max_followup=max_followup,
            out=out,
            **kwargs,
        )
