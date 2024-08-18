import base64
from io import BytesIO

from lionagi.os.sys_util import SysUtil
from lionagi.os.file.tokenize.token_calculator import ImageTokenCalculator


class OpenAIImageTokenCalculator(ImageTokenCalculator):

    def __init__(self, config=None):
        super().__init__()
        self.config = config

    def calculate(self, image_base64: str, detail: str):
        if not image_base64:
            return 0

        return calculate_image_token_usage_from_base64(
            image_base64=image_base64,
            detail=detail,
            image_pricing=self.config,
        )


def calculate_image_token_usage_from_base64(image_base64: str, detail, image_pricing):
    """
    Calculate the token usage for processing OpenAI images from a
    base64-encoded string.

    Parameters:
    image_base64 (str): The base64-encoded string of the image.
    detail (str): The detail level of the image, either 'low' or 'high'.

    Returns:
    int: The total token cost for processing the image.
    """

    Image = SysUtil.check_import(
        package_name="PIL", import_name="Image", pip_name="Pillow"
    )

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

    # Scale to fit within a 2048 x 2048 square
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

    # Calculate the number of 512px squares
    num_squares = (width // image_pricing["square_size"]) * (
        height // image_pricing["square_size"]
    )
    token_cost = image_pricing["base_cost"] + image_pricing["square_cost"] * num_squares

    return token_cost
