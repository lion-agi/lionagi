import logging
import tempfile
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from lionagi.operatives.action.tool import Tool
from lionagi.utils import to_num

from .base import LionTool


class WriterAction(str, Enum):
    """
    The type of actions for the WriterTool:
      - 'open': Create or open a document in memory
      - 'write': Write or append text
      - 'list_docs': List docs in memory
      - 'close': Remove a doc from memory
      - 'save_file': Save text to a file on disk (within allowed directory)
      - 'save_chunks': Save a list of chunk objects to disk (within allowed directory)
    """

    open = "open"
    write = "write"
    list_docs = "list_docs"
    close = "close"
    save_file = "save_file"
    save_chunks = "save_chunks"


class WriterRequest(BaseModel):

    action: WriterAction = Field(...)

    # For open/write
    path: str | None = None
    doc_id: str | None = None
    content: str | None = None
    start_offset: int | None = None
    end_offset: int | None = None

    # For save_file or save_chunks
    directory: str | None = None
    filename: str | None = None
    chunks: list | None = None

    @field_validator("start_offset", "end_offset", mode="before")
    def _validate_offsets(cls, v):
        try:
            return to_num(v, num_type=int)
        except ValueError:
            return None


class WriterDocumentInfo(BaseModel):
    doc_id: str
    length: int


class WriterResponse(BaseModel):
    success: bool
    error: str | None = None

    doc_info: WriterDocumentInfo | None = None
    updated_length: int | None = None
    doc_list: list[str] | None = None
    saved_path: str | None = None


class WriterTool(LionTool):
    """
    A WriterTool that restricts writing to a single allowed root directory.

    doc_id -> (temp_file_path, doc_length)
    """

    is_lion_system_tool = True
    system_tool_name = "writer_tool"

    def __init__(self, allowed_root: str):
        """
        :param allowed_root: The directory path under which all writes must occur.
        """
        super().__init__()
        self.documents = {}
        self._tool = None

        # Store a *resolved* root path that we’ll compare against
        self.allowed_root = Path(allowed_root).resolve()

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

        else:
            return WriterResponse(success=False, error="Unknown action type")

    # -----------------
    # In-memory doc ops
    # -----------------

    def _open_doc(self, path: str | None) -> WriterResponse:
        """
        If path is given, read existing file content into memory; else empty doc.
        """
        original_text = ""
        if path is not None:
            try:
                with open(path, "r", encoding="utf-8") as f:
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
            with open(path, "r", encoding="utf-8") as f:
                old_text = f.read()
        except Exception as e:
            return WriterResponse(success=False, error=f"Read error: {str(e)}")

        # Overwrite or append
        if start is None:
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
        doc_ids = list(self.documents.keys())
        return WriterResponse(success=True, doc_list=doc_ids)

    def _close_doc(self, doc_id: str) -> WriterResponse:
        if doc_id not in self.documents:
            return WriterResponse(
                success=False, error="doc_id not found in memory"
            )
        del self.documents[doc_id]
        return WriterResponse(success=True)

    # -----------------
    # Restricted saving
    # -----------------

    def _save_file(
        self, text: str, directory: str, filename: str
    ) -> WriterResponse:
        """
        Save text to disk only if it's inside the allowed_root.
        """
        # Construct the full path
        dir_path = Path(directory).resolve()
        file_path = dir_path / filename

        # Check if the resolved path is within our allowed root
        if not str(dir_path).startswith(str(self.allowed_root)):
            return WriterResponse(
                success=False,
                error=f"Target directory '{dir_path}' is outside of allowed root '{self.allowed_root}'",
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
        Save a list of chunk objects to a single file or multiple files,
        as long as it's in the allowed root.
        For demonstration, let's combine them into one JSON file or
        just one text file. Adjust as needed.
        """
        import json
        from pathlib import Path

        dir_path = Path(directory).resolve()
        file_path = dir_path / filename

        # Check if inside allowed root
        if not str(dir_path).startswith(str(self.allowed_root)):
            return WriterResponse(
                success=False,
                error=f"Target directory '{dir_path}' is outside of allowed root '{self.allowed_root}'",
            )

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            with file_path.open("w", encoding="utf-8") as f:
                # Example: just store them as JSON
                json.dump(chunks, f, ensure_ascii=False, indent=2)
            return WriterResponse(success=True, saved_path=str(file_path))
        except Exception as e:
            logging.error(f"Failed saving chunks: {e}")
            return WriterResponse(success=False, error=str(e))

    def to_tool(self):
        if self._tool is None:

            def writer_tool(**kwargs):
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
