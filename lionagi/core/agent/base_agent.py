from collections import deque

from lionagi.core.schema import BaseRelatableNode
from lionagi.core.mail import StartMail, MailManager

from lionagi.libs import func_call, AsyncUtil


class BaseAgent(BaseRelatableNode):
    def __init__(self, structure, executable_class, output_parser=None, executable_class_kwargs=None) -> None:
        if executable_class_kwargs is None:
            executable_class_kwargs = {}
        super().__init__()
        self.structure = structure
        self.executable = executable_class(**executable_class_kwargs)
        self.start = StartMail()
        self.mailManager = MailManager([self.structure, self.executable, self.start])
        self.output_parser = output_parser

    async def mail_manager_control(self, refresh_time=1):
        while not self.structure.execute_stop or not self.executable.execute_stop:
            await AsyncUtil.sleep(refresh_time)
        self.mailManager.execute_stop = True

    async def execute(self, context=None):
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

        if self.output_parser:
            return self.output_parser(self)
