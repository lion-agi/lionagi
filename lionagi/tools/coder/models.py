from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CoderAction(str, Enum):
    """
    Sandbox or code-based ops:
      - 'start_sandbox': Start a new sandbox
      - 'stop_sandbox': Terminate sandbox
      - 'list_sandboxes': Show active sandbox IDs
      - 'run_code': Execute snippet
      - 'install_pkg': Install a package in sandbox
      - 'upload_file': Copy local file -> sandbox
      - 'download_file': Copy sandbox file -> local
      - 'shell_command': (Optionally) run local shell command
    """

    start_sandbox = "start_sandbox"
    stop_sandbox = "stop_sandbox"
    list_sandboxes = "list_sandboxes"
    run_code = "run_code"
    install_pkg = "install_pkg"
    upload_file = "upload_file"
    download_file = "download_file"
    shell_command = "shell_command"


class CoderRequest(BaseModel):
    """
    Request for CoderTool, describing sandbox ops or code execution.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "CoderTool: Manages code execution in a secure sandbox (like E2B). "
                "Supports package install, file upload/download, optional local shell."
            )
        }
    )

    action: CoderAction

    sandbox_id: Optional[str] = Field(
        None, description="For referencing an existing sandbox if required."
    )
    code: Optional[str] = Field(
        None, description="For 'run_code'. The snippet of Python/JS, etc."
    )
    language: Optional[str] = Field(
        None,
        description="For 'run_code'. E.g. 'python'. If None, default='python'.",
    )
    pkg_manager: Optional[str] = Field(
        None, description="For 'install_pkg'. E.g. 'pip','npm','apt','uv'."
    )
    pkg_name: Optional[str] = Field(
        None, description="For 'install_pkg'. The package name to install."
    )
    local_path: Optional[str] = Field(
        None,
        description=(
            "For 'upload_file','download_file'. The path on host. If None, invalid for those."
        ),
    )
    remote_path: Optional[str] = Field(
        None,
        description=(
            "For 'upload_file','download_file'. The path in sandbox. If None, invalid for those."
        ),
    )
    template: Optional[str] = Field(
        None,
        description="For 'start_sandbox'. A custom environment ID if needed.",
    )
    cpu: Optional[int] = Field(
        None,
        description="For 'start_sandbox'. Desired CPU cores if supported.",
    )
    ram: Optional[int] = Field(
        None,
        description="For 'start_sandbox'. Desired RAM in MB if supported.",
    )
    command: Optional[str] = Field(
        None,
        description="For 'shell_command'. A local shell command if you allow it.",
    )
    verbose: bool = Field(False, description="If True, produce extra logs.")


class RunCodeResult(BaseModel):
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error: Optional[str] = None
    result_objects: Optional[List[Dict[str, Any]]] = None


class CoderResponse(BaseModel):
    """
    Response from CoderTool.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "CoderTool Response: Contains sandbox IDs, run_code results, shell command outputs, etc."
            )
        }
    )

    success: bool
    error: Optional[str] = None

    sandbox_id: Optional[str] = None
    sandbox_list: Optional[List[str]] = None
    run_result: Optional[RunCodeResult] = None
    command_output: Optional[str] = None
    return_code: Optional[int] = None
