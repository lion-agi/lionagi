"""
This module contains the BaseAgent class, which serves as a base class for agents.
"""

from lionagi.core.mail.schema import StartMail
from lionagi.core.schema.base_node import BaseRelatableNode
from lionagi.core.mail.mail_manager import MailManager

from lionagi.libs import func_call, AsyncUtil


class BaseAgent(BaseRelatableNode):
    """
    A base class for agents.

    Attributes:
        structure: The structure of the agent.
        executable: The executable object of the agent.
        start: The StartMail object for triggering the agent.
        mailManager: The MailManager object for managing agent communication.
        output_parser: A function for parsing the agent's output (optional).
        start_context: The initial context for the agent (optional).

    Methods:
        __init__(self, structure, executable_obj, output_parser=None) -> None:
            Initializes the BaseAgent instance.

        async mail_manager_control(self, refresh_time=1) -> None:
            Controls the mail manager execution based on the structure and executable states.

        async execute(self, context=None) -> Any:
            Executes the agent with the given context and returns the parsed output (if available).
    """

    def __init__(self, structure, executable_obj, output_parser=None) -> None:
        """
        Initializes the BaseAgent instance.

        Args:
            structure: The structure of the agent.
            executable_obj: The executable object of the agent.
            output_parser: A function for parsing the agent's output (optional).
        """
        super().__init__()
        self.structure = structure
        self.executable = executable_obj
        self.start = StartMail()
        self.mailManager = MailManager([self.structure, self.executable, self.start])
        self.output_parser = output_parser
        self.start_context = None

    async def mail_manager_control(self, refresh_time=1):
        """
        Controls the mail manager execution based on the structure and executable states.

        Args:
            refresh_time: The time interval (in seconds) for checking the execution states (default: 1).
        """
        while not self.structure.execute_stop or not self.executable.execute_stop:
            await AsyncUtil.sleep(refresh_time)
        self.mailManager.execute_stop = True

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
            structure_id=self.structure.id_,
            executable_id=self.executable.id_,
        )
        await func_call.mcall(
            [0.1, 0.1, 0.1, 0.1],
            [
                self.structure.execute,
                self.executable.execute,
                self.mailManager.execute,
                self.mail_manager_control,
            ],
        )

        self.structure.execute_stop = False
        self.executable.execute_stop = False
        self.mailManager.execute_stop = False

        if self.output_parser:
            return self.output_parser(self)
