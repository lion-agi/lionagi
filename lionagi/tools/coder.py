import logging
import os
import subprocess
import uuid
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from lionagi.operatives.action.tool import Tool

from .base import LionTool


def run_command(
    command_list: list[str], cwd: Path | None = None
) -> tuple[str, int]:
    """
    Runs a shell command and returns (combined_stdout, exit_code).
    No user interaction, no streaming. For advanced usage, handle pipes, etc.
    """
    proc = subprocess.Popen(
        command_list, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    out, _ = proc.communicate()
    return out.decode("utf-8", errors="replace"), proc.returncode


def truncate_output(text: str, max_len: int = 5000) -> str:
    """
    Truncate the output to prevent overly large results.
    """
    if len(text) > max_len:
        return text[:max_len] + "...(truncated)..."
    return text


def truncate_display_str(s: str, max_length: int = 30) -> str:
    """
    Truncate a string for display if it exceeds max_length.
    """
    if len(s) <= max_length:
        return s
    return s[:max_length] + "..."


def format_string_for_display(s: str, threshold: int = 30) -> str:
    """
    Format a string for display, showing either the entire string if short
    or just a length-based descriptor if long.
    """
    if len(s) <= threshold:
        return f"'{s}'"
    return f"[{len(s)} characters]"


# ---------------------------
# CODERTOOL SCHEMA
# ---------------------------


class CoderAction(str, Enum):
    """
    The enumerated actions that the CoderTool can handle:
      - E2B sandbox management: start/stop/list, run code, install pkg, upload/download
      - Local file ops: file_str_replace, fuzzy_find, shell_command
    """

    start_sandbox = "start_sandbox"
    stop_sandbox = "stop_sandbox"
    list_sandboxes = "list_sandboxes"
    run_code = "run_code"
    install_pkg = "install_pkg"
    upload_file = "upload_file"
    download_file = "download_file"

    file_str_replace = "file_str_replace"
    fuzzy_find = "fuzzy_find"
    shell_command = "shell_command"


class CoderRequest(BaseModel):
    """
    The input model for the CoderTool. Depending on the 'action', different fields
    apply. The 'description' of each field is intended as a prompt/hint for the LLM.
    """

    action: CoderAction = Field(
        ...,
        description=(
            "One of the enumerated coder actions:\n"
            "- 'start_sandbox': Create a new E2B sandbox.\n"
            "- 'stop_sandbox': Stop an existing sandbox.\n"
            "- 'list_sandboxes': List all active sandbox IDs.\n"
            "- 'run_code': Run code in a specified sandbox.\n"
            "- 'install_pkg': Install a package in a sandbox.\n"
            "- 'upload_file': Upload a local file to a sandbox.\n"
            "- 'download_file': Download a file from a sandbox.\n"
            "- 'file_str_replace': Replace an exact string in a local file.\n"
            "- 'fuzzy_find': Fuzzy match files in a local Git repo.\n"
            "- 'shell_command': Run a local shell command."
        ),
    )

    # E2B sandbox fields
    sandbox_id: str | None = Field(
        None,
        description=(
            "Unique ID of the sandbox to operate on. Required for most sandbox actions "
            "(e.g., 'run_code', 'install_pkg', 'upload_file', 'download_file', 'stop_sandbox')."
        ),
    )
    code: str | None = Field(
        None,
        description=(
            "The source code to run if action='run_code'. Usually a Python or JS code snippet."
        ),
    )
    language: str | None = Field(
        None,
        description=(
            "Programming language for 'run_code' (e.g. 'python', 'javascript'). Defaults to 'python'."
        ),
    )
    pkg_manager: str | None = Field(
        None,
        description=(
            "If action='install_pkg', which package manager is used (e.g., 'pip', 'npm', 'apt', 'uv')."
        ),
    )
    pkg_name: str | None = Field(
        None,
        description=(
            "If action='install_pkg', name of the package to install (e.g., 'requests')."
        ),
    )
    local_path: str | None = Field(
        None,
        description=(
            "Local filesystem path used for file operations (upload_file, download_file), "
            "or local ops like shell_command."
        ),
    )
    remote_path: str | None = Field(
        None,
        description=(
            "In-sandbox path for upload_file or download_file (e.g., '/home/user/data.txt')."
        ),
    )
    template: str | None = Field(
        None,
        description=(
            "If action='start_sandbox', optional E2B template ID (custom environment)."
        ),
    )
    cpu: int | None = Field(
        None,
        description=(
            "If action='start_sandbox', optional CPU (vCPUs) for the sandbox (if supported)."
        ),
    )
    ram: int | None = Field(
        None,
        description=(
            "If action='start_sandbox', optional RAM (in MB) for the sandbox (if supported)."
        ),
    )

    # file_str_replace
    filepath: str | None = Field(
        None,
        description=(
            "If action='file_str_replace', path to the local file to modify."
        ),
    )
    old_str: str | None = Field(
        None,
        description=(
            "If action='file_str_replace', the exact string to replace (must appear exactly once)."
        ),
    )
    new_str: str | None = Field(
        None,
        description=(
            "If action='file_str_replace', the new string to insert in place of old_str."
        ),
    )

    # fuzzy_find
    search_term: str | None = Field(
        None,
        description=(
            "If action='fuzzy_find', substring or partial name to match against local repo files."
        ),
    )
    repo_path: str = Field(
        ".",
        description=(
            "If action='fuzzy_find', local path to the Git repository (default: current dir)."
        ),
    )
    threshold: int = Field(
        60,
        description=(
            "If action='fuzzy_find', minimum fuzzy match score (0-100). Default: 60."
        ),
    )
    max_results: int = Field(
        10,
        description=(
            "If action='fuzzy_find', max number of file matches to return. Default: 10."
        ),
    )
    include_paths: list[str] | None = Field(
        None,
        description=(
            "If action='fuzzy_find', optional list of path patterns to include (e.g., ['*.py', '*.md'])."
        ),
    )
    exclude_patterns: list[str] | None = Field(
        None,
        description=(
            "If action='fuzzy_find', optional list of path patterns to exclude (in addition to defaults)."
        ),
    )

    # shell_command
    command: str | None = Field(
        None,
        description=(
            "If action='shell_command', the local command line string to execute (e.g. 'ls -lah')."
        ),
    )

    verbose: bool = Field(
        False,
        description=(
            "If true, produce more detailed console output (when a CLI with 'rich' is available)."
        ),
    )


class RunCodeResult(BaseModel):
    """
    Represents the outcome of running code in an E2B sandbox.

    - stdout: The standard output from the code execution
    - stderr: The standard error output (if any)
    - error: An error message if the code crashed or returned an exception
    - result_objects: A list of returned objects (e.g., images, data) from E2B
    """

    stdout: str | None = None
    stderr: str | None = None
    error: str | None = None
    result_objects: list[dict[str, Any]] | None = None


class CoderResponse(BaseModel):
    """
    The structured response from the CoderTool.
    Fields are populated depending on which action was taken.
    """

    success: bool = Field(
        ...,
        description="Indicates whether the requested action was performed successfully.",
    )
    error: str | None = Field(
        None,
        description="Any error message or reason for failure if success=False.",
    )

    # For sandbox operations
    sandbox_id: str | None = Field(
        None, description="New or existing sandbox ID if relevant."
    )
    sandbox_list: list[str] | None = Field(
        None,
        description="List of currently active sandbox IDs if action='list_sandboxes'.",
    )

    # For run_code
    run_result: RunCodeResult | None = Field(
        None,
        description="Populated if action='run_code' succeeded, contains stdout/stderr/error.",
    )

    # For file_str_replace
    message: str | None = Field(
        None,
        description="A success or informational message if action='file_str_replace'.",
    )

    # For fuzzy_find
    fuzzy_matches: list[tuple[str, int]] | None = Field(
        None,
        description="List of (file_path, score) for fuzzy-matching if action='fuzzy_find'.",
    )

    # For shell_command
    command_output: str | None = Field(
        None, description="Truncated stdout of the local shell command."
    )
    return_code: int | None = Field(
        None, description="Exit code from the local shell command."
    )


class CoderTool(LionTool):
    """
    Manages E2B sandbox operations (start/stop, run code, install packages, upload/download)
    plus local file tasks (file_str_replace, fuzzy_find, shell_command).
    Uses your new Pydantic models for request/response. in a Python 3.10 environment with optional 'uv' for dependency management.
    """

    is_lion_system_tool = True
    system_tool_name = "coder_tool"
    from lionagi.libs.package.imports import check_import

    Sandbox = check_import("e2b_code_interpreter", import_name="Sandbox")
    Console = check_import("rich.console", import_name="Console")
    Panel = check_import("rich.panel", import_name="Panel")
    Markdown = check_import("rich.markdown", import_name="Markdown")
    Repo = check_import("git", import_name="Repo")
    InvalidGitRepositoryError = check_import(
        "git.exc", import_name="InvalidGitRepositoryError"
    )
    fuzz_process = check_import("fuzzywuzzy", import_name="process")

    def __init__(self, e2b_api_key: str):
        super().__init__()
        self.e2b_api_key = e2b_api_key
        self.sandboxes = {}
        self.console = CoderTool.Console()
        self._tool = None

    def handle_request(self, request: CoderRequest) -> CoderResponse:
        if isinstance(request, dict):
            request = CoderRequest(**request)

        action = request.action
        verbose = request.verbose

        # ---- E2B sandbox actions ----
        if action == CoderAction.start_sandbox:
            return self._start_sandbox(
                request.template, request.cpu, request.ram, verbose
            )

        elif action == CoderAction.stop_sandbox:
            if not request.sandbox_id:
                return CoderResponse(
                    success=False,
                    error="sandbox_id required for 'stop_sandbox'",
                )
            return self._stop_sandbox(request.sandbox_id, verbose)

        elif action == CoderAction.list_sandboxes:
            return self._list_sandboxes()

        elif action == CoderAction.run_code:
            if not request.sandbox_id:
                return CoderResponse(
                    success=False, error="sandbox_id required for 'run_code'"
                )
            if not request.code:
                return CoderResponse(
                    success=False, error="code is required for 'run_code'"
                )
            return self._run_code(
                request.sandbox_id, request.code, request.language, verbose
            )

        elif action == CoderAction.install_pkg:
            if not request.sandbox_id:
                return CoderResponse(
                    success=False,
                    error="sandbox_id required for 'install_pkg'",
                )
            if not request.pkg_manager or not request.pkg_name:
                return CoderResponse(
                    success=False,
                    error="pkg_manager and pkg_name are required",
                )
            return self._install_pkg(
                request.sandbox_id,
                request.pkg_manager,
                request.pkg_name,
                verbose,
            )

        elif action == CoderAction.upload_file:
            if not request.sandbox_id:
                return CoderResponse(
                    success=False,
                    error="sandbox_id required for 'upload_file'",
                )
            if not request.local_path or not request.remote_path:
                return CoderResponse(
                    success=False,
                    error="local_path and remote_path are required",
                )
            return self._upload_file(
                request.sandbox_id,
                request.local_path,
                request.remote_path,
                verbose,
            )

        elif action == CoderAction.download_file:
            if not request.sandbox_id:
                return CoderResponse(
                    success=False,
                    error="sandbox_id required for 'download_file'",
                )
            if not request.local_path or not request.remote_path:
                return CoderResponse(
                    success=False,
                    error="local_path and remote_path are required",
                )
            return self._download_file(
                request.sandbox_id,
                request.local_path,
                request.remote_path,
                verbose,
            )

        # ---- Local file ops ----
        elif action == CoderAction.file_str_replace:
            if (
                not request.filepath
                or not request.old_str
                or not request.new_str
            ):
                return CoderResponse(
                    success=False,
                    error="filepath, old_str, new_str are required",
                )
            return self._file_str_replace(
                request.filepath, request.old_str, request.new_str, verbose
            )

        elif action == CoderAction.fuzzy_find:
            if not request.search_term:
                return CoderResponse(
                    success=False,
                    error="search_term is required for 'fuzzy_find'",
                )
            return self._fuzzy_find_project_files(
                request.search_term,
                request.repo_path,
                request.threshold,
                request.max_results,
                request.include_paths,
                request.exclude_patterns,
                verbose,
            )

        elif action == CoderAction.shell_command:
            if not request.command:
                return CoderResponse(
                    success=False,
                    error="command is required for 'shell_command'",
                )
            return self._run_shell_command(request.command, verbose)

        # unknown action
        return CoderResponse(success=False, error="Unknown action type")

    # -----------------------------------------------------
    # E2B sandbox logic
    # -----------------------------------------------------

    def _start_sandbox(
        self,
        template: str | None,
        cpu: int | None,
        ram: int | None,
        verbose: bool,
    ) -> CoderResponse:
        try:
            sbx_id = f"sandbox_{uuid.uuid4().hex[:8]}"
            if template:
                sbx = CoderTool.Sandbox(
                    api_key=self.e2b_api_key, template=template
                )
            else:
                sbx = CoderTool.Sandbox(api_key=self.e2b_api_key)

            sbx.start()
            self.sandboxes[sbx_id] = sbx

            if verbose and self.console:
                self.console.print(
                    f"[green bold]Started sandbox:[/green bold] {sbx_id}"
                )

            return CoderResponse(success=True, sandbox_id=sbx_id)
        except Exception as e:
            logging.error(f"Failed to start sandbox: {e}")
            return CoderResponse(success=False, error=str(e))

    def _stop_sandbox(self, sandbox_id: str, verbose: bool) -> CoderResponse:
        sbx = self.sandboxes.get(sandbox_id)
        if not sbx:
            return CoderResponse(
                success=False, error=f"Sandbox not found: {sandbox_id}"
            )

        try:
            sbx.kill()
        except Exception as e:
            logging.warning(f"Error stopping sandbox {sandbox_id}: {e}")

        del self.sandboxes[sandbox_id]
        if verbose and self.console:
            self.console.print(
                f"[yellow bold]Stopped sandbox:[/yellow bold] {sandbox_id}"
            )

        return CoderResponse(success=True, sandbox_id=sandbox_id)

    def _list_sandboxes(self) -> CoderResponse:
        return CoderResponse(
            success=True, sandbox_list=list(self.sandboxes.keys())
        )

    def _run_code(
        self,
        sandbox_id: str,
        code: str,
        language: str | None,
        verbose: bool,
    ) -> CoderResponse:
        sbx = self.sandboxes.get(sandbox_id)
        if not sbx:
            return CoderResponse(
                success=False, error=f"Sandbox not found: {sandbox_id}"
            )

        lang = language or "python"
        try:
            exec_result = sbx.run_code(
                code,
                language=lang,
                on_stderr=lambda stderr: logging.info(
                    f"[{sandbox_id} stderr] {stderr}"
                ),
                on_stdout=lambda stdout: logging.info(
                    f"[{sandbox_id} stdout] {stdout}"
                ),
            )
            error_msg = exec_result.error.value if exec_result.error else None

            result_objs = []
            if exec_result.results:
                for obj in exec_result.results:
                    result_objs.append(
                        obj.model_dump() if hasattr(obj, "model_dump") else {}
                    )

            run_result = RunCodeResult(
                stdout=exec_result.stdout,
                stderr=exec_result.stderr,
                error=error_msg,
                result_objects=result_objs,
            )

            if verbose and self.console:
                self.console.print(
                    f"[bold green]Code executed in sandbox {sandbox_id}[/bold green] (lang={lang})"
                )

            return CoderResponse(success=True, run_result=run_result)
        except Exception as ex:
            logging.error(f"Error running code in {sandbox_id}: {ex}")
            return CoderResponse(success=False, error=str(ex))

    def _install_pkg(
        self, sandbox_id: str, manager: str, pkg_name: str, verbose: bool
    ) -> CoderResponse:
        sbx = self.sandboxes.get(sandbox_id)
        if not sbx:
            return CoderResponse(
                success=False, error=f"Sandbox not found: {sandbox_id}"
            )

        try:
            if manager == "pip":
                cmd = f"pip install {pkg_name}"
            elif manager == "npm":
                cmd = f"npm install {pkg_name}"
            elif manager == "apt":
                cmd = f"apt-get update && apt-get install -y {pkg_name}"
            elif manager == "uv":
                cmd = f"uv install {pkg_name}"
            else:
                return CoderResponse(
                    success=False, error=f"Unsupported pkg_manager '{manager}'"
                )

            result = sbx.commands.run(cmd)
            if result.exit_code != 0:
                return CoderResponse(
                    success=False,
                    error=result.stderr
                    or f"Install failed: {pkg_name} with {manager}",
                )

            if verbose and self.console:
                self.console.print(
                    f"[bold green]Installed '{pkg_name}' via {manager}[/bold green] in sandbox {sandbox_id}"
                )

            return CoderResponse(success=True)
        except Exception as ex:
            logging.error(f"Error installing {pkg_name} with {manager}: {ex}")
            return CoderResponse(success=False, error=str(ex))

    def _upload_file(
        self, sandbox_id: str, local_path: str, remote_path: str, verbose: bool
    ) -> CoderResponse:
        sbx = self.sandboxes.get(sandbox_id)
        if not sbx:
            return CoderResponse(
                success=False, error=f"Sandbox not found: {sandbox_id}"
            )

        if not os.path.exists(local_path):
            return CoderResponse(
                success=False, error=f"Local file not found: {local_path}"
            )

        try:
            with open(local_path, "rb") as f:
                file_bytes = f.read()

            res = sbx.files.write(remote_path, file_bytes)
            if not res:
                return CoderResponse(
                    success=False, error="Upload returned None or failed."
                )

            if verbose and self.console:
                self.console.print(
                    f"[cyan bold]Uploaded[/cyan bold] {local_path} to sandbox:{remote_path}"
                )

            return CoderResponse(success=True)
        except Exception as ex:
            logging.error(f"Error uploading file: {ex}")
            return CoderResponse(success=False, error=str(ex))

    def _download_file(
        self, sandbox_id: str, local_path: str, remote_path: str, verbose: bool
    ) -> CoderResponse:
        sbx = self.sandboxes.get(sandbox_id)
        if not sbx:
            return CoderResponse(
                success=False, error=f"Sandbox not found: {sandbox_id}"
            )

        try:
            content = sbx.files.read(remote_path)
            if content is None:
                return CoderResponse(
                    success=False,
                    error=f"Could not read remote file: {remote_path}",
                )

            with open(local_path, "wb") as f:
                if isinstance(content, bytes):
                    f.write(content)
                else:
                    f.write(content.encode("utf-8"))

            if verbose and self.console:
                self.console.print(
                    f"[cyan bold]Downloaded[/cyan bold] sandbox:{remote_path} to {local_path}"
                )

            return CoderResponse(success=True)
        except Exception as ex:
            logging.error(f"Error downloading file: {ex}")
            return CoderResponse(success=False, error=str(ex))

    # -----------------------------------------------------
    # Local File Ops
    # -----------------------------------------------------

    def _file_str_replace(
        self, filepath: str, old_str: str, new_str: str, verbose: bool
    ) -> CoderResponse:
        path = Path(filepath)
        if not path.exists():
            msg = f"File not found: {filepath}"
            if verbose and self.console:
                self.console.print(f"[red]{msg}[/red]")
            return CoderResponse(success=False, error=msg)

        content = path.read_text()
        count = content.count(old_str)
        if count == 0:
            msg = f"String not found: {truncate_display_str(old_str)}"
            if verbose and self.console:
                self.console.print(f"[red]{msg}[/red]")
            return CoderResponse(success=False, error=msg)
        elif count > 1:
            msg = f"String appears {count} times - must be unique"
            if verbose and self.console:
                self.console.print(f"[red]{msg}[/red]")
            return CoderResponse(success=False, error=msg)

        new_content = content.replace(old_str, new_str)
        path.write_text(new_content)

        if verbose:
            replaced_msg = (
                f"Replaced in {filepath}:\n"
                f"{format_string_for_display(old_str)} → {format_string_for_display(new_str)}"
            )
            self.console.print(
                CoderTool.Panel(
                    replaced_msg,
                    title="✓ String Replaced",
                    border_style="bright_blue",
                )
            )

        return CoderResponse(
            success=True,
            message=f"Replaced '{old_str}' with '{new_str}' in {filepath}",
        )

    def _fuzzy_find_project_files(
        self,
        search_term: str,
        repo_path: str,
        threshold: int,
        max_results: int,
        include_paths: list[str] | None,
        exclude_patterns: list[str] | None,
        verbose: bool,
    ) -> CoderResponse:
        if not 0 <= threshold <= 100:
            return CoderResponse(
                success=False, error="Threshold must be between 0 and 100"
            )

        try:
            repo = CoderTool.Repo(repo_path)
        except CoderTool.InvalidGitRepositoryError:
            return CoderResponse(
                success=False, error=f"Not a git repository: {repo_path}"
            )

        tracked_files = repo.git.ls_files().splitlines()
        untracked_files = list(repo.untracked_files)
        all_files = tracked_files + untracked_files

        if include_paths:
            filtered = []
            for pattern in include_paths:
                filtered.extend(
                    f for f in all_files if Path(repo_path, f).match(pattern)
                )
            all_files = filtered

        DEFAULT_EXCLUDE = [
            "*.pyc",
            "__pycache__/*",
            ".git/*",
            "*.so",
            "*.o",
            "*.class",
        ]
        exclude_list = DEFAULT_EXCLUDE + (exclude_patterns or [])

        def _exclude(f):
            for pat in exclude_list:
                if Path(repo_path, f).match(pat):
                    return True
            return False

        all_files = [f for f in all_files if not _exclude(f)]

        results = CoderTool.process.extract(
            search_term, all_files, limit=max_results
        )
        filtered_matches = [
            (path, score) for (path, score) in results if score >= threshold
        ]

        if verbose:
            info_sections = []

            params_section = [
                "## Search Parameters",
                f"**Search Term**: `{search_term}`",
                f"**Repository**: `{repo_path}`",
                f"**Threshold**: {threshold}",
                f"**Max Results**: {max_results}",
            ]
            if include_paths:
                params_section.append("\n**Include Patterns**:")
                for pat in include_paths:
                    params_section.append(f"- `{pat}`")
            if exclude_patterns:
                params_section.append("\n**Exclude Patterns**:")
                for pat in exclude_patterns:
                    params_section.append(f"- `{pat}`")
            info_sections.append("\n".join(params_section))

            stats_section = [
                "## Results Statistics",
                f"**Total Files Scanned**: {len(all_files)}",
                f"**Matches Found**: {len(filtered_matches)}",
            ]
            info_sections.append("\n".join(stats_section))

            if filtered_matches:
                results_section = ["## Top Matches"]
                for path, score in filtered_matches[:5]:
                    results_section.append(f"- `{path}` (score: {score})")
                info_sections.append("\n".join(results_section))
            else:
                info_sections.append("## Results\n*No matches found*")

            md_text = "\n\n".join(info_sections)
            self.console.print(
                CoderTool.Panel(
                    CoderTool.Markdown(md_text),
                    title="🔍 Fuzzy Find Results",
                    border_style="bright_blue",
                )
            )

        return CoderResponse(success=True, fuzzy_matches=filtered_matches)

    def _run_shell_command(self, command: str, verbose: bool) -> CoderResponse:
        if verbose and self.console and CoderTool.Panel:
            self.console.print(
                CoderTool.Panel(
                    command, title="🐚 Shell", border_style="bright_yellow"
                )
            )

        try:
            out, code = run_command(["/bin/bash", "-c", command])
            out = truncate_output(out)

            if verbose and self.console:
                style = "bold green" if code == 0 else "bold red"
                self.console.print(
                    f"[{style}]Return code={code}[/{style}]\n{out}"
                )

            return CoderResponse(
                success=(code == 0),
                command_output=out,
                return_code=code,
                error=None if code == 0 else "Non-zero exit code",
            )
        except Exception as e:
            if verbose and self.console:
                self.console.print(f"[red]{e}[/red]")
            return CoderResponse(success=False, error=str(e))

    def to_tool(self):
        if self._tool is None:

            def coder_tool(**kwargs):
                """
                Entrypoint for the CoderTool. Provide a CoderRequest as JSON.
                Returns a dict matching CoderResponse.
                """
                resp = self.handle_request(CoderRequest(**kwargs))
                return resp.model_dump()

            if self.system_tool_name != "coder_tool":
                coder_tool.__name__ = self.system_tool_name

            self._tool = Tool(
                func_callable=coder_tool,
                request_options=CoderRequest,
            )
        return self._tool
