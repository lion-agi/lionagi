import contextlib
from lionagi.libs import convert, AsyncUtil, ParseUtil
from lionagi.core.schema import ActionNode
from lionagi.core.mail import BaseMail
from lionagi.core.messages import System, Instruction

from lionagi.core.branch import Branch
from lionagi.core.execute.base_executor import BaseExecutor

class BranchExecutor(Branch, BaseExecutor):

    async def forward(self) -> None:
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
        while not self.execute_stop:
            await self.forward()
            await AsyncUtil.sleep(refresh_time)

    async def _process_node(self, mail: BaseMail):
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
        self.send(mail.sender_id, "end", {"request_source": self.id_, "package": "end"})
        self.execute_stop = True
        raise ValueError("Multiple path selection is currently not supported")

    def _process_condition(self, mail: BaseMail):
        relationship = mail.package["package"]
        check_result = relationship.condition(self)
        back_mail = {"from": self.id_, "edge_id": mail.package["package"].id_, "check_result": check_result}
        self.send(mail.sender_id, "condition", {"request_source": self.id_, "package": back_mail})

    def _system_process(self, system: System, verbose=True, context_verbose=False):
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

        self.add_message(system=system)

    async def _instruction_process(self, instruction: Instruction, verbose=True, **kwargs):
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

        result = await self.chat(instruction, **kwargs)
        with contextlib.suppress(Exception):
            result = ParseUtil.fuzzy_parse_json(result)
            if "response" in result.keys():
                result = result["response"]
        if verbose and len(self.assistant_responses) != 0:
            display(
                Markdown(
                    f"{self.last_assistant_response.sender}: {convert.to_str(result)}"
                )
            )
            print("-----------------------------------------------------")

        self.execution_responses.append(result)

    async def _action_process(self, action: ActionNode, verbose=True):
        from lionagi.libs import SysUtil

        SysUtil.check_import("IPython")
        from IPython.display import Markdown, display

        try:
            func = getattr(self, action.action)
        except:
            raise ValueError(f"{action.action} is not a valid action")

        if verbose:
            display(
                Markdown(
                    f"{action.instruction.sender}: {convert.to_str(action.instruction.instruct)}"
                )
            )

        if action.tools:
            self.register_tools(action.tools)
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

        if verbose and len(self.assistant_responses) != 0:
            display(
                Markdown(
                    f"{self.last_assistant_response.sender}: {convert.to_str(result)}"
                )
            )
            print("-----------------------------------------------------")

        self.execution_responses.append(result)

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
        
