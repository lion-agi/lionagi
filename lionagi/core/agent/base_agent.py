from collections.abc import Callable
from typing import Any

from lionagi.core.executor.base_executor import BaseExecutor
from lionagi.core.generic.node import Node
from lionagi.core.mail.mail_manager import MailManager
from lionagi.core.mail.start_mail import StartMail
from lionagi.libs import AsyncUtil, func_call


class BaseAgent(Node):

    def __init__(
        self,
        structure: BaseExecutor,
        executable: BaseExecutor,
        output_parser=None,
        **kwargs,
    ) -> None:
        """
        Initializes the BaseAgent instance.

        Args:
            structure: The structure of the agent.
            executable_obj: The executable object of the agent.
            output_parser: A function for parsing the agent's output (optional).
        """
        super().__init__(**kwargs)
        self.structure: BaseExecutor = structure
        self.executable: BaseExecutor = executable
        self.start: StartMail = StartMail()
        self.mail_manager: MailManager = MailManager(
            [self.structure, self.executable, self.start]
        )
        self.output_parser: Callable | None = output_parser
        self.start_context: Any | None = None

    async def mail_manager_control(self, refresh_time=1):
        """
        Controls the mail manager execution based on the structure and executable states.

        Args:
            refresh_time: The time interval (in seconds) for checking the execution states (default: 1).
        """
        while (
            not self.structure.execute_stop or not self.executable.execute_stop
        ):
            await AsyncUtil.sleep(refresh_time)
        self.mail_manager.execute_stop = True

    async def execute(self, context=None):
        """
        Executes the agent with the given context and returns the parsed output (if available).

        Args:
            context: The initial context for the agent (optional).

        Returns:
            The parsed output of the agent (if available).
        """
        self.start_context = context
        self.start.trigger(
            context=context,
            structure_id=self.structure.ln_id,
            executable_id=self.executable.ln_id,
        )
        await func_call.mcall(
            [0.1, 0.1, 0.1, 0.1],
            [
                self.structure.execute,
                self.executable.execute,
                self.mail_manager.execute,
                self.mail_manager_control,
            ],
        )

        self.structure.execute_stop = False
        self.executable.execute_stop = False
        self.mail_manager.execute_stop = False

        if self.output_parser:
            return self.output_parser(self)
