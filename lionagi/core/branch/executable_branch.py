import contextlib
from collections import deque
from typing import Any

from lionagi.libs import convert, AsyncUtil, ParseUtil

from ..schema import BaseRelatableNode, ActionNode
from ..mail import BaseMail
from ..messages import System, Instruction
from ..agent import BaseAgent

from .branch import Branch


class ExecutableBranch(BaseRelatableNode):

    def __init__(self, verbose=True, **kwargs):
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
        mail = BaseMail(
            sender_id=self.id_,
            recipient_id=recipient_id,
            category=category,
            package=package,
        )
        self.pending_outs.append(mail)

    async def forward(self):
        for key in list(self.pending_ins.keys()):
            while self.pending_ins[key]:
                mail = self.pending_ins[key].popleft()
                if mail.category == "start":  # needed
                    self._process_start(mail)
                elif mail.category == "node":
                    await self._process_node(mail)
                elif mail.category == "node_list":
                    self._process_node_list(mail)
                elif mail.category == "condition":
                    self._process_condition(mail)
                elif mail.category == "end":  # needed
                    self._process_end(mail)

    async def execute(self, refresh_time=1):  # needed
        while not self.execute_stop:
            await self.forward()
            await AsyncUtil.sleep(refresh_time)

    async def _process_node(self, mail: BaseMail):

        if isinstance(mail.package, System):
            self._system_process(mail.package, verbose=self.verbose)
            self.send(mail.sender_id, "node_id", mail.package.id_)

        elif isinstance(mail.package, Instruction):
            await self._instruction_process(mail.package, verbose=self.verbose)
            self.send(mail.sender_id, "node_id", mail.package.id_)

        elif isinstance(mail.package, ActionNode):
            await self._action_process(mail.package, verbose=self.verbose)
            self.send(mail.sender_id, "node_id", mail.package.instruction.id_)
        else:
            try:
                await self._agent_process(mail.package, verbose=self.verbose)
                self.send(mail.sender_id, "node_id", mail.package.id_)
            except:
                raise ValueError(f"Invalid mail to process. Mail:{mail}")

    def _process_node_list(self, mail: BaseMail):
        self.send(mail.sender_id, "end", "end")
        self.execute_stop = True
        raise ValueError("Multiple path selection is currently not supported")

    def _process_condition(self, mail: BaseMail):
        relationship = mail.package
        check_result = relationship.condition(self)
        back_mail = {"relationship_id": mail.package.id_, "check_result": check_result}
        self.send(mail.sender_id, "condition", back_mail)

    def _system_process(self, system: System, verbose=True, context_verbose=False):
        from lionagi.libs import SysUtil
        SysUtil.check_import('IPython')
        from IPython.display import Markdown, display
        if verbose:
            print(f"------------------Welcome: {system.sender}--------------------")
            display(Markdown(f"system: {convert.to_str(system.system_info)}"))
            if self.context and context_verbose:
                display(Markdown(f"context: {convert.to_str(self.context)}"))

        self.branch.add_message(system=system)

    async def _instruction_process(
        self, instruction: Instruction, verbose=True, **kwargs
    ):
        from lionagi.libs import SysUtil
        SysUtil.check_import('IPython')
        from IPython.display import Markdown, display
        if verbose:
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
        from lionagi.libs import SysUtil
        SysUtil.check_import('IPython')
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
        context = self.responses
        if verbose:
            print("*****************************************************")
        result = await agent.execute(context)

        if verbose:
            print("*****************************************************")

        self.context = result
        self.responses.append(result)

    def _process_start(self, mail):
        start_mail_content = mail.package
        self.context = start_mail_content["context"]
        self.send(start_mail_content["structure_id"], "start", "start")

    def _process_end(self, mail):
        self.execute_stop = True
        self.send(mail.sender_id, "end", "end")
