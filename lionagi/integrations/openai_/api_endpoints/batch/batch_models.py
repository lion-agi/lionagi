from typing import Literal

from pydantic import BaseModel, Field

from ..data_models import OpenAIEndpointResponseBody


class Data(BaseModel):
    code: str = Field(description="An error code identifying the error type.")

    message: str = Field(
        description="A human-readable message providing more details"
        " about the error."
    )

    param: str | None = Field(
        None,
        description="The name of the parameter that caused the "
        "error, if applicable.",
    )

    line: int | None = Field(
        None,
        description="The line number of the input file where "
        "the error occurred, if applicable.",
    )


class Error(BaseModel):
    object: Literal["list"] = Field(
        description="The object type, which is always 'list'."
    )

    data: Data = Field(description="A list of error data.")


class RequestCounts(BaseModel):
    total: int = Field(description="Total number of requests in the batch.")

    completed: int = Field(
        description="Number of requests that have been completed successfully."
    )

    failed: int = Field(description="Number of requests that have failed.")


class OpenAIBatchResponseBody(OpenAIEndpointResponseBody):
    id: str = Field(description="A unique identifier for the batch.")

    object: Literal["batch"] = Field(
        description="The object type, which is always 'batch'."
    )

    endpoint: str = Field(description="The API endpoint used for this batch.")

    errors: Error | None = Field(
        None, description="Errors encountered during batch processing."
    )

    input_file_id: str | None = Field(
        None, description="The ID of the input file for the batch."
    )

    completion_window: str | None = Field(
        None,
        description="The time frame within which the batch "
        "should be processed.",
    )

    status: str = Field(description="The current status of the batch.")

    output_file_id: str | None = Field(
        None,
        description="The ID of the file containing the outputs of "
        "successfully executed requests.",
    )

    error_file_id: str | None = Field(
        None,
        description="The ID of the file containing the outputs "
        "of requests with errors.",
    )

    created_at: int | None = Field(
        None,
        description="The Unix timestamp (in seconds) for when "
        "the batch was created.",
    )

    in_progress_at: int | None = Field(
        None,
        description="The Unix timestamp (in seconds) for when the"
        " batch started processing.",
    )

    expires_at: int | None = Field(
        None,
        description="The Unix timestamp (in seconds) for"
        " when the batch will expire.",
    )

    finalizing_at: int | None = Field(
        None,
        description="The Unix timestamp (in seconds) for"
        " when the batch started finalizing.",
    )

    completed_at: int | None = Field(
        None,
        description="The Unix timestamp (in seconds) for"
        " when the batch was completed.",
    )

    failed_at: int | None = Field(
        None,
        description="The Unix timestamp (in seconds) for"
        " when the batch failed.",
    )

    expired_at: int | None = Field(
        None,
        description="The Unix timestamp (in seconds) for"
        " when the batch expired.",
    )

    cancelling_at: int | None = Field(
        None,
        description="The Unix timestamp (in seconds) for"
        " when the batch started cancelling.",
    )

    cancelled_at: int | None = Field(
        None,
        description="The Unix timestamp (in seconds) for"
        " when the batch was cancelled.",
    )

    request_counts: RequestCounts = Field(
        description="The request counts for different statuses"
        " within the batch."
    )

    metadata: dict | None = Field(
        description="Set of 16 key-value pairs that can be"
        " attached to an object."
    )
