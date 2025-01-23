import logging
import tempfile
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from lionagi.operatives.action.tool import Tool
from lionagi.utils import to_num

from ..base import LionTool


class WriterAction(str, Enum):
    """
    This enumeration indicates the *type* of action the LLM wants to perform:
      - 'open': Create or open a document in memory for writing
      - 'write': Write or append text to an opened document (partial offsets)
      - 'list_docs': List doc_ids in memory
      - 'close': Remove a previously opened doc from memory
      - 'save_file': Save text to a file on disk (restricted to allowed directory)
      - 'save_chunks': Save a list of chunk objects to a single file (also restricted)
    """

    open = "open"
    write = "write"
    list_docs = "list_docs"
    close = "close"
    save_file = "save_file"
    save_chunks = "save_chunks"


class WriterRequest(BaseModel):
    """
    The request model for the 'WriterTool'.
    It indicates:
      - action: one of ('open', 'write', 'list_docs', 'close', 'save_file', 'save_chunks')
      - path: path to open if action='open' (optional)
      - doc_id: required if action='write' or 'close'
      - content: text to write if action='write' or 'save_file'
      - start_offset, end_offset: partial overwrite range if action='write'
      - directory, filename: used if action='save_file' or 'save_chunks'
      - chunks: list of chunk data to save if action='save_chunks'
    """

    action: WriterAction = Field(
        ...,
        description=(
            "Action to perform. Must be one of: "
            "- 'open': Open/create a doc in memory. "
            "- 'write': Write partial text to a doc. "
            "- 'list_docs': List open doc_ids. "
            "- 'close': Close a doc. "
            "- 'save_file': Save text to disk (allowed directory only). "
            "- 'save_chunks': Save chunk objects to disk."
        ),
    )

    path: str | None = Field(
        None,
        description=(
            "Local file path to open for writing. If not provided, we create an "
            "empty doc in memory. Used only if action='open'."
        ),
    )

    doc_id: str | None = Field(
        None,
        description=(
            "Unique ID referencing a previously opened document. "
            "Required for 'write' or 'close'. Not used if action='open' or "
            "'list_docs' or 'save_file'/'save_chunks'."
        ),
    )

    content: str | None = Field(
        None,
        description=(
            "Text to write if action='write' or 'save_file'. If action='save_file', "
            "this is the file's content."
        ),
    )

    start_offset: int | None = Field(
        None,
        description=(
            "Character start offset in the doc for partial writing. "
            "If omitted or None, append at the end. Used only if action='write'."
        ),
    )

    end_offset: int | None = Field(
        None,
        description=(
            "Character end offset in the doc for partial overwrite. "
            "If omitted or None, default is start_offset + len(content). "
            "Only used if action='write'."
        ),
    )

    directory: str | None = Field(
        None,
        description=(
            "Directory in which to save the file or chunks if action='save_file' or 'save_chunks'. "
            "Must be within the allowed root directory."
        ),
    )

    filename: str | None = Field(
        None,
        description=("Filename used if action='save_file' or 'save_chunks'."),
    )

    chunks: list | None = Field(
        None,
        description=(
            "List of chunk objects to save if action='save_chunks'. "
            "Each chunk could be a dict with text, metadata, etc."
        ),
    )

    @field_validator("start_offset", "end_offset", mode="before")
    def _validate_offsets(cls, v):
        try:
            return to_num(v, num_type=int)
        except ValueError:
            return None


class WriterDocumentInfo(BaseModel):
    """
    Returned info when we 'open' a doc for writing.
    doc_id: The unique ID to reference this doc in subsequent 'write' calls
    length: The total character length of the doc in memory
    """

    doc_id: str
    length: int


class WriterResponse(BaseModel):
    """
    The response from the 'WriterTool'.

    - If action='open', doc_info is set on success.
    - If action='write', updated_length is set on success.
    - If action='list_docs', doc_list is set.
    - If action='save_file' or 'save_chunks', saved_path is set if successful.
    - If failure, success=False & error holds details.
    """

    success: bool = Field(
        ...,
        description="Indicates if the requested action was performed successfully.",
    )
    error: str | None = Field(
        None,
        description="Describes any error that occurred, if success=False.",
    )

    doc_info: WriterDocumentInfo | None = None
    updated_length: int | None = None
    doc_list: list[str] | None = None

    saved_path: str | None = Field(
        None,
        description="Path where the file or chunks were saved, if action='save_file'/'save_chunks'.",
    )


class WriterTool(LionTool):
    """
    A WriterTool that stores docs in memory and restricts disk writes to an allowed root directory.
    """

    is_lion_system_tool = True
    system_tool_name = "writer_tool"

    def __init__(self, allowed_root: str):
        """
        :param allowed_root: The only directory (and subdirs) where we permit file saving.
        """
        super().__init__()
        # doc_id -> (temp_file_path, doc_length)
        self.documents = {}

        # For restricted disk writes:
        self.allowed_root = Path(allowed_root).resolve()

        self._tool = None

    def handle_request(self, request: WriterRequest) -> WriterResponse:
        if isinstance(request, dict):
            request = WriterRequest(**request)

        action = request.action

        if action == WriterAction.open:
            return self._open_doc(request.path)

        elif action == WriterAction.write:
            if not request.doc_id:
                return WriterResponse(
                    success=False, error="doc_id is required for 'write'"
                )
            if request.content is None:
                return WriterResponse(
                    success=False, error="content is required for 'write'"
                )
            return self._write_doc(
                request.doc_id,
                request.content,
                request.start_offset,
                request.end_offset,
            )

        elif action == WriterAction.list_docs:
            return self._list_docs()

        elif action == WriterAction.close:
            if not request.doc_id:
                return WriterResponse(
                    success=False, error="doc_id is required for 'close'"
                )
            return self._close_doc(request.doc_id)

        elif action == WriterAction.save_file:
            if not request.directory or not request.filename:
                return WriterResponse(
                    success=False,
                    error="directory and filename are required for 'save_file'",
                )
            if request.content is None:
                return WriterResponse(
                    success=False, error="content is required for 'save_file'"
                )
            return self._save_file(
                text=request.content,
                directory=request.directory,
                filename=request.filename,
            )

        elif action == WriterAction.save_chunks:
            if not request.directory or not request.filename:
                return WriterResponse(
                    success=False,
                    error="directory and filename are required for 'save_chunks'",
                )
            if not request.chunks:
                return WriterResponse(
                    success=False,
                    error="chunks list is required for 'save_chunks'",
                )
            return self._save_chunks(
                chunks=request.chunks,
                directory=request.directory,
                filename=request.filename,
            )

        return WriterResponse(success=False, error="Unknown action type")

    # ------------------------
    # In-memory doc management
    # ------------------------

    def _open_doc(self, path: str | None) -> WriterResponse:
        """
        If path is given, read existing file content into memory.
        If not found or None, create empty doc.
        """
        original_text = ""
        if path is not None:
            try:
                with open(path, encoding="utf-8") as f:
                    original_text = f.read()
            except FileNotFoundError:
                pass  # treat as empty if not found

        temp_file = tempfile.NamedTemporaryFile(
            delete=False, mode="w", encoding="utf-8"
        )
        temp_file.write(original_text)
        temp_file.close()

        doc_id = f"WRITER_{abs(hash(path if path else temp_file.name))}"
        self.documents[doc_id] = (temp_file.name, len(original_text))

        return WriterResponse(
            success=True,
            doc_info=WriterDocumentInfo(
                doc_id=doc_id, length=len(original_text)
            ),
        )

    def _write_doc(
        self, doc_id: str, content: str, start: int | None, end: int | None
    ) -> WriterResponse:
        if doc_id not in self.documents:
            return WriterResponse(
                success=False, error="doc_id not found in memory"
            )

        path, length = self.documents[doc_id]
        try:
            with open(path, encoding="utf-8") as f:
                old_text = f.read()
        except Exception as e:
            return WriterResponse(success=False, error=f"Read error: {str(e)}")

        if start is None:
            # Append
            new_text = old_text + content
        else:
            s = max(0, start)
            if end is None:
                e = s + len(content)
            else:
                e = max(s, min(end, len(old_text)))
            new_text = old_text[:s] + content + old_text[e:]

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_text)
        except Exception as e:
            return WriterResponse(
                success=False, error=f"Write error: {str(e)}"
            )

        updated_length = len(new_text)
        self.documents[doc_id] = (path, updated_length)
        return WriterResponse(success=True, updated_length=updated_length)

    def _list_docs(self) -> WriterResponse:
        return WriterResponse(
            success=True, doc_list=list(self.documents.keys())
        )

    def _close_doc(self, doc_id: str) -> WriterResponse:
        if doc_id not in self.documents:
            return WriterResponse(
                success=False, error="doc_id not found in memory"
            )
        del self.documents[doc_id]
        return WriterResponse(success=True)

    # ------------------------
    # Restricted disk writes
    # ------------------------

    def _save_file(
        self, text: str, directory: str, filename: str
    ) -> WriterResponse:
        """
        Save text to a file within the allowed_root only.
        """
        dir_path = Path(directory).resolve()
        file_path = dir_path / filename

        # Ensure the directory is within allowed_root
        if not str(dir_path).startswith(str(self.allowed_root)):
            return WriterResponse(
                success=False,
                error=(
                    f"Target directory '{dir_path}' is outside allowed root '{self.allowed_root}'"
                ),
            )

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            with file_path.open("w", encoding="utf-8") as f:
                f.write(text)
            return WriterResponse(success=True, saved_path=str(file_path))
        except Exception as e:
            logging.error(f"Failed saving file: {e}")
            return WriterResponse(success=False, error=str(e))

    def _save_chunks(
        self, chunks: list, directory: str, filename: str
    ) -> WriterResponse:
        """
        Save a list of chunk objects as JSON (or in any format) to a single file,
        restricted to allowed_root.
        """
        import json

        dir_path = Path(directory).resolve()
        file_path = dir_path / filename

        # Check if directory is within allowed_root
        if not str(dir_path).startswith(str(self.allowed_root)):
            return WriterResponse(
                success=False,
                error=(
                    f"Target directory '{dir_path}' is outside allowed root '{self.allowed_root}'"
                ),
            )

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(chunks, f, ensure_ascii=False, indent=2)
            return WriterResponse(success=True, saved_path=str(file_path))
        except Exception as e:
            logging.error(f"Failed saving chunks: {e}")
            return WriterResponse(success=False, error=str(e))

    def to_tool(self):
        if self._tool is None:

            def writer_tool(**kwargs):
                """
                Entrypoint for the WriterTool. Accepts a WriterRequest (JSON).
                """
                return self.handle_request(
                    WriterRequest(**kwargs)
                ).model_dump()

            if self.system_tool_name != "writer_tool":
                writer_tool.__name__ = self.system_tool_name

            self._tool = Tool(
                func_callable=writer_tool,
                request_options=WriterRequest,
            )
        return self._tool
