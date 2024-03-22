from lionagi.core.mail.schema import StartMail
from lionagi.core.schema.base_node import BaseRelatableNode
from lionagi.core.mail.mail_manager import MailManager

from lionagi.libs import func_call, AsyncUtil


class BaseAgent(BaseRelatableNode):
    def __init__(self, structure, executable_obj, output_parser=None) -> None:

        super().__init__()
        self.structure = structure
        self.executable = executable_obj
        self.start = StartMail()
        self.mailManager = MailManager([self.structure, self.executable, self.start])
        self.output_parser = output_parser
        self.start_context = None

    async def mail_manager_control(self, refresh_time=1):
        while not self.structure.execute_stop or not self.executable.execute_stop:
            await AsyncUtil.sleep(refresh_time)
        self.mailManager.execute_stop = True

    async def execute(self, context=None):
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
