import base64
import math
import os
from io import BytesIO
from typing import Literal

import aiohttp
import yaml
from PIL import Image
from pydantic import BaseModel, Field, field_validator

image_token_config_file_name = os.path.join(
    os.path.dirname(__file__), "openai_image_token_data.yaml"
)


class OpenAIImageTokenCalculator(BaseModel):
    model: str = Field(description="ID of the model to use.")

    @field_validator("model")
    @classmethod
    def validate_model_image_function(cls, value: str):
        with open(image_token_config_file_name) as file:
            token_config = yaml.safe_load(file)

        token_config = token_config.get(value, None)

        if token_config is None:
            raise ValueError("The model does not have vision capabilities.")
        return value

    @staticmethod
    async def get_image_size(url: str):
        if url.startswith("data:image/jpeg;base64,"):
            # base64 encoded format
            image_base64 = url.split("data:image/jpeg;base64,")[1]
            image_base64.strip("{}")
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
        else:
            # image url
            async with aiohttp.ClientSession() as client:
                async with client.get(url=url) as response:
                    response.raise_for_status()

                    content = await response.read()

                    image = Image.open(BytesIO(content))

        return image.size

    async def calculate(
        self, url: str, detail: Literal["low", "high", "auto"] = "auto"
    ):
        if detail not in ["low", "high", "auto"]:
            raise ValueError(
                "Invalid detail option. Valid options are: low, high, auto"
            )

        with open(image_token_config_file_name) as file:
            token_config = yaml.safe_load(file)

        token_config = token_config.get(self.model, None)

        if token_config is None:
            raise ValueError("The model does not have vision capabilities.")

        width, height = await self.get_image_size(url)

        if detail == "low":
            return token_config["base"]
        if detail == "auto":
            # TODO: check "auto" option condition
            if width <= 512 and height <= 512:
                return token_config["base"]

        # Scale to fit within a 2048 x 2048 square
        if max(width, height) > 2048:
            scale_factor = 2048 / max(width, height)
            width = int(width * scale_factor)
            height = int(height * scale_factor)

        # Scale such that the shortest side is 768px
        if min(width, height) > 768:
            scale_factor = 768 / min(width, height)
            width = int(width * scale_factor)
            height = int(height * scale_factor)

        # Calculate the number of 512px squares
        num_squares = math.ceil(width / 512) * math.ceil(height / 512)

        return num_squares * token_config["tile"] + token_config["base"]
