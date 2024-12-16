from pydantic import Field

from ..data_models import OpenAIEndpointPathParam, OpenAIEndpointResponseBody


class OpenAIDeleteFilePathParam(OpenAIEndpointPathParam):
    file_id: str = Field(
        description="The ID of the file to use for this request."
    )


class OpenAIDeleteFileResponseBody(OpenAIEndpointResponseBody):
    id: str = Field(
        description="The file identifier, which can be referenced "
        "in the API endpoints.",
    )

    object: str = Field(description="The object type, which is always file.")

    deleted: bool = Field(description="The deletion status")
