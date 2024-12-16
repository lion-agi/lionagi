from enum import Enum
from typing import Literal, Optional

from pydantic import Field

from ..data_models import OpenAIEndpointRequestBody


class Size(str, Enum):
    S256 = "256x256"
    S512 = "512x512"
    S1024 = "1024x1024"
    S1792_1024 = "1792x1024"
    S1024_1792 = "1024x1792"


class Style(str, Enum):
    VIVID = "vivid"
    NATURAL = "natural"


class OpenAIImageRequestBody(OpenAIEndpointRequestBody):
    prompt: str = Field(
        description="A text description of the desired image(s)."
    )

    model: str = Field(
        "dall-e-2", description="The model to use for image generation."
    )

    n: int | None = Field(
        1, description="The number of images to generate.", ge=1, le=10
    )

    quality: Literal["standard", "hd"] | None = Field(
        "standard",
        description="The quality of the image that will be generated.",
    )

    response_format: Literal["url", "b64_json"] | None = Field(
        "url",
        description="The format in which the generated images are returned.",
    )

    size: Size | None = Field(
        "1024x1024", description="The size of the generated images."
    )

    style: Style | None = Field(
        "vivid", description="The style of the generated images."
    )

    user: str | None = Field(
        None,
        description="A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.",
    )
