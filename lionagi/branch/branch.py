from collections import deque
from typing import Any, Dict, List, Optional, Union, TypeVar

import pandas as pd

from lionagi.util import to_dict, to_list, SysUtil
from lionagi.schema import BaseActionNode, BaseMail
from lionagi.message import Instruction, System
from lionagi.action import ActionManager
from lionagi.provider import StatusTracker, Services, BaseService
from lionagi.provider.api.oai import OpenAIService
from lionagi.flow import ChatFlow

from .util import MessageUtil
from lionagi.branch.conversation import Conversation

OAIService = "OpenAI"
# default service should change to be settable
try:
    OAIService = Services.OpenAI()
except:
    pass

T = TypeVar('T', bound='Branch')


# noinspection PyUnresolvedReferences
class Branch(Conversation):
    """
    Manages dynamic chat flows, integrating with Language Learning Models (LLMs) and executing custom actions.

    The `Branch` class extends `Conversation` to offer advanced features for real-time chat management. It enables asynchronous communication, integrates with LLMs for response generation, and handles custom actions for interactive chat experiences. Suitable for developing sophisticated chatbots, virtual assistants, and customer support systems.

    Attributes:
        branch_name (Optional[str]): An identifier for the branch.
        sender (str): Default sender identifier, defaults to 'system'.
        action_manager (ActionManager): Manages custom actions within the chat flow.
        service (BaseService): The chat service provider, defaults to OpenAI's GPT models.
        llmconfig (Dict[str, Any]): Configuration for LLM integration.
        instruction_sets (Optional[Dict[str, Any]]): Predefined sets of instructions for the chat flow.
        messages (pandas.DataFrame): Stores the chat messages.
        datalogger (DataLogger): Logs conversation data.
        persist_path (Optional[str]): Path for persisting conversation data.

    Methods:
        from_csv(filepath, **kwargs): Initializes a `Branch` instance from a CSV file.
        from_json(filepath, **kwargs): Initializes a `Branch` instance from a JSON file.
        messages_describe() -> Dict[str, Any]: Summarizes the conversation's state.
        has_actions() -> bool: Checks if there are registered actions.
        merge_branch(branch, update=True): Merges conversation data from another branch.
        register(actions): Registers custom actions.
        delete_actions(actions, verbose=True) -> bool: Deletes specified actions.
        send(recipient, category, package): Sends a package to a recipient.
        receive(sender, **kwargs): Receives a package from a sender.
        _add_service(service, llmconfig): Adds a chat service provider.
        _is_invoked() -> bool: Checks if an action has been invoked.
        call_chatcompletion(**kwargs): Asynchronously calls the chat completion service.
        chat(**kwargs) -> Any: Processes a chat instruction asynchronously.
        ReAct(**kwargs): Executes a reason-action cycle.
        auto_followup(**kwargs): Performs automated follow-up actions.

    """

    def __init__(self, branch_name=None, system=None, messages=None, service=None,
                 sender=None, llmconfig=None, actions=None, datalogger=None,
                 persist_path=None, instruction_sets=None, action_manager=None, **kwargs):
        """
        Initializes a Branch instance with configurable parameters for chat flow management.

        Args:
            branch_name (Optional[str]): Identifier for the branch instance.
            system (Optional[Union[System, str, Dict[str, Any]]]): Initial system message or configuration.
            messages (Optional[pandas.DataFrame]): Preloaded messages for the conversation.
            service (Optional[BaseService]): Chat service provider. Defaults to OpenAI if not specified.
            sender (Optional[str]): Default sender identifier. Defaults to 'system'.
            llmconfig (Optional[Dict[str, Any]]): Configuration for LLM integration.
            actions (Optional[Union[BaseActionNode, List[BaseActionNode]]]): List of actions to be registered.
            datalogger (Optional[DataLogger]): Logs conversation data.
            persist_path (Optional[str]): Path for persisting conversation data.
            instruction_sets (Optional[Dict[str, Any]]): Sets of instructions for guiding the chat flow.
            action_manager (Optional[ActionManager]): Manages custom actions within the chat flow.
            **kwargs: Additional keyword arguments for configuration.
        """

        # init base conversation class
        super().__init__(messages=messages, datalogger=datalogger,
                         persist_path=persist_path, **kwargs)

        # add branch name
        self.branch_name = branch_name
        self.sender = sender or 'system'

        # add action manager and register actions
        self.action_manager = action_manager if action_manager else ActionManager()
        if actions:
            try:
                self.register(actions)
            except Exception as e:
                raise TypeError(f"Error in registering actions: {e}")

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
                 actions=None, datalogger=None, persist_path=None, instruction_sets=None,
                 action_manager=None, read_kwargs=None, **kwargs):
        """
        Initializes a Branch instance from a CSV file containing conversation data.

        Args:
            filepath (str): Path to the CSV file.
            branch_name, service, llmconfig, actions, datalogger, persist_path, instruction_sets, action_manager: See __init__ for details.
            read_kwargs (Optional[Dict[str, Any]]): Additional keyword arguments for pandas.read_csv().
            **kwargs: Additional initialization parameters.
        Returns:
            Branch: An instance of the Branch class.
        """
        self = cls._from_csv(
            filepath=filepath, read_kwargs=read_kwargs, branch_name=branch_name,
            service=service, llmconfig=llmconfig, actions=actions, datalogger=datalogger,
            persist_path=persist_path, instruction_sets=instruction_sets,
            action_manager=action_manager, **kwargs)

        return self

    @classmethod
    def from_json(cls, filepath, branch_name=None, service=None, llmconfig=None,
                  actions=None, datalogger=None, persist_path=None, instruction_sets=None,
                  action_manager=None, read_kwargs=None, **kwargs):
        """
        Initializes a Branch instance from a JSON file containing conversation data.

        Args:
            filepath (str): Path to the JSON file.
            branch_name, service, llmconfig, actions, datalogger, persist_path, instruction_sets, action_manager: See __init__ for details.
            read_kwargs (Optional[Dict[str, Any]]): Additional keyword arguments for pandas.read_json().
            **kwargs: Additional initialization parameters.
        Returns:
            Branch: An instance of the Branch class.
        """
        self = cls._from_json(
            filepath=filepath, read_kwargs=read_kwargs, branch_name=branch_name,
            service=service, llmconfig=llmconfig, actions=actions, datalogger=datalogger,
            persist_path=persist_path, instruction_sets=instruction_sets,
            action_manager=action_manager, **kwargs)

        return self

    def messages_describe(self) -> Dict[str, Any]:
        """
        Provides a summary of the conversation state including message counts, registered actions, and instruction sets.

        Returns:
            Dict[str, Any]: A dictionary containing details about the conversation's state, such as total message count, a summary by role and sender, and lists of instruction sets and registered actions.
        """
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self._info(),
            "summary_by_sender": self._info(use_sender=True),
            "instruction_sets": self.instruction_sets,
            "registered_actions": self.action_manager.registry,
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    @property
    def has_actions(self) -> bool:
        """
        Checks if there are any registered actions in the action manager.

        Returns:
            bool: True if there are registered actions, False otherwise.
        """
        return self.action_manager.registry != {}

    # todo: also update other attributes
    def merge_branch(self, branch: 'Branch', update: bool = True) -> None:
        """
        Merges conversation data from another branch into this one, including messages and actions.

        Args:
            branch (Branch): The branch instance to merge from.
            update (bool): If True, updates existing instruction sets and actions. If False, only adds non-existing ones.

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

    # ----- action manager methods ----- #
    def register(self, actions: Union[BaseActionNode, List[BaseActionNode]]) -> None:
        """
        Registers one or more actions with the action manager for use within the chat flow.

        Args:
            actions (Union[BaseActionNode, List[BaseActionNode]]): The action or list of actions to register.
        """
        if not isinstance(actions, list):
            actions = to_list(actions, flatten=True, dropna=True)
        self.action_manager.register(actions=actions)

    def delete_actions(
            self, actions: Union[bool, T, List[T], str, List[str], List[Dict[str, Any]]],
            verbose: bool = True
    ) -> bool:
        """
        Deletes specified actions from the action manager's registry.

        Args:
            actions (Union[bool, BaseActionNode, List[BaseActionNode], str, List[str], List[Dict[str, Any]]]): The actions to delete.
            verbose (bool): If True, prints a confirmation message.

        Returns:
            bool: True if actions were successfully deleted, False otherwise.
        """
        if isinstance(actions, list):
            if SysUtil.is_same_dtype(actions, str):
                for act_ in actions:
                    if act_ in self.action_manager.registry:
                        self.action_manager.registry.pop(act_)
                if verbose:
                    print("actions successfully deleted")
                return True
            elif SysUtil.is_same_dtype(actions, _cols):
                for act_ in actions:
                    if act_.name in self.action_manager.registry:
                        self.action_manager.registry.pop(act_.name)
                if verbose:
                    print("actions successfully deleted")
                return True
        if verbose:
            print("actions deletion failed")
        return False

    def send(self, recipient: str, category: str, package: Any) -> None:
        """
        Sends a package (message, action, etc.) to a specified recipient.

        Args:
            recipient (str): The recipient's identifier.
            category (str): The category of the package being sent.
            package (Any): The actual package to send.
        """

        mail_ = BaseMail(
            sender=self.sender, recipient=recipient, category=category,
            package=package)
        self.pending_outs.append(mail_)

    def receive(self, sender: str, messages: bool = True, actions: bool = True,
                service: bool = True, llmconfig: bool = True) -> None:
        """
        Receives and processes a package from a specified sender based on the category.

        Args:
            sender (str): The identifier of the sender.
            messages (bool): If True, processes received messages.
            actions (bool): If True, processes received actions.
            service (bool): If True, updates the service provider.
            llmconfig (bool): If True, updates the llmconfig.
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

            elif mail_.category == 'actions' and actions:
                if not isinstance(mail_.package, BaseActionNode):
                    raise ValueError('Invalid actions format')
                self.action_manager.register([mail_.package])

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
        Processes all pending packages from all senders.
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
    async def call_chatcompletion(self, sender=None, with_sender=False, **kwargs):
        """
        Asynchronously calls the chat completion service to generate a response.

        Args:
            sender (Optional[str]): The name of the sender to include in chat completions.
            with_sender (bool): If True, includes sender information in messages.
            **kwargs: Arbitrary keyword arguments for the chat completion service.
        """
        await ChatFlow.call_chatcompletion(
            self, sender=sender, with_sender=with_sender, **kwargs
        )

    async def chat(
            self,
            instruction: Union[Instruction, str],
            context: Optional[Any] = None,
            sender: Optional[str] = None,
            system: Optional[Union[System, str, Dict[str, Any]]] = None,
            actions: Union[bool, T, List[T], str, List[str]] = False,
            out: bool = True,
            invoke: bool = True,
            **kwargs) -> Any:
        """
        Processes a chat instruction asynchronously, optionally invoking actions.

        Args:
            instruction (Union[Instruction, str]): The instruction for the chat.
            context (Optional[Any]): Additional context for the chat.
            sender (Optional[str]): The sender of the chat message.
            system (Optional[Union[System, str, Dict[str, Any]]]): System message to be processed.
            actions (Union[bool, T, List[T], str, List[str]]): Specifies actions to be invoked.
            out (bool): If True, outputs the chat response.
            invoke (bool): If True, invokes actions as part of the chat.
            **kwargs: Arbitrary keyword arguments for chat completion.

        Returns:
            Any: The result of the chat operation, potentially including action outputs.
        """
        return await ChatFlow.chat(
            self, instruction=instruction, context=context,
            sender=sender, system=system, actions=actions,
            out=out, invoke=invoke, **kwargs
        )

    async def ReAct(
            self,
            instruction: Union[Instruction, str],
            context=None,
            sender=None,
            system=None,
            actions=None,
            num_rounds: int = 1,
            **kwargs):
        """
        Executes a reason-action cycle with optional actions invocation over multiple rounds.

        Args:
            instruction (Union[Instruction, str]): Initial instruction for the cycle.
            context: Context relevant to the instruction.
            sender (Optional[str]): Identifier for the message sender.
            system: Initial system message or configuration.
            actions: Tools to be registered or used during the cycle.
            num_rounds (int): Number of reason-action cycles to perform.
            **kwargs: Additional keyword arguments for customization.

        Returns:
            Any: The final result after completing the reason-action cycles.
        """
        return await ChatFlow.ReAct(
            self, instruction=instruction, context=context,
            sender=sender, system=system, actions=actions,
            num_rounds=num_rounds, **kwargs
        )

    async def auto_followup(
            self,
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
            instruction (Union[Instruction, str]): The initial instruction for follow-up.
            context: Context relevant to the instruction.
            sender (Optional[str]): Identifier for the message sender.
            system: Initial system message or configuration.
            actions: Specifies actions to be considered for follow-up actions.
            max_followup (int): Maximum number of follow-up chats allowed.
            out (bool): If True, outputs the result of the follow-up action.
            **kwargs: Additional keyword arguments for follow-up customization.
        """
        return await ChatFlow.auto_followup(
            self, instruction=instruction, context=context,
            sender=sender, system=system, actions=actions,
            max_followup=max_followup, out=out, **kwargs
        )
