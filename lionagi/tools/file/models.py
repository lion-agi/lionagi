import tempfile
from enum import Enum
from typing import Literal

import docling
from pydantic import BaseModel, Field, field_validator, model_validator

from lionagi.operatives.action.tool import Tool
from lionagi.utils import to_num


class WriterAction(str, Enum):
    """
    write: write contents into a file, (overwrite will create new path if not exist)
    append: append contents into a file, (no overwrite, will create new path if not exist)
    move: move a file from one location to another, the file should have reference in manager's working memory
    delete: delete a file in local file system, also remove from manager's working memory
    """

    WRITE = "write"
    APPEND = "append"
    MOVE = "move"
    DELETE = "delete"


class ReaderAction(str, Enum):
    """
    open: open a local or remote file/url into manager's working memory, allows LLM to access sources. Convert a file/URL to text and store it internally for partial reads
    read: read a chunk of file content from manager's working memory into LLM conversation context, Return a partial slice of the already-opened doc
    list: list files from a particular directory, optionally recursive, with file size and last modified time, optionally label file suffix
    close: close a file in manager's working memory, remove the references, the file will have to be opened again for LLM to access
    stat: get file size and last modified time and other metadata
    """

    OPEN = "open"
    READ = "read"
    LIST = "list"
    CLOSE = "close"
    STAT = "stat"


class ReaderRequest(BaseModel):
    """
    The request model for the 'ReaderTool'.
    It indicates:
      - whether we are 'open'-ing a doc or 'read'-ing from a doc
      - which file/URL we want to open (if action='open')
      - which doc_id and offsets we want to read (if action='read')
    """

    action: ReaderAction = Field(
        ...,
        description="Action to perform. Must be one of: open, read, list, close, stat",
    )

    path_or_url: str | None = Field(
        None,
        description=(
            "Local file path or remote URL to open. This field is REQUIRED if action='open'. "
            "If action='read', leave it None."
        ),
    )

    doc_id: str | None = Field(
        None,
        description=(
            "Unique ID referencing a previously opened document. "
            "This field is REQUIRED if action='read'. If action='open', leave it None."
        ),
    )

    start_offset: int | None = Field(
        None,
        description=(
            "Character start offset in the doc for partial reading. "
            "If omitted or None, defaults to 0. Only used if action='read'."
        ),
    )

    end_offset: int | None = Field(
        None,
        description=(
            "Character end offset in the doc for partial reading. "
            "If omitted or None, we read until the document's end. Only used if action='read'."
        ),
    )

    @model_validator(mode="before")
    def _validate_request(cls, values):
        for k, v in values.items():
            if v == {}:
                values[k] = None
            if k in ["start_offset", "end_offset"]:
                try:
                    values[k] = to_num(v, num_type=int)
                except ValueError:
                    values[k] = None
        return values


class DocumentInfo(BaseModel):
    """
    Returned info when we 'open' a doc.
    doc_id: The unique string to reference this doc in subsequent 'read' calls
    length: The total character length of the converted text
    """

    doc_id: str
    length: int | None = None


class PartialChunk(BaseModel):
    """
    Represents a partial slice of text from [start_offset..end_offset).
    """

    start_offset: int | None = None
    end_offset: int | None = None
    content: str | None = None


class ReaderResponse(BaseModel):
    """
    The response from the 'ReaderTool'.
    - If action='open' succeeded, doc_info is filled (doc_id & length).
    - If action='read' succeeded, chunk is filled (the partial text).
    - If failure occurs, success=False & error hold details.
    """

    success: bool = Field(
        ...,
        description=(
            "Indicates if the requested action was performed successfully."
        ),
    )
    error: str | None = Field(
        None,
        description=("Describes any error that occurred, if success=False."),
    )
    doc_info: DocumentInfo | None = Field(
        None,
        description=(
            "Populated only if action='open' succeeded, letting the LLM know doc_id & total length."
        ),
    )
    chunk: PartialChunk | None = Field(
        None,
        description=(
            "Populated only if action='read' succeeded, providing the partial slice of text."
        ),
    )


class ReaderTool:

    def __init__(
        self,
        provider: Literal["docling"] = "docling",
    ):
        self.provider = provider
        self.converter = None
        self.documents = {}


class ReaderTool:
    """
    A single tool that the LLM can call with ReaderRequest to either:
      - open a doc (File/URL) -> returns doc_id, doc length
      - read partial text from doc -> returns chunk
    """

    is_lion_system_tool = True
    system_tool_name = "reader_tool"

    from lionagi.libs.package.imports import check_import

    DocumentConverter = check_import(
        "docling",
        module_name="document_converter",
        import_name="DocumentConverter",
    )

    def __init__(self):
        super().__init__()
        self.converter = ReaderTool.DocumentConverter()
        self.documents = {}  # doc_id -> (temp_file_path, doc_length)
        self._tool = None

    def handle_request(self, request: ReaderRequest) -> ReaderResponse:
        """
        A function that takes ReaderRequest to either:
        - open a doc (File/URL) -> returns doc_id, doc length
        - read partial text from doc -> returns chunk
        """
        if isinstance(request, dict):
            request = ReaderRequest(**request)
        if request.action == "open":
            return self._open_doc(request.path_or_url)
        elif request.action == "read":
            return self._read_doc(
                request.doc_id, request.start_offset, request.end_offset
            )
        else:
            return ReaderResponse(success=False, error="Unknown action type")

    def _open_doc(self, source: str) -> ReaderResponse:
        try:
            result = self.converter.convert(source)
            text = result.document.export_to_markdown()
        except Exception as e:
            return ReaderResponse(
                success=False, error=f"Conversion error: {str(e)}"
            )

        doc_id = f"DOC_{abs(hash(source))}"
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, mode="w", encoding="utf-8"
        )
        temp_file.write(text)
        doc_len = len(text)
        temp_file.close()

        # store info
        self.documents[doc_id] = (temp_file.name, doc_len)

        return ReaderResponse(
            success=True, doc_info=DocumentInfo(doc_id=doc_id, length=doc_len)
        )

    def _read_doc(self, doc_id: str, start: int, end: int) -> ReaderResponse:
        if doc_id not in self.documents:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )

        path, length = self.documents[doc_id]
        # clamp offsets
        s = max(0, start if start is not None else 0)
        e = min(length, end if end is not None else length)

        try:
            with open(path, encoding="utf-8") as f:
                f.seek(s)
                content = f.read(e - s)
        except Exception as ex:
            return ReaderResponse(
                success=False, error=f"Read error: {str(ex)}"
            )

        return ReaderResponse(
            success=True,
            chunk=PartialChunk(start_offset=s, end_offset=e, content=content),
        )

    def to_tool(self):
        if self._tool is None:

            def reader_tool(**kwargs):
                """
                A function that takes ReaderRequest to either:
                - open a doc (File/URL) -> returns doc_id, doc length
                - read partial text from doc -> returns chunk
                """
                return self.handle_request(
                    ReaderRequest(**kwargs)
                ).model_dump()

            if self.system_tool_name != "reader_tool":
                reader_tool.__name__ = self.system_tool_name

            self._tool = Tool(
                func_callable=reader_tool,
                request_options=ReaderRequest,
            )
        return self._tool
