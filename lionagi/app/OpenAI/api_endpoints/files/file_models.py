from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class FilePurpose(str, Enum):
    ASSISTANTS = "assistants"
    ASSISTANTS_OUTPUT = "assistants_output"
    VISION = "vision"
    BATCH = "batch"
    BATCH_OUTPUT = "batch_output"
    FINE_TUNE = "fine-tune"
    FINE_TUNE_RESULTS = "fine-tune-results"


class File(BaseModel):
    id: str = Field(
        ...,
        description="The file identifier, which can be referenced in the API endpoints.",
    )
    bytes: int = Field(..., description="The size of the file, in bytes.")
    created_at: int = Field(
        ...,
        description="The Unix timestamp (in seconds) for when the file was created.",
    )
    filename: str = Field(..., description="The name of the file.")
    object: str = Field("file", description="The object type, which is always file.")
    purpose: FilePurpose = Field(..., description="The intended purpose of the file.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "file-abc123",
                "object": "file",
                "bytes": 120000,
                "created_at": 1677610602,
                "filename": "salesOverview.pdf",
                "purpose": "assistants",
            }
        }
    )


class FileList(BaseModel):
    data: List[File] = Field(..., description="List of File objects.")
    object: str = Field("list", description="The object type, which is always list.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": "file-abc123",
                        "object": "file",
                        "bytes": 175,
                        "created_at": 1613677385,
                        "filename": "salesOverview.pdf",
                        "purpose": "assistants",
                    },
                    {
                        "id": "file-def456",
                        "object": "file",
                        "bytes": 140,
                        "created_at": 1613779121,
                        "filename": "puppy.jsonl",
                        "purpose": "fine-tune",
                    },
                ],
                "object": "list",
            }
        }
    )


class UploadFileRequest(BaseModel):
    file: str = Field(
        ..., description="The File object (not file name) to be uploaded."
    )
    purpose: FilePurpose = Field(
        ..., description="The intended purpose of the uploaded file."
    )


class ListFilesParameters(BaseModel):
    purpose: Optional[FilePurpose] = Field(
        None, description="Only return files with the given purpose."
    )


class DeleteFileResponse(BaseModel):
    id: str = Field(..., description="The ID of the deleted file.")
    object: str = Field("file", description="The object type, which is always file.")
    deleted: bool = Field(
        ..., description="Indicates whether the file was successfully deleted."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"id": "file-abc123", "object": "file", "deleted": True}
        }
    )


# API function signatures (these would be implemented elsewhere)


def upload_file(request: UploadFileRequest) -> File:
    """Upload a file that can be used across various endpoints."""
    ...


def list_files(params: ListFilesParameters) -> FileList:
    """Returns a list of files that belong to the user's organization."""
    ...


def retrieve_file(file_id: str) -> File:
    """Returns information about a specific file."""
    ...


def delete_file(file_id: str) -> DeleteFileResponse:
    """Delete a file."""
    ...


def retrieve_file_content(file_id: str) -> str:
    """Returns the contents of the specified file."""
    ...
