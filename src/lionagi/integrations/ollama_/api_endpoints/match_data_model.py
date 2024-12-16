# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


def match_data_model(task_name):
    if task_name == "generate_completion":
        from .completion.request_body import OllamaCompletionRequestBody

        return {"request_body": OllamaCompletionRequestBody}

    elif task_name == "generate_chat_completion":
        from .chat_completion.request_body import (
            OllamaChatCompletionRequestBody,
        )

        return {"request_body": OllamaChatCompletionRequestBody}

    elif task_name == "generate_embeddings":
        from .embedding.request_body import OllamaEmbeddingRequestBody

        return {"request_body": OllamaEmbeddingRequestBody}

    elif task_name == "create_model":
        from .model.create_model import OllamaCreateModelRequestBody

        return {"json_data": OllamaCreateModelRequestBody}

    elif (
        task_name == "list_local_models" or task_name == "list_running_models"
    ):
        return {}

    elif task_name == "show_model_information":
        from .model.show_model import OllamaShowModelRequestBody

        return {"json_data": OllamaShowModelRequestBody}

    elif task_name == "copy_model":
        from .model.copy_model import OllamaCopyModelRequestBody

        return {"json_data": OllamaCopyModelRequestBody}

    elif task_name == "delete_model":
        from .model.delete_model import OllamaDeleteModelRequestBody

        return {"json_data": OllamaDeleteModelRequestBody}

    elif task_name == "pull_model":
        from .model.pull_model import OllamaPullModelRequestBody

        return {"json_data": OllamaPullModelRequestBody}

    elif task_name == "push_model":
        from .model.push_model import OllamaPushModelRequestBody

        return {"json_data": OllamaPushModelRequestBody}

    else:
        raise ValueError(
            f"Invalid task: {task_name}. Not supported in the service."
        )
