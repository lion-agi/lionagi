# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import base64
from collections.abc import Callable
from io import BytesIO

import tiktoken

GPT4O_IMAGE_PRICING = {
    "base_cost": 85,
    "low_detail": 0,
    "max_dimension": 2048,
    "min_side": 768,
    "tile_size": 512,
    "tile_cost": 170,
}

GPT4O_MINI_IMAGE_PRICING = {
    "base_cost": 2833,
    "low_detail": 0,
    "max_dimension": 2048,
    "min_side": 768,
    "tile_size": 512,
    "tile_cost": 5667,
}

O1_IMAGE_PRICING = {
    "base_cost": 75,
    "low_detail": 0,
    "max_dimension": 2048,
    "min_side": 768,
    "tile_size": 512,
    "tile_cost": 150,
}


def calculate_image_token_usage_from_base64(
    image_base64: str, detail, image_pricing
):
    from PIL import Image

    # Decode the base64 string to get image data
    if "data:image/jpeg;base64," in image_base64:
        image_base64 = image_base64.split("data:image/jpeg;base64,")[1]
        image_base64.strip("{}")

    image_data = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_data))

    # Get image dimensions
    width, height = image.size

    if detail == "low":
        return image_pricing["base_cost"] + image_pricing["low_detail"]

    # Scale to fit within a 2048 x 2048 tile
    max_dimension = image_pricing["max_dimension"]
    if width > max_dimension or height > max_dimension:
        scale_factor = max_dimension / max(width, height)
        width = int(width * scale_factor)
        height = int(height * scale_factor)

    # Scale such that the shortest side is 768px
    min_side = image_pricing["min_side"]
    if min(width, height) > min_side:
        scale_factor = min_side / min(width, height)
        width = int(width * scale_factor)
        height = int(height * scale_factor)

    # Calculate the number of 512px tiles
    num_tiles = (width // image_pricing["tile_size"]) * (
        height // image_pricing["tile_size"]
    )
    token_cost = (
        image_pricing["base_cost"] + image_pricing["tile_cost"] * num_tiles
    )

    return token_cost


def get_encoding_name(value: str) -> str:
    try:
        enc = tiktoken.encoding_for_model(value)
        return enc.name
    except:
        try:
            tiktoken.get_encoding(value)
            return value
        except Exception:
            return "o200k_base"


def get_image_pricing(model: str) -> dict:
    if "gpt-4o-mini" in model:
        return GPT4O_MINI_IMAGE_PRICING
    elif "gpt-4o" in model:
        return GPT4O_IMAGE_PRICING
    elif "o1" in model and "mini" not in model:
        return O1_IMAGE_PRICING
    else:
        raise ValueError("Invalid model name")


class TokenCalculator:

    @staticmethod
    def calculate_message_tokens(messages: list[dict], /, **kwargs) -> int:

        model = kwargs.get("model", "gpt-4o")
        tokenizer = tiktoken.get_encoding(get_encoding_name(model)).encode

        num_tokens = 0
        for msg in messages:
            num_tokens += 4
            _c = msg.get("content")
            num_tokens += TokenCalculator._calculate_chatitem(
                _c, tokenizer=tokenizer, model_name=model
            )
        return num_tokens  # buffer for chat

    @staticmethod
    def calcualte_embed_token(inputs: list[str], /, **kwargs) -> int:
        try:
            if not "inputs" in kwargs:
                raise ValueError("Missing 'inputs' field in payload")

            tokenizer = tiktoken.get_encoding(
                get_encoding_name(
                    kwargs.get("model", "text-embedding-3-small")
                )
            ).encode

            return sum(
                TokenCalculator._calculate_embed_item(i, tokenizer=tokenizer)
                for i in inputs
            )
        except Exception:
            return 0

    @staticmethod
    def tokenize(
        s_: str = None,
        /,
        encoding_name: str | None = None,
        tokenizer: Callable | None = None,
        return_tokens: bool = False,
    ) -> int | list[int]:

        if not s_:
            return 0

        if not callable(tokenizer):
            encoding_name = get_encoding_name(encoding_name)
            tokenizer = tiktoken.get_encoding(encoding_name).encode
        try:
            if return_tokens:
                return tokenizer(s_)
            return len(tokenizer(s_))
        except Exception:
            return 0

    @staticmethod
    def _calculate_chatitem(i_, tokenizer: Callable, model_name: str) -> int:
        try:
            if isinstance(i_, str):
                return TokenCalculator.tokenize(
                    i_, encoding_name=model_name, tokenizer=tokenizer
                )

            if isinstance(i_, dict):
                if "text" in i_:
                    return TokenCalculator._calculate_chatitem(str(i_["text"]))
                elif "image_url" in i_:
                    a: str = i_["image_url"].get("url", "")
                    if "data:image/jpeg;base64," in a:
                        a = a.split("data:image/jpeg;base64,")[1].strip()
                        pricing = get_image_pricing(model_name)
                        return (
                            calculate_image_token_usage_from_base64(
                                a, i_.get("detail", "low"), pricing
                            )
                            + 15  # buffer for image
                        )

            if isinstance(i_, list):
                return sum(
                    TokenCalculator._calculate_chatitem(
                        x, tokenizer, model_name
                    )
                    for x in i_
                )
        except Exception:
            return 0

    @staticmethod
    def _calculate_embed_item(s_, tokenizer: Callable) -> int:
        try:
            if isinstance(s_, str):
                return TokenCalculator.tokenize(s_, tokenizer=tokenizer)

            if isinstance(s_, list):
                return sum(
                    TokenCalculator._calculate_embed_item(x, tokenizer)
                    for x in s_
                )
        except Exception:
            return 0
