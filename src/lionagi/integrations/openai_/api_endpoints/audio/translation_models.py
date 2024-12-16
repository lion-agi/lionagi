from typing import IO, Optional

from pydantic import ConfigDict, Field, field_validator

from ..data_models import OpenAIEndpointRequestBody, OpenAIEndpointResponseBody
from .types import TranscriptionResponseFormat, WhisperModel


class OpenAITranslationRequestBody(OpenAIEndpointRequestBody):
    file: str | IO = Field(description="The audio file to translate")
    model: WhisperModel = Field(description="The model to use for translation")
    prompt: str | None = Field(
        None,
        description="An optional text to guide the model's style "
        "or continue a previous audio segment",
    )
    response_format: TranscriptionResponseFormat = Field(
        default="json",
        description="The format of the transcript output",
    )
    temperature: float = Field(
        default=0, ge=0, le=1, description="The sampling temperature"
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


class OpenAITranslationResponseBody(OpenAIEndpointResponseBody):
    text: str = Field(description="The translated text")
