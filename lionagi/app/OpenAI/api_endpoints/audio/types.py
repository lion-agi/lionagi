from enum import Enum


class TTSModel(str, Enum):
    TTS_1 = "tts-1"
    TTS_1_HD = "tts-1-hd"


class Voice(str, Enum):
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"


class AudioFormat(str, Enum):
    MP3 = "mp3"
    OPUS = "opus"
    AAC = "aac"
    FLAC = "flac"
    WAV = "wav"
    PCM = "pcm"


class WhisperModel(str, Enum):
    WHISPER_1 = "whisper-1"


class TranscriptionResponseFormat(str, Enum):
    JSON = "json"
    TEXT = "text"
    SRT = "srt"
    VERBOSE_JSON = "verbose_json"
    VTT = "vtt"


class TimestampGranularity(str, Enum):
    WORD = "word"
    SEGMENT = "segment"
