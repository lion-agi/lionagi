import tempfile
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from lionagi.libs.file.chunk import chunk_content
from lionagi.operatives.action.tool import Tool
from lionagi.utils import to_num

from .base import LionTool


class ReaderAction(str, Enum):
    """
    Expanded Reader actions, including chunk-based reading.
    """

    open = "open"
    read = "read"
    search = "search"
    list_docs = "list_docs"
    close = "close"
    chunk_doc = "chunk_doc"
    list_chunks = "list_chunks"
    read_chunk = "read_chunk"
    read_chunks = "read_chunks"


class ReaderRequest(BaseModel):
    """
    Request model for the expanded ReaderTool.
    """

    action: ReaderAction = Field(...)

    # Standard open/read/search
    path_or_url: str | None = None
    doc_id: str | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    search_query: str | None = None

    # Chunking parameters
    chunk_size: int = 1500
    overlap: float = 0.1
    threshold: int = 200

    # Which chunk index(es) to read
    chunk_index: int | None = None
    chunk_indexes: list[int] | None = None

    @field_validator("start_offset", "end_offset", mode="before")
    def _validate_offsets(cls, v):
        try:
            return to_num(v, num_type=int)
        except ValueError:
            return None


class DocumentInfo(BaseModel):
    doc_id: str
    length: int | None = None


class PartialChunk(BaseModel):
    start_offset: int | None = None
    end_offset: int | None = None
    content: str | None = None


class SearchResult(BaseModel):
    positions: list[int] = Field(default_factory=list)


class ChunkMetadata(BaseModel):
    """
    Describes one chunk in memory.
    index: the chunk index
    start: character start offset in the doc (optional)
    end: character end offset in the doc (optional)
    text: the actual chunk content
    """

    index: int
    start: int
    end: int
    text: str


class ReaderResponse(BaseModel):
    success: bool
    error: str | None = None

    # Standard returns
    doc_info: DocumentInfo | None = None
    chunk: PartialChunk | None = None
    search_result: SearchResult | None = None
    doc_list: list[str] | None = None

    # New chunk-based returns
    chunk_list: list[ChunkMetadata] | None = None
    chunks_read: list[ChunkMetadata] | None = None


class ReaderTool(LionTool):
    """
    A ReaderTool that supports chunking in memory.
    """

    is_lion_system_tool = True
    system_tool_name = "reader_tool"

    # Example: you have a doc converter
    from lionagi.libs.package.imports import check_import

    DocumentConverter = check_import(
        "docling",
        module_name="document_converter",
        import_name="DocumentConverter",
    )

    def __init__(self):
        super().__init__()
        self.converter = ReaderTool.DocumentConverter()
        # documents[doc_id] = {
        #    "text_path": "/tmp/somefile",
        #    "length": 123,
        #    "chunks": List[ChunkMetadata]
        # }
        self.documents: dict[str, dict[str, Any]] = {}
        self._tool = None

    def handle_request(self, request: ReaderRequest) -> ReaderResponse:
        if isinstance(request, dict):
            request = ReaderRequest(**request)

        action = request.action
        if action == ReaderAction.open:
            if not request.path_or_url:
                return ReaderResponse(
                    success=False, error="path_or_url is required for 'open'"
                )
            return self._open_doc(request.path_or_url)

        elif action == ReaderAction.read:
            if not request.doc_id:
                return ReaderResponse(
                    success=False, error="doc_id is required for 'read'"
                )
            return self._read_doc(
                request.doc_id, request.start_offset, request.end_offset
            )

        elif action == ReaderAction.search:
            if not request.doc_id:
                return ReaderResponse(
                    success=False, error="doc_id is required for 'search'"
                )
            if not request.search_query:
                return ReaderResponse(
                    success=False,
                    error="search_query is required for 'search'",
                )
            return self._search_doc(request.doc_id, request.search_query)

        elif action == ReaderAction.list_docs:
            return self._list_docs()

        elif action == ReaderAction.close:
            if not request.doc_id:
                return ReaderResponse(
                    success=False, error="doc_id is required for 'close'"
                )
            return self._close_doc(request.doc_id)

        # ---- NEW CHUNK-BASED ACTIONS ----
        elif action == ReaderAction.chunk_doc:
            if not request.doc_id:
                return ReaderResponse(
                    success=False, error="doc_id is required for 'chunk_doc'"
                )
            return self._chunk_doc(
                doc_id=request.doc_id,
                chunk_size=request.chunk_size,
                overlap=request.overlap,
                threshold=request.threshold,
            )

        elif action == ReaderAction.list_chunks:
            if not request.doc_id:
                return ReaderResponse(
                    success=False, error="doc_id is required for 'list_chunks'"
                )
            return self._list_chunks(request.doc_id)

        elif action == ReaderAction.read_chunk:
            if not request.doc_id:
                return ReaderResponse(
                    success=False, error="doc_id is required for 'read_chunk'"
                )
            if request.chunk_index is None:
                return ReaderResponse(
                    success=False,
                    error="chunk_index is required for 'read_chunk'",
                )
            return self._read_chunk(
                doc_id=request.doc_id, chunk_index=request.chunk_index
            )

        elif action == ReaderAction.read_chunks:
            if not request.doc_id:
                return ReaderResponse(
                    success=False, error="doc_id is required for 'read_chunks'"
                )
            if not request.chunk_indexes:
                return ReaderResponse(
                    success=False,
                    error="chunk_indexes is required for 'read_chunks'",
                )
            return self._read_chunks(
                doc_id=request.doc_id, chunk_indexes=request.chunk_indexes
            )

        else:
            return ReaderResponse(success=False, error="Unknown action type")

    # -------------------------------
    # Existing core read logic
    # -------------------------------

    def _open_doc(self, source: str) -> ReaderResponse:
        """
        Convert the file/URL to text, store in a temp file, track doc_id.
        """
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
        temp_file.close()

        self.documents[doc_id] = {
            "text_path": temp_file.name,
            "length": len(text),
            "chunks": [],  # will store chunk metadata here
        }

        return ReaderResponse(
            success=True,
            doc_info=DocumentInfo(doc_id=doc_id, length=len(text)),
        )

    def _read_doc(
        self, doc_id: str, start: int | None, end: int | None
    ) -> ReaderResponse:
        if doc_id not in self.documents:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )

        doc_info = self.documents[doc_id]
        length = doc_info["length"]
        path = doc_info["text_path"]

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

    def _search_doc(self, doc_id: str, query: str) -> ReaderResponse:
        if doc_id not in self.documents:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )

        doc_info = self.documents[doc_id]
        path = doc_info["text_path"]
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except Exception as ex:
            return ReaderResponse(
                success=False, error=f"Search read error: {str(ex)}"
            )

        positions = []
        start_index = 0
        while True:
            pos = text.find(query, start_index)
            if pos == -1:
                break
            positions.append(pos)
            start_index = pos + 1

        return ReaderResponse(
            success=True, search_result=SearchResult(positions=positions)
        )

    def _list_docs(self) -> ReaderResponse:
        return ReaderResponse(
            success=True, doc_list=list(self.documents.keys())
        )

    def _close_doc(self, doc_id: str) -> ReaderResponse:
        if doc_id not in self.documents:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )
        del self.documents[doc_id]
        return ReaderResponse(success=True)

    # --------------------------------------
    # New in-memory chunking operations
    # --------------------------------------

    def _chunk_doc(
        self, doc_id: str, chunk_size: int, overlap: float, threshold: int
    ) -> ReaderResponse:
        """
        Read the entire doc text from file, split into chunks, store them in memory.
        """
        if doc_id not in self.documents:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )

        doc_info = self.documents[doc_id]
        path = doc_info["text_path"]

        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            return ReaderResponse(
                success=False, error=f"Error reading doc: {str(e)}"
            )

        # chunk_content should return a list of textual pieces
        chunks = chunk_content(
            text, chunk_size=chunk_size, overlap=overlap, threshold=threshold
        )
        # We'll create chunk metadata with start/end offsets if desired.
        # For a simple approach, let's assume chunk_content returns a list of raw text segments in order.

        chunk_meta_list = []
        curr_start = 0
        for i, ctext in enumerate(chunks):
            chunk_len = len(ctext)
            chunk_meta_list.append(
                ChunkMetadata(
                    index=i,
                    start=curr_start,
                    end=curr_start + chunk_len,
                    text=ctext,
                )
            )
            curr_start += chunk_len

        doc_info["chunks"] = chunk_meta_list

        return ReaderResponse(
            success=True,
            chunk_list=chunk_meta_list,  # show the newly created chunks
        )

    def _list_chunks(self, doc_id: str) -> ReaderResponse:
        if doc_id not in self.documents:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )

        chunk_meta_list = self.documents[doc_id].get("chunks", [])
        return ReaderResponse(success=True, chunk_list=chunk_meta_list)

    def _read_chunk(self, doc_id: str, chunk_index: int) -> ReaderResponse:
        if doc_id not in self.documents:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )

        chunk_meta_list = self.documents[doc_id].get("chunks", [])
        if chunk_index < 0 or chunk_index >= len(chunk_meta_list):
            return ReaderResponse(
                success=False, error="chunk_index out of range"
            )

        return ReaderResponse(
            success=True, chunks_read=[chunk_meta_list[chunk_index]]
        )

    def _read_chunks(
        self, doc_id: str, chunk_indexes: list[int]
    ) -> ReaderResponse:
        if doc_id not in self.documents:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )

        chunk_meta_list = self.documents[doc_id].get("chunks", [])
        out = []
        for idx in chunk_indexes:
            if 0 <= idx < len(chunk_meta_list):
                out.append(chunk_meta_list[idx])
            else:
                # skip invalid indexes or raise error
                pass

        return ReaderResponse(success=True, chunks_read=out)

    def to_tool(self):
        if self._tool is None:

            def reader_tool(**kwargs):
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
