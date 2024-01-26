# Default configs for the OpenAI API

# ChatCompletion
oai_chat_llmconfig = {
    "model": "gpt-4-turbo-preview",
    "frequency_penalty": 0,
    "max_tokens": None,
    "n": 1,
    "presence_penalty": 0, 
    "response_format": {"type": "text"}, 
    "seed": None, 
    "stop": None,
    "stream": False,
    "temperature": 0.7, 
    "top_p": 1, 
    "tools": None,
    "tool_choice": "none", 
    "user": None
    }

oai_chat_schema = {
    "required" : ["model", "frequency_penalty", "n", "presence_penalty", "response_format", "temperature", "top_p"],
    "optional": ["seed", "stop", "stream", "tools", "tool_choice", "user", "max_tokens"],
    "input": "messages",
    "config": oai_chat_llmconfig
    }


# Finetune
oai_finetune_llmconfig = {
    "model": "gpt-3.5-turbo",
    "hyperparameters": {
        "batch_size": "auto", 
        "learning_rate_multiplier": "auto",
        "n_epochs": "auto"
    },
    "suffix": None,
    "training_file": None,
    }

oai_finetune_schema = {
    "required" : ["model", "training_file"],
    "optional": ["hyperparameters", "suffix", "validate_file"],
    "input": ["training_file"],
    "config": oai_finetune_llmconfig 
}


# Audio ---- create  speech

oai_audio_speech_llmconfig = {
    "model": "tts-1",
    "voice": "alloy",
    "response_format": "mp3",
    "speed": 1
    }
oai_audio_speech_schema = {
    "required" : ["model", "voice"],
    "optional": ["response_format", "speed"],
    "input": "input",
    "config": oai_audio_speech_llmconfig
    }


# Audio ----------- create transcription
oai_audio_transcriptions_llmconfig = {
    "model": "whisper-1",
    "language": None,
    "prompt": None,
    "response_format": "json",
    "temperature": 0
    }
oai_audio_transcriptions_schema = {
    "required" : ["model", "voice"],
    "optional": ["response_format", "language", "prompt", "response_format", "temperature"],
    "input": "file",
    "config": oai_audio_transcriptions_llmconfig
    }


# Audio ------------    translations
oai_audio_translations_llmconfig = {
    "model": "whisper-1",
    "prompt": None,
    "response_format": "json",
    "temperature": 0
    }

oai_audio_translations_schema = {
    "required" : ["model"],
    "optional": ["response_format", "speed", "prompt", "temperature"],
    "input": "file",
    "config": oai_audio_translations_llmconfig
    }








# images












oai_schema = {
    
    "chat/completions": oai_chat_schema,
    "finetune": oai_finetune_schema,
    "audio_speech": oai_audio_speech_schema, 
    "audio_transcriptions": oai_audio_transcriptions_schema,
    "audio_translations": oai_audio_translations_schema,
    
}
