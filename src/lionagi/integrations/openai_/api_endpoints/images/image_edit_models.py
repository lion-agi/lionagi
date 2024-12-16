from enum import Enum
from typing import IO, Literal, Optional

from pydantic import ConfigDict, Field, field_validator

from ..data_models import OpenAIEndpointRequestBody


class Size(str, Enum):
    S256 = "256x256"
    S512 = "512x512"
    S1024 = "1024x1024"


class OpenAIImageEditRequestBody(OpenAIEndpointRequestBody):
    image: str | IO = Field(
        description="The image to edit. Must be a valid PNG file, less than 4MB, and square.",
    )

    prompt: str = Field(
        description="A text description of the desired image(s).",
        max_length=1000,
    )

    mask: str | IO | None = Field(
        None,
        description="An additional image whose fully transparent areas indicate where image should be edited.",
    )

    model: Literal["dall-e-2"] | None = Field(
        "dall-e-2", description="The model to use for image generation."
    )

    n: int | None = Field(
        1, description="The number of images to generate.", ge=1, le=10
    )

    size: Size | None = Field(
        "1024x1024", description="The size of the generated images."
    )

    response_format: Literal["url", "b64_json"] | None = Field(
        "url",
        description="The format in which the generated images are returned.",
    )

    user: str | None = Field(
        None,
        description="A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.",
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("image", "mask")
    @classmethod
    def get_file_object(cls, value):
        if isinstance(value, str):
            value = open(value, "rb")
        return value

    def __del__(self):
        # Ensure files are closed when the object is destroyed
        image_obj = self.__dict__.get("image")
        if image_obj and not image_obj.closed:
            image_obj.close()

        mask_obj = self.__dict__.get("mask")
        if mask_obj and not mask_obj.closed:
            mask_obj.close()
