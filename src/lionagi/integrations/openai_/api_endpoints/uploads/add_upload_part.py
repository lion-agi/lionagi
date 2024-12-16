from pydantic import Field

from ..data_models import OpenAIEndpointPathParam, OpenAIEndpointRequestBody


class OpenAIUploadPartPathParam(OpenAIEndpointPathParam):
    upload_id: str = Field(description="The ID of the Upload.")


class OpenAIUploadPartRequestBody(OpenAIEndpointRequestBody):
    data: bytes = Field(description="The chunk of bytes for this Part.")
