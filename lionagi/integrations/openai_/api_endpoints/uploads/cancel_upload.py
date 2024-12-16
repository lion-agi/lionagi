from pydantic import Field

from ..data_models import OpenAIEndpointPathParam


class OpenAICancelUploadPathParam(OpenAIEndpointPathParam):
    upload_id: str = Field(description="The ID of the Upload.")
