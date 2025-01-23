from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class WriterAction(str, Enum):
    """
    The enumerated actions for writing or modifying local files/docs:
      - 'open_doc': Create or open doc in memory for writing
      - 'write_doc': Overwrite/append partial text
      - 'list_docs': Show doc_ids stored in memory
      - 'close_doc': Remove doc from memory
      - 'save_file': Save text to disk within allowed root
    """

    open_doc = "open_doc"
    write_doc = "write_doc"
    list_docs = "list_docs"
    close_doc = "close_doc"
    save_file = "save_file"


class WriterRequest(BaseModel):
    """
    Request model for WriterTool. LLM picks 'action' + relevant fields.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "WriterTool: Use these actions to create or modify docs in memory, "
                "or save text to disk."
            )
        }
    )

    action: WriterAction = Field(
        ..., description="Which write-oriented action to perform."
    )

    path: str | None = Field(
        None,
        description=(
            "If action='open_doc', an existing file path to load text from. If not found or None, create empty doc."
        ),
    )
    doc_id: str | None = Field(
        None,
        description="For 'write_doc','close_doc'. The in-memory doc ID to modify or remove.",
    )
    content: str | None = Field(
        None,
        description="For 'write_doc' or 'save_file'. The text to be written.",
    )
    start_offset: int | None = Field(
        None,
        description="For 'write_doc'. The start offset if partially overwriting. If None, append at doc end.",
    )
    end_offset: int | None = Field(
        None,
        description="For 'write_doc'. The end offset. If None, start_offset+len(content).",
    )
    directory: str | None = Field(
        None,
        description="For 'save_file'. The directory under allowed root to write the file.",
    )
    filename: str | None = Field(
        None, description="For 'save_file'. The filename in that directory."
    )


class WriterResponse(BaseModel):
    """
    Response from the WriterTool, showing doc state or file path saved.
    """

    success: bool
    error: str | None = Field(
        None, description="If success=False, reason for failure."
    )

    doc_id: str | None = None
    doc_list: list[str] | None = None
    updated_length: int | None = None
    saved_path: str | None = None
