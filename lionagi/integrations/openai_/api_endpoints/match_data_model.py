def match_data_model(task_name):
    if task_name == "create_speech":
        from lionagi.integrations.openai_.api_endpoints.audio.speech_models import (
            OpenAISpeechRequestBody,
        )

        return {"request_body": OpenAISpeechRequestBody}
    elif task_name == "create_transcription":
        from lionagi.integrations.openai_.api_endpoints.audio.transcription_models import (
            OpenAITranscriptionRequestBody,
        )

        return {"request_body": OpenAITranscriptionRequestBody}
    elif task_name == "create_translation":
        from lionagi.integrations.openai_.api_endpoints.audio.translation_models import (
            OpenAITranslationRequestBody,
        )

        return {"request_body": OpenAITranslationRequestBody}
    elif task_name == "create_chat_completion":
        from lionagi.integrations.openai_.api_endpoints.chat_completions.request.request_body import (
            OpenAIChatCompletionRequestBody,
        )

        return {"request_body": OpenAIChatCompletionRequestBody}
    elif task_name == "create_embeddings":
        from lionagi.integrations.openai_.api_endpoints.embeddings.request_body import (
            OpenAIEmbeddingRequestBody,
        )

        return {"request_body": OpenAIEmbeddingRequestBody}
    elif task_name == "create_fine_tuning_job":
        from lionagi.integrations.openai_.api_endpoints.fine_tuning.create_jobs import (
            OpenAICreateFineTuningJobRequestBody,
        )

        return {"json_data": OpenAICreateFineTuningJobRequestBody}
    elif task_name == "list_fine_tuning_jobs":
        from lionagi.integrations.openai_.api_endpoints.fine_tuning.list_fine_tuning_jobs import (
            OpenAIListFineTuningJobsQueryParam,
        )

        return {"params": OpenAIListFineTuningJobsQueryParam}
    elif task_name == "list_fine_tuning_events":
        from lionagi.integrations.openai_.api_endpoints.fine_tuning.list_fine_tuning_events import (
            OpenAIListFineTuningEventsPathParam,
            OpenAIListFineTuningEventsQueryParam,
        )

        return {
            "params": OpenAIListFineTuningEventsQueryParam,
            "path_param": OpenAIListFineTuningEventsPathParam,
        }
    elif task_name == "list_fine_tuning_checkpoints":
        from lionagi.integrations.openai_.api_endpoints.fine_tuning.list_fine_tuning_checkpoints import (
            OpenAIListFineTuningCheckpointsPathParam,
            OpenAIListFineTuningCheckpointsQueryParam,
        )

        return {
            "params": OpenAIListFineTuningCheckpointsQueryParam,
            "path_param": OpenAIListFineTuningCheckpointsPathParam,
        }
    elif task_name == "retrieve_fine_tuning_job":
        from lionagi.integrations.openai_.api_endpoints.fine_tuning.retrieve_jobs import (
            OpenAIRetrieveFineTuningJobPathParam,
        )

        return {"path_param": OpenAIRetrieveFineTuningJobPathParam}
    elif task_name == "cancel_fine_tuning":
        from lionagi.integrations.openai_.api_endpoints.fine_tuning.cancel_jobs import (
            OpenAICancelFineTuningPathParam,
        )

        return {"path_param": OpenAICancelFineTuningPathParam}
    elif task_name == "create_batch":
        from lionagi.integrations.openai_.api_endpoints.batch.create_batch import (
            OpenAIBatchRequestBody,
        )

        return {"json_data": OpenAIBatchRequestBody}
    elif task_name == "retrieve_batch":
        from lionagi.integrations.openai_.api_endpoints.batch.retrieve_batch import (
            OpenAIRetrieveBatchPathParam,
        )

        return {"path_param": OpenAIRetrieveBatchPathParam}
    elif task_name == "cancel_batch":
        from lionagi.integrations.openai_.api_endpoints.batch.cancel_batch import (
            OpenAICancelBatchPathParam,
        )

        return {"path_param": OpenAICancelBatchPathParam}
    elif task_name == "list_batch":
        from lionagi.integrations.openai_.api_endpoints.batch.list_batch import (
            OpenAIListBatchQueryParam,
        )

        return {"params": OpenAIListBatchQueryParam}
    elif task_name == "upload_file":
        from lionagi.integrations.openai_.api_endpoints.files.upload_file import (
            OpenAIUploadFileRequestBody,
        )

        return {"form_data": OpenAIUploadFileRequestBody}
    elif task_name == "list_files":
        from lionagi.integrations.openai_.api_endpoints.files.list_files import (
            OpenAIListFilesQueryParam,
        )

        return {"params": OpenAIListFilesQueryParam}
    elif task_name == "retrieve_file" or task_name == "retrieve_file_content":
        from lionagi.integrations.openai_.api_endpoints.files.retrieve_file import (
            OpenAIRetrieveFilePathParam,
        )

        return {"path_param": OpenAIRetrieveFilePathParam}
    elif task_name == "delete_file":
        from lionagi.integrations.openai_.api_endpoints.files.delete_file import (
            OpenAIDeleteFilePathParam,
        )

        return {"path_param": OpenAIDeleteFilePathParam}
    elif task_name == "create_upload":
        from lionagi.integrations.openai_.api_endpoints.uploads.create_upload import (
            OpenAIUploadRequestBody,
        )

        return {"json_data": OpenAIUploadRequestBody}
    elif task_name == "add_upload_part":
        from lionagi.integrations.openai_.api_endpoints.uploads.add_upload_part import (
            OpenAIUploadPartPathParam,
            OpenAIUploadPartRequestBody,
        )

        return {
            "path_param": OpenAIUploadPartPathParam,
            "form_data": OpenAIUploadPartRequestBody,
        }
    elif task_name == "complete_upload":
        from lionagi.integrations.openai_.api_endpoints.uploads.complete_upload import (
            OpenAICompleteUploadPathParam,
            OpenAICompleteUploadRequestBody,
        )

        return {
            "path_param": OpenAICompleteUploadPathParam,
            "json_data": OpenAICompleteUploadRequestBody,
        }
    elif task_name == "cancel_upload":
        from lionagi.integrations.openai_.api_endpoints.uploads.cancel_upload import (
            OpenAICancelUploadPathParam,
        )

        return {"path_param": OpenAICancelUploadPathParam}
    elif task_name == "create_image":
        from lionagi.integrations.openai_.api_endpoints.images.image_models import (
            OpenAIImageRequestBody,
        )

        return {"json_data": OpenAIImageRequestBody}
    elif task_name == "create_image_edit":
        from lionagi.integrations.openai_.api_endpoints.images.image_edit_models import (
            OpenAIImageEditRequestBody,
        )

        return {"form_data": OpenAIImageEditRequestBody}
    elif task_name == "create_image_variation":
        from lionagi.integrations.openai_.api_endpoints.images.image_variation_models import (
            OpenAIImageVariationRequestBody,
        )

        return {"form_data": OpenAIImageVariationRequestBody}
    elif task_name == "list_models":
        return {}
    elif task_name == "retrieve_model":
        from lionagi.integrations.openai_.api_endpoints.models.retrieve_model import (
            OpenAIRetrieveModelPathParam,
        )

        return {"path_param": OpenAIRetrieveModelPathParam}
    elif task_name == "delete_fine_tuned_model":
        from lionagi.integrations.openai_.api_endpoints.models.delete_fine_tuned_model import (
            OpenAIDeleteFineTunedModelPathParam,
        )

        return {"path_param": OpenAIDeleteFineTunedModelPathParam}
    elif task_name == "create_moderation":
        from lionagi.integrations.openai_.api_endpoints.moderations.request_body import (
            OpenAIModerationRequestBody,
        )

        return {"json_data": OpenAIModerationRequestBody}
    else:
        raise ValueError(
            f"Invalid task: {task_name}. Not supported in the service."
        )
