from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChunkAction(str, Enum):
    """
    Actions dedicated to chunking doc text or loading chunks from disk:

    - 'chunk_doc': Create chunk metadata from a doc or file
    - 'list_chunks': List chunk metadata for an existing chunk set
    - 'read_chunks': Return the text of specific chunk indexes
    - 'save_chunks': Save chunk data to disk
    - 'load_chunks': Load chunk data from disk into memory
    - 'close_chunks': Remove chunk set from memory
    """

    chunk_doc = "chunk_doc"
    list_chunks = "list_chunks"
    read_chunks = "read_chunks"
    save_chunks = "save_chunks"
    load_chunks = "load_chunks"
    close_chunks = "close_chunks"


class ChunkRequest(BaseModel):
    """
    Request model for ChunkTool. The LLM picks 'action' + relevant fields.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "ChunkTool: A specialized tool for splitting text into chunks, listing them, reading chunk content, "
                "and optionally saving/loading chunk data to/from disk."
            )
        }
    )

    action: ChunkAction = Field(
        ..., description="Which chunk-based operation to perform."
    )

    doc_id: str | None = Field(
        None,
        description="If chunking from an in-memory doc, reference doc_id. If None, might chunk from file_path.",
    )
    file_path: str | None = Field(
        None,
        description="If chunking directly from a local file instead of an in-memory doc.",
    )

    chunk_size: int = Field(
        1500,
        description=("For 'chunk_doc'. Approx chunk size in chars."),
    )
    overlap: float = Field(
        0.1, description="For 'chunk_doc'. Fraction of overlap [0..1)."
    )
    threshold: int = Field(
        200,
        description=(
            "For 'chunk_doc'. Min final chunk size. If smaller, merges with prior chunk."
        ),
    )
    chunk_indexes: list[int] | None = Field(
        None,
        description=("For 'read_chunks'. The chunk indexes to retrieve."),
    )
    # For saving/loading chunk data
    directory: str | None = Field(
        None,
        description="For 'save_chunks','load_chunks'. The directory path in allowed root.",
    )
    filename: str | None = Field(
        None,
        description="For 'save_chunks','load_chunks'. The chunk data file name.",
    )
    chunks: list[Any] | None = Field(
        None,
        description=(
            "For 'save_chunks'. The chunk objects to be written. If None, invalid for that action."
        ),
    )


class ChunkResponse(BaseModel):
    """
    Response from ChunkTool, including chunk metadata or read results.
    """

    success: bool
    error: str | None = None

    chunk_list: list[dict] | None = Field(
        None,
        description="If 'chunk_doc','list_chunks', the chunk metadata objects.",
    )
    chunks_read: list[dict] | None = Field(
        None,
        description="If 'read_chunks', the chunk data for requested indexes.",
    )
    saved_path: str | None = Field(
        None, description="If 'save_chunks', path to the chunk data file."
    )
