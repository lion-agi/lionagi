from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from .file_models import (
    File,
    FilePurpose,
)  # Assuming we import from the previous file models


class UploadStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Upload(BaseModel):
    id: str = Field(..., description="The Upload unique identifier.")
    object: str = Field(
        "upload", description="The object type, which is always 'upload'."
    )
    bytes: int = Field(..., description="The intended number of bytes to be uploaded.")
    created_at: int = Field(
        ...,
        description="The Unix timestamp (in seconds) for when the Upload was created.",
    )
    filename: str = Field(..., description="The name of the file to be uploaded.")
    purpose: FilePurpose = Field(..., description="The intended purpose of the file.")
    status: UploadStatus = Field(..., description="The status of the Upload.")
    expires_at: int = Field(
        ..., description="The Unix timestamp (in seconds) for when the Upload expires."
    )
    file: Optional[File] = Field(
        None, description="The File object created after completion."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "upload_abc123",
                "object": "upload",
                "bytes": 2147483648,
                "created_at": 1719184911,
                "filename": "training_examples.jsonl",
                "purpose": "fine-tune",
                "status": "completed",
                "expires_at": 1719127296,
                "file": {
                    "id": "file-xyz321",
                    "object": "file",
                    "bytes": 2147483648,
                    "created_at": 1719186911,
                    "filename": "training_examples.jsonl",
                    "purpose": "fine-tune",
                },
            }
        }
    )


class UploadPart(BaseModel):
    id: str = Field(..., description="The upload Part unique identifier.")
    object: str = Field(
        "upload.part", description="The object type, which is always 'upload.part'."
    )
    created_at: int = Field(
        ...,
        description="The Unix timestamp (in seconds) for when the Part was created.",
    )
    upload_id: str = Field(
        ..., description="The ID of the Upload object that this Part was added to."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "part_def456",
                "object": "upload.part",
                "created_at": 1719186911,
                "upload_id": "upload_abc123",
            }
        }
    )


class CreateUploadRequest(BaseModel):
    filename: str = Field(..., description="The name of the file to upload.")
    purpose: FilePurpose = Field(
        ..., description="The intended purpose of the uploaded file."
    )
    bytes: int = Field(
        ..., description="The number of bytes in the file you are uploading."
    )
    mime_type: str = Field(..., description="The MIME type of the file.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "purpose": "fine-tune",
                "filename": "training_examples.jsonl",
                "bytes": 2147483648,
                "mime_type": "text/jsonl",
            }
        }
    )


class AddUploadPartRequest(BaseModel):
    data: bytes = Field(..., description="The chunk of bytes for this Part.")


class CompleteUploadRequest(BaseModel):
    part_ids: List[str] = Field(..., description="The ordered list of Part IDs.")
    md5: Optional[str] = Field(
        None, description="The optional md5 checksum for the file contents."
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"part_ids": ["part_def456", "part_ghi789"]}}
    )


# API function signatures (these would be implemented elsewhere)


def create_upload(request: CreateUploadRequest) -> Upload:
    """Creates an intermediate Upload object that you can add Parts to."""
    ...


def add_upload_part(upload_id: str, request: AddUploadPartRequest) -> UploadPart:
    """Adds a Part to an Upload object."""
    ...


def complete_upload(upload_id: str, request: CompleteUploadRequest) -> Upload:
    """Completes the Upload."""
    ...


def cancel_upload(upload_id: str) -> Upload:
    """Cancels the Upload."""
    ...
