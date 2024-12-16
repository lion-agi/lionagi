from enum import Enum
from typing import IO

from pydantic import ConfigDict, Field, field_validator

from ..data_models import OpenAIEndpointRequestBody


class Purpose(str, Enum):
    ASSISTANT = "assistant"
    VISION = "vision"
    BATCH = "batch"
    FINE_TUNE = "fine-tune"


class OpenAIUploadFileRequestBody(OpenAIEndpointRequestBody):
    file: str | IO = Field(
        description="The File object (not file name) to be uploaded."
    )

    purpose: Purpose = Field(
        description="The intended purpose of the uploaded file."
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("file")
    @classmethod
    def get_file_object(cls, value):
        if isinstance(value, str):
            value = open(value, "rb")
        return value

    def __del__(self):
        # Ensure the file is closed when the object is destroyed
        file_obj = self.__dict__.get("file")
        if file_obj and not file_obj.closed:
            file_obj.close()
