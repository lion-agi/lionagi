from typing import List, Optional

# translation.py
from pydantic import BaseModel, Field
from .types import WhisperModel, TranscriptionResponseFormat
from .transcription_models import TranscriptionResponse


class CreateTranslationRequest(BaseModel):
    file: bytes = Field(..., description="The audio file to translate")
    model: WhisperModel = Field(..., description="The model to use for translation")
    prompt: Optional[str] = Field(
        None,
        description="An optional text to guide the model's style or continue a previous audio segment",
    )
    response_format: TranscriptionResponseFormat = Field(
        default=TranscriptionResponseFormat.JSON,
        description="The format of the transcript output",
    )
    temperature: float = Field(
        default=0, ge=0, le=1, description="The sampling temperature"
    )


def create_translation(request: CreateTranslationRequest) -> TranscriptionResponse:
    """Translates audio into English."""
    ...
