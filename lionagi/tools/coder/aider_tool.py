"""
Aider integration tool for code editing.
Supports both CLI and API modes with sandbox isolation.
"""

import asyncio
import os
import tempfile
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ...libs.package.imports import check_import
from ..base import LionTool
from .base import CodeError, CoderTool, FileChange


class AiderMode(str, Enum):
    """Aider operation modes"""

    CLI = "cli"  # Interactive CLI mode
    API = "api"  # Direct API calls


class AiderRequest(BaseModel):
    """
    Request model for Aider operations.

    Examples:
        CLI mode:
        ```python
        {
            "mode": "cli",
            "files": ["src/main.py"],
            "instruction": "Add error handling",
            "sandbox": "e2b"
        }
        ```

        API mode:
        ```python
        {
            "mode": "api",
            "files": ["src/main.py"],
            "changes": [
                {
                    "type": "modify",
                    "path": "src/main.py",
                    "content": "def main():\n    try:\n        process()\n    except Exception as e:\n        print(f'Error: {e}')"
                }
            ]
        }
        ```
    """

    mode: AiderMode = Field(..., description="Operation mode (cli/api)")
    files: List[str] = Field(..., description="Files to edit", min_items=1)
    instruction: Optional[str] = Field(
        None, description="Edit instruction for CLI mode"
    )
    changes: Optional[List[FileChange]] = Field(
        None, description="Explicit changes for API mode"
    )
    sandbox: Optional[str] = Field(None, description="Sandbox to use")
    options: Dict[str, Any] = Field(
        default_factory=dict, description="Additional options"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "mode": "cli",
                    "files": ["src/main.py"],
                    "instruction": "Add error handling",
                    "sandbox": "e2b",
                },
                {
                    "mode": "api",
                    "files": ["src/main.py"],
                    "changes": [
                        {
                            "type": "modify",
                            "path": "src/main.py",
                            "content": "def main():\n    try:\n        process()\n    except Exception as e:\n        print(f'Error: {e}')",
                        }
                    ],
                },
            ]
        }
    }


class AiderResponse(BaseModel):
    """
    Response from Aider operations.

    Attributes:
        success: Operation success flag
        changes: List of changes made
        error: Error message if failed
        logs: Operation logs
    """

    success: bool = Field(..., description="Operation success status")
    changes: Optional[List[FileChange]] = Field(
        None, description="Changes made to files"
    )
    error: Optional[str] = Field(None, description="Error message if failed")
    logs: List[str] = Field(default_factory=list, description="Operation logs")


class AiderTool(CoderTool):
    """
    Aider integration for code editing.

    Features:
    - CLI and API modes
    - Sandbox isolation
    - State tracking
    - Change validation
    """

    is_lion_system_tool = True
    system_tool_name = "aider_tool"

    # Import Aider with version check
    aider = check_import("aider", module_name="aider", min_version="0.1.0")

    def __init__(self, coder_manager: Any):
        """
        Initialize tool with coder manager.

        Args:
            coder_manager: CoderManager instance
        """
        super().__init__(coder_manager.file_manager)
        self.coder_manager = coder_manager
        self._tool = None

    async def handle_request(self, request: AiderRequest) -> AiderResponse:
        """
        Handle Aider requests in CLI or API mode.

        Args:
            request: Aider operation request

        Returns:
            Operation response with changes or error
        """
        if isinstance(request, dict):
            request = AiderRequest(**request)

        try:
            # Validate files
            files = await self.validate_files(request.files)

            # Handle sandbox if specified
            if request.sandbox:
                sandbox = await self.coder_manager.get_sandbox(request.sandbox)
                self.sandbox = sandbox
                await self.prepare_sandbox(files)

            # Process based on mode
            if request.mode == AiderMode.CLI:
                return await self._handle_cli_mode(
                    files, request.instruction, request.options
                )
            else:
                return await self._handle_api_mode(
                    files, request.changes, request.options
                )

        except Exception as e:
            return AiderResponse(success=False, error=str(e))

    async def _handle_cli_mode(
        self, files: List[Path], instruction: str, options: Dict[str, Any]
    ) -> AiderResponse:
        """Handle CLI mode operation"""
        if not instruction:
            return AiderResponse(
                success=False, error="Instruction required for CLI mode"
            )

        try:
            # Create temporary working directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)

                # Copy files to temp dir
                for file in files:
                    dst = temp_dir / file.name
                    dst.write_text(file.read_text())

                # Run Aider in CLI mode
                command = [
                    "aider",
                    "--no-git",
                    "--working-dir",
                    str(temp_dir),
                    *[str(f.name) for f in files],
                    "--edit",
                    instruction,
                ]

                if self.sandbox:
                    result = await self.sandbox.run_command(" ".join(command))
                    logs = result.get("output", [])
                else:
                    process = await asyncio.create_subprocess_exec(
                        *command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, stderr = await process.communicate()
                    logs = [stdout.decode(), stderr.decode()]

                # Collect changes
                changes = []
                for file in files:
                    temp_file = temp_dir / file.name
                    if temp_file.exists():
                        new_content = temp_file.read_text()
                        if new_content != file.read_text():
                            changes.append(
                                FileChange(
                                    type="modify",
                                    path=str(file),
                                    content=new_content,
                                    description=f"Modified by Aider: {instruction}",
                                )
                            )

                return AiderResponse(success=True, changes=changes, logs=logs)

        except Exception as e:
            return AiderResponse(
                success=False, error=f"CLI mode failed: {str(e)}"
            )

    async def _handle_api_mode(
        self,
        files: List[Path],
        changes: List[FileChange],
        options: Dict[str, Any],
    ) -> AiderResponse:
        """Handle API mode operation"""
        if not changes:
            return AiderResponse(
                success=False, error="Changes required for API mode"
            )

        try:
            # Validate changes
            file_map = {str(f): f for f in files}
            for change in changes:
                if change.path not in file_map:
                    return AiderResponse(
                        success=False, error=f"Invalid file: {change.path}"
                    )

            # Apply changes
            applied = []
            for change in changes:
                file = file_map[change.path]
                if change.type == "modify" and change.content:
                    file.write_text(change.content)
                    applied.append(change)

            return AiderResponse(success=True, changes=applied)

        except Exception as e:
            return AiderResponse(
                success=False, error=f"API mode failed: {str(e)}"
            )

    def to_tool(self):
        """Convert to Tool instance"""
        if self._tool is not None:
            return self._tool

        async def aider_tool(**kwargs):
            """Aider tool for code editing"""
            return (
                await self.handle_request(AiderRequest(**kwargs))
            ).model_dump()

        if self.system_tool_name != "aider_tool":
            aider_tool.__name__ = self.system_tool_name

        from lionagi.operatives.action.tool import Tool

        self._tool = Tool(
            func_callable=aider_tool, request_options=AiderRequest
        )
        return self._tool
