from lion_core import CoreLib
from typing import Any, Mapping


# refactor this function to be separated for different cases of input
def calculate_num_token(
    payload: Mapping[str, Any] = None,
    api_endpoint: str = None,
    token_encoding_name: str = None,
) -> int:  # sourcery skip: avoid-builtin-shadow
    """
    Calculates the number of tokens required for a request based on the payload and API endpoint.

    The token calculation logic might vary based on different API endpoints and payload content.
    This method should be implemented in a subclass to provide the specific calculation logic
    for the OpenAI API.

    Parameters:
            payload (Mapping[str, Any]): The payload of the request.

            api_endpoint (str): The specific API endpoint for the request.

            token_encoding_name (str): The name of the token encoding method.

    Returns:
            int: The estimated number of tokens required for the request.

    Example:
            >>> rate_limiter = OpenAIRateLimiter(100, 200)
            >>> payload = {'prompt': 'Translate the following text:', 'max_tokens': 50}
            >>> rate_limiter.calculate_num_token(payload, 'completions')
            # Expected token calculation for the given payload and endpoint.
    """
    import tiktoken
    from .ln_image import ImageUtil

    token_encoding_name = token_encoding_name or "cl100k_base"
    encoding = tiktoken.get_encoding(token_encoding_name)
    if api_endpoint.endswith("completions"):
        max_tokens = payload.get("max_tokens", 15)
        n = payload.get("n", 1)
        completion_tokens = n * max_tokens
        if api_endpoint.startswith("chat/"):
            num_tokens = 0

            for message in payload["messages"]:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n

                _content = message.get("content")
                if isinstance(_content, str):
                    num_tokens += len(encoding.encode(_content))

                elif isinstance(_content, list):
                    for item in _content:
                        if isinstance(item, dict):
                            if "text" in item:
                                num_tokens += len(
                                    encoding.encode(CoreLib.to_str(item["text"]))
                                )
                            elif "image_url" in item:
                                a: str = item["image_url"]["url"]
                                if "data:image/jpeg;base64," in a:
                                    a = a.split("data:image/jpeg;base64,")[1].strip()
                                num_tokens += (
                                    ImageUtil.calculate_image_token_usage_from_base64(
                                        a, item.get("detail", "low")
                                    )
                                )
                                num_tokens += (
                                    20  # for every image we add 20 tokens buffer
                                )
                        elif isinstance(item, str):
                            num_tokens += len(encoding.encode(item))
                        else:
                            num_tokens += len(encoding.encode(str(item)))

            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens + completion_tokens
        else:
            prompt = payload["format_prompt"]
            if isinstance(prompt, str):  # single format_prompt
                prompt_tokens = len(encoding.encode(prompt))
                return prompt_tokens + completion_tokens
            elif isinstance(prompt, list):  # multiple prompts
                prompt_tokens = sum(len(encoding.encode(p)) for p in prompt)
                return prompt_tokens + completion_tokens * len(prompt)
            else:
                raise TypeError(
                    'Expecting either string or list of strings for "format_prompt" field in completion request'
                )
    elif api_endpoint == "embeddings":
        input = payload["input"]
        if isinstance(input, str):  # single input
            return len(encoding.encode(input))
        elif isinstance(input, list):  # multiple inputs
            return sum(len(encoding.encode(i)) for i in input)
        else:
            raise TypeError(
                'Expecting either string or list of strings for "inputs" field in embedding request'
            )
    else:
        raise NotImplementedError(
            f'API endpoint "{api_endpoint}" not implemented in this script'
        )
