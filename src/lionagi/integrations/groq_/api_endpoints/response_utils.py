# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from .data_models import GroqAudioResponse, GroqChatCompletionResponse


def match_response(
    request_model: Any,
    response: dict[str, Any] | list[dict[str, Any]] | None,
) -> dict[str, Any] | list[dict[str, Any]] | None:
    """Match response to appropriate model and format."""
    if response is None:
        return None

    endpoint = request_model.endpoint.split("/")[0]

    # Chat completions endpoint
    if endpoint == "chat":
        if isinstance(response, dict):
            # Single response
            try:
                # Validate and parse through Pydantic model
                parsed = GroqChatCompletionResponse(**response)
                # Return in consistent format
                return {
                    "choices": parsed.choices,
                    "model": parsed.model,
                    "usage": parsed.usage,
                }
            except Exception as e:
                import warnings

                warnings.warn(f"Failed to parse chat response: {str(e)}")
                return response
        else:
            # Stream response list
            result = []
            for chunk in response:
                if not isinstance(chunk, dict):
                    continue

                try:
                    if "choices" in chunk:
                        # Regular chunk with content
                        result.append(
                            {
                                "choices": [
                                    {
                                        "delta": {
                                            "content": choice.get(
                                                "delta", {}
                                            ).get("content", ""),
                                            "role": "assistant",
                                        }
                                    }
                                    for choice in chunk["choices"]
                                ]
                            }
                        )

                        # Add usage if present
                        if "usage" in chunk:
                            result[-1]["usage"] = chunk["usage"]

                    elif "usage" in chunk:
                        # Final chunk with usage stats
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
                                "usage": chunk["usage"],
                            }
                        )
                except Exception as e:
                    import warnings

                    warnings.warn(f"Failed to parse stream chunk: {str(e)}")
                    continue

            return result

    # Audio endpoints
    elif endpoint == "audio":
        try:
            if isinstance(response, dict):
                parsed = GroqAudioResponse(**response)
                return {"text": parsed.text, "metadata": parsed.x_groq}
        except Exception as e:
            import warnings

            warnings.warn(f"Failed to parse audio response: {str(e)}")
            return response

    # Default case
    return response
