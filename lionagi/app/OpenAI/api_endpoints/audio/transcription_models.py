from typing import List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict
from .types import WhisperModel, TranscriptionResponseFormat, TimestampGranularity


class CreateTranscriptionRequest(BaseModel):
    file: bytes = Field(..., description="The audio file to transcribe")
    model: WhisperModel = Field(..., description="The model to use for transcription")
    language: Optional[str] = Field(
        None, description="The language of the input audio (ISO-639-1 format)"
    )
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
    timestamp_granularities: Optional[List[TimestampGranularity]] = Field(
        default=["segment"],
        description="The timestamp granularities to populate for this transcription",
    )


class TranscriptionResponse(BaseModel):
    text: str = Field(..., description="The transcribed text")


class Word(BaseModel):
    word: str
    start: float
    end: float


class Segment(BaseModel):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: List[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float


class VerboseTranscriptionResponse(BaseModel):
    task: str = Field("transcribe", description="The task performed")
    language: str = Field(
        ..., description="The detected or specified language of the input audio"
    )
    duration: float = Field(
        ..., description="The duration of the input audio in seconds"
    )
    text: str = Field(..., description="The transcribed text")
    words: Optional[List[Word]] = Field(None, description="Word-level timestamps")
    segments: List[Segment] = Field(..., description="Segment-level details")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task": "transcribe",
                "language": "english",
                "duration": 8.470000267028809,
                "text": "The beach was a popular spot on a hot summer day. People were swimming in the ocean, building sandcastles, and playing beach volleyball.",
                "segments": [
                    {
                        "id": 0,
                        "seek": 0,
                        "start": 0.0,
                        "end": 3.319999933242798,
                        "text": " The beach was a popular spot on a hot summer day.",
                        "tokens": [
                            50364,
                            440,
                            7534,
                            390,
                            257,
                            3743,
                            4008,
                            322,
                            257,
                            2368,
                            4266,
                            786,
                            13,
                            50530,
                        ],
                        "temperature": 0.0,
                        "avg_logprob": -0.2860786020755768,
                        "compression_ratio": 1.2363636493682861,
                        "no_speech_prob": 0.00985979475080967,
                    }
                ],
            }
        }
    )


def create_transcription(
    request: CreateTranscriptionRequest,
) -> Union[TranscriptionResponse, VerboseTranscriptionResponse]:
    """Transcribes audio into the input language."""
    ...
