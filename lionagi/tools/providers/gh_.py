import logging
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from lionagi.operatives.action.tool import Tool

from ..base import LionTool


def run_git_command(
    args: list[str], cwd: Path | None = None
) -> tuple[str, int]:
    """
    Run a git command (e.g. ["git", "clone", ...]) in the specified working directory.
    Returns (combined_stdout_stderr, exit_code).
    """
    import subprocess

    proc = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd
    )
    out, _ = proc.communicate()
    return out.decode("utf-8"), proc.returncode


class GithubAction(str, Enum):
    """
    Enumerates common GitHub/Git actions:
      - 'list_repos': List the user's repositories on GitHub
      - 'clone_repo': Clone a repository locally using 'git clone'
      - 'create_branch': Create a new branch locally (e.g. 'git checkout -b')
      - 'checkout_branch': Switch to an existing branch locally
      - 'commit_push': Stage files, commit, and push changes to remote
      - 'open_pull_request': Open a new pull request via GitHub API
      - 'list_prs': List open pull requests via GitHub API
      - 'merge_pr': Merge (or close) an existing pull request via GitHub API
    """

    list_repos = "list_repos"
    clone_repo = "clone_repo"
    create_branch = "create_branch"
    checkout_branch = "checkout_branch"
    commit_push = "commit_push"
    open_pull_request = "open_pull_request"
    list_prs = "list_prs"
    merge_pr = "merge_pr"


class GithubRequest(BaseModel):
    """
    The input model for the GitHubTool. Depending on 'action', different fields apply.
    """

    action: GithubAction = Field(
        ...,
        description=(
            "Which GitHub operation to perform:\n"
            "- 'list_repos'\n"
            "- 'clone_repo'\n"
            "- 'create_branch'\n"
            "- 'checkout_branch'\n"
            "- 'commit_push'\n"
            "- 'open_pull_request'\n"
            "- 'list_prs'\n"
            "- 'merge_pr'"
        ),
    )

    github_token: str | None = Field(
        None,
        description=(
            "GitHub personal access token, required for certain API calls (list_repos, open_pull_request, etc.). "
            "If not needed for local Git ops, this can be omitted."
        ),
    )

    # Common fields
    repo_url: str | None = Field(
        None,
        description=(
            "For clone_repo, or if referencing a GitHub repo (e.g. 'https://github.com/user/repo.git')."
        ),
    )
    local_path: str | None = Field(
        None,
        description=(
            "Local filesystem path to operate in (e.g., clone destination or existing repo path)."
        ),
    )
    branch_name: str | None = Field(
        None,
        description=(
            "Name of the branch to create or checkout. Required for create_branch/checkout_branch."
        ),
    )
    commit_message: str | None = Field(
        None,
        description=("Commit message if action='commit_push'."),
    )
    files_to_commit: list[str] | None = Field(
        None,
        description=(
            "List of file paths to stage if action='commit_push'. If omitted, all changes are committed."
        ),
    )

    # For pull requests
    base_branch: str | None = Field(
        None,
        description=(
            "The base branch (e.g. 'main') if opening or merging a PR."
        ),
    )
    pr_title: str | None = Field(
        None,
        description=(
            "Title of the pull request if action='open_pull_request'."
        ),
    )
    pr_body: str | None = Field(
        None,
        description=(
            "Body/description of the pull request if action='open_pull_request'."
        ),
    )
    pr_number: int | None = Field(
        None,
        description=(
            "Pull request number if action='merge_pr', 'list_prs' (filter?), etc."
        ),
    )


class RepoInfo(BaseModel):
    """
    Minimal metadata about a GitHub repository.
    """

    name: str
    full_name: str
    private: bool
    url: str


class PRInfo(BaseModel):
    """
    Minimal metadata about a GitHub pull request.
    """

    number: int
    title: str
    user: str
    url: str


class GithubResponse(BaseModel):
    """
    The structured response from the GitHubTool, depending on the action.
    """

    success: bool = Field(
        ...,
        description="Indicates whether the requested GitHub action was successful.",
    )
    error: str | None = Field(
        None,
        description="If success=False, this describes the error or failure reason.",
    )

    # For local git actions (clone_repo, create_branch, checkout_branch, commit_push):
    output: str | None = Field(
        None,
        description=(
            "Any combined stdout/stderr from local git commands if applicable."
        ),
    )

    # For list_repos
    repos: list[RepoInfo] | None = Field(
        None,
        description="Populated if action='list_repos' succeeded, listing the user's repositories.",
    )

    # For list_prs
    prs: list[PRInfo] | None = Field(
        None,
        description="Populated if action='list_prs' succeeded, listing open pull requests.",
    )

    # For open_pull_request
    pr_url: str | None = Field(
        None,
        description=(
            "If action='open_pull_request' succeeded, URL of the newly created PR."
        ),
    )


class GithubTool(LionTool):
    """
    A tool for basic Git/GitHub operations.
    - local Git commands with run_git_command
    - optional GitHub API calls with PyGithub or direct REST
    """

    is_lion_system_tool = True
    system_tool_name = "github_tool"

    from lionagi.libs.package.imports import check_import

    Github = check_import("github", import_name="Github", pip_name="PyGithub")

    def __init__(self, github_token: str | None = None):
        super().__init__()
        self.github_token = github_token
        if github_token:
            self.client = GithubTool.Github(github_token)
        else:
            self.client = None
        self._tool = None

    def handle_request(self, request: GithubRequest) -> GithubResponse:
        if isinstance(request, dict):
            request = GithubRequest(**request)

        action = request.action
        if action == GithubAction.list_repos:
            return self._list_repos(request)
        elif action == GithubAction.clone_repo:
            return self._clone_repo(request)
        elif action == GithubAction.create_branch:
            return self._create_branch(request)
        elif action == GithubAction.checkout_branch:
            return self._checkout_branch(request)
        elif action == GithubAction.commit_push:
            return self._commit_push(request)
        elif action == GithubAction.open_pull_request:
            return self._open_pull_request(request)
        elif action == GithubAction.list_prs:
            return self._list_prs(request)
        elif action == GithubAction.merge_pr:
            return self._merge_pr(request)

        return GithubResponse(success=False, error="Unknown action")

    # ----------------------------------
    # LOCAL GIT COMMANDS
    # ----------------------------------

    def _clone_repo(self, request: GithubRequest) -> GithubResponse:
        if not request.repo_url or not request.local_path:
            return GithubResponse(
                success=False, error="repo_url and local_path are required"
            )

        cmd = ["git", "clone", request.repo_url, request.local_path]
        out, code = run_git_command(cmd)
        if code != 0:
            return GithubResponse(success=False, error=out)
        return GithubResponse(success=True, output=out)

    def _create_branch(self, request: GithubRequest) -> GithubResponse:
        if not request.local_path or not request.branch_name:
            return GithubResponse(
                success=False, error="local_path and branch_name are required"
            )
        cmd = ["git", "checkout", "-b", request.branch_name]
        out, code = run_git_command(cmd, cwd=Path(request.local_path))
        if code != 0:
            return GithubResponse(success=False, error=out)
        return GithubResponse(success=True, output=out)

    def _checkout_branch(self, request: GithubRequest) -> GithubResponse:
        if not request.local_path or not request.branch_name:
            return GithubResponse(
                success=False, error="local_path and branch_name are required"
            )
        cmd = ["git", "checkout", request.branch_name]
        out, code = run_git_command(cmd, cwd=Path(request.local_path))
        if code != 0:
            return GithubResponse(success=False, error=out)
        return GithubResponse(success=True, output=out)

    def _commit_push(self, request: GithubRequest) -> GithubResponse:
        if not request.local_path or not request.commit_message:
            return GithubResponse(
                success=False,
                error="local_path and commit_message are required",
            )

        cwd = Path(request.local_path)
        if request.files_to_commit:
            cmd_add = ["git", "add"] + request.files_to_commit
        else:
            cmd_add = ["git", "add", "--all"]
        out_add, code_add = run_git_command(cmd_add, cwd=cwd)
        if code_add != 0:
            return GithubResponse(success=False, error=out_add)

        cmd_commit = ["git", "commit", "-m", request.commit_message]
        out_commit, code_commit = run_git_command(cmd_commit, cwd=cwd)
        if code_commit != 0:
            return GithubResponse(success=False, error=out_commit)

        cmd_push = ["git", "push", "origin", "HEAD"]
        out_push, code_push = run_git_command(cmd_push, cwd=cwd)
        if code_push != 0:
            return GithubResponse(success=False, error=out_push)

        combined = f"{out_add}\n{out_commit}\n{out_push}"
        return GithubResponse(success=True, output=combined)

    # ----------------------------------
    # GITHUB API CALLS
    # ----------------------------------

    def _list_repos(self, request: GithubRequest) -> GithubResponse:
        if not self.client:
            return GithubResponse(
                success=False,
                error="GitHub client not initialized (no token).",
            )

        try:
            user = self.client.get_user()
            repos_data = []
            for repo in user.get_repos():
                repos_data.append(
                    RepoInfo(
                        name=repo.name,
                        full_name=repo.full_name,
                        private=repo.private,
                        url=repo.html_url,
                    )
                )
            return GithubResponse(success=True, repos=repos_data)
        except Exception as e:
            return GithubResponse(success=False, error=str(e))

    def _open_pull_request(self, request: GithubRequest) -> GithubResponse:
        if not self.client:
            return GithubResponse(
                success=False, error="GitHub client not initialized."
            )
        if (
            not request.repo_url
            or not request.branch_name
            or not request.base_branch
            or not request.pr_title
        ):
            return GithubResponse(
                success=False,
                error="repo_url, branch_name, base_branch, pr_title required",
            )

        full_name = request.repo_url.replace(
            "https://github.com/", ""
        ).replace(".git", "")
        try:
            repo = self.client.get_repo(full_name)
            pr = repo.create_pull(
                title=request.pr_title,
                body=request.pr_body or "",
                head=request.branch_name,
                base=request.base_branch,
            )
            return GithubResponse(success=True, pr_url=pr.html_url)
        except Exception as e:
            logging.error(f"Error creating PR: {e}")
            return GithubResponse(success=False, error=str(e))

    def _list_prs(self, request: GithubRequest) -> GithubResponse:
        if not self.client:
            return GithubResponse(
                success=False, error="GitHub client not initialized."
            )
        if not request.repo_url:
            return GithubResponse(success=False, error="repo_url required")

        full_name = request.repo_url.replace(
            "https://github.com/", ""
        ).replace(".git", "")
        try:
            repo = self.client.get_repo(full_name)
            open_prs = repo.get_pulls(state="open")
            data = []
            for pr in open_prs:
                data.append(
                    PRInfo(
                        number=pr.number,
                        title=pr.title,
                        user=pr.user.login,
                        url=pr.html_url,
                    )
                )
            return GithubResponse(success=True, prs=data)
        except Exception as e:
            return GithubResponse(success=False, error=str(e))

    def _merge_pr(self, request: GithubRequest) -> GithubResponse:
        if not self.client:
            return GithubResponse(
                success=False, error="GitHub client not initialized."
            )
        if not request.repo_url or not request.pr_number:
            return GithubResponse(
                success=False, error="repo_url and pr_number required"
            )

        full_name = request.repo_url.replace(
            "https://github.com/", ""
        ).replace(".git", "")
        try:
            repo = self.client.get_repo(full_name)
            pull = repo.get_pull(request.pr_number)
            res = pull.merge()
            return GithubResponse(success=True, output=str(res))
        except Exception as e:
            return GithubResponse(success=False, error=str(e))

    def to_tool(self):
        if self._tool is None:

            def github_tool(**kwargs):
                """
                Unified tool interface for GitHub operations.
                """
                return self.handle_request(
                    GithubRequest(**kwargs)
                ).model_dump()

            if self.system_tool_name != "github_tool":
                github_tool.__name__ = self.system_tool_name

            self._tool = Tool(
                func_callable=github_tool,
                request_options=GithubRequest,
            )
        return self._tool
