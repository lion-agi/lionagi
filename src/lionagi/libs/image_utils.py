import base64
from pathlib import Path

import numpy as np


class ImageUtil:

    from .imports_utils import check_import

    cv2 = check_import("cv2", pip_name="opencv-python")

    @classmethod
    def preprocess_image(
        cls, image: np.ndarray, color_conversion_code: int | None = None
    ):
        color_conversion_code = color_conversion_code or cls.cv2.COLOR_BGR2RGB
        return cls.cv2.cvtColor(image, color_conversion_code)

    @classmethod
    def encode_image_to_base64(
        cls, image: np.ndarray, file_extension: str = ".jpg"
    ) -> str:
        success, buffer = cls.cv2.imencode(file_extension, image)
        if not success:
            raise ValueError(
                f"Could not encode image to {file_extension} format."
            )
        encoded_image = base64.b64encode(buffer).decode("utf-8")
        return encoded_image

    @classmethod
    def read_image_to_array(
        cls, fp: Path | str, color_flag: int | None = None
    ):
        image = cls.cv2.imread(str(fp), color_flag)
        color_flag = color_flag or cls.cv2.IMREAD_COLOR
        if image is None:
            raise ValueError(f"Could not read image from path: {fp}")
        return image

    @classmethod
    def read_image_to_base64(
        cls, image_path: str, color_flag: int | None = None
    ) -> str:
        image_path = str(image_path)
        image = cls.read_image_to_array(image_path, color_flag)

        file_extension = "." + image_path.split(".")[-1]
        return cls.encode_image_to_base64(image, file_extension)
