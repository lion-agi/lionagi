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
