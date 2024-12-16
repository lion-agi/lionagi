from pydantic import Field

from ..data_models import OpenAIEndpointRequestBody


class OpenAIUploadRequestBody(OpenAIEndpointRequestBody):
    filename: str = Field(description="The name of the file to upload.")

    purpose: str = Field(
        description="The intended purpose of the uploaded file."
    )

    bytes: int = Field(
        description="The intended number of bytes to be uploaded."
    )

    mime_type: str = Field(description="The MIME type of the file.")
