imported_models = {}


def match_response(request_model, response: dict | list):
    global imported_models

    endpoint = request_model.endpoint
    method = request_model.method

    # audio
    if "audio" in endpoint:
        # create transcription
        if endpoint == "audio/transcriptions":
            if len(response) == 1:
                # transcription object
                if "OpenAITranscriptionResponseBody" not in imported_models:
                    from .audio.transcription_models import (
                        OpenAITranscriptionResponseBody,
                    )

                    imported_models["OpenAITranscriptionResponseBody"] = (
                        OpenAITranscriptionResponseBody
                    )
                return imported_models["OpenAITranscriptionResponseBody"](
                    **response
                )
            else:
                # verbose transcription object
                if (
                    "OpenAIVerboseTranscriptionResponseBody"
                    not in imported_models
                ):
                    from .audio.transcription_models import (
                        OpenAIVerboseTranscriptionResponseBody,
                    )

                    imported_models[
                        "OpenAIVerboseTranscriptionResponseBody"
                    ] = OpenAIVerboseTranscriptionResponseBody
                return imported_models[
                    "OpenAIVerboseTranscriptionResponseBody"
                ](**response)

        # create translation
        if endpoint == "audio/translations":
            if "OpenAITranslationResponseBody" not in imported_models:
                from .audio.translation_models import (
                    OpenAITranslationResponseBody,
                )

                imported_models["OpenAITranslationResponseBody"] = (
                    OpenAITranslationResponseBody
                )
            return imported_models["OpenAITranslationResponseBody"](**response)

    # Chat
    elif endpoint == "chat/completions":
        if isinstance(response, dict):
            if "OpenAIChatCompletionResponseBody" not in imported_models:
                from .chat_completions.response.response_body import (
                    OpenAIChatCompletionResponseBody,
                )

                imported_models["OpenAIChatCompletionResponseBody"] = (
                    OpenAIChatCompletionResponseBody
                )
            return imported_models["OpenAIChatCompletionResponseBody"](
                **response
            )
        else:
            # stream list
            if "OpenAIChatCompletionChunkResponseBody" not in imported_models:
                from .chat_completions.response.response_body import (
                    OpenAIChatCompletionChunkResponseBody,
                )

                imported_models["OpenAIChatCompletionChunkResponseBody"] = (
                    OpenAIChatCompletionChunkResponseBody
                )
            result = []
            for item in response:
                result.append(
                    imported_models["OpenAIChatCompletionChunkResponseBody"](
                        **item
                    )
                )
            return result

    # Embeddings
    elif endpoint == "embeddings":
        if "OpenAIEmbeddingResponseBody" not in imported_models:
            from .embeddings.response_body import OpenAIEmbeddingResponseBody

            imported_models["OpenAIEmbeddingResponseBody"] = (
                OpenAIEmbeddingResponseBody
            )
        return imported_models["OpenAIEmbeddingResponseBody"](**response)

    # Fine-tuning
    elif "fine_tuning" in endpoint:
        # create fine-tuning job
        if endpoint == "fine_tuning/jobs" and method == "POST":
            if "OpenAIFineTuningJobResponseBody" not in imported_models:
                from .fine_tuning.fine_tuning_job_models import (
                    OpenAIFineTuningJobResponseBody,
                )

                imported_models["OpenAIFineTuningJobResponseBody"] = (
                    OpenAIFineTuningJobResponseBody
                )
            return imported_models["OpenAIFineTuningJobResponseBody"](
                **response
            )

        # list fine-tuning jobs
        if endpoint == "fine_tuning/jobs" and method == "GET":
            if "OpenAIListFineTuningJobsResponseBody" not in imported_models:
                from .fine_tuning.list_fine_tuning_jobs import (
                    OpenAIListFineTuningJobsResponseBody,
                )

                imported_models["OpenAIListFineTuningJobsResponseBody"] = (
                    OpenAIListFineTuningJobsResponseBody
                )
            return imported_models["OpenAIListFineTuningJobsResponseBody"](
                **response
            )

        # list fine-tuning events
        if endpoint == "fine_tuning/jobs/{fine_tuning_job_id}/events":
            if "OpenAIListFineTuningEventsResponseBody" not in imported_models:
                from .fine_tuning.list_fine_tuning_events import (
                    OpenAIListFineTuningEventsResponseBody,
                )

                imported_models["OpenAIListFineTuningEventsResponseBody"] = (
                    OpenAIListFineTuningEventsResponseBody
                )
            return imported_models["OpenAIListFineTuningEventsResponseBody"](
                **response
            )

        # list fine-tuning checkpoints
        if endpoint == "fine_tuning/jobs/{fine_tuning_job_id}/checkpoints":
            if (
                "OpenAIListFineTuningCheckpointsResponseBody"
                not in imported_models
            ):
                from .fine_tuning.list_fine_tuning_checkpoints import (
                    OpenAIListFineTuningCheckpointsResponseBody,
                )

                imported_models[
                    "OpenAIListFineTuningCheckpointsResponseBody"
                ] = OpenAIListFineTuningCheckpointsResponseBody
            return imported_models[
                "OpenAIListFineTuningCheckpointsResponseBody"
            ](**response)

        # retrieve fine-tuning job
        if endpoint == "fine_tuning/jobs/{fine_tuning_job_id}":
            if "OpenAIFineTuningJobResponseBody" not in imported_models:
                from .fine_tuning.fine_tuning_job_models import (
                    OpenAIFineTuningJobResponseBody,
                )

                imported_models["OpenAIFineTuningJobResponseBody"] = (
                    OpenAIFineTuningJobResponseBody
                )
            return imported_models["OpenAIFineTuningJobResponseBody"](
                **response
            )

        # cancel fine-tuning
        # TODO: need verification
        if endpoint == "fine_tuning/jobs/{fine_tuning_job_id}/cancel":
            if "OpenAIFineTuningJobResponseBody" not in imported_models:
                from .fine_tuning.fine_tuning_job_models import (
                    OpenAIFineTuningJobResponseBody,
                )

                imported_models["OpenAIFineTuningJobResponseBody"] = (
                    OpenAIFineTuningJobResponseBody
                )
            return imported_models["OpenAIFineTuningJobResponseBody"](
                **response
            )

    # Batch
    elif "batches" in endpoint:
        if endpoint == "batches" and method == "GET":
            # list batch
            if "OpenAIListBatchResponseBody" not in imported_models:
                from .batch.list_batch import OpenAIListBatchResponseBody

                imported_models["OpenAIListBatchResponseBody"] = (
                    OpenAIListBatchResponseBody
                )
            return imported_models["OpenAIListBatchResponseBody"](**response)
        else:
            # other batch endpoints
            if "OpenAIBatchResponseBody" not in imported_models:
                from .batch.batch_models import OpenAIBatchResponseBody

                imported_models["OpenAIBatchResponseBody"] = (
                    OpenAIBatchResponseBody
                )
            return imported_models["OpenAIBatchResponseBody"](**response)

    # Files
    elif "files" in endpoint:
        # upload file
        if endpoint == "files" and method == "POST":
            if "OpenAIFileResponseBody" not in imported_models:
                from .files.file_models import OpenAIFileResponseBody

                imported_models["OpenAIFileResponseBody"] = (
                    OpenAIFileResponseBody
                )
            return imported_models["OpenAIFileResponseBody"](**response)

        # list files
        if endpoint == "files" and method == "GET":
            if "OpenAIListFilesResponseBody" not in imported_models:
                from .files.list_files import OpenAIListFilesResponseBody

                imported_models["OpenAIListFilesResponseBody"] = (
                    OpenAIListFilesResponseBody
                )
            return imported_models["OpenAIListFilesResponseBody"](**response)

        # retrieve file
        if endpoint == "files/{file_id}" and method == "GET":
            if "OpenAIFileResponseBody" not in imported_models:
                from .files.file_models import OpenAIFileResponseBody

                imported_models["OpenAIFileResponseBody"] = (
                    OpenAIFileResponseBody
                )
            return imported_models["OpenAIFileResponseBody"](**response)

        # delete file
        if endpoint == "files/{file_id}" and method == "DELETE":
            if "OpenAIDeleteFileResponseBody" not in imported_models:
                from .files.delete_file import OpenAIDeleteFileResponseBody

                imported_models["OpenAIDeleteFileResponseBody"] = (
                    OpenAIDeleteFileResponseBody
                )
            return imported_models["OpenAIDeleteFileResponseBody"](**response)

        # retrieve file content
        if endpoint == "files/{file_id}/content":
            return response

    # Uploads
    if "uploads" in endpoint:
        if endpoint == "uploads/{upload_id}/parts":
            # add upload part
            if "OpenAIUploadPartResponseBody" not in imported_models:
                from .uploads.uploads_models import (
                    OpenAIUploadPartResponseBody,
                )

                imported_models["OpenAIUploadPartResponseBody"] = (
                    OpenAIUploadPartResponseBody
                )
            return imported_models["OpenAIUploadPartResponseBody"](**response)
        else:
            # other upload endpoints
            if "OpenAIUploadResponseBody" not in imported_models:
                from .uploads.uploads_models import OpenAIUploadResponseBody

                imported_models["OpenAIUploadResponseBody"] = (
                    OpenAIUploadResponseBody
                )
            return imported_models["OpenAIUploadResponseBody"](**response)

    # Images
    if "images" in endpoint:
        if "OpenAIImageResponseBody" not in imported_models:
            from .images.response_body import OpenAIImageResponseBody

            imported_models["OpenAIImageResponseBody"] = (
                OpenAIImageResponseBody
            )
        return imported_models["OpenAIImageResponseBody"](**response)

    if "models" in endpoint:
        # list models
        if endpoint == "models":
            if "OpenAIListModelResponseBody" not in imported_models:
                from .models.models_models import OpenAIListModelResponseBody

                imported_models["OpenAIListModelResponseBody"] = (
                    OpenAIListModelResponseBody
                )
            return imported_models["OpenAIListModelResponseBody"](**response)

        # retrieve model
        if endpoint == "models/{model}" and method == "GET":
            if "OpenAIModelResponseBody" not in imported_models:
                from .models.models_models import OpenAIModelResponseBody

                imported_models["OpenAIModelResponseBody"] = (
                    OpenAIModelResponseBody
                )
            return imported_models["OpenAIModelResponseBody"](**response)

        # delete a fine-tuned model
        if endpoint == "models/{model}" and method == "DELETE":
            if "OpenAIDeleteFineTunedModelResponseBody" not in imported_models:
                from .models.delete_fine_tuned_model import (
                    OpenAIDeleteFineTunedModelResponseBody,
                )

                imported_models["OpenAIDeleteFineTunedModelResponseBody"] = (
                    OpenAIDeleteFineTunedModelResponseBody
                )
            return imported_models["OpenAIDeleteFineTunedModelResponseBody"](
                **response
            )

    # Moderation
    if endpoint == "moderations":
        if "OpenAIModerationResponseBody" not in imported_models:
            from .moderations.response_body import OpenAIModerationResponseBody

            imported_models["OpenAIModerationResponseBody"] = (
                OpenAIModerationResponseBody
            )
        return imported_models["OpenAIModerationResponseBody"](**response)

    raise ValueError(
        "There is no standard response model for the provided request and response"
    )
