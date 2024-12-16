from pydantic import ConfigDict, Field

from ..data_models import OpenAIEndpointRequestBody
from .types import AudioFormat, TTSModel, Voice


class OpenAISpeechRequestBody(OpenAIEndpointRequestBody):
    model: TTSModel = Field(description="The TTS model to use")
    input: str = Field(
        description="The text to generate audio for", max_length=4096
    )
    voice: Voice = Field(
        description="The voice to use when generating the audio"
    )
    response_format: AudioFormat = Field(
        default=AudioFormat.MP3,
        description="The format of the generated audio",
    )
    speed: float = Field(
        default=1.0,
        ge=0.25,
        le=4.0,
        description="The speed of the generated audio",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "model": "tts-1",
                "input": "The quick brown fox jumped over the lazy dog.",
                "voice": "alloy",
            }
        }
    )
