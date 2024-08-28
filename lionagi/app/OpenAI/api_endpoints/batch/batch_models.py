from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field
from .base_models import OpenAIBaseModel
from .types import (
    ObjectTypeLiteral,
    EndpointLiteral,
    CompletionWindowLiteral,
    BatchStatusType,
)
from .error_models import ErrorList


class RequestCounts(BaseModel):
    total: int = Field(description="The total number of requests.")
    completed: int = Field(description="The number of completed requests.")
    failed: int = Field(description="The number of failed requests.")


class Batch(OpenAIBaseModel):
    id: str = Field(description="A unique identifier for the batch.")
    object: ObjectTypeLiteral = Field(
        "batch", description="The object type, which is always 'batch'."
    )
    endpoint: EndpointLiteral = Field(
        description="The API endpoint used for this batch."
    )
    errors: Optional[ErrorList] = Field(
        None, description="List of errors encountered during batch processing."
    )
    input_file_id: str = Field(description="The ID of the input file for this batch.")
    completion_window: CompletionWindowLiteral = Field(
        description="The time window for completing the batch."
    )
    status: BatchStatusType = Field(description="The current status of the batch.")
    output_file_id: Optional[str] = Field(
        None, description="The ID of the output file, if available."
    )
    error_file_id: Optional[str] = Field(
        None, description="The ID of the error file, if errors occurred."
    )
    created_at: int = Field(
        description="The Unix timestamp when the batch was created."
    )
    in_progress_at: Optional[int] = Field(
        None, description="The Unix timestamp when the batch started processing."
    )
    expires_at: Optional[int] = Field(
        None, description="The Unix timestamp when the batch will expire."
    )
    finalizing_at: Optional[int] = Field(
        None, description="The Unix timestamp when the batch started finalizing."
    )
    completed_at: Optional[int] = Field(
        None, description="The Unix timestamp when the batch completed."
    )
    failed_at: Optional[int] = Field(
        None, description="The Unix timestamp when the batch failed, if applicable."
    )
    expired_at: Optional[int] = Field(
        None, description="The Unix timestamp when the batch expired, if applicable."
    )
    cancelling_at: Optional[int] = Field(
        None, description="The Unix timestamp when batch cancellation was requested."
    )
    cancelled_at: Optional[int] = Field(
        None, description="The Unix timestamp when the batch was cancelled."
    )
    request_counts: RequestCounts = Field(
        description="Counts of total, completed, and failed requests."
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Optional metadata associated with the batch."
    )

    def __init__(self, **data):
        super().__init__(**data)
        if self.metadata:
            for key, value in self.metadata.items():
                if len(key) > 64:
                    raise ValueError(f"Metadata key '{key}' exceeds 64 character limit")
                if len(value) > 512:
                    raise ValueError(
                        f"Metadata value for key '{key}' exceeds 512 character limit"
                    )


class CreateBatchRequest(BaseModel):
    input_file_id: str = Field(description="The ID of the input file for the batch.")
    endpoint: EndpointLiteral = Field(
        description="The API endpoint to use for this batch."
    )
    completion_window: CompletionWindowLiteral = Field(
        description="The time window for completing the batch."
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Optional metadata to associate with the batch."
    )


class CancelBatchRequest(BaseModel):
    batch_id: str = Field(description="The ID of the batch to cancel.")


class RetrieveBatchRequest(BaseModel):
    batch_id: str = Field(description="The ID of the batch to retrieve.")


class ListBatchParameters(BaseModel):
    after: Optional[str] = Field(None, description="A cursor for use in pagination.")
    limit: Optional[int] = Field(
        20, description="Number of batches to return, default is 20."
    )


class ListBatchResponse(BaseModel):
    object: Literal["list"] = Field(
        "list", description="The object type, which is always 'list'."
    )
    data: List[Batch] = Field(description="A list of Batch objects.")
    has_more: bool = Field(
        description="Whether there are more batches that can be retrieved."
    )
