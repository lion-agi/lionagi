from collections import deque
import asyncio

from lionagi.core import ExecutableBranch
from lionagi.core.schema import BaseRelatableNode
from lionagi.core.mail.mail_manager import MailManager
from lionagi.core.mail import BaseMail


class ExecutableInstructionMapping(BaseRelatableNode):

    def __init__(self, verbose=True, **kwargs):
        super().__init__()
        self.branches = {}
        self.pending_ins = {}
        self.pending_outs = deque()
        self.structure_id = ""
        self.mail_transfer = MailTransder()
        self.mail_manager = MailManager([self.mail_transfer])
        self.execute_stop = False
        self.verbose = verbose
        self.kwargs = kwargs
        self.num_end_branches = 0

    def transfer_ins(self):
        for key in list(self.pending_ins.keys()):
            while self.pending_ins[key]:
                mail = self.pending_ins[key].popleft()
                if mail.category == "start":
                    self._process_start(mail)
                elif mail.category == "node_list":
                    self._process_node_list(mail)
                elif (mail.category == "node") or (mail.category == "condition") or (mail.category == "end"):
                    mail.sender_id = self.mail_transfer.id_
                    mail.recipient_id = mail.package['request_source']
                    self.mail_transfer.pending_outs.append(mail)

    def transfer_outs(self):
        for key in list(self.mail_transfer.pending_ins.keys()):
            while self.mail_transfer.pending_ins[key]:
                mail = self.mail_transfer.pending_ins[key].popleft()
                if mail.category == "end":
                    self.num_end_branches += 1
                    if self.num_end_branches == len(self.branches):  # tell when structure should stop
                        mail.sender_id = self.id_
                        mail.recipient_id = self.structure_id
                        self.pending_outs.append(mail)
                        self.execute_stop = True
                else:
                    mail.sender_id = self.id_
                    mail.recipient_id = self.structure_id
                    self.pending_outs.append(mail)

    def _process_start(self, start_mail):
        branch = ExecutableBranch(verbose=self.verbose, **self.kwargs)
        branch.context = start_mail.package["context"]
        self.branches[branch.id_] = branch
        self.mail_manager.add_sources([branch])
        self.structure_id = start_mail.package["structure_id"]
        mail = BaseMail(sender_id=self.id_,
                        recipient_id=self.structure_id,
                        category="start",
                        package={"request_source": branch.id_, "package": "start"})
        self.pending_outs.append(mail)

    def _process_node_list(self, nl_mail):
        source_branch_id = nl_mail.package["request_source"]
        node_list = nl_mail.package["package"]
        shared_context = self.branches[source_branch_id].context
        shared_context_log = self.branches[source_branch_id].context_log
        base_branch = self.branches[source_branch_id].branch

        first_node_mail = BaseMail(sender_id=self.mail_transfer.id_,
                                   recipient_id=source_branch_id,
                                   category="node",
                                   package={"request_source": source_branch_id, "package": node_list[0]})
        self.mail_transfer.pending_outs.append(first_node_mail)

        for i in range(1, len(node_list)):
            branch = ExecutableBranch(verbose=self.verbose,
                                      messages=base_branch.messages.copy(),
                                      service=base_branch.service,
                                      llmconfig=base_branch.llmconfig,
                                      datalogger=base_branch.datalogger)
            branch.context = shared_context
            branch.context_log = shared_context_log
            self.branches[branch.id_] = branch
            self.mail_manager.add_sources([branch])
            node_mail = BaseMail(sender_id=self.mail_transfer.id_,
                                 recipient_id=branch.id_,
                                 category="node",
                                 package={"request_source": source_branch_id, "package": node_list[i]})
            self.mail_transfer.pending_outs.append(node_mail)

    async def execute(self, refresh_time=1):
        while not self.execute_stop:
            self.transfer_ins()
            self.transfer_outs()
            self.mail_manager.collect_all()
            self.mail_manager.send_all()
            tasks = [branch.forward() for branch in self.branches.values() if branch.pending_ins]
            await asyncio.gather(*tasks)
            await asyncio.sleep(refresh_time)


class MailTransder(BaseRelatableNode):
    def __init__(self):
        super().__init__()
        self.pending_ins = {}
        self.pending_outs = deque()