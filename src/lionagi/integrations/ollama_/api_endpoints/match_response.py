# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

imported_models = {}


def match_response(request_model, response: dict | list):
    global imported_models

    endpoint = request_model.endpoint

    if endpoint == "generate":
        if isinstance(response, list):
            if "OllamaStreamCompletionResponseBody" not in imported_models:
                from .completion.response_body import (
                    OllamaStreamCompletionResponseBody,
                )

                imported_models["OllamaStreamCompletionResponseBody"] = (
                    OllamaStreamCompletionResponseBody
                )
            if "OllamaCompletionResponseBody" not in imported_models:
                from .completion.response_body import (
                    OllamaCompletionResponseBody,
                )

                imported_models["OllamaCompletionResponseBody"] = (
                    OllamaCompletionResponseBody
                )

            result = []
            for item in response[:-1]:
                result.append(
                    imported_models["OllamaStreamCompletionResponseBody"](
                        **item
                    )
                )

            result.append(
                imported_models["OllamaCompletionResponseBody"](**response[-1])
            )
            return result
        else:
            if "OllamaCompletionResponseBody" not in imported_models:
                from .completion.response_body import (
                    OllamaCompletionResponseBody,
                )

                imported_models["OllamaCompletionResponseBody"] = (
                    OllamaCompletionResponseBody
                )
            return imported_models["OllamaCompletionResponseBody"](**response)

    elif endpoint == "chat":
        if isinstance(response, list):
            if "OllamaStreamChatCompletionResponseBody" not in imported_models:
                from .chat_completion.response_body import (
                    OllamaStreamChatCompletionResponseBody,
                )

                imported_models["OllamaStreamChatCompletionResponseBody"] = (
                    OllamaStreamChatCompletionResponseBody
                )
            if "OllamaChatCompletionResponseBody" not in imported_models:
                from .chat_completion.response_body import (
                    OllamaChatCompletionResponseBody,
                )

                imported_models["OllamaChatCompletionResponseBody"] = (
                    OllamaChatCompletionResponseBody
                )

            result = []
            for item in response[:-1]:
                result.append(
                    imported_models["OllamaStreamChatCompletionResponseBody"](
                        **item
                    )
                )

            result.append(
                imported_models["OllamaChatCompletionResponseBody"](
                    **response[-1]
                )
            )
            return result
        else:
            if "OllamaChatCompletionResponseBody" not in imported_models:
                from .chat_completion.response_body import (
                    OllamaChatCompletionResponseBody,
                )

                imported_models["OllamaChatCompletionResponseBody"] = (
                    OllamaChatCompletionResponseBody
                )
            return imported_models["OllamaChatCompletionResponseBody"](
                **response
            )

    elif endpoint == "embed":
        if "OllamaEmbeddingResponseBody" not in imported_models:
            from .embedding.response_body import OllamaEmbeddingResponseBody

            imported_models["OllamaEmbeddingResponseBody"] = (
                OllamaEmbeddingResponseBody
            )
        return imported_models["OllamaEmbeddingResponseBody"](**response)

    elif endpoint == "create":
        if "OllamaCreateModelResponseBody" not in imported_models:
            from .model.create_model import OllamaCreateModelResponseBody

            imported_models["OllamaCreateModelResponseBody"] = (
                OllamaCreateModelResponseBody
            )
        if isinstance(response, list):
            return [
                imported_models["OllamaCreateModelResponseBody"](**res)
                for res in response
            ]
        else:  # dict
            return imported_models["OllamaCreateModelResponseBody"](**response)

    elif endpoint == "tags":
        if "OllamaListLocalModelsResponseBody" not in imported_models:
            from .model.list_model import OllamaListLocalModelsResponseBody

            imported_models["OllamaListLocalModelsResponseBody"] = (
                OllamaListLocalModelsResponseBody
            )
        return imported_models["OllamaListLocalModelsResponseBody"](**response)

    elif endpoint == "show":
        if "OllamaShowModelResponseBody" not in imported_models:
            from .model.show_model import OllamaShowModelResponseBody

            imported_models["OllamaShowModelResponseBody"] = (
                OllamaShowModelResponseBody
            )
        return imported_models["OllamaShowModelResponseBody"](**response)

    elif endpoint == "pull":
        if "OllamaPullModelResponseBody" not in imported_models:
            from .model.pull_model import OllamaPullModelResponseBody

            imported_models["OllamaPullModelResponseBody"] = (
                OllamaPullModelResponseBody
            )
        if isinstance(response, list):
            return [
                imported_models["OllamaPullModelResponseBody"](**res)
                for res in response
            ]
        else:  # dict
            return imported_models["OllamaPullModelResponseBody"](**response)

    elif endpoint == "push":
        if "OllamaPushModelResponseBody" not in imported_models:
            from .model.push_model import OllamaPushModelResponseBody

            imported_models["OllamaPushModelResponseBody"] = (
                OllamaPushModelResponseBody
            )
        if isinstance(response, list):
            return [
                imported_models["OllamaPushModelResponseBody"](**res)
                for res in response
            ]
        else:  # dict
            return imported_models["OllamaPushModelResponseBody"](**response)

    elif endpoint == "ps":
        if "OllamaListRunningModelsResponseBody" not in imported_models:
            from .model.list_model import OllamaListRunningModelsResponseBody

            imported_models["OllamaListRunningModelsResponseBody"] = (
                OllamaListRunningModelsResponseBody
            )
        return imported_models["OllamaListRunningModelsResponseBody"](
            **response
        )

    elif not response:
        return

    else:
        raise ValueError(
            "There is no standard response model for the provided request and response"
        )
