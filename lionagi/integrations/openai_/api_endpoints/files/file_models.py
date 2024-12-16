from enum import Enum

from pydantic import Field

from ..data_models import OpenAIEndpointResponseBody


class Purpose(str, Enum):
    ASSISTANTS = "assistants"
    ASSISTANTS_OUTPUT = "assistants_output"
    VISION = "vision"
    BATCH = "batch"
    BATCH_OUTPUT = "batch_output"
    FINE_TUNE = "fine-tune"
    FINE_TUNE_RESULTS = "fine-tune-results"


class Status(str, Enum):
    UPLOADED = "uploaded"
    PROCESSED = "processed"
    ERROR = "error"


class OpenAIFileResponseBody(OpenAIEndpointResponseBody):
    id: str = Field(
        description="The file identifier, which can be "
        "referenced in the API endpoints.",
    )

    bytes: int = Field(description="The size of the file, in bytes.")

    created_at: int = Field(
        description="The Unix timestamp (in seconds) for "
        "when the file was created.",
    )

    filename: str = Field(description="The name of the file.")

    object: str = Field(description="The object type, which is always file.")

    purpose: Purpose = Field(description="The intended purpose of the file.")

    status: Status = Field(
        None,
        description="The current status of the file, which can be "
        "either uploaded, processed, or error.",
        deprecated=True,
    )

    status_details: str | None = Field(
        None,
        description="For details on why a fine-tuning training "
        "file failed validation, "
        "see the error field on fine_tuning.job.",
        deprecated=True,
    )
