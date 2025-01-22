import tempfile
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from lionagi.operatives.action.tool import Tool
from lionagi.utils import to_num

from .base import LionTool


class ReaderAction(str, Enum):
    """
    This enumeration indicates the *type* of action the LLM wants to perform.
    - 'open': Convert a file/URL to text and store it internally for partial reads
    - 'read': Return a partial slice of the already-opened doc
    - 'search': Search for a substring in the text; return positions or relevant snippets
    - 'list_docs': List doc_ids currently opened in memory
    - 'close': Remove a previously opened doc from memory
    - 'chunk_doc': Split the doc's text into in-memory chunks
    - 'list_chunks': List chunk metadata for a doc
    - 'read_chunk': Return a single chunk from a doc by index
    - 'read_chunks': Return multiple chunks from a doc by a list of indexes
    """

    open = "open"
    read = "read"
    search = "search"
    list_docs = "list_docs"
    close = "close"

    # NEW chunk-based actions
    chunk_doc = "chunk_doc"
    list_chunks = "list_chunks"
    read_chunk = "read_chunk"
    read_chunks = "read_chunks"


class ReaderRequest(BaseModel):
    """
    The request model for the 'ReaderTool'.

    It indicates:
      - action: one of ('open', 'read', 'search', 'list_docs', 'close',
        'chunk_doc', 'list_chunks', 'read_chunk', 'read_chunks').
      - path_or_url: required if action='open'
      - doc_id: required for any doc-based action ('read','search','close','chunk_doc','list_chunks','read_chunk','read_chunks')
      - start_offset, end_offset: partial read offsets if action='read'
      - search_query: substring to find if action='search'
      - chunk_size, overlap, threshold: chunking parameters if action='chunk_doc'
      - chunk_index, chunk_indexes: which chunk(s) to read if action='read_chunk'/'read_chunks'
    """

    action: ReaderAction = Field(
        ...,
        description=(
            "Action to perform. Must be one of: "
            "- 'open': Convert a file/URL to text and store for partial reads. "
            "- 'read': Return a partial slice of a doc. "
            "- 'search': Look for a substring in a doc's text. "
            "- 'list_docs': List open doc_ids. "
            "- 'close': Remove a doc. "
            "- 'chunk_doc': Split doc's text into chunks in memory. "
            "- 'list_chunks': List chunk metadata for a doc. "
            "- 'read_chunk': Return one chunk by index. "
            "- 'read_chunks': Return multiple chunks by indexes."
        ),
    )

    path_or_url: str | None = Field(
        None,
        description=(
            "Local file path or remote URL to open. REQUIRED if action='open'. "
            "If action!='open', leave it None."
        ),
    )

    doc_id: str | None = Field(
        None,
        description=(
            "Unique ID referencing a previously opened document. "
            "Required for actions: 'read','search','close','chunk_doc','list_chunks','read_chunk','read_chunks'. "
            "If action='open', leave it None."
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
            "If omitted or None, read until doc's end. Only used if action='read'."
        ),
    )

    search_query: str | None = Field(
        None,
        description=(
            "Substring to search for in the doc. Used only if action='search'."
        ),
    )

    chunk_size: int = Field(
        1500,
        description=(
            "Chunk size for action='chunk_doc'. If not chunking, ignore."
        ),
    )

    overlap: float = Field(
        0.1,
        description=(
            "Fractional overlap between consecutive chunks for action='chunk_doc'."
        ),
    )

    threshold: int = Field(
        200,
        description=(
            "Minimum size of the final chunk, used if action='chunk_doc'."
        ),
    )

    chunk_index: int | None = Field(
        None,
        description=("Chunk index to read if action='read_chunk'."),
    )

    chunk_indexes: list[int] | None = Field(
        None,
        description=("List of chunk indexes to read if action='read_chunks'."),
    )

    @field_validator("start_offset", "end_offset", mode="before")
    def _validate_offsets(cls, v):
        try:
            return to_num(v, num_type=int)
        except ValueError:
            return None


class DocumentInfo(BaseModel):
    """
    Returned info when we 'open' a doc.
    doc_id: The unique string to reference this doc in subsequent calls
    length: The total character length of the doc text
    """

    doc_id: str
    length: int | None = None


class PartialChunk(BaseModel):
    """
    Represents a partial slice of text read from [start_offset..end_offset).
    """

    start_offset: int | None = None
    end_offset: int | None = None
    content: str | None = None


class SearchResult(BaseModel):
    """
    A model for search results, e.g. positions of a substring in the doc text.
    """

    positions: list[int] = Field(default_factory=list)


class ChunkMetadata(BaseModel):
    """
    Describes one chunk of the doc text in memory.

    index: the chunk index
    start: character start offset in doc
    end: character end offset in doc
    text: the chunk content
    """

    index: int
    start: int
    end: int
    text: str


class ReaderResponse(BaseModel):
    """
    The response from the 'ReaderTool'.

    - If action='open', doc_info is set on success.
    - If action='read', chunk is set on success.
    - If action='search', search_result is set on success.
    - If action='list_docs', doc_list is set on success.
    - If action='chunk_doc', chunk_list is set on success.
    - If action='read_chunk' or 'read_chunks', chunks_read is set on success.
    - If failure, success=False and error contains details.
    """

    success: bool = Field(
        ...,
        description="Indicates if the requested action was performed successfully.",
    )
    error: str | None = Field(
        None,
        description="Describes any error that occurred, if success=False.",
    )

    doc_info: DocumentInfo | None = None
    chunk: PartialChunk | None = None
    search_result: SearchResult | None = None
    doc_list: list[str] | None = None

    chunk_list: list[ChunkMetadata] | None = Field(
        None, description="Populated if action='chunk_doc' or 'list_chunks'."
    )
    chunks_read: list[ChunkMetadata] | None = Field(
        None, description="Populated if action='read_chunk' or 'read_chunks'."
    )


class ReaderTool(LionTool):
    """
    A ReaderTool that the LLM can call to open docs, read them, search,
    chunk them in memory, and read specific chunks.
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
        # We'll store each doc's data in a dict:
        # documents[doc_id] = {
        #   "text_path": "/temp/file",
        #   "length": int,
        #   "chunks": [ChunkMetadata, ...]
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
            return self._read_chunk(request.doc_id, request.chunk_index)

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
            return self._read_chunks(request.doc_id, request.chunk_indexes)

        else:
            return ReaderResponse(success=False, error="Unknown action type")

    # -------------------
    # Core doc operations
    # -------------------

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
        temp_file.close()

        self.documents[doc_id] = {
            "text_path": temp_file.name,
            "length": len(text),
            "chunks": [],
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

        doc_data = self.documents[doc_id]
        path = doc_data["text_path"]
        length = doc_data["length"]

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

        doc_data = self.documents[doc_id]
        path = doc_data["text_path"]
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

    # ----------------------
    # Chunk-based operations
    # ----------------------

    def _chunk_doc(
        self, doc_id: str, chunk_size: int, overlap: float, threshold: int
    ) -> ReaderResponse:
        doc_data = self.documents.get(doc_id)
        if not doc_data:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )

        path = doc_data["text_path"]
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            return ReaderResponse(
                success=False, error=f"Error reading doc: {str(e)}"
            )

        from lionagi.libs.file.chunk import chunk_content

        chunk_texts = chunk_content(text, chunk_size, overlap, threshold)

        # We'll build a list of ChunkMetadata
        chunk_meta_list: list[ChunkMetadata] = []
        current_start = 0
        for i, ctext in enumerate(chunk_texts):
            chunk_len = len(ctext)
            chunk_meta_list.append(
                ChunkMetadata(
                    index=i,
                    start=current_start,
                    end=current_start + chunk_len,
                    text=ctext,
                )
            )
            current_start += chunk_len

        # Store them
        doc_data["chunks"] = chunk_meta_list

        return ReaderResponse(success=True, chunk_list=chunk_meta_list)

    def _list_chunks(self, doc_id: str) -> ReaderResponse:
        doc_data = self.documents.get(doc_id)
        if not doc_data:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )
        return ReaderResponse(success=True, chunk_list=doc_data["chunks"])

    def _read_chunk(self, doc_id: str, chunk_index: int) -> ReaderResponse:
        doc_data = self.documents.get(doc_id)
        if not doc_data:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )

        chunks = doc_data.get("chunks", [])
        if chunk_index < 0 or chunk_index >= len(chunks):
            return ReaderResponse(
                success=False, error="chunk_index out of range"
            )

        return ReaderResponse(success=True, chunks_read=[chunks[chunk_index]])

    def _read_chunks(self, doc_id: str, indexes: list[int]) -> ReaderResponse:
        doc_data = self.documents.get(doc_id)
        if not doc_data:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )

        chunks = doc_data.get("chunks", [])
        result = []
        for i in indexes:
            if 0 <= i < len(chunks):
                result.append(chunks[i])
            else:
                # either skip or raise an error
                pass

        return ReaderResponse(success=True, chunks_read=result)

    def to_tool(self):
        if self._tool is None:

            def reader_tool(**kwargs):
                """
                The main entrypoint for using the ReaderTool.
                Accepts a ReaderRequest (JSON).
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
