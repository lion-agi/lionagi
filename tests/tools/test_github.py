from pathlib import Path

import pytest

from lionagi.tools.providers.gh_ import (
    GithubAction,
    GithubRequest,
    GithubTool,
    PRInfo,
    RepoInfo,
)


@pytest.fixture
def github_tool(mock_github_client, mock_git_command, temp_dir):
    """Initialize GithubTool with mocked dependencies."""
    return GithubTool(github_token="mock-token")


def test_list_repos(github_tool, mock_github_client):
    """Test listing repositories."""
    # Setup mock repos
    mock_repo = (
        mock_github_client.get_user.return_value.get_repos.return_value
    ) = [
        type(
            "MockRepo",
            (),
            {
                "name": "test-repo",
                "full_name": "user/test-repo",
                "private": False,
                "html_url": "https://github.com/user/test-repo",
            },
        )
    ]

    request = GithubRequest(action=GithubAction.list_repos)
    response = github_tool.handle_request(request)

    assert response.success
    assert response.repos is not None
    assert len(response.repos) == 1
    assert response.repos[0].name == "test-repo"
    assert response.repos[0].full_name == "user/test-repo"
    assert not response.repos[0].private


def test_clone_repo(github_tool, temp_dir):
    """Test cloning a repository."""
    request = GithubRequest(
        action=GithubAction.clone_repo,
        repo_url="https://github.com/user/test-repo.git",
        local_path=str(temp_dir / "test-repo"),
    )
    response = github_tool.handle_request(request)

    assert response.success
    assert response.output is not None


def test_branch_operations(github_tool, temp_dir):
    """Test branch creation and checkout."""
    repo_path = temp_dir / "test-repo"

    # Create branch
    create_request = GithubRequest(
        action=GithubAction.create_branch,
        local_path=str(repo_path),
        branch_name="feature/test",
    )
    create_response = github_tool.handle_request(create_request)
    assert create_response.success

    # Checkout branch
    checkout_request = GithubRequest(
        action=GithubAction.checkout_branch,
        local_path=str(repo_path),
        branch_name="feature/test",
    )
    checkout_response = github_tool.handle_request(checkout_request)
    assert checkout_response.success


def test_commit_push(github_tool, temp_dir):
    """Test commit and push operations."""
    repo_path = temp_dir / "test-repo"

    request = GithubRequest(
        action=GithubAction.commit_push,
        local_path=str(repo_path),
        commit_message="Test commit",
        files_to_commit=["test.txt"],
    )
    response = github_tool.handle_request(request)

    assert response.success
    assert response.output is not None


def test_pull_request_operations(github_tool, mock_github_client):
    """Test pull request operations."""
    # Setup mock PR
    mock_pr = type(
        "MockPR",
        (),
        {
            "number": 1,
            "title": "Test PR",
            "user": type("MockUser", (), {"login": "test-user"}),
            "html_url": "https://github.com/user/test-repo/pull/1",
        },
    )
    mock_github_client.get_repo.return_value.get_pulls.return_value = [mock_pr]

    # Test opening PR
    open_request = GithubRequest(
        action=GithubAction.open_pull_request,
        repo_url="https://github.com/user/test-repo",
        branch_name="feature/test",
        base_branch="main",
        pr_title="Test PR",
        pr_body="Test PR description",
    )
    open_response = github_tool.handle_request(open_request)
    assert open_response.success

    # Test listing PRs
    list_request = GithubRequest(
        action=GithubAction.list_prs,
        repo_url="https://github.com/user/test-repo",
    )
    list_response = github_tool.handle_request(list_request)
    assert list_response.success
    assert list_response.prs is not None
    assert len(list_response.prs) == 1
    assert list_response.prs[0].number == 1

    # Test merging PR
    merge_request = GithubRequest(
        action=GithubAction.merge_pr,
        repo_url="https://github.com/user/test-repo",
        pr_number=1,
    )
    merge_response = github_tool.handle_request(merge_request)
    assert merge_response.success


def test_error_handling(github_tool, mock_github_client):
    """Test error handling for various scenarios."""
    # Test missing token
    tool_no_token = GithubTool()
    request = GithubRequest(action=GithubAction.list_repos)
    response = tool_no_token.handle_request(request)
    assert not response.success
    assert response.error is not None

    # Test invalid repo URL
    clone_request = GithubRequest(
        action=GithubAction.clone_repo,
        repo_url="invalid-url",
        local_path="/tmp/test",
    )
    response = github_tool.handle_request(clone_request)
    assert not response.success
    assert response.error is not None

    # Test missing required fields
    pr_request = GithubRequest(
        action=GithubAction.open_pull_request,
        repo_url="https://github.com/user/test-repo",
        # Missing required fields
    )
    response = github_tool.handle_request(pr_request)
    assert not response.success
    assert response.error is not None

    # Test API errors
    mock_github_client.get_user.side_effect = Exception("API Error")
    request = GithubRequest(action=GithubAction.list_repos)
    response = github_tool.handle_request(request)
    assert not response.success
    assert response.error is not None


def test_local_git_operations_error_handling(github_tool, mocker):
    """Test error handling for local git operations."""
    # Mock git command to fail
    mocker.patch(
        "lionagi.tools.providers.gh_.run_git_command",
        return_value=("Error output", 1),
    )

    request = GithubRequest(
        action=GithubAction.create_branch,
        local_path="/tmp/test",
        branch_name="feature/test",
    )
    response = github_tool.handle_request(request)

    assert not response.success
    assert response.error is not None
