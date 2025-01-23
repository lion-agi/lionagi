from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GithubAction(str, Enum):
    """
    Local Git or GitHub API calls:
      - 'list_repos': Show user GH repos
      - 'clone_repo': Clone a remote repo locally
      - 'create_branch': New branch locally
      - 'checkout_branch': Switch branch
      - 'commit_push': Stage & commit local changes, push to remote
      - 'open_pull_request': Create new PR
      - 'list_prs': List open PRs
      - 'merge_pr': Merge or close a PR
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
    Request for GithubTool, describing local or remote git ops.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "GithubTool: For local Git commands and GitHub API tasks. "
                "Use 'repo_url' for remote repos, 'local_path' for local repo dir."
            )
        }
    )

    action: GithubAction

    github_token: Optional[str] = Field(
        None, description="Personal GH token if needed for GH API calls."
    )
    repo_url: Optional[str] = Field(
        None,
        description="For 'clone_repo' or referencing GH repo. E.g. 'https://github.com/user/repo.git'.",
    )
    local_path: Optional[str] = Field(
        None,
        description="For local Git commands, the local repo path on disk.",
    )
    branch_name: Optional[str] = Field(
        None,
        description="For 'create_branch','checkout_branch'. The branch name.",
    )
    commit_message: Optional[str] = Field(
        None, description="For 'commit_push'. The commit message."
    )
    files_to_commit: Optional[List[str]] = Field(
        None, description="For 'commit_push'. If None, stage all changes."
    )
    base_branch: Optional[str] = Field(
        None,
        description="For 'open_pull_request'. The base branch (e.g. 'main').",
    )
    pr_title: Optional[str] = Field(
        None, description="For 'open_pull_request'. The new PR's title."
    )
    pr_body: Optional[str] = Field(
        None, description="For 'open_pull_request'. The PR body."
    )
    pr_number: Optional[int] = Field(
        None,
        description="For 'merge_pr' or 'list_prs'. The PR # if filtering or merging.",
    )


class RepoInfo(BaseModel):
    name: str
    full_name: str
    private: bool
    url: str


class PRInfo(BaseModel):
    number: int
    title: str
    user: str
    url: str


class GithubResponse(BaseModel):
    """
    Response from GithubTool.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "GithubTool Response: Contains local Git outputs or GH API results (repos, PR info, etc.)."
            )
        }
    )

    success: bool
    error: Optional[str] = Field(
        None, description="If success=False, reason for failure."
    )
    output: Optional[str] = None
    repos: Optional[List[RepoInfo]] = None
    prs: Optional[List[PRInfo]] = None
    pr_url: Optional[str] = None
