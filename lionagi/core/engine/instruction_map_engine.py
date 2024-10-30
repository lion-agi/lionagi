import asyncio

from pydantic import Field

from lionagi.core.collections import Exchange, Pile, pile, progression
from lionagi.core.engine.branch_engine import BranchExecutor
from lionagi.core.executor.base_executor import BaseExecutor
from lionagi.core.mail.mail import Mail, Package
from lionagi.core.mail.mail_manager import MailManager


class InstructionMapEngine(BaseExecutor):
    """
    Manages the execution of a mapped set of instructions across multiple branches within an executable structure.

    Attributes:
        branches (dict[str, BranchExecutor]): A dictionary of branch executors managing individual instruction flows.
        structure_id (str): The identifier for the structure within which these branches operate.
        mail_transfer (Exchange): Handles the transfer of mail between branches and other components.
        branch_kwargs (dict): Keyword arguments used for initializing branches.
        num_end_branches (int): Tracks the number of branches that have completed execution.
        mail_manager (MailManager): Manages the distribution and collection of mails across branches.
    """

    branches: Pile[BranchExecutor] = Field(
        default_factory=dict,
        description="The branches of the instruction mapping.",
    )
    structure_id: str = Field(
        "", description="The ID of the executable structure."
    )
    mail_transfer: Exchange = Field(
        default_factory=Exchange, description="The mail transfer."
    )
    branch_kwargs: dict = Field(
        default_factory=dict,
        description="The keyword arguments for the initializing the branches.",
    )
    num_end_branches: int = Field(0, description="The number of end branches.")
    mail_manager: MailManager = Field(
        default_factory=MailManager, description="The mail manager."
    )

    def __init__(self, **kwargs):
        """
        Initializes an InstructionMapExecutor with the given parameters.

        Args:
            **kwargs: Arbitrary keyword arguments passed to the base executor and used for initializing branch executors.
        """
        super().__init__(**kwargs)
        self.mail_manager = MailManager([self.mail_transfer])

    def transfer_ins(self):
        """
        Processes incoming mails, directing them appropriately based on their categories, and handles the initial setup
        of branches or the routing of node and condition mails.
        """
        for key in list(self.mailbox.pending_ins.keys()):
            while self.mailbox.pending_ins[key].size() > 0:
                mail_id = self.mailbox.pending_ins[key].popleft()
                mail = self.mailbox.pile.pop(mail_id)
                if mail.category == "start":
                    self._process_start(mail)
                elif mail.category == "node_list":
                    self._process_node_list(mail)
                elif (
                    (mail.category == "node")
                    or (mail.category == "condition")
                    or (mail.category == "end")
                ):
                    mail.sender = self.mail_transfer.ln_id
                    mail.recipient = mail.package.request_source
                    self.mail_transfer.include(mail, "out")

    def transfer_outs(self):
        """
        Processes outgoing mails from the central mail transfer, handling end-of-execution notifications and routing
        other mails to appropriate recipients.
        """
        for key in list(self.mail_transfer.pending_ins.keys()):
            while self.mail_transfer.pending_ins[key].size() > 0:
                mail_id = self.mail_transfer.pending_ins[key].popleft()
                mail = self.mail_transfer.pile.pop(mail_id)
                if mail.category == "end":
                    self.num_end_branches += 1
                    if self.num_end_branches == len(
                        self.branches
                    ):  # tell when structure should stop
                        mail.sender = self.ln_id
                        mail.recipient = self.structure_id
                        self.mailbox.include(mail, "out")
                        self.execute_stop = True
                else:
                    mail.sender = self.ln_id
                    mail.recipient = self.structure_id
                    self.mailbox.include(mail, "out")

    def _process_start(self, start_mail: Mail):
        """
        Processes a start mail to initialize a new branch executor and configures it based on the mail's package content.

        Args:
            start_mail (BaseMail): The mail initiating the start of a new branch execution.
        """
        branch = BranchExecutor(verbose=self.verbose, **self.branch_kwargs)
        branch.context = start_mail.package.package["context"]
        self.branches[branch.ln_id] = branch
        self.mail_manager.add_sources([branch])
        self.structure_id = start_mail.package.package["structure_id"]

        pack = Package(
            category="start", package="start", request_source=branch.ln_id
        )
        mail = Mail(
            sender=self.ln_id,
            recipient=self.structure_id,
            package=pack,
        )
        self.mailbox.include(mail, "out")

    def _process_node_list(self, nl_mail: Mail):
        """
        Processes a node list mail, setting up new branches or propagating the execution context based on the node list
        provided in the mail.

        Args:
            nl_mail (BaseMail): The mail containing a list of nodes to be processed in subsequent branches.
        """
        source_branch_id = nl_mail.package.request_source
        node_list = nl_mail.package.package
        shared_context = self.branches[source_branch_id].context
        shared_context_log = self.branches[source_branch_id].context_log
        base_branch = self.branches[source_branch_id]

        pack = Package(
            category="node",
            package=node_list[0],
            request_source=source_branch_id,
        )
        mail = Mail(
            sender=self.mail_transfer.ln_id,
            recipient=source_branch_id,
            package=pack,
        )
        self.mail_transfer.include(mail, "out")

        for i in range(1, len(node_list)):
            system = base_branch.system.clone() if base_branch.system else None
            if system:
                system.sender = base_branch.ln_id
            progress = progression()
            messages = pile()

            for id_ in base_branch.progress:
                clone_message = base_branch.messages[id_].clone()
                progress.append(clone_message.ln_id)
                messages.append(clone_message)

            branch = BranchExecutor(
                verbose=self.verbose,
                messages=messages,
                user=base_branch.user,
                system=base_branch.system.clone(),
                progress=progress,
                imodel=base_branch.imodel,
            )
            for message in branch.messages:
                message.sender = base_branch.ln_id
                message.recipient = branch.ln_id

            branch.context = shared_context
            branch.context_log = shared_context_log
            self.branches[branch.ln_id] = branch
            self.mail_manager.add_sources([branch])
            node_pacakge = Package(
                category="node",
                package=node_list[i],
                request_source=source_branch_id,
            )
            node_mail = Mail(
                sender=self.mail_transfer.ln_id,
                recipient=branch.ln_id,
                package=node_pacakge,
            )
            self.mail_transfer.include(node_mail, "out")

    async def forward(self):
        """
        Forwards the execution by processing all incoming and outgoing mails and advancing the state of all active branches.
        """
        self.transfer_ins()
        self.transfer_outs()
        self.mail_manager.collect_all()
        self.mail_manager.send_all()
        tasks = [
            branch.forward()
            for branch in self.branches.values()
            if branch.mailbox.pending_ins
        ]
        await asyncio.gather(*tasks)
        return

    async def execute(self, refresh_time=1):
        """
        Continuously executes the forward process at specified intervals until instructed to stop.

        Args:
            refresh_time (int): The time in seconds between execution cycles.
        """
        while not self.execute_stop:
            await self.forward()
            await asyncio.sleep(refresh_time)
