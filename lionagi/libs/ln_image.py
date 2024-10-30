import base64
from typing import Optional

import numpy as np

from .sys_util import SysUtil


class ImageUtil:

    @staticmethod
    def preprocess_image(
        image: np.ndarray, color_conversion_code: int | None = None
    ) -> np.ndarray:
        SysUtil.check_import("cv2", pip_name="opencv-python")
        import cv2

        color_conversion_code = color_conversion_code or cv2.COLOR_BGR2RGB
        return cv2.cvtColor(image, color_conversion_code)

    @staticmethod
    def encode_image_to_base64(
        image: np.ndarray, file_extension: str = ".jpg"
    ) -> str:
        SysUtil.check_import("cv2", pip_name="opencv-python")
        import cv2

        success, buffer = cv2.imencode(file_extension, image)
        if not success:
            raise ValueError(
                f"Could not encode image to {file_extension} format."
            )
        encoded_image = base64.b64encode(buffer).decode("utf-8")
        return encoded_image

    @staticmethod
    def read_image_to_array(
        image_path: str, color_flag: int | None = None
    ) -> np.ndarray:
        SysUtil.check_import("cv2", pip_name="opencv-python")
        import cv2

        image = cv2.imread(image_path, color_flag)
        color_flag = color_flag or cv2.IMREAD_COLOR
        if image is None:
            raise ValueError(f"Could not read image from path: {image_path}")
        return image

    @staticmethod
    def read_image_to_base64(
        image_path: str,
        color_flag: int | None = None,
    ) -> str:
        image_path = str(image_path)
        image = ImageUtil.read_image_to_array(image_path, color_flag)

        file_extension = "." + image_path.split(".")[-1]
        return ImageUtil.encode_image_to_base64(image, file_extension)

    # @staticmethod
    # def encode_image(image_path):
    #     with open(image_path, "rb") as image_file:
    #         return base64.b64encode(image_file.read()).decode("utf-8")

    @staticmethod
    def calculate_image_token_usage_from_base64(image_base64: str, detail):
        """
        Calculate the token usage for processing OpenAI images from a base64-encoded string.

        Parameters:
        image_base64 (str): The base64-encoded string of the image.
        detail (str): The detail level of the image, either 'low' or 'high'.

        Returns:
        int: The total token cost for processing the image.
        """
        import base64
        from io import BytesIO

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
            return 85

        # Scale to fit within a 2048 x 2048 square
        max_dimension = 2048
        if width > max_dimension or height > max_dimension:
            scale_factor = max_dimension / max(width, height)
            width = int(width * scale_factor)
            height = int(height * scale_factor)

        # Scale such that the shortest side is 768px
        min_side = 768
        if min(width, height) > min_side:
            scale_factor = min_side / min(width, height)
            width = int(width * scale_factor)
            height = int(height * scale_factor)

        # Calculate the number of 512px squares
        num_squares = (width // 512) * (height // 512)
        token_cost = 170 * num_squares + 85

        return token_cost
