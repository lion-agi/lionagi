# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

imported_models = {}


def match_response(request_model, response: dict | list):
    global imported_models

    endpoint = request_model.endpoint
    method = request_model.method

    # Messages endpoint
    if endpoint == "messages":
        if isinstance(response, dict):
            # Single message response
            if "AnthropicMessageResponseBody" not in imported_models:
                from .messages.response.response_body import (
                    AnthropicMessageResponseBody,
                )

                imported_models["AnthropicMessageResponseBody"] = (
                    AnthropicMessageResponseBody
                )

            # Convert to OpenAI-like format for AssistantResponse
            if response.get("content") and len(response["content"]) > 0:
                text_content = " ".join(
                    block["text"]
                    for block in response["content"]
                    if block["type"] == "text"
                )
                return {
                    "choices": [
                        {
                            "message": {
                                "content": text_content,
                                "role": "assistant",
                            }
                        }
                    ],
                    "model": response.get("model"),
                    "usage": response.get("usage", {}),
                }
            return response
        else:
            # Stream response list
            if "AnthropicMessageResponseBody" not in imported_models:
                from .messages.response.response_body import (
                    AnthropicMessageResponseBody,
                )

                imported_models["AnthropicMessageResponseBody"] = (
                    AnthropicMessageResponseBody
                )

            # For streaming, we need to convert each chunk to OpenAI format
            result = []
            for item in response:
                if "type" not in item:
                    continue

                if item.get("type") == "content_block_delta":
                    if text := item.get("delta", {}).get(
                        "type"
                    ) == "text_delta" and item.get("delta", {}).get(
                        "text", {}
                    ):
                        result.append(
                            {
                                "choices": [
                                    {
                                        "delta": {
                                            "content": item["delta"]["text"],
                                            "role": "assistant",
                                        }
                                    }
                                ]
                            }
                        )
                elif item.get("type") == "message_delta":
                    # Include usage updates
                    if "usage" in item:
                        result.append(
                            {
                                "choices": [
                                    {
                                        "delta": {
                                            "content": "",
                                            "role": "assistant",
                                        }
                                    }
                                ],
                                "usage": item["usage"],
                            }
                        )
                elif item.get("type") == "message_stop":
                    # Final message with stop reason
                    result.append(
                        {
                            "choices": [
                                {
                                    "delta": {
                                        "content": "",
                                        "role": "assistant",
                                    },
                                    "finish_reason": "stop",
                                }
                            ],
                            "usage": item.get("usage", {}),
                        }
                    )

            return result

    raise ValueError(
        "There is no standard response model for the provided request and response"
    )
