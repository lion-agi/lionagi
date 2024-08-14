API_key_schema = "OPENAI_API_KEY"

## Chat Completion
oai_chat_llmconfig = {
    "frequency_penalty": 0,
    "max_tokens": None,
    "n": 1,
    "presence_penalty": 0,
    "response_format": {"type": "text"},
    "seed": None,
    "stop": None,
    "stream": False,
    "temperature": 0.1,
    "top_p": 1,
    "tools": None,
    "tool_choice": "none",
    "user": None,
    "logprobs": False,
    "top_logprobs": None,
    "logit_bias": None,
    "service_tier": None,
    "stream_options": None,
    "parallel_tool_calls": True,
}

oai_chat_schema = {
    "required_params": [
        "model",
        "frequency_penalty",
        "n",
        "presence_penalty",
        "response_format",
        "temperature",
        "top_p",
    ],
    "optional_params": [
        "seed",
        "stop",
        "stream",
        "tools",
        "tool_choice",
        "user",
        "max_tokens",
        "logprobs",
        "top_logprobs",
        "logit_bias",
        "service_tier",
        "stream_options",
        "parallel_tool_calls",
    ],
    "input_key": "messages",
    "config": oai_chat_llmconfig,
}


## fine-tuning

# Finetune
oai_finetune_llmconfig = {
    "model": "gpt-3.5-turbo",
    "hyperparameters": {
        "batch_size": "auto",
        "learning_rate_multiplier": "auto",
        "n_epochs": "auto",
    },
    "suffix": None,
    "training_file": None,
}

oai_finetune_schema = {
    "required_params": ["model", "training_file"],
    "optional_params": ["hyperparameters", "suffix", "validate_file"],
    "input_key": ["training_file"],
    "config": oai_finetune_llmconfig,
}


## Audio ---- create  speech

oai_audio_speech_llmconfig = {
    "model": "tts-1",
    "voice": "alloy",
    "response_format": "mp3",
    "speed": 1,
}
oai_audio_speech_schema = {
    "required": ["model", "voice"],
    "optional": ["response_format", "speed"],
    "input_": "input_",
    "config": oai_audio_speech_llmconfig,
}

# Audio ----------- create transcription
oai_audio_transcriptions_llmconfig = {
    "model": "whisper-1",
    "language": None,
    "format_prompt": None,
    "response_format": "json",
    "temperature": 0,
}
oai_audio_transcriptions_schema = {
    "required": ["model", "voice"],
    "optional": [
        "response_format",
        "language",
        "format_prompt",
        "response_format",
        "temperature",
    ],
    "input_": "file",
    "config": oai_audio_transcriptions_llmconfig,
}

# Audio ------------    translations
oai_audio_translations_llmconfig = {
    "model": "whisper-1",
    "format_prompt": None,
    "response_format": "json",
    "temperature": 0,
}

oai_audio_translations_schema = {
    "required": ["model"],
    "optional": ["response_format", "speed", "format_prompt", "temperature"],
    "input_": "file",
    "config": oai_audio_translations_llmconfig,
}

## embeddings

oai_embeddings_llmconfig = {
    "model": "text-embedding-ada-002",
    "encoding_format": "float",
    "user": None,
    "dimensions": None,
}

oai_embeddings_schema = {
    "required_params": ["model", "encoding_format"],
    "optional_params": ["user", "dimensions"],
    "input_key": "input",
    "config": oai_embeddings_llmconfig,
}


OAI_CONFIG = {
    "chat/completions": oai_chat_schema,
    "finetune": oai_finetune_schema,
    "audio_speech": oai_audio_speech_schema,
    "audio_transcriptions": oai_audio_transcriptions_schema,
    "audio_translations": oai_audio_translations_schema,
    "API_key_schema": API_key_schema,
    "embeddings": oai_embeddings_schema,
    "base_url": "https://api.openai.com/v1/",
}
