import tempfile

from lionagi.operatives.action.tool import Tool

from ..base import LionTool
from .models import *


class ReaderTool(LionTool):
    """
    A single tool that the LLM can call with ReaderRequest to either:
      - open a doc (File/URL) -> returns doc_id, doc length
      - read partial text from doc -> returns chunk
    """

    is_lion_system_tool = True
    system_tool_name = "reader_tool"

    def __init__(self):
        from lionagi.libs.package.imports import check_import

        DocumentConverter = check_import(
            "docling",
            module_name="document_converter",
            import_name="DocumentConverter",
        )

        super().__init__()
        self.converter = DocumentConverter()
        self.documents = {}  # doc_id -> (temp_file_path, doc_length, source)
        self._tool = None

    def handle_request(self, request: ReaderOption) -> ReaderResponse:
        """
        A function that takes ReaderRequest to either:
        - open a doc (File/URL) -> returns doc_id, doc length
        - read partial text from doc -> returns chunk
        """
        if isinstance(request, dict):
            request = ReaderOption(**request)
        if request.action == "open":
            return self._open_doc(request.path_or_url)
        elif request.action == "read":
            return self._read_doc(
                request.doc_id,
                request.start_offset,
                request.end_offset,
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
        self.documents[doc_id] = (temp_file.name, doc_len, str(source))

        return ReaderResponse(
            success=True,
            doc_info=DocumentInfo(
                doc_id=doc_id, length=doc_len, source=str(source)
            ),
        )

    def _read_doc(self, doc_id: str, start: int, end: int) -> ReaderResponse:
        if doc_id not in self.documents:
            for k, v in self.documents.items():
                if v[2] == doc_id:
                    doc_id = k
                    break
        if doc_id not in self.documents:
            return ReaderResponse(
                success=False, error="doc_id not found in memory"
            )

        path, length, source = self.documents[doc_id]
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
                - open a local File as md -> returns doc_id, doc length, source
                - scrape a webiste as md -> returns doc_id, doc length, source
                - read partial text from doc -> returns chunk
                """
                return self.handle_request(ReaderOption(**kwargs)).model_dump()

            if self.system_tool_name != "reader_tool":
                reader_tool.__name__ = self.system_tool_name

            self._tool = Tool(
                func_callable=reader_tool,
                request_options=ReaderOption,
            )
        return self._tool
