import base64
from typing import Optional

import numpy as np

from lionagi.os.sys_utils import SysUtil


class ImageUtil:
    """Utility class for image processing operations."""

    cv2 = SysUtil.check_import("cv2", pip_name="opencv-python")

    @classmethod
    def preprocess_image(
        cls, image: np.ndarray, color_conversion_code: Optional[int] = None
    ) -> np.ndarray:
        """
        Preprocess an image by applying color conversion.

        Args:
            image: Input image as a numpy array.
            color_conversion_code: OpenCV color conversion code.

        Returns:
            Preprocessed image as a numpy array.
        """
        color_conversion_code = color_conversion_code or cls.cv2.COLOR_BGR2RGB
        return cls.cv2.cvtColor(image, color_conversion_code)

    @classmethod
    def encode_image_to_base64(
        cls, image: np.ndarray, file_extension: str = ".jpg"
    ) -> str:
        """
        Encode an image to base64 string.

        Args:
            image: Input image as a numpy array.
            file_extension: File extension for encoding.

        Returns:
            Base64 encoded string of the image.

        Raises:
            ValueError: If encoding fails.
        """
        success, buffer = cls.cv2.imencode(file_extension, image)
        if not success:
            raise ValueError(f"Could not encode image to {file_extension} format.")
        return base64.b64encode(buffer).decode("utf-8")

    @classmethod
    def read_image_to_array(
        cls, image_path: str, color_flag: Optional[int] = None
    ) -> np.ndarray:
        """
        Read an image file into a numpy array.

        Args:
            image_path: Path to the image file.
            color_flag: OpenCV color flag for reading the image.

        Returns:
            Image as a numpy array.

        Raises:
            ValueError: If the image cannot be read.
        """
        color_flag = color_flag or cls.cv2.IMREAD_COLOR
        image = cls.cv2.imread(image_path, color_flag)
        if image is None:
            raise ValueError(f"Could not read image from path: {image_path}")
        return image

    @classmethod
    def read_image_to_base64(
        cls,
        image_path: str,
        color_flag: Optional[int] = None,
    ) -> str:
        """
        Read an image file and encode it to base64 string.

        Args:
            image_path: Path to the image file.
            color_flag: OpenCV color flag for reading the image.

        Returns:
            Base64 encoded string of the image.
        """
        image = cls.read_image_to_array(image_path, color_flag)
        file_extension = "." + image_path.split(".")[-1]
        return cls.encode_image_to_base64(image, file_extension)


# File: lion_core/util/image_util.py
