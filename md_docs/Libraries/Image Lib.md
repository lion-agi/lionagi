# Image Utility API Reference

This module provides utility functions for preprocessing, encoding, reading, and calculating token usage for images.

## Functions

### `preprocess_image`
```python
preprocess_image(image: np.ndarray, color_conversion_code: Optional[int] = None) -> np.ndarray
```
Converts the color space of the given image. By default, it converts from BGR to RGB.

**Parameters**:
- `image` (`np.ndarray`): The input image in numpy array format.
- `color_conversion_code` (`Optional[int]`): The OpenCV color conversion code. Default is `cv2.COLOR_BGR2RGB`.

**Returns**:
- `np.ndarray`: The color-converted image.

### `encode_image_to_base64`
```python
encode_image_to_base64(image: np.ndarray, file_extension: str = ".jpg") -> str
```
Encodes the given image to a base64 string.

**Parameters**:
- `image` (`np.ndarray`): The input image in numpy array format.
- `file_extension` (`str`): The file extension for the image format. Default is ".jpg".

**Returns**:
- `str`: The base64-encoded string of the image.

**Raises**:
- `ValueError`: If the image cannot be encoded to the specified format.

### `read_image_to_array`
```python
read_image_to_array(image_path: str, color_flag: Optional[int] = None) -> np.ndarray
```
Reads an image from the specified path and returns it as a numpy array.

**Parameters**:
- `image_path` (`str`): The file path of the image to read.
- `color_flag` (`Optional[int]`): The OpenCV flag for color type. Default is `cv2.IMREAD_COLOR`.

**Returns**:
- `np.ndarray`: The image as a numpy array.

**Raises**:
- `ValueError`: If the image cannot be read from the specified path.

### `read_image_to_base64`
```python
read_image_to_base64(image_path: str, color_flag: Optional[int] = None) -> str
```
Reads an image from the specified path and encodes it to a base64 string.

**Parameters**:
- `image_path` (`str`): The file path of the image to read.
- `color_flag` (`Optional[int]`): The OpenCV flag for color type. Default is `cv2.IMREAD_COLOR`.

**Returns**:
- `str`: The base64-encoded string of the image.

**Raises**:
- `ValueError`: If the image cannot be read from the specified path.

### `calculate_image_token_usage_from_base64`
```python
calculate_image_token_usage_from_base64(image_base64: str, detail: str) -> int
```
Calculates the token usage for processing OpenAI images from a base64-encoded string.

**Parameters**:
- `image_base64` (`str`): The base64-encoded string of the image.
- `detail` (`str`): The detail level of the image, either 'low' or 'high'.

**Returns**:
- `int`: The total token cost for processing the image.

## Usage Examples

```python
import numpy as np
from lionagi.libs.image_util import ImageUtil

# Preprocess image
image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
processed_image = ImageUtil.preprocess_image(image)
print(processed_image.shape)  # Output: (100, 100, 3)

# Encode image to base64
encoded_image = ImageUtil.encode_image_to_base64(image)
print(encoded_image)  # Output: Base64 string of the image

# Read image to array
image_path = "path/to/image.jpg"
image_array = ImageUtil.read_image_to_array(image_path)
print(image_array.shape)  # Output: Shape of the image array

# Read image to base64
encoded_image = ImageUtil.read_image_to_base64(image_path)
print(encoded_image)  # Output: Base64 string of the image

# Calculate image token usage from base64
token_usage = ImageUtil.calculate_image_token_usage_from_base64(encoded_image, detail="high")
print(token_usage)  # Output: Token usage cost
```

These examples demonstrate how to use the various image utility functions provided by the `ImageUtil` class in the `ln_image` module. You can preprocess images, encode images to base64, read images to arrays or base64, and calculate token usage for processing images.
