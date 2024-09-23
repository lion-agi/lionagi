from lion_core.session.session import Session as CoreSession
from lionagi.core.session.branch import Branch
from lionagi.core.generic.pile import pile, Pile
from lionagi.libs.sys_util import SysUtil


class Session(CoreSession):
    branches: Pile[Branch] = pile()

    def delete_branch(self, branch):
        """
        Deletes a branch from the session.

        Args:
            branch (Branch | str): The branch or its ID to delete.
        """
        branch_id = SysUtil.get_id(branch)
        self.branches.pop(branch_id)
        self.mail_manager.delete_source(branch_id)

        if self.default_branch == branch:
            if self.branches.size() == 0:
                self.default_branch = None
            else:
                self.default_branch = self.branches[0]

    async def chat(self, *args, branch=None, **kwargs):
        """
        Initiates a chat interaction with a branch.

        Args:
            *args: Positional arguments to pass to the chat method.
            branch (Branch, optional): The branch to chat with. Defaults to the default branch.
            **kwargs: Keyword arguments to pass to the chat method.

        Returns:
            Any: The result of the chat interaction.

        Raises:
            ValueError: If the specified branch is not found in the session branches.
        """
        if branch is None:
            branch = self.default_branch
        if branch not in self.branches:
            raise ValueError("Branch not found in session branches")
        return await self.branches[branch].chat(*args, **kwargs)

    async def direct(self, *args, branch=None, **kwargs):
        """
        Initiates a direct interaction with a branch.

        Args:
            *args: Positional arguments to pass to the direct method.
            branch (Branch, optional): The branch to interact with. Defaults to the default branch.
            **kwargs: Keyword arguments to pass to the direct method.

        Returns:
            Any: The result of the direct interaction.

        Raises:
            ValueError: If the specified branch is not found in the session branches.
        """
        if branch is None:
            branch = self.default_branch
        if branch not in self.branches:
            raise ValueError("Branch not found in session branches")
        return await self.branches[branch].direct(*args, **kwargs)
