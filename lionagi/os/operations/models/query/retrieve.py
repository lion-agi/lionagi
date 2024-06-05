DEFAULT_TOOL_NAME = "document_retrieval_tool"
DEFAULT_TOOL_DESCRIPTION = """A tool to execute natural language queries
against a knowledge base to fetch relevant documents.
"""


class DocumentRetrievalTool(AsyncToolBase):
    """Document Retrieval Tool.

    A tool that utilizes a retriever to fetch documents.

    Args:
        retriever (BaseRetriever): The retriever for querying documents.
        metadata (ToolInfo): Metadata about the tool.
        document_postprocessors (Optional[List[BaseDocumentPostprocessor]]): A list of
            document postprocessors.
    """

    def __init__(
        self,
        retriever: BaseRetriever,
        metadata: ToolInfo,
        document_postprocessors: Optional[List[BaseDocumentPostprocessor]] = None,
    ) -> None:
        self._retriever = retriever
        self._metadata = metadata
        self._document_postprocessors = document_postprocessors or []

    @classmethod
    def from_defaults(
        cls,
        retriever: BaseRetriever,
        document_postprocessors: Optional[List[BaseDocumentPostprocessor]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> "DocumentRetrievalTool":
        name = name or DEFAULT_TOOL_NAME
        description = description or DEFAULT_TOOL_DESCRIPTION

        metadata = ToolInfo(name=name, description=description)
        return cls(
            retriever=retriever,
            metadata=metadata,
            document_postprocessors=document_postprocessors,
        )

    @property
    def retriever(self) -> BaseRetriever:
        return self._retriever

    @property
    def metadata(self) -> ToolInfo:
        return self._metadata

    def call(self, *args: Any, **kwargs: Any) -> ToolResult:
        query = ""
        if args is not None:
            query += ", ".join([str(arg) for arg in args]) + "\n"
        if kwargs is not None:
            query += ", ".join([f"{k!s} is {v!s}" for k, v in kwargs.items()]) + "\n"
        if query == "":
            raise ValueError("Cannot execute query without inputs")

        documents = self._retriever.retrieve(query)
        documents = self._apply_document_postprocessors(documents, query)
        content = ""
        for doc in documents:
            doc_copy = doc.document.copy()
            doc_copy.text_template = "{metadata_str}\n{content}"
            doc_copy.metadata_template = "{key} = {value}"
            content += doc_copy.get_content(MetadataMode.LLM) + "\n\n"
        return ToolResult(
            content=content,
            tool_name=self.metadata.name,
            raw_input={"input": input},
            raw_output=documents,
        )

    async def acall(self, *args: Any, **kwargs: Any) -> ToolResult:
        query = ""
        if args is not None:
            query += ", ".join([str(arg) for arg in args]) + "\n"
        if kwargs is not None:
            query += ", ".join([f"{k!s} is {v!s}" for k, v in kwargs.items()]) + "\n"
        if query == "":
            raise ValueError("Cannot execute query without inputs")
        documents = await self._retriever.aretrieve(query)
        content = ""
        documents = self._apply_document_postprocessors(documents, query)
        for doc in documents:
            doc_copy = doc.document.copy()
            doc_copy.text_template = "{metadata_str}\n{content}"
            doc_copy.metadata_template = "{key} = {value}"
            content += doc_copy.get_content(MetadataMode.LLM) + "\n\n"
        return ToolResult(
            content=content,
            tool_name=self.metadata.name,
            raw_input={"input": input},
            raw_output=documents,
        )

    def as_custom_tool(self) -> "CustomTool":
        raise NotImplementedError("`as_custom_tool` is not implemented.")

    def _apply_document_postprocessors(
        self, documents: List[DocumentWithScore], query_details: QueryDetails
    ) -> List[DocumentWithScore]:
        for document_postprocessor in self._document_postprocessors:
            documents = document_postprocessor.postprocess_documents(
                documents, query_details=query_details
            )
        return documents


from abc import abstractmethod
from typing import List

from core.query_schema import QueryDetails, QueryType
from core.prompts.mixin import PromptHandler
from core.schema import DocumentWithScore


class BaseImageRetriever(PromptHandler):
    """Base class for image retrieval."""

    def text_to_image_retrieve(self, query: QueryType) -> List[DocumentWithScore]:
        """Retrieve image documents based on a text query.

        Args:
            query (QueryType): A text query or a QueryDetails object.
        """
        if isinstance(query, str):
            query = QueryDetails(query_str=query)
        return self._text_to_image_retrieve(query)

    @abstractmethod
    def _text_to_image_retrieve(
        self,
        query_details: QueryDetails,
    ) -> List[DocumentWithScore]:
        """Retrieve image documents based on a text query.

        To be implemented by subclasses.

        """

    def image_to_image_retrieve(self, query: QueryType) -> List[DocumentWithScore]:
        """Retrieve image documents based on an image.

        Args:
            query (QueryType): An image path or a QueryDetails object.
        """
        if isinstance(query, str):
            query = QueryDetails(query_str="", image_path=query)
        return self._image_to_image_retrieve(query)

    @abstractmethod
    def _image_to_image_retrieve(
        self,
        query_details: QueryDetails,
    ) -> List[DocumentWithScore]:
        """Retrieve image documents based on an image.

        To be implemented by subclasses.

        """

    # Async Methods
    async def atext_to_image_retrieve(
        self,
        query: QueryType,
    ) -> List[DocumentWithScore]:
        if isinstance(query, str):
            query = QueryDetails(query_str=query)
        return await self._atext_to_image_retrieve(query)

    @abstractmethod
    async def _atext_to_image_retrieve(
        self,
        query_details: QueryDetails,
    ) -> List[DocumentWithScore]:
        """Asynchronously retrieve image documents based on a text query.

        To be implemented by subclasses.

        """

    async def aimage_to_image_retrieve(
        self,
        query: QueryType,
    ) -> List[DocumentWithScore]:
        if isinstance(query, str):
            query = QueryDetails(query_str="", image_path=query)
        return await self._aimage_to_image_retrieve(query)

    @abstractmethod
    async def _aimage_to_image_retrieve(
        self,
        query_details: QueryDetails,
    ) -> List[DocumentWithScore]:
        """Asynchronously retrieve image documents based on an image.

        To be implemented by subclasses.

        """
