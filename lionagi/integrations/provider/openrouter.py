from os import getenv

from lionagi.integrations.config.openrouter_configs import openrouter_schema
from lionagi.libs.ln_api import BaseService, PayloadPackage

allowed_kwargs = [
    "model",
    "frequency_penalty",
    "n",
    "presence_penalty",
    "response_format",
    "temperature",
    "top_p",
    "seed",
    "stop",
    "stream",
    "stream_options",
    "tools",
    "tool_choice",
    "user",
    "max_tokens",
    "logprobs",
    "top_logprobs",
    "logit_bias",
]


class OpenRouterService(BaseService):
    base_url = "https://openrouter.ai/api/v1/"
    available_endpoints = ["chat/completions"]
    schema = openrouter_schema
    key_scheme = "OPENROUTER_API_KEY"
    token_encoding_name = "cl100k_base"

    def __init__(
        self,
        api_key=None,
        key_scheme=None,
        schema=None,
        token_encoding_name: str = "cl100k_base",
        **kwargs,
    ):
        key_scheme = key_scheme or self.key_scheme
        super().__init__(
            api_key=api_key or getenv(key_scheme),
            schema=schema or self.schema,
            token_encoding_name=token_encoding_name,
            **kwargs,
        )
        self.active_endpoint = []
        self.allowed_kwargs = allowed_kwargs

    async def serve(
        self, input_, endpoint="chat/completions", method="post", **kwargs
    ):
        """
        Serves the input using the specified endpoint and method.

        Args:
                input_: The input text to be processed.
                endpoint: The API endpoint to use for processing.
                method: The HTTP method to use for the request.
                **kwargs: Additional keyword arguments to pass to the payload creation.

        Returns:
                A tuple containing the payload and the completion assistant_response from the API.

        Raises:
                ValueError: If the specified endpoint is not supported.

        Examples:
                >>> service = OpenAIService(api_key="your_api_key")
                >>> asyncio.run(service.serve("Hello, world!","chat/completions"))
                (payload, completion)

                >>> service = OpenAIService()
                >>> asyncio.run(service.serve("Convert this text to speech.","audio_speech"))
                ValueError: 'audio_speech' is currently not supported
        """
        if endpoint not in self.active_endpoint:
            await self.init_endpoint(endpoint)
        if endpoint == "chat/completions":
            return await self.serve_chat(input_, **kwargs)
        else:
            return ValueError(f"{endpoint} is currently not supported")

    async def serve_chat(self, messages, required_tokens=None, **kwargs):
        """
        Serves the chat completion request with the given messages.

        Args:
                messages: The messages to be included in the chat completion.
                **kwargs: Additional keyword arguments for payload creation.

        Returns:
                A tuple containing the payload and the completion assistant_response from the API.

        Raises:
                Exception: If the API call fails.
        """
        if "chat/completions" not in self.active_endpoint:
            await self.init_endpoint("chat/completions")
            self.active_endpoint.append("chat/completions")

        msgs = []

        for msg in messages:
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, (dict, str)):
                    msgs.append({"role": msg["role"], "content": content})
                elif isinstance(content, list):
                    _content = []
                    for i in content:
                        if "text" in i:
                            _content.append(
                                {"type": "text", "text": str(i["text"])}
                            )
                        elif "image_url" in i:
                            _content.append(
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"{i['image_url'].get('url')}",
                                        "detail": i["image_url"].get(
                                            "detail", "low"
                                        ),
                                    },
                                }
                            )
                    msgs.append({"role": msg["role"], "content": _content})

        payload = PayloadPackage.chat_completion(
            msgs,
            self.endpoints["chat/completions"].config,
            self.schema["chat/completions"],
            **kwargs,
        )
        try:
            completion = await self.call_api(
                payload,
                "chat/completions",
                "post",
                required_tokens=required_tokens,
            )
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e

    # async def serve_embedding(self, embed_str, required_tokens=None, **kwargs):
    #     if "embeddings" not in self.active_endpoint:
    #         await self.init_endpoint("embeddings")
    #         self.active_endpoint.append("embeddings")

    #     payload = PayloadPackage.embeddings(
    #         embed_str,
    #         self.endpoints["embeddings"].config,
    #         self.schema["embeddings"],
    #         **kwargs,
    #     )

    #     try:
    #         embed = await self.call_api(
    #             payload, "embeddings", "post", required_tokens=required_tokens
    #         )
    #         return payload, embed
    #     except Exception as e:
    #         self.status_tracker.num_tasks_failed += 1
    #         raise e
