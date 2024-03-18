from collections import deque
from typing import Any

from IPython.display import Markdown, display

import lionagi.libs.ln_convert as convert
from lionagi.libs.ln_async import AsyncUtil
from lionagi.libs.ln_parse import ParseUtil

from lionagi.core.schema.base_node import BaseRelatableNode
from lionagi.core.schema.action_node import ActionNode

from lionagi.core.mail.schema import BaseMail

from lionagi.core.messages.schema import System, Instruction


from lionagi import Branch
from lionagi.core.agent.base_agent import BaseAgent


class ExecutableBranch(BaseRelatableNode):

    def __init__(self, **kwargs):
        super().__init__()
        self.branch: Branch = Branch(**kwargs)
        self.pending_ins = {}  # needed
        self.pending_outs = deque()  # needed
        self.responses = []
        self.execute_stop = False  # needed
        self.context = None  # needed

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
                if mail.category == "node":
                    await self._process_node(mail)
                elif mail.category == "end":  # needed
                    self._process_end(mail)

    async def execute(self, refresh_time=1):  # needed
        while not self.execute_stop:
            await self.forward()
            await AsyncUtil.sleep(refresh_time)

    async def _process_node(self, mail: BaseMail):

        if isinstance(mail.package, System):
            self._system_process(mail.package)
            self.send(mail.sender_id, "node_id", mail.package.id_)
            return

        elif isinstance(mail.package, Instruction):
            await self._instruction_process(mail.package)
            self.send(mail.sender_id, "node_id", mail.package.id_)
            return

        elif isinstance(mail.package, ActionNode):
            await self._action_process(mail.package)
            self.send(mail.sender_id, "node_id", mail.package.instruction.id_)
            return

        elif isinstance(mail.package, BaseAgent):
            await self._agent_process(mail.package)
            self.send(mail.sender_id, "node_id", mail.package.id_)
            return

    def _system_process(self, system: System, verbose=True, context_verbose=False):
        if verbose:
            print(f"---------------Welcome: {system.recipient}------------------")
            display(Markdown(f"system: {convert.to_str(system.system_info)}"))
            if self.context and context_verbose:
                display(Markdown(f"context: {convert.to_str(self.context)}"))

        self.branch.add_message(system=system)

    async def _instruction_process(
        self, instruction: Instruction, verbose=True, **kwargs
    ):
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
        try:
            result = ParseUtil.fuzzy_parse_json(result)
            if "response" in result.keys():
                result = result["response"]
        except:
            pass

        if verbose:
            display(
                Markdown(
                    f"{self.branch.last_assistant_response.sender}: {convert.to_str(result)}"
                )
            )

        self.responses.append(result)

    async def _agent_process(self, agent):
        context = self.responses
        result = await agent.execute(context)

        self.context = result
        self.responses.append(result)

    def _process_start(self, mail):
        start_mail_content = mail.package
        self.context = start_mail_content["context"]
        self.send(start_mail_content["structure_id"], "start", "start")

    def _process_end(self, mail):
        self.execute_stop = True
        self.send(mail.sender_id, "end", "end")

    async def _action_process(self, action: ActionNode):
        # instruction = action.instruction
        # if self.context:
        #     instruction.content.update({"context": self.context})
        #     self.context=None
        try:
            func = getattr(self.branch, action.action)
        except:
            raise ValueError(f"{action.action} is not a valid action")

        if action.tools:
            self.branch.register_tools(action.tools)
        # result = await func(instruction, tools=action.tools, **action.action_kwargs)
        if self.context:
            result = await func(
                action.instruction.content,
                context=self.context,
                tools=action.tools,
                **action.action_kwargs,
            )
            self.context = None
        else:
            result = await func(
                action.instruction.content, tools=action.tools, **action.action_kwargs
            )
        print("action calls:", result)
        self.responses.append(result)
