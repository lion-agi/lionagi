from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from lionagi.utils import to_num

__all__ = (
    "ReaderAction",
    "ReaderOption",
    "DocumentInfo",
    "PartialChunk",
    "ReaderResponse",
)


class ReaderAction(str, Enum):
    """
    This enumeration indicates the *type* of action the LLM wants to perform.
    - 'open': Convert a file/URL to text and store it internally for partial reads
    - 'read': Return a partial slice of the already-opened doc
    - 'scrape': Scrape an internet URL and store it internally for partial reads. Alias of open, but only for URLs
    """

    open = "open"
    read = "read"
    scrape = "scrape"


class ReaderOption(BaseModel):
    """
    The request model for the 'ReaderTool'.
    It indicates:
      - whether we are 'open'-ing a doc or 'read'-ing from a doc
      - which file/URL we want to open (if action='open')
      - which doc_id and offsets we want to read (if action='read')
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": """
------------------
The request for the 'ReaderTool'. Mainly used for opening docs from a 
file or URL or reading a partial slice of the already-opened docs. Some clever 
one-round caveats:\n
1. Open a doc and reading one or more slices of the opened doc, by putting in a
list of action requests with the same path_or_url/doc_id, first action should be 
'open' or 'scrape' and the rest should be 'read'. With 'sequential' action strategy.
2. Manipulating multiple docs at once. By putting in a list of action requests of 
different path_or_url/doc_id. With 'concurrent'/'batch' action strategy.
3. Manipulating multiple docs in sequence. By putting in a list of action requests
of different path_or_url/doc_id. With 'sequential' action strategy. You can also
combine the two strategies together.
------------------
"""
        }
    )

    action: ReaderAction = Field(
        ...,
        description=(
            "**Always Required**. Action to perform. Must be one of the ReaderAction "
            "enum options."
        ),
    )

    path_or_url: str | None = Field(
        None,
        description=(
            "Local file path or remote URL to open. This field is REQUIRED IFF action in ['open', 'scrape']."
        ),
    )

    doc_id: str | None = Field(
        None,
        description=(
            "Unique ID or path_or_url referencing a previously opened document. "
            "This field is REQUIRED if action='read'. Else, leave it None."
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

    @field_validator("start_offset", "end_offset", mode="before")
    def _validate_offsets(cls, v):
        try:
            return to_num(v, num_type=int)
        except ValueError:
            return None


class DocumentInfo(BaseModel):
    """
    Returned info when we 'open' a doc.
    doc_id: The unique string to reference this doc in subsequent 'read' calls
    length: The total character length of the converted text
    """

    doc_id: str
    length: int | None = None
    source: str | None = None


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
    - If action='scrape' succeeded, doc_info is filled (doc_id & length).
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
