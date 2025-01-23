from pathlib import Path

import pytest

from lionagi.tools.coder.coder import (
    CoderAction,
    CoderRequest,
    CoderTool,
    RunCodeResult,
)


@pytest.fixture
def coder_tool(mock_e2b_sandbox, mock_rich_console, temp_dir):
    """Initialize CoderTool with mocked dependencies."""
    return CoderTool(e2b_api_key="mock-key")


def test_sandbox_lifecycle(coder_tool, mock_e2b_sandbox):
    """Test sandbox start, list, and stop operations."""
    # Start sandbox
    start_request = CoderRequest(action=CoderAction.start_sandbox)
    start_response = coder_tool.handle_request(start_request)

    assert start_response.success
    assert start_response.sandbox_id is not None
    sandbox_id = start_response.sandbox_id

    # List sandboxes
    list_request = CoderRequest(action=CoderAction.list_sandboxes)
    list_response = coder_tool.handle_request(list_request)

    assert list_response.success
    assert list_response.sandbox_list is not None
    assert sandbox_id in list_response.sandbox_list

    # Stop sandbox
    stop_request = CoderRequest(
        action=CoderAction.stop_sandbox, sandbox_id=sandbox_id
    )
    stop_response = coder_tool.handle_request(stop_request)

    assert stop_response.success

    # Verify sandbox is stopped
    list_response = coder_tool.handle_request(list_request)
    assert sandbox_id not in list_response.sandbox_list


def test_code_execution(coder_tool, mock_e2b_sandbox):
    """Test code execution in sandbox."""
    # Start sandbox
    start_response = coder_tool.handle_request(
        CoderRequest(action=CoderAction.start_sandbox)
    )
    sandbox_id = start_response.sandbox_id

    # Execute Python code
    code = """
    def add(a, b):
        return a + b
    result = add(2, 3)
    print(f"Result: {result}")
    """

    run_request = CoderRequest(
        action=CoderAction.run_code,
        sandbox_id=sandbox_id,
        code=code,
        language="python",
    )
    run_response = coder_tool.handle_request(run_request)

    assert run_response.success
    assert run_response.run_result is not None
    assert run_response.run_result.stdout is not None
    assert "Result: 5" in run_response.run_result.stdout
    assert not run_response.run_result.error


def test_package_installation(coder_tool, mock_e2b_sandbox):
    """Test package installation in sandbox."""
    # Start sandbox
    start_response = coder_tool.handle_request(
        CoderRequest(action=CoderAction.start_sandbox)
    )
    sandbox_id = start_response.sandbox_id

    # Install package with pip
    install_request = CoderRequest(
        action=CoderAction.install_pkg,
        sandbox_id=sandbox_id,
        pkg_manager="pip",
        pkg_name="requests",
    )
    install_response = coder_tool.handle_request(install_request)

    assert install_response.success

    # Install package with npm
    install_request = CoderRequest(
        action=CoderAction.install_pkg,
        sandbox_id=sandbox_id,
        pkg_manager="npm",
        pkg_name="axios",
    )
    install_response = coder_tool.handle_request(install_request)

    assert install_response.success


def test_file_operations(coder_tool, mock_e2b_sandbox, temp_dir):
    """Test file upload and download operations."""
    # Start sandbox
    start_response = coder_tool.handle_request(
        CoderRequest(action=CoderAction.start_sandbox)
    )
    sandbox_id = start_response.sandbox_id

    # Create test file
    test_file = temp_dir / "test.txt"
    test_file.write_text("Test content")

    # Upload file
    upload_request = CoderRequest(
        action=CoderAction.upload_file,
        sandbox_id=sandbox_id,
        local_path=str(test_file),
        remote_path="/workspace/test.txt",
    )
    upload_response = coder_tool.handle_request(upload_request)

    assert upload_response.success

    # Download file
    download_path = temp_dir / "downloaded.txt"
    download_request = CoderRequest(
        action=CoderAction.download_file,
        sandbox_id=sandbox_id,
        local_path=str(download_path),
        remote_path="/workspace/test.txt",
    )
    download_response = coder_tool.handle_request(download_request)

    assert download_response.success
    assert download_path.exists()


def test_shell_command(coder_tool, mock_rich_console):
    """Test shell command execution."""
    request = CoderRequest(
        action=CoderAction.shell_command, command="echo 'Hello, World!'"
    )
    response = coder_tool.handle_request(request)

    assert response.success
    assert response.command_output is not None
    assert response.return_code == 0


def test_error_handling(coder_tool, mock_e2b_sandbox):
    """Test error handling for various scenarios."""
    # Test invalid sandbox ID
    run_request = CoderRequest(
        action=CoderAction.run_code,
        sandbox_id="nonexistent",
        code="print('test')",
    )
    response = coder_tool.handle_request(run_request)
    assert not response.success
    assert response.error is not None

    # Test invalid package manager
    install_request = CoderRequest(
        action=CoderAction.install_pkg,
        sandbox_id="test",
        pkg_manager="invalid",
        pkg_name="test",
    )
    response = coder_tool.handle_request(install_request)
    assert not response.success
    assert response.error is not None

    # Test file operation errors
    upload_request = CoderRequest(
        action=CoderAction.upload_file,
        sandbox_id="test",
        local_path="/nonexistent/path",
        remote_path="/test.txt",
    )
    response = coder_tool.handle_request(upload_request)
    assert not response.success
    assert response.error is not None

    # Test shell command errors
    command_request = CoderRequest(
        action=CoderAction.shell_command, command="nonexistent-command"
    )
    response = coder_tool.handle_request(command_request)
    assert not response.success
    assert response.error is not None


def test_sandbox_resource_options(coder_tool, mock_e2b_sandbox):
    """Test sandbox creation with different resource options."""
    # Test with CPU and RAM specifications
    request = CoderRequest(action=CoderAction.start_sandbox, cpu=2, ram=4096)
    response = coder_tool.handle_request(request)
    assert response.success
    assert response.sandbox_id is not None

    # Test with custom template
    request = CoderRequest(
        action=CoderAction.start_sandbox, template="custom-template"
    )
    response = coder_tool.handle_request(request)
    assert response.success
    assert response.sandbox_id is not None


def test_code_execution_languages(coder_tool, mock_e2b_sandbox):
    """Test code execution in different languages."""
    start_response = coder_tool.handle_request(
        CoderRequest(action=CoderAction.start_sandbox)
    )
    sandbox_id = start_response.sandbox_id

    # Test Python
    python_request = CoderRequest(
        action=CoderAction.run_code,
        sandbox_id=sandbox_id,
        code="print('Hello from Python')",
        language="python",
    )
    response = coder_tool.handle_request(python_request)
    assert response.success

    # Test JavaScript
    js_request = CoderRequest(
        action=CoderAction.run_code,
        sandbox_id=sandbox_id,
        code="console.log('Hello from JavaScript')",
        language="javascript",
    )
    response = coder_tool.handle_request(js_request)
    assert response.success
