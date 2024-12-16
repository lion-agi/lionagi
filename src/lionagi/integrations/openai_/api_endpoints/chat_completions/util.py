from .request.request_body import OpenAIChatCompletionRequestBody


def get_text_messages(request_body: OpenAIChatCompletionRequestBody):
    messages_list = request_body.model_dump(exclude_unset=True).get("messages")
    parsed_str = "["

    for msg in messages_list:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if isinstance(
            content, list
        ):  # Check if content is a list (second example)
            content_str = []
            for sub_content in content:
                if sub_content.get("type") == "text":
                    content_str.append(f'{sub_content.get("text", "")}')
            content = " ".join(
                content_str
            )  # Combine all sub_content items into a single string
        parsed_str += f"role: {role} content: {content} "

    parsed_str = parsed_str.strip()  # Remove trailing space
    parsed_str += "]"

    return parsed_str


def get_images(request_body: OpenAIChatCompletionRequestBody):
    messages_list = request_body.model_dump(exclude_unset=True).get("messages")
    image_urls = []

    for msg in messages_list:
        content = msg.get("content", "")

        if isinstance(
            content, list
        ):  # Check if content is a list (second example)
            for sub_content in content:
                if sub_content.get("type") == "image_url":
                    image_url = sub_content.get("image_url")
                    url = image_url.get("url")
                    detail = image_url.get("detail", "auto")
                    image_urls.append((url, detail))
    return image_urls
