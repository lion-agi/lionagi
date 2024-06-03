import base64
import numpy as np
from typing import Optional
from lionagi.os.libs.sys_util import check_import


class ImageUtil:

    @staticmethod
    def preprocess_image(
        image: np.ndarray, color_conversion_code: Optional[int] = None
    ) -> np.ndarray:
        check_import("cv2", pip_name="opencv-python")
        import cv2

        color_conversion_code = color_conversion_code or cv2.COLOR_BGR2RGB
        return cv2.cvtColor(image, color_conversion_code)

    @staticmethod
    def encode_image_to_base64(image: np.ndarray, file_extension: str = ".jpg") -> str:
        check_import("cv2", pip_name="opencv-python")
        import cv2

        success, buffer = cv2.imencode(file_extension, image)
        if not success:
            raise ValueError(f"Could not encode image to {file_extension} format.")
        encoded_image = base64.b64encode(buffer).decode("utf-8")
        return encoded_image

    @staticmethod
    def read_image_to_array(
        image_path: str, color_flag: Optional[int] = None
    ) -> np.ndarray:
        check_import("cv2", pip_name="opencv-python")
        import cv2

        image = cv2.imread(image_path, color_flag)
        color_flag = color_flag or cv2.IMREAD_COLOR
        if image is None:
            raise ValueError(f"Could not read image from path: {image_path}")
        return image

    @staticmethod
    def read_image_to_base64(
        image_path: str,
        color_flag: Optional[int] = None,
    ) -> str:
        image_path = str(image_path)
        image = ImageUtil.read_image_to_array(image_path, color_flag)

        file_extension = "." + image_path.split(".")[-1]
        return ImageUtil.encode_image_to_base64(image, file_extension)
