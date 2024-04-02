"""
This module contains the ExecutableBranch class, which represents an executable branch in a conversation tree.
"""

import contextlib
from collections import deque
from typing import Any

from lionagi.libs import convert, AsyncUtil, ParseUtil

from ..schema import BaseRelatableNode, ActionNode
from ..mail import BaseMail
from ..messages import System, Instruction

from .branch import Branch


class ExecutableBranch(BaseRelatableNode):
    """
    Represents an executable branch in a conversation tree.

    Attributes:
        branch (Branch): The branch associated with the executable branch.
        pending_ins (dict): The pending incoming mails for the executable branch.
        pending_outs (deque): The pending outgoing mails for the executable branch.
        responses (list): The responses generated by the executable branch.
        execute_stop (bool): A flag indicating whether the execution should stop.
        context (Any): The context of the executable branch.
        context_log (list): The log of contexts for the executable branch.
        verbose (bool): A flag indicating whether to provide verbose output.

    Methods:
        __init__(self, verbose=True, **kwargs) -> None:
            Initializes the ExecutableBranch instance.

        send(self, recipient_id: str, category: str, package: Any) -> None:
            Sends a mail to a recipient.

        async forward(self) -> None:
            Forwards the pending incoming mails to the appropriate processing methods.

        async execute(self, refresh_time=1) -> None:
            Executes the executable branch.

        async _process_node(self, mail: BaseMail) -> None:
            Processes a node mail.

        _process_node_list(self, mail: BaseMail) -> None:
            Processes a node list mail.

        _process_condition(self, mail: BaseMail) -> None:
            Processes a condition mail.

        _system_process(self, system: System, verbose=True, context_verbose=False) -> None:
            Processes a system message.

        async _instruction_process(self, instruction: Instruction, verbose=True, **kwargs) -> None:
            Processes an instruction message.

        async _action_process(self, action: ActionNode, verbose=True) -> None:
            Processes an action node.

        async _agent_process(self, agent, verbose=True) -> None:
            Processes an agent.

        _process_start(self, mail: BaseMail) -> None:
            Processes a start mail.

        _process_end(self, mail: BaseMail) -> None:
            Processes an end mail.
    """

    def __init__(self, verbose=True, **kwargs):
        """
        Initializes the ExecutableBranch instance.

        Args:
            verbose (bool): A flag indicating whether to provide verbose output (default: True).
            **kwargs: Additional keyword arguments for initializing the branch.
        """
        super().__init__()
        self.branch: Branch = Branch(**kwargs)
        self.pending_ins = {}  # needed
        self.pending_outs = deque()  # needed
        self.responses = []
        self.execute_stop = False  # needed
        self.context = None  # needed
        self.context_log = []
        self.verbose = verbose

    def send(self, recipient_id: str, category: str, package: Any) -> None:
        """
        Sends a mail to a recipient.

        Args:
            recipient_id (str): The ID of the recipient.
            category (str): The category of the mail.
            package (Any): The package to send in the mail.
        """
        mail = BaseMail(
            sender_id=self.id_,
            recipient_id=recipient_id,
            category=category,
            package=package,
        )
        self.pending_outs.append(mail)

    async def forward(self) -> None:
        """
        Forwards the pending incoming mails to the appropriate processing methods.
        """
        for key in list(self.pending_ins.keys()):
            while self.pending_ins[key]:
                mail = self.pending_ins[key].popleft()
                if mail.category == "start":
                    self._process_start(mail)
                elif mail.category == "node":
                    await self._process_node(mail)
                elif mail.category == "node_list":
                    self._process_node_list(mail)
                elif mail.category == "condition":
                    self._process_condition(mail)
                elif mail.category == "end":
                    self._process_end(mail)

    async def execute(self, refresh_time=1) -> None:
        """
        Executes the executable branch.

        Args:
            refresh_time (int): The refresh time for execution (default: 1).
        """
        while not self.execute_stop:
            await self.forward()
            await AsyncUtil.sleep(refresh_time)

    async def _process_node(self, mail: BaseMail):
        """
        Processes a node mail.

        Args:
            mail (BaseMail): The node mail to process.

        Raises:
            ValueError: If the mail package is invalid.
        """
        if isinstance(mail.package["package"], System):
            self._system_process(mail.package["package"], verbose=self.verbose)
            self.send(mail.sender_id, "node_id", {"request_source": self.id_, "package": mail.package["package"].id_})

        elif isinstance(mail.package["package"], Instruction):
            await self._instruction_process(mail.package["package"], verbose=self.verbose)
            self.send(mail.sender_id, "node_id", {"request_source": self.id_, "package": mail.package["package"].id_})

        elif isinstance(mail.package["package"], ActionNode):
            await self._action_process(mail.package["package"], verbose=self.verbose)
            self.send(mail.sender_id, "node_id", {"request_source": self.id_, "package": mail.package["package"].instruction.id_})
        else:
            try:
                await self._agent_process(mail.package["package"], verbose=self.verbose)
                self.send(mail.sender_id, "node_id", {"request_source": self.id_, "package": mail.package["package"].id_})
            except:
                raise ValueError(f"Invalid mail to process. Mail:{mail}")

    def _process_node_list(self, mail: BaseMail):
        """
        Processes a node list mail.

        Args:
            mail (BaseMail): The node list mail to process.

        Raises:
            ValueError: If multiple path selection is not supported.
        """
        self.send(mail.sender_id, "end", {"request_source": self.id_, "package": "end"})
        self.execute_stop = True
        raise ValueError("Multiple path selection is currently not supported")

    def _process_condition(self, mail: BaseMail):
        """
        Processes a condition mail.

        Args:
            mail (BaseMail): The condition mail to process.
        """
        relationship = mail.package["package"]
        check_result = relationship.condition(self)
        back_mail = {"from": self.branch.id_, "relationship_id": mail.package["package"].id_, "check_result": check_result}
        self.send(mail.sender_id, "condition", {"request_source": self.id_, "package": back_mail})

    def _system_process(self, system: System, verbose=True, context_verbose=False):
        """
        Processes a system message.

        Args:
            system (System): The system message to process.
            verbose (bool): A flag indicating whether to provide verbose output (default: True).
            context_verbose (bool): A flag indicating whether to display the context (default: False).
        """
        from lionagi.libs import SysUtil

        SysUtil.check_import("IPython")
        from IPython.display import Markdown, display

        if verbose:
            print(f"------------------Welcome: {system.sender}--------------------")
            with contextlib.suppress(Exception):
                system.content = ParseUtil.fuzzy_parse_json(system.content)
            display(Markdown(f"system: {convert.to_str(system.system_info)}"))
            if self.context and context_verbose:
                display(Markdown(f"context: {convert.to_str(self.context)}"))

        self.branch.add_message(system=system)

    async def _instruction_process(
        self, instruction: Instruction, verbose=True, **kwargs
    ):
        """
        Processes an instruction message.

        Args:
            instruction (Instruction): The instruction message to process.
            verbose (bool): A flag indicating whether to provide verbose output (default: True).
            **kwargs: Additional keyword arguments for processing the instruction.
        """
        from lionagi.libs import SysUtil

        SysUtil.check_import("IPython")
        from IPython.display import Markdown, display

        if verbose:
            with contextlib.suppress(Exception):
                instruction.content = ParseUtil.fuzzy_parse_json(instruction.content)
            display(
                Markdown(
                    f"{instruction.sender}: {convert.to_str(instruction.instruct)}"
                )
            )

        if self.context:
            instruction.content.update({"context": self.context})
            self.context = None

        result = await self.branch.chat(instruction, **kwargs)
        with contextlib.suppress(Exception):
            result = ParseUtil.fuzzy_parse_json(result)
            if "response" in result.keys():
                result = result["response"]
        if verbose and len(self.branch.assistant_responses) != 0:
            display(
                Markdown(
                    f"{self.branch.last_assistant_response.sender}: {convert.to_str(result)}"
                )
            )
            print("-----------------------------------------------------")

        self.responses.append(result)

    async def _action_process(self, action: ActionNode, verbose=True):
        """
        Processes an action node.

        Args:
            action (ActionNode): The action node to process.
            verbose (bool): A flag indicating whether to provide verbose output (default: True).

        Raises:
            ValueError: If the action is not valid.
        """
        from lionagi.libs import SysUtil

        SysUtil.check_import("IPython")
        from IPython.display import Markdown, display

        try:
            func = getattr(self.branch, action.action)
        except:
            raise ValueError(f"{action.action} is not a valid action")

        if verbose:
            display(
                Markdown(
                    f"{action.instruction.sender}: {convert.to_str(action.instruction.instruct)}"
                )
            )

        if action.tools:
            self.branch.register_tools(action.tools)
        if self.context:
            result = await func(
                action.instruction.content["instruction"],
                context=self.context,
                tools=action.tools,
                **action.action_kwargs,
            )
            self.context = None
        else:
            result = await func(
                action.instruction.content, tools=action.tools, **action.action_kwargs
            )

        if verbose and len(self.branch.assistant_responses) != 0:
            display(
                Markdown(
                    f"{self.branch.last_assistant_response.sender}: {convert.to_str(result)}"
                )
            )
            print("-----------------------------------------------------")

        self.responses.append(result)

    async def _agent_process(self, agent, verbose=True):
        """
        Processes an agent.

        Args:
            agent: The agent to process.
            verbose (bool): A flag indicating whether to provide verbose output (default: True).
        """
        context = self.responses
        if verbose:
            print("*****************************************************")
        result = await agent.execute(context)

        if verbose:
            print("*****************************************************")

        self.context = result
        self.responses.append(result)

    def _process_start(self, mail):
        """
        Processes a start mail.

        Args:
            mail (BaseMail): The start mail to process.
        """
        start_mail_content = mail.package
        self.context = start_mail_content["context"]
        self.send(start_mail_content["structure_id"], "start", {"request_source": self.id_, "package": "start"})

    def _process_end(self, mail):
        """
        Processes an end mail.

        Args:
            mail (BaseMail): The end mail to process.
        """
        self.execute_stop = True
        self.send(mail.sender_id, "end", {"request_source": self.id_, "package": "end"})