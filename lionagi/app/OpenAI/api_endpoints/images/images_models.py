from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ImageModel(str, Enum):
    DALL_E_2 = "dall-e-2"
    DALL_E_3 = "dall-e-3"


class ImageSize(str, Enum):
    S256 = "256x256"
    S512 = "512x512"
    S1024 = "1024x1024"
    S1792_1024 = "1792x1024"
    S1024_1792 = "1024x1792"


class ImageQuality(str, Enum):
    STANDARD = "standard"
    HD = "hd"


class ImageStyle(str, Enum):
    VIVID = "vivid"
    NATURAL = "natural"


class ResponseFormat(str, Enum):
    URL = "url"
    B64_JSON = "b64_json"


class Image(BaseModel):
    url: Optional[str] = Field(
        None,
        description="The URL of the generated image, if response_format is url (default).",
    )
    b64_json: Optional[str] = Field(
        None,
        description="The base64-encoded JSON of the generated image, if response_format is b64_json.",
    )
    revised_prompt: Optional[str] = Field(
        None,
        description="The prompt that was used to generate the image, if there was any revision to the prompt.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://...",
                "revised_prompt": "A cute baby sea otter wearing a beret",
            }
        }
    )


class ImageResponse(BaseModel):
    created: int = Field(
        ..., description="The Unix timestamp of when the image was created."
    )
    data: List[Image] = Field(..., description="The list of generated images.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "created": 1589478378,
                "data": [{"url": "https://..."}, {"url": "https://..."}],
            }
        }
    )


class CreateImageRequest(BaseModel):
    prompt: str = Field(
        ..., description="A text description of the desired image(s).", max_length=4000
    )
    model: ImageModel = Field(
        ImageModel.DALL_E_2, description="The model to use for image generation."
    )
    n: Optional[int] = Field(
        1, description="The number of images to generate.", ge=1, le=10
    )
    quality: Optional[ImageQuality] = Field(
        ImageQuality.STANDARD,
        description="The quality of the image that will be generated.",
    )
    response_format: Optional[ResponseFormat] = Field(
        ResponseFormat.URL,
        description="The format in which the generated images are returned.",
    )
    size: Optional[ImageSize] = Field(
        ImageSize.S1024, description="The size of the generated images."
    )
    style: Optional[ImageStyle] = Field(
        ImageStyle.VIVID, description="The style of the generated images."
    )
    user: Optional[str] = Field(
        None,
        description="A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "model": "dall-e-3",
                "prompt": "A cute baby sea otter",
                "n": 1,
                "size": "1024x1024",
            }
        }
    )


class CreateImageEditRequest(BaseModel):
    image: bytes = Field(
        ...,
        description="The image to edit. Must be a valid PNG file, less than 4MB, and square.",
    )
    prompt: str = Field(
        ..., description="A text description of the desired image(s).", max_length=1000
    )
    mask: Optional[bytes] = Field(
        None,
        description="An additional image whose fully transparent areas indicate where image should be edited.",
    )
    model: Literal[ImageModel.DALL_E_2] = Field(
        ImageModel.DALL_E_2, description="The model to use for image generation."
    )
    n: Optional[int] = Field(
        1, description="The number of images to generate.", ge=1, le=10
    )
    size: Optional[ImageSize] = Field(
        ImageSize.S1024, description="The size of the generated images."
    )
    response_format: Optional[ResponseFormat] = Field(
        ResponseFormat.URL,
        description="The format in which the generated images are returned.",
    )
    user: Optional[str] = Field(
        None,
        description="A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.",
    )


class CreateImageVariationRequest(BaseModel):
    image: bytes = Field(
        ...,
        description="The image to use as the basis for the variation(s). Must be a valid PNG file, less than 4MB, and square.",
    )
    model: Literal[ImageModel.DALL_E_2] = Field(
        ImageModel.DALL_E_2, description="The model to use for image generation."
    )
    n: Optional[int] = Field(
        1, description="The number of images to generate.", ge=1, le=10
    )
    response_format: Optional[ResponseFormat] = Field(
        ResponseFormat.URL,
        description="The format in which the generated images are returned.",
    )
    size: Optional[ImageSize] = Field(
        ImageSize.S1024, description="The size of the generated images."
    )
    user: Optional[str] = Field(
        None,
        description="A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.",
    )


# API function signatures (these would be implemented elsewhere)


def create_image(request: CreateImageRequest) -> ImageResponse:
    """Creates an image given a prompt."""
    ...


def create_image_edit(request: CreateImageEditRequest) -> ImageResponse:
    """Creates an edited or extended image given an original image and a prompt."""
    ...


def create_image_variation(request: CreateImageVariationRequest) -> ImageResponse:
    """Creates a variation of a given image."""
    ...
