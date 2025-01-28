"""
Diff generation and application tool with fuzzy matching.
"""

import difflib
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from ...libs.validate import string_similarity
from .base import CoderTool, FileChange


class DiffFormat(str, Enum):
    """Supported diff formats"""

    UNIFIED = "unified"
    CONTEXT = "context"
    HTML = "html"


class DiffRequest(BaseModel):
    """
    Request model for diff operations.

    Examples:
        Generate diff:
        ```python
        {
            "path": "src/main.py",
            "original": "def main():\n    pass",
            "modified": "def main():\n    print('hello')",
            "format": "unified",
            "context_lines": 3
        }
        ```

        Apply diff:
        ```python
        {
            "path": "src/main.py",
            "diff": "--- src/main.py\n+++ src/main.py\n@@ ... @@\n...",
            "fuzzy_match": True,
            "match_threshold": 0.8
        }
        ```
    """

    path: str = Field(..., description="Target file path")
    original: Optional[str] = Field(
        None, description="Original content for diff generation"
    )
    modified: Optional[str] = Field(
        None, description="Modified content for diff generation"
    )
    diff: Optional[str] = Field(None, description="Diff to apply")
    format: DiffFormat = Field(DiffFormat.UNIFIED, description="Diff format")
    context_lines: int = Field(
        3, description="Context lines around changes", ge=0
    )
    fuzzy_match: bool = Field(
        True, description="Use fuzzy matching for applying diffs"
    )
    match_threshold: float = Field(
        0.8, description="Fuzzy match threshold", gt=0.0, le=1.0
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "path": "src/main.py",
                    "original": "def main():\n    pass",
                    "modified": "def main():\n    print('hello')",
                    "format": "unified",
                    "context_lines": 3,
                },
                {
                    "path": "src/main.py",
                    "diff": "--- src/main.py\n+++ src/main.py\n@@ ... @@\n...",
                    "fuzzy_match": True,
                    "match_threshold": 0.8,
                },
            ]
        }
    }


class DiffResponse(BaseModel):
    """
    Response from diff operations.

    Attributes:
        success: Operation success flag
        diff: Generated diff if requested
        content: New content if diff applied
        error: Error message if failed
        matches: Fuzzy match info if relevant
    """

    success: bool = Field(..., description="Operation success status")
    diff: Optional[str] = Field(None, description="Generated diff content")
    content: Optional[str] = Field(
        None, description="New content after applying diff"
    )
    error: Optional[str] = Field(None, description="Error message if failed")
    matches: Dict[str, float] = Field(
        default_factory=dict, description="Fuzzy match scores"
    )


class DiffTool(CoderTool):
    """
    Tool for diff operations with fuzzy matching.

    Features:
    - Diff generation in multiple formats
    - Safe diff application
    - Fuzzy matching for hunks
    - HTML diff visualization
    """

    is_lion_system_tool = True
    system_tool_name = "diff_tool"

    def __init__(self, coder_manager: Any):
        super().__init__(coder_manager.file_manager)
        self.coder_manager = coder_manager
        self._tool = None

    async def handle_request(self, request: DiffRequest) -> DiffResponse:
        """
        Handle diff generation or application.

        Args:
            request: Diff operation request

        Returns:
            Operation response with diff/content
        """
        if isinstance(request, dict):
            request = DiffRequest(**request)

        try:
            # Validate path
            path = (
                await self.validate_files([request.path], must_exist=True)
            )[0]

            # Generate or apply diff
            if request.original is not None and request.modified is not None:
                # Generate diff
                return await self._generate_diff(
                    request.original,
                    request.modified,
                    path,
                    request.format,
                    request.context_lines,
                )
            elif request.diff is not None:
                # Apply diff
                return await self._apply_diff(
                    request.diff,
                    path,
                    request.fuzzy_match,
                    request.match_threshold,
                )
            else:
                return DiffResponse(
                    success=False,
                    error="Must provide either original/modified or diff",
                )

        except Exception as e:
            return DiffResponse(success=False, error=str(e))

    async def _generate_diff(
        self,
        original: str,
        modified: str,
        path: Path,
        format: DiffFormat,
        context_lines: int,
    ) -> DiffResponse:
        """Generate diff in specified format"""
        try:
            if format == DiffFormat.UNIFIED:
                diff = "\n".join(
                    difflib.unified_diff(
                        original.splitlines(),
                        modified.splitlines(),
                        fromfile=str(path),
                        tofile=str(path),
                        n=context_lines,
                        lineterm="",
                    )
                )
            elif format == DiffFormat.CONTEXT:
                diff = "\n".join(
                    difflib.context_diff(
                        original.splitlines(),
                        modified.splitlines(),
                        fromfile=str(path),
                        tofile=str(path),
                        n=context_lines,
                        lineterm="",
                    )
                )
            elif format == DiffFormat.HTML:
                diff = difflib.HtmlDiff().make_file(
                    original.splitlines(),
                    modified.splitlines(),
                    str(path),
                    str(path),
                    context=True,
                    numlines=context_lines,
                )
            else:
                raise ValueError(f"Unsupported format: {format}")

            return DiffResponse(success=True, diff=diff)

        except Exception as e:
            return DiffResponse(
                success=False, error=f"Failed to generate diff: {str(e)}"
            )

    async def _apply_diff(
        self, diff: str, path: Path, fuzzy_match: bool, match_threshold: float
    ) -> DiffResponse:
        """Apply diff with optional fuzzy matching"""
        try:
            # Parse diff
            current = path.read_text()
            hunks = self._parse_diff(diff)

            # Apply hunks
            new_content = current
            matches = {}

            for hunk in hunks:
                old_lines = hunk["old_lines"]
                new_lines = hunk["new_lines"]

                if fuzzy_match:
                    # Find best match for hunk context
                    best_pos, score = self._find_best_match(
                        old_lines, new_content, match_threshold
                    )
                    if best_pos is not None:
                        matches[str(hunk["start"])] = score
                        new_content = (
                            new_content[:best_pos]
                            + "\n".join(new_lines)
                            + new_content[
                                best_pos + len("\n".join(old_lines)) :
                            ]
                        )
                else:
                    # Direct replacement
                    start = hunk["start"]
                    if not self._verify_context(old_lines, new_content, start):
                        raise ValueError(f"Context mismatch at line {start}")
                    new_content = (
                        new_content[:start]
                        + "\n".join(new_lines)
                        + new_content[start + len("\n".join(old_lines)) :]
                    )

            return DiffResponse(
                success=True, content=new_content, matches=matches
            )

        except Exception as e:
            return DiffResponse(
                success=False, error=f"Failed to apply diff: {str(e)}"
            )

    def _parse_diff(self, diff: str) -> List[Dict]:
        """Parse unified diff format into hunks"""
        hunks = []
        current_hunk = None

        for line in diff.splitlines():
            if line.startswith("@@"):
                # New hunk header
                if current_hunk:
                    hunks.append(current_hunk)

                # Parse hunk header
                old_start = int(line.split()[1].split(",")[0][1:])
                current_hunk = {
                    "start": old_start,
                    "old_lines": [],
                    "new_lines": [],
                }
            elif current_hunk is not None:
                if line.startswith("-"):
                    current_hunk["old_lines"].append(line[1:])
                elif line.startswith("+"):
                    current_hunk["new_lines"].append(line[1:])
                elif line.startswith(" "):
                    current_hunk["old_lines"].append(line[1:])
                    current_hunk["new_lines"].append(line[1:])

        if current_hunk:
            hunks.append(current_hunk)

        return hunks

    def _find_best_match(
        self, old_lines: List[str], content: str, threshold: float
    ) -> Tuple[Optional[int], float]:
        """Find best fuzzy match for hunk context"""
        best_score = 0
        best_pos = None
        old_text = "\n".join(old_lines)

        # Split content into potential matches
        content_lines = content.splitlines()
        for i in range(len(content_lines)):
            window = "\n".join(content_lines[i : i + len(old_lines)])
            score = string_similarity(
                old_text, window, algorithm="jaro_winkler"
            )
            if score and score > best_score:
                best_score = score
                best_pos = content.find(window)

        if best_score >= threshold:
            return best_pos, best_score
        return None, 0.0

    def _verify_context(
        self, old_lines: List[str], content: str, start: int
    ) -> bool:
        """Verify diff context matches"""
        old_text = "\n".join(old_lines)
        content_part = content[start : start + len(old_text)]
        return old_text == content_part

    def to_tool(self):
        """Convert to Tool instance"""
        if self._tool is not None:
            return self._tool

        async def diff_tool(**kwargs):
            """Diff tool for code changes"""
            return (
                await self.handle_request(DiffRequest(**kwargs))
            ).model_dump()

        if self.system_tool_name != "diff_tool":
            diff_tool.__name__ = self.system_tool_name

        from lionagi.operatives.action.tool import Tool

        self._tool = Tool(func_callable=diff_tool, request_options=DiffRequest)
        return self._tool
