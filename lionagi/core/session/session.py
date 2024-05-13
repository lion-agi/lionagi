from ..generic.abc import Component
from ..generic import (
    Pile,
    Progression,
    Flow,
    progression,
    pile,
    flow,
    iModel,
    DataLogger,
)
from ..message import System
from lionagi.libs.ln_api import BaseService
from typing import Any, Tuple
from ..action.tool import Tool, TOOL_TYPE
from ..action.tool_manager import ToolManager

from lionagi.libs import SysUtil


class Session:

    def __init__(
        self,
        system=None,  # the default system message node for the session
        model=None,
        datalogger=None,
        persist_path=None,
    ):

        self.ln_id = SysUtil.create_id()
        self.timestamp = SysUtil.get_timestamp(sep=None)[:-6]
        self.system = system or System(
            system="You are a helpful assistant.",
            sender=self.ln_id,
            recipient="assistant",
        )
        self.model = model or iModel()
        self.datalogger = datalogger or DataLogger(persist_path)


class Session:

    def __init__(
        self,
        system: dict | list | System | None = None,
        sender: str | None = None,
        llmconfig: dict[str, str | int | dict] | None = None,
        service: BaseService | None = None,
        branches: dict[str, Branch] | None = None,
        default_branch: Branch | None = None,
        default_branch_name: str | None = None,
        tools: TOOL_TYPE | None = None,
        # instruction_sets: Optional[List[Instruction]] = None,
        tool_manager: ToolManager | None = None,
        messages: dataframe.ln_DataFrame | None = None,
        datalogger: None | DataLogger = None,
        persist_path: Path | str | None = None,
    ):
        self.branches = branches if isinstance(branches, dict) else {}
        self.service = service
        self.setup_default_branch(
            system=system,
            sender=sender,
            default_branch=default_branch,
            default_branch_name=default_branch_name,
            messages=messages,
            # instruction_sets=instruction_sets,
            tool_manager=tool_manager,
            service=service,
            llmconfig=llmconfig,
            tools=tools,
            persist_path=persist_path,
            datalogger=datalogger,
        )
        self.mail_manager = MailManager(self.branches)
        self.datalogger = self.default_branch.datalogger
        for key, branch in self.branches.items():
            branch.name = key

    # ---- branch manipulation ---- #
    def new_branch(
        self,
        branch_name: str,
        system: dict | list | System | None = None,
        sender: str | None = None,
        messages: dataframe.ln_DataFrame | None = None,
        tool_manager=None,
        service=None,
        llmconfig=None,
        tools: TOOL_TYPE = False,
    ) -> None:
        """Create a new branch with the specified configurations.

        Args:
                branch_name (str | None): Name of the new branch.
                system (Optional[Union[System, str]]): System or context identifier for the new branch.
                sender (str | None): Default sender identifier for the new branch.
                messages (Optional[dataframe.ln_DataFrame]): Initial set of messages for the new branch.
                instruction_sets (Optional[Any]): Instruction sets for the new branch.
                tool_manager (Optional[Any]): Tool manager for handling tools in the new branch.
                service (BaseService]): External service instance for the ne | None branch.
                llmconfig (dict[str, Any] | None): Configuration for language learning models in the new branch.
                tools (TOOL_TYPE | None): List of tools available for the new branch.

        Raises:
                ValueError: If the branch name already exists.

        Examples:
                >>> session.new_branch("new_branch_name")
        """
        if branch_name in self.branches.keys():
            raise ValueError(
                f"Invalid new branch name {branch_name}. Branch already existed."
            )
        if isinstance(tools, Tool):
            tools = [tools]
        new_branch = Branch(
            name=branch_name,
            messages=messages,
            tool_manager=tool_manager,
            service=service,
            llmconfig=llmconfig,
            tools=tools,
        )
        if system:
            new_branch.add_message(system=system, sender=sender)

        self.branches[branch_name] = new_branch
        self.mail_manager.sources[branch_name] = new_branch
        self.mail_manager.mails[branch_name] = {}

    def get_branch(
        self, branch: Branch | str | None = None, get_name: bool = False
    ) -> Branch | Tuple[Branch, str]:
        """
        Retrieve a branch by name or instance.

        Args:
                branch (Optional[Branch | str]): The branch name or instance to retrieve.
                get_name (bool): If True, returns a tuple of the branch instance and its name.

        Returns:
                Union[Branch, Tuple[Branch, str]]: The branch instance or a tuple of the branch instance and its name.

        Raises:
                ValueError: If the branch name does not exist or the branch input is invalid.

        Examples:
                >>> branch_instance = session.get_branch("existing_branch_name")
                >>> branch_instance, branch_name = session.get_branch("existing_branch_name", get_name=True)
        """
        if isinstance(branch, str):
            if branch not in self.branches.keys():
                raise ValueError(f"Invalid branch name {branch}. Not exist.")
            return (
                (self.branches[branch], branch) if get_name else self.branches[branch]
            )
        elif isinstance(branch, Branch) and branch in self.branches.values():
            return (branch, branch.name) if get_name else branch
        elif branch is None:
            if get_name:
                return self.default_branch, self.default_branch_name
            return self.default_branch

        else:
            raise ValueError(f"Invalid branch input {branch}.")

    def change_default_branch(self, branch: str | Branch) -> None:
        """Change the default branch of the session.

        Args:
                branch (str | Branch): The branch name or instance to set as the new default.

        Examples:
                >>> session.change_default_branch("new_default_branch")
        """
        branch_, name_ = self.get_branch(branch, get_name=True)
        self.default_branch = branch_
        self.default_branch_name = name_

    def delete_branch(self, branch: Branch | str, verbose: bool = True) -> bool:
        """Delete a branch from the session.

        Args:
                branch (Branch | str): The branch name or instance to delete.
                verbose (bool): If True, prints a message upon deletion.

        Returns:
                bool: True if the branch was successfully deleted.

        Raises:
                ValueError: If attempting to delete the current default branch.

        Examples:
                >>> session.delete_branch("branch_to_delete")
        """
        _, branch_name = self.get_branch(branch, get_name=True)

        if branch_name == self.default_branch_name:
            raise ValueError(
                f"{branch_name} is the current default branch, please switch to another branch before delete it."
            )
        self.branches.pop(branch_name)
        # self.mail_manager.sources.pop(branch_name)
        self.mail_manager.mails.pop(branch_name)
        if verbose:
            print(f"Branch {branch_name} is deleted.")
        return True

    def merge_branch(
        self,
        from_: str | Branch,
        to_branch: str | Branch,
        update: bool = True,
        del_: bool = False,
    ) -> None:
        """Merge messages and settings from one branch to another.

        Args:
                from_ (str | Branch): The source branch name or instance.
                to_branch (str | Branch): The target branch name or instance where the merge will happen.
                update (bool): If True, updates the target branch with the source branch's settings.
                del_ (bool): If True, deletes the source branch after merging.

        Examples:
                >>> session.merge_branch("source_branch", "target_branch", del_=True)
        """
        from_ = self.get_branch(branch=from_)
        to_branch, to_name = self.get_branch(branch=to_branch, get_name=True)
        to_branch.merge_branch(from_, update=update)

        if del_:
            if from_ == self.default_branch:
                self.default_branch_name = to_name
                self.default_branch = to_branch
            self.delete_branch(from_, verbose=False)

    def take_branch(self, branch):
        self.branches[branch.branch_name] = branch
        self.mail_manager.sources[branch.id_] = branch
        self.mail_manager.mails[branch.id_] = {}

    def collect(self, from_: str | Branch | list[str | Branch] | None = None):
        """
        Collects requests from specified branches or from all branches if none are specified.

        This method is intended to aggregate data or requests from one or more branches for processing or analysis.

        Args:
                from_ (Optional[Union[str, Branch, List[str | Branch]]]): The branch(es) from which to collect requests.
                        Can be a single branch name, a single branch instance, a list of branch names, a list of branch instances, or None.
                        If None, requests are collected from all branches.

        Examples:
                >>> session.collect("branch_name")
                >>> session.collect([branch_instance_1, "branch_name_2"])
                >>> session.collect()  # Collects from all branches
        """
        if from_ is None:
            for branch in self.branches.values():
                self.mail_manager.collect(branch.id_)
        else:
            if not isinstance(from_, list):
                from_ = [from_]
            for branch in from_:
                if isinstance(branch, str):
                    branch = self.branches[branch]
                    self.mail_manager.collect(branch.id_)
                elif isinstance(branch, Branch):
                    self.mail_manager.collect(branch.id_)

    def send(self, to_: str | Branch | list[str | Branch] | None = None):
        """
        Sends requests or data to specified branches or to all branches if none are specified.

        This method facilitates the distribution of data or requests to one or more branches, potentially for further tool or processing.

        Args:
                to_ (Optional[Union[str, Branch, List[str | Branch]]]): The target branch(es) to which to send requests.
                        Can be a single branch name, a single branch instance, a list of branch names, a list of branch instances, or None.
                        If None, requests are sent to all branches.

        Examples:
                >>> session.send("target_branch")
                >>> session.send([branch_instance_1, "target_branch_2"])
                >>> session.send()  # Sends to all branches
        """
        if to_ is None:
            for branch in self.branches.values():
                self.mail_manager.send(branch.id_)
        else:
            if not isinstance(to_, list):
                to_ = [to_]
            for branch in to_:
                if isinstance(branch, str):
                    branch = self.branches[branch]
                    self.mail_manager.send(branch.id_)
                if isinstance(branch, Branch):
                    self.mail_manager.send(branch.id_)

    def collect_send_all(self, receive_all=False):
        """
        Collects and sends requests across all branches, optionally invoking a receive operation on each branch.

        This method is a convenience function for performing a full cycle of collect and send operations across all branches,
        useful in scenarios where data or requests need to be aggregated and then distributed uniformly.

        Args:
                receive_all (bool): If True, triggers a `receive_all` method on each branch after sending requests,
                        which can be used to process or acknowledge the received data.

        Examples:
                >>> session.collect_send_all()
                >>> session.collect_send_all(receive_all=True)
        """
        self.collect()
        self.send()
        if receive_all:
            for branch in self.branches.values():
                branch.receive_all()

    def setup_default_branch(self, **kwargs):
        self._setup_default_branch(**kwargs)
        self._verify_default_branch()

    def _verify_default_branch(self):
        if self.branches:
            if self.default_branch_name not in self.branches.keys():
                raise ValueError("default branch name is not in imported branches")
            if self.default_branch is not self.branches[self.default_branch_name]:
                raise ValueError(
                    f"default branch does not match Branch object under {self.default_branch_name}"
                )

        if not self.branches:
            self.branches[self.default_branch_name] = self.default_branch

    def _setup_default_branch(
        self,
        system,
        sender,
        default_branch,
        default_branch_name,
        messages,  # instruction_sets,
        tool_manager,
        service,
        llmconfig,
        tools,
        persist_path,
        datalogger,
    ):

        branch = default_branch or Branch(
            name=default_branch_name,
            service=service,
            llmconfig=llmconfig,
            tools=tools,
            tool_manager=tool_manager,
            # instruction_sets=instruction_sets,
            messages=messages,
            persist_path=persist_path,
            datalogger=datalogger,
        )

        self.default_branch = branch
        self.default_branch_name = default_branch_name or "main"
        if system:
            self.default_branch.add_message(system=system, sender=sender)

        self.llmconfig = self.default_branch.llmconfig
