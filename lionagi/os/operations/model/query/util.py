"""Image Manipulation Utilities."""

import base64
from io import BytesIO
from typing import cast

from PIL import Image


def image_to_base64(image: Image, format: str = "JPEG") -> str:
    """Convert a PIL.Image to a base64 encoded string."""
    buffer = BytesIO()
    image.save(buffer, format=format)
    return cast(str, base64.b64encode(buffer.getvalue()))


def base64_to_image(data: str) -> Image:
    """Convert a base64 encoded string to a PIL.Image."""
    buffer = BytesIO(base64.b64decode(data))
    return Image.open(buffer)
