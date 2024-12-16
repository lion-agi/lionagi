from typing import Optional

from pydantic import Field

from ..data_models import OpenAIEndpointResponseBody
from ..files.file_models import OpenAIFileResponseBody, Purpose


class OpenAIUploadResponseBody(OpenAIEndpointResponseBody):
    id: str = Field(description="The Upload unique identifier.")

    created_at: int = Field(
        description="The Unix timestamp (in seconds) for when the Upload was created.",
    )

    filename: str = Field(description="The name of the file to be uploaded.")

    bytes: int = Field(
        description="The intended number of bytes to be uploaded."
    )

    purpose: Purpose = Field(description="The intended purpose of the file.")

    status: str = Field(description="The status of the Upload.")

    expires_at: int = Field(
        description="The Unix timestamp (in seconds) for when the Upload expires."
    )

    object: str = Field(
        description="The object type, which is always 'upload'."
    )

    file: OpenAIFileResponseBody | None = Field(
        None, description="The File object created after completion."
    )


class OpenAIUploadPartResponseBody(OpenAIUploadResponseBody):
    id: str = Field(description="The upload Part unique identifier.")

    created_at: int = Field(
        description="The Unix timestamp (in seconds) for when the Part was created.",
    )

    upload_id: str = Field(
        description="The ID of the Upload object that this Part was added to."
    )

    object: str = Field(
        description="The object type, which is always 'upload.part'."
    )
