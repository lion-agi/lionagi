from pydantic import Field

from ..data_models import OpenAIEndpointPathParam


class OpenAIRetrieveFilePathParam(OpenAIEndpointPathParam):
    file_id: str = Field(
        description="The ID of the file to use for this request."
    )
