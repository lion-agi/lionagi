from typing import List, Optional

from pydantic import Field

from ..data_models import OpenAIEndpointPathParam, OpenAIEndpointRequestBody


class OpenAICompleteUploadPathParam(OpenAIEndpointPathParam):
    upload_id: str = Field(description="The ID of the Upload.")


class OpenAICompleteUploadRequestBody(OpenAIEndpointRequestBody):
    part_ids: list[str] = Field(description="The ordered list of Part IDs.")

    md5: str | None = Field(
        description="The optional md5 checksum for the file contents to verify "
        "if the bytes uploaded matches what you expect."
    )
