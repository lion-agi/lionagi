from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ReaderAction(str, Enum):
    """
    The enumerated actions for reading local files or in-memory docs:
      - 'open_doc': Convert a file/URL to text in memory, return doc_id
      - 'read_doc': Retrieve partial text from doc by offsets
      - 'search_doc': Find substring in doc text, return positions
      - 'list_docs': Show doc_ids stored in memory
      - 'close_doc': Remove a doc from memory
    """

    open_doc = "open_doc"
    read_doc = "read_doc"
    search_doc = "search_doc"
    list_docs = "list_docs"
    close_doc = "close_doc"


class ReaderRequest(BaseModel):
    """
    Request model for ReaderTool. The LLM sets 'action' + relevant fields.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "ReaderTool: Use these actions to read text from local files or memory. "
                "No chunking or writing is done here—this is read-only usage."
            )
        }
    )

    action: ReaderAction = Field(
        ..., description="Which read-oriented action to perform."
    )

    path_or_url: str | None = Field(
        None,
        description=(
            "If action='open_doc', a local file path or URL to convert into doc text in memory."
        ),
    )
    doc_id: str | None = Field(
        None,
        description=(
            "For 'read_doc','search_doc','close_doc'. The ID referencing an opened doc in memory."
        ),
    )
    start_offset: int | None = Field(
        None,
        description=(
            "For 'read_doc'. The start offset in doc text. If None, default=0."
        ),
    )
    end_offset: int | None = Field(
        None,
        description=(
            "For 'read_doc'. The end offset in doc text. If None, read until doc end."
        ),
    )
    search_query: str | None = Field(
        None,
        description=(
            "For 'search_doc'. The substring to find. If None, invalid for that action."
        ),
    )


class ReaderResponse(BaseModel):
    """
    Response from the ReaderTool, capturing read results or doc listings.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "ReaderTool Response: Contains partial content, search results, doc list, etc."
            )
        }
    )

    success: bool
    error: str | None = Field(
        None, description="If success=False, reason for failure."
    )

    doc_id: str | None = None
    doc_list: list[str] | None = None

    partial_content: str | None = Field(
        None,
        description="If 'read_doc' succeeds, the text slice read from [start_offset..end_offset).",
    )
    positions: list[int] | None = Field(
        None,
        description="If 'search_doc', the positions in text where search_query is found.",
    )
