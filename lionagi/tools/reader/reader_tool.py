import tempfile
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from lionagi.libs.file.chunk import Chunk, chunk_content
from lionagi.operatives.action.tool import Tool
from lionagi.utils import to_num

from ..base import LionTool
from .models import (
    ChunkMetadata,
    DocumentInfo,
    ReaderAction,
    ReaderRequest,
    ReaderResponse,
    SearchResult,
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
            if not text.strip():
                return ReaderResponse(
                    success=False,
                    error="Parsed document text is empty. Check if docling can parse this PDF.",
                )
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
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            return ReaderResponse(
                success=False, error=f"Error reading doc: {str(e)}"
            )

        from lionagi.libs.file.chunk import chunk_content

        chunk_texts = chunk_content(
            text, chunk_size=chunk_size, overlap=overlap, threshold=threshold
        )

        # Optional: debug print for your logs
        # print(f"[DEBUG] chunk_content returned {len(chunk_texts)} chunk(s).")

        if not chunk_texts:
            return ReaderResponse(
                success=False,
                error=(
                    "chunk_content returned an empty list of chunks. Possibly "
                    "the text is empty or chunking logic needs adjustment."
                ),
            )

        chunk_meta_list: list[ChunkMetadata] = []

        # The effective step between chunk starts
        step = int(chunk_size - (overlap * chunk_size))
        current_start = 0

        for i, ctext in enumerate(chunk_texts):
            c_len = len(ctext)
            chunk_meta_list.append(
                ChunkMetadata(
                    index=i,
                    start=current_start,
                    end=current_start + c_len,
                    text=ctext,
                )
            )
            current_start += step

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
                The single entrypoint for using the ReaderTool. Accepts a
                ReaderRequest (JSON). When needing specific features don't
                make up things like `read_chunks`, specify the operation by
                configuring the different fields in the ReaderRequest model.
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
