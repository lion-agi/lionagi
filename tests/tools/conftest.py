import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from lionagi.tools.reader import ReaderResponse, SearchResult


# Common fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_text():
    """Sample text content for testing."""
    return "This is a test document.\nIt has multiple lines.\nFor testing purposes."


@pytest.fixture
def mock_document_converter(mocker, sample_text):
    """Mock DocumentConverter for reader.py"""
    mock_conv = MagicMock()
    mock_doc = MagicMock()
    mock_doc.export_to_markdown.return_value = sample_text
    mock_conv.convert.return_value.document = mock_doc
    mocker.patch(
        "lionagi.tools.reader.ReaderTool.DocumentConverter",
        return_value=mock_conv,
    )
    return mock_conv


@pytest.fixture
def mock_github_client(mocker):
    """Mock PyGithub client for gh_.py"""
    mock_client = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()

    # Setup mock user
    mock_user.get_repos.return_value = []
    mock_client.get_user.return_value = mock_user

    # Setup mock repo
    mock_repo.name = "test-repo"
    mock_repo.full_name = "user/test-repo"
    mock_repo.private = False
    mock_repo.html_url = "https://github.com/user/test-repo"

    # Setup PR operations
    mock_pr = MagicMock()
    mock_pr.number = 1
    mock_pr.title = "Test PR"
    mock_pr.user.login = "test-user"
    mock_pr.html_url = "https://github.com/user/test-repo/pull/1"
    mock_repo.create_pull.return_value = mock_pr
    mock_repo.get_pulls.return_value = [mock_pr]

    # Setup error cases
    mock_repo_func = MagicMock()

    def get_repo(full_name):
        if full_name == "invalid-url":
            raise Exception("Invalid repository")
        return mock_repo

    mock_repo_func.side_effect = get_repo
    mock_client.get_repo = mock_repo_func
    mock_client.get_user.return_value = mock_user

    mocker.patch(
        "lionagi.tools.providers.gh_.GithubTool.Github",
        return_value=mock_client,
    )
    return mock_client


@pytest.fixture
def mock_git_command(mocker):
    """Mock git command execution for gh_.py"""

    def mock_run(*args, **kwargs):
        if "invalid-url" in args[0]:
            return "Error: Invalid repository", 1
        return "Mock git output", 0

    mocker.patch(
        "lionagi.tools.providers.gh_.run_git_command", side_effect=mock_run
    )
    return mock_run


@pytest.fixture
def mock_e2b_sandbox(mocker):
    """Mock E2B sandbox for coder.py"""
    mock_sandbox = MagicMock()

    # Mock run_code
    mock_result = MagicMock()
    mock_result.stdout = "Result: 5\n"
    mock_result.stderr = ""
    mock_result.error = None
    mock_result.results = []
    mock_sandbox.run_code.return_value = mock_result

    # Mock commands
    mock_command_result = MagicMock()
    mock_command_result.exit_code = 0
    mock_command_result.stderr = None
    mock_sandbox.commands.run.return_value = mock_command_result

    # Mock files
    mock_sandbox.files.write.return_value = True
    mock_sandbox.files.read.return_value = b"Test content"

    mock_sandbox_class = MagicMock(return_value=mock_sandbox)
    mocker.patch("lionagi.tools.coder.CoderTool.Sandbox", mock_sandbox_class)
    return mock_sandbox


@pytest.fixture
def mock_rich_console(mocker):
    """Mock rich console for coder.py"""
    mock_console = MagicMock()
    mocker.patch(
        "lionagi.tools.coder.CoderTool.Console", return_value=mock_console
    )
    return mock_console


@pytest.fixture
def mock_tempfile(mocker, temp_dir):
    """Mock tempfile operations"""
    counter = 0

    def create_temp_file(*args, **kwargs):
        nonlocal counter
        counter += 1
        temp_file = temp_dir / f"mock_temp_file_{counter}"
        temp_file.write_text("")  # Create empty file

        mock_temp = MagicMock()
        mock_temp.name = str(temp_file)
        return mock_temp

    mock_temp_class = MagicMock(side_effect=create_temp_file)
    mocker.patch("tempfile.NamedTemporaryFile", mock_temp_class)
    return mock_temp_class


@pytest.fixture
def mock_file_operations(mocker, temp_dir):
    """Mock file operations for reader.py and writer.py"""
    # Store file contents in memory
    file_contents = {}

    def mock_read_text(self, *args, **kwargs):
        path_str = str(self)
        if path_str in file_contents:
            return file_contents[path_str]
        if os.path.isfile(path_str):
            with open(path_str, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def mock_write_text(self, content, *args, **kwargs):
        file_contents[str(self)] = content
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(str(self)), exist_ok=True)
        # Write to actual file using built-in open
        with open(str(self), "w", encoding="utf-8") as f:
            f.write(content)

    def mock_exists(self):
        path_str = str(self)
        return path_str in file_contents or os.path.isfile(path_str)

    mocker.patch.object(Path, "read_text", mock_read_text)
    mocker.patch.object(Path, "write_text", mock_write_text)
    mocker.patch.object(Path, "exists", mock_exists)

    # Mock chunk_content function
    def mock_chunk_content(text, chunk_size, overlap, threshold):
        return ["Chunk 1", "Chunk 2", "Chunk 3"]

    mocker.patch("lionagi.libs.file.chunk.chunk_content", mock_chunk_content)

    # Mock search functionality
    def mock_find(text, query, start_index=0):
        return text.find(query, start_index)

    mocker.patch(
        "lionagi.tools.reader.ReaderTool._search_doc",
        side_effect=lambda doc_id, query: ReaderResponse(
            success=True, search_result=SearchResult(positions=[0, 10])
        ),
    )

    return file_contents
